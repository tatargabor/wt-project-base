"""Tests for BaseProjectType."""

from wt_project_base.project_type import BaseProjectType


def test_info(base_pt):
    info = base_pt.info
    assert info.name == "base"
    assert info.version == "0.1.0"
    assert info.parent is None


def test_verification_rules_count(base_pt):
    rules = base_pt.get_verification_rules()
    assert len(rules) == 3


def test_verification_rule_ids(base_pt):
    ids = {r.id for r in base_pt.get_verification_rules()}
    assert ids == {"file-size-limit", "no-secrets-in-source", "todo-tracking"}


def test_orchestration_directives_count(base_pt):
    directives = base_pt.get_orchestration_directives()
    assert len(directives) == 4


def test_orchestration_directive_ids(base_pt):
    ids = {d.id for d in base_pt.get_orchestration_directives()}
    assert ids == {"install-deps-npm", "install-deps-python", "no-parallel-lockfile", "config-review"}


def test_templates(base_pt):
    templates = base_pt.get_templates()
    assert len(templates) == 1
    assert templates[0].id == "default"


def test_template_dir_resolves(base_pt):
    tdir = base_pt.get_template_dir("default")
    assert tdir is not None
    assert tdir.is_dir()
    assert (tdir / "manifest.yaml").exists()


def test_template_dir_unknown_returns_none(base_pt):
    assert base_pt.get_template_dir("nonexistent") is None


def test_secrets_rule_has_error_severity(base_pt):
    rules = {r.id: r for r in base_pt.get_verification_rules()}
    assert rules["no-secrets-in-source"].severity == "error"
