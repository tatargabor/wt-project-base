"""CLI for wt-project-base — resolve rules, manage feedback."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from wt_project_base.project_type import BaseProjectType


def _load_project_type_from_dir(project_dir: Path):
    """Load project type from wt/plugins/project-type.yaml via entry points."""
    try:
        import yaml
    except ImportError:
        print("Error: PyYAML required. pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    pt_file = project_dir / "wt" / "plugins" / "project-type.yaml"
    if not pt_file.exists():
        return BaseProjectType(), pt_file

    with open(pt_file) as f:
        data = yaml.safe_load(f) or {}

    type_name = data.get("type", "base")

    try:
        from importlib.metadata import entry_points
    except ImportError:
        from importlib_metadata import entry_points  # type: ignore

    try:
        eps = entry_points(group="wt_tools.project_types")
    except TypeError:
        eps = entry_points().get("wt_tools.project_types", [])

    for ep in eps:
        if ep.name == type_name:
            cls = ep.load()
            return cls(), pt_file

    print(f"Warning: project type '{type_name}' not found, using base", file=sys.stderr)
    return BaseProjectType(), pt_file


def cmd_resolve(args):
    """Resolve and display merged rules and directives."""
    from wt_project_base.resolver import ProjectTypeResolver

    project_dir = Path(args.project_dir).resolve()
    pt, pt_file = _load_project_type_from_dir(project_dir)
    resolver = ProjectTypeResolver(pt, pt_file)

    rules = resolver.resolve_rules()
    directives = resolver.resolve_directives()
    summary = resolver.summary()
    warnings = resolver.get_warnings()

    # Determine which rules are custom/overridden for annotation
    pkg_rule_ids = {r.id for r in pt.get_verification_rules()}
    override_ids = set()
    for ov_source in [resolver._overlay, resolver._local]:
        if ov_source:
            override_ids.update(ov_source.get("rule_overrides", {}).keys())

    print(f"Project type: {pt.info.name} (v{pt.info.version})")
    print(f"Overlay: {pt_file}")
    if resolver._local_path.exists():
        print(f"Local overrides: {resolver._local_path}")
    print()

    print(f"Verification rules ({summary['rules']['total']}):")
    for rule in rules:
        source = "custom" if rule.id not in pkg_rule_ids else "override" if rule.id in override_ids else "package"
        print(f"  [{rule.severity:7s}] {rule.id}: {rule.description}  ({source})")

    print(f"\nOrchestration directives ({summary['directives']['total']}):")
    pkg_dir_ids = {d.id for d in pt.get_orchestration_directives()}
    for d in directives:
        source = "custom" if d.id not in pkg_dir_ids else "package"
        print(f"  [{d.action:16s}] {d.id}: {d.description}  ({source})")

    print(f"\nSummary:")
    rs = summary["rules"]
    print(f"  Rules: {rs['total']} total ({rs['from_package']} package, {rs['custom']} custom, {rs['disabled']} disabled, {rs['overridden']} overridden)")
    ds = summary["directives"]
    print(f"  Directives: {ds['total']} total ({ds['from_package']} package, {ds['custom']} custom, {ds['disabled']} disabled)")

    if warnings:
        print(f"\nWarnings:")
        for w in warnings:
            print(f"  ⚠ {w}")


def cmd_feedback_record(args):
    """Record a feedback lesson."""
    from wt_project_base.feedback import FeedbackLesson, FeedbackStore, SuggestedFix, VALID_ISSUE_TYPES

    project_dir = Path(args.project_dir).resolve()
    store_path = project_dir / "wt" / "knowledge" / "lessons" / "rule-feedback.yaml"

    fix = None
    if args.fix_type and args.fix_value:
        fix = SuggestedFix(type=args.fix_type, value=args.fix_value)

    lesson = FeedbackLesson(
        rule_id=args.rule_id,
        issue=args.issue,
        context=args.context,
        suggested_fix=fix,
    )

    store = FeedbackStore(store_path)
    errors = store.append(lesson)
    if errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Recorded feedback for rule '{args.rule_id}' → {store_path}")


def cmd_feedback_export(args):
    """Export feedback lessons as anonymized YAML."""
    from wt_project_base.feedback import FeedbackStore

    project_dir = Path(args.project_dir).resolve()
    store_path = project_dir / "wt" / "knowledge" / "lessons" / "rule-feedback.yaml"

    if not store_path.exists():
        print("No feedback lessons found.", file=sys.stderr)
        sys.exit(0)

    store = FeedbackStore(store_path)
    print(store.export())


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="wt-project-base",
        description="Base project type — resolve rules, manage feedback",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Existing commands
    subparsers.add_parser("rules", help="List base verification rules")
    subparsers.add_parser("directives", help="List base orchestration directives")
    subparsers.add_parser("info", help="Show project type info")

    # Resolve command
    resolve_parser = subparsers.add_parser("resolve", help="Show merged rules and directives for a project")
    resolve_parser.add_argument("--project-dir", default=".", help="Project directory (default: current)")

    # Feedback commands
    feedback_parser = subparsers.add_parser("feedback", help="Manage feedback lessons")
    fb_sub = feedback_parser.add_subparsers(dest="fb_command")

    record_parser = fb_sub.add_parser("record", help="Record a feedback lesson")
    record_parser.add_argument("--project-dir", default=".", help="Project directory")
    record_parser.add_argument("--rule-id", required=True, help="Rule ID")
    record_parser.add_argument("--issue", required=True, help="Issue type: false_positive, too_aggressive, missing_exclude, missing_rule, config_improvement")
    record_parser.add_argument("--context", required=True, help="Description (no project names!)")
    record_parser.add_argument("--fix-type", help="Suggested fix type")
    record_parser.add_argument("--fix-value", help="Suggested fix value")

    export_parser = fb_sub.add_parser("export", help="Export anonymized feedback")
    export_parser.add_argument("--project-dir", default=".", help="Project directory")

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
    elif args.command == "resolve":
        cmd_resolve(args)
    elif args.command == "feedback":
        if args.fb_command == "record":
            cmd_feedback_record(args)
        elif args.fb_command == "export":
            cmd_feedback_export(args)
        else:
            feedback_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
