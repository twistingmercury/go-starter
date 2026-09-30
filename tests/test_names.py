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
