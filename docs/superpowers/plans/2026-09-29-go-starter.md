# go-starter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A stdlib-only Python CLI, `go-starter`, that scaffolds a new Go project from a bundled `{{GO_MODULE}}`/`{{APP_NAME}}` template and installs its own Claude Code skill with `--install-skill`.

**Architecture:** A `python-uv-starter`-scaffolded package `go_starter` bundles two data trees: `template/` (the Go project as `.tmpl` files) and `skills/go-starter/` (the Claude skill). `main.py` handles `--install-skill` first, then refuses to run unless `~/.claude/skills/go-starter/VERSION` carries this build's content hash (same rule as gralph), then validates names, checks the target is empty, and renders. Rendering is literal `str.replace` on both file paths and contents, then `.tmpl` is stripped.

**Tech Stack:** Python ≥ 3.12, stdlib only (`argparse`, `pathlib`, `importlib.resources`, `hashlib`, `shutil`), pytest + ruff via uv. Template needs Go 1.27 tooling only at verification time.

**Spec:** The "Context" section below. There is no separate design doc; the design was agreed in conversation on 2026-09-29.

## Context

`~/dev/scratch/go-basic-project` is meant to be a template for new Go projects, with the module path and binary name swapped in per project. Doing that by hand or by having an agent edit files is error-prone: the bare word `app` is also the tail of `example.com/app`, so a naive replace corrupts the module path. The agreed design is a standalone CLI a person or a skill can run. It bundles the Go template with explicit tokens, and it bundles the Claude skill too, installing it with `--install-skill` exactly like `~/dev/gralph` does. Normal runs exit 1 when the installed skill is missing or its hash doesn't match the binary, so skill and CLI never drift.

Decisions already made with the user: Python, stdlib only; Go-only tool named `go-starter`; new sibling repo scaffolded with `python-uv-starter`; skill embedded in the CLI; block-on-stale-skill behavior copied from gralph; Go version stays pinned (the tooling image is sha256-pinned), not a token; only two tokens, `{{GO_MODULE}}` and `{{APP_NAME}}`.

Reference implementations: `~/.claude/skills/python-uv-starter/scripts/scaffold.sh` and `tests/scaffold.bats` (behavior to port), `~/dev/gralph/internal/skillinstall/skillinstall.go` and `~/dev/gralph/cmd/main/main.go` (skill install/check semantics), `~/.claude/skills/python-uv-starter/SKILL.md` (skill shape).

## Global Constraints

- Python floor `>=3.12`; `dependencies = []` stays empty. Dev deps are only `pytest` and `ruff`.
- Code follows the user's rules: early returns, blank line after every `if` block, named functions over inline lambdas longer than a line, one job per function, comments say why not what, no `# noqa` or other suppressions.
- Ruff config from the scaffold (`select = ["N"]`) stays; `uv run ruff format` before every commit because the Docker build runs `ruff format --check`.
- Tokens are exactly `{{GO_MODULE}}` and `{{APP_NAME}}`. No other `{{` may appear in `template/`.
- Every template file ends in `.tmpl`, including dotfiles and `.gitkeep` placeholders.
- Skill install path is `~/.claude/skills/go-starter` via `Path.home()`; no override flag or env var, matching gralph.
- `VERSION` file format: line 1 the CLI version, line 2 `sha256:<hex>`, trailing newline.
- Commit after each task with a conventional message ending in `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Never push.

## Review Focus

1. Module whose last segment isn't a valid app name (`github.com/Acme/MyTool`) — expected: exit 1 with a message that says to pass `--app-name`, not a traceback. Test in Task 2 and Task 6.
2. Module with a scheme or trailing slash (`https://github.com/x/y`, `github.com/x/y/`) — expected: rejected before any write. Test in Task 2.
3. Target given as a path to an existing regular file — expected: exit 1 `error: ...`, not a traceback from `mkdir`. Test in Task 6.
4. Target that doesn't exist yet — expected: created, then scaffolded. Test in Task 6.
5. `--install-skill` when `~/.claude/skills` doesn't exist yet — expected: parents created, install succeeds. Test in Task 5.

---

## File Structure

New repo `~/dev/scratch/go-starter` (created by Task 1). Paths below are relative to it.

| Path | Responsibility |
| --- | --- |
| `pyproject.toml` | Generated; Task 3 adds `[tool.setuptools.package-data]` |
| `src/go_starter/cli.py` | argparse only; returns a `Namespace` |
| `src/go_starter/names.py` | Validate module path and app name, derive app name |
| `src/go_starter/embedded.py` | Locate bundled resources and walk them in sorted order |
| `src/go_starter/render.py` | Empty-target check and template rendering |
| `src/go_starter/skillinstall.py` | Install, hash, and check the bundled skill |
| `src/go_starter/main.py` | Wire the above; the console entry point |
| `src/go_starter/template/**/*.tmpl` | The Go project template |
| `src/go_starter/skills/go-starter/SKILL.md`, `agents/openai.yaml` | The Claude skill |
| `tests/conftest.py` | `fake_home` and `installed_skill` fixtures |
| `tests/test_names.py`, `test_embedded.py`, `test_render.py`, `test_skillinstall.py`, `test_cli.py`, `test_main.py`, `test_integration_go.py` | One test module per source module plus the Go compile check |
| `docs/superpowers/plans/2026-09-29-go-starter.md` | This plan, copied in by Task 1 |

