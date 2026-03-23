"""Tests for faction relationships, spillover, and vendettas."""

from portlight.content.factions import (
    FACTION_RELATIONSHIPS,
    FACTIONS,
    get_allies,
    get_enemies,
    get_relationship,
    get_rivals,
)
from portlight.engine.narrative import _BEATS_BY_ID
from portlight.engine.underworld import (
    apply_standing_spillover,
    check_vendetta,
    get_political_summary,
    record_contraband_trade,
)


class TestFactionRelationships:
    """All 6 faction pairs must have defined relationships."""

    def test_six_relationships_defined(self):
        assert len(FACTION_RELATIONSHIPS) == 6

    def test_all_pairs_covered(self):
        fids = sorted(FACTIONS.keys())
        for i, a in enumerate(fids):
            for b in fids[i + 1:]:
                rel = get_relationship(a, b)
                assert rel is not None, f"Missing relationship: {a} ↔ {b}"

    def test_relationships_have_description(self):
        for rel in FACTION_RELATIONSHIPS:
            assert rel.description, f"{rel.faction_a}↔{rel.faction_b} missing description"
            assert rel.vendetta_trigger, f"{rel.faction_a}↔{rel.faction_b} missing vendetta_trigger"

    def test_dispositions_valid(self):
        valid = {"allied", "neutral", "rival", "hostile"}
        for rel in FACTION_RELATIONSHIPS:
            assert rel.disposition in valid, f"{rel.faction_a}↔{rel.faction_b}: invalid '{rel.disposition}'"

    def test_spillover_range(self):
        for rel in FACTION_RELATIONSHIPS:
            assert -1.0 <= rel.spillover <= 0.5, (
                f"{rel.faction_a}↔{rel.faction_b}: spillover {rel.spillover} outside range"
            )

    def test_hostile_has_negative_spillover(self):
        for rel in FACTION_RELATIONSHIPS:
            if rel.disposition == "hostile":
                assert rel.spillover < 0, (
                    f"Hostile relationship {rel.faction_a}↔{rel.faction_b} should have negative spillover"
                )


class TestFactionQueryHelpers:
    """get_allies, get_enemies, get_rivals."""

    def test_crimson_tide_enemies(self):
        enemies = get_enemies("crimson_tide")
        assert "deep_reef" in enemies

    def test_monsoon_syndicate_enemies(self):
        enemies = get_enemies("monsoon_syndicate")
        assert "iron_wolves" in enemies

    def test_deep_reef_enemies(self):
        enemies = get_enemies("deep_reef")
        assert "crimson_tide" in enemies
        assert "iron_wolves" in enemies

    def test_crimson_tide_rivals(self):
        rivals = get_rivals("crimson_tide")
        assert "monsoon_syndicate" in rivals
        assert "iron_wolves" in rivals

    def test_no_self_enemies(self):
        for fid in FACTIONS:
            assert fid not in get_enemies(fid)
            assert fid not in get_rivals(fid)
            assert fid not in get_allies(fid)

    def test_relationship_symmetry(self):
        """If A is enemy of B, B is enemy of A."""
        for fid in FACTIONS:
            for enemy_id in get_enemies(fid):
                assert fid in get_enemies(enemy_id), (
                    f"{fid} is enemy of {enemy_id} but not vice versa"
                )


class TestStandingSpillover:
    """Gaining standing with one faction affects others."""

    def test_helping_crimson_tide_hurts_deep_reef(self):
        standing = {"crimson_tide": 20}
        spillovers = apply_standing_spillover(standing, "crimson_tide", 5)
        # Deep Reef is hostile to Crimson Tide (spillover -0.4)
        assert "deep_reef" in spillovers
        assert spillovers["deep_reef"] < 0

    def test_helping_monsoon_syndicate_hurts_iron_wolves(self):
        standing = {"monsoon_syndicate": 20}
        spillovers = apply_standing_spillover(standing, "monsoon_syndicate", 5)
        assert "iron_wolves" in spillovers
        assert spillovers["iron_wolves"] < 0

    def test_neutral_relationship_no_spillover(self):
        standing = {"monsoon_syndicate": 20}
        spillovers = apply_standing_spillover(standing, "monsoon_syndicate", 3)
        # Deep Reef is neutral to Syndicate (spillover 0.0)
        assert spillovers.get("deep_reef", 0) == 0

    def test_spillover_capped_at_0_and_100(self):
        standing = {"crimson_tide": 2, "deep_reef": 98}
        apply_standing_spillover(standing, "crimson_tide", 10)
        assert standing.get("deep_reef", 0) >= 0
        assert standing.get("deep_reef", 0) <= 100

    def test_small_delta_still_produces_spillover_for_hostile(self):
        standing = {"crimson_tide": 20, "deep_reef": 20}
        spillovers = apply_standing_spillover(standing, "crimson_tide", 3)
        # -0.4 * 3 = -1.2, rounds to -1
        assert spillovers.get("deep_reef", 0) != 0 or abs(-0.4 * 3) < 1


class TestVendettas:
    """Vendetta detection."""

    def test_no_vendetta_at_low_standing(self):
        standing = {"crimson_tide": 5}
        vendettas = check_vendetta(standing, "crimson_tide")
        assert len(vendettas) == 0

    def test_vendetta_triggers_at_trade_standing(self):
        standing = {"crimson_tide": 30, "deep_reef": 0}
        vendettas = check_vendetta(standing, "crimson_tide")
        # Deep Reef is hostile to Crimson Tide and player has 0 standing with them
        assert "deep_reef" in vendettas

    def test_no_vendetta_if_enemy_standing_neutral(self):
        standing = {"crimson_tide": 30, "deep_reef": 15}
        vendettas = check_vendetta(standing, "crimson_tide")
        # Deep Reef standing is above prey threshold
        assert "deep_reef" not in vendettas


class TestPoliticalSummary:
    """Human-readable political status."""

    def test_empty_standing_no_output(self):
        summary = get_political_summary({})
        assert len(summary) == 0

    def test_trusted_faction_shows(self):
        standing = {"crimson_tide": 55}
        summary = get_political_summary(standing)
        assert any("trusted" in s.lower() for s in summary)

    def test_vendetta_shows(self):
        standing = {"crimson_tide": 30, "deep_reef": 0}
        summary = get_political_summary(standing)
        assert any("VENDETTA" in s for s in summary)


class TestSpilloverIntegration:
    """Spillover integrates with contraband trade."""

    def test_contraband_trade_triggers_spillover(self):
        standing = {}
        # Trade with Crimson Tide
        delta = record_contraband_trade(standing, "crimson_tide", "black_powder", 5)
        assert delta > 0
        # Now apply spillover manually (caller's responsibility)
        spillovers = apply_standing_spillover(standing, "crimson_tide", delta)
        # Deep Reef should be affected
        assert len(spillovers) > 0


class TestFactionPoliticsNarrative:
    """Political narrative beats exist."""

    POLITICAL_BEAT_IDS = [
        "faction_spillover", "vendetta_declared",
        "political_survivor", "faction_diplomat",
    ]

    def test_all_political_beats_defined(self):
        for beat_id in self.POLITICAL_BEAT_IDS:
            assert beat_id in _BEATS_BY_ID, f"Missing political beat: {beat_id}"

    def test_political_beats_have_text(self):
        for beat_id in self.POLITICAL_BEAT_IDS:
            beat = _BEATS_BY_ID[beat_id]
            assert beat.title, f"{beat_id} missing title"
            assert beat.text, f"{beat_id} missing text"
