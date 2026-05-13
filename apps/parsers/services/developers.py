from __future__ import annotations

from apps.checks.models import Source

from .common import ConfigurableSourceParser


class ProblemDevelopersParser(ConfigurableSourceParser):
    source = Source.PROBLEM_DEVELOPERS
    risk_flags = ("problem_developer", "construction_delay", "shareholder_dispute")
