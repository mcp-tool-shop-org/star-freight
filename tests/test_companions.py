"""Tests for the companion system — recruitment, morale, departure, combat bonuses."""

from __future__ import annotations

import random

from portlight.content.companions import (
    COMPANIONS,
    MORALE_REACTIONS,
    ROLES,
    get_companions_at_port,
)
from portlight.engine.companion_engine import (
    PartyState,
    apply_morale_trigger,
    can_recruit,
    check_departures,
    dismiss,
    get_cohesion,
    get_party_combat_bonus,
    get_party_summary,
    recruit,
    roll_interception,
)


def _rng(seed: int = 42) -> random.Random:
    return random.Random(seed)


def _empty_party() -> PartyState:
    return PartyState()


def _standing(**regions) -> dict[str, int]:
    base = {"Mediterranean": 0, "North Atlantic": 0, "West Africa": 0, "East Indies": 0, "South Seas": 0}
    base.update(regions)
    return base


# ---------------------------------------------------------------------------
# Content catalog
# ---------------------------------------------------------------------------

class TestCompanionCatalog:
    def test_ten_companions_defined(self):
        assert len(COMPANIONS) == 10

    def test_two_per_role(self):
        role_counts: dict[str, int] = {}
        for c in COMPANIONS.values():
            role_counts[c.role_id] = role_counts.get(c.role_id, 0) + 1
        for role_id in ROLES:
            assert role_counts.get(role_id, 0) == 2, f"Role {role_id} doesn't have 2 companions"

    def test_five_roles_defined(self):
        assert len(ROLES) == 5

    def test_all_companions_have_dialog(self):
        for c in COMPANIONS.values():
            assert c.greeting
            assert c.hire_dialog
            assert c.departure_line

    def test_get_companions_at_port(self):
        comps = get_companions_at_port("ironhaven")
        assert len(comps) >= 1
        assert any(c.id == "iron_marta" for c in comps)

    def test_no_companions_at_empty_port(self):
        assert get_companions_at_port("nonexistent") == []

    def test_morale_reactions_cover_key_triggers(self):
        assert "combat_won" in MORALE_REACTIONS
        assert "contraband_trade" in MORALE_REACTIONS
        assert "spared_enemy" in MORALE_REACTIONS


# ---------------------------------------------------------------------------
# Recruitment
# ---------------------------------------------------------------------------

class TestRecruitment:
    def test_can_recruit_success(self):
        party = _empty_party()
        error = can_recruit(party, "red_tomas", 500, _standing(), "corsairs_rest")
        assert error is None

    def test_cant_recruit_wrong_port(self):
        party = _empty_party()
        error = can_recruit(party, "red_tomas", 500, _standing(), "ironhaven")
        assert error is not None

    def test_cant_recruit_no_silver(self):
        party = _empty_party()
        error = can_recruit(party, "red_tomas", 5, _standing(), "corsairs_rest")
        assert error is not None
        assert "silver" in error.lower()

    def test_cant_recruit_low_standing(self):
        party = _empty_party()
        error = can_recruit(party, "star_lila", 500, _standing(), "crosswind_isle")
        assert error is not None
        assert "standing" in error.lower()

    def test_can_recruit_with_standing(self):
        party = _empty_party()
        standing = _standing(**{"East Indies": 15})
        error = can_recruit(party, "star_lila", 500, standing, "crosswind_isle")
        assert error is None

    def test_cant_recruit_party_full(self):
        party = _empty_party()
        recruit(party, "red_tomas", 1)
        recruit(party, "iron_marta", 1)
        error = can_recruit(party, "old_henry", 500, _standing(**{"North Atlantic": 10}), "thornport")
        assert error is not None
        assert "full" in error.lower()

    def test_cant_recruit_departed(self):
        party = _empty_party()
        party.departed.append("red_tomas")
        error = can_recruit(party, "red_tomas", 500, _standing(), "corsairs_rest")
        assert error is not None
        assert "left" in error.lower()

    def test_recruit_adds_to_party(self):
        party = _empty_party()
        state = recruit(party, "red_tomas", current_day=10)
        assert len(party.companions) == 1
        assert state.companion_id == "red_tomas"
        assert state.morale == 70
        assert state.joined_day == 10


# ---------------------------------------------------------------------------
# Dismissal
# ---------------------------------------------------------------------------

class TestDismissal:
    def test_dismiss_removes(self):
        party = _empty_party()
        recruit(party, "red_tomas", 1)
        error = dismiss(party, "red_tomas")
        assert error is None
        assert len(party.companions) == 0

    def test_dismiss_unknown(self):
        party = _empty_party()
        error = dismiss(party, "nonexistent")
        assert error is not None


# ---------------------------------------------------------------------------
# Morale
# ---------------------------------------------------------------------------

