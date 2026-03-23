"""Tests for the ranged weapon catalog and ammo system."""

from __future__ import annotations

from portlight.content.ranged_weapons import (
    AMMO,
    RANGED_WEAPONS,
    get_ammo_for_region,
    get_weapons_for_region,
)


# ---------------------------------------------------------------------------
# Weapon catalog
# ---------------------------------------------------------------------------

class TestWeaponCatalog:
    def test_weapons_defined(self):
        assert len(RANGED_WEAPONS) >= 6

    def test_weapon_types_valid(self):
        for w in RANGED_WEAPONS.values():
            assert w.weapon_type in ("firearm", "thrown", "mechanical")

    def test_all_weapons_have_positive_damage(self):
        for w in RANGED_WEAPONS.values():
            assert w.damage_min > 0
            assert w.damage_max >= w.damage_min

    def test_accuracy_in_range(self):
        for w in RANGED_WEAPONS.values():
            assert 0.0 < w.accuracy <= 1.0

    def test_firearms_are_loud(self):
        firearms = [w for w in RANGED_WEAPONS.values() if w.weapon_type == "firearm"]
        assert len(firearms) >= 2
        for w in firearms:
            assert w.loud is True

    def test_thrown_weapons_are_silent(self):
        thrown = [w for w in RANGED_WEAPONS.values() if w.weapon_type == "thrown"]
        assert len(thrown) == 3
        for w in thrown:
            assert w.loud is False

    def test_thrown_have_zero_reload(self):
        thrown = [w for w in RANGED_WEAPONS.values() if w.weapon_type == "thrown"]
        for w in thrown:
            assert w.reload_turns == 0

    def test_firearms_have_reload(self):
        firearms = [w for w in RANGED_WEAPONS.values() if w.weapon_type == "firearm"]
        for w in firearms:
            assert w.reload_turns >= 1

    def test_bolas_have_stun(self):
        bolas = RANGED_WEAPONS["bolas"]
        assert bolas.stun_turns > 0

    def test_stun_only_on_stun_weapons(self):
        stun_weapons = {"bolas", "blowgun"}  # weapons that can stun
        for w in RANGED_WEAPONS.values():
            if w.id not in stun_weapons:
                assert w.stun_turns == 0, f"{w.id} has unexpected stun"


# ---------------------------------------------------------------------------
# Regional availability
# ---------------------------------------------------------------------------

class TestRegionalAvailability:
    def test_mediterranean_weapons(self):
        weapons = get_weapons_for_region("Mediterranean")
        ids = {w.id for w in weapons}
        assert "matchlock_pistol" in ids
        assert "hand_crossbow" in ids
        assert "throwing_knife" in ids

    def test_south_seas_weapons(self):
        weapons = get_weapons_for_region("South Seas")
        ids = {w.id for w in weapons}
        assert "sling" in ids
        assert "bolas" in ids
        assert "throwing_knife" in ids

    def test_throwing_knife_available_everywhere(self):
        regions = ["Mediterranean", "North Atlantic", "West Africa", "East Indies", "South Seas"]
        for region in regions:
            weapons = get_weapons_for_region(region)
            assert any(w.id == "throwing_knife" for w in weapons)

    def test_wheellock_in_north_atlantic(self):
        na_weapons = get_weapons_for_region("North Atlantic")
        assert any(w.id == "wheellock_pistol" for w in na_weapons)

    def test_unknown_region_returns_empty(self):
        assert get_weapons_for_region("Narnia") == []


# ---------------------------------------------------------------------------
# Ammo catalog
# ---------------------------------------------------------------------------

class TestAmmoCatalog:
    def test_ammo_types_defined(self):
        assert len(AMMO) >= 2

    def test_ammo_has_positive_quantity(self):
        for a in AMMO.values():
            assert a.quantity > 0
            assert a.silver_cost > 0

    def test_ammo_types_match_weapons(self):
        ammo_types = {a.weapon_type for a in AMMO.values()}
        assert "firearm" in ammo_types
        assert "mechanical" in ammo_types

    def test_ammo_region_availability(self):
        ammo = get_ammo_for_region("Mediterranean")
        ids = {a.id for a in ammo}
        assert "pistol_shot" in ids
        assert "crossbow_bolts" in ids
