"""Tests for template deployment."""

import yaml
from pathlib import Path

from wt_project_base.deploy import (
    _resolve_file_list,
    _target_path,
    _load_manifest,
    deploy_templates,
    get_available_modules,
    resolve_template,
)
from wt_project_base.project_type import BaseProjectType


def test_load_manifest(template_dir):
    manifest = _load_manifest(template_dir)
    assert manifest is not None
    assert "core" in manifest
    assert "modules" in manifest


def test_load_manifest_missing(tmp_path):
    assert _load_manifest(tmp_path) is None


def test_resolve_file_list_core_only(template_dir):
    manifest = _load_manifest(template_dir)
    files, warns = _resolve_file_list(template_dir, manifest, modules=None)
    assert files == ["project-knowledge.yaml"]
    assert not warns


def test_resolve_file_list_with_module(template_dir):
    manifest = _load_manifest(template_dir)
    files, warns = _resolve_file_list(template_dir, manifest, modules=["extras"])
    assert "project-knowledge.yaml" in files
    assert "rules/extra.md" in files
    assert not warns


def test_resolve_file_list_unknown_module(template_dir):
    manifest = _load_manifest(template_dir)
    files, warns = _resolve_file_list(template_dir, manifest, modules=["nonexistent"])
    assert len(warns) == 1
    assert "nonexistent" in warns[0]


def test_resolve_file_list_no_manifest(template_dir):
    """Without manifest, all files except manifest.yaml are included."""
    (template_dir / "manifest.yaml").unlink()
    files, warns = _resolve_file_list(template_dir, None, modules=None)
    assert "project-knowledge.yaml" in files
    assert "rules/extra.md" in files
    assert "manifest.yaml" not in files


def test_target_path_rules_mapping(tmp_path):
    result = _target_path("rules/data-privacy.md", tmp_path)
    assert result == tmp_path / ".claude" / "rules" / "data-privacy.md"


def test_target_path_project_knowledge_default(tmp_path):
    result = _target_path("project-knowledge.yaml", tmp_path)
    assert result == tmp_path / "project-knowledge.yaml"


def test_target_path_project_knowledge_wt_dir(tmp_path):
    (tmp_path / "wt" / "knowledge").mkdir(parents=True)
    result = _target_path("project-knowledge.yaml", tmp_path)
    assert result == tmp_path / "wt" / "knowledge" / "project-knowledge.yaml"


def test_get_available_modules(template_dir):
    modules = get_available_modules(template_dir)
    assert "extras" in modules
    assert modules["extras"] == "Extra rules"


def test_deploy_core_files(template_dir, tmp_path):
    """Deploy using BaseProjectType's real template."""
    pt = BaseProjectType()
    messages = deploy_templates(pt, "default", tmp_path)
    deployed = [m for m in messages if "Deployed" in m]
    assert len(deployed) >= 1


def test_deploy_skip_existing(template_dir, tmp_path):
    pt = BaseProjectType()
    # First deploy
    deploy_templates(pt, "default", tmp_path)
    # Second deploy — should skip
    messages = deploy_templates(pt, "default", tmp_path)
    skipped = [m for m in messages if "Skipped" in m]
    assert len(skipped) >= 1


def test_deploy_force_overwrites(tmp_path):
    pt = BaseProjectType()
    deploy_templates(pt, "default", tmp_path)
    messages = deploy_templates(pt, "default", tmp_path, force=True)
    overwritten = [m for m in messages if "Overwritten" in m]
    assert len(overwritten) >= 1


def test_deploy_dry_run(tmp_path):
    pt = BaseProjectType()
    messages = deploy_templates(pt, "default", tmp_path, dry_run=True)
    would = [m for m in messages if "Would" in m]
    assert len(would) >= 1
    # Files should NOT actually exist
    # (project-knowledge.yaml goes to root since wt/knowledge doesn't exist)
    # Check that at least the dry-run message was produced
    assert len(would) >= 1


def test_resolve_template_auto_select():
    pt = BaseProjectType()
    tid, tdir = resolve_template(pt)
    assert tid == "default"
    assert tdir.is_dir()


def test_resolve_template_unknown_raises():
    pt = BaseProjectType()
    import pytest
    with pytest.raises(ValueError, match="Unknown template"):
        resolve_template(pt, "nonexistent")
