"""Aggregation — turn many run metrics into tuning insight.

Computes medians, means, distributions, and frequency tables
across runs grouped by captain, policy, scenario, route, and path.
"""

from __future__ import annotations

from statistics import mean, median

from portlight.balance.types import (
    CaptainAggregate,
    RouteAggregate,
    RunMetrics,
    VictoryAggregate,
)


def _median_positive(values: list[int | float]) -> float:
    """Median of positive values only. Returns -1 if none."""
    pos = [v for v in values if v > 0]
    if not pos:
        return -1
    return median(pos)


def _safe_mean(values: list[int | float]) -> float:
    if not values:
        return 0
    return mean(values)


def aggregate_by_captain(metrics: list[RunMetrics]) -> list[CaptainAggregate]:
    """Group metrics by captain type and compute aggregates."""
    by_captain: dict[str, list[RunMetrics]] = {}
    for m in metrics:
        ct = m.config.captain_type
        by_captain.setdefault(ct, []).append(m)

    results = []
    for captain_type, runs in sorted(by_captain.items()):
        agg = CaptainAggregate(captain_type=captain_type, run_count=len(runs))

        agg.median_brigantine_day = _median_positive(
            [r.timing.first_brigantine for r in runs]
        )
        agg.median_galleon_day = _median_positive(
            [r.timing.first_galleon for r in runs]
        )
        agg.median_net_worth_20 = _safe_mean([r.net_worth_at_20 for r in runs])
        agg.median_net_worth_40 = _safe_mean([r.net_worth_at_40 for r in runs])
        agg.median_net_worth_60 = _safe_mean([r.net_worth_at_60 for r in runs])

        agg.mean_inspections = _safe_mean([r.inspections for r in runs])
        agg.mean_seizures = _safe_mean([r.seizures for r in runs])
        agg.mean_defaults = _safe_mean([r.defaults for r in runs])
        agg.mean_contracts_completed = _safe_mean(
            [r.contracts_completed for r in runs]
        )
        agg.mean_contracts_failed = _safe_mean(
            [r.contracts_failed for r in runs]
        )

        # Heat by region
        med_heats = [r.avg_heat_by_region.get("Mediterranean", 0) for r in runs]
        wa_heats = [r.avg_heat_by_region.get("West Africa", 0) for r in runs]
        ei_heats = [r.avg_heat_by_region.get("East Indies", 0) for r in runs]
        agg.avg_heat_med = _safe_mean(med_heats)
        agg.avg_heat_wa = _safe_mean(wa_heats)
        agg.avg_heat_ei = _safe_mean(ei_heats)

        # Victory path frequency
        for r in runs:
            if r.strongest_victory_path:
                p = r.strongest_victory_path
                agg.strongest_path_freq[p] = agg.strongest_path_freq.get(p, 0) + 1
            for cp in r.completed_victory_paths:
                agg.completed_path_freq[cp] = agg.completed_path_freq.get(cp, 0) + 1

        # Infrastructure timing
        agg.median_first_warehouse = _median_positive(
            [r.timing.first_warehouse for r in runs]
        )
        agg.median_first_broker = _median_positive(
            [r.timing.first_broker for r in runs]
        )
        agg.median_first_license = _median_positive(
            [r.timing.first_license for r in runs]
        )

        # Adoption rates
        agg.insurance_adoption_rate = (
            sum(1 for r in runs if r.insurance_policies_bought > 0) / len(runs)
        )
        agg.credit_adoption_rate = (
            sum(1 for r in runs if r.credit_draw_total > 0) / len(runs)
        )

        results.append(agg)
    return results


def aggregate_routes(metrics: list[RunMetrics]) -> list[RouteAggregate]:
    """Aggregate route metrics across all runs."""
    by_route: dict[str, RouteAggregate] = {}

    for m in metrics:
        captain_type = m.config.captain_type
        for rm in m.route_metrics:
            if rm.route_key not in by_route:
                by_route[rm.route_key] = RouteAggregate(route_key=rm.route_key)
            agg = by_route[rm.route_key]
            agg.total_uses += rm.times_used
            agg.total_profit += rm.total_profit
            agg.captain_breakdown[captain_type] = (
                agg.captain_breakdown.get(captain_type, 0) + rm.times_used
            )

    results = []
    for agg in by_route.values():
        if agg.total_uses > 0:
            agg.avg_profit_per_use = agg.total_profit / agg.total_uses
        results.append(agg)

    results.sort(key=lambda r: r.total_uses, reverse=True)
    return results


def aggregate_victory_paths(metrics: list[RunMetrics]) -> list[VictoryAggregate]:
    """Aggregate victory path health across all runs."""
    path_ids = [
        "lawful_trade_house", "shadow_network",
        "oceanic_reach", "commercial_empire",
    ]
    by_path: dict[str, VictoryAggregate] = {}
    total_runs = len(metrics)

    for pid in path_ids:
        by_path[pid] = VictoryAggregate(path_id=pid)

    for m in metrics:
        captain = m.config.captain_type
        if m.strongest_victory_path:
            p = m.strongest_victory_path
            if p in by_path:
                by_path[p].candidacy_count += 1
                by_path[p].captain_skew[captain] = (
                    by_path[p].captain_skew.get(captain, 0) + 1
                )

        for cp in m.completed_victory_paths:
            if cp in by_path:
                by_path[cp].completion_count += 1

    for agg in by_path.values():
        if total_runs > 0:
            agg.candidacy_rate = agg.candidacy_count / total_runs
            agg.completion_rate = agg.completion_count / total_runs

    return list(by_path.values())
