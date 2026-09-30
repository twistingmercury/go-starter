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
