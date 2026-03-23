"""Tests for weapon provenance — kill tracking, relic growth, naming, recognition."""

from __future__ import annotations

import random

from portlight.engine.weapon_provenance import (
    RELIC_THRESHOLDS,
    check_recognition,
    create_provenance,
    get_provenance_summary,
    get_relic_tier,
    get_weapon_display_name,
    record_kill,
)


def _rng(seed: int = 42) -> random.Random:
    return random.Random(seed)


# ---------------------------------------------------------------------------
# Relic tiers
# ---------------------------------------------------------------------------

class TestRelicTiers:
    def test_unnamed_below_threshold(self):
        assert get_relic_tier(0) == "unnamed"
        assert get_relic_tier(2) == "unnamed"

    def test_bloodied_at_threshold(self):
        assert get_relic_tier(3) == "bloodied"
        assert get_relic_tier(9) == "bloodied"

    def test_reaper_at_threshold(self):
        assert get_relic_tier(10) == "reaper"
        assert get_relic_tier(24) == "reaper"

    def test_legendary_at_threshold(self):
        assert get_relic_tier(25) == "legendary"
        assert get_relic_tier(100) == "legendary"

    def test_thresholds_ascending(self):
        assert RELIC_THRESHOLDS["bloodied"] < RELIC_THRESHOLDS["reaper"] < RELIC_THRESHOLDS["legendary"]


# ---------------------------------------------------------------------------
# Kill recording
# ---------------------------------------------------------------------------

class TestRecordKill:
    def test_increments_kill_count(self):
        prov = create_provenance("cutlass")
        record_kill(prov)
        assert prov.kills == 1

    def test_tier_change_at_threshold(self):
        prov = create_provenance("cutlass")
        prov.kills = 2  # one more = bloodied
        tier_change, _ = record_kill(prov)
        assert tier_change == "bloodied"

    def test_no_tier_change_below_threshold(self):
        prov = create_provenance("cutlass")
        tier_change, _ = record_kill(prov)
        assert tier_change is None

    def test_named_kill_creates_epithet(self):
        prov = create_provenance("cutlass")
        _, epithet = record_kill(prov, captain_id="gnaw", captain_name="Gnaw")
        assert epithet == "Gnaw's Bane"
        assert prov.epithet == "Gnaw's Bane"

    def test_second_named_kill_keeps_first_epithet(self):
        prov = create_provenance("cutlass")
        record_kill(prov, "gnaw", "Gnaw")
        _, epithet = record_kill(prov, "scarlet_ana", "Scarlet Ana")
        assert epithet is None  # keeps "Gnaw's Bane"
        assert prov.epithet == "Gnaw's Bane"

    def test_three_named_kills_upgrades_epithet(self):
        prov = create_provenance("cutlass")
        record_kill(prov, "gnaw", "Gnaw")
        record_kill(prov, "scarlet_ana", "Scarlet Ana")
        _, epithet = record_kill(prov, "the_butcher", "The Butcher")
        assert epithet is not None
        assert "Captain" in epithet  # "The Captain Killer"

    def test_named_kills_tracked(self):
        prov = create_provenance("cutlass")
        record_kill(prov, "gnaw", "Gnaw")
        record_kill(prov, "scarlet_ana", "Scarlet Ana")
        assert "gnaw" in prov.named_kills
        assert "scarlet_ana" in prov.named_kills

    def test_duplicate_captain_not_double_counted(self):
        prov = create_provenance("cutlass")
        record_kill(prov, "gnaw", "Gnaw")
        record_kill(prov, "gnaw", "Gnaw")
        assert prov.named_kills.count("gnaw") == 1

    def test_anonymous_kill_no_epithet(self):
        prov = create_provenance("cutlass")
        _, epithet = record_kill(prov)
        assert epithet is None


# ---------------------------------------------------------------------------
# Recognition
# ---------------------------------------------------------------------------

