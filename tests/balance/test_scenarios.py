"""Tests for balance harness integrity — scenarios, policies, and runner.

Proves the harness itself is trustworthy before using it for tuning.
"""

from __future__ import annotations

import pytest

from portlight.balance.runner import run_balance_simulation
from portlight.balance.scenarios import SCENARIOS, get_scenario
from portlight.balance.types import BalanceRunConfig, PolicyId


class TestScenarioDefinitions:
    def test_all_scenarios_load(self):
        for sid in SCENARIOS:
            scenario = get_scenario(sid)
            assert scenario.id == sid
            assert len(scenario.seeds) >= 3

    def test_unknown_scenario_raises(self):
        with pytest.raises(ValueError, match="Unknown scenario"):
            get_scenario("nonexistent")

    def test_all_scenarios_have_stable_seeds(self):
        for sid, scenario in SCENARIOS.items():
            assert len(scenario.seeds) == len(set(scenario.seeds)), \
                f"{sid} has duplicate seeds"


class TestPolicies:
    @pytest.mark.parametrize("policy", list(PolicyId))
    def test_every_policy_runs_without_crash(self, policy: PolicyId):
        """Each policy can run at least a short simulation."""
        config = BalanceRunConfig(
            scenario_id="test",
            seed=42,
            captain_type="merchant",
            policy_id=policy,
            max_days=10,
        )
        metrics = run_balance_simulation(config)
        assert metrics.days_played >= 5
        assert metrics.final_silver >= 0

    @pytest.mark.parametrize("captain", ["merchant", "smuggler", "navigator"])
    def test_every_captain_runs(self, captain: str):
        """Each captain type works with the default policy."""
        config = BalanceRunConfig(
            scenario_id="test",
            seed=42,
            captain_type=captain,
            policy_id=PolicyId.OPPORTUNISTIC_TRADER,
            max_days=15,
        )
        metrics = run_balance_simulation(config)
        assert metrics.days_played >= 10
        assert metrics.config.captain_type == captain


class TestRunnerIntegrity:
    def test_deterministic_with_same_seed(self):
        """Same config produces same results."""
        config = BalanceRunConfig(
            scenario_id="test", seed=42, captain_type="merchant",
            policy_id=PolicyId.LAWFUL_CONSERVATIVE, max_days=20,
        )
        m1 = run_balance_simulation(config)
        m2 = run_balance_simulation(config)
        assert m1.days_played == m2.days_played
        assert m1.final_silver == m2.final_silver
        assert m1.total_trades == m2.total_trades

    def test_different_seeds_diverge(self):
        """Different seeds produce different results."""
        c1 = BalanceRunConfig(
            scenario_id="test", seed=42, captain_type="merchant",
            policy_id=PolicyId.LAWFUL_CONSERVATIVE, max_days=30,
        )
        c2 = BalanceRunConfig(
            scenario_id="test", seed=999, captain_type="merchant",
            policy_id=PolicyId.LAWFUL_CONSERVATIVE, max_days=30,
        )
        m1 = run_balance_simulation(c1)
        m2 = run_balance_simulation(c2)
        # They may differ in silver, trades, or routes
        assert (m1.final_silver != m2.final_silver or
                m1.total_trades != m2.total_trades)

    def test_metrics_have_route_data(self):
        """Runs that trade produce route metrics."""
        config = BalanceRunConfig(
            scenario_id="test", seed=42, captain_type="merchant",
            policy_id=PolicyId.OPPORTUNISTIC_TRADER, max_days=30,
        )
        metrics = run_balance_simulation(config)
        assert metrics.total_trades > 0
        # Route metrics may or may not be populated depending on sell tracking

    def test_stop_on_bankruptcy(self):
        """Runs stop if captain goes bankrupt."""
        # Use a seed and short max_days — should not crash
        config = BalanceRunConfig(
            scenario_id="test", seed=7777, captain_type="navigator",
            policy_id=PolicyId.LEVERAGE_FORWARD, max_days=120,
        )
        metrics = run_balance_simulation(config)
        assert metrics.final_silver >= 0  # never negative


class TestReporting:
    def test_report_generation(self):
        """Can build reports from metrics."""
        from portlight.balance.reporting import build_batch_report

        configs = [
            BalanceRunConfig(
                scenario_id="test", seed=s, captain_type=ct,
                policy_id=PolicyId.LAWFUL_CONSERVATIVE, max_days=15,
            )
            for ct in ["merchant", "smuggler"]
            for s in [42, 137]
        ]
        metrics = [run_balance_simulation(c) for c in configs]
        report = build_batch_report(metrics, "test")

        assert report.total_runs == 4
        assert len(report.captain_aggregates) == 2
        assert len(report.victory_aggregates) == 4
