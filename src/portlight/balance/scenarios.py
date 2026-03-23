"""Scenario definitions — curated seed packs and world modifiers.

Each scenario controls world conditions for comparable balance runs.
Seeds are fixed so results are reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BalanceScenario:
    """A named test scenario with fixed seeds and world modifiers."""
    id: str
    description: str
    seeds: tuple[int, ...]
    max_days: int = 120
    # Modifiers (applied to game session at start)
    shock_frequency_mult: float = 1.0    # regional market shocks
    enforcement_mult: float = 1.0        # inspection frequency
    premium_goods_bias: float = 1.0      # luxury availability
    contract_board_bias: float = 1.0     # offer frequency


SCENARIOS: dict[str, BalanceScenario] = {
    "stable_baseline": BalanceScenario(
        id="stable_baseline",
        description="Low volatility. Best for captain parity comparison.",
        seeds=(42, 137, 256, 512, 777),
        shock_frequency_mult=0.5,
    ),
    "mixed_volatility": BalanceScenario(
        id="mixed_volatility",
        description="Normal world with moderate shocks. Default calibration set.",
        seeds=(101, 202, 303, 404, 505),
    ),
    "high_shock": BalanceScenario(
        id="high_shock",
        description="Aggressive regional shifts. Stress-tests staging and insurance.",
        seeds=(666, 999, 1234, 5678, 9999),
        shock_frequency_mult=2.0,
    ),
    "lawful_friendly": BalanceScenario(
        id="lawful_friendly",
        description="Lower enforcement friction. Tests Merchant snowball risk.",
        seeds=(11, 22, 33, 44, 55),
        enforcement_mult=0.5,
    ),
    "shadow_friendly": BalanceScenario(
        id="shadow_friendly",
        description="Stronger discreet opportunity density. Tests Smuggler upside.",
        seeds=(13, 31, 57, 79, 97),
        enforcement_mult=0.7,
        premium_goods_bias=1.3,
    ),
    "long_haul_friendly": BalanceScenario(
        id="long_haul_friendly",
        description="Good East Indies timing. Tests Navigator and Oceanic Reach.",
        seeds=(100, 200, 300, 400, 500),
        premium_goods_bias=1.2,
    ),
    "finance_pressure": BalanceScenario(
        id="finance_pressure",
        description="Tighter liquidity. Tests credit/insurance decision value.",
        seeds=(7, 14, 21, 28, 35),
        shock_frequency_mult=1.5,
    ),
}


def get_scenario(scenario_id: str) -> BalanceScenario:
    """Get a scenario by ID or raise ValueError."""
    if scenario_id not in SCENARIOS:
        valid = ", ".join(SCENARIOS.keys())
        raise ValueError(f"Unknown scenario: {scenario_id}. Valid: {valid}")
    return SCENARIOS[scenario_id]
