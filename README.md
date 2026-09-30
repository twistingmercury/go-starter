# go-starter

> **Maturity Level**: Emerging - Unreleased; CLI flags and template may change.
> **Version**: v0.0.1
>
> - **Emerging**: Prototype, not production-ready, expect breaking changes
> - **Basic**: Production-ready but actively evolving, expect minor version changes
> - **Mature**: Stable, battle-tested, changes are rare

---

## Table of Contents

- [Usage](#usage)
- [How it works](#how-it-works)
- [Key Considerations](#key-considerations)
- [Development Considerations](#development-considerations)
- [Versioning](#versioning)

## Usage

`go-starter` scaffolds a new Go CLI project from a template bundled inside the
tool, and ships the matching Claude Code skill so Claude can drive the scaffold
for you.

Install the tool, then install its skill:

```sh
make build            # Docker: lint, test, build the wheel into dist/
make install          # uv tool install dist/go_starter-*.whl
go-starter --install-skill
```

Scaffold a project:

```sh
mkdir my-tool && cd my-tool
go-starter --module github.com/acme/my-tool
make local            # format, lint, scan, test, build .bin/local/my-tool
```

| Flag | Meaning |
| --- | --- |
| `--module <path>` | Go module path. Required. |
| `--app-name <name>` | Binary name. Defaults to the last module segment. |
| `[target]` | Directory to scaffold into. Default `.`; created if missing. |
| `--install-skill` | Install the bundled Claude Code skill and exit. |
| `-v`, `--version` | Print the tool version. |

The generated project has a `src/` Go module with `main` in `cmd/`, a Makefile
(`analyze`, `test`, `local`, `build`, `install`), a Docker-based
cross-platform build for linux and darwin on amd64 and arm64, a GitHub Actions
workflow, and lint configs. The bundled skill lists the full layout in
`src/go_starter/skills/go-starter/SKILL.md`.

## How it works

- **Template as package data.** Every generated file lives under
  `src/go_starter/template/` with a `.tmpl` suffix and two literal tokens,
  `{{GO_MODULE}}` and `{{APP_NAME}}`. Rendering copies the tree, replaces the
  tokens, strips the suffix, and marks `build/build.sh` executable.
- **Skill gate.** `--install-skill` copies the bundled skill to
  `~/.claude/skills/go-starter/` and writes a `VERSION` stamp holding the
  tool version and a SHA-256 of the skill contents. Every other run first
  checks that stamp against the running binary and exits 1 with a hint if the
  skill is missing or stale. The skill and the tool can't drift apart.
- **Modules.** `cli.py` parses arguments, `names.py` validates the module path
  and app name, `embedded.py` walks package data in sorted order,
  `render.py` checks the target and writes the tree, `skillinstall.py` handles
  the skill, and `main.py` wires them together and maps user errors to
  `error: ...` on stderr.

## Key Considerations

- **Target must be empty.** The target may only contain `.git`, `.claude`,
  `.codex`, or `.agents`, and none of those may be symlinks. Anything else
  blocks the run and is named in the error. Nothing is written on refusal.
- **Names are strict.** The module path is a plain host/path with no scheme or
  trailing slash. The app name must be lowercase; when the derived name isn't,
  the error tells you to pass `--app-name`.
- **Substitution is literal.** Tokens are replaced with `str.replace`, so `&`,
  `\`, and `$` in values need no escaping.
- **Stdlib only.** The runtime has no dependencies. Dev dependencies are
  `pytest` and `ruff`.
- **Version comes from the build.** The wheel is stamped from the latest git
  tag at build time. With no tag it is `0.0.0.dev0`.

## Development Considerations

### Quick Start

Requires `uv`, Docker, and optionally Go on PATH.

```sh
make test             # ruff format, ruff check, pytest
make build            # runs the same gates inside Docker, then builds the wheel
make install          # install the wheel as a uv tool
make uninstall
```

### Testing

`make test` formats, lints, and runs the full pytest suite. The suite uses a
fake `HOME` fixture in `tests/conftest.py`, so it never touches your real
`~/.claude`. `tests/test_integration_go.py` renders a project and compiles it
with `go build`; it skips when `go` isn't on PATH, which includes the Docker
build.

### Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/).

Version is determined from git tags:

```bash
git describe --tags --always
```

Changes are recorded in [CHANGELOG.md](CHANGELOG.md).
