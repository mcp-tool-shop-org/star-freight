"""Stress reporting — structured output from stress runs."""

from __future__ import annotations

import json
from pathlib import Path

from portlight.stress.types import StressBatchReport, StressRunReport


def build_batch_report(reports: list[StressRunReport]) -> StressBatchReport:
    """Aggregate individual stress run reports into a batch report."""
    batch = StressBatchReport(
        total_scenarios=len(reports),
        reports=reports,
    )
    failure_by_sub: dict[str, int] = {}
    for r in reports:
        if not r.passed:
            batch.total_failures += 1
            for inv in r.invariant_results:
                sub = inv.subsystem.value if hasattr(inv.subsystem, 'value') else str(inv.subsystem)
                failure_by_sub[sub] = failure_by_sub.get(sub, 0) + 1
    batch.failure_by_subsystem = failure_by_sub
    return batch


def write_json_report(batch: StressBatchReport, path: Path) -> None:
    """Write batch report as JSON."""
    data = {
        "total_scenarios": batch.total_scenarios,
        "total_failures": batch.total_failures,
        "failure_by_subsystem": batch.failure_by_subsystem,
        "scenarios": [],
    }
    for r in batch.reports:
        data["scenarios"].append({
            "scenario_id": r.scenario_id,
            "passed": r.passed,
            "invariant_failures": r.invariant_failures,
            "days_survived": r.days_survived,
            "final_silver": r.final_silver,
            "final_ship_class": r.final_ship_class,
            "notes": r.notes,
            "violations": [
                {
                    "name": inv.name,
                    "subsystem": inv.subsystem.value,
                    "message": inv.message,
                }
                for inv in r.invariant_results
            ],
        })
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def write_markdown_report(batch: StressBatchReport, path: Path) -> None:
    """Write batch report as markdown."""
    lines = [
        "# Stress Report",
        "",
        f"Total scenarios: {batch.total_scenarios}",
        f"Failures: {batch.total_failures}",
        "",
    ]
    if batch.failure_by_subsystem:
        lines.append("## Failures by Subsystem")
        lines.append("")
        for sub, count in sorted(batch.failure_by_subsystem.items()):
            lines.append(f"- **{sub}**: {count}")
        lines.append("")

    lines.append("## Scenario Results")
    lines.append("")
    lines.append("| Scenario | Passed | Violations | Days | Final Silver |")
    lines.append("|----------|--------|------------|------|-------------|")
    for r in batch.reports:
        status = "PASS" if r.passed else "FAIL"
        lines.append(
            f"| {r.scenario_id} | {status} | {r.invariant_failures} | "
            f"{r.days_survived} | {r.final_silver} |"
        )
    lines.append("")

    # Detail on failures
    failed = [r for r in batch.reports if not r.passed]
    if failed:
        lines.append("## Failure Details")
        lines.append("")
        for r in failed:
            lines.append(f"### {r.scenario_id}")
            for inv in r.invariant_results:
                lines.append(f"- **{inv.name}** ({inv.subsystem.value}): {inv.message}")
            lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))
