"""CLI for wt-project-base — list available rules and directives."""

import argparse
import json
import sys
from dataclasses import asdict

from wt_project_base.project_type import BaseProjectType


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="wt-project-base",
        description="Base project type — list rules and directives",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("rules", help="List verification rules")
    subparsers.add_parser("directives", help="List orchestration directives")
    info_parser = subparsers.add_parser("info", help="Show project type info")

    args = parser.parse_args()
    pt = BaseProjectType()

    if args.command == "rules":
        for rule in pt.get_verification_rules():
            print(f"  [{rule.severity:7s}] {rule.id}: {rule.description}")
    elif args.command == "directives":
        for d in pt.get_orchestration_directives():
            print(f"  [{d.action:16s}] {d.id}: {d.description}")
    elif args.command == "info":
        info = pt.info
        print(f"Name:        {info.name}")
        print(f"Version:     {info.version}")
        print(f"Description: {info.description}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
