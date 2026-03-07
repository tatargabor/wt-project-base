## Why

The wt-project-base package was recently initialized with its core plugin system (ProjectType ABC, resolver, deploy, feedback), but several polish items were deferred: there is no README, no tests, and the openspec config lacks project context. Before moving on to downstream work, we should close these gaps so the package is presentable as a reusable base library.

This package is strictly a shared parent — never used directly by end users. Every project MUST have a specific project type plugin (like `wt-project-web`, `wt-project-go`, etc.) that extends this base. The base provides the ABC, universal rules, resolver infrastructure, and template deploy system that all concrete plugins inherit.

## What Changes

- Add a `README.md` explaining the package's role as the abstract base layer, its API (ProjectType ABC, dataclasses), universal rules/directives it ships, and a guide for creating new project type plugins
- Add unit tests for core modules (resolver, deploy, feedback, project_type)
- Fill in `openspec/config.yaml` with project context for AI guidance on future changes
- Ensure `.gitignore` covers `.wt-tools/`

## Capabilities

### New Capabilities
- `readme`: Project README — ecosystem position, API reference, "how to create a plugin" guide
- `test-suite`: Unit tests for resolver, deploy, feedback, and project_type modules
- `project-hygiene`: openspec config context and gitignore cleanup

### Modified Capabilities
_(none)_

## Impact

- No code logic changes — documentation, tests, and config only
- No API or dependency changes
- Downstream consumers (wt-project-web) unaffected
