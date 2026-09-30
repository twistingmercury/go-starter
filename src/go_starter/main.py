import sys
from pathlib import Path

from go_starter import names, render, skillinstall
from go_starter.cli import get_args

USER_ERRORS = (
    skillinstall.SkillCheckError,
    names.InvalidNameError,
    render.TargetNotEmptyError,
    FileExistsError,
    NotADirectoryError,
)


def main(argv=None) -> int:
    args = get_args(argv)
    if args.install_skill:
        return install_skill()

    return scaffold(args.module, args.app_name, Path(args.target))


def install_skill() -> int:
    print(skillinstall.install())
    return 0


def scaffold(module: str, app_name: str | None, target: Path) -> int:
    try:
        skillinstall.check()
        names.validate_module(module)
        app_name = names.validate_app_name(app_name or names.derive_app_name(module))
        # Created before the emptiness check so a brand-new path is a valid target.
        target.mkdir(parents=True, exist_ok=True)
        render.require_empty_target(target)
        render.render(target, {"GO_MODULE": module, "APP_NAME": app_name})
    except USER_ERRORS as err:
        print(f"error: {err}", file=sys.stderr)
        return 1

    print(f"Scaffolded {app_name} in {target.resolve()}")
    return 0
