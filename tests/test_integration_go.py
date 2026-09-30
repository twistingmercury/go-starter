import shutil
import subprocess

import pytest

from go_starter.main import main

pytestmark = pytest.mark.skipif(
    shutil.which("go") is None, reason="go toolchain not on PATH"
)


def test_rendered_project_compiles(tmp_path, installed_skill):
    target = tmp_path / "proj"

    assert main(["--module", "example.com/demo", str(target)]) == 0

    result = subprocess.run(
        ["go", "build", "-o", str(target / "demo"), "./cmd"],
        cwd=target / "src",
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (target / "demo").exists()
