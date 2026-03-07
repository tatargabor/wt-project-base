## 1. Project Hygiene

- [x] 1.1 Add `.wt-tools/` to `.gitignore`
- [x] 1.2 Fill in `openspec/config.yaml` context section with project description (Python plugin base library, PyYAML dependency, plugin conventions)

## 2. README

- [x] 2.1 Create `README.md` with ecosystem position: abstract base layer, never used directly, every project needs a specific plugin (wt-project-web, wt-project-python, wt-project-laravel, etc.)
- [x] 2.2 Add plugin hierarchy diagram (base → web/python/laravel → your-org)
- [x] 2.3 Add API reference section: ProjectType ABC methods, dataclasses (ProjectTypeInfo, TemplateInfo, VerificationRule, OrchestrationDirective)
- [x] 2.4 Add universal rules and directives listing (what BaseProjectType ships)
- [x] 2.5 Add "Creating a Project Type Plugin" guide with minimal example (subclass, entry point, templates)
- [x] 2.6 Add links to wt-tools and wt-project-web

## 3. Tests

- [x] 3.1 Create `tests/` directory with `conftest.py` (shared fixtures: tmp project dirs, sample YAML overlays)
- [x] 3.2 Add `test_project_type.py` — BaseProjectType returns correct rules (3), directives (4), templates (1), info, template_dir resolves
- [x] 3.3 Add `test_resolver.py` — overlay merging: disabled rules, rule overrides, custom rules, custom directives, warnings for unknown IDs, .local-overrides layering
- [x] 3.4 Add `test_deploy.py` — manifest parsing, core file resolution, module selection, path mappings (rules/ → .claude/rules/), force/skip behavior, dry-run, unknown module warning
- [x] 3.5 Add `test_feedback.py` — lesson validation, store append/persist/load, invalid issue rejection, export format, identifying content detection
- [x] 3.6 Add pytest to pyproject.toml dev dependencies and configure testpaths
