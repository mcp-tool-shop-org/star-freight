"""Dogfood runner tests — verify scenario loading and execution."""

import json
from pathlib import Path

from portlight.engine.dogfood_runner import (
    load_scenario,
    run_scenario,
    run_wave,
    compare_baseline_divergence,
)


SCENARIO_DIR = Path("F:/AI/star-freight/dogfood/scenarios")


class TestScenarioLoading:
    def test_load_relief_baseline(self):
        s = load_scenario(SCENARIO_DIR / "relief_baseline_90d_s42.json")
        assert s["id"] == "relief_baseline_90d_s42"
        assert s["path"] == "relief"
        assert s["days"] == 90

    def test_load_all_scenarios(self):
        manifests = list(SCENARIO_DIR.glob("*.json"))
        assert len(manifests) == 12
        for path in manifests:
            s = load_scenario(path)
            assert "id" in s
            assert "path" in s
            assert "seed" in s


class TestScenarioExecution:
    def test_run_relief_baseline(self):
        s = load_scenario(SCENARIO_DIR / "relief_baseline_90d_s42.json")
        record = run_scenario(s)
        assert record["scenario_id"] == "relief_baseline_90d_s42"
        assert record["days_actual"] >= 30
        assert record["captain_identity"] != ""

    def test_run_stress_scenario(self):
        s = load_scenario(SCENARIO_DIR / "gray_seizure_60d_s17.json")
        record = run_scenario(s)
        assert record["scenario_class"] == "stress"
        assert record["days_actual"] >= 20

    def test_run_recovery_scenario(self):
        s = load_scenario(SCENARIO_DIR / "recovery_broke_hull_45d_s99.json")
        record = run_scenario(s)
        assert record["scenario_class"] == "recovery"


class TestWaveExecution:
    def test_run_full_wave(self):
        records = run_wave(SCENARIO_DIR)
        assert len(records) == 12
        classes = {r["scenario_class"] for r in records}
        assert "baseline" in classes
        assert "stress" in classes
        assert "recovery" in classes
        assert "tui" in classes

    def test_baseline_divergence(self):
        records = run_wave(SCENARIO_DIR)
        div = compare_baseline_divergence(records)
        assert div["baseline_count"] == 3
        assert div["unique_identities"] >= 2  # at least 2 distinct captain identities
        assert len(div["paths"]) == 3