---

### Task 1: Scaffold the repo

**Files:**
- Create: `~/dev/scratch/go-starter/` via `python-uv-starter`
- Keep: `docs/superpowers/plans/2026-09-29-go-starter.md` (this file, already present before scaffolding)

**Interfaces:**
- Produces: package `go_starter` with `main.py` (`main(argv=None)`), `cli.py` (`get_args(argv=None)`), `[project.scripts] go-starter = "go_starter.main:main"`, Makefile targets `test`, `analyze`, `build`, `install`, `uninstall`.

- [ ] **Step 1: Render the scaffold**

`scaffold.sh` refuses a non-empty target and `docs/` already holds this plan, so park it during the render and merge it back over the generated `docs/.gitkeep`.

```bash
cd ~/dev/scratch/go-starter
mv docs ../go-starter-docs.tmp
bash ~/.claude/skills/python-uv-starter/scripts/scaffold.sh \
  --project-name go-starter \
  --description "Scaffold a new Go project from a bundled template"
cp -r ../go-starter-docs.tmp/. docs/
rm -rf ../go-starter-docs.tmp
```

Expected: `Scaffolded go-starter in /home/jeremy/dev/scratch/go-starter`, `src/go_starter/main.py` exists, and `docs/superpowers/plans/2026-09-29-go-starter.md` is back in place.

- [ ] **Step 2: Verify the generated project passes its own tests**

Run: `make test`
Expected: ruff clean, pytest reports the two generated stubs passing, `uv.lock` created.

- [ ] **Step 3: Init git**

```bash
git init -b main
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: scaffold go-starter with python-uv-starter

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Name validation and derivation

**Files:**
- Create: `src/go_starter/names.py`
- Test: `tests/test_names.py`

**Interfaces:**
- Produces: `InvalidNameError(ValueError)`; `validate_module(module: str) -> str`; `validate_app_name(name: str) -> str`; `derive_app_name(module: str) -> str`. Validators return the input unchanged on success and raise `InvalidNameError` otherwise.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_names.py
import pytest

from go_starter import names


@pytest.mark.parametrize(
    "module",
    [
        "example.com/app",
        "github.com/acme/tool",
        "github.com/acme/tool/v2",
        "gitlab.com/a-b/c_d.e~f",
        "localmod",
    ],
)
def test_validate_module_accepts_go_module_paths(module):
    assert names.validate_module(module) == module


@pytest.mark.parametrize(
    "module",
    [
        "",
        "https://github.com/acme/tool",
        "github.com/acme/tool/",
        "Github.com/acme/tool",
        "github.com//tool",
        "has space/x",
        "{{GO_MODULE}}",
    ],
)
def test_validate_module_rejects_bad_paths(module):
    with pytest.raises(names.InvalidNameError):
        names.validate_module(module)


@pytest.mark.parametrize("name", ["app", "my-tool", "my_tool", "tool2"])
def test_validate_app_name_accepts_lowercase_names(name):
    assert names.validate_app_name(name) == name


@pytest.mark.parametrize("name", ["", "MyTool", "2tool", "my tool", "my/tool", "-tool"])
def test_validate_app_name_rejects_bad_names(name):
    with pytest.raises(names.InvalidNameError):
        names.validate_app_name(name)


def test_validate_app_name_error_mentions_the_override_flag():
    with pytest.raises(names.InvalidNameError, match="--app-name"):
        names.validate_app_name("MyTool")


@pytest.mark.parametrize(
    ("module", "expected"),
    [
        ("example.com/app", "app"),
        ("github.com/acme/tool", "tool"),
        ("github.com/acme/tool/v2", "v2"),
        ("localmod", "localmod"),
    ],
)
def test_derive_app_name_takes_last_segment(module, expected):
    assert names.derive_app_name(module) == expected
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_names.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'go_starter.names'`

- [ ] **Step 3: Write the implementation**

```python
# src/go_starter/names.py
"""Validation for the two values that get substituted into the template."""

import re

# Deliberately looser than the Go spec; `go mod` is the real authority. This
# only has to stop typos and things that would corrupt go.mod or file paths.
MODULE_RE = re.compile(r"^[a-z0-9][a-z0-9.\-]*(/[A-Za-z0-9._~\-]+)*$")
APP_NAME_RE = re.compile(r"^[a-z][a-z0-9_\-]*$")


class InvalidNameError(ValueError):
    """A module path or app name that must not reach the template."""


def validate_module(module: str) -> str:
    if not MODULE_RE.fullmatch(module):
        raise InvalidNameError(
            f"module path must look like host/path with a lowercase host and no scheme, spaces, or trailing slash: {module!r}"
        )

    return module


def validate_app_name(name: str) -> str:
    if not APP_NAME_RE.fullmatch(name):
        raise InvalidNameError(
            f"app name must match ^[a-z][a-z0-9_-]*$ (pass --app-name to override the derived name): {name!r}"
        )

    return name


def derive_app_name(module: str) -> str:
    return module.rsplit("/", 1)[-1]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_names.py -v`
