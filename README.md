# go-starter

Scaffolds a new Go project from a bundled template and ships the matching
Claude Code skill.

## Install

```sh
make build      # Docker: format check, lint, tests, wheel to dist/
make install    # uv tool install dist/go_starter-*.whl
go-starter --install-skill
```

`--install-skill` replaces `~/.claude/skills/go-starter/` with the copy
bundled in this build and prints the path. Every other run exits 1 until the
installed skill matches the binary, and tells you to run it again.

## Use

```sh
mkdir my-tool && cd my-tool
go-starter --module github.com/acme/my-tool
make local
```

| Flag | Meaning |
| --- | --- |
| `--module <path>` | Go module path. Required. |
| `--app-name <name>` | Binary name. Defaults to the last segment of the module path. |
| `[target]` | Directory to scaffold into. Defaults to `.`; created if missing; must be empty apart from `.git`, `.claude`, `.codex`, `.agents`. |
| `--install-skill` | Install the bundled skill and exit. |

## Develop

`make test` runs ruff and pytest. The Go compile test is skipped when `go`
isn't on PATH, which includes the Docker build.
