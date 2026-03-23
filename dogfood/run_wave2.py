"""Wave 2 — Confirmation wave.

Did the economy repair reveal the real remaining issues, or hide a new imbalance?

Pass A: Baseline confirmation (3 runs)
Pass B: Investigation source diversity (3 runs)
Pass C: Stress confirmation (3 runs)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from portlight.engine.playtest import (
    CaptainPosture,
    simulate_run,
    generate_synthesis,
    analyze_divergence,
    RunMetrics,
)
from portlight.engine.dogfood_runner import (
    load_scenario,
    run_scenario,
    compare_baseline_divergence,
)

SCENARIO_DIR = Path(__file__).parent / "scenarios"
OUTPUT_PATH = Path(__file__).parent / "wave2_results.json"


def run_pass_a():
    """Baseline confirmation: all 3 captains, 90 days."""
    print("PASS A: BASELINE CONFIRMATION")
    print("-" * 50)

    results = {}
    for posture in [CaptainPosture.RELIEF, CaptainPosture.GRAY, CaptainPosture.HONOR]:
        state, metrics = simulate_run(posture, days=90, seed=42)
        syn = generate_synthesis(metrics)
        results[posture] = (metrics, syn)

        total_sold = sum(v for k, v in metrics.goods_traded.items() if k.startswith('sell_'))
        total_bought = sum(v for k, v in metrics.goods_traded.items() if k.startswith('buy_'))

        print(f"\n  [{posture.value.upper()}]")
        print(f"    Credits:    {metrics.final_credits}")
        print(f"    Trade:      B:{total_bought} S:{total_sold}")
        print(f"    Combat:     {metrics.combat_count} ({metrics.encounter_outcomes})")
        print(f"    Pay missed: {metrics.pay_missed}")
        print(f"    Injuries:   {metrics.crew_injuries}")
        print(f"    Identity:   {syn['identity']}")
        print(f"    Fear:       {syn['feared']}")
        print(f"    Pressure:   {syn['main_pressure']}")

    # Credit snapshots at key intervals
    print("\n  Credit trajectories:")
    for day_target in [30, 60, 90]:
        line = f"    Day {day_target:>2}: "
        for p in [CaptainPosture.RELIEF, CaptainPosture.GRAY, CaptainPosture.HONOR]:
            _, m = simulate_run(p, days=day_target, seed=42)
            line += f"  {p.value}={m.final_credits:>5}"
        print(line)

    # Divergence
    m_r, _ = results[CaptainPosture.RELIEF]
    m_g, _ = results[CaptainPosture.GRAY]
    m_h, _ = results[CaptainPosture.HONOR]
    div = analyze_divergence(m_r, m_g, m_h)
    print(f"\n  Divergence: station={div['route_divergence']:.2f} lane={div['lane_divergence']:.2f} trade={div['trade_divergence']:.2f}")
    print(f"  Economic divergence: {div['economic_divergence']:.2f}")

    # Balance check
    credits = [m_r.final_credits, m_g.final_credits, m_h.final_credits]
    dominant = max(credits)
    weakest = min(credits)
    ratio = dominant / max(1, abs(weakest)) if weakest > 0 else float('inf')
    print(f"\n  Balance: strongest/weakest = {dominant}/{weakest} (ratio: {ratio:.1f}x)")

    all_survive = all(m.pay_missed == 0 for m, _ in results.values())
    print(f"  All survive without missed pay: {all_survive}")

    return results, div


def run_pass_b():
    """Investigation source diversity."""
    print("\n\nPASS B: INVESTIGATION SOURCE DIVERSITY")
    print("-" * 50)

    # Run each captain and track investigation sources
    source_report = {}
    for posture in [CaptainPosture.RELIEF, CaptainPosture.GRAY, CaptainPosture.HONOR]:
        state, metrics = simulate_run(posture, days=90, seed=42)
        source_report[posture.value] = {
            "sources": metrics.investigation_sources,
            "fragments_total": sum(metrics.investigation_sources.values()) if metrics.investigation_sources else 0,
            "source_types": list(metrics.investigation_sources.keys()) if metrics.investigation_sources else [],
        }
        print(f"\n  [{posture.value.upper()}]")
        print(f"    Investigation sources: {metrics.investigation_sources}")
        print(f"    Total fragments: {source_report[posture.value]['fragments_total']}")
        print(f"    Source types: {source_report[posture.value]['source_types']}")

    # Diversity check
    all_source_types = set()
    for data in source_report.values():
        all_source_types.update(data["source_types"])

    print(f"\n  Total unique source types across all runs: {len(all_source_types)}")
    print(f"  Source types seen: {sorted(all_source_types)}")

    non_station = [s for s in all_source_types if s != "station"]
    print(f"  Non-station sources: {non_station}")

    return source_report


def run_pass_c():
    """Stress confirmation post-fix."""
    print("\n\nPASS C: STRESS CONFIRMATION")
    print("-" * 50)

    stress_scenarios = [
        "gray_seizure_60d_s17",
        "relief_shortage_60d_s17",
        "honor_escalation_60d_s17",
    ]

    stress_results = {}
    for scenario_id in stress_scenarios:
        scenario = load_scenario(SCENARIO_DIR / f"{scenario_id}.json")
        record = run_scenario(scenario)
        stress_results[scenario_id] = record

        print(f"\n  [{scenario_id}]")
        print(f"    Credits:    {record['final_credits']}")
        print(f"    Identity:   {record['captain_identity']}")
        print(f"    Pressure:   {record['main_pressure']}")
        print(f"    Fear:       {record['feared']}")
        print(f"    Combat:     {record['combat_count']} ({record['encounter_outcomes']})")
        print(f"    Injuries:   {record['crew_injuries']}")
        print(f"    Delays:     {record['delays']}")
        print(f"    Pay missed: {record['pay_missed']}")

    # Stress signal clarity
    print("\n  Stress signal clarity:")
    for sid, r in stress_results.items():
        economic_signal = r['final_credits'] < 0
        pressure_signal = r['main_pressure']
        print(f"    {sid}: credits={r['final_credits']}, pressure='{pressure_signal}', economic_death={'YES' if economic_signal else 'no'}")

    return stress_results


def main():
    print("=" * 60)
    print("STAR FREIGHT - DOGFOOD WAVE 2")
    print("Confirmation wave post-P0 economy fix")
    print("=" * 60)
    print()

    baseline_results, div = run_pass_a()
    source_report = run_pass_b()
    stress_results = run_pass_c()

    # Save results
    wave2_data = {
        "wave": 2,
        "build": "post-P0-economy-fix",
        "pass_a": {
            "divergence": div,
            "credits": {p.value: m.final_credits for p, (m, _) in baseline_results.items()},
            "all_survive": all(m.pay_missed == 0 for m, _ in baseline_results.values()),
        },
        "pass_b": source_report,
        "pass_c": {sid: {"credits": r["final_credits"], "pressure": r["main_pressure"],
                         "fear": r["feared"]} for sid, r in stress_results.items()},
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(wave2_data, f, indent=2, default=str)

    print(f"\n\nResults saved to: {OUTPUT_PATH}")
    print("\n" + "=" * 60)
    print("WAVE 2 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
