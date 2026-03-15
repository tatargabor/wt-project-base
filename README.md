# wt-project-base

Abstract base layer for [wt-tools](https://github.com/tatargabor/wt-tools) project type plugins. Provides the `ProjectType` ABC, universal verification rules, orchestration directives, and infrastructure (resolver, template deploy, feedback) that all concrete plugins inherit.

**This package is never used directly.** Every project needs a specific project type plugin for its stack — [wt-project-web](https://github.com/tatargabor/wt-project-web) for modern web apps, or your own for Python, Laravel, Go, etc.

## Plugin Architecture

```
wt-project-base              Universal rules (file size, secrets, TODOs)
  ├── wt-project-web          Modern web (i18n, routing, DB migrations, components, design)
  ├── wt-project-python       Python projects (your org creates this)
  ├── wt-project-laravel      Laravel projects (your org creates this)
  └── your-org-custom         Any stack — extend base or another plugin
```

Each layer inherits rules and directives from its parent. Customize per-project via `wt/plugins/project-type.yaml` without writing Python.

## What BaseProjectType Ships

### Verification Rules

| ID | Severity | Description |
|----|----------|-------------|
| `file-size-limit` | warning | Source files should not exceed 400 lines |
| `no-secrets-in-source` | error | No hardcoded API keys, secrets, or passwords |
| `todo-tracking` | info | TODO/FIXME/HACK comments should reference an issue |

### Orchestration Directives

| ID | Action | Description |
|----|--------|-------------|
| `install-deps-npm` | post-merge | Run `npm install` after package.json changes |
| `install-deps-python` | post-merge | Run `pip install -e .` after pyproject.toml changes |
| `no-parallel-lockfile` | serialize | Serialize changes that modify lock files |
| `config-review` | flag-for-review | Flag CI/CD and infra config changes for review |

## API Reference

### ProjectType ABC

The base class every project type plugin must implement:

```python
from wt_project_base import ProjectType

class MyProjectType(ProjectType):
    @property
    def info(self) -> ProjectTypeInfo:
        """Return project type metadata."""

    def get_templates(self) -> List[TemplateInfo]:
        """Return available template variants."""

    def get_verification_rules(self) -> List[VerificationRule]:
        """Return verification rules for this project type."""

    def get_orchestration_directives(self) -> List[OrchestrationDirective]:
        """Return orchestration directives for this project type."""
```

### Profile Methods (Optional)

These methods integrate with the wt-tools orchestration engine. Override them to provide stack-specific behavior:

| Method | Purpose | Default |
|--------|---------|---------|
| `planning_rules()` | Quality patterns for decompose prompt | `[]` |
| `security_rules_paths()` | Paths to security rule files for review | `[]` |
| `security_checklist()` | Security checklist items for proposals | `[]` |
| `generated_file_patterns()` | Glob patterns for auto-resolved merge files | `[]` |
| `detect_package_manager()` | Detect PM from lockfiles | `None` |
| `detect_test_command()` | Read test command from project config | `None` |
| `detect_build_command()` | Read build command from project config | `None` |
| `detect_dev_server()` | Read dev server command | `None` |
| `bootstrap_worktree()` | Install deps in new worktree | no-op |
| `post_merge_install()` | Install deps after merge | no-op |
| `ignore_patterns()` | Glob patterns to exclude from digest/codemap | `[]` |
| `gate_overrides(change_type)` | Per-change-type verify gate config | `{}` |
| `lockfile_pm_map()` | Map lockfile names to package managers | `{}` |

### Dataclasses

| Class | Fields | Purpose |
|-------|--------|---------|
| `ProjectTypeInfo` | `name`, `version`, `description`, `parent` | Plugin metadata |
| `TemplateInfo` | `id`, `description`, `template_dir` | Template variant definition |
| `VerificationRule` | `id`, `description`, `check`, `severity`, `config`, `ignore` | Declarative verification rule |
| `OrchestrationDirective` | `id`, `description`, `trigger`, `action`, `config` | Orchestration guardrail |

### Infrastructure Modules

- **`ProjectTypeResolver`** — Merges package rules with YAML overlays (`project-type.yaml` + `.local-overrides.yaml`). Supports disabling rules, overriding config/severity, and adding custom rules/directives.
- **`deploy_templates()`** — Deploys template files from a plugin into a target project. Manifest-based with optional modules (`manifest.yaml` defines core files + opt-in module packs).
- **`FeedbackStore`** — Collects anonymized rule improvement lessons for upstream feedback. Validates anonymization, stores in `wt/knowledge/lessons/rule-feedback.yaml`.

## Creating a Project Type Plugin

### 1. Subclass `ProjectType`

```python
# my_project_type/project_type.py
from wt_project_base import ProjectType, ProjectTypeInfo, TemplateInfo
from wt_project_base import VerificationRule, OrchestrationDirective

class PythonProjectType(ProjectType):
    @property
    def info(self):
        return ProjectTypeInfo(
            name="python", version="0.1.0",
            description="Python project conventions", parent="base",
        )

    def get_templates(self):
        return [TemplateInfo(
            id="default", description="Python project scaffold",
            template_dir="templates/default",
        )]

    def get_verification_rules(self):
        return [VerificationRule(
            id="docstring-coverage",
            description="Public functions need docstrings",
            check="pattern-audit", severity="warning",
            config={"pattern": "**/*.py", "match": r"def \w+\("},
        )]

    def get_orchestration_directives(self):
        return [OrchestrationDirective(
            id="run-tests", description="Run pytest after changes",
            trigger='change-modifies("**/*.py")',
            action="post-merge", config={"command": "pytest"},
        )]

    def gate_overrides(self, change_type: str) -> dict:
        """Per-change-type verification gate configuration."""
        if change_type == "foundational":
            return {"e2e_required": True, "smoke_blocking": False}
        return {}
```

### 2. Register via entry point

```toml
# pyproject.toml
[project.entry-points."wt_tools.project_types"]
python = "my_project_type:PythonProjectType"
```

### 3. Add templates

```yaml
# templates/default/manifest.yaml
core:
  - project-knowledge.yaml

modules:
  typing:
    description: "Strict typing conventions (mypy, pyright)"
    files:
      - rules/typing.md
```

### 4. Install and use

```bash
pip install -e .
wt-project init  # auto-detects installed project types
```

## Customization (without Python)

Override rules per-project via `wt/plugins/project-type.yaml`:

```yaml
disabled_rules:
  - todo-tracking          # don't enforce TODO references

rule_overrides:
  file-size-limit:
    config:
      max_lines: 600       # allow larger files

custom_rules:
  - id: require-changelog
    description: "Changes must update CHANGELOG.md"
    check: file-mentions
    severity: warning
    config:
      file: "CHANGELOG.md"
```

Personal overrides (gitignored) go in `.local-overrides.yaml`.

## Related

- [wt-tools](https://github.com/tatargabor/wt-tools) — The orchestration engine that consumes project type plugins
- [wt-project-web](https://github.com/tatargabor/wt-project-web) — Reference implementation: web project type with Next.js and SPA templates, 13 convention rule files, design integration

## License

MIT
