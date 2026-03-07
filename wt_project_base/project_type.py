"""Base project type — universal rules for any software project."""

from typing import List

from wt_project_base.base import (
    OrchestrationDirective,
    ProjectType,
    ProjectTypeInfo,
    TemplateInfo,
    VerificationRule,
)


class BaseProjectType(ProjectType):
    """Universal project type.

    Provides verification rules and orchestration directives that apply
    to any software project regardless of tech stack.
    """

    @property
    def info(self) -> ProjectTypeInfo:
        return ProjectTypeInfo(
            name="base",
            version="0.1.0",
            description="Universal project knowledge — rules and directives for any project",
        )

    def get_templates(self) -> List[TemplateInfo]:
        return [
            TemplateInfo(
                id="default",
                description="Minimal project knowledge scaffold",
                template_dir="templates/default",
            ),
        ]

    def get_verification_rules(self) -> List[VerificationRule]:
        return [
            VerificationRule(
                id="file-size-limit",
                description="Source files should not exceed 400 lines",
                check="file-line-count",
                severity="warning",
                config={
                    "pattern": "src/**/*.{py,ts,tsx,js,jsx,rs,go}",
                    "max_lines": 400,
                },
            ),
            VerificationRule(
                id="no-secrets-in-source",
                description="Source files should not contain hardcoded secrets",
                check="pattern-absence",
                severity="error",
                config={
                    "pattern": "**/*.{py,ts,tsx,js,jsx,yaml,yml,json}",
                    "forbidden": [
                        r"(?i)(api[_-]?key|secret[_-]?key|password)\s*[:=]\s*['\"][^'\"]{8,}",
                    ],
                    "exclude": ["*.example", "*.test.*", "*.spec.*"],
                },
            ),
            VerificationRule(
                id="todo-tracking",
                description="TODO/FIXME/HACK comments should reference an issue or change",
                check="pattern-audit",
                severity="info",
                config={
                    "pattern": "**/*.{py,ts,tsx,js,jsx}",
                    "match": r"(?i)\b(TODO|FIXME|HACK|XXX)\b",
                },
            ),
        ]

    def get_orchestration_directives(self) -> List[OrchestrationDirective]:
        return [
            OrchestrationDirective(
                id="install-deps-npm",
                description="Install npm dependencies after package.json changes",
                trigger='change-modifies("package.json")',
                action="post-merge",
                config={"command": "npm install"},
            ),
            OrchestrationDirective(
                id="install-deps-python",
                description="Install Python dependencies after pyproject.toml changes",
                trigger='change-modifies("pyproject.toml")',
                action="post-merge",
                config={"command": "pip install -e ."},
            ),
            OrchestrationDirective(
                id="no-parallel-lockfile",
                description="Serialize changes that modify lock files to prevent merge conflicts",
                trigger='change-modifies-any("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "poetry.lock", "uv.lock")',
                action="serialize",
                config={"with": 'changes-modifying-any("*lock*")'},
            ),
            OrchestrationDirective(
                id="config-review",
                description="Flag changes to CI/CD and infrastructure config for review",
                trigger='change-modifies-any(".github/**", "Dockerfile", "docker-compose*.yml", ".gitlab-ci.yml")',
                action="flag-for-review",
            ),
        ]
