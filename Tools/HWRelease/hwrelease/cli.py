"""Command-line interface for hwrelease."""

import argparse
import sys
from pathlib import Path

from . import core


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="hwrelease",
        description="Export hardware release artifacts from InverterGen5 tags.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_up = sub.add_parser("update",
                          help="export missing board revisions from release tags")
    p_up.add_argument("--hw-repo", type=Path, default=None,
                      help="path to the hardware repo (default: from Config/Products.yaml)")
    p_up.add_argument("--tag", default=None, help="export only this tag")
    p_up.add_argument("--tag-pattern", default="*",
                      help="git tag glob for discovery (default: all tags)")
    p_up.add_argument("--force", action="store_true",
                      help="regenerate even if already in the manifest")

    p_show = sub.add_parser("show", help="show artifacts for a part number")
    p_show.add_argument("part_number", help="e.g. HW-C2-PCB-CTRL-A")

    sub.add_parser("list", help="list all exported board revisions")

    sub.add_parser("build-viewer",
                   help="regenerate the PCB assembly viewer page from the manifest")

    args = parser.parse_args(argv)
    if args.command == "update":
        hw_repo = args.hw_repo or core.default_hw_repo()
        if not (hw_repo / ".git").is_dir():
            print(f"error: {hw_repo} is not a git repository", file=sys.stderr)
            return 2
        return core.update(hw_repo, tag_pattern=args.tag_pattern,
                           only_tag=args.tag, force=args.force)
    if args.command == "show":
        return core.show(args.part_number)
    if args.command == "list":
        return core.list_boards()
    if args.command == "build-viewer":
        from . import viewer
        return viewer.build_viewer()
    return 2


if __name__ == "__main__":
    sys.exit(main())
