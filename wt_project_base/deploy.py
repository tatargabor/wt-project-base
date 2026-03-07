"""Deploy template files from a project type package into a target project."""

import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from wt_project_base.base import ProjectType


# Map template-relative paths to target-relative paths
_PATH_MAPPINGS: Dict[str, str] = {
    "rules/": ".claude/rules/",
}


def _target_path(template_rel: str, target_dir: Path) -> Path:
    """Map a template-relative path to the target directory location."""
    # project-knowledge.yaml → wt/knowledge/ if it exists, else project root
    if template_rel == "project-knowledge.yaml":
        wt_knowledge = target_dir / "wt" / "knowledge"
        if wt_knowledge.is_dir():
            return wt_knowledge / template_rel
        return target_dir / template_rel

    # Apply path mappings (e.g., rules/ → .claude/rules/)
    for prefix, target_prefix in _PATH_MAPPINGS.items():
        if template_rel.startswith(prefix):
            return target_dir / target_prefix / template_rel[len(prefix):]

    # Default: same relative path
    return target_dir / template_rel


def resolve_template(
    project_type: ProjectType,
    template_id: Optional[str] = None,
) -> Tuple[str, Path]:
    """Resolve which template to use, returning (template_id, template_dir).

    If template_id is None and only one template exists, auto-select it.
    Raises ValueError if template_id is needed but not provided, or if
    the specified template doesn't exist.
    """
    templates = project_type.get_templates()

    if not templates:
        raise ValueError(
            f"Project type '{project_type.info.name}' has no templates"
        )

    if template_id is None:
        if len(templates) == 1:
            template_id = templates[0].id
        else:
            names = ", ".join(t.id for t in templates)
            raise ValueError(
                f"Multiple templates available for '{project_type.info.name}': "
                f"{names}. Use --template <name> to select one."
            )

    template_dir = project_type.get_template_dir(template_id)
    if template_dir is None or not template_dir.is_dir():
        names = ", ".join(t.id for t in templates)
        raise ValueError(
            f"Unknown template '{template_id}' for project type "
            f"'{project_type.info.name}'. Available: {names}"
        )

    return template_id, template_dir


def deploy_templates(
    project_type: ProjectType,
    template_id: Optional[str],
    target_dir: Path,
    force: bool = False,
    dry_run: bool = False,
) -> List[str]:
    """Deploy template files from a project type into the target directory.

    Returns a list of status messages for each file (deployed/skipped/overwritten).
    """
    resolved_id, template_dir = resolve_template(project_type, template_id)
    messages: List[str] = []

    # Walk the template directory and copy files
    for src_path in sorted(template_dir.rglob("*")):
        if src_path.is_dir():
            continue

        rel = str(src_path.relative_to(template_dir))
        dst = _target_path(rel, target_dir)

        if dst.exists() and not force:
            messages.append(f"  Skipped (exists): {dst.relative_to(target_dir)}")
            continue

        verb = "Would deploy" if dry_run else "Deployed"
        if dst.exists() and force:
            verb = "Would overwrite" if dry_run else "Overwritten"

        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst)

        messages.append(f"  {verb}: {dst.relative_to(target_dir)}")

    return messages
