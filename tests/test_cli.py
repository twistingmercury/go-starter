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
