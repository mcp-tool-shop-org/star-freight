"""Execute Wave 1 — all 12 dogfood scenarios.

Outputs structured results for the synthesis verdict.
Run from repo root: python dogfood/run_wave1.py
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from portlight.engine.dogfood_runner import (
    run_wave,
    compare_baseline_divergence,
)

SCENARIO_DIR = Path(__file__).parent / "scenarios"
OUTPUT_PATH = Path(__file__).parent / "wave1_results.json"


def main():
    print("=" * 60)
    print("STAR FREIGHT — DOGFOOD WAVE 1")
    print("v0.1.0-dogfood | 12 scenarios | Feature freeze")
    print("=" * 60)
    print()

    # Run all 12 scenarios
    print("Running all 12 scenarios...")
    records = run_wave(SCENARIO_DIR)
    print(f"  Completed: {len(records)} runs\n")

    # Classify runs
    baselines = [r for r in records if r["scenario_class"] == "baseline"]
    stress = [r for r in records if r["scenario_class"] == "stress"]
    recovery = [r for r in records if r["scenario_class"] == "recovery"]
    tui = [r for r in records if r["scenario_class"] == "tui"]

    # === BASELINE DIVERGENCE ===
    print("=" * 60)
    print("BASELINE DIVERGENCE")
    print("=" * 60)
    div = compare_baseline_divergence(records)
    print(f"  Station divergence:  {div['station_divergence']:.2f}")
    print(f"  Lane divergence:     {div['lane_divergence']:.2f}")
    print(f"  Credit spread:       {div['credit_spread']}")
    print(f"  Unique identities:   {div['unique_identities']}/3")
    print(f"  Unique fears:        {div['unique_fears']}/3")
    print()

    for r in baselines:
        print(f"  [{r['path'].upper()}]")
        print(f"    Identity:   {r['captain_identity']}")
        print(f"    Fear:       {r['feared']}")
        print(f"    Credits:    {r['final_credits']}")
        print(f"    Stations:   {r['dominant_stations']}")
        print(f"    Lanes:      {r['dominant_lanes']}")
        print(f"    Combat:     {r['combat_count']} fights, {r['retreats']} retreats")
        print(f"    Goods:      {len(r['goods_traded'])} varieties")
        print(f"    Reputation: {r['final_reputation']}")
        print()

    # === STRESS RUNS ===
    print("=" * 60)
    print("STRESS RUNS")
    print("=" * 60)
    for r in stress:
        print(f"  [{r['scenario_id']}]")
        print(f"    Identity:   {r['captain_identity']}")
        print(f"    Pressure:   {r['main_pressure']}")
        print(f"    Fear:       {r['feared']}")
        print(f"    Credits:    {r['final_credits']}")
        print(f"    Days:       {r['days_actual']}")
        print(f"    Combat:     {r['combat_count']} fights, {r['retreats']} retreats")
        print(f"    Injuries:   {r['crew_injuries']}")
        print(f"    Delays:     {r['delays']}")
        print(f"    Pay missed: {r['pay_missed']}")
        print()

    # === RECOVERY RUNS ===
    print("=" * 60)
    print("RECOVERY RUNS")
    print("=" * 60)
    for r in recovery:
        print(f"  [{r['scenario_id']}]")
        print(f"    Identity:   {r['captain_identity']}")
        print(f"    Pressure:   {r['main_pressure']}")
        print(f"    Credits:    {r['final_credits']}")
        print(f"    Days:       {r['days_actual']}")
        print(f"    Combat:     {r['combat_count']} fights")
        print(f"    Injuries:   {r['crew_injuries']}")
        print(f"    Departures: {r['crew_departures']}")
        print(f"    Pay missed: {r['pay_missed']}")
        print()

    # === TUI RUNS ===
    print("=" * 60)
    print("TUI RUNS")
    print("=" * 60)
    for r in tui:
        print(f"  [{r['scenario_id']}]")
        print(f"    Identity:   {r['captain_identity']}")
        print(f"    Days:       {r['days_actual']}")
        print(f"    Stations:   {len(r['stations_visited'])} unique")
        print(f"    Goods:      {len(r['goods_traded'])} varieties")
        print(f"    Combat:     {r['combat_count']} fights")
        print()

    # === CROSS-RUN ANALYSIS ===
    print("=" * 60)
    print("CROSS-RUN ANALYSIS")
    print("=" * 60)

    # Captain path credit comparison
    print("\n  Credit outcomes by path:")
    for r in records:
        print(f"    {r['scenario_id']:40s} -> {r['final_credits']:>6}cr")

    # Combat frequency comparison
    print("\n  Combat frequency:")
    for r in records:
        print(f"    {r['scenario_id']:40s} -> {r['combat_count']:>3} fights, {r['retreats']:>2} retreats")

    # Investigation sources
    print("\n  Investigation sources used:")
    for r in records:
        if r['investigation_sources']:
            print(f"    {r['scenario_id']:40s} -> {r['investigation_sources']}")

    # Dominant stations across all runs
    print("\n  Dominant stations by run:")
    for r in records:
        print(f"    {r['scenario_id']:40s} -> {r['dominant_stations']}")

    # Save full results
    with open(OUTPUT_PATH, "w") as f:
        json.dump({
            "wave": 1,
            "build": "v0.1.0-dogfood",
            "runs": records,
            "divergence": div,
        }, f, indent=2, default=str)

    print(f"\n  Full results saved to: {OUTPUT_PATH}")
    print()
    print("=" * 60)
    print("WAVE 1 COMPLETE")
    print("=" * 60)

    return records, div


if __name__ == "__main__":
    main()
