"""Tests for the injury system — triggers, healing, effects, and style blocking."""

from __future__ import annotations

import random


from portlight.content.injuries import (
    INJURIES,
    get_injured_body_parts,
    get_injury_pool,
)
from portlight.engine.injuries import (
    INJURY_DAMAGE_THRESHOLD,
    check_injury_blocks_style,
    create_injury,
    get_injury_effects,
    heal_injury_tick,
    roll_injury,
    treat_injury,
)
from portlight.engine.models import ActiveInjury


# ---------------------------------------------------------------------------
# Injury catalog
# ---------------------------------------------------------------------------

class TestInjuryCatalog:
    def test_all_injuries_have_required_fields(self):
        for inj in INJURIES.values():
            assert inj.id
            assert inj.name
            assert inj.severity in ("minor", "major", "crippling")
            assert inj.body_part in ("hand", "arm", "leg", "eye", "torso")
            assert len(inj.attack_types) > 0

    def test_eight_injuries_defined(self):
        assert len(INJURIES) == 8

    def test_severity_distribution(self):
        severities = [i.severity for i in INJURIES.values()]
        assert severities.count("minor") == 2
        assert severities.count("major") == 3
        assert severities.count("crippling") == 3

    def test_permanent_injuries_have_no_heal_days(self):
        permanent = [i for i in INJURIES.values() if i.heal_days is None]
        assert len(permanent) == 2  # blinded_eye, severed_fingers
        for inj in permanent:
            assert inj.severity == "crippling"


# ---------------------------------------------------------------------------
# Injury pool by attack type
# ---------------------------------------------------------------------------

class TestInjuryPool:
    def test_slash_pool_includes_cuts(self):
        pool = get_injury_pool("slash")
        ids = {i.id for i in pool}
        assert "cut_hand" in ids
        assert "deep_slash" in ids

    def test_thrust_pool_includes_ribs(self):
        pool = get_injury_pool("thrust")
        ids = {i.id for i in pool}
        assert "bruised_ribs" in ids

    def test_shoot_pool_includes_gunshot(self):
        pool = get_injury_pool("shoot")
        ids = {i.id for i in pool}
        assert "gunshot_wound" in ids

    def test_unknown_attack_type_empty_pool(self):
        assert get_injury_pool("magic") == []


# ---------------------------------------------------------------------------
# Roll injury
# ---------------------------------------------------------------------------

class TestRollInjury:
    def test_below_threshold_never_triggers(self):
        for seed in range(100):
            result = roll_injury(INJURY_DAMAGE_THRESHOLD - 1, "slash", random.Random(seed))
            assert result is None

    def test_high_damage_triggers_sometimes(self):
        results = [roll_injury(6, "slash", random.Random(s)) for s in range(100)]
        injuries = [r for r in results if r is not None]
        assert len(injuries) > 10  # should trigger often with 6 damage

    def test_injury_bonus_increases_chance(self):
        base_results = [roll_injury(4, "slash", random.Random(s)) for s in range(200)]
        bonus_results = [roll_injury(4, "slash", random.Random(s), injury_bonus=0.5) for s in range(200)]
        base_count = sum(1 for r in base_results if r is not None)
        bonus_count = sum(1 for r in bonus_results if r is not None)
        assert bonus_count > base_count

    def test_result_is_valid_injury_id(self):
        result = roll_injury(8, "slash", random.Random(42))
        if result is not None:
            assert result in INJURIES


# ---------------------------------------------------------------------------
# Create injury
# ---------------------------------------------------------------------------

class TestCreateInjury:
    def test_creates_active_injury(self):
        active = create_injury("cut_hand", current_day=50)
        assert active.injury_id == "cut_hand"
        assert active.acquired_day == 50
        assert active.heal_remaining == 10
        assert active.treated is False

    def test_permanent_injury_has_none_heal(self):
        active = create_injury("blinded_eye", current_day=100)
        assert active.heal_remaining is None


# ---------------------------------------------------------------------------
# Healing
# ---------------------------------------------------------------------------

class TestHealing:
    def test_healing_reduces_remaining_days(self):
        injuries = [ActiveInjury(injury_id="cut_hand", acquired_day=1, heal_remaining=10)]
        result = heal_injury_tick(injuries, days=3, in_port=True)
        assert len(result) == 1
        assert result[0].heal_remaining == 7

    def test_fully_healed_removed_from_list(self):
        injuries = [ActiveInjury(injury_id="cut_hand", acquired_day=1, heal_remaining=2)]
        result = heal_injury_tick(injuries, days=3, in_port=True)
        assert len(result) == 0

    def test_no_healing_at_sea(self):
        injuries = [ActiveInjury(injury_id="cut_hand", acquired_day=1, heal_remaining=10)]
        result = heal_injury_tick(injuries, days=5, in_port=False)
        assert result[0].heal_remaining == 10

    def test_medicines_double_heal_rate(self):
        injuries = [ActiveInjury(injury_id="cut_hand", acquired_day=1, heal_remaining=10)]
        result = heal_injury_tick(injuries, days=3, in_port=True, has_medicines=True)
        assert result[0].heal_remaining == 4  # 10 - (3*2) = 4

    def test_permanent_injury_never_heals(self):
        injuries = [ActiveInjury(injury_id="blinded_eye", acquired_day=1, heal_remaining=None)]
        result = heal_injury_tick(injuries, days=100, in_port=True, has_medicines=True)
        assert len(result) == 1
        assert result[0].heal_remaining is None

    def test_does_not_mutate_original(self):
        injuries = [ActiveInjury(injury_id="cut_hand", acquired_day=1, heal_remaining=10)]
        heal_injury_tick(injuries, days=3, in_port=True)
        assert injuries[0].heal_remaining == 10  # unchanged


