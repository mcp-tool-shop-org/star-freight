"""Tests for the naval combat engine.

Covers: round resolution per action combination, enemy AI behavior,
flee mechanics, boarding threshold, crew casualties, hull damage,
zero-cannon ship restrictions, and enemy ship generation.
"""

from __future__ import annotations

import random

import pytest

from portlight.engine.models import EnemyShip, Ship
from portlight.engine.naval import (
    BOARDING_BASE_THRESHOLD,
    NAVAL_ACTIONS,
    attempt_flee,
    calc_boarding_threshold,
    generate_enemy_ship,
    get_valid_actions,
    pick_enemy_naval_action,
    resolve_boarding,
    resolve_naval_round,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_player_ship(**overrides) -> Ship:
    defaults = dict(
        template_id="trade_brigantine",
        name="Player Ship",
        hull=100,
        hull_max=100,
        cargo_capacity=80,
        speed=6.0,
        crew=15,
        crew_max=20,
        cannons=6,
        maneuver=0.5,
    )
    defaults.update(overrides)
    return Ship(**defaults)


def _make_enemy_ship(**overrides) -> EnemyShip:
    defaults = dict(
        name="Pirate Ship",
        hull=80,
        hull_max=80,
        cannons=4,
        maneuver=0.6,
        speed=6.5,
        crew=12,
        crew_max=15,
    )
    defaults.update(overrides)
    return EnemyShip(**defaults)


RNG = random.Random(42)


# ---------------------------------------------------------------------------
# Action validation
# ---------------------------------------------------------------------------

class TestActionValidation:
    def test_armed_ship_has_all_actions(self):
        actions = get_valid_actions(6)
        for a in NAVAL_ACTIONS:
            assert a in actions
        assert "flee" in actions

    def test_unarmed_ship_only_close_evade_flee(self):
        actions = get_valid_actions(0)
        assert "close" in actions
        assert "evade" in actions
        assert "flee" in actions
        assert "broadside" not in actions
        assert "rake" not in actions

    def test_negative_cannons_treated_as_unarmed(self):
        actions = get_valid_actions(-1)
        assert "flee" in actions
        assert "broadside" not in actions

    def test_flee_always_available(self):
        """Flee must be available regardless of armament — prevents soft-lock."""
        for cannons in [0, 1, 6, 12]:
            assert "flee" in get_valid_actions(cannons)


# ---------------------------------------------------------------------------
# Enemy ship generation
# ---------------------------------------------------------------------------

class TestEnemyShipGeneration:
    def test_low_strength_no_cannons(self):
        ship = generate_enemy_ship("Weakling", 1, random.Random(1))
        assert ship.cannons == 0
        assert ship.hull > 0
        assert ship.crew > 0

    def test_mid_strength_has_cannons(self):
        ship = generate_enemy_ship("Mid", 5, random.Random(1))
        assert ship.cannons > 0
        assert ship.hull > 0
        assert ship.crew > 0

    def test_high_strength_heavy_armament(self):
        ship = generate_enemy_ship("Gnaw", 9, random.Random(1))
        assert ship.cannons >= 12
        assert ship.hull >= 100
        assert ship.crew >= 30

    def test_strength_scales_hull(self):
        weak = generate_enemy_ship("W", 2, random.Random(1))
        strong = generate_enemy_ship("S", 8, random.Random(1))
        assert strong.hull > weak.hull

    def test_ship_name_includes_captain(self):
        ship = generate_enemy_ship("Scarlet Ana", 6, random.Random(1))
        assert "Scarlet Ana" in ship.name


# ---------------------------------------------------------------------------
# Boarding threshold
# ---------------------------------------------------------------------------

class TestBoardingThreshold:
    def test_base_threshold(self):
        # Maneuver 0.0 → no reduction
        assert calc_boarding_threshold(0.0, 0.5) == BOARDING_BASE_THRESHOLD

    def test_high_maneuver_reduces_threshold(self):
        # Maneuver 0.9 → floor(0.9*2)=1, threshold = 3-1 = 2
        assert calc_boarding_threshold(0.9, 0.5) == 2

    def test_threshold_minimum_is_one(self):
        # Even with maneuver 1.0, threshold can't go below 1
        assert calc_boarding_threshold(1.0, 0.5) >= 1

    def test_low_maneuver_keeps_high_threshold(self):
        assert calc_boarding_threshold(0.2, 0.5) == BOARDING_BASE_THRESHOLD


# ---------------------------------------------------------------------------
# Flee mechanics
# ---------------------------------------------------------------------------

class TestFlee:
    def test_fast_ship_escapes_reliably(self):
        player = _make_player_ship(speed=9.0, maneuver=0.8)
        enemy = _make_enemy_ship(speed=4.0, cannons=4)
        escapes = sum(1 for _ in range(100) if attempt_flee(player, enemy, random.Random(_))[0])
        assert escapes > 70  # should escape most of the time

    def test_slow_ship_rarely_escapes(self):
        player = _make_player_ship(speed=3.0, maneuver=0.2)
        enemy = _make_enemy_ship(speed=9.0, cannons=6)
        escapes = sum(1 for _ in range(100) if attempt_flee(player, enemy, random.Random(_))[0])
        assert escapes < 30

    def test_flee_always_returns_damage(self):
        player = _make_player_ship(speed=5.0)
        enemy = _make_enemy_ship(cannons=6)
        for seed in range(50):
            escaped, damage = attempt_flee(player, enemy, random.Random(seed))
            assert damage >= 0
            if not escaped:
                assert damage > 0  # failed flee always takes damage

    def test_flee_from_unarmed_enemy(self):
        player = _make_player_ship(speed=5.0)
        enemy = _make_enemy_ship(cannons=0)
        escaped, damage = attempt_flee(player, enemy, random.Random(1))
        if escaped:
            assert damage == 0  # no cannons = no grazing shot


# ---------------------------------------------------------------------------
# Round resolution — broadside
# ---------------------------------------------------------------------------

class TestBroadsideRounds:
    def test_broadside_vs_broadside_both_take_damage(self):
        player = _make_player_ship(cannons=6)
        enemy = _make_enemy_ship(cannons=4)
        rng = random.Random(42)
        result = resolve_naval_round("broadside", "broadside", player, enemy, 0, rng)
        assert result.player_hull_delta < 0
        assert result.enemy_hull_delta < 0

    def test_broadside_vs_evade_reduced_damage(self):
        player = _make_player_ship(cannons=6)
        enemy = _make_enemy_ship(cannons=4)
        # Normal broadside damage
        full_damages = []
        evade_damages = []
        for seed in range(50):
            rng = random.Random(seed)
            normal = resolve_naval_round("broadside", "broadside", player, enemy, 0, rng)
            rng = random.Random(seed)
            evaded = resolve_naval_round("broadside", "evade", player, enemy, 0, rng)
            full_damages.append(abs(normal.enemy_hull_delta))
            evade_damages.append(abs(evaded.enemy_hull_delta))
        # Evade should result in less average damage
        assert sum(evade_damages) < sum(full_damages)

    def test_zero_cannon_broadside_does_nothing(self):
        player = _make_player_ship(cannons=0)
        enemy = _make_enemy_ship(cannons=4)
        rng = random.Random(42)
        result = resolve_naval_round("broadside", "broadside", player, enemy, 0, rng)
        assert result.enemy_hull_delta == 0  # player has no cannons
        assert result.player_hull_delta < 0  # enemy still fires

    def test_broadside_vs_close_damages_closer(self):
        player = _make_player_ship(cannons=6)
        enemy = _make_enemy_ship(cannons=0)
        rng = random.Random(42)
        result = resolve_naval_round("broadside", "close", player, enemy, 0, rng)
        assert result.enemy_hull_delta < 0  # player fires on closing ship
        assert result.boarding_progress == 1  # enemy still closes


# ---------------------------------------------------------------------------
# Round resolution — close
# ---------------------------------------------------------------------------

class TestCloseRounds:
    def test_close_vs_close_advances_boarding_twice(self):
        player = _make_player_ship()
        enemy = _make_enemy_ship()
        rng = random.Random(42)
        result = resolve_naval_round("close", "close", player, enemy, 0, rng)
        assert result.boarding_progress == 2  # both close

    def test_close_vs_evade_no_boarding_progress(self):
        player = _make_player_ship()
        enemy = _make_enemy_ship()
        rng = random.Random(42)
        result = resolve_naval_round("close", "evade", player, enemy, 0, rng)
        assert result.boarding_progress == 0  # evade negates close

    def test_close_vs_broadside_takes_damage_but_advances(self):
        player = _make_player_ship()
        enemy = _make_enemy_ship(cannons=6)
        rng = random.Random(42)
        result = resolve_naval_round("close", "broadside", player, enemy, 0, rng)
        assert result.player_hull_delta < 0  # takes fire
        assert result.boarding_progress == 1  # but still closes


# ---------------------------------------------------------------------------
# Round resolution — rake
# ---------------------------------------------------------------------------

class TestRakeRounds:
    def test_rake_kills_crew(self):
        player = _make_player_ship(cannons=6)
        enemy = _make_enemy_ship()
        rng = random.Random(42)
        result = resolve_naval_round("rake", "close", player, enemy, 0, rng)
        assert result.enemy_crew_delta < 0  # crew casualties

    def test_rake_does_less_hull_damage_than_broadside(self):
        player = _make_player_ship(cannons=12)
        enemy = _make_enemy_ship()
        rake_hull = []
        broad_hull = []
        for seed in range(50):
            r1 = resolve_naval_round("rake", "close", player, enemy, 0, random.Random(seed))
            r2 = resolve_naval_round("broadside", "close", player, enemy, 0, random.Random(seed))
            rake_hull.append(abs(r1.enemy_hull_delta))
            broad_hull.append(abs(r2.enemy_hull_delta))
        assert sum(rake_hull) < sum(broad_hull)

    def test_rake_vs_evade_reduced_crew_kill(self):
        player = _make_player_ship(cannons=12)
        enemy = _make_enemy_ship()
        normal_kills = []
        evade_kills = []
        for seed in range(50):
            r1 = resolve_naval_round("rake", "close", player, enemy, 0, random.Random(seed))
            r2 = resolve_naval_round("rake", "evade", player, enemy, 0, random.Random(seed))
            normal_kills.append(abs(r1.enemy_crew_delta))
            evade_kills.append(abs(r2.enemy_crew_delta))
        assert sum(evade_kills) <= sum(normal_kills)


# ---------------------------------------------------------------------------
# Round resolution — evade
# ---------------------------------------------------------------------------

class TestEvadeRounds:
    def test_evade_vs_evade_nothing_happens(self):
        player = _make_player_ship()
        enemy = _make_enemy_ship()
        rng = random.Random(42)
        result = resolve_naval_round("evade", "evade", player, enemy, 0, rng)
        assert result.player_hull_delta == 0
        assert result.enemy_hull_delta == 0
        assert result.boarding_progress == 0

    def test_evade_halves_incoming_broadside(self):
        player = _make_player_ship()
        enemy = _make_enemy_ship(cannons=12)
        evade_dmg = []
        normal_dmg = []
        for seed in range(50):
            r1 = resolve_naval_round("evade", "broadside", player, enemy, 0, random.Random(seed))
            r2 = resolve_naval_round("close", "broadside", player, enemy, 0, random.Random(seed))
            evade_dmg.append(abs(r1.player_hull_delta))
            normal_dmg.append(abs(r2.player_hull_delta))
        assert sum(evade_dmg) < sum(normal_dmg)

    def test_evade_can_fully_dodge_weak_broadside(self):
        """Evade against a ship with few cannons can result in 0 hull damage."""
        player = _make_player_ship()
        enemy = _make_enemy_ship(cannons=1)  # very weak broadside
        zero_found = False
        for seed in range(200):
            r = resolve_naval_round("evade", "broadside", player, enemy, 0, random.Random(seed))
            if r.player_hull_delta == 0:
                zero_found = True
                break
        assert zero_found, "Evade should be able to fully avoid a 1-cannon broadside"


# ---------------------------------------------------------------------------
# Flavor text
# ---------------------------------------------------------------------------

class TestFlavor:
    def test_all_action_combos_have_flavor(self):
        player = _make_player_ship(cannons=6)
        enemy = _make_enemy_ship(cannons=4)
        for pa in NAVAL_ACTIONS:
            for ea in NAVAL_ACTIONS:
                rng = random.Random(42)
                result = resolve_naval_round(pa, ea, player, enemy, 0, rng)
                assert result.flavor  # non-empty


# ---------------------------------------------------------------------------
# Enemy AI
# ---------------------------------------------------------------------------

class TestEnemyAI:
    def test_aggressive_favors_broadside_and_close(self):
        player = _make_player_ship()
        enemy = _make_enemy_ship(cannons=4)
        actions = [pick_enemy_naval_action("aggressive", enemy, player, 0, 3, random.Random(s)) for s in range(100)]
        assert actions.count("broadside") + actions.count("close") > 50

    def test_defensive_favors_evade_and_rake(self):
        player = _make_player_ship()
        enemy = _make_enemy_ship(cannons=4)
        actions = [pick_enemy_naval_action("defensive", enemy, player, 0, 3, random.Random(s)) for s in range(100)]
        assert actions.count("evade") + actions.count("rake") > 50

    def test_unarmed_enemy_only_closes_or_evades(self):
        player = _make_player_ship()
        enemy = _make_enemy_ship(cannons=0)
        for seed in range(50):
            action = pick_enemy_naval_action("aggressive", enemy, player, 0, 3, random.Random(seed))
            assert action in ("close", "evade")

    def test_near_boarding_pushes_close(self):
        player = _make_player_ship()
        enemy = _make_enemy_ship(cannons=4)
        # Boarding progress = threshold - 1
        actions = [pick_enemy_naval_action("balanced", enemy, player, 2, 3, random.Random(s)) for s in range(100)]
        assert actions.count("close") > 30  # should push for boarding


# ---------------------------------------------------------------------------
# Boarding resolution
# ---------------------------------------------------------------------------

class TestBoarding:
    def test_overwhelming_advantage_low_losses(self):
        losses = [resolve_boarding(30, 5, random.Random(s)) for s in range(50)]
        avg_player_lost = sum(loss[0] for loss in losses) / 50
        assert avg_player_lost < 2

    def test_even_fight_significant_losses(self):
        losses = [resolve_boarding(15, 15, random.Random(s)) for s in range(50)]
        avg_player_lost = sum(loss[0] for loss in losses) / 50
        assert avg_player_lost > 1

    def test_disadvantaged_player_takes_more(self):
        even_losses = [resolve_boarding(10, 10, random.Random(s))[0] for s in range(50)]
        bad_losses = [resolve_boarding(5, 15, random.Random(s))[0] for s in range(50)]
        assert sum(bad_losses) > sum(even_losses)

    def test_advantage_flag_correct(self):
        _, _, advantage = resolve_boarding(30, 5, random.Random(1))
        assert advantage is True
        _, _, advantage = resolve_boarding(3, 30, random.Random(1))
        assert advantage is False


# ---------------------------------------------------------------------------
# Integration: multi-round naval combat
# ---------------------------------------------------------------------------

class TestMultiRoundCombat:
    def test_combat_resolves_within_reasonable_turns(self):
        """A naval fight between brigantine and pirate cutter should end."""
        player = _make_player_ship(hull=100, cannons=6, crew=15)
        enemy = _make_enemy_ship(hull=70, cannons=2, crew=8)
        rng = random.Random(42)

        p_hull, e_hull = player.hull, enemy.hull
        p_crew, e_crew = player.crew, enemy.crew
        boarding = 0
        threshold = calc_boarding_threshold(player.maneuver, enemy.maneuver)

        for turn in range(30):
            pa = "broadside" if player.cannons > 0 else "close"
            ea = pick_enemy_naval_action("aggressive", enemy, player, boarding, threshold, rng)
            result = resolve_naval_round(pa, ea, player, enemy, boarding, rng)

            p_hull += result.player_hull_delta
            e_hull += result.enemy_hull_delta
            p_crew += result.player_crew_delta
            e_crew += result.enemy_crew_delta
            boarding = result.boarding_progress

            if p_hull <= 0 or e_hull <= 0 or boarding >= threshold:
                break
        else:
            pytest.fail("Combat did not resolve in 30 turns")

    def test_sloop_vs_sloop_boards_quickly(self):
        """Two unarmed sloops should close and board fast."""
        player = _make_player_ship(cannons=0, maneuver=0.9)
        enemy = _make_enemy_ship(cannons=0, maneuver=0.85)
        rng = random.Random(42)

        boarding = 0
        threshold = calc_boarding_threshold(player.maneuver, enemy.maneuver)

        for turn in range(10):
            ea = pick_enemy_naval_action("aggressive", enemy, player, boarding, threshold, rng)
            result = resolve_naval_round("close", ea, player, enemy, boarding, rng)
            boarding = result.boarding_progress
            if boarding >= threshold:
                break

        assert boarding >= threshold, f"Boarding not reached in 10 turns (progress={boarding}, threshold={threshold})"
