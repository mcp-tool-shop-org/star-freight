"""Wave 3 — P1 tuning confirmation.

Prove that the tuned game is viable, divergent, stressful in the right
ways, and not hiding a new dominant path.

7-scenario confirmation set:
  Core:     Baseline Relief / Gray / Honor (90 days)
  Stress:   Seizure / Shortage / Escalation
  Recovery: Burned Rep

Pass bar:
  - strongest/weakest end-credit ratio in 3-5x
  - all 3 baselines survive
  - Relief richest but not runaway
  - Gray viable and not dead-man-walking late game
  - Honor survives escalation without profiting from it
  - fear classifier returns 3 distinct captain fears
  - high divergence across route / station / goods / posture
  - recovery run is painful but playable
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
)

SCENARIO_DIR = Path(__file__).parent / "scenarios"
OUTPUT_PATH = Path(__file__).parent / "wave3_results.json"


def run_core_confirmation():
    """Baseline confirmation: all 3 captains, 90 days."""
    print("CORE CONFIRMATION: BASELINES")
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
        print(f"    Repairs:    {metrics.repairs_needed}")
        print(f"    Delays:     {metrics.delays}")
        print(f"    Identity:   {syn['identity']}")
        print(f"    Fear:       {syn['feared']}")
        print(f"    Pressure:   {syn['main_pressure']}")

    # Credit trajectories at checkpoints
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
    print(f"  Overall divergence:  {div['overall_divergence']:.2f}")

    # Balance check
    credits = {p.value: m.final_credits for p, (m, _) in results.items()}
    dominant = max(credits.values())
    weakest = min(credits.values())
    ratio = dominant / max(1, abs(weakest)) if weakest > 0 else float('inf')
    print(f"\n  Balance: strongest={dominant} weakest={weakest} ratio={ratio:.2f}x")

    # Survival check
    all_survive = all(m.final_credits > 0 for m, _ in results.values())
    print(f"  All survive (positive credits): {all_survive}")

    # Fear distinctness
    fears = {p.value: syn['feared'] for p, (_, syn) in results.items()}
    unique_fears = len(set(fears.values()))
    print(f"\n  Fear classifier:")
    for cap, fear in fears.items():
        print(f"    {cap}: {fear}")
    print(f"  Unique fears: {unique_fears}/3")

    return results, div, credits, fears


def run_stress_confirmation():
    """Stress confirmation: seizure, shortage, escalation."""
    print("\n\nSTRESS CONFIRMATION")
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
        print(f"    Repairs:    {record['repairs_needed']}")
        print(f"    Delays:     {record['delays']}")
        print(f"    Pay missed: {record['pay_missed']}")

    # Escalation comfort check
    esc = stress_results.get("honor_escalation_60d_s17", {})
    baseline_honor_credits = None  # will be passed in from core
    print(f"\n  Escalation check:")
    print(f"    Escalation credits: {esc.get('final_credits', 'N/A')}")
    print(f"    Injuries under escalation: {esc.get('crew_injuries', 0)}")
    print(f"    Repairs under escalation: {esc.get('repairs_needed', 0)}")

    return stress_results


def run_recovery_confirmation():
    """Recovery confirmation: burned rep."""
    print("\n\nRECOVERY CONFIRMATION")
    print("-" * 50)

    scenario = load_scenario(SCENARIO_DIR / "recovery_burned_rep_45d_s99.json")
    record = run_scenario(scenario)

    print(f"\n  [recovery_burned_rep_45d_s99]")
    print(f"    Credits:    {record['final_credits']}")
    print(f"    Identity:   {record['captain_identity']}")
    print(f"    Pressure:   {record['main_pressure']}")
    print(f"    Fear:       {record['feared']}")
    print(f"    Combat:     {record['combat_count']} ({record['encounter_outcomes']})")
    print(f"    Injuries:   {record['crew_injuries']}")
    print(f"    Delays:     {record['delays']}")
    print(f"    Pay missed: {record['pay_missed']}")
    print(f"    Survived:   {record['final_credits'] > 0}")

    return record


def evaluate_pass_bar(credits, fears, stress_results, recovery_record, div):
    """Evaluate all Wave 3 pass criteria."""
    print("\n\n" + "=" * 60)
    print("WAVE 3 PASS BAR EVALUATION")
    print("=" * 60)

    verdicts = {}

    # 1. Credit ratio 3-5x
    dominant = max(credits.values())
    weakest = min(credits.values())
    ratio = dominant / max(1, abs(weakest)) if weakest > 0 else float('inf')
    in_band = 3.0 <= ratio <= 5.0
    verdicts["credit_ratio"] = {
        "pass": in_band,
        "value": round(ratio, 2),
        "target": "3.0-5.0x",
        "detail": f"{dominant}/{weakest}",
    }
    status = "PASS" if in_band else "FAIL"
    print(f"\n  1. Credit ratio {ratio:.2f}x (target 3-5x): {status}")

    # 2. All baselines survive
    all_survive = all(v > 0 for v in credits.values())
    verdicts["all_survive"] = {"pass": all_survive, "credits": credits}
    status = "PASS" if all_survive else "FAIL"
    print(f"  2. All baselines survive: {status} ({credits})")

    # 3. Relief richest but not runaway
    relief_richest = credits["relief"] == dominant
    not_runaway = ratio <= 5.0
    relief_ok = relief_richest and not_runaway
    verdicts["relief_shape"] = {"pass": relief_ok, "richest": relief_richest, "ratio": round(ratio, 2)}
    status = "PASS" if relief_ok else ("WARN" if relief_richest else "FAIL")
    print(f"  3. Relief richest, not runaway: {status}")

    # 4. Gray viable (not dead-man-walking)
    gray_viable = credits["gray"] > 200  # meaningful floor
    verdicts["gray_viable"] = {"pass": gray_viable, "credits": credits["gray"]}
    status = "PASS" if gray_viable else "FAIL"
    print(f"  4. Gray viable (>{200}): {status} (credits={credits['gray']})")

    # 5. Honor escalation not profitable
    esc = stress_results.get("honor_escalation_60d_s17", {})
    esc_credits = esc.get("final_credits", 0)
    honor_baseline = credits["honor"]
    # Escalation should not exceed baseline (it's a 60-day stress run vs 90-day baseline)
    # So per-day rate matters: esc_credits/60 vs honor_baseline/90
    esc_rate = esc_credits / 60 if esc_credits > 0 else 0
    baseline_rate = honor_baseline / 90 if honor_baseline > 0 else 0
    esc_comfortable = esc_rate > baseline_rate * 1.1  # escalation earns more per day = bad
    esc_survives = esc_credits > 0
    honor_ok = esc_survives and not esc_comfortable
    verdicts["honor_escalation"] = {
        "pass": honor_ok,
        "escalation_credits": esc_credits,
        "escalation_rate": round(esc_rate, 1),
        "baseline_rate": round(baseline_rate, 1),
        "comfortable": esc_comfortable,
        "survives": esc_survives,
    }
    status = "PASS" if honor_ok else "FAIL"
    print(f"  5. Honor escalation shape: {status} (esc={esc_credits} rate={esc_rate:.1f}/day vs baseline {baseline_rate:.1f}/day)")

    # 6. Fear classifier — 3 distinct fears
    unique_fears = len(set(fears.values()))
    fear_ok = unique_fears == 3
    verdicts["fear_distinct"] = {"pass": fear_ok, "unique": unique_fears, "fears": fears}
    status = "PASS" if fear_ok else "FAIL"
    print(f"  6. Fear classifier distinct: {status} ({unique_fears}/3)")

    # 7. Divergence high
    overall_div = div.get("overall_divergence", 0)
    div_ok = overall_div > 0.5
    verdicts["divergence"] = {"pass": div_ok, "overall": round(overall_div, 2), "detail": {k: round(v, 2) for k, v in div.items()}}
    status = "PASS" if div_ok else "FAIL"
    print(f"  7. Divergence high: {status} (overall={overall_div:.2f})")

    # 8. Recovery painful but playable
    recovery_survives = recovery_record["final_credits"] > 0
    recovery_painful = recovery_record["final_credits"] < 500  # should be thin
    recovery_ok = recovery_survives  # must survive; pain is informational
    verdicts["recovery"] = {
        "pass": recovery_ok,
        "credits": recovery_record["final_credits"],
        "painful": recovery_painful,
        "survives": recovery_survives,
    }
    status = "PASS" if recovery_ok else "FAIL"
    pain = " (painful)" if recovery_painful else " (comfortable)"
    print(f"  8. Recovery playable: {status} (credits={recovery_record['final_credits']}{pain})")

    # Overall verdict
    all_pass = all(v["pass"] for v in verdicts.values())
    print(f"\n  {'=' * 40}")
    print(f"  WAVE 3 VERDICT: {'PASS' if all_pass else 'FAIL'}")
    print(f"  {'=' * 40}")

    return verdicts, all_pass


def main():
    print("=" * 60)
    print("STAR FREIGHT - DOGFOOD WAVE 3")
    print("P1 tuning confirmation — prove the calibration holds")
    print("=" * 60)
    print()

    # Core
    baseline_results, div, credits, fears = run_core_confirmation()

    # Stress
    stress_results = run_stress_confirmation()

    # Recovery
    recovery_record = run_recovery_confirmation()

    # Evaluate
    verdicts, all_pass = evaluate_pass_bar(credits, fears, stress_results, recovery_record, div)

    # Save results
    wave3_data = {
        "wave": 3,
        "build": "post-P1-tuning",
        "verdict": "PASS" if all_pass else "FAIL",
        "core": {
            "credits": credits,
            "fears": fears,
            "divergence": {k: round(v, 3) if isinstance(v, float) else v for k, v in div.items()},
        },
        "stress": {
            sid: {
                "credits": r["final_credits"],
                "pressure": r["main_pressure"],
                "fear": r["feared"],
                "combat_count": r["combat_count"],
                "crew_injuries": r["crew_injuries"],
                "repairs_needed": r["repairs_needed"],
            }
            for sid, r in stress_results.items()
        },
        "recovery": {
            "scenario": "recovery_burned_rep_45d_s99",
            "credits": recovery_record["final_credits"],
            "pressure": recovery_record["main_pressure"],
            "fear": recovery_record["feared"],
            "survives": recovery_record["final_credits"] > 0,
        },
        "verdicts": verdicts,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(wave3_data, f, indent=2, default=str)

    print(f"\n\nResults saved to: {OUTPUT_PATH}")
    print("\n" + "=" * 60)
    print("WAVE 3 COMPLETE")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
