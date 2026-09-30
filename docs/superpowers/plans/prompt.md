# go-starter

You are running one task from a Gralph loop. The task follows this prompt,
starting with a line `<id>: <name>`; everything after that line is the task's
own instructions. You have no memory of earlier tasks, so check any claim about
prior work against the repository.

## Project

- Repository: `/home/jeremy/dev/scratch/go-starter`, a Python >= 3.12,
  stdlib-only CLI managed with uv. Package `go_starter` under `src/`, tests
  under `tests/`.
- Context documents: `docs/superpowers/plans/2026-09-29-go-starter.md` is the
  implementation plan. Its "Context" and "Global Constraints" sections are the
  spec, and the code and tests inside each plan task are the reference
  implementation. Each Gralph task names the plan task it implements and lists
  every deviation from it. Where the Gralph task and the plan disagree, the
  Gralph task wins. Ignore the plan's own commit and checkbox steps; this
  prompt's commit rules apply instead.
- Reference material outside the repo, read-only:
  `/home/jeremy/dev/scratch/go-basic-project` (the Go project the template is
  copied from), `/home/jeremy/dev/gralph/internal/skillinstall/skillinstall.go`
  and `/home/jeremy/dev/gralph/cmd/main/main.go` (skill install semantics),
  `/home/jeremy/.claude/skills/python-uv-starter/SKILL.md` (skill shape).
- Code shape: early returns with the happy path at the left margin, a blank
  line after every `if` block except before a closing brace or `else`, named
  functions instead of multi-line inline callbacks, one job per function,
  comments explain why not what, no `# noqa` or other linter suppressions.
  `dependencies = []` stays empty; dev deps are only `pytest` and `ruff`.
- Build and test, all run from the repository root, all must exit 0:
  1. `make test` (ruff format, ruff check --fix, uv sync, ruff check, pytest)
  2. `uv run ruff format --check`
  3. `make build` (Docker-first: `ruff format --check`, `ruff check`, pytest on
     Python 3.12, then `uv build`; wheel lands in `dist/`). Requires a running
     Docker daemon. If `docker info` fails, the task fails; do not skip it.
  4. After committing, `git status --porcelain` prints nothing except
     `docs/superpowers/plans/tasks.yaml`, which Gralph owns and rewrites.
  The wheel version comes from `git describe --tags`; with no tags it is
  `0.0.0.dev0`. Never hardcode a version in checks; use `dist/go_starter-*.whl`.
- Commits: after all four gates pass, commit this task's work with a
  conventional message (`feat:`, `chore:`, `docs:`, `test:`) whose body ends
  with the line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
  Stage only the files the task touched, never `docs/superpowers/plans/tasks.yaml`.
  Never push, tag, or rewrite history.

## Rules

- Do only this task, within its stated scope. There is no retry and no later
  session to defer work to.
- Never edit `tasks.yaml`; Gralph owns task state.
- Preserve unrelated changes in the workspace and Git.
- Run the task's verification. Never claim an outcome it does not support.
- Clean up anything you created that the task does not keep.
- Commit only as the commit rules above allow, and only after verification
  passes. Keep `tasks.yaml` out of commits.

## Finish

End with a short report of what changed, each verification command and its
result, and what was committed. The last non-blank line of your output must be
this JSON object, on a single line, with nothing else on that line and no code
block around it:

{"state": "completed", "error": ""}

`state` is `completed` only when the work, its verification, cleanup, and any
required commit all succeeded; otherwise it is `failed`, with a one-line
`error`.
