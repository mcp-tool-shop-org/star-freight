"""Tests for weapon quality — degradation, maintenance, smith upgrades, combat integration."""

from __future__ import annotations

import random


from portlight.engine.weapon_quality import (
    MELEE_DEGRADE_USES,
    QUALITY_TIERS,
    UPGRADE_COST,
    assign_loot_quality,
    assign_purchase_quality,
    can_upgrade,
    check_degradation,
    degrade_quality,
    get_maintenance_cost,
    get_quality_display,
    get_quality_effects,
    get_weapon_summary,
    maintain_weapon,
    tick_weapon_degradation,
    upgrade_weapon,
)


def _rng(seed: int = 42) -> random.Random:
    return random.Random(seed)


# ---------------------------------------------------------------------------
# Quality tiers
# ---------------------------------------------------------------------------

class TestQualityTiers:
    def test_five_tiers_defined(self):
        assert len(QUALITY_TIERS) == 5

    def test_tier_order(self):
        assert QUALITY_TIERS == ("rusted", "worn", "standard", "fine", "masterwork")

    def test_all_tiers_have_effects(self):
        for tier in QUALITY_TIERS:
            effects = get_quality_effects(tier)
            assert effects.label
            assert effects.color

    def test_rusted_penalties(self):
        e = get_quality_effects("rusted")
        assert e.damage_mod == -1
        assert e.accuracy_mod == -0.10

    def test_standard_neutral(self):
        e = get_quality_effects("standard")
        assert e.damage_mod == 0
        assert e.accuracy_mod == 0.0

    def test_masterwork_bonuses(self):
        e = get_quality_effects("masterwork")
        assert e.damage_mod == 2
        assert e.accuracy_mod == 0.10

    def test_unknown_tier_defaults_to_standard(self):
        e = get_quality_effects("nonexistent")
        assert e.damage_mod == 0


# ---------------------------------------------------------------------------
# Degradation
# ---------------------------------------------------------------------------

class TestDegradation:
    def test_degrade_standard_to_worn(self):
        assert degrade_quality("standard") == "worn"

    def test_degrade_masterwork_to_fine(self):
        assert degrade_quality("masterwork") == "fine"

    def test_degrade_rusted_stays_rusted(self):
        assert degrade_quality("rusted") == "rusted"

    def test_check_degradation_at_threshold(self):
        assert check_degradation("cutlass", "melee", MELEE_DEGRADE_USES) is True

    def test_check_degradation_below_threshold(self):
        assert check_degradation("cutlass", "melee", MELEE_DEGRADE_USES - 1) is False

    def test_tick_degrades_at_threshold(self):
        quality = {"cutlass": "standard"}
        usage = {"cutlass": MELEE_DEGRADE_USES - 1}  # one more use will trigger
        degraded, new_q = tick_weapon_degradation(quality, usage, "cutlass", "melee")
        assert degraded is True
        assert new_q == "worn"
        assert quality["cutlass"] == "worn"
        assert usage["cutlass"] == 0  # reset after degradation

    def test_tick_no_degrade_below_threshold(self):
        quality = {"cutlass": "standard"}
        usage = {"cutlass": 0}
        degraded, _ = tick_weapon_degradation(quality, usage, "cutlass", "melee")
        assert degraded is False

    def test_tick_rusted_never_degrades(self):
        quality = {"cutlass": "rusted"}
        usage = {"cutlass": 100}
        degraded, _ = tick_weapon_degradation(quality, usage, "cutlass", "melee")
        assert degraded is False

    def test_usage_accumulates(self):
        quality = {"cutlass": "standard"}
        usage = {}
        tick_weapon_degradation(quality, usage, "cutlass", "melee", uses=3)
        assert usage["cutlass"] == 3
        tick_weapon_degradation(quality, usage, "cutlass", "melee", uses=2)
        assert usage["cutlass"] == 5


# ---------------------------------------------------------------------------
# Maintenance
# ---------------------------------------------------------------------------

class TestMaintenance:
    def test_maintain_resets_usage(self):
        quality = {"cutlass": "standard"}
        usage = {"cutlass": 8}
        remaining, error = maintain_weapon("cutlass", quality, usage, silver=100)
        assert error is None
        assert usage["cutlass"] == 0
        assert remaining < 100

    def test_maintain_not_enough_silver(self):
        quality = {"cutlass": "fine"}
        usage = {"cutlass": 5}
        _, error = maintain_weapon("cutlass", quality, usage, silver=1)
        assert error is not None
        assert "silver" in error.lower()

    def test_maintenance_cost_scales_with_quality(self):
        low = get_maintenance_cost("cutlass", {"cutlass": "worn"})
        high = get_maintenance_cost("cutlass", {"cutlass": "masterwork"})
        assert high > low


# ---------------------------------------------------------------------------
# Smith upgrades
# ---------------------------------------------------------------------------

