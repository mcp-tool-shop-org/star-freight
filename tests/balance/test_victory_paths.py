"""Victory path balance tests — all four paths should appear in practice.

These tests verify that victory paths are distinct and reachable,
not that they're perfectly balanced.
"""

from __future__ import annotations

from portlight.balance.aggregates import aggregate_victory_paths
from portlight.balance.runner import run_balance_simulation
from portlight.balance.types import BalanceRunConfig, PolicyId, RunMetrics


def _run_varied_batch(max_days: int = 80) -> list[RunMetrics]:
    """Run a varied batch across captains and policies."""
    configs = []
    combos = [
        ("merchant", PolicyId.LAWFUL_CONSERVATIVE),
        ("merchant", PolicyId.OPPORTUNISTIC_TRADER),
        ("smuggler", PolicyId.SHADOW_RUNNER),
        ("smuggler", PolicyId.OPPORTUNISTIC_TRADER),
        ("navigator", PolicyId.LONG_HAUL_OPTIMIZER),
        ("navigator", PolicyId.OPPORTUNISTIC_TRADER),
    ]
    for captain, policy in combos:
        for seed in (42, 137, 256):
            configs.append(BalanceRunConfig(
                scenario_id="victory_test",
                seed=seed,
                captain_type=captain,
                policy_id=policy,
                max_days=max_days,
            ))

    return [run_balance_simulation(c) for c in configs]


class TestVictoryPathHealth:
    def test_multiple_paths_appear_as_candidates(self):
        """At least 2 different paths should appear as strongest candidate."""
        metrics = _run_varied_batch()
        paths_seen = set()
        for m in metrics:
            if m.strongest_victory_path:
                paths_seen.add(m.strongest_victory_path)

        assert len(paths_seen) >= 2, \
            f"Only {len(paths_seen)} paths appeared as candidates: {paths_seen}"

    def test_lawful_not_universal_default(self):
        """Lawful Trade House shouldn't be strongest in >70% of all runs."""
        metrics = _run_varied_batch()
        vaggs = aggregate_victory_paths(metrics)

        lawful = next(
            (v for v in vaggs if v.path_id == "lawful_trade_house"), None
        )
        if lawful:
            assert lawful.candidacy_rate < 0.70, \
                f"Lawful dominates: {lawful.candidacy_rate:.0%} candidacy"

    def test_shadow_network_appears_for_smuggler(self):
        """Shadow Network should be strongest for smuggler in some runs."""
        metrics = [
            run_balance_simulation(BalanceRunConfig(
                scenario_id="shadow_test", seed=s,
                captain_type="smuggler",
                policy_id=PolicyId.SHADOW_RUNNER,
                max_days=80,
            ))
            for s in (8, 16, 20, 42, 50, 67, 137, 256, 512, 777)
        ]

        shadow_count = sum(
            1 for m in metrics
            if m.strongest_victory_path == "shadow_network"
        )
        assert shadow_count >= 1, \
            f"Shadow Network never appears as strongest for smuggler. " \
            f"Paths seen: {[m.strongest_victory_path for m in metrics]}"

    def test_oceanic_reach_appears_for_navigator(self):
        """Oceanic Reach should be strongest for navigator in some runs."""
        metrics = [
            run_balance_simulation(BalanceRunConfig(
                scenario_id="oceanic_test", seed=s,
                captain_type="navigator",
                policy_id=PolicyId.LONG_HAUL_OPTIMIZER,
                max_days=80,
            ))
            for s in (42, 137, 256, 512, 777, 999, 1234, 2048)
        ]

        oceanic_count = sum(
            1 for m in metrics
            if m.strongest_victory_path == "oceanic_reach"
        )
        assert oceanic_count >= 1, \
            "Oceanic Reach never appears as strongest for navigator"
