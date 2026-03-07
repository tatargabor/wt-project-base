## ADDED Requirements

### Requirement: OpenSpec config has project context
The openspec/config.yaml SHALL include a context section describing the tech stack (Python, PyYAML), project nature (plugin base library for wt-tools), and key conventions.

#### Scenario: AI gets proper context for future changes
- **WHEN** a new openspec change is created
- **THEN** the AI receives project context describing this as a Python plugin base library

### Requirement: Gitignore covers wt-tools artifacts
The .gitignore SHALL include `.wt-tools/` to prevent wt-tools runtime artifacts from being committed.

#### Scenario: wt-tools directory is ignored
- **WHEN** wt-tools creates its `.wt-tools/` directory during operation
- **THEN** git status does not show it as untracked
