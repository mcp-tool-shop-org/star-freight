"""Balance type definitions — canonical schema for runs, metrics, and reports.

Every balance report is built from these. Keeps the harness coherent
and prevents degradation into loose dicts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Run configuration
# ---------------------------------------------------------------------------

class PolicyId(str, Enum):
    LAWFUL_CONSERVATIVE = "lawful_conservative"
    OPPORTUNISTIC_TRADER = "opportunistic_trader"
    CONTRACT_FORWARD = "contract_forward"
    INFRASTRUCTURE_FORWARD = "infrastructure_forward"
    LEVERAGE_FORWARD = "leverage_forward"
    SHADOW_RUNNER = "shadow_runner"
    LONG_HAUL_OPTIMIZER = "long_haul_optimizer"


@dataclass
class BalanceRunConfig:
    """Configuration for a single balance simulation run."""
    scenario_id: str
    seed: int
    captain_type: str               # "merchant", "smuggler", "navigator"
    policy_id: PolicyId
    max_days: int = 120
    stop_on_victory: bool = False
    notes: str = ""


# ---------------------------------------------------------------------------
# Route metrics (per-run, per-route)
# ---------------------------------------------------------------------------

@dataclass
class RouteRunMetrics:
    """Metrics for a single route within one run."""
    route_key: str                   # "porto_novo->al_manar"
    times_used: int = 0
    total_profit: int = 0
    total_revenue: int = 0
    total_cost: int = 0
    loss_count: int = 0


# ---------------------------------------------------------------------------
# Phase timing (when things first happen)
# ---------------------------------------------------------------------------

@dataclass
class PhaseTiming:
    """Day of first occurrence for key game events. -1 = never happened."""
    first_warehouse: int = -1
    first_broker: int = -1
    first_license: int = -1
    first_credit_line: int = -1
    first_insurance: int = -1
    first_brigantine: int = -1
    first_galleon: int = -1
    first_east_indies: int = -1
    first_victory_candidate: int = -1
    first_premium_contract: int = -1
    first_discreet_contract: int = -1


# ---------------------------------------------------------------------------
# Run metrics (one per simulation)
# ---------------------------------------------------------------------------

@dataclass
class RunMetrics:
    """Complete metrics for one balance simulation run."""
    config: BalanceRunConfig

    # Core outcomes
    days_played: int = 0
    final_silver: int = 0
    final_net_worth: int = 0
    final_ship_class: str = "sloop"

    # Trade activity
    voyages_completed: int = 0
    profitable_voyages: int = 0
    total_trades: int = 0
    total_trade_profit: int = 0

    # Contracts
    contracts_accepted: int = 0
    contracts_completed: int = 0
    contracts_failed: int = 0

    # Enforcement
    inspections: int = 0
    seizures: int = 0
    defaults: int = 0
    avg_heat_by_region: dict[str, float] = field(default_factory=dict)

    # Infrastructure
    warehouses_opened: int = 0
    brokers_opened: int = 0
    licenses_bought: int = 0

    # Finance
    insurance_policies_bought: int = 0
    claims_paid: int = 0
    credit_draw_total: int = 0
    credit_repaid_total: int = 0

    # Campaign
    strongest_victory_path: str = ""
    completed_victory_paths: list[str] = field(default_factory=list)

    # Timing
    timing: PhaseTiming = field(default_factory=PhaseTiming)

    # Route detail
    route_metrics: list[RouteRunMetrics] = field(default_factory=list)

    # Net worth snapshots at day bands
    net_worth_at_20: int = 0
    net_worth_at_40: int = 0
    net_worth_at_60: int = 0
    net_worth_at_80: int = 0
    net_worth_at_100: int = 0


# ---------------------------------------------------------------------------
# Aggregates (across multiple runs)
# ---------------------------------------------------------------------------

@dataclass
class CaptainAggregate:
    """Aggregated metrics for one captain type across runs."""
    captain_type: str
    run_count: int = 0
    median_brigantine_day: float = -1
    median_galleon_day: float = -1
    median_net_worth_20: float = 0
    median_net_worth_40: float = 0
    median_net_worth_60: float = 0
    mean_inspections: float = 0
    mean_seizures: float = 0
    mean_defaults: float = 0
    mean_contracts_completed: float = 0
    mean_contracts_failed: float = 0
    avg_heat_med: float = 0
    avg_heat_wa: float = 0
    avg_heat_ei: float = 0
    strongest_path_freq: dict[str, int] = field(default_factory=dict)
    completed_path_freq: dict[str, int] = field(default_factory=dict)
    median_first_warehouse: float = -1
    median_first_broker: float = -1
    median_first_license: float = -1
    insurance_adoption_rate: float = 0
    credit_adoption_rate: float = 0


@dataclass
class RouteAggregate:
    """Aggregated metrics for one route across runs."""
    route_key: str
    total_uses: int = 0
    total_profit: int = 0
    avg_profit_per_use: float = 0
    loss_rate: float = 0
    captain_breakdown: dict[str, int] = field(default_factory=dict)


@dataclass
class VictoryAggregate:
    """Victory path health across all runs."""
    path_id: str
    candidacy_count: int = 0
    completion_count: int = 0
    candidacy_rate: float = 0
    completion_rate: float = 0
    captain_skew: dict[str, int] = field(default_factory=dict)
    median_first_candidate_day: float = -1


# ---------------------------------------------------------------------------
# Batch report
# ---------------------------------------------------------------------------

@dataclass
class BalanceBatchReport:
    """Full balance report from a batch of runs."""
    scenario_id: str
    total_runs: int = 0
    captain_aggregates: list[CaptainAggregate] = field(default_factory=list)
    route_aggregates: list[RouteAggregate] = field(default_factory=list)
    victory_aggregates: list[VictoryAggregate] = field(default_factory=list)
    all_run_metrics: list[RunMetrics] = field(default_factory=list)
    notes: str = ""
