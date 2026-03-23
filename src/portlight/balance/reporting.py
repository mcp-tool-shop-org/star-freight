"""Balance reporting — JSON and markdown output from aggregated metrics.

Produces human-readable reports and machine-comparable JSON.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from portlight.balance.aggregates import (
    aggregate_by_captain,
    aggregate_routes,
    aggregate_victory_paths,
)
from portlight.balance.types import BalanceBatchReport, RunMetrics


def build_batch_report(
    metrics: list[RunMetrics],
    scenario_id: str = "mixed",
) -> BalanceBatchReport:
    """Build a complete batch report from run metrics."""
    return BalanceBatchReport(
        scenario_id=scenario_id,
        total_runs=len(metrics),
        captain_aggregates=aggregate_by_captain(metrics),
        route_aggregates=aggregate_routes(metrics),
        victory_aggregates=aggregate_victory_paths(metrics),
        all_run_metrics=metrics,
    )


def write_json_report(report: BalanceBatchReport, path: Path) -> None:
    """Write full report as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _report_to_dict(report)
    path.write_text(json.dumps(data, indent=2, default=str))


def write_markdown_report(report: BalanceBatchReport, path: Path) -> None:
    """Write human-readable markdown report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = _build_markdown(report)
    path.write_text("\n".join(lines))


# ---------------------------------------------------------------------------
# JSON serialization
# ---------------------------------------------------------------------------

def _report_to_dict(report: BalanceBatchReport) -> dict:
    """Convert report to JSON-safe dict."""
    return {
        "scenario_id": report.scenario_id,
        "total_runs": report.total_runs,
        "captain_aggregates": [asdict(a) for a in report.captain_aggregates],
        "route_aggregates": [asdict(a) for a in report.route_aggregates[:20]],
        "victory_aggregates": [asdict(a) for a in report.victory_aggregates],
        "notes": report.notes,
    }


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def _build_markdown(report: BalanceBatchReport) -> list[str]:
    lines: list[str] = []
    lines.append(f"# Balance Report — {report.scenario_id}")
    lines.append(f"\nTotal runs: {report.total_runs}\n")

    # Executive summary
    lines.append("## Executive Summary\n")
    _add_summary(lines, report)

    # Captain parity
    lines.append("\n## Captain Parity\n")
    _add_captain_table(lines, report)

    # Route diversity
    lines.append("\n## Route Economics\n")
    _add_route_table(lines, report)

    # Victory paths
    lines.append("\n## Victory Path Health\n")
    _add_victory_table(lines, report)

    # Infrastructure timing
    lines.append("\n## Infrastructure & Finance Timing\n")
    _add_infra_table(lines, report)

    return lines


def _add_summary(lines: list[str], report: BalanceBatchReport) -> None:
    """Add executive summary based on aggregates."""
    if not report.captain_aggregates:
        lines.append("No data available.\n")
        return

    # Find fastest to brigantine
    brig_times = {
        a.captain_type: a.median_brigantine_day
        for a in report.captain_aggregates
        if a.median_brigantine_day > 0
    }
    if brig_times:
        fastest = min(brig_times, key=brig_times.get)
        slowest = max(brig_times, key=brig_times.get)
        gap = brig_times[slowest] - brig_times[fastest]
        lines.append(
            f"- **Brigantine gap**: {fastest} fastest "
            f"(day {brig_times[fastest]:.0f}), "
            f"{slowest} slowest (day {brig_times[slowest]:.0f}), "
            f"gap = {gap:.0f} days"
        )

    # Route concentration
    if report.route_aggregates:
        total_uses = sum(r.total_uses for r in report.route_aggregates)
        top = report.route_aggregates[0]
        if total_uses > 0:
            concentration = top.total_uses / total_uses
            lines.append(
                f"- **Top route**: {top.route_key} "
                f"({top.total_uses} uses, "
                f"{concentration:.0%} of all traffic)"
            )

    # Victory path dominance
    for va in report.victory_aggregates:
        if va.candidacy_rate > 0.5:
            lines.append(
                f"- **Dominant path**: {va.path_id} "
                f"(strongest in {va.candidacy_rate:.0%} of runs)"
            )

    lines.append("")


def _add_captain_table(lines: list[str], report: BalanceBatchReport) -> None:
    """Add captain comparison table."""
    lines.append(
        "| Captain | Runs | Brig Day | Galleon Day | "
        "NW@40 | Inspections | Seizures | Defaults | "
        "Contracts OK | Strongest Path |"
    )
    lines.append(
        "|---------|------|----------|-------------|"
        "-------|-------------|----------|----------|"
        "--------------|----------------|"
    )

    for a in report.captain_aggregates:
        brig = f"{a.median_brigantine_day:.0f}" if a.median_brigantine_day > 0 else "-"
        gall = f"{a.median_galleon_day:.0f}" if a.median_galleon_day > 0 else "-"
        nw = f"{a.median_net_worth_40:.0f}"
        # Most frequent strongest path
        top_path = "-"
        if a.strongest_path_freq:
            top_path = max(a.strongest_path_freq, key=a.strongest_path_freq.get)
            top_path = top_path[:20]

        lines.append(
            f"| {a.captain_type:9s} | {a.run_count:4d} | {brig:>8s} | "
            f"{gall:>11s} | {nw:>5s} | "
            f"{a.mean_inspections:>11.1f} | {a.mean_seizures:>8.1f} | "
            f"{a.mean_defaults:>8.1f} | "
            f"{a.mean_contracts_completed:>12.1f} | {top_path:14s} |"
        )

    lines.append("")


def _add_route_table(lines: list[str], report: BalanceBatchReport) -> None:
    """Add top routes table."""
    lines.append("| Route | Uses | Total Profit | Avg Profit | Captain Mix |")
    lines.append("|-------|------|-------------|------------|-------------|")

    for r in report.route_aggregates[:10]:
        mix = ", ".join(
            f"{ct}:{n}" for ct, n in sorted(r.captain_breakdown.items())
        )
        lines.append(
            f"| {r.route_key:30s} | {r.total_uses:4d} | "
            f"{r.total_profit:>11,d} | {r.avg_profit_per_use:>10.0f} | "
            f"{mix} |"
        )

    lines.append("")


def _add_victory_table(lines: list[str], report: BalanceBatchReport) -> None:
    """Add victory path health table."""
    lines.append(
        "| Path | Candidacy | Completion | "
        "Candidacy Rate | Completion Rate | Captain Skew |"
    )
    lines.append(
        "|------|-----------|------------|"
        "---------------|-----------------|--------------|"
    )

    for v in report.victory_aggregates:
        skew = ", ".join(
            f"{ct}:{n}" for ct, n in sorted(v.captain_skew.items())
        )
        lines.append(
            f"| {v.path_id:20s} | {v.candidacy_count:>9d} | "
            f"{v.completion_count:>10d} | "
            f"{v.candidacy_rate:>13.0%} | "
            f"{v.completion_rate:>15.0%} | {skew} |"
        )

    lines.append("")


def _add_infra_table(lines: list[str], report: BalanceBatchReport) -> None:
    """Add infrastructure and finance timing table."""
    lines.append(
        "| Captain | 1st Warehouse | 1st Broker | 1st License | "
        "Insurance % | Credit % |"
    )
    lines.append(
        "|---------|---------------|------------|-------------|"
        "-------------|----------|"
    )

    for a in report.captain_aggregates:
        wh = f"day {a.median_first_warehouse:.0f}" if a.median_first_warehouse > 0 else "-"
        br = f"day {a.median_first_broker:.0f}" if a.median_first_broker > 0 else "-"
        lic = f"day {a.median_first_license:.0f}" if a.median_first_license > 0 else "-"
        lines.append(
            f"| {a.captain_type:9s} | {wh:>13s} | {br:>10s} | "
            f"{lic:>11s} | {a.insurance_adoption_rate:>11.0%} | "
            f"{a.credit_adoption_rate:>8.0%} |"
        )

    lines.append("")
