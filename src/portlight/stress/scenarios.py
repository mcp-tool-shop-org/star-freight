"""Curated stress scenarios — compound pressure situations that test invariant truth.

Each scenario injects specific preconditions (low silver, high debt, warehouse
about to close, etc.) then runs a policy bot under pressure while checking
invariants after every tick. The goal is not to measure balance — it's to prove
that the game never enters an illegal state.
"""

from __future__ import annotations

from portlight.stress.types import StressScenario


STRESS_SCENARIOS: dict[str, StressScenario] = {
    # --- Credit stress ---
    "debt_spiral": StressScenario(
        id="debt_spiral",
        description="Max credit drawn, low silver, interest accruing. "
                    "Tests that credit interest never creates negative silver "
                    "and that 3 defaults freeze the line.",
        captain_type="merchant",
        seed=42,
        max_days=40,
        inject_silver=50,
        inject_provisions=10,
        pressure_tags=["credit", "economy"],
    ),

    # --- Infrastructure neglect ---
    "warehouse_neglect": StressScenario(
        id="warehouse_neglect",
        description="Warehouse with cargo, silver too low for upkeep. "
                    "Tests that closure clears inventory cleanly and "
                    "inactive warehouse invariant holds.",
        captain_type="merchant",
        seed=137,
        max_days=30,
        inject_silver=20,
        inject_provisions=15,
        pressure_tags=["infrastructure", "economy"],
    ),

    # --- Insurance under pressure ---
    "insured_luxury_loss": StressScenario(
        id="insured_luxury_loss",
        description="Carrying insured luxury cargo through storm-heavy route. "
                    "Tests that claim payouts stay within coverage cap and "
                    "denied claims don't reduce cap.",
        captain_type="navigator",
        seed=999,
        max_days=30,
        inject_provisions=20,
        pressure_tags=["insurance", "economy"],
    ),

    # --- Contract deadline crunch ---
    "contract_expiry_under_pressure": StressScenario(
        id="contract_expiry_under_pressure",
        description="Multiple active contracts with tight deadlines and "
                    "insufficient cargo. Tests that expiry produces exactly "
                    "one outcome per contract, no dual resolution.",
        captain_type="merchant",
        seed=256,
        max_days=25,
        inject_silver=200,
        inject_provisions=10,
        pressure_tags=["contracts", "economy"],
    ),

    # --- Heat + license conflict ---
    "heat_license_conflict": StressScenario(
        id="heat_license_conflict",
        description="Smuggler with high heat trying to maintain licenses. "
                    "Tests that heat doesn't corrupt license state and "
                    "market stock stays non-negative under pressure sales.",
        captain_type="smuggler",
        seed=666,
        max_days=35,
        inject_heat={"Mediterranean": 25, "West Africa": 15},
        inject_provisions=20,
        pressure_tags=["reputation", "infrastructure", "economy"],
    ),

    # --- Legitimization pivot ---
    "legitimization_pivot": StressScenario(
        id="legitimization_pivot",
        description="Smuggler switching to lawful trade mid-game. "
                    "Tests that reputation shifts don't corrupt contract "
                    "state or produce duplicate milestones.",
        captain_type="smuggler",
        seed=512,
        max_days=50,
        inject_trust=5,
        inject_standing={"Mediterranean": 10, "West Africa": 5},
        pressure_tags=["reputation", "contracts", "campaign"],
    ),

    # --- Oceanic overextension ---
    "oceanic_overextension": StressScenario(
        id="oceanic_overextension",
        description="Navigator deep in East Indies with expensive ship, "
                    "low provisions, credit drawn. Tests compound drain "
                    "from wages + interest + upkeep doesn't violate silver.",
        captain_type="navigator",
        seed=777,
        max_days=40,
        inject_silver=100,
        inject_provisions=5,
        pressure_tags=["economy", "credit", "infrastructure"],
    ),

    # --- Victory then stress ---
    "victory_then_stress": StressScenario(
        id="victory_then_stress",
        description="Session near victory completion then hit with economic "
                    "pressure. Tests that campaign state stays consistent "
                    "under duress — no duplicate paths, milestones persistent.",
        captain_type="merchant",
        seed=1234,
        max_days=60,
        inject_trust=15,
        inject_standing={"Mediterranean": 20, "West Africa": 10, "East Indies": 5},
        pressure_tags=["campaign", "economy"],
    ),

    # --- Save/load mid-crisis ---
    "save_load_mid_crisis": StressScenario(
        id="save_load_mid_crisis",
        description="Active credit + warehouse + contracts + insurance "
                    "all in flight, save and reload. Tests that compound "
                    "state round-trips without invariant violations.",
        captain_type="merchant",
        seed=5678,
        max_days=30,
        inject_provisions=15,
        pressure_tags=["persistence", "economy", "infrastructure", "credit"],
    ),
}


def get_stress_scenario(scenario_id: str) -> StressScenario | None:
    """Get a stress scenario by ID."""
    return STRESS_SCENARIOS.get(scenario_id)


def all_scenario_ids() -> list[str]:
    """All registered stress scenario IDs."""
    return list(STRESS_SCENARIOS.keys())
