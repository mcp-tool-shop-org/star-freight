"""Tests for the melee weapon system — catalog, regional availability, combat integration."""

import random

from portlight.content.melee_weapons import MELEE_WEAPONS, get_melee_weapons_for_region
from portlight.engine.combat import (
    _calc_melee_damage,
    create_player_combatant,
)


# ---------------------------------------------------------------------------
# Catalog validation
# ---------------------------------------------------------------------------

class TestMeleeWeaponCatalog:
    def test_weapons_defined(self):
        assert len(MELEE_WEAPONS) == 8

    def test_all_weapons_have_ids(self):
        for weapon_id, weapon in MELEE_WEAPONS.items():
            assert weapon.id == weapon_id
            assert weapon.name

    def test_weapon_classes_valid(self):
        valid_classes = {"blade", "dagger", "polearm", "axe", "club"}
        for w in MELEE_WEAPONS.values():
            assert w.weapon_class in valid_classes, f"{w.id} has invalid class {w.weapon_class}"

    def test_all_have_positive_cost(self):
        for w in MELEE_WEAPONS.values():
            assert w.silver_cost > 0, f"{w.id} has no cost"

    def test_cutlass_available_everywhere(self):
        cutlass = MELEE_WEAPONS["cutlass"]
        assert len(cutlass.available_regions) == 5

    def test_dagger_available_everywhere(self):
        dagger = MELEE_WEAPONS["dagger"]
        assert len(dagger.available_regions) == 5

    def test_rapier_limited_regions(self):
        rapier = MELEE_WEAPONS["rapier"]
        assert "Mediterranean" in rapier.available_regions
        assert "North Atlantic" in rapier.available_regions
        assert len(rapier.available_regions) == 2


# ---------------------------------------------------------------------------
# Regional availability
# ---------------------------------------------------------------------------

class TestMeleeWeaponRegions:
    def test_mediterranean_has_weapons(self):
        weapons = get_melee_weapons_for_region("Mediterranean")
        assert len(weapons) >= 3  # cutlass, rapier, dagger, halberd

    def test_east_indies_has_kris(self):
        weapons = get_melee_weapons_for_region("East Indies")
        ids = {w.id for w in weapons}
        assert "kris" in ids

    def test_halberd_only_mediterranean(self):
        halberd = MELEE_WEAPONS["halberd"]
        assert halberd.available_regions == ("Mediterranean",)

    def test_unknown_region_returns_empty(self):
        assert get_melee_weapons_for_region("Atlantis") == []


# ---------------------------------------------------------------------------
# Style compatibility
# ---------------------------------------------------------------------------

class TestStyleCompatibility:
    def test_rapier_compatible_with_la_destreza(self):
        rapier = MELEE_WEAPONS["rapier"]
        assert "la_destreza" in rapier.compatible_styles

    def test_boarding_axe_compatible_with_highland(self):
        axe = MELEE_WEAPONS["boarding_axe"]
        assert "highland_broadsword" in axe.compatible_styles

    def test_kris_compatible_with_silat(self):
        kris = MELEE_WEAPONS["kris"]
        assert "silat" in kris.compatible_styles

    def test_cutlass_no_style_compat(self):
        cutlass = MELEE_WEAPONS["cutlass"]
        assert len(cutlass.compatible_styles) == 0

    def test_dagger_no_style_compat(self):
        dagger = MELEE_WEAPONS["dagger"]
        assert len(dagger.compatible_styles) == 0


# ---------------------------------------------------------------------------
# Speed modifiers
# ---------------------------------------------------------------------------

class TestSpeedModifiers:
    def test_dagger_gives_stamina_bonus(self):
        dagger = MELEE_WEAPONS["dagger"]
        assert dagger.speed_mod == 1

    def test_halberd_gives_stamina_penalty(self):
        halberd = MELEE_WEAPONS["halberd"]
        assert halberd.speed_mod == -1

    def test_cutlass_neutral_speed(self):
        cutlass = MELEE_WEAPONS["cutlass"]
        assert cutlass.speed_mod == 0

    def test_dagger_increases_stamina_max(self):
        with_dagger = create_player_combatant(melee_weapon_id="dagger")
        without = create_player_combatant()
        assert with_dagger.stamina_max == without.stamina_max + 1

    def test_halberd_decreases_stamina_max(self):
        with_halberd = create_player_combatant(melee_weapon_id="halberd")
        without = create_player_combatant()
        assert with_halberd.stamina_max == without.stamina_max - 1


# ---------------------------------------------------------------------------
# Combat damage integration
# ---------------------------------------------------------------------------

class TestMeleeDamage:
    def test_weapon_adds_damage_bonus(self):
        rng = random.Random(42)
        # With cutlass (+1 damage)
        dmg_armed = _calc_melee_damage("thrust", "win", rng, melee_weapon_id="cutlass")
        rng2 = random.Random(42)
        dmg_unarmed = _calc_melee_damage("thrust", "win", rng2)
        assert dmg_armed > dmg_unarmed

    def test_rapier_thrust_bonus(self):
        """Rapier should add +1 base + 2 thrust = +3 on thrust wins."""
        rng = random.Random(42)
        dmg = _calc_melee_damage("thrust", "win", rng, melee_weapon_id="rapier")
        rng2 = random.Random(42)
        dmg_bare = _calc_melee_damage("thrust", "win", rng2)
        assert dmg == dmg_bare + 3  # +1 damage_bonus + 2 thrust_bonus

    def test_halberd_slash_bonus(self):
        """Halberd should add +3 base + 2 slash = +5 on slash wins."""
        rng = random.Random(42)
        dmg = _calc_melee_damage("slash", "win", rng, melee_weapon_id="halberd")
        rng2 = random.Random(42)
        dmg_bare = _calc_melee_damage("slash", "win", rng2)
        assert dmg == dmg_bare + 5  # +3 damage_bonus + 2 slash_bonus

    def test_no_damage_on_loss(self):
        rng = random.Random(42)
        dmg = _calc_melee_damage("thrust", "lose", rng, melee_weapon_id="cutlass")
        assert dmg == 0

    def test_invalid_weapon_no_crash(self):
        rng = random.Random(42)
        dmg = _calc_melee_damage("thrust", "win", rng, melee_weapon_id="nonexistent")
        assert dmg >= 0  # still calculates base damage

    def test_melee_weapon_id_on_combatant(self):
        state = create_player_combatant(melee_weapon_id="rapier")
        assert state.melee_weapon_id == "rapier"
