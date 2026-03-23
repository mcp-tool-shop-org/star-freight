"""Tests for captain memory — NPC agency for pirate captains.

Covers: relationship model, breakpoint derivation, encounter recording,
goal generation, autonomous actions, tick staggering, save/load roundtrip.
"""

from __future__ import annotations

import random


from portlight.engine.captain_memory import (
    BREAKPOINTS,
    CaptainGoal,
    CaptainMemory,
    CaptainRelationship,
    EncounterMemory,
    derive_breakpoint,
    derive_goals,
    get_or_create_memory,
    get_relationship_summary,
    record_encounter,
    resolve_action,
    tick_captain_agency,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mem(captain_id: str = "scarlet_ana", **rel_overrides) -> CaptainMemory:
    rel = CaptainRelationship(**rel_overrides)
    return CaptainMemory(captain_id=captain_id, relationship=rel)


def _rng(seed: int = 42) -> random.Random:
    return random.Random(seed)


# ---------------------------------------------------------------------------
# Breakpoint derivation
# ---------------------------------------------------------------------------

class TestBreakpoints:
    def test_ally(self):
        assert derive_breakpoint(CaptainRelationship(respect=60, grudge=10)) == "ally"

    def test_ally_blocked_by_grudge(self):
        assert derive_breakpoint(CaptainRelationship(respect=60, grudge=25)) != "ally"

    def test_nemesis_high_grudge(self):
        assert derive_breakpoint(CaptainRelationship(grudge=50)) == "nemesis"

    def test_nemesis_moderate_grudge_low_fear(self):
        assert derive_breakpoint(CaptainRelationship(grudge=35, fear=10)) == "nemesis"

    def test_prey(self):
        assert derive_breakpoint(CaptainRelationship(fear=60, grudge=20)) == "prey"

    def test_prey_blocked_by_grudge(self):
        assert derive_breakpoint(CaptainRelationship(fear=60, grudge=45)) != "prey"

    def test_rival(self):
        assert derive_breakpoint(CaptainRelationship(respect=35, familiarity=45)) == "rival"

    def test_neutral_default(self):
        assert derive_breakpoint(CaptainRelationship()) == "neutral"

    def test_all_breakpoints_reachable(self):
        """Every defined breakpoint can be derived."""
        reached = set()
        configs = [
            CaptainRelationship(respect=60, grudge=10),    # ally
            CaptainRelationship(respect=35, familiarity=50), # rival
            CaptainRelationship(fear=60, grudge=20),         # prey
            CaptainRelationship(grudge=55),                  # nemesis
            CaptainRelationship(),                           # neutral
        ]
        for rel in configs:
            reached.add(derive_breakpoint(rel))
        assert reached == set(BREAKPOINTS)


# ---------------------------------------------------------------------------
# Encounter recording
# ---------------------------------------------------------------------------

class TestRecordEncounter:
    def test_basic_win(self):
        mem = _mem()
        enc = record_encounter(mem, day=10, region="Mediterranean", outcome="player_won")
        assert enc.respect_delta == 15
        assert enc.fear_delta == 10
        assert mem.relationship.respect == 15
        assert mem.times_defeated_by_player == 1
        assert len(mem.encounters) == 1

    def test_spare_boosts_respect_reduces_grudge(self):
        mem = _mem(grudge=20)
        enc = record_encounter(mem, day=10, region="Med", outcome="player_won", player_spared=True)
        assert enc.respect_delta == 25
        assert enc.grudge_delta == -10
        assert mem.times_spared == 1
        assert mem.relationship.grudge == 10  # 20 + (-10) = 10

    def test_flee_reduces_respect(self):
        mem = _mem(respect=20)
        record_encounter(mem, day=10, region="Med", outcome="fled")
        assert mem.relationship.respect == 10  # 20 + (-10)

    def test_firearm_modifier(self):
        mem = _mem()
        enc = record_encounter(mem, day=10, region="Med", outcome="player_won", player_used_firearm=True)
        assert enc.respect_delta == 15 + (-5)  # base + firearm penalty
        assert enc.fear_delta == 10 + 10        # base + firearm fear

    def test_heavy_crew_kills(self):
        mem = _mem()
        enc = record_encounter(mem, day=10, region="Med", outcome="player_won", crew_killed=8)
        assert enc.grudge_delta == 5 + 20  # base + heavy crew kill modifier

    def test_ship_sunk_tracking(self):
        mem = _mem()
        record_encounter(mem, day=10, region="Med", outcome="ship_sunk")
        assert mem.player_sank_their_ship is True

    def test_relationship_clamped(self):
        mem = _mem(respect=95)
        record_encounter(mem, day=10, region="Med", outcome="player_won_spared", player_spared=True)
        assert mem.relationship.respect <= 100

    def test_multiple_encounters_accumulate(self):
        mem = _mem()
        record_encounter(mem, day=10, region="Med", outcome="player_won")
        record_encounter(mem, day=20, region="Med", outcome="player_won")
        assert len(mem.encounters) == 2
        assert mem.relationship.respect == 30  # 15 + 15
        assert mem.times_defeated_by_player == 2

    def test_familiarity_always_increases(self):
        mem = _mem()
        for outcome in ["player_won", "player_lost", "fled", "negotiated"]:
            fam_before = mem.relationship.familiarity
            record_encounter(mem, day=10, region="Med", outcome=outcome)
            assert mem.relationship.familiarity > fam_before


# ---------------------------------------------------------------------------
# Goal derivation
# ---------------------------------------------------------------------------

class TestGoalDerivation:
    def test_ally_warns(self):
        mem = _mem(respect=55, grudge=10)
        goals = derive_goals(mem, "Mediterranean", "Mediterranean", 500, 100)
        verbs = [g.verb for g in goals]
        assert "warn" in verbs

    def test_nemesis_ambushes(self):
        mem = _mem(grudge=60, fear=10)
        goals = derive_goals(mem, "Mediterranean", "Mediterranean", 500, 100)
        verbs = [g.verb for g in goals]
        assert "ambush" in verbs

    def test_rival_challenges(self):
        mem = _mem(respect=35, familiarity=50)
        goals = derive_goals(mem, "Mediterranean", "Mediterranean", 500, 100)
        verbs = [g.verb for g in goals]
        assert "challenge" in verbs

    def test_prey_retreats(self):
        mem = _mem(fear=60, grudge=15)
        goals = derive_goals(mem, "Mediterranean", "Mediterranean", 500, 100)
        verbs = [g.verb for g in goals]
        assert "retreat" in verbs

    def test_neutral_extorts_wealthy(self):
        mem = _mem()
        goals = derive_goals(mem, "Mediterranean", "Mediterranean", 500, 100)
        verbs = [g.verb for g in goals]
        assert "extort" in verbs

    def test_high_familiarity_generates_rumor(self):
        mem = _mem(familiarity=40)
        goals = derive_goals(mem, "Mediterranean", "North Atlantic", 100, 100)
        verbs = [g.verb for g in goals]
        assert "rumor" in verbs

    def test_max_two_goals(self):
        mem = _mem(respect=55, grudge=10, familiarity=50)
        goals = derive_goals(mem, "Mediterranean", "Mediterranean", 500, 100)
        assert len(goals) <= 2

    def test_no_goals_with_no_encounters(self):
        """Fresh memory with default relationship has limited goals."""
        mem = _mem(familiarity=0)
        goals = derive_goals(mem, "North Atlantic", "Mediterranean", 100, 100)
        # Neutral + different region + poor = minimal goals
        non_rumor = [g for g in goals if g.verb != "rumor"]
        assert len(non_rumor) == 0


# ---------------------------------------------------------------------------
# Action resolution
# ---------------------------------------------------------------------------

class TestActionResolution:
    def test_warn_produces_message(self):
        mem = _mem("scarlet_ana")
        goal = CaptainGoal("warn", 0.7, "test")
        action = resolve_action(goal, mem, "Scarlet Ana", "The Crimson Tide")
        assert action is not None
        assert action.verb == "warn"
        assert "Scarlet Ana" in action.message
        assert action.effect_type == "message"

    def test_gift_includes_silver(self):
        mem = _mem("scarlet_ana")
        mem.times_spared = 2
        goal = CaptainGoal("gift", 0.3, "test")
        action = resolve_action(goal, mem, "Scarlet Ana", "The Crimson Tide")
        assert action.effect_type == "silver"
        assert action.effect_value > 0

    def test_ambush_creates_encounter(self):
        mem = _mem("gnaw")
        goal = CaptainGoal("ambush", 0.85, "test")
        action = resolve_action(goal, mem, "Gnaw", "The Iron Wolves")
        assert action.effect_type == "encounter"

    def test_trade_offer_creates_contract(self):
        mem = _mem("scarlet_ana")
        goal = CaptainGoal("trade_offer", 0.5, "test")
        action = resolve_action(goal, mem, "Scarlet Ana", "The Crimson Tide")
        assert action.effect_type == "contract"


# ---------------------------------------------------------------------------
# Tick / agency
# ---------------------------------------------------------------------------

class TestTickAgency:
    def test_tick_with_no_memories_returns_empty(self):
        actions = tick_captain_agency({}, "Mediterranean", 500, 50, _rng())
        assert actions == []

    def test_tick_with_memories_sometimes_produces_actions(self):
        """Over many days, at least some actions should fire."""
        mem = _mem("scarlet_ana", respect=55, grudge=10, familiarity=30)
        mem.encounters.append(EncounterMemory(day=1, region="Med", outcome="player_won"))
        memories = {"scarlet_ana": mem}
        all_actions = []
        for day in range(1, 50):
            actions = tick_captain_agency(memories, "Mediterranean", 500, day, _rng(day))
            all_actions.extend(actions)
        assert len(all_actions) > 0

    def test_tick_max_one_per_day(self):
        # Create memories for multiple captains
        memories = {}
        for cid in ["scarlet_ana", "the_butcher", "gnaw", "raj_the_quiet"]:
            m = _mem(cid, respect=55, grudge=10, familiarity=50)
            m.encounters.append(EncounterMemory(day=1, region="Med", outcome="player_won"))
            memories[cid] = m
        for day in range(1, 100):
            actions = tick_captain_agency(memories, "Mediterranean", 500, day, _rng(day))
            assert len(actions) <= 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_get_or_create_new(self):
        memories: dict = {}
        mem = get_or_create_memory(memories, "gnaw")
        assert mem.captain_id == "gnaw"
        assert "gnaw" in memories

    def test_get_or_create_existing(self):
        memories = {"gnaw": _mem("gnaw", respect=50)}
        mem = get_or_create_memory(memories, "gnaw")
        assert mem.relationship.respect == 50

    def test_relationship_summary(self):
        mem = _mem("scarlet_ana", respect=55, fear=20, grudge=10, familiarity=40)
        summary = get_relationship_summary(mem)
        assert summary["breakpoint"] == "ally"
        assert summary["respect"] == 55


# ---------------------------------------------------------------------------
# Save/load roundtrip
# ---------------------------------------------------------------------------

class TestSaveLoad:
    def test_captain_memory_roundtrips(self):
        from portlight.engine.models import PirateState
        from portlight.engine.save import _pirate_state_from_dict, _pirate_state_to_dict

        mem = CaptainMemory(
            captain_id="gnaw",
            relationship=CaptainRelationship(respect=-20, fear=40, grudge=70, familiarity=30),
            encounters=[EncounterMemory(day=10, region="NA", outcome="player_won", crew_killed=6)],
            last_seen_day=10, last_seen_region="North Atlantic",
            times_spared=0, times_defeated_by_player=1,
            player_sank_their_ship=True,
        )
        state = PirateState(captain_memories={"gnaw": mem})
        d = _pirate_state_to_dict(state)
        restored = _pirate_state_from_dict(d)

        assert "gnaw" in restored.captain_memories
        rm = restored.captain_memories["gnaw"]
        assert rm.relationship.grudge == 70
        assert rm.player_sank_their_ship is True
        assert len(rm.encounters) == 1
        assert rm.encounters[0].crew_killed == 6

    def test_empty_memories_roundtrips(self):
        from portlight.engine.models import PirateState
        from portlight.engine.save import _pirate_state_from_dict, _pirate_state_to_dict

        state = PirateState()
        d = _pirate_state_to_dict(state)
        restored = _pirate_state_from_dict(d)
        assert restored.captain_memories == {}