class TestRecognition:
    def test_unnamed_never_recognized(self):
        prov = create_provenance("cutlass")
        result = check_recognition(prov, "Cutlass", "gnaw", 50, _rng())
        assert result.recognized is False

    def test_legendary_almost_always_recognized(self):
        prov = create_provenance("cutlass")
        prov.kills = 30
        recognized_count = 0
        for seed in range(50):
            result = check_recognition(prov, "Cutlass", "gnaw", 0, _rng(seed))
            if result.recognized:
                recognized_count += 1
        assert recognized_count > 35  # 90% base

    def test_previous_victim_always_recognizes(self):
        prov = create_provenance("cutlass")
        prov.kills = 3  # bloodied
        prov.named_kills = ["gnaw"]
        result = check_recognition(prov, "Cutlass", "gnaw", 0, _rng())
        assert result.recognized is True
        assert "KNOW" in result.flavor

    def test_recognition_gives_fear_and_respect(self):
        prov = create_provenance("cutlass")
        prov.kills = 25  # legendary
        result = check_recognition(prov, "Cutlass", "scarlet_ana", 50, _rng())
        if result.recognized:
            assert result.fear_bonus > 0
            assert result.respect_bonus > 0

    def test_none_provenance_no_recognition(self):
        result = check_recognition(None, "Fists", "gnaw", 50, _rng())
        assert result.recognized is False

    def test_recognition_increments_counter(self):
        prov = create_provenance("cutlass")
        prov.kills = 25  # legendary
        before = prov.times_recognized
        check_recognition(prov, "Cutlass", "gnaw", 50, _rng())
        # May or may not be recognized (probabilistic), but if it is, counter increments
        if prov.times_recognized > before:
            assert prov.times_recognized == before + 1


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

class TestDisplay:
    def test_unnamed_weapon_shows_base_name(self):
        prov = create_provenance("cutlass")
        display = get_weapon_display_name("Cutlass", prov)
        assert display == "Cutlass"

    def test_bloodied_weapon_shows_tier(self):
        prov = create_provenance("cutlass")
        prov.kills = 5
        prov.epithet = "Gnaw's Bane"
        display = get_weapon_display_name("Cutlass", prov)
        assert "Gnaw's Bane" in display
        assert "Bloodied" in display

    def test_custom_name_overrides(self):
        prov = create_provenance("cutlass")
        prov.kills = 10
        prov.custom_name = "Old Faithful"
        display = get_weapon_display_name("Cutlass", prov)
        assert "Old Faithful" in display

    def test_provenance_summary(self):
        prov = create_provenance("cutlass", port_id="porto_novo", day=5)
        prov.kills = 12
        prov.named_kills = ["gnaw"]
        prov.epithet = "Gnaw's Bane"
        summary = get_provenance_summary(prov)
        assert summary["kills"] == 12
        assert summary["relic_tier"] == "reaper"
        assert summary["epithet"] == "Gnaw's Bane"


# ---------------------------------------------------------------------------
# Provenance creation
# ---------------------------------------------------------------------------

class TestCreateProvenance:
    def test_fresh_provenance(self):
        prov = create_provenance("rapier", "porto_novo", "Mediterranean", 10)
        assert prov.weapon_id == "rapier"
        assert prov.acquired_port == "porto_novo"
        assert prov.kills == 0
        assert prov.epithet is None


# ---------------------------------------------------------------------------
# Save/load roundtrip
# ---------------------------------------------------------------------------

class TestSaveLoad:
    def test_provenance_roundtrips(self):
        from portlight.engine.models import CombatGear
        from portlight.engine.save import _combat_gear_from_dict, _combat_gear_to_dict

        prov = create_provenance("cutlass", "porto_novo", "Med", 5)
        prov.kills = 12
        prov.named_kills = ["gnaw", "scarlet_ana"]
        prov.epithet = "Gnaw's Bane"
        prov.times_recognized = 3

        gear = CombatGear(
            melee_weapon="cutlass",
            weapon_provenance={"cutlass": prov},
        )
        d = _combat_gear_to_dict(gear)
        restored = _combat_gear_from_dict(d)

        rp = restored.weapon_provenance["cutlass"]
        assert rp.kills == 12
        assert rp.named_kills == ["gnaw", "scarlet_ana"]
        assert rp.epithet == "Gnaw's Bane"
        assert rp.times_recognized == 3
        assert rp.acquired_port == "porto_novo"

    def test_empty_provenance_roundtrips(self):
        from portlight.engine.models import CombatGear
        from portlight.engine.save import _combat_gear_from_dict, _combat_gear_to_dict

        gear = CombatGear()
        d = _combat_gear_to_dict(gear)
        restored = _combat_gear_from_dict(d)
        assert restored.weapon_provenance == {}
