"""wt-project-base: Base project type plugin for wt-tools."""

from wt_project_base.base import (
    OrchestrationDirective,
    ProjectType,
    ProjectTypeInfo,
    TemplateInfo,
    VerificationRule,
)
from wt_project_base.project_type import BaseProjectType
from wt_project_base.resolver import ProjectTypeResolver

__all__ = [
    "BaseProjectType",
    "OrchestrationDirective",
    "ProjectType",
    "ProjectTypeInfo",
    "ProjectTypeResolver",
    "TemplateInfo",
    "VerificationRule",
]
