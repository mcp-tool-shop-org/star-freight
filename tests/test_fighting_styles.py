"""Tests for fighting styles content and training engine."""

from __future__ import annotations

import pytest

from portlight.content.fighting_styles import (
    FIGHTING_STYLES,
    STYLE_MASTERS,
)
from portlight.engine.training import (
    can_learn_style,
    check_style_usable,
    get_available_training,
    get_masters_at_port,
    learn_style,
)


# ---- Valid action names for beat/loses_to validation ----
VALID_ACTIONS = {
    "thrust", "slash", "parry", "dodge", "shoot", "throw",
    "estocada", "cleave", "leg_sweep", "keris_strike", "joint_lock",
}


# =========================================================================
# 1. Style definitions (5 tests)
# =========================================================================

class TestStyleDefinitions:
    """Verify all five styles exist with correct metadata."""

    @pytest.mark.parametrize("style_id", [
        "la_destreza", "highland_broadsword", "dambe", "silat", "lua",
    ])
    def test_style_exists(self, style_id: str) -> None:
        assert style_id in FIGHTING_STYLES

    def test_style_regions(self) -> None:
        expected = {
            "la_destreza": "Mediterranean",
            "highland_broadsword": "North Atlantic",
            "dambe": "West Africa",
            "silat": "East Indies",
            "lua": "South Seas",
        }
        for sid, region in expected.items():
            assert FIGHTING_STYLES[sid].region == region

    def test_training_ports_assigned(self) -> None:
        expected_ports = {
            "la_destreza": ("porto_novo", "al_manar"),
            "highland_broadsword": ("ironhaven", "thornport"),
            "dambe": ("sun_harbor", "pearl_shallows"),
            "silat": ("jade_port", "monsoon_reach"),
            "lua": ("coral_throne", "typhoon_anchorage"),
        }
        for sid, ports in expected_ports.items():
            assert FIGHTING_STYLES[sid].training_port_ids == ports

    def test_descriptions_nonempty(self) -> None:
        for style in FIGHTING_STYLES.values():
            assert len(style.description) > 0

    def test_historical_notes_nonempty(self) -> None:
        for style in FIGHTING_STYLES.values():
            assert len(style.historical_note) > 0


# =========================================================================
# 2. Master definitions (3 tests)
# =========================================================================

class TestMasterDefinitions:
    """Verify all ten masters exist with correct mappings."""

    def test_ten_masters_exist(self) -> None:
        assert len(STYLE_MASTERS) == 10

    def test_masters_map_to_valid_style_and_port(self) -> None:
        for master in STYLE_MASTERS.values():
            style = FIGHTING_STYLES[master.style_id]
            assert master.port_id in style.training_port_ids

    def test_two_masters_per_style(self) -> None:
        counts: dict[str, int] = {}
        for master in STYLE_MASTERS.values():
            counts[master.style_id] = counts.get(master.style_id, 0) + 1
        for style_id in FIGHTING_STYLES:
            assert counts.get(style_id, 0) == 2, f"{style_id} should have 2 masters"


# =========================================================================
# 3. can_learn_style (8 tests)
# =========================================================================

class TestCanLearnStyle:
    """Prerequisite checks for learning a style."""

    def test_success_no_prereqs(self) -> None:
        result = can_learn_style([], set(), 200, "porto_novo", "la_destreza")
        assert result is None

    def test_success_with_prereqs(self) -> None:
        # Silat requires 1 prerequisite style
        result = can_learn_style(
            ["la_destreza"], set(), 200, "jade_port", "silat",
        )
        assert result is None

    def test_already_known(self) -> None:
        result = can_learn_style(
            ["la_destreza"], set(), 200, "porto_novo", "la_destreza",
        )
        assert result is not None
        assert "already know" in result

    def test_wrong_port(self) -> None:
        result = can_learn_style([], set(), 200, "ironhaven", "la_destreza")
        assert result is not None
        assert "No" in result and "master" in result

    def test_not_enough_silver(self) -> None:
        result = can_learn_style([], set(), 10, "porto_novo", "la_destreza")
        assert result is not None
        assert "silver" in result.lower()

    def test_prereq_not_met_silat(self) -> None:
        result = can_learn_style([], set(), 200, "jade_port", "silat")
        assert result is not None
        assert "requires" in result.lower()

    def test_injury_blocks_hand(self) -> None:
        result = can_learn_style(
            [], {"hand"}, 200, "porto_novo", "la_destreza",
        )
        assert result is not None
        assert "hand" in result

    def test_injury_blocks_leg(self) -> None:
        result = can_learn_style(
            [], {"leg"}, 200, "sun_harbor", "dambe",
        )
        assert result is not None
        assert "leg" in result

    def test_unrelated_injury_doesnt_block(self) -> None:
        # Eye injury should not block la_destreza (needs hand, arm)
        result = can_learn_style(
            [], {"eye"}, 200, "porto_novo", "la_destreza",
        )
        assert result is None


