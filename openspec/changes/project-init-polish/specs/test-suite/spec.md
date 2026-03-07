## ADDED Requirements

### Requirement: Resolver tests cover overlay merging
Tests SHALL verify that ProjectTypeResolver correctly merges package rules with YAML overlay data, including disabled rules, rule overrides, custom rules, and .local-overrides.

#### Scenario: Disabled rule is removed
- **WHEN** a YAML overlay lists a rule ID in disabled_rules
- **THEN** that rule is excluded from resolved output

#### Scenario: Rule override merges config
- **WHEN** a YAML overlay provides rule_overrides with config changes
- **THEN** the resolved rule has merged config values

#### Scenario: Custom rule is appended
- **WHEN** a YAML overlay defines custom_rules
- **THEN** those rules appear in the resolved output alongside package rules

#### Scenario: Unknown disabled rule produces warning
- **WHEN** a YAML overlay disables a rule ID that does not exist in the package
- **THEN** a warning is recorded

### Requirement: Deploy tests cover manifest-based file resolution
Tests SHALL verify that deploy_templates correctly resolves files from manifest core + modules, applies path mappings, and respects force/dry-run flags.

#### Scenario: Core files deployed from manifest
- **WHEN** a manifest defines core files
- **THEN** only those files are deployed (not all files in template dir)

#### Scenario: Module files added when selected
- **WHEN** a module is selected via the modules parameter
- **THEN** that module's files are included in deploy alongside core files

#### Scenario: Existing files skipped without force
- **WHEN** a target file already exists and force is False
- **THEN** the file is skipped with a "Skipped" message

#### Scenario: Unknown module produces warning
- **WHEN** a non-existent module name is requested
- **THEN** a warning is produced listing available modules

### Requirement: Feedback tests cover lesson lifecycle
Tests SHALL verify FeedbackStore CRUD operations, validation, and export.

#### Scenario: Valid lesson is stored and persisted
- **WHEN** a valid FeedbackLesson is appended to FeedbackStore
- **THEN** it is persisted to the YAML file and retrievable

#### Scenario: Invalid lesson is rejected
- **WHEN** a lesson with an invalid issue type is appended
- **THEN** validation errors are returned and the lesson is not stored

#### Scenario: Export produces anonymized YAML
- **WHEN** lessons are exported
- **THEN** the output is valid YAML with a header and no timestamps

### Requirement: BaseProjectType tests verify shipped content
Tests SHALL verify that BaseProjectType returns the expected rules, directives, templates, and info.

#### Scenario: Correct number of rules and directives
- **WHEN** BaseProjectType is instantiated
- **THEN** it returns 3 verification rules and 4 orchestration directives

#### Scenario: Template directory resolves
- **WHEN** get_template_dir("default") is called
- **THEN** it returns a valid Path pointing to the templates/default directory