Expected: all PASS

- [ ] **Step 5: Format and commit**

```bash
uv run ruff format && uv run ruff check
git add src/go_starter/names.py tests/test_names.py
git commit -m "feat: validate module path and app name

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Bundle the Go template as package data

**Files:**
- Create: `src/go_starter/embedded.py`
- Create: `src/go_starter/template/**` (from `~/dev/scratch/go-basic-project`)
- Modify: `pyproject.toml` (add package-data)
- Test: `tests/test_embedded.py`

**Interfaces:**
- Produces: `embedded.resource(*parts: str) -> Traversable` returning `files("go_starter") / parts...`; `embedded.iter_files(root: Traversable, prefix: str = "") -> Iterator[tuple[str, Traversable]]` yielding `(posix_relative_path, entry)` for every file under `root`, depth-first, sorted by name at each level.
- Produces: the template tree listed in Step 3.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_embedded.py
from go_starter import embedded

EXPECTED_TEMPLATE_FILES = {
    ".dockerignore.tmpl",
    ".gitignore.tmpl",
    "CHANGELOG.md.tmpl",
    "Makefile.tmpl",
    "README.md.tmpl",
    "build/Dockerfile.tmpl",
    "build/build.sh.tmpl",
    "docs/.gitkeep.tmpl",
    "src/cmd/main.go.tmpl",
    "src/go.mod.tmpl",
    "tests/.gitkeep.tmpl",
}


def test_iter_files_lists_every_template_file_including_dotfiles():
    found = {rel for rel, _ in embedded.iter_files(embedded.resource("template"))}
    assert found == EXPECTED_TEMPLATE_FILES


def test_iter_files_is_sorted_and_stable():
    first = [rel for rel, _ in embedded.iter_files(embedded.resource("template"))]
    second = [rel for rel, _ in embedded.iter_files(embedded.resource("template"))]
    assert first == sorted(first) == second


def test_template_uses_only_the_two_tokens():
    tokens = set()
    for _, entry in embedded.iter_files(embedded.resource("template")):
        text = entry.read_text()
        start = 0
        while (start := text.find("{{", start)) != -1:
            end = text.find("}}", start)
            tokens.add(text[start : end + 2])
            start = end
    assert tokens == {"{{GO_MODULE}}", "{{APP_NAME}}"}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_embedded.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'go_starter.embedded'`

- [ ] **Step 3: Copy the Go project in as `.tmpl` files**

```bash
SRC=~/dev/scratch/go-basic-project
T=src/go_starter/template
mkdir -p $T/build $T/src/cmd $T/docs $T/tests
cp $SRC/.dockerignore   $T/.dockerignore.tmpl
cp $SRC/.gitignore      $T/.gitignore.tmpl
cp $SRC/Makefile        $T/Makefile.tmpl
cp $SRC/build/Dockerfile $T/build/Dockerfile.tmpl
cp $SRC/build/build.sh  $T/build/build.sh.tmpl
cp $SRC/src/cmd/main.go $T/src/cmd/main.go.tmpl
cp $SRC/src/go.mod      $T/src/go.mod.tmpl
: > $T/docs/.gitkeep.tmpl
: > $T/tests/.gitkeep.tmpl
```

- [ ] **Step 4: Tokenize and clean up the copied files**

`src/go.mod.tmpl` — replace the first line so the file reads:

```
module {{GO_MODULE}}

go 1.27.1
```

`Makefile.tmpl` — recipe lines must keep their leading TAB. Make these exact line changes:

| Old line | New line |
| --- | --- |
| `default: help` | `.DEFAULT_GOAL := help` |
| `GOBIN := "${HOME}/go/bin"` | `GOBIN := ${HOME}/go/bin` |
| `BIN_NAME ?= app` | `BIN_NAME ?= {{APP_NAME}}` |
| `local: analyze test ## Performs only a local build of gralph` | `local: analyze test ## Performs only a local build of {{APP_NAME}}` |
| `` build: ## Performs a full build of gralph (Docker-based; use `make local` for a quick local binary) `` | `` build: ## Performs a full build of {{APP_NAME}} (Docker-based; use `make local` for a quick local binary) `` |
| `install: local ## Install gralph to $GOBIN` | `install: local ## Install {{APP_NAME}} to $GOBIN` |
| `	cp ${LOCAL_BUILD}/gralph ${GOBIN}/${BIN_NAME}"` | `	cp ${LOCAL_BUILD}/${BIN_NAME} ${GOBIN}/${BIN_NAME}` |
| `uninstall: ## Uninstall gralph to $GOBIN` | `uninstall: ## Uninstall {{APP_NAME}} from $GOBIN` |
| `	rm ${GOBIN}/"${BIN_NAME}"` | `	rm ${GOBIN}/${BIN_NAME}` |

Delete the two unused lines `GOOS := ...` and `GOARCH := ...`.

`build/Dockerfile.tmpl`:

```bash
sed -i 's|/app ./cmd$|/{{APP_NAME}} ./cmd|' src/go_starter/template/build/Dockerfile.tmpl
grep -c '{{APP_NAME}} ./cmd' src/go_starter/template/build/Dockerfile.tmpl   # expect 4
```

`build/build.sh.tmpl`: change `IMAGE_NAME="${IMAGE_NAME:-gralph}"` to `IMAGE_NAME="${IMAGE_NAME:-{{APP_NAME}}}"` and delete the line `	printf "${MODULE}\n"` inside `main()`.

Create `README.md.tmpl`:

```markdown
# {{APP_NAME}}

Go module `{{GO_MODULE}}`.

## Build

| Command | What it does |
| --- | --- |
| `make local` | Lint, vet, test, then build `.bin/local/{{APP_NAME}}` for this machine |
| `make build` | Docker-based build; exports linux and darwin binaries for amd64 and arm64 to `.bin/` |
| `make install` | Copy the local build to `$HOME/go/bin/{{APP_NAME}}` |

Run `make` with no arguments to list every target.
```

Create `CHANGELOG.md.tmpl`:

```markdown
# Changelog

## Unreleased
```

- [ ] **Step 5: Declare the package data**

Append to `pyproject.toml`:

```toml
[tool.setuptools.package-data]
# The second glob is required: plain * never matches leading dots, so
# .gitignore.tmpl and .dockerignore.tmpl would be silently dropped from the wheel.
go_starter = ["template/**/*", "template/**/.*", "skills/**/*"]
```

- [ ] **Step 6: Write `embedded.py`**

```python
# src/go_starter/embedded.py
"""Access to the data trees shipped inside the go_starter package."""

