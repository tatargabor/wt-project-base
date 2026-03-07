## Context

wt-project-base is the abstract base layer of the wt-tools project type plugin system. It provides:
- `ProjectType` ABC and dataclasses (`VerificationRule`, `OrchestrationDirective`, `TemplateInfo`, `ProjectTypeInfo`)
- `BaseProjectType` with universal rules (file-size, no-secrets, todo-tracking) and directives (dep install, lockfile serialize, config review)
- `ProjectTypeResolver` for merging package rules with YAML overlays
- Template deploy system with manifest-based module selection
- Anonymized feedback/lesson collection

The package has working code but lacks README, tests, and openspec project context.

## Goals / Non-Goals

**Goals:**
- README that clearly positions this as a base library for plugin authors, not end users
- Unit tests covering the core modules with good coverage
- openspec config.yaml filled in so future changes get proper AI context
- Clean gitignore

**Non-Goals:**
- No code changes to existing modules
- No new features or API modifications
- No end-user documentation (that belongs in concrete plugins like wt-project-web)
- No CI/CD setup (premature for this stage)

## Decisions

### README structure
Follow the pattern established by `wt-project-web/README.md` — concise, functional, with the plugin hierarchy diagram. Sections: what it is, plugin architecture diagram, API reference (ABC + dataclasses), universal rules/directives list, "Creating a Plugin" guide with minimal example, links to wt-tools and wt-project-web.

**Why:** Consistent with the ecosystem. The primary audience is developers creating new project type plugins, not end users.

### Test framework: pytest with no extra dependencies
Use pytest only. Tests should exercise the public API of each module using the real `BaseProjectType` — no mocks needed since all dependencies are local dataclasses and YAML files.

**Why:** The package has zero external runtime deps besides PyYAML. Tests can use tmp_path for file operations. Keeping it simple.

### Test scope
- `resolver.py`: overlay merging, disabled rules, custom rules, warnings, .local-overrides
- `deploy.py`: manifest parsing, file resolution, module selection, path mapping, dry-run
- `feedback.py`: lesson validation, store CRUD, export, identifying content detection
- `project_type.py`: BaseProjectType returns correct rules/directives/templates/info

**Why:** These are the four core modules with actual logic. `base.py` is just dataclasses (no tests needed), `cli.py` is a thin CLI wrapper (test via the modules it calls), `__init__.py` is re-exports.

## Risks / Trade-offs

- [Risk] README may drift from code as the API evolves → Mitigation: Keep it concise, reference code rather than duplicating it
- [Risk] Tests may be too tightly coupled to current rule IDs → Mitigation: Test behavior (counts, types) not specific string values where possible
