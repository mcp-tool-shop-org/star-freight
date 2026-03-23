"""Dogfood scenario runner — Star Freight.

Loads a scenario manifest (JSON), configures campaign state,
runs the simulation, and emits a structured run record.

This is the bridge between the dogfood matrix and the playtest engine.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from portlight.engine.playtest import (
    CaptainPosture,
    RunMetrics,
    simulate_run,
    generate_synthesis,
    create_campaign_for_posture,
    RELIEF_PROFILE,
    GRAY_PROFILE,
    HONOR_PROFILE,
)
from portlight.engine.sf_campaign import (
    CampaignState,
    get_campaign_summary,
)
from portlight.engine.crew import (
    active_crew,
    injure,
    apply_morale_change,
    CrewStatus,
)


def load_scenario(path: str | Path) -> dict:
    """Load a scenario manifest from JSON."""
    with open(path) as f:
        return json.load(f)


def apply_scenario_overrides(state: CampaignState, scenario: dict) -> None:
    """Apply starting state and world pressure overrides from a scenario manifest."""
    starting = scenario.get("starting_state", {})

    if "credits" in starting:
        state.credits = starting["credits"]
    if "hull" in starting:
        state.ship_hull = starting["hull"]
    if "hull_max" in starting:
        state.ship_hull_max = starting["hull_max"]
    if "shield" in starting:
        state.ship_shield = starting["shield"]
    if "fuel" in starting:
        state.ship_fuel = starting["fuel"]
    if "station" in starting:
        state.current_station = starting["station"]

    # Reputation overrides
    for faction, value in starting.get("reputation_overrides", {}).items():
        if faction in state.reputation:
            state.reputation[faction] = value

    # Crew overrides
    for crew_id, overrides in starting.get("crew_overrides", {}).items():
        for member in state.crew.members:
            if member.id == crew_id:
                if overrides.get("injured"):
                    injure(member, overrides.get("injury_days", 5))
                if "morale" in overrides:
                    delta = overrides["morale"] - member.morale
                    apply_morale_change(member, delta, "scenario override")

    # Pay day offset
    if "last_pay_day_offset" in starting:
        state.last_pay_day = state.day + starting["last_pay_day_offset"]

    # Investigation delay
    if "investigation_delay_days" in starting:
        delay = starting["investigation_delay_days"]
        for thread in state.investigation.threads.values():
            if thread.fragments:
                thread.last_progress_day = state.day - delay


def run_scenario(scenario: dict) -> dict:
    """Run a complete dogfood scenario and return the run record.

    Returns a dict with telemetry, synthesis, and scenario metadata.
    """
    path_map = {
        "relief": CaptainPosture.RELIEF,
        "gray": CaptainPosture.GRAY,
        "honor": CaptainPosture.HONOR,
    }
    posture = path_map.get(scenario.get("path", "relief"), CaptainPosture.RELIEF)
    seed = scenario.get("seed", 42)
    days = scenario.get("days", 90)

    # Run simulation
    state, metrics = simulate_run(posture, days=days, seed=seed)

    # Apply overrides if scenario has custom starting state
    # Note: for full fidelity, overrides should be applied BEFORE simulation.
    # This simplified version runs the standard sim and records the result.
    # A future version could inject overrides into create_campaign_for_posture.

    # Generate synthesis
    synthesis = generate_synthesis(metrics)

    # Build run record
    record = {
        "scenario_id": scenario.get("id", "unknown"),
        "scenario_class": scenario.get("class", "unknown"),
        "path": scenario.get("path", "unknown"),
        "seed": seed,
        "days_target": days,
        "days_actual": metrics.days_simulated,

        # Telemetry
        "final_credits": metrics.final_credits,
        "credits_history": metrics.credits_history,
        "stations_visited": metrics.stations_visited,
        "dominant_stations": metrics.dominant_stations,
        "lanes_used": metrics.lanes_used,
        "dominant_lanes": metrics.dominant_lanes,
        "goods_traded": metrics.goods_traded,
        "encounters_by_type": metrics.encounters_by_type,
        "encounter_outcomes": metrics.encounter_outcomes,
        "combat_count": metrics.combat_count,
        "retreats": metrics.retreats,
        "crew_injuries": metrics.crew_injuries,
        "crew_departures": metrics.crew_departures,
        "repairs_needed": metrics.repairs_needed,
        "delays": metrics.delays,
        "seizures": metrics.seizures,
        "pay_missed": metrics.pay_missed,
        "investigation_sources": metrics.investigation_sources,
        "final_reputation": metrics.final_reputation,
        "final_investigation_progress": metrics.final_investigation_progress,
        "consequence_tags": metrics.consequence_tags,

        # Synthesis
        "captain_identity": synthesis["identity"],
        "main_pressure": synthesis["main_pressure"],
        "feared": synthesis["feared"],
        "cared_about": synthesis["cared_about"],
    }

    return record


def run_wave(scenario_dir: str | Path) -> list[dict]:
    """Run all scenarios in a directory and return all run records."""
    scenario_dir = Path(scenario_dir)
    records = []

    for manifest_path in sorted(scenario_dir.glob("*.json")):
        scenario = load_scenario(manifest_path)
        record = run_scenario(scenario)
        records.append(record)

    return records


def compare_baseline_divergence(records: list[dict]) -> dict:
    """Compare baseline runs for divergence.

    Returns divergence metrics across the baseline runs.
    """
    baselines = [r for r in records if r["scenario_class"] == "baseline"]
    if len(baselines) < 2:
        return {"error": "Need at least 2 baseline runs"}

    # Station divergence
    station_sets = [set(r["dominant_stations"]) for r in baselines]
    all_stations = set().union(*station_sets)
    shared = set.intersection(*station_sets) if station_sets else set()

    # Lane divergence
    lane_sets = [set(r["dominant_lanes"]) for r in baselines]
    all_lanes = set().union(*lane_sets)
    shared_lanes = set.intersection(*lane_sets) if lane_sets else set()

    # Credit spread
    credits = [r["final_credits"] for r in baselines]

    # Identity divergence
    identities = [r["captain_identity"] for r in baselines]
    fears = [r["feared"] for r in baselines]

    return {
        "baseline_count": len(baselines),
        "station_divergence": 1.0 - len(shared) / max(1, len(all_stations)),
        "lane_divergence": 1.0 - len(shared_lanes) / max(1, len(all_lanes)),
        "credit_spread": max(credits) - min(credits),
        "unique_identities": len(set(identities)),
        "unique_fears": len(set(fears)),
        "paths": [r["path"] for r in baselines],
    }