class TestMorale:
    def test_combat_won_boosts_marine(self):
        party = _empty_party()
        recruit(party, "iron_marta", 1)  # marine, reckless
        results = apply_morale_trigger(party, "combat_won")
        assert len(results) == 1
        assert results[0][1] > 0  # positive morale delta

    def test_contraband_upsets_gentle(self):
        party = _empty_party()
        recruit(party, "dr_amara", 1)  # surgeon, gentle
        results = apply_morale_trigger(party, "contraband_trade")
        assert len(results) == 1
        assert results[0][1] < 0  # negative

    def test_profitable_trade_makes_qm_happy(self):
        party = _empty_party()
        recruit(party, "coin_mariam", 1)  # quartermaster, lawful
        results = apply_morale_trigger(party, "profitable_trade")
        deltas = [r[1] for r in results]
        assert any(d > 0 for d in deltas)

    def test_morale_clamped(self):
        party = _empty_party()
        state = recruit(party, "red_tomas", 1)
        state.morale = 99
        apply_morale_trigger(party, "nemesis_defeated")  # big boost
        assert state.morale <= 100

    def test_morale_floor(self):
        party = _empty_party()
        state = recruit(party, "iron_marta", 1)
        state.morale = 2
        apply_morale_trigger(party, "fled_combat")  # marine hates this
        assert state.morale >= 0


# ---------------------------------------------------------------------------
# Departure
# ---------------------------------------------------------------------------

class TestDeparture:
    def test_low_morale_triggers_departure(self):
        party = _empty_party()
        state = recruit(party, "red_tomas", 1)
        state.morale = 5  # below threshold
        departures = check_departures(party)
        assert len(departures) == 1
        assert departures[0].companion_id == "red_tomas"
        assert len(party.companions) == 0
        assert "red_tomas" in party.departed

    def test_ok_morale_no_departure(self):
        party = _empty_party()
        state = recruit(party, "red_tomas", 1)
        state.morale = 50
        departures = check_departures(party)
        assert len(departures) == 0
        assert len(party.companions) == 1

    def test_departed_cant_rejoin(self):
        party = _empty_party()
        state = recruit(party, "red_tomas", 1)
        state.morale = 5
        check_departures(party)
        error = can_recruit(party, "red_tomas", 500, _standing(), "corsairs_rest")
        assert error is not None


# ---------------------------------------------------------------------------
# Combat bonuses
# ---------------------------------------------------------------------------

class TestCombatBonuses:
    def test_marine_gives_damage_bonus(self):
        party = _empty_party()
        recruit(party, "iron_marta", 1)
        bonus = get_party_combat_bonus(party)
        assert bonus["damage_bonus"] >= 1

    def test_navigator_gives_speed(self):
        party = _empty_party()
        recruit(party, "star_lila", 1)
        bonus = get_party_combat_bonus(party)
        assert bonus["speed_bonus"] > 0

    def test_low_morale_reduces_bonus(self):
        party = _empty_party()
        state = recruit(party, "iron_marta", 1)
        state.morale = 15  # low
        bonus = get_party_combat_bonus(party)
        assert bonus["damage_bonus"] == 0  # scaled down to 0

    def test_empty_party_no_bonus(self):
        party = _empty_party()
        bonus = get_party_combat_bonus(party)
        assert all(v == 0 or v == 0.0 for v in bonus.values())

    def test_interception_roll(self):
        party = _empty_party()
        recruit(party, "iron_marta", 1)  # marine, 25% interception
        intercepted_count = 0
        for seed in range(100):
            intercepted, _ = roll_interception(party, 3, _rng(seed))
            if intercepted:
                intercepted_count += 1
        assert 10 < intercepted_count < 50  # ~25%


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

class TestDisplay:
    def test_party_summary(self):
        party = _empty_party()
        recruit(party, "red_tomas", 1)
        summary = get_party_summary(party)
        assert len(summary) == 1
        assert summary[0]["name"] == "Red Tomas"
        assert summary[0]["role"] == "Marine"

    def test_cohesion(self):
        party = _empty_party()
        s1 = recruit(party, "red_tomas", 1)
        s2 = recruit(party, "old_henry", 1)
        s1.morale = 80
        s2.morale = 60
        assert get_cohesion(party) == 70

    def test_empty_cohesion(self):
        assert get_cohesion(_empty_party()) == 0


# ---------------------------------------------------------------------------
# Save/load
# ---------------------------------------------------------------------------

class TestSaveLoad:
    def test_party_roundtrips(self):
        from portlight.engine.save import _party_from_dict, _party_to_dict
        party = _empty_party()
        s1 = recruit(party, "red_tomas", current_day=10)
        s1.morale = 55
        party.departed.append("old_henry")

        d = _party_to_dict(party)
        restored = _party_from_dict(d)
        assert len(restored.companions) == 1
        assert restored.companions[0].companion_id == "red_tomas"
        assert restored.companions[0].morale == 55
        assert "old_henry" in restored.departed

    def test_empty_party_roundtrips(self):
        from portlight.engine.save import _party_from_dict, _party_to_dict
        party = _empty_party()
        d = _party_to_dict(party)
        restored = _party_from_dict(d)
        assert len(restored.companions) == 0
