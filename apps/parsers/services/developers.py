from __future__ import annotations

from .common import ConfigurableSourceParser


class ProblemDevelopersParser(ConfigurableSourceParser):
    source = "problem_developers"
    risk_flags = ("problem_developer", "construction_delay", "shareholder_dispute")
