"""Shared fixtures for wt-project-base tests."""

import pytest
from pathlib import Path

import yaml

from wt_project_base.project_type import BaseProjectType


@pytest.fixture
def base_pt():
    """A BaseProjectType instance."""
    return BaseProjectType()


@pytest.fixture
def overlay_yaml(tmp_path):
    """Write a YAML overlay file and return its path.

    Usage: overlay_yaml({"disabled_rules": ["file-size-limit"]})
    """
    def _write(data: dict) -> Path:
        p = tmp_path / "project-type.yaml"
        p.write_text(yaml.dump(data, default_flow_style=False))
        return p
    return _write


@pytest.fixture
def template_dir(tmp_path):
    """Create a minimal template directory with manifest and files."""
    tdir = tmp_path / "template"
    tdir.mkdir()

    # Core file
    (tdir / "project-knowledge.yaml").write_text("version: 1\n")

    # Module file
    rules_dir = tdir / "rules"
    rules_dir.mkdir()
    (rules_dir / "extra.md").write_text("# Extra rule\n")

    # Manifest
    manifest = {
        "core": ["project-knowledge.yaml"],
        "modules": {
            "extras": {
                "description": "Extra rules",
                "files": ["rules/extra.md"],
            }
        },
    }
    (tdir / "manifest.yaml").write_text(yaml.dump(manifest, default_flow_style=False))

    return tdir
