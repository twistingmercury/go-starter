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