class TestSmithUpgrade:
    def test_can_upgrade_standard(self):
        error = can_upgrade("cutlass", {"cutlass": "standard"}, silver=200, at_smith=True)
        assert error is None

    def test_cant_upgrade_masterwork(self):
        error = can_upgrade("cutlass", {"cutlass": "masterwork"}, silver=1000, at_smith=True)
        assert error is not None
        assert "masterwork" in error.lower()

    def test_cant_upgrade_no_smith(self):
        error = can_upgrade("cutlass", {"cutlass": "standard"}, silver=200, at_smith=False)
        assert error is not None
        assert "smith" in error.lower()

    def test_cant_upgrade_no_silver(self):
        error = can_upgrade("cutlass", {"cutlass": "standard"}, silver=5, at_smith=True)
        assert error is not None

    def test_upgrade_changes_quality(self):
        quality = {"cutlass": "standard"}
        usage = {"cutlass": 5}
        new_q, remaining, days = upgrade_weapon("cutlass", quality, usage, silver=500)
        assert new_q == "fine"
        assert quality["cutlass"] == "fine"
        assert usage["cutlass"] == 0  # reset
        assert remaining == 500 - UPGRADE_COST["standard"]
        assert days > 0

    def test_upgrade_from_rusted(self):
        quality = {"cutlass": "rusted"}
        usage = {}
        new_q, _, _ = upgrade_weapon("cutlass", quality, usage, silver=500)
        assert new_q == "worn"

    def test_upgrade_cost_escalates(self):
        assert UPGRADE_COST["rusted"] < UPGRADE_COST["standard"] < UPGRADE_COST["fine"]


# ---------------------------------------------------------------------------
# Loot quality
# ---------------------------------------------------------------------------

class TestLootQuality:
    def test_purchase_always_standard(self):
        assert assign_purchase_quality() == "standard"

    def test_weak_opponent_mostly_rusted(self):
        qualities = [assign_loot_quality(2, _rng(s)) for s in range(100)]
        assert qualities.count("rusted") > 20
        assert "masterwork" not in qualities

    def test_strong_opponent_can_drop_fine(self):
        qualities = [assign_loot_quality(8, _rng(s)) for s in range(100)]
        assert "fine" in qualities

    def test_boss_can_drop_masterwork(self):
        qualities = [assign_loot_quality(9, _rng(s)) for s in range(200)]
        assert "masterwork" in qualities

    def test_all_qualities_in_valid_tiers(self):
        for strength in range(1, 11):
            for seed in range(50):
                q = assign_loot_quality(strength, _rng(seed))
                assert q in QUALITY_TIERS


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

class TestDisplayHelpers:
    def test_quality_display_has_markup(self):
        display = get_quality_display("cutlass", {"cutlass": "fine"})
        assert "Fine" in display
        assert "green" in display

    def test_weapon_summary(self):
        summary = get_weapon_summary(
            "cutlass", "Cutlass",
            {"cutlass": "worn"}, {"cutlass": 7},
            "melee",
        )
        assert summary["quality"] == "worn"
        assert summary["usage"] == 7
        assert summary["near_degradation"] is True  # 7 of 10 = 3 remaining

    def test_near_degradation_flag(self):
        summary = get_weapon_summary(
            "cutlass", "Cutlass",
            {"cutlass": "standard"}, {"cutlass": 1},
            "melee",
        )
        assert summary["near_degradation"] is False


# ---------------------------------------------------------------------------
# Combat integration
# ---------------------------------------------------------------------------

class TestCombatIntegration:
    def test_quality_affects_melee_damage(self):
        """Fine weapons should deal more average damage than rusted ones."""
        from portlight.engine.combat import _calc_melee_damage

        fine_dmg = []
        rusted_dmg = []
        for seed in range(100):
            rng = random.Random(seed)
            d1 = _calc_melee_damage("thrust", "win", rng, weapon_quality="fine")
            rng2 = random.Random(seed)
            d2 = _calc_melee_damage("thrust", "win", rng2, weapon_quality="rusted")
            fine_dmg.append(d1)
            rusted_dmg.append(d2)
        assert sum(fine_dmg) > sum(rusted_dmg)

    def test_quality_affects_ranged_accuracy(self):
        """Fine ranged weapons should hit more often."""
        from portlight.engine.combat import _calc_ranged_damage

        fine_hits = 0
        rusted_hits = 0
        for seed in range(200):
            _, hit_f = _calc_ranged_damage("matchlock_pistol", random.Random(seed), weapon_quality="fine")
            _, hit_r = _calc_ranged_damage("matchlock_pistol", random.Random(seed), weapon_quality="rusted")
            if hit_f:
                fine_hits += 1
            if hit_r:
                rusted_hits += 1
        assert fine_hits > rusted_hits

    def test_save_load_roundtrip(self):
        """Quality and usage should survive save/load."""
        from portlight.engine.models import CombatGear
        from portlight.engine.save import _combat_gear_from_dict, _combat_gear_to_dict

        gear = CombatGear(
            melee_weapon="rapier",
            weapon_quality={"rapier": "fine", "matchlock_pistol": "worn"},
            weapon_usage={"rapier": 7, "matchlock_pistol": 12},
        )
        d = _combat_gear_to_dict(gear)
        restored = _combat_gear_from_dict(d)
        assert restored.weapon_quality == {"rapier": "fine", "matchlock_pistol": "worn"}
        assert restored.weapon_usage == {"rapier": 7, "matchlock_pistol": 12}
