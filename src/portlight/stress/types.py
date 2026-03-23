"""Stress test type definitions — scenarios, traces, and invariant results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Subsystem(str, Enum):
    ECONOMY = "economy"
    CONTRACTS = "contracts"
    INFRASTRUCTURE = "infrastructure"
    INSURANCE = "insurance"
    CREDIT = "credit"
    CAMPAIGN = "campaign"
    PERSISTENCE = "persistence"


@dataclass
class InvariantResult:
    """Result of checking one invariant."""
    name: str
    subsystem: Subsystem
    passed: bool
    message: str = ""


@dataclass
class TraceEvent:
    """One event in a stress run trace."""
    day: int
    action: str
    detail: str = ""
    silver_after: int = 0


@dataclass
class StressScenario:
    """A curated compound-pressure scenario."""
    id: str
    description: str
    captain_type: str = "merchant"
    seed: int = 42
    max_days: int = 60
    # Injected preconditions (applied before simulation)
    inject_silver: int | None = None
    inject_provisions: int | None = None
    inject_heat: dict[str, int] | None = None
    inject_trust: int | None = None
    inject_standing: dict[str, int] | None = None
    # Tags for categorization
    pressure_tags: list[str] = field(default_factory=list)


@dataclass
class StressRunReport:
    """Report from one stress scenario run."""
    scenario_id: str
    invariant_results: list[InvariantResult] = field(default_factory=list)
    trace: list[TraceEvent] = field(default_factory=list)
    invariant_failures: int = 0
    days_survived: int = 0
    final_silver: int = 0
    final_ship_class: str = "sloop"
    notes: str = ""

    @property
    def passed(self) -> bool:
        return self.invariant_failures == 0


@dataclass
class StressBatchReport:
    """Report from a batch of stress scenarios."""
    total_scenarios: int = 0
    total_failures: int = 0
    reports: list[StressRunReport] = field(default_factory=list)
    failure_by_subsystem: dict[str, int] = field(default_factory=dict)
