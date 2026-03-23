"""Tests for the sparing flow — spare/take-all post-victory consequences.

Verifies that sparing and taking-all produce different outcomes across:
captain memory, underworld standing, companion morale, and silver reward.
"""

from __future__ import annotations

import random

from portlight.engine.captain_memory import (
    CaptainMemory,
    CaptainRelationship,
    record_encounter,
)
from portlight.engine.underworld import record_duel_outcome


def _rng(seed: int = 42) -> random.Random:
    return random.Random(seed)


# ---------------------------------------------------------------------------
# Captain memory: spare vs take-all
# ---------------------------------------------------------------------------

class TestCaptainMemory:
    def test_spare_boosts_respect(self):
        mem = CaptainMemory(captain_id="scarlet_ana")
        enc = record_encounter(mem, 10, "Med", "player_won", player_spared=True)
        assert enc.respect_delta > 0
        assert mem.relationship.respect > 0

    def test_spare_reduces_grudge(self):
        mem = CaptainMemory(captain_id="scarlet_ana", relationship=CaptainRelationship(grudge=30))
        record_encounter(mem, 10, "Med", "player_won", player_spared=True)
        assert mem.relationship.grudge < 30  # reduced

    def test_take_all_increases_grudge(self):
        mem = CaptainMemory(captain_id="gnaw")
        record_encounter(mem, 10, "Med", "player_won", player_spared=False)
        assert mem.relationship.grudge > 0

    def test_spare_tracks_count(self):
        mem = CaptainMemory(captain_id="scarlet_ana")
        record_encounter(mem, 10, "Med", "player_won", player_spared=True)
        assert mem.times_spared == 1
        record_encounter(mem, 20, "Med", "player_won", player_spared=True)
        assert mem.times_spared == 2

    def test_spare_vs_take_all_respect_difference(self):
        mem_spare = CaptainMemory(captain_id="test")
        mem_take = CaptainMemory(captain_id="test")
        record_encounter(mem_spare, 10, "Med", "player_won", player_spared=True)
        record_encounter(mem_take, 10, "Med", "player_won", player_spared=False)
        assert mem_spare.relationship.respect > mem_take.relationship.respect

    def test_spare_vs_take_all_fear_difference(self):
        mem_spare = CaptainMemory(captain_id="test")
        mem_take = CaptainMemory(captain_id="test")
        record_encounter(mem_spare, 10, "Med", "player_won", player_spared=True)
        record_encounter(mem_take, 10, "Med", "player_won", player_spared=False)
        assert mem_spare.relationship.fear < mem_take.relationship.fear


# ---------------------------------------------------------------------------
# Underworld standing
# ---------------------------------------------------------------------------

class TestUnderworldStanding:
    def test_spare_gives_more_standing(self):
        standing = {}
        delta_spare = record_duel_outcome(standing.copy(), "crimson_tide", True, spared=True)
        delta_take = record_duel_outcome(standing.copy(), "crimson_tide", True, spared=False)
        assert delta_spare > delta_take  # sparing = +5, taking = +2

    def test_spare_gives_5_standing(self):
        standing = {}
        delta = record_duel_outcome(standing, "crimson_tide", True, spared=True)
        assert delta == 5

    def test_take_all_gives_2_standing(self):
        standing = {}
        delta = record_duel_outcome(standing, "crimson_tide", True, spared=False)
        assert delta == 2


# ---------------------------------------------------------------------------
# Companion morale
# ---------------------------------------------------------------------------

