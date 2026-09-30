import argparse
from importlib.metadata import version


def get_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="go-starter",
        description="Scaffold a new Go project from the bundled template.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {version('go-starter')}"
    )
    parser.add_argument(
        "--module", help="Go module path, for example github.com/acme/tool"
    )
    parser.add_argument(
        "--app-name", help="binary name (default: last segment of --module)"
    )
    parser.add_argument(
        "--install-skill",
        action="store_true",
        help="install the go-starter skill bundled with this build into ~/.claude/skills and exit",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="directory to scaffold into (default: current directory)",
    )
    args = parser.parse_args(argv)
    if not args.install_skill and args.module is None:
        parser.error("--module is required")

    return args