from collections.abc import Iterator
from importlib.resources import files
from importlib.resources.abc import Traversable


def resource(*parts: str) -> Traversable:
    root = files("go_starter")
    for part in parts:
        root = root / part

    return root


def iter_files(
    root: Traversable, prefix: str = ""
) -> Iterator[tuple[str, Traversable]]:
    # Sorted so the skill content hash is identical on every filesystem.
    for entry in sorted(root.iterdir(), key=entry_name):
        rel = f"{prefix}{entry.name}"
        if entry.is_dir():
            yield from iter_files(entry, f"{rel}/")
            continue

        yield rel, entry


def entry_name(entry: Traversable) -> str:
    return entry.name
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `uv run pytest tests/test_embedded.py -v`
Expected: all PASS. If `test_iter_files_lists_every_template_file_including_dotfiles` fails, diff the two sets; a missing dotfile means Step 3 skipped a `cp`.

- [ ] **Step 8: Prove the wheel carries the data**

```bash
uv build
unzip -l dist/go_starter-*.whl | grep -c '\.tmpl$'
```

Expected: `11`. Then `rm -rf dist`.

- [ ] **Step 9: Format and commit**

```bash
uv run ruff format && uv run ruff check
git add pyproject.toml src/go_starter/embedded.py src/go_starter/template tests/test_embedded.py
git commit -m "feat: bundle the Go project template as package data

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Render the template

**Files:**
- Create: `src/go_starter/render.py`
- Test: `tests/test_render.py`

**Interfaces:**
- Consumes: `embedded.resource`, `embedded.iter_files` (Task 3).
- Produces: `TargetNotEmptyError(Exception)`; `require_empty_target(target: Path) -> None`; `render(target: Path, tokens: dict[str, str]) -> None`; `substitute(text: str, tokens: dict[str, str]) -> str`. `ALLOWED_ENTRIES = frozenset({".git", ".claude", ".codex", ".agents"})`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_render.py
import os
from pathlib import Path

import pytest

from go_starter import render

TOKENS = {"GO_MODULE": "example.com/demo", "APP_NAME": "demo"}


def all_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*") if p.is_file())


def test_render_writes_the_project_with_tokens_replaced(tmp_path):
    render.render(tmp_path, TOKENS)

    assert (tmp_path / "src/go.mod").read_text().startswith("module example.com/demo\n")
    assert "BIN_NAME ?= demo\n" in (tmp_path / "Makefile").read_text()
    assert "/.bin/amd64/linux/demo ./cmd" in (tmp_path / "build/Dockerfile").read_text()
    assert (
        'IMAGE_NAME="${IMAGE_NAME:-demo}"' in (tmp_path / "build/build.sh").read_text()
    )
    assert (tmp_path / "docs/.gitkeep").exists()
    assert (tmp_path / "tests/.gitkeep").exists()
    assert (tmp_path / ".gitignore").exists()


def test_render_leaves_no_tokens_or_tmpl_suffixes(tmp_path):
    render.render(tmp_path, TOKENS)

    for path in all_files(tmp_path):
        assert not path.name.endswith(".tmpl"), path
        assert "{{" not in path.read_text(), path


def test_render_marks_build_script_executable(tmp_path):
    render.render(tmp_path, TOKENS)

    assert os.access(tmp_path / "build/build.sh", os.X_OK)


def test_substitute_is_literal_for_regex_and_sed_metacharacters():
    assert (
        render.substitute("x {{APP_NAME}} y", {"APP_NAME": r"a&b\1$2"})
        == r"x a&b\1$2 y"
    )


def test_require_empty_target_allows_agent_metadata_dirs(tmp_path):
    for name in render.ALLOWED_ENTRIES:
        (tmp_path / name).mkdir()

    render.require_empty_target(tmp_path)


def test_require_empty_target_names_the_blocking_entry(tmp_path):
    (tmp_path / "notes.txt").touch()

    with pytest.raises(render.TargetNotEmptyError, match="notes.txt"):
        render.require_empty_target(tmp_path)


def test_require_empty_target_rejects_symlinked_metadata_dir(tmp_path):
    (tmp_path / ".git").symlink_to(tmp_path)

    with pytest.raises(render.TargetNotEmptyError, match=".git"):
        render.require_empty_target(tmp_path)


def test_require_empty_target_rejects_an_already_scaffolded_dir(tmp_path):
    render.render(tmp_path, TOKENS)

    with pytest.raises(render.TargetNotEmptyError):
        render.require_empty_target(tmp_path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_render.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'go_starter.render'`