# ---------------------------------------------------------------------------
# Treatment
# ---------------------------------------------------------------------------

class TestTreatment:
    def test_successful_treatment(self):
        injury = ActiveInjury(injury_id="broken_sword_arm", heal_remaining=60)
        result, silver, error = treat_injury(injury, silver=500)
        assert error is None
        assert result.treated is True
        assert result.heal_remaining == 30  # halved
        assert silver == 300  # 500 - 200

    def test_not_enough_silver(self):
        injury = ActiveInjury(injury_id="broken_sword_arm", heal_remaining=60)
        result, silver, error = treat_injury(injury, silver=50)
        assert error is not None
        assert "200 silver" in error
        assert silver == 50  # unchanged

    def test_permanent_injury_cannot_be_treated(self):
        injury = ActiveInjury(injury_id="blinded_eye", heal_remaining=None)
        _, _, error = treat_injury(injury, silver=1000)
        assert error is not None
        assert "permanent" in error.lower()

    def test_already_treated(self):
        injury = ActiveInjury(injury_id="cut_hand", heal_remaining=5, treated=True)
        _, _, error = treat_injury(injury, silver=1000)
        assert error is not None
        assert "already" in error.lower()

    def test_free_treatment_for_minor(self):
        injury = ActiveInjury(injury_id="cut_hand", heal_remaining=10)
        result, silver, error = treat_injury(injury, silver=100)
        assert error is None
        assert silver == 100  # cut_hand has heal_silver=0


# ---------------------------------------------------------------------------
# Effect aggregation
# ---------------------------------------------------------------------------

class TestEffects:
    def test_no_injuries_default_effects(self):
        effects = get_injury_effects([])
        assert effects["melee_damage_mod"] == 0
        assert effects["can_dodge"] is True
        assert effects["can_use_firearms"] is True
        assert effects["thrust_multiplier"] == 1.0

    def test_single_injury_effects(self):
        effects = get_injury_effects(["cut_hand"])
        assert effects["melee_damage_mod"] == -1

    def test_multiple_injuries_stack(self):
        effects = get_injury_effects(["cut_hand", "deep_slash"])
        assert effects["melee_damage_mod"] == -2  # -1 + -1

    def test_shattered_knee_blocks_dodge(self):
        effects = get_injury_effects(["shattered_knee"])
        assert effects["can_dodge"] is False

    def test_severed_fingers_blocks_firearms(self):
        effects = get_injury_effects(["severed_fingers"])
        assert effects["can_use_firearms"] is False

    def test_broken_arm_halves_thrust(self):
        effects = get_injury_effects(["broken_sword_arm"])
        assert effects["thrust_multiplier"] == 0.5

    def test_gunshot_reduces_hp_and_stamina(self):
        effects = get_injury_effects(["gunshot_wound"])
        assert effects["hp_max_mod"] == -2
        assert effects["stamina_max_mod"] == -2


# ---------------------------------------------------------------------------
# Injured body parts
# ---------------------------------------------------------------------------

class TestInjuredBodyParts:
    def test_empty_injuries(self):
        assert get_injured_body_parts([]) == set()

    def test_single_injury(self):
        assert get_injured_body_parts(["cut_hand"]) == {"hand"}

    def test_multiple_injuries_unique_parts(self):
        parts = get_injured_body_parts(["cut_hand", "shattered_knee"])
        assert parts == {"hand", "leg"}

    def test_unknown_injury_ignored(self):
        assert get_injured_body_parts(["nonexistent"]) == set()


# ---------------------------------------------------------------------------
# Style blocking
# ---------------------------------------------------------------------------

class TestStyleBlocking:
    def test_hand_injury_blocks_hand_style(self):
        assert check_injury_blocks_style(["cut_hand"], ("hand", "arm")) is True

    def test_leg_injury_blocks_leg_style(self):
        assert check_injury_blocks_style(["shattered_knee"], ("leg",)) is True

    def test_unrelated_injury_doesnt_block(self):
        # Eye injury doesn't block a style needing hand+arm
        assert check_injury_blocks_style(["blinded_eye"], ("hand", "arm")) is False

    def test_no_injuries_doesnt_block(self):
        assert check_injury_blocks_style([], ("hand", "arm", "leg")) is False
