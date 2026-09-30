# go-starter

> **Maturity Level**: Emerging - in active, initial development; expect breaking changes.
> **Version**: v0.0.1

---

## Table of Contents

- [Usage](#usage)
- [How it works](#how-it-works)
- [Key Considerations](#key-considerations)
- [Development Considerations](#development-considerations)
- [Versioning](#versioning)

## Usage

A new Python project

```sh
go-starter --version
```

| Flag        | Short | Required | Description                 |
| ----------- | ----- | -------- | --------------------------- |
| `--version` | `-v`  | No       | Print the version and exit  |

## How it works

Argument parsing lives in `src/go_starter/cli.py` and the entry point in
`src/go_starter/main.py`.

## Key Considerations

- Supported platforms are Linux and macOS only.

## Development Considerations

Requires Python >= 3.12 and [uv](https://docs.astral.sh/uv/).

### Quick Start

```sh
uv sync
uv run go-starter
```

### Testing

```sh
make test      # sync, lint, and run pytest
make analyze   # format and auto-fix lint findings
make build     # Docker-first build; exports the wheel to dist/
make help      # list available targets
```

## Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/).

Version is determined from git tags:

```bash
git describe --tags --always
```
