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
        # A symlinked metadata dir could point anywhere, so it doesn't get a pass.
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