# =========================================================================
# 4. learn_style (3 tests)
# =========================================================================

class TestLearnStyle:
    """Apply learning effects."""

    def test_deducts_correct_silver(self) -> None:
        _, remaining = learn_style([], 200, "la_destreza")
        assert remaining == 200 - 80

    def test_adds_style_to_list(self) -> None:
        new_styles, _ = learn_style([], 200, "la_destreza")
        assert "la_destreza" in new_styles

    def test_does_not_modify_original_list(self) -> None:
        original: list[str] = []
        learn_style(original, 200, "la_destreza")
        assert original == []


# =========================================================================
# 5. get_available_training (3 tests)
# =========================================================================

class TestGetAvailableTraining:
    """Port-based training lookups."""

    def test_porto_novo_has_la_destreza(self) -> None:
        styles = get_available_training("porto_novo")
        assert styles == ["la_destreza"]

    def test_jade_port_has_silat(self) -> None:
        styles = get_available_training("jade_port")
        assert styles == ["silat"]

    def test_nonexistent_port_returns_empty(self) -> None:
        styles = get_available_training("nowhere_port")
        assert styles == []


# =========================================================================
# 6. get_masters_at_port (2 tests)
# =========================================================================

class TestGetMastersAtPort:
    """Master lookups by port."""

    def test_ironhaven_masters(self) -> None:
        masters = get_masters_at_port("ironhaven")
        assert len(masters) == 1
        assert masters[0].id == "red_hamish"

    def test_nonexistent_port_returns_empty(self) -> None:
        masters = get_masters_at_port("nowhere_port")
        assert masters == []


# =========================================================================
# 7. check_style_usable (4 tests)
# =========================================================================

class TestCheckStyleUsable:
    """Injury-based usability checks."""

    def test_healthy_is_usable(self) -> None:
        assert check_style_usable("la_destreza", set()) is True

    def test_injured_hand_blocks_la_destreza(self) -> None:
        assert check_style_usable("la_destreza", {"hand"}) is False

    def test_injured_leg_blocks_dambe(self) -> None:
        assert check_style_usable("dambe", {"leg"}) is False

    def test_unrelated_injury_doesnt_block_broadsword(self) -> None:
        # Highland broadsword needs arm only; eye injury is irrelevant
        assert check_style_usable("highland_broadsword", {"eye"}) is True


# =========================================================================
# 8. Style action validation (2 tests)
# =========================================================================

class TestStyleActionValidation:
    """Structural integrity of special actions."""

    def test_all_actions_have_positive_stamina_and_nonneg_cooldown(self) -> None:
        for style in FIGHTING_STYLES.values():
            action = style.special_action
            assert action is not None, f"{style.id} missing special action"
            assert action.stamina_cost > 0, f"{action.id} stamina must be positive"
            assert action.cooldown >= 0, f"{action.id} cooldown must be non-negative"

    def test_beats_and_loses_to_contain_valid_actions(self) -> None:
        for style in FIGHTING_STYLES.values():
            action = style.special_action
            assert action is not None
            for name in action.beats:
                assert name in VALID_ACTIONS, f"{action.id} beats unknown action: {name}"
            for name in action.loses_to:
                assert name in VALID_ACTIONS, f"{action.id} loses_to unknown action: {name}"
