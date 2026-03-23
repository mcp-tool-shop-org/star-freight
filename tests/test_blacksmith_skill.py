"""Tests for the blacksmith skill — learning, effects, field repair, integration."""

from __future__ import annotations

from portlight.content.skills import (
    SKILLS,
    SKILL_TRAINERS,
    get_blacksmith_effects,
    get_trainers_at_port,
)
from portlight.engine.skill_engine import (
    apply_maintenance_discount,
    apply_upgrade_discount,
    can_learn_skill,
    field_repair_weapon,
    get_degrade_threshold_bonus,
    get_field_repair_max_quality,
    get_skill_display,
    get_skill_level,
    learn_skill,
)
from portlight.engine.weapon_quality import check_degradation


# ---------------------------------------------------------------------------
# Skill catalog
# ---------------------------------------------------------------------------

class TestSkillCatalog:
    def test_blacksmith_defined(self):
        assert "blacksmith" in SKILLS
        skill = SKILLS["blacksmith"]
        assert skill.max_level == 3
        assert len(skill.levels) == 3

    def test_levels_have_escalating_costs(self):
        skill = SKILLS["blacksmith"]
        costs = [level.silver_cost for level in skill.levels]
        assert costs == sorted(costs)
        assert costs[0] < costs[2]

    def test_trainers_exist(self):
        assert len(SKILL_TRAINERS) == 5  # 5 blacksmith trainers
        for t in SKILL_TRAINERS.values():
            assert t.skill_id == "blacksmith"

    def test_trainers_at_shipyard_ports(self):
        ports_with_trainers = {t.port_id for t in SKILL_TRAINERS.values()}
        assert "ironhaven" in ports_with_trainers
        assert "porto_novo" in ports_with_trainers
        assert "silva_bay" in ports_with_trainers

    def test_get_trainers_at_port(self):
        trainers = get_trainers_at_port("ironhaven", "blacksmith")
        assert len(trainers) == 1
        assert trainers[0].max_teach_level == 3

    def test_no_trainers_at_non_shipyard(self):
        assert get_trainers_at_port("al_manar", "blacksmith") == []


# ---------------------------------------------------------------------------
# Learning
# ---------------------------------------------------------------------------

class TestLearning:
    def test_can_learn_from_scratch(self):
        error = can_learn_skill({}, 500, "ironhaven", "blacksmith")
        assert error is None

    def test_cant_learn_no_silver(self):
        error = can_learn_skill({}, 10, "ironhaven", "blacksmith")
        assert error is not None
        assert "silver" in error.lower()

    def test_cant_learn_wrong_port(self):
        error = can_learn_skill({}, 500, "al_manar", "blacksmith")
        assert error is not None
        assert "trainer" in error.lower()

    def test_cant_exceed_max_level(self):
        error = can_learn_skill({"blacksmith": 3}, 500, "ironhaven", "blacksmith")
        assert error is not None
        assert "maximum" in error.lower()

    def test_cant_exceed_trainer_level(self):
        # typhoon_smith can only teach level 1
        error = can_learn_skill({"blacksmith": 1}, 500, "typhoon_anchorage", "blacksmith")
        assert error is not None
        assert "level" in error.lower()

    def test_learn_increments_level(self):
        skills, silver, days = learn_skill({}, 500, "blacksmith")
        assert skills["blacksmith"] == 1
        assert silver < 500
        assert days > 0

    def test_learn_level_2(self):
        skills, silver, days = learn_skill({"blacksmith": 1}, 500, "blacksmith")
        assert skills["blacksmith"] == 2

    def test_get_skill_level(self):
        assert get_skill_level({}, "blacksmith") == 0
        assert get_skill_level({"blacksmith": 2}, "blacksmith") == 2

    def test_get_skill_display(self):
        assert get_skill_display({}, "blacksmith") == "Untrained"
        assert get_skill_display({"blacksmith": 1}, "blacksmith") == "Apprentice"
        assert get_skill_display({"blacksmith": 3}, "blacksmith") == "Master"


# ---------------------------------------------------------------------------
# Blacksmith effects
# ---------------------------------------------------------------------------

class TestBlacksmithEffects:
    def test_level_0_no_effects(self):
        effects = get_blacksmith_effects(0)
        assert effects["maintenance_discount"] == 0.0
        assert effects["degrade_slow"] == 0.0
        assert effects["field_repair"] is False

    def test_level_1_basic(self):
        effects = get_blacksmith_effects(1)
        assert effects["maintenance_discount"] == 0.25
        assert effects["degrade_slow"] == 0.20
        assert effects["field_repair"] is False

    def test_level_2_field_repair(self):
        effects = get_blacksmith_effects(2)
        assert effects["field_repair"] is True
        assert effects["maintenance_discount"] == 0.50

    def test_level_3_master(self):
        effects = get_blacksmith_effects(3)
        assert effects["upgrade_discount"] == 0.25
        assert effects["degrade_slow"] == 0.60