- [ ] **Step 3: Write the implementation**

```python
# src/go_starter/render.py
"""Turn the bundled template into a project directory."""

import stat
from pathlib import Path

from go_starter import embedded

ALLOWED_ENTRIES = frozenset({".git", ".claude", ".codex", ".agents"})
TEMPLATE_SUFFIX = ".tmpl"
EXECUTABLE_FILES = ("build/build.sh",)


class TargetNotEmptyError(Exception):
    """The target holds something a user might care about."""


def require_empty_target(target: Path) -> None:
    for entry in target.iterdir():
        if entry.name in ALLOWED_ENTRIES and not entry.is_symlink():
            continue

        raise TargetNotEmptyError(
            f"target directory is not empty; blocking entry: {entry.name}"
        )


def substitute(text: str, tokens: dict[str, str]) -> str:
    # str.replace is literal, so values with &, \, or $ never need escaping.
    for key, value in tokens.items():
        text = text.replace(f"{{{{{key}}}}}", value)

    return text


def render(target: Path, tokens: dict[str, str]) -> None:
    for rel, entry in embedded.iter_files(embedded.resource("template")):
        dest = target / substitute(rel.removesuffix(TEMPLATE_SUFFIX), tokens)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(substitute(entry.read_text(), tokens))

    for rel in EXECUTABLE_FILES:
        mark_executable(target / rel)


def mark_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
```

Note on `substitute`: `f"{{{{{key}}}}}"` produces the literal `{{KEY}}`; four braces emit two, then `{key}` interpolates, then four more emit two.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_render.py -v`
Expected: all PASS

- [ ] **Step 5: Format and commit**

```bash
uv run ruff format && uv run ruff check
git add src/go_starter/render.py tests/test_render.py
git commit -m "feat: render the bundled template into an empty directory

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: Bundled skill and `skillinstall`

**Files:**
- Create: `src/go_starter/skills/go-starter/SKILL.md`
- Create: `src/go_starter/skills/go-starter/agents/openai.yaml`
- Create: `src/go_starter/skillinstall.py`
- Create: `tests/conftest.py`
- Test: `tests/test_skillinstall.py`

**Interfaces:**
- Consumes: `embedded.resource`, `embedded.iter_files` (Task 3).
- Produces: `SKILL_NAME = "go-starter"`; `SkillCheckError(Exception)`; `skill_dir() -> Path`; `content_hash() -> str` (`"sha256:<hex>"`); `install() -> Path`; `check() -> None` (raises `SkillCheckError`).
- Produces fixtures: `fake_home` (a `Path`, `HOME` monkeypatched to it) and `installed_skill` (runs `install()` under `fake_home`, returns the installed `Path`).

- [ ] **Step 1: Write the skill files**

`src/go_starter/skills/go-starter/SKILL.md`:

```markdown
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
| `.gitignore`, `.dockerignore`, `README.md`, `CHANGELOG.md` | Repo hygiene |
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
```

`src/go_starter/skills/go-starter/agents/openai.yaml`:

```yaml
interface:
  display_name: "Go Starter"
  short_description: "Scaffold an empty Go CLI project with go-starter"
  default_prompt: "Use $go-starter to scaffold a new Go project in the current directory."
```

