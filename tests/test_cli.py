import pytest

from go_starter.cli import get_args


def test_version_flag_prints_version_and_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        get_args(["--version"])

    assert exc.value.code == 0
    assert "go-starter" in capsys.readouterr().out


def test_unknown_flag_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        get_args(["--bogus"])

    assert exc.value.code == 2
    assert "--bogus" in capsys.readouterr().err