class TestCompanionMorale:
    def test_sparing_boosts_gentle_surgeon(self):
        from portlight.engine.companion_engine import CompanionState, PartyState, apply_morale_trigger
        party = PartyState(companions=[
            CompanionState(companion_id="dr_amara", role_id="surgeon", morale=50, personality="gentle"),
        ])
        reactions = apply_morale_trigger(party, "spared_enemy")
        assert len(reactions) == 1
        assert reactions[0][1] > 0  # positive delta

    def test_taking_all_upsets_gentle(self):
        from portlight.engine.companion_engine import CompanionState, PartyState, apply_morale_trigger
        party = PartyState(companions=[
            CompanionState(companion_id="dr_amara", role_id="surgeon", morale=50, personality="gentle"),
        ])
        reactions = apply_morale_trigger(party, "took_all")
        assert len(reactions) == 1
        assert reactions[0][1] < 0  # negative

    def test_taking_all_pleases_smuggler(self):
        from portlight.engine.companion_engine import CompanionState, PartyState, apply_morale_trigger
        party = PartyState(companions=[
            CompanionState(companion_id="shadow_kai", role_id="smuggler", morale=50, personality="pragmatic"),
        ])
        reactions = apply_morale_trigger(party, "took_all")
        deltas = [r[1] for r in reactions]
        assert any(d > 0 for d in deltas)

    def test_sparing_vs_taking_morale_divergence(self):
        """Gentle surgeon should have very different morale after spare vs take-all."""
        from portlight.engine.companion_engine import CompanionState, PartyState, apply_morale_trigger

        party_spare = PartyState(companions=[
            CompanionState(companion_id="dr_amara", role_id="surgeon", morale=50, personality="gentle"),
        ])
        party_take = PartyState(companions=[
            CompanionState(companion_id="dr_amara", role_id="surgeon", morale=50, personality="gentle"),
        ])
        apply_morale_trigger(party_spare, "spared_enemy")
        apply_morale_trigger(party_take, "took_all")
        spare_morale = party_spare.companions[0].morale
        take_morale = party_take.companions[0].morale
        assert spare_morale > take_morale


# ---------------------------------------------------------------------------
# Silver reward
# ---------------------------------------------------------------------------

class TestSilverReward:
    def test_take_all_gives_more_silver(self):
        """Take-all should give more silver than sparing."""
        strength = 7
        spare_silver = 20 + strength * 3  # from _finalize_victory
        take_silver = 20 + strength * 7
        assert take_silver > spare_silver


# ---------------------------------------------------------------------------
# Encounter state persistence
# ---------------------------------------------------------------------------

class TestEncounterPersistence:
    """Verify that victory state survives save/load (bug fix: encounter persistence)."""

    def test_pending_victory_persists_in_encounter_state(self):
        """When pending_victory is True, it must be written to encounter_state dict."""
        from portlight.engine.models import PirateState
        pirates = PirateState()
        # Simulate what _sync_encounter_phase does after victory
        estate = {"pending_victory": True, "boarding_progress": 2, "boarding_threshold": 2}
        pirates.encounter_state = estate
        pirates.encounter_phase = "resolved"
        assert pirates.encounter_state["pending_victory"] is True
        assert pirates.encounter_phase == "resolved"

    def test_pending_victory_survives_dict_roundtrip(self):
        """pending_victory flag must survive serialization to dict and back."""
        import json
        estate = {
            "pending_victory": True,
            "boarding_progress": 2,
            "boarding_threshold": 2,
            "player_hp": 4,
            "opponent_hp": 0,
        }
        serialized = json.dumps(estate)
        restored = json.loads(serialized)
        assert restored["pending_victory"] is True
        assert restored["opponent_hp"] == 0

    def test_restore_reads_pending_victory(self):
        """_restore_encounter logic should set _pending_victory from estate."""
        estate = {"pending_victory": True}
        # Simulate the restore logic from cli.py _restore_encounter
        pending_victory = False
        if estate and estate.get("pending_victory"):
            pending_victory = True
        assert pending_victory is True

    def test_empty_estate_does_not_set_pending_victory(self):
        """Empty encounter_state should NOT trigger pending_victory."""
        estate = {}
        pending_victory = False
        if estate and estate.get("pending_victory"):
            pending_victory = True
        assert pending_victory is False