- [ ] **Step 2: Write the fixtures and failing tests**

```python
# tests/conftest.py
import pytest

from go_starter import skillinstall


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    return home


@pytest.fixture
def installed_skill(fake_home):
    return skillinstall.install()
```

```python
# tests/test_skillinstall.py
from importlib.metadata import version

import pytest

from go_starter import skillinstall


def test_install_writes_the_skill_under_the_home_skills_dir(fake_home):
    dest = skillinstall.install()

    assert dest == fake_home / ".claude" / "skills" / "go-starter"
    assert (dest / "SKILL.md").read_text().startswith("---\nname: go-starter\n")
    assert (dest / "agents" / "openai.yaml").exists()


def test_install_creates_missing_parent_directories(fake_home):
    assert not (fake_home / ".claude").exists()

    skillinstall.install()

    assert (fake_home / ".claude" / "skills" / "go-starter" / "SKILL.md").exists()


def test_install_writes_version_stamp(installed_skill):
    lines = (installed_skill / "VERSION").read_text().splitlines()

    assert lines == [version("go-starter"), skillinstall.content_hash()]


def test_install_replaces_a_stale_copy(fake_home):
    stale = skillinstall.skill_dir() / "old.md"
    stale.parent.mkdir(parents=True)
    stale.write_text("stale")

    skillinstall.install()

    assert not stale.exists()


def test_content_hash_is_stable_and_prefixed():
    assert skillinstall.content_hash() == skillinstall.content_hash()
    assert skillinstall.content_hash().startswith("sha256:")


def test_check_passes_after_install(installed_skill):
    skillinstall.check()


def test_check_fails_when_not_installed(fake_home):
    with pytest.raises(skillinstall.SkillCheckError, match="not installed"):
        skillinstall.check()


def test_check_fails_when_hash_differs(installed_skill):
    (installed_skill / "VERSION").write_text("0.0.0\nsha256:deadbeef\n")

    with pytest.raises(
        skillinstall.SkillCheckError, match="outdated .*installed by 0.0.0"
    ):
        skillinstall.check()


def test_check_fails_when_version_file_missing(installed_skill):
    (installed_skill / "VERSION").unlink()

    with pytest.raises(
        skillinstall.SkillCheckError, match="outdated .*installed by unknown"
    ):
        skillinstall.check()
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run pytest tests/test_skillinstall.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'go_starter.skillinstall'`

- [ ] **Step 4: Write the implementation**

```python
# src/go_starter/skillinstall.py
"""Install and verify the Claude Code skill bundled with this package."""

import hashlib
import shutil
from importlib.metadata import version
from pathlib import Path

from go_starter import embedded

SKILL_NAME = "go-starter"
VERSION_FILE = "VERSION"
INSTALL_HINT = "Run: go-starter --install-skill"


class SkillCheckError(Exception):
    """The installed skill is missing or doesn't match this build."""


def skill_dir() -> Path:
    return Path.home() / ".claude" / "skills" / SKILL_NAME


def content_hash() -> str:
    digest = hashlib.sha256()
    for rel, entry in embedded.iter_files(embedded.resource("skills", SKILL_NAME)):
        digest.update(rel.encode())
        digest.update(entry.read_bytes())

    return f"sha256:{digest.hexdigest()}"


def install() -> Path:
    dest = skill_dir()
    if dest.exists():
        shutil.rmtree(dest)

    for rel, entry in embedded.iter_files(embedded.resource("skills", SKILL_NAME)):
        path = dest / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(entry.read_bytes())

    (dest / VERSION_FILE).write_text(f"{version('go-starter')}\n{content_hash()}\n")
    return dest


def check() -> None:
    dest = skill_dir()
    if not dest.exists():
        raise SkillCheckError(
            f"the {SKILL_NAME} skill is not installed.\n{INSTALL_HINT}"
        )

    installed_by, installed_hash = read_stamp(dest)
    if installed_hash == content_hash():
        return

    raise SkillCheckError(
        f"the {SKILL_NAME} skill is outdated (installed by {installed_by}, this is go-starter {version('go-starter')}).\n{INSTALL_HINT}"
    )


def read_stamp(dest: Path) -> tuple[str, str]:
    try:
        lines = (dest / VERSION_FILE).read_text().splitlines()
    except FileNotFoundError:
        return "unknown", ""

    installed_by = lines[0] if lines and lines[0] else "unknown"
    installed_hash = lines[1] if len(lines) > 1 else ""
    return installed_by, installed_hash
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_skillinstall.py tests/test_embedded.py -v`
Expected: all PASS (`test_embedded` still passes because the `skills/` glob was added in Task 3).

- [ ] **Step 6: Format and commit**

