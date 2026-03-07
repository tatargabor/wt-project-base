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
        for tmpl in self.get_templates():
            if tmpl.id == template_id:
                pkg_dir = Path(__file__).parent
                return pkg_dir / tmpl.template_dir
        return None

    def get_all_verification_rules(self) -> List[VerificationRule]:
        """Return verification rules including inherited ones from parent types."""
        return self.get_verification_rules()

    def get_all_orchestration_directives(self) -> List[OrchestrationDirective]:
        """Return orchestration directives including inherited ones from parent types."""
        return self.get_orchestration_directives()
