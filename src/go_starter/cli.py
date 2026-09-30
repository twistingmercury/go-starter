import argparse
from importlib.metadata import version


def get_args(argv=None):
    parser = argparse.ArgumentParser(prog="go-starter")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {version('go-starter')}",
    )
    return parser.parse_args(argv)