# ---------------------------------------------------------------------------
# Maintenance discount
# ---------------------------------------------------------------------------

class TestMaintenanceDiscount:
    def test_no_skill_no_discount(self):
        assert apply_maintenance_discount(20, 0) == 20

    def test_level_1_discount(self):
        result = apply_maintenance_discount(20, 1)
        assert result == 15  # 20 * 0.75

    def test_level_3_discount(self):
        result = apply_maintenance_discount(20, 3)
        assert result == 10  # 20 * 0.50

    def test_minimum_cost_is_1(self):
        assert apply_maintenance_discount(1, 3) >= 1


# ---------------------------------------------------------------------------
# Upgrade discount
# ---------------------------------------------------------------------------

class TestUpgradeDiscount:
    def test_no_skill_no_discount(self):
        assert apply_upgrade_discount(100, 0) == 100
        assert apply_upgrade_discount(100, 2) == 100  # only level 3

    def test_level_3_discount(self):
        result = apply_upgrade_discount(100, 3)
        assert result == 75  # 100 * 0.75


# ---------------------------------------------------------------------------
# Degradation slowdown
# ---------------------------------------------------------------------------

class TestDegradationSlowdown:
    def test_no_skill_no_bonus(self):
        assert get_degrade_threshold_bonus(0) == 0

    def test_level_1_bonus(self):
        bonus = get_degrade_threshold_bonus(1)
        assert bonus == 2  # 10 * 0.20

    def test_level_3_bonus(self):
        bonus = get_degrade_threshold_bonus(3)
        assert bonus == 6  # 10 * 0.60

    def test_bonus_delays_degradation(self):
        # Without skill: degrades at 10 uses
        assert check_degradation("cutlass", "melee", 10) is True
        # With level 3 bonus: doesn't degrade at 10
        assert check_degradation("cutlass", "melee", 10, threshold_bonus=6) is False
        # Degrades at 16
        assert check_degradation("cutlass", "melee", 16, threshold_bonus=6) is True


# ---------------------------------------------------------------------------
# Field repair
# ---------------------------------------------------------------------------

class TestFieldRepair:
    def test_cant_repair_without_skill(self):
        quality = {"cutlass": "worn"}
        usage = {"cutlass": 5}
        success, error = field_repair_weapon("cutlass", quality, usage, 0)
        assert success is False
        assert "Journeyman" in error

    def test_level_2_can_field_repair(self):
        quality = {"cutlass": "worn"}
        usage = {"cutlass": 8}
        success, error = field_repair_weapon("cutlass", quality, usage, 2)
        assert success is True
        assert error is None
        assert usage["cutlass"] == 0  # reset
        assert quality["cutlass"] == "standard"  # restored

    def test_field_repair_resets_usage(self):
        quality = {"cutlass": "standard"}
        usage = {"cutlass": 7}
        field_repair_weapon("cutlass", quality, usage, 2)
        assert usage["cutlass"] == 0

    def test_field_repair_wont_exceed_standard(self):
        quality = {"cutlass": "fine"}
        usage = {"cutlass": 5}
        field_repair_weapon("cutlass", quality, usage, 3)
        assert quality["cutlass"] == "fine"  # already above standard, no change

    def test_field_repair_max_quality(self):
        assert get_field_repair_max_quality(2) == "standard"
        assert get_field_repair_max_quality(3) == "standard"
        assert get_field_repair_max_quality(0) == "rusted"  # can't really repair


# ---------------------------------------------------------------------------
# Save/load roundtrip
# ---------------------------------------------------------------------------

class TestSaveLoad:
    def test_skills_roundtrip(self):
        from portlight.engine.models import Captain
        from portlight.engine.save import _captain_from_dict, _captain_to_dict

        captain = Captain(skills={"blacksmith": 2})
        d = _captain_to_dict(captain)
        restored = _captain_from_dict(d)
        assert restored.skills == {"blacksmith": 2}

    def test_empty_skills_roundtrip(self):
        from portlight.engine.models import Captain
        from portlight.engine.save import _captain_from_dict, _captain_to_dict

        captain = Captain()
        d = _captain_to_dict(captain)
        restored = _captain_from_dict(d)
        assert restored.skills == {}
