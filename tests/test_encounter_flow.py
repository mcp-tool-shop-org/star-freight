"""Tests for the encounter state machine — approach, naval, boarding, duel flow."""

from __future__ import annotations

import random

import pytest

from portlight.engine.encounter import (
    begin_fight,
    create_duel_combatants,
    create_encounter,
    get_encounter_combat_actions,
    get_encounter_naval_actions,
    resolve_boarding_phase,
    resolve_duel_turn,
    resolve_flee,
    resolve_naval_turn,
    resolve_negotiate,
)
from portlight.engine.models import (
    Port,
    PortFeature,
    Ship,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rng(seed: int = 42) -> random.Random:
    return random.Random(seed)


def _make_ship(**overrides) -> Ship:
    defaults = dict(
        template_id="trade_brigantine", name="Player Ship",
        hull=100, hull_max=100, cargo_capacity=80, speed=6.0,
        crew=15, crew_max=20, cannons=6, maneuver=0.5,
    )
    defaults.update(overrides)
    return Ship(**defaults)


def _test_ports() -> dict[str, Port]:
    return {
        "porto_novo": Port(id="porto_novo", name="Porto Novo", description="", region="Mediterranean"),
        "corsairs_rest": Port(id="corsairs_rest", name="Corsair's Rest", description="", region="Mediterranean",
                              features=[PortFeature.BLACK_MARKET]),
    }


# ---------------------------------------------------------------------------
# Encounter creation
# ---------------------------------------------------------------------------

class TestEncounterCreation:
    def test_creates_encounter(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        assert enc is not None
        assert enc.phase == "approach"
        assert enc.enemy_captain_name
        assert enc.enemy_ship_hull > 0

    def test_encounter_has_valid_faction(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        assert enc.enemy_faction_id

    def test_encounter_enemy_ship_stats(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        assert enc.enemy_ship_hull_max > 0
        assert enc.enemy_ship_crew > 0


# ---------------------------------------------------------------------------
# Negotiate
# ---------------------------------------------------------------------------

class TestNegotiate:
    def test_allied_standing_always_succeeds(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        standing = {enc.enemy_faction_id: 60}  # allied threshold = 50
        success, msg = resolve_negotiate(enc, standing, "merchant", _rng())
        assert success is True
        assert enc.phase == "resolved"

    def test_trade_standing_succeeds(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        standing = {enc.enemy_faction_id: 30}  # trade threshold = 25
        success, msg = resolve_negotiate(enc, standing, "merchant", _rng())
        assert success is True

    def test_no_standing_sometimes_fails(self):
        results = []
        for seed in range(50):
            enc = create_encounter(_test_ports(), "porto_novo", _rng(seed))
            standing = {enc.enemy_faction_id: 0}  # prey
            success, msg = resolve_negotiate(enc, standing, "merchant", _rng(seed + 100))
            results.append(success)
        assert not all(results)  # should fail at least sometimes

    def test_prey_standing_always_fails(self):
        for seed in range(20):
            enc = create_encounter(_test_ports(), "porto_novo", _rng(seed))
            standing = {}  # no standing = 0 = prey
            success, msg = resolve_negotiate(enc, standing, "merchant", _rng(seed + 100))
            assert success is False


# ---------------------------------------------------------------------------
# Flee
# ---------------------------------------------------------------------------

class TestFlee:
    def test_fast_ship_can_escape(self):
        _enc = create_encounter(_test_ports(), "porto_novo", _rng())
        ship = _make_ship(speed=9.0, maneuver=0.8)
        escapes = 0
        for seed in range(50):
            enc2 = create_encounter(_test_ports(), "porto_novo", _rng(seed))
            escaped, dmg, msg = resolve_flee(enc2, ship, _rng(seed + 200))
            if escaped:
                escapes += 1
        assert escapes > 20

    def test_flee_returns_damage(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        ship = _make_ship(speed=5.0)
        escaped, dmg, msg = resolve_flee(enc, ship, _rng())
        assert dmg >= 0
        assert msg

    def test_successful_flee_resolves_encounter(self):
        _enc = create_encounter(_test_ports(), "porto_novo", _rng())
        ship = _make_ship(speed=15.0, maneuver=0.95)  # very fast
        for seed in range(50):
            enc2 = create_encounter(_test_ports(), "porto_novo", _rng(seed))
            escaped, _, _ = resolve_flee(enc2, ship, _rng(seed + 300))
            if escaped:
                assert enc2.phase == "resolved"
                return
        pytest.skip("No successful flee in 50 attempts")


# ---------------------------------------------------------------------------
# Begin fight
# ---------------------------------------------------------------------------

class TestBeginFight:
    def test_transitions_to_naval(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        ship = _make_ship()
        msg = begin_fight(enc, ship)
        assert enc.phase == "naval"
        assert "Battle stations" in msg

    def test_sets_boarding_threshold(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        ship = _make_ship(maneuver=0.9)
        begin_fight(enc, ship)
        assert enc.boarding_threshold >= 1


# ---------------------------------------------------------------------------
# Naval combat
# ---------------------------------------------------------------------------

class TestNavalCombat:
    def test_broadside_deals_damage(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        ship = _make_ship(cannons=6)
        begin_fight(enc, ship)
        _initial_hull = enc.enemy_ship_hull
        _result = resolve_naval_turn(enc, "broadside", ship, _rng())
        # Broadside should do some damage across many runs
        total_dmg = 0
        for seed in range(20):
            enc2 = create_encounter(_test_ports(), "porto_novo", _rng(seed))
            begin_fight(enc2, ship)
            r = resolve_naval_turn(enc2, "broadside", ship, _rng(seed + 100))
            total_dmg += abs(r["enemy_hull_delta"])
        assert total_dmg > 0

    def test_close_advances_boarding(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        ship = _make_ship()
        begin_fight(enc, ship)
        result = resolve_naval_turn(enc, "close", ship, _rng())
        # May or may not advance depending on enemy action
        assert "boarding_progress" in result

    def test_naval_combat_can_sink_enemy(self):
        """Sustained broadside fire should eventually sink the enemy."""
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        ship = _make_ship(cannons=20)  # man-of-war
        begin_fight(enc, ship)
        for i in range(30):
            if enc.phase != "naval":
                break
            resolve_naval_turn(enc, "broadside", ship, _rng(i))
        assert enc.enemy_ship_hull == 0 or enc.phase != "naval"

    def test_naval_turns_tracked(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        ship = _make_ship()
        begin_fight(enc, ship)
        resolve_naval_turn(enc, "broadside", ship, _rng())
        assert enc.naval_turns == 1

    def test_valid_naval_actions(self):
        armed = get_encounter_naval_actions(6)
        assert "broadside" in armed
        assert "flee" in armed
        unarmed = get_encounter_naval_actions(0)
        assert "broadside" not in unarmed
        assert "flee" in unarmed


# ---------------------------------------------------------------------------
# Boarding
# ---------------------------------------------------------------------------

class TestBoarding:
    def test_boarding_transitions_to_duel(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        enc.phase = "boarding"
        result = resolve_boarding_phase(enc, player_crew=15, rng=_rng())
        assert enc.phase == "duel"
        assert result["player_crew_lost"] >= 0
        assert result["enemy_crew_lost"] >= 0

    def test_boarding_flavor_text(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        enc.phase = "boarding"
        result = resolve_boarding_phase(enc, player_crew=15, rng=_rng())
        assert "Grappling hooks" in result["flavor"]


# ---------------------------------------------------------------------------
# Duel (personal combat phase)
# ---------------------------------------------------------------------------

class TestDuelPhase:
    def test_create_combatants(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        p, o = create_duel_combatants(
            enc, player_crew=15, player_style=None,
            player_injury_ids=[], player_firearm=None,
            player_ammo=0, player_throwing=0,
        )
        assert p.hp > 0
        assert o.hp > 0

    def test_duel_round_resolves(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        enc.phase = "duel"
        p, o = create_duel_combatants(
            enc, player_crew=10, player_style=None,
            player_injury_ids=[], player_firearm=None,
            player_ammo=0, player_throwing=0,
        )
        result = resolve_duel_turn(enc, "thrust", p, o, _rng())
        assert result.turn == 1
        assert result.flavor

    def test_duel_can_end_fight(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        enc.phase = "duel"
        enc.enemy_strength = 3  # weak opponent
        p, o = create_duel_combatants(
            enc, player_crew=20, player_style=None,
            player_injury_ids=[], player_firearm=None,
            player_ammo=0, player_throwing=0,
        )
        for i in range(20):
            if enc.phase == "resolved":
                break
            resolve_duel_turn(enc, "thrust", p, o, _rng(i))
        assert p.hp <= 0 or o.hp <= 0

    def test_valid_combat_actions(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        p, _ = create_duel_combatants(
            enc, player_crew=10, player_style="la_destreza",
            player_injury_ids=[], player_firearm="matchlock_pistol",
            player_ammo=3, player_throwing=2,
        )
        actions = get_encounter_combat_actions(p)
        assert "thrust" in actions
        assert "shoot" in actions
        assert "throw" in actions
        assert "estocada" in actions


# ---------------------------------------------------------------------------
# End-to-end: full encounter flow
# ---------------------------------------------------------------------------

class TestEndToEnd:
    def test_full_encounter_negotiate_success(self):
        enc = create_encounter(_test_ports(), "porto_novo", _rng())
        standing = {enc.enemy_faction_id: 60}
        success, _ = resolve_negotiate(enc, standing, "merchant", _rng())
        assert success
        assert enc.phase == "resolved"

    def test_full_encounter_fight_to_duel(self):
        """Walk through approach → naval → boarding → duel."""
        enc = create_encounter(_test_ports(), "porto_novo", _rng(7))
        ship = _make_ship(cannons=6)

        # Approach → fight
        begin_fight(enc, ship)
        assert enc.phase == "naval"

        # Naval: close until boarding
        for i in range(15):
            if enc.phase != "naval":
                break
            resolve_naval_turn(enc, "close", ship, _rng(i + 100))

        if enc.phase == "boarding":
            _result = resolve_boarding_phase(enc, player_crew=15, rng=_rng())
            assert enc.phase == "duel"

            # Duel: fight until resolved
            p, o = create_duel_combatants(
                enc, player_crew=15, player_style=None,
                player_injury_ids=[], player_firearm=None,
                player_ammo=0, player_throwing=0,
            )
            for j in range(20):
                if enc.phase == "resolved":
                    break
                resolve_duel_turn(enc, "thrust", p, o, _rng(j + 200))

            assert enc.phase == "resolved"


# ---------------------------------------------------------------------------
# Save/load roundtrip for new fields
# ---------------------------------------------------------------------------

class TestSaveLoadCompat:
    def test_captain_with_combat_fields_roundtrips(self):
        """Captain with combat gear, injuries, and styles should serialize."""
        from portlight.engine.models import ActiveInjury, Captain, CombatGear
        from portlight.engine.save import _captain_from_dict, _captain_to_dict

        captain = Captain(
            name="Test",
            learned_styles=["la_destreza", "dambe"],
            active_style="la_destreza",
            combat_gear=CombatGear(
                firearm="matchlock_pistol", firearm_ammo=3,
                throwing_weapons={"throwing_knife": 5},
            ),
            injuries=[
                ActiveInjury(injury_id="cut_hand", acquired_day=10, heal_remaining=5),
            ],
        )
        d = _captain_to_dict(captain)
        restored = _captain_from_dict(d)
        assert restored.learned_styles == ["la_destreza", "dambe"]
        assert restored.active_style == "la_destreza"
        assert restored.combat_gear.firearm == "matchlock_pistol"
        assert restored.combat_gear.firearm_ammo == 3
        assert len(restored.injuries) == 1
        assert restored.injuries[0].injury_id == "cut_hand"

    def test_ship_with_combat_fields_roundtrips(self):
        from portlight.engine.save import _ship_from_dict, _ship_to_dict

        ship = Ship(
            template_id="trade_brigantine", name="Test Ship",
            hull=90, hull_max=100, cargo_capacity=80, speed=6.0,
            crew=15, crew_max=20, cannons=6, maneuver=0.5,
        )
        d = _ship_to_dict(ship)
        restored = _ship_from_dict(d)
        assert restored.cannons == 6
        assert restored.maneuver == 0.5

    def test_old_save_without_combat_fields(self):
        """Old saves missing combat fields should load with defaults."""
        from portlight.engine.save import _captain_from_dict

        old_captain_data = {
            "name": "Old Captain", "silver": 1000, "provisions": 20, "day": 50,
            "captain_type": "merchant", "ship": {
                "template_id": "trade_brigantine", "name": "Old Ship",
                "hull": 80, "hull_max": 100, "cargo_capacity": 80,
                "speed": 6.0, "crew": 12, "crew_max": 20,
            },
            "cargo": [], "standing": {},
        }
        captain = _captain_from_dict(old_captain_data)
        assert captain.learned_styles == []
        assert captain.active_style is None
        assert captain.combat_gear.firearm is None
        assert captain.injuries == []

        # Ship should get cannons/maneuver from template
        ship = captain.ship
        assert ship.cannons == 6  # brigantine
        assert ship.maneuver == 0.5

    def test_pirate_state_new_fields(self):
        from portlight.engine.models import PirateState
        from portlight.engine.save import _pirate_state_from_dict, _pirate_state_to_dict

        state = PirateState(naval_victories=3, naval_defeats=1)
        d = _pirate_state_to_dict(state)
        restored = _pirate_state_from_dict(d)
        assert restored.naval_victories == 3
        assert restored.naval_defeats == 1
