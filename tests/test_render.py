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
    assert (
        (tmp_path / ".github/workflows/ci.yaml")
        .read_text()
        .startswith("name: demo CI\n")
    )
    assert (tmp_path / ".shellcheckrc").exists()


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
