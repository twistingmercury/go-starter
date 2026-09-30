---
name: go-starter
description: Use when standing up a new, empty Go project in the current directory with a src/ module layout, a Makefile (analyze, test, local, build, install), and a Docker-based cross-platform build. Not for modifying an existing Go project.
---

# Go Starter

Scaffolds the current directory as a minimal Go CLI project by running the
`go-starter` command. It's deterministic: every file comes from the template
bundled inside that binary. Don't hand-write the files.

## Generated layout

| Path | Purpose |
| --- | --- |
| `src/go.mod`, `src/cmd/main.go` | The Go module; `main` package lives in `cmd/` |
| `Makefile` | `help`, `analyze`, `test`, `local`, `build`, `install`, `uninstall` |
| `build/Dockerfile`, `build/build.sh` | Lint, scan, test, then export linux and darwin binaries for amd64 and arm64 to `.bin/` |
| `.github/workflows/ci.yaml` | Runs build/build.sh on develop and main |
| `.gitignore`, `.dockerignore`, `.markdownlint.json`, `.markdownlintignore`, `.shellcheckrc`, `README.md`, `CHANGELOG.md` | Repo hygiene |
| `docs/`, `tests/` | Empty placeholders (`.gitkeep`) |

## Steps

1. **Check the tool.** Run `go-starter --version`. If the command is missing,
   tell the user to install it (`make install` in the go-starter repo) and stop.
   If it reports the skill is outdated, run `go-starter --install-skill` and
   continue.
2. **Pick names.** Ask for the Go module path (for example
   `github.com/acme/tool`) if the user didn't give one. The binary name defaults
   to the last segment of the module path; pass `--app-name` only when the user
   wants something else or the derived name isn't lowercase.
3. **Check the target.** Run from the directory that becomes the repo root. It
   may only hold `.git`, `.claude`, `.codex`, or `.agents`. The tool checks
   this itself and refuses anything else before writing. On refusal, report
   the blocking entry and ask the user whether to move it or choose another
   directory. Never delete it or render somewhere else yourself.
4. **Render.**

   ```sh
   go-starter --module <module-path> [--app-name <name>]
   ```

5. **Verify** from the project root, checking exit codes. Run `make local`. It
   formats, lints, scans, tests, and builds `.bin/local/<name>`. If
   `docker info` succeeds, run `make build` too. If either fails, say so and
   don't claim the scaffold passes.
6. **Hand off.** Summarize the layout and the commands (`make local`,
   `make build`, `make install`).

Don't `git init`, commit, push, or add dependencies unless the user asks.

## Common mistakes

- Editing generated files to change the module or binary name. Re-run
  `go-starter` in a clean directory instead.
- Running Go commands from the repo root. The module lives in `src/`; the
  Makefile already handles this.