```bash
uv run ruff format && uv run ruff check
git add src/go_starter/skills src/go_starter/skillinstall.py tests/conftest.py tests/test_skillinstall.py
git commit -m "feat: bundle the go-starter skill and install it with a version stamp

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: CLI and entry point

**Files:**
- Modify: `src/go_starter/cli.py` (replace generated content)
- Modify: `src/go_starter/main.py` (replace generated content)
- Modify: `tests/test_cli.py`, `tests/test_main.py` (replace generated stubs)
- Create: `tests/test_integration_go.py`

**Interfaces:**
- Consumes: `names.*` (Task 2), `render.*` (Task 4), `skillinstall.*` (Task 5), fixtures from `tests/conftest.py` (Task 5).
- Produces: `cli.get_args(argv=None) -> argparse.Namespace` with `module: str | None`, `app_name: str | None`, `install_skill: bool`, `target: str`; `main.main(argv=None) -> int`.

- [ ] **Step 1: Write the failing CLI tests**

```python
# tests/test_cli.py
import pytest

from go_starter.cli import get_args


def test_module_and_default_target():
    args = get_args(["--module", "github.com/acme/tool"])

    assert args.module == "github.com/acme/tool"
    assert args.app_name is None
    assert args.target == "."
    assert args.install_skill is False


def test_explicit_app_name_and_target():
    args = get_args(
        ["--module", "github.com/acme/tool", "--app-name", "acme", "out/dir"]
    )

    assert args.app_name == "acme"
    assert args.target == "out/dir"


def test_install_skill_does_not_need_module():
    args = get_args(["--install-skill"])

    assert args.install_skill is True
    assert args.module is None


def test_module_is_required_otherwise():
    with pytest.raises(SystemExit) as exc:
        get_args([])

    assert exc.value.code == 2
```

- [ ] **Step 2: Write the failing main tests**

```python
# tests/test_main.py
from pathlib import Path

from go_starter.main import main


def test_scaffolds_into_a_new_target_dir(tmp_path, installed_skill, capsys):
    target = tmp_path / "new" / "proj"

    assert main(["--module", "github.com/acme/tool", str(target)]) == 0
    assert (
        (target / "src/go.mod").read_text().startswith("module github.com/acme/tool\n")
    )
    assert "BIN_NAME ?= tool\n" in (target / "Makefile").read_text()
    assert capsys.readouterr().out.strip() == f"Scaffolded tool in {target.resolve()}"


def test_honors_explicit_app_name(tmp_path, installed_skill):
    assert (
        main(["--module", "github.com/acme/tool", "--app-name", "acme", str(tmp_path)])
        == 0
    )
    assert "BIN_NAME ?= acme\n" in (tmp_path / "Makefile").read_text()


def test_refuses_to_run_without_the_skill(tmp_path, fake_home, capsys):
    assert main(["--module", "github.com/acme/tool", str(tmp_path)]) == 1
    assert "not installed" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


def test_rejects_bad_module_before_writing(tmp_path, installed_skill, capsys):
    assert main(["--module", "https://github.com/acme/tool", str(tmp_path)]) == 1
    assert "error: module path" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


def test_rejects_underivable_app_name_with_a_hint(tmp_path, installed_skill, capsys):
    assert main(["--module", "github.com/Acme/MyTool", str(tmp_path)]) == 1
    assert "--app-name" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


def test_refuses_non_empty_target_and_writes_nothing(tmp_path, installed_skill, capsys):
    (tmp_path / "notes.txt").touch()

    assert main(["--module", "github.com/acme/tool", str(tmp_path)]) == 1
    assert "blocking entry: notes.txt" in capsys.readouterr().err
    assert [p.name for p in tmp_path.iterdir()] == ["notes.txt"]


def test_target_that_is_a_file_is_an_error_not_a_traceback(
    tmp_path, installed_skill, capsys
):
    target = tmp_path / "afile"
    target.touch()

    assert main(["--module", "github.com/acme/tool", str(target)]) == 1
    assert capsys.readouterr().err.startswith("error: ")


def test_install_skill_prints_the_path_and_exits_zero(fake_home, capsys):
    assert main(["--install-skill"]) == 0
    assert capsys.readouterr().out.strip() == str(
        fake_home / ".claude/skills/go-starter"
    )
```

- [ ] **Step 3: Write the failing Go integration test**

```python
# tests/test_integration_go.py
import shutil
import subprocess

import pytest

from go_starter.main import main

pytestmark = pytest.mark.skipif(
    shutil.which("go") is None, reason="go toolchain not on PATH"
)


def test_rendered_project_compiles(tmp_path, installed_skill):
    assert main(["--module", "example.com/demo", str(tmp_path)]) == 0

    result = subprocess.run(
        ["go", "build", "-o", str(tmp_path / "demo"), "./cmd"],
        cwd=tmp_path / "src",
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "demo").exists()
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `uv run pytest tests/test_cli.py tests/test_main.py tests/test_integration_go.py -v`
Expected: FAIL. `test_cli` fails with `unrecognized arguments: --module`; `test_main` fails because the generated `main` returns `None` and prints `hello, world`.

- [ ] **Step 5: Replace `cli.py`**

