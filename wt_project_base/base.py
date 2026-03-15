"""Base class for project type plugins.

This module defines the ProjectType interface that all project knowledge
plugins must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ProjectTypeInfo:
    """Metadata about a project type plugin."""
    name: str
    version: str
    description: str
    parent: Optional[str] = None  # e.g., "web" extends "base"


@dataclass
class TemplateInfo:
    """A template variant provided by a project type."""
    id: str  # e.g., "nextjs", "spa"
    description: str
    template_dir: str  # relative to plugin package


@dataclass
class VerificationRule:
    """A declarative verification rule."""
    id: str
    description: str
    check: str  # check type: cross-file-key-parity, file-mentions, etc.
    severity: str = "warning"  # error, warning, info
    config: Dict[str, Any] = field(default_factory=dict)
    ignore: List[str] = field(default_factory=list)


@dataclass
class OrchestrationDirective:
    """An orchestration guardrail."""
    id: str
    description: str
    trigger: str  # trigger expression
    action: str  # action type: serialize, warn, flag-for-review, post-merge
    config: Dict[str, Any] = field(default_factory=dict)


class ProjectType(ABC):
    """Base class for project type plugins.

    Project types provide domain-specific knowledge to wt-tools:
    - Templates for project-knowledge.yaml and .claude/rules/
    - Verification rules for opsx:verify
    - Orchestration directives for the sentinel
    """

    @property
    @abstractmethod
    def info(self) -> ProjectTypeInfo:
        """Return project type metadata."""

    @abstractmethod
    def get_templates(self) -> List[TemplateInfo]:
        """Return available template variants."""

    @abstractmethod
    def get_verification_rules(self) -> List[VerificationRule]:
        """Return verification rules for this project type."""

    @abstractmethod
    def get_orchestration_directives(self) -> List[OrchestrationDirective]:
        """Return orchestration directives for this project type."""

    def get_template_dir(self, template_id: str) -> Optional[Path]:
        """Return the directory containing template files for a variant."""
        import inspect

        for tmpl in self.get_templates():
            if tmpl.id == template_id:
                # Resolve relative to the concrete subclass's module, not the base
                cls_file = inspect.getfile(type(self))
                pkg_dir = Path(cls_file).parent
                return pkg_dir / tmpl.template_dir
        return None

    def get_all_verification_rules(self) -> List[VerificationRule]:
        """Return verification rules including inherited ones from parent types."""
        return self.get_verification_rules()

    def get_all_orchestration_directives(self) -> List[OrchestrationDirective]:
        """Return orchestration directives including inherited ones from parent types."""
        return self.get_orchestration_directives()

    # --- Profile methods (engine integration) ---
    # All have default implementations for backward compat.

    def planning_rules(self) -> str:
        """Quality patterns for the decompose/planning prompt.

        Returns a text block appended to core planning rules.
        Should include security patterns, testing conventions, and
        architecture constraints specific to this project type.
        """
        return ""

    def security_rules_paths(self, project_path: str) -> List[Path]:
        """Paths to security rule files for review retry context.

        These files get loaded and injected into the retry prompt
        when code review finds CRITICAL issues.
        """
        return []

    def security_checklist(self) -> str:
        """Security checklist items for proposal.md template.

        Returns markdown checklist lines injected into the
        Security Checklist section of render_proposal().
        """
        return ""

    def generated_file_patterns(self) -> List[str]:
        """Glob patterns for generated files that can be auto-resolved during merge.

        These files get 'ours' strategy during merge conflicts.
        Examples: "*.tsbuildinfo", "pnpm-lock.yaml", ".next/**"
        """
        return []

    def lockfile_pm_map(self) -> List[tuple]:
        """Mapping of lockfile names to package manager commands.

        Used for PM detection, bootstrap, post-merge install.
        Example: [("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn")]
        """
        return []

    def detect_package_manager(self, project_path: str) -> Optional[str]:
        """Detect the package manager for this project.

        Default implementation uses lockfile_pm_map().
        """
        d = Path(project_path)
        for lockfile, pm in self.lockfile_pm_map():
            if (d / lockfile).is_file():
                return pm
        return None

    def detect_test_command(self, project_path: str) -> Optional[str]:
        """Detect the test command for this project."""
        return None

    def detect_build_command(self, project_path: str) -> Optional[str]:
        """Detect the build command for this project."""
        return None

    def detect_dev_server(self, project_path: str) -> Optional[str]:
        """Detect the dev server start command for this project."""
        return None

    def bootstrap_worktree(self, project_path: str, wt_path: str) -> bool:
        """Install dependencies in a new worktree.

        Called after worktree creation. Should install deps but not
        modify source. Returns True on success.
        """
        return True

    def post_merge_install(self, project_path: str) -> bool:
        """Install dependencies after a merge.

        Called after successful merge on main branch.
        Returns True on success.
        """
        return True

    def ignore_patterns(self) -> List[str]:
        """Patterns to ignore during digest/codemap generation.

        Examples: ["node_modules", ".venv", "target"]
        """
        return []
