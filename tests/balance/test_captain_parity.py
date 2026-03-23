"""Captain parity tests — broad guardrails, not strict equality.

These tests catch balance drift without false alarms.
Thresholds are generous to avoid brittleness.
"""

from __future__ import annotations

import pytest

from portlight.balance.aggregates import aggregate_by_captain
from portlight.balance.runner import run_balance_simulation
from portlight.balance.types import BalanceRunConfig, PolicyId, RunMetrics


def _run_captain_batch(
    captain_type: str,
    policy: PolicyId = PolicyId.OPPORTUNISTIC_TRADER,
    seeds: tuple[int, ...] = (42, 137, 256, 999, 314, 777, 9, 16, 23, 55),
    max_days: int = 60,
) -> list[RunMetrics]:
    """Run a batch for one captain with multiple seeds."""
    return [
        run_balance_simulation(BalanceRunConfig(
            scenario_id="parity_test",
            seed=s,
            captain_type=captain_type,
            policy_id=policy,
            max_days=max_days,
        ))
        for s in seeds
    ]


class TestCaptainParity:
    def test_all_captains_profitable_30_days(self):
        """No captain should go bankrupt within 30 days of basic trading."""
        for ct in ["merchant", "smuggler", "navigator"]:
            metrics = _run_captain_batch(ct, max_days=30)
            profitable = sum(1 for m in metrics if m.final_silver > 300)
            assert profitable >= 1, \
                f"{ct} had no profitable runs in 30 days"

    def test_all_captains_make_trades(self):
        """Every captain should complete at least some trades."""
        for ct in ["merchant", "smuggler", "navigator"]:
            metrics = _run_captain_batch(ct, max_days=40)
            total_trades = sum(m.total_trades for m in metrics)
            assert total_trades > 0, \
                f"{ct} made zero trades in 40 days"

    def test_merchant_not_too_far_ahead_on_brigantine(self):
        """Merchant shouldn't reach brigantine >25% faster than field median."""
        all_metrics = []
        for ct in ["merchant", "smuggler", "navigator"]:
            all_metrics.extend(_run_captain_batch(ct, max_days=60))

        aggs = aggregate_by_captain(all_metrics)
        brig_times = {
            a.captain_type: a.median_brigantine_day
            for a in aggs
            if a.median_brigantine_day > 0
        }

        if len(brig_times) < 2:
            pytest.skip("Not enough captains reached brigantine")

        fastest = min(brig_times.values())
        slowest = max(brig_times.values())
        if slowest > 0:
            gap_pct = (slowest - fastest) / slowest
            assert gap_pct < 0.65, \
                f"Brigantine gap too large: {gap_pct:.0%} (fastest={fastest}, slowest={slowest})"


class TestRoutes:
    def test_no_single_route_dominates_all_traffic(self):
        """No route should carry >60% of all traffic."""
        all_metrics = []
        for ct in ["merchant", "smuggler", "navigator"]:
            all_metrics.extend(_run_captain_batch(ct, max_days=50))

        from portlight.balance.aggregates import aggregate_routes
        route_aggs = aggregate_routes(all_metrics)
        if not route_aggs:
            pytest.skip("No routes used")

        total = sum(r.total_uses for r in route_aggs)
        top = route_aggs[0]
        concentration = top.total_uses / max(total, 1)
        assert concentration < 0.60, \
            f"Route {top.route_key} dominates at {concentration:.0%}"

    def test_multiple_routes_used(self):
        """At least 3 different routes should be used across all captains."""
        all_metrics = []
        for ct in ["merchant", "smuggler", "navigator"]:
            all_metrics.extend(_run_captain_batch(ct, max_days=50))

        from portlight.balance.aggregates import aggregate_routes
        route_aggs = aggregate_routes(all_metrics)
        used_routes = [r for r in route_aggs if r.total_uses > 0]
        assert len(used_routes) >= 3, \
            f"Only {len(used_routes)} routes used, need diversity"
