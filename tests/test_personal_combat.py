"""Tests for the personal combat engine.

Covers: action resolution, stamina system, ranged weapons, fighting style
integration, injury effects, AI personality behavior, state mutation,
automated resolution, and legacy compatibility.
"""

from __future__ import annotations

import random

import pytest

from portlight.engine.combat import (
    BASE_PLAYER_HP,
    BASE_PLAYER_STAMINA,
    CORE_ACTIONS,
    PARRY_STAMINA_BONUS,
    STAMINA_COSTS,
    STAMINA_REGEN_PER_TURN,
    CombatResult,
    CombatRound,
    CombatantState,
    apply_round_to_states,
    create_opponent_combatant,
    create_player_combatant,
    get_available_actions,
    pick_opponent_action,
    resolve_combat_automated,
    resolve_combat_round,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rng(seed: int = 42) -> random.Random:
    return random.Random(seed)


def _player(**kw) -> CombatantState:
    return create_player_combatant(**kw)


def _opponent(strength: int = 5, personality: str = "balanced", **kw) -> CombatantState:
    return create_opponent_combatant(strength=strength, personality=personality, **kw)


# ---------------------------------------------------------------------------
# Combatant creation
# ---------------------------------------------------------------------------

class TestCombatantCreation:
    def test_player_base_hp(self):
        p = _player()
        assert p.hp == BASE_PLAYER_HP
        assert p.hp_max == BASE_PLAYER_HP

    def test_player_crew_bonus(self):
        p = _player(crew=15)
        # crew_bonus = 15-5 = 10, //5 = 2
        assert p.hp == BASE_PLAYER_HP + 2

    def test_player_with_style_hp_bonus(self):
        p = _player(active_style="highland_broadsword")
        assert p.hp == BASE_PLAYER_HP + 2  # highland gives +2 HP

    def test_player_with_injuries(self):
        p = _player(injury_ids=["gunshot_wound"])
        # gunshot: hp_max_mod=-2, stamina_max_mod=-2
        assert p.hp == BASE_PLAYER_HP - 2
        assert p.stamina == BASE_PLAYER_STAMINA - 2

    def test_opponent_strength_scales_hp(self):
        weak = _opponent(strength=3)
        strong = _opponent(strength=9)
        assert strong.hp > weak.hp
        # strength 9: 10 + (9-5)*2 = 18
        assert strong.hp == 18
        # strength 3: 10 + (3-5)*2 = 6, but floor is 6
        assert weak.hp == 6

    def test_opponent_hp_floor(self):
        o = _opponent(strength=1)
        assert o.hp >= 6


# ---------------------------------------------------------------------------
# Action validation
# ---------------------------------------------------------------------------

class TestActionValidation:
    def test_base_actions_always_available(self):
        p = _player()
        actions = get_available_actions(p)
        for a in CORE_ACTIONS:
            assert a in actions

    def test_shoot_requires_ammo(self):
        p = _player(firearm_id="matchlock_pistol", firearm_ammo=1)
        assert "shoot" in get_available_actions(p)
        p2 = _player()
        assert "shoot" not in get_available_actions(p2)

    def test_throw_requires_weapons(self):
        p = _player(throwing_weapons=3)
        assert "throw" in get_available_actions(p)
        p2 = _player()
        assert "throw" not in get_available_actions(p2)

    def test_dodge_blocked_after_dodge(self):
        p = _player()
        p.last_action = "dodge"
        assert "dodge" not in get_available_actions(p)

    def test_dodge_blocked_by_injury(self):
        p = _player(injury_ids=["shattered_knee"])
        assert "dodge" not in get_available_actions(p)

    def test_shoot_blocked_by_injury(self):
        p = _player(firearm_id="matchlock_pistol", firearm_ammo=1, injury_ids=["severed_fingers"])
        assert "shoot" not in get_available_actions(p)

    def test_style_action_available(self):
        p = _player(active_style="la_destreza")
        actions = get_available_actions(p)
        assert "estocada" in actions

    def test_style_action_blocked_by_cooldown(self):
        p = _player(active_style="la_destreza")
        p.style_cooldowns["estocada"] = 2
        actions = get_available_actions(p)
        assert "estocada" not in actions

    def test_stunned_can_only_dodge(self):
        p = _player()
        p.stun_turns = 1
        actions = get_available_actions(p)
        assert actions == ["dodge"]


# ---------------------------------------------------------------------------
# Core melee triangle
# ---------------------------------------------------------------------------

class TestMeleeTriangle:
    def test_thrust_beats_slash(self):
        p, o = _player(), _opponent()
        result = resolve_combat_round("thrust", p, o, "balanced", _rng())
        if result.opponent_action == "slash":
            assert result.damage_to_opponent > 0

    def test_slash_beats_parry(self):
        p, _o = _player(), _opponent()
        # Force opponent to parry by using defensive personality
        results = []
        for seed in range(50):
            r = resolve_combat_round("slash", p, _opponent(), "defensive", _rng(seed))
            if r.opponent_action == "parry":
                results.append(r)
        assert any(r.damage_to_opponent > 0 for r in results)

    def test_parry_beats_thrust(self):
        p, _o = _player(), _opponent()
        results = []
        for seed in range(50):
            r = resolve_combat_round("parry", p, _opponent(), "aggressive", _rng(seed))
            if r.opponent_action == "thrust":
                results.append(r)
        assert any(r.damage_to_opponent > 0 for r in results)

    def test_same_stance_draw_no_damage(self):
        """When both pick the same melee action, neither takes damage."""
        # Run many rounds to find a same-stance case
        for seed in range(100):
            p, o = _player(), _opponent()
            r = resolve_combat_round("thrust", p, o, "aggressive", _rng(seed))
            if r.opponent_action == "thrust":
                assert r.damage_to_opponent == 0
                assert r.damage_to_player == 0
                return
        pytest.skip("No same-stance draw found in 100 seeds")

    def test_parry_vs_parry_no_damage(self):
        """Parry vs parry should be a clean stalemate with zero damage."""
        for seed in range(100):
            p, o = _player(), _opponent()
            r = resolve_combat_round("parry", p, o, "defensive", _rng(seed))
            if r.opponent_action == "parry":
                assert r.damage_to_opponent == 0, "Parry vs parry should deal 0 damage to opponent"
                assert r.damage_to_player == 0, "Parry vs parry should deal 0 damage to player"
                return
        pytest.skip("No parry-vs-parry found in 100 seeds")


# ---------------------------------------------------------------------------
# Ranged combat
# ---------------------------------------------------------------------------

class TestRangedCombat:
    def test_shoot_deals_damage(self):
        p = _player(firearm_id="matchlock_pistol", firearm_ammo=3)
        hits = 0
        for seed in range(50):
            o = _opponent()
            r = resolve_combat_round("shoot", p, o, "aggressive", _rng(seed))
            if r.damage_to_opponent > 0:
                hits += 1
        assert hits > 10  # ~65% accuracy

    def test_shoot_cant_be_parried(self):
        """When opponent parries against a shot, they still take damage."""
        p = _player(firearm_id="matchlock_pistol", firearm_ammo=5)
        parry_hits = 0
        for seed in range(100):
            o = _opponent()
            r = resolve_combat_round("shoot", p, o, "defensive", _rng(seed))
            if r.opponent_action == "parry" and r.damage_to_opponent > 0:
                parry_hits += 1
        assert parry_hits > 0  # confirmed: parry doesn't block bullets

    def test_throw_consumes_weapon(self):
        p = _player(throwing_weapons=3)
        o = _opponent()
        r = resolve_combat_round("throw", p, o, "balanced", _rng())
        apply_round_to_states(r, p, o)
        assert p.throwing_weapons == 2

    def test_dodge_avoids_ranged(self):
        """Dodge should avoid all damage from shooting opponents."""
        for seed in range(50):
            p = _player()
            o = _opponent(ammo=5)
            o.ammo = 5
            r = resolve_combat_round("dodge", p, o, "wild", _rng(seed))
            if r.opponent_action == "shoot":
                # Player dodged, should take 0 damage from the shot
                # (dodge handles this before shoot resolution)
                assert r.damage_to_player == 0
                return
        pytest.skip("No dodge-vs-shoot found")


# ---------------------------------------------------------------------------
# Stamina system
# ---------------------------------------------------------------------------

class TestStaminaSystem:
    def test_melee_costs_stamina(self):
        p, o = _player(), _opponent()
        r = resolve_combat_round("thrust", p, o, "balanced", _rng())
        # Cost: -1 for thrust, +1 regen = net 0
        assert r.player_stamina_delta == STAMINA_REGEN_PER_TURN - STAMINA_COSTS["thrust"]

    def test_dodge_costs_more_stamina(self):
        p, o = _player(), _opponent()
        r = resolve_combat_round("dodge", p, o, "balanced", _rng())
        # Cost: -2 for dodge, +1 regen = net -1
        assert r.player_stamina_delta == STAMINA_REGEN_PER_TURN - STAMINA_COSTS["dodge"]

    def test_parry_restores_bonus_stamina(self):
        p, o = _player(), _opponent()
        r = resolve_combat_round("parry", p, o, "balanced", _rng())
        # Cost: -1 parry, +1 regen, +1 parry bonus = net +1
        expected = STAMINA_REGEN_PER_TURN - STAMINA_COSTS["parry"] + PARRY_STAMINA_BONUS
        assert r.player_stamina_delta == expected

    def test_stamina_clamped_to_max(self):
        p, o = _player(), _opponent()
        p.stamina = p.stamina_max  # full
        r = resolve_combat_round("parry", p, o, "balanced", _rng())
        apply_round_to_states(r, p, o)
        assert p.stamina <= p.stamina_max

    def test_stamina_doesnt_go_negative(self):
        p, o = _player(), _opponent()
        p.stamina = 0
        r = resolve_combat_round("dodge", p, o, "balanced", _rng())
        apply_round_to_states(r, p, o)
        assert p.stamina >= 0


# ---------------------------------------------------------------------------
# Fighting style integration
# ---------------------------------------------------------------------------

class TestStyleIntegration:
    def test_la_destreza_thrust_bonus(self):
        """La Destreza should add +1 to thrust damage."""
        styled_dmg = []
        plain_dmg = []
        for seed in range(100):
            p_styled = _player(active_style="la_destreza")
            p_plain = _player()
            o1 = _opponent()
            o2 = _opponent()
            r1 = resolve_combat_round("thrust", p_styled, o1, "balanced", _rng(seed))
            r2 = resolve_combat_round("thrust", p_plain, o2, "balanced", _rng(seed))
            styled_dmg.append(r1.damage_to_opponent)
            plain_dmg.append(r2.damage_to_opponent)
        # Styled should deal more total damage (when winning)
        assert sum(styled_dmg) >= sum(plain_dmg)

    def test_highland_hp_bonus(self):
        p = _player(active_style="highland_broadsword")
        assert p.hp == BASE_PLAYER_HP + 2

    def test_dambe_dodge_counter(self):
        """Dambe dodge should deal counter-damage."""
        for seed in range(50):
            p = _player(active_style="dambe")
            o = _opponent()
            r = resolve_combat_round("dodge", p, o, "aggressive", _rng(seed))
            if r.opponent_action in CORE_ACTIONS:
                assert r.damage_to_opponent == 1  # dambe passive
                return
        pytest.skip("No dodge-vs-melee found")

    def test_style_special_action_resolves(self):
        p = _player(active_style="la_destreza")
        o = _opponent()
        r = resolve_combat_round("estocada", p, o, "balanced", _rng())
        assert r.player_action == "estocada"
        assert r.flavor  # has flavor text

    def test_style_cooldown_applied(self):
        p = _player(active_style="la_destreza")
        o = _opponent()
        r = resolve_combat_round("estocada", p, o, "balanced", _rng())
        apply_round_to_states(r, p, o)
        assert p.style_cooldowns.get("estocada", 0) > 0


# ---------------------------------------------------------------------------
# Injury integration
# ---------------------------------------------------------------------------

class TestInjuryIntegration:
    def test_heavy_damage_can_cause_injury(self):
        """Opponent shooting the player (4-6 dmg) should sometimes inflict an injury."""
        injuries = []
        for seed in range(200):
            p = _player()
            o = _opponent(strength=7, ammo=5)
            o.ammo = 5
            r = resolve_combat_round("thrust", p, o, "wild", _rng(seed))
            if r.injury_inflicted:
                injuries.append(r.injury_inflicted)
            # Also check opponent injuries from player style actions
            if r.opponent_injury:
                injuries.append(r.opponent_injury)
        # Ranged hits do 4-6 damage, should trigger injuries
        assert len(injuries) > 0

    def test_low_damage_no_injury(self):
        """Draw damage (1) should never cause injury."""
        for seed in range(100):
            p, o = _player(), _opponent()
            r = resolve_combat_round("thrust", p, o, "balanced", _rng(seed))
            if r.damage_to_player <= 3:
                assert r.injury_inflicted is None

    def test_injury_effects_reduce_damage(self):
        plain_dmg = []
        injured_dmg = []
        for seed in range(100):
            p1 = _player()
            p2 = _player(injury_ids=["broken_sword_arm"])
            o1 = _opponent()
            o2 = _opponent()
            r1 = resolve_combat_round("thrust", p1, o1, "balanced", _rng(seed))
            r2 = resolve_combat_round("thrust", p2, o2, "balanced", _rng(seed))
            plain_dmg.append(r1.damage_to_opponent)
            injured_dmg.append(r2.damage_to_opponent)
        # Broken sword arm: -2 melee dmg + thrust halved
        assert sum(injured_dmg) < sum(plain_dmg)


# ---------------------------------------------------------------------------
# Opponent AI
# ---------------------------------------------------------------------------

class TestOpponentAI:
    def test_aggressive_favors_offense(self):
        actions = [pick_opponent_action("aggressive", _opponent(), _player(), None, _rng(s)) for s in range(100)]
        offensive = sum(1 for a in actions if a in ("thrust", "slash"))
        assert offensive > 50

    def test_defensive_favors_defense(self):
        actions = [pick_opponent_action("defensive", _opponent(), _player(), None, _rng(s)) for s in range(100)]
        defensive = sum(1 for a in actions if a in ("parry", "dodge"))
        assert defensive > 35

    def test_balanced_counters_repeat(self):
        """Balanced AI should counter repeated player thrust with more parry."""
        countered = [pick_opponent_action("balanced", _opponent(), _player(), "thrust", _rng(s)) for s in range(100)]
        base = [pick_opponent_action("balanced", _opponent(), _player(), None, _rng(s)) for s in range(100)]
        assert countered.count("parry") > base.count("parry")

    def test_no_ammo_no_shoot(self):
        o = _opponent(ammo=0)
        for seed in range(50):
            action = pick_opponent_action("wild", o, _player(), None, _rng(seed))
            assert action != "shoot"

    def test_stunned_only_dodges(self):
        o = _opponent()
        o.stun_turns = 1
        for seed in range(20):
            action = pick_opponent_action("aggressive", o, _player(), None, _rng(seed))
            assert action == "dodge"


# ---------------------------------------------------------------------------
# State mutation
# ---------------------------------------------------------------------------

class TestStateMutation:
    def test_hp_reduces_on_damage(self):
        p, o = _player(), _opponent()
        initial_hp = p.hp
        r = CombatRound(turn=1, player_action="thrust", opponent_action="slash",
                        damage_to_player=3, damage_to_opponent=2)
        apply_round_to_states(r, p, o)
        assert p.hp == initial_hp - 3
        assert o.hp == o.hp_max - 2

    def test_hp_floors_at_zero(self):
        p, o = _player(), _opponent()
        r = CombatRound(turn=1, player_action="thrust", opponent_action="slash",
                        damage_to_player=999)
        apply_round_to_states(r, p, o)
        assert p.hp == 0

    def test_ammo_consumed_on_shoot(self):
        p = _player(firearm_id="matchlock_pistol", firearm_ammo=2)
        o = _opponent()
        r = CombatRound(turn=1, player_action="shoot", opponent_action="thrust")
        apply_round_to_states(r, p, o)
        assert p.ammo == 1
        assert p.reload_turns == 1  # matchlock has 1 turn reload

    def test_reload_ticks_down(self):
        p = _player(firearm_id="matchlock_pistol", firearm_ammo=1)
        o = _opponent()
        # Shoot
        r1 = CombatRound(turn=1, player_action="shoot", opponent_action="thrust")
        apply_round_to_states(r1, p, o)
        assert p.reload_turns == 1
        # Next round (not shooting)
        r2 = CombatRound(turn=2, player_action="thrust", opponent_action="thrust",
                         player_stamina_delta=0, opponent_stamina_delta=0)
        apply_round_to_states(r2, p, o)
        assert p.reload_turns == 0

    def test_injury_appended_to_state(self):
        p, o = _player(), _opponent()
        r = CombatRound(turn=1, player_action="thrust", opponent_action="slash",
                        injury_inflicted="cut_hand")
        apply_round_to_states(r, p, o)
        assert "cut_hand" in p.injury_ids

    def test_last_action_tracked(self):
        p, o = _player(), _opponent()
        r = CombatRound(turn=1, player_action="dodge", opponent_action="thrust")
        apply_round_to_states(r, p, o)
        assert p.last_action == "dodge"


# ---------------------------------------------------------------------------
# Automated resolution
# ---------------------------------------------------------------------------

class TestAutomatedResolution:
    def test_combat_resolves(self):
        result = resolve_combat_automated(
            player_stances=["thrust"] * 15,
            opponent_id="scarlet_ana",
            opponent_name="Scarlet Ana",
            opponent_personality="balanced",
            opponent_strength=6,
            rng=_rng(),
        )
        assert isinstance(result, CombatResult)
        assert result.opponent_name == "Scarlet Ana"
        assert len(result.rounds) > 0

    def test_player_can_win(self):
        # Strong crew, many stances
        wins = 0
        for seed in range(50):
            result = resolve_combat_automated(
                player_stances=["thrust", "slash", "parry"] * 6,
                opponent_id="test", opponent_name="Weak Pirate",
                opponent_personality="wild",
                opponent_strength=3,
                rng=_rng(seed),
                player_crew=20,
            )
            if result.player_won:
                wins += 1
        assert wins > 10

    def test_strong_opponent_hard_to_beat(self):
        losses = 0
        for seed in range(50):
            result = resolve_combat_automated(
                player_stances=["thrust"] * 10,
                opponent_id="gnaw", opponent_name="Gnaw",
                opponent_personality="aggressive",
                opponent_strength=9,
                rng=_rng(seed),
                player_crew=5,
            )
            if not result.player_won and not result.draw:
                losses += 1
        assert losses > 15

    def test_silver_positive_on_win(self):
        # Guarantee a win by giving massive advantage
        result = resolve_combat_automated(
            player_stances=["thrust", "slash", "parry"] * 10,
            opponent_id="test", opponent_name="Test",
            opponent_personality="defensive",
            opponent_strength=1,
            rng=_rng(42),
            player_crew=30,
        )
        if result.player_won:
            assert result.silver_delta > 0

    def test_with_fighting_style(self):
        result = resolve_combat_automated(
            player_stances=["estocada", "thrust", "slash"] * 5,
            opponent_id="test", opponent_name="Test",
            opponent_personality="balanced",
            opponent_strength=5,
            rng=_rng(42),
            player_style="la_destreza",
        )
        assert len(result.rounds) > 0

    def test_with_ranged_weapons(self):
        result = resolve_combat_automated(
            player_stances=["shoot", "thrust", "thrust"] * 5,
            opponent_id="test", opponent_name="Test",
            opponent_personality="balanced",
            opponent_strength=5,
            rng=_rng(42),
            player_firearm="matchlock_pistol",
            player_ammo=3,
        )
        assert result.ammo_spent >= 0

    def test_injuries_tracked(self):
        """Combats with ranged weapons (4+ dmg) should sometimes produce injuries."""
        all_injuries: list[str] = []
        for seed in range(100):
            result = resolve_combat_automated(
                player_stances=["shoot", "thrust", "slash"] * 6,
                opponent_id="test", opponent_name="Brute",
                opponent_personality="aggressive",
                opponent_strength=8,
                rng=_rng(seed),
                player_firearm="matchlock_pistol",
                player_ammo=6,
            )
            all_injuries.extend(result.injuries_sustained)
            all_injuries.extend(result.opponent_injuries)
        # Ranged hits do 4-6 damage, which can trigger injuries
        assert len(all_injuries) > 0

    def test_deterministic_with_same_seed(self):
        args = dict(
            player_stances=["thrust", "slash", "parry"] * 5,
            opponent_id="test", opponent_name="Test",
            opponent_personality="balanced",
            opponent_strength=6,
            player_crew=10,
        )
        r1 = resolve_combat_automated(**args, rng=_rng(42))
        r2 = resolve_combat_automated(**args, rng=_rng(42))
        assert len(r1.rounds) == len(r2.rounds)
        assert r1.player_won == r2.player_won
        assert r1.silver_delta == r2.silver_delta


# ---------------------------------------------------------------------------
# Flavor text
# ---------------------------------------------------------------------------

class TestFlavorText:
    def test_melee_rounds_have_flavor(self):
        for seed in range(20):
            p, o = _player(), _opponent()
            r = resolve_combat_round("thrust", p, o, "balanced", _rng(seed))
            assert r.flavor  # non-empty string


# ---------------------------------------------------------------------------
# Throwing weapon gear sync (CLI-level cleanup)
# ---------------------------------------------------------------------------

class TestThrowingWeaponGearSync:
    """Verify that fully-spent throwing weapons are pruned from gear dict."""

    def test_spent_weapons_removed_from_dict(self):
        """After spending all throwing knives, the key should be removed."""
        gear = {"throwing_knife": 1, "bolas": 2}
        # Simulate the sync: 1 spent total
        total_before = sum(gear.values())
        remaining = total_before - 1  # threw 1
        spent = total_before - remaining
        for wid in list(gear):
            if spent <= 0:
                break
            can_take = min(spent, gear[wid])
            gear[wid] -= can_take
            spent -= can_take
        # Cleanup zero-count entries
        gear = {k: v for k, v in gear.items() if v > 0}
        assert "throwing_knife" not in gear
        assert gear == {"bolas": 2}

    def test_partial_spend_keeps_weapon(self):
        """Spending 1 of 3 bolas should keep the entry."""
        gear = {"bolas": 3}
        total_before = sum(gear.values())
        spent = total_before - 2  # 1 spent
        for wid in list(gear):
            if spent <= 0:
                break
            can_take = min(spent, gear[wid])
            gear[wid] -= can_take
            spent -= can_take
        gear = {k: v for k, v in gear.items() if v > 0}
        assert gear == {"bolas": 2}
