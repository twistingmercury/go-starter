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
        f"the {SKILL_NAME} skill is outdated (installed by {installed_by}, "
        f"this is go-starter {version('go-starter')}).\n{INSTALL_HINT}"
    )


def read_stamp(dest: Path) -> tuple[str, str]:
    try:
        lines = (dest / VERSION_FILE).read_text().splitlines()
    except FileNotFoundError:
        return "unknown", ""

    installed_by = lines[0] if lines and lines[0] else "unknown"
    installed_hash = lines[1] if len(lines) > 1 else ""
    return installed_by, installed_hash
