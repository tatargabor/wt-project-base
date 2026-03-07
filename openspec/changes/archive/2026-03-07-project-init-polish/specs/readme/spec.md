## ADDED Requirements

### Requirement: README explains ecosystem position
The README SHALL explain that wt-project-base is the abstract base layer of the wt-tools project type plugin system, never used directly by end users. It SHALL include a plugin hierarchy diagram showing base → web → your-org layering.

#### Scenario: Reader understands the package role
- **WHEN** a developer reads the README
- **THEN** they understand this package is a shared parent, not a standalone tool

### Requirement: README documents the API
The README SHALL list the ProjectType ABC methods, all dataclasses (ProjectTypeInfo, TemplateInfo, VerificationRule, OrchestrationDirective), and the universal rules/directives that BaseProjectType ships.

#### Scenario: Plugin author finds API reference
- **WHEN** a developer wants to create a new project type plugin
- **THEN** they can find the abstract methods they need to implement and the dataclass signatures

### Requirement: README includes plugin creation guide
The README SHALL include a "Creating a Project Type Plugin" section with a minimal working example showing how to subclass ProjectType, register via entry points, and ship templates. It SHALL emphasize that every project needs its own specific plugin — users MUST create one for their stack.

#### Scenario: Developer creates a new plugin
- **WHEN** a developer follows the plugin creation guide
- **THEN** they can create a minimal working project type plugin with entry point registration

### Requirement: README links to ecosystem
The README SHALL link to wt-tools (parent orchestration system) and wt-project-web (reference implementation of a concrete plugin).

#### Scenario: Reader navigates to related projects
- **WHEN** a developer wants to see a concrete plugin example or the orchestration system
- **THEN** they find links to wt-project-web and wt-tools
