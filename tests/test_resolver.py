"""Tests for ProjectTypeResolver."""

import yaml
from pathlib import Path

from wt_project_base.project_type import BaseProjectType
from wt_project_base.resolver import ProjectTypeResolver


def test_no_overlay_returns_package_rules(base_pt, tmp_path):
    overlay = tmp_path / "project-type.yaml"  # does not exist
    resolver = ProjectTypeResolver(base_pt, overlay)
    rules = resolver.resolve_rules()
    assert len(rules) == 3


def test_disabled_rule_removed(base_pt, overlay_yaml):
    path = overlay_yaml({"disabled_rules": ["file-size-limit"]})
    resolver = ProjectTypeResolver(base_pt, path)
    rules = resolver.resolve_rules()
    ids = {r.id for r in rules}
    assert "file-size-limit" not in ids
    assert len(rules) == 2


def test_rule_override_merges_config(base_pt, overlay_yaml):
    path = overlay_yaml({
        "rule_overrides": {
            "file-size-limit": {
                "config": {"max_lines": 800},
            }
        }
    })
    resolver = ProjectTypeResolver(base_pt, path)
    rules = {r.id: r for r in resolver.resolve_rules()}
    assert rules["file-size-limit"].config["max_lines"] == 800
    # Original config key should still be there
    assert "pattern" in rules["file-size-limit"].config


def test_rule_override_changes_severity(base_pt, overlay_yaml):
    path = overlay_yaml({
        "rule_overrides": {
            "todo-tracking": {"severity": "warning"},
        }
    })
    resolver = ProjectTypeResolver(base_pt, path)
    rules = {r.id: r for r in resolver.resolve_rules()}
    assert rules["todo-tracking"].severity == "warning"


def test_custom_rule_appended(base_pt, overlay_yaml):
    path = overlay_yaml({
        "custom_rules": [{
            "id": "my-custom-rule",
            "description": "A custom rule",
            "check": "custom",
            "severity": "error",
        }]
    })
    resolver = ProjectTypeResolver(base_pt, path)
    rules = resolver.resolve_rules()
    ids = {r.id for r in rules}
    assert "my-custom-rule" in ids
    assert len(rules) == 4


def test_custom_directive_appended(base_pt, overlay_yaml):
    path = overlay_yaml({
        "custom_directives": [{
            "id": "my-directive",
            "description": "A custom directive",
            "trigger": "always",
            "action": "warn",
        }]
    })
    resolver = ProjectTypeResolver(base_pt, path)
    directives = resolver.resolve_directives()
    ids = {d.id for d in directives}
    assert "my-directive" in ids
    assert len(directives) == 5


def test_disabled_directive_removed(base_pt, overlay_yaml):
    path = overlay_yaml({"disabled_directives": ["config-review"]})
    resolver = ProjectTypeResolver(base_pt, path)
    directives = resolver.resolve_directives()
    ids = {d.id for d in directives}
    assert "config-review" not in ids


def test_unknown_disabled_rule_produces_warning(base_pt, overlay_yaml):
    path = overlay_yaml({"disabled_rules": ["nonexistent-rule"]})
    resolver = ProjectTypeResolver(base_pt, path)
    resolver.resolve_rules()  # trigger resolution
    warnings = resolver.get_warnings()
    assert any("nonexistent-rule" in w for w in warnings)


def test_unknown_disabled_directive_produces_warning(base_pt, overlay_yaml):
    path = overlay_yaml({"disabled_directives": ["nonexistent-dir"]})
    resolver = ProjectTypeResolver(base_pt, path)
    resolver.resolve_directives()
    warnings = resolver.get_warnings()
    assert any("nonexistent-dir" in w for w in warnings)


def test_local_overrides_layered(base_pt, tmp_path):
    # Main overlay disables one rule
    main = tmp_path / "project-type.yaml"
    main.write_text(yaml.dump({"disabled_rules": ["file-size-limit"]}))

    # Local overrides disables another
    local = tmp_path / ".local-overrides.yaml"
    local.write_text(yaml.dump({"disabled_rules": ["todo-tracking"]}))

    resolver = ProjectTypeResolver(base_pt, main)
    rules = resolver.resolve_rules()
    ids = {r.id for r in rules}
    assert "file-size-limit" not in ids
    assert "todo-tracking" not in ids
    assert len(rules) == 1  # only no-secrets-in-source remains


def test_summary_counts(base_pt, overlay_yaml):
    path = overlay_yaml({
        "disabled_rules": ["todo-tracking"],
        "custom_rules": [{"id": "x", "description": "x", "check": "x"}],
        "rule_overrides": {"file-size-limit": {"config": {"max_lines": 999}}},
    })
    resolver = ProjectTypeResolver(base_pt, path)
    summary = resolver.summary()
    assert summary["rules"]["from_package"] == 3
    assert summary["rules"]["disabled"] == 1
    assert summary["rules"]["custom"] == 1
    assert summary["rules"]["overridden"] == 1
    assert summary["rules"]["total"] == 3  # 3 package - 1 disabled + 1 custom
