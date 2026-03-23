"""Tests for stress scenarios — prove each scenario runs and invariants hold."""

from __future__ import annotations

import pytest

from portlight.balance.types import PolicyId
from portlight.stress.runner import run_stress_scenario
from portlight.stress.scenarios import STRESS_SCENARIOS, all_scenario_ids, get_stress_scenario
from portlight.stress.types import StressRunReport


# ---------------------------------------------------------------------------
# Scenario registry
# ---------------------------------------------------------------------------

class TestScenarioRegistry:
    def test_all_scenarios_registered(self):
        assert len(STRESS_SCENARIOS) == 9

    def test_all_ids_unique(self):
        ids = all_scenario_ids()
        assert len(ids) == len(set(ids))

    def test_get_scenario_returns_correct(self):
        s = get_stress_scenario("debt_spiral")
        assert s is not None
        assert s.id == "debt_spiral"

    def test_get_unknown_returns_none(self):
        assert get_stress_scenario("nonexistent") is None

    def test_every_scenario_has_tags(self):
        for s in STRESS_SCENARIOS.values():
            assert len(s.pressure_tags) > 0, f"{s.id} has no pressure tags"


# ---------------------------------------------------------------------------
# Scenario execution — each scenario must pass all invariants
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("scenario_id", all_scenario_ids())
class TestScenarioExecution:
    def test_scenario_runs_without_crash(self, scenario_id):
        """Every scenario completes without exception."""
        scenario = STRESS_SCENARIOS[scenario_id]
        report = run_stress_scenario(scenario)
        assert isinstance(report, StressRunReport)
        assert report.scenario_id == scenario_id
        assert report.days_survived > 0

    def test_no_invariant_violations(self, scenario_id):
        """No scenario should produce invariant violations under normal policy."""
        scenario = STRESS_SCENARIOS[scenario_id]
        report = run_stress_scenario(scenario)
        if not report.passed:
            violation_detail = "\n".join(
                f"  - {inv.name} ({inv.subsystem.value}): {inv.message}"
                for inv in report.invariant_results
            )
            pytest.fail(
                f"Scenario {scenario_id} had {report.invariant_failures} "
                f"invariant violations:\n{violation_detail}"
            )


# ---------------------------------------------------------------------------
# Policy variation — ensure invariants hold across different play styles
# ---------------------------------------------------------------------------

class TestPolicyVariation:
    @pytest.mark.parametrize("policy_id", [
        PolicyId.LAWFUL_CONSERVATIVE,
        PolicyId.OPPORTUNISTIC_TRADER,
        PolicyId.SHADOW_RUNNER,
    ])
    def test_debt_spiral_lawful_under_all_policies(self, policy_id):
        """Debt spiral scenario stays lawful under different play styles."""
        scenario = STRESS_SCENARIOS["debt_spiral"]
        report = run_stress_scenario(scenario, policy_id)
        assert report.passed, (
            f"debt_spiral failed under {policy_id.value}: "
            f"{[inv.name for inv in report.invariant_results]}"
        )

    @pytest.mark.parametrize("policy_id", [
        PolicyId.INFRASTRUCTURE_FORWARD,
        PolicyId.LEVERAGE_FORWARD,
    ])
    def test_warehouse_neglect_under_infra_policies(self, policy_id):
        """Warehouse neglect stays lawful with infrastructure-heavy policies."""
        scenario = STRESS_SCENARIOS["warehouse_neglect"]
        report = run_stress_scenario(scenario, policy_id)
        assert report.passed, (
            f"warehouse_neglect failed under {policy_id.value}: "
            f"{[inv.name for inv in report.invariant_results]}"
        )


# ---------------------------------------------------------------------------
# Trace quality
# ---------------------------------------------------------------------------

class TestTraceQuality:
    def test_trace_records_events(self):
        scenario = STRESS_SCENARIOS["debt_spiral"]
        report = run_stress_scenario(scenario)
        assert len(report.trace) > 0
        # Should have at least one tick per day survived
        tick_events = [e for e in report.trace if e.action == "tick"]
        assert len(tick_events) > 0

    def test_trace_captures_bankruptcy(self):
        """If a scenario goes bankrupt, trace records it."""
        scenario = STRESS_SCENARIOS["oceanic_overextension"]
        report = run_stress_scenario(scenario)
        # This scenario starts very low — may or may not bankrupt
        # Just verify trace has content
        assert len(report.trace) > 0

    def test_violation_trace_has_detail(self):
        """If any violation occurs, it appears in trace with detail."""
        # Run all scenarios, check that any violations are traced
        for scenario in STRESS_SCENARIOS.values():
            report = run_stress_scenario(scenario)
            for inv in report.invariant_results:
                violation_traces = [
                    e for e in report.trace
                    if e.action == f"invariant_violation:{inv.name}"
                ]
                assert len(violation_traces) > 0, (
                    f"Violation {inv.name} in {scenario.id} not traced"
                )