```python
# src/go_starter/cli.py
import argparse
from importlib.metadata import version


def get_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="go-starter",
        description="Scaffold a new Go project from the bundled template.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {version('go-starter')}"
    )
    parser.add_argument(
        "--module", help="Go module path, for example github.com/acme/tool"
    )
    parser.add_argument(
        "--app-name", help="binary name (default: last segment of --module)"
    )
    parser.add_argument(
        "--install-skill",
        action="store_true",
        help="install the go-starter skill bundled with this build into ~/.claude/skills and exit",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="directory to scaffold into (default: current directory)",
    )
    args = parser.parse_args(argv)
    if not args.install_skill and args.module is None:
        parser.error("--module is required")

    return args
```

- [ ] **Step 6: Replace `main.py`**

```python
# src/go_starter/main.py
import sys
from pathlib import Path

from go_starter import names, render, skillinstall
from go_starter.cli import get_args

USER_ERRORS = (
    skillinstall.SkillCheckError,
    names.InvalidNameError,
    render.TargetNotEmptyError,
    FileExistsError,
    NotADirectoryError,
)


def main(argv=None) -> int:
    args = get_args(argv)
    if args.install_skill:
        return install_skill()

    return scaffold(args.module, args.app_name, Path(args.target))


def install_skill() -> int:
    print(skillinstall.install())
    return 0


def scaffold(module: str, app_name: str | None, target: Path) -> int:
    try:
        skillinstall.check()
        names.validate_module(module)
        app_name = names.validate_app_name(app_name or names.derive_app_name(module))
        # Created before the emptiness check so a brand-new path is a valid target.
        target.mkdir(parents=True, exist_ok=True)
        render.require_empty_target(target)
        render.render(target, {"GO_MODULE": module, "APP_NAME": app_name})
    except USER_ERRORS as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"Scaffolded {app_name} in {target.resolve()}")
    return 0
```

The console script wrapper generated for `[project.scripts]` calls `sys.exit(main())`, so the returned int becomes the exit code.

- [ ] **Step 7: Run the whole suite**

Run: `uv run pytest -v`
Expected: all PASS, including `test_rendered_project_compiles` (Go is on this machine). If `test_install_skill_prints_the_path_and_exits_zero` fails on path formatting, `print(Path)` is fine; check the fixture's `HOME`.

- [ ] **Step 8: Format, lint, commit**

```bash
uv run ruff format && uv run ruff check
git add src/go_starter/cli.py src/go_starter/main.py tests/test_cli.py tests/test_main.py tests/test_integration_go.py
git commit -m "feat: go-starter CLI with --install-skill gate

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Docs, build, and end-to-end verification

**Files:**
- Modify: `README.md` (replace generated content)
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Write the README**

```markdown
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
```

Add under `## Unreleased` in `CHANGELOG.md`: `- Initial release: scaffold a Go project, install the bundled Claude skill with --install-skill.`

- [ ] **Step 2: Full local gate**

```bash
make test
make build
```

Expected: both exit 0; `dist/go_starter-0.0.1-py3-none-any.whl` exists. `make build` requires Docker; if `docker info` fails, stop and report rather than skipping.

- [ ] **Step 3: Install and exercise the skill gate**

```bash
make install
go-starter --version                       # go-starter 0.0.1
D=$(mktemp -d); go-starter --module example.com/demo "$D"; echo "exit=$?"
```

Expected: `error: the go-starter skill is not installed.` then `Run: go-starter --install-skill`, `exit=1`, and `ls -A "$D"` prints nothing. (If a go-starter skill was already installed from an earlier build, expect the `outdated` message instead.)

```bash
go-starter --install-skill                  # prints /home/jeremy/.claude/skills/go-starter
cat ~/.claude/skills/go-starter/VERSION     # 0.0.1 then sha256:...
```

- [ ] **Step 4: Scaffold a real project and build it both ways**

```bash
go-starter --module example.com/demo "$D" && cd "$D"
grep -r '{{' . ; find . -name '*.tmpl'     # both print nothing
make local && ./.bin/local/demo             # Why, hello there!
make build && ls .bin/*/*/demo              # four binaries
```

Expected: `make local` runs goimports, golangci-lint, govulncheck, gosec, `go test`, then builds; `make build` exports `.bin/{amd64,arm64}/{darwin,linux}/demo`.

- [ ] **Step 5: Confirm the skill fires**

Open a new Claude Code session in another empty directory and say "stand up a new Go project for module example.com/probe". Expected: the `go-starter` skill is invoked, it runs the CLI, then runs `make local`. Then `cd .. && rm -rf` that probe directory and `$D`.

- [ ] **Step 6: Commit**

```bash
cd ~/dev/scratch/go-starter
uv run ruff format && uv run ruff check
git add README.md CHANGELOG.md
git commit -m "docs: README and changelog for go-starter

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

- [ ] **Step 7: Report**

Tell the user everything in Steps 2 to 5 passed with the observed output, and that `~/dev/scratch/go-basic-project` is now redundant. Do not delete it; that's their call.
