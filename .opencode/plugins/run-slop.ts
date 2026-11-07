import { spawn } from "node:child_process";
import { access } from "node:fs/promises";
import { resolve as resolvePath } from "node:path";

import { Plugin } from "@opencode/plugin";

const TIMEOUT_MS = 10_000;

interface CommandResult {
  code: number | null;
  stdout: string;
  stderr: string;
  timedOut: boolean;
}

function run(command: string, args: string[], cwd: string): Promise<CommandResult> {
  return new Promise((resolveRun, rejectRun) => {
    const child = spawn(command, args, { cwd, stdio: ["ignore", "pipe", "pipe"] });

    let stdout = "";
    let stderr = "";
    let timedOut = false;

    const timer = setTimeout(() => {
      timedOut = true;
      child.kill("SIGKILL");
    }, TIMEOUT_MS);

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk: string) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk: string) => {
      stderr += chunk;
    });

    child.on("error", (error) => {
      clearTimeout(timer);
      rejectRun(error);
    });

    child.on("close", (code) => {
      clearTimeout(timer);
      resolveRun({ code, stdout, stderr, timedOut });
    });
  });
}

interface SlopOutput {
  stdout: string;
  stderr: string;
  exitCode: number | null;
}

function formatResult(result: SlopOutput, metadata: Record<string, unknown> = {}) {
  return {
    content: JSON.stringify(result),
    metadata: { exitCode: result.exitCode, ...metadata },
  };
}

export default Plugin.define({
  id: "sloperator.run-slop",
  async setup(ctx) {
    const directory = ctx.location.directory;

    await ctx.tool.transform((tools) => {
      tools.add({
        name: "run_slop",
        description:
          "Run a SlopLang (.slop) program with the project's interpreter and return its output. The path is resolved from the project root.",
        input: {
          type: "object",
          properties: {
            path: {
              type: "string",
              description: "Path to the .slop file, relative to the project root or absolute.",
            },
          },
          required: ["path"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input) => {
          const { path } = input as { path: string };
          const file = resolvePath(directory, path);

          try {
            await access(file);
          } catch {
            return formatResult(
              { stdout: "", stderr: `Could not find SlopLang program at '${file}'.`, exitCode: null },
              { file },
            );
          }

          // Prefer uv (the documented entrypoint), then fall back to the project venv.
          const candidates = [
            { command: "uv", args: ["run", "sloperator.py", file] },
            { command: resolvePath(directory, ".venv/bin/python"), args: ["sloperator.py", file] },
          ];

          let result: CommandResult | undefined;
          let lastError: NodeJS.ErrnoException | undefined;

          for (const candidate of candidates) {
            try {
              result = await run(candidate.command, candidate.args, directory);
              break;
            } catch (error) {
              lastError = error as NodeJS.ErrnoException;
              if (lastError.code !== "ENOENT") break;
            }
          }

          if (!result) {
            return formatResult(
              {
                stdout: "",
                stderr: `Could not run the SlopLang interpreter: ${lastError?.message ?? "unknown error"}. Install uv or create the project venv.`,
                exitCode: null,
              },
              { file },
            );
          }

          if (result.timedOut) {
            return formatResult(
              {
                stdout: result.stdout,
                stderr: `Running '${path}' timed out after ${TIMEOUT_MS}ms.${result.stderr ? `\n${result.stderr}` : ""}`,
                exitCode: result.code,
              },
              { file, timedOut: true },
            );
          }

          return formatResult(
            { stdout: result.stdout, stderr: result.stderr, exitCode: result.code },
            { file },
          );
        },
      });
    });
  },
});
