"""Tests for the armor system — catalog, regional availability, combat integration."""

import random

from portlight.content.armor import ARMOR, get_armor_for_region
from portlight.engine.combat import (
    CombatantState,
    create_player_combatant,
    resolve_combat_round,
)


# ---------------------------------------------------------------------------
# Catalog validation
# ---------------------------------------------------------------------------

class TestArmorCatalog:
    def test_armor_pieces_defined(self):
        assert len(ARMOR) == 6

    def test_all_armor_have_ids(self):
        for armor_id, armor in ARMOR.items():
            assert armor.id == armor_id
            assert armor.name

    def test_armor_types_valid(self):
        valid_types = {"light", "medium", "heavy"}
        for a in ARMOR.values():
            assert a.armor_type in valid_types, f"{a.id} has invalid type {a.armor_type}"

    def test_damage_reduction_positive(self):
        for a in ARMOR.values():
            assert a.damage_reduction > 0, f"{a.id} has no damage reduction"

    def test_light_armor_no_penalties(self):
        for a in ARMOR.values():
            if a.armor_type == "light":
                assert a.dodge_penalty == 0, f"Light armor {a.id} shouldn't penalize dodge"
                assert a.stamina_penalty == 0, f"Light armor {a.id} shouldn't penalize stamina"

    def test_heavy_armor_has_penalties(self):
        for a in ARMOR.values():
            if a.armor_type == "heavy":
                assert a.dodge_penalty > 0, f"Heavy armor {a.id} should penalize dodge"
                assert a.stamina_penalty < 0, f"Heavy armor {a.id} should reduce stamina"

    def test_dr_scales_with_tier(self):
        light_dr = max(a.damage_reduction for a in ARMOR.values() if a.armor_type == "light")
        medium_dr = max(a.damage_reduction for a in ARMOR.values() if a.armor_type == "medium")
        heavy_dr = max(a.damage_reduction for a in ARMOR.values() if a.armor_type == "heavy")
        assert light_dr <= medium_dr <= heavy_dr
        assert light_dr < heavy_dr  # at least light < heavy

    def test_all_regions_represented(self):
        all_regions = set()
        for a in ARMOR.values():
            all_regions.update(a.available_regions)
        assert "Mediterranean" in all_regions
        assert "North Atlantic" in all_regions
        assert "West Africa" in all_regions
        assert "East Indies" in all_regions

    def test_cost_scales_with_tier(self):
        min_light = min(a.silver_cost for a in ARMOR.values() if a.armor_type == "light")
        max_heavy = max(a.silver_cost for a in ARMOR.values() if a.armor_type == "heavy")
        assert min_light < max_heavy


# ---------------------------------------------------------------------------
# Regional availability
# ---------------------------------------------------------------------------

class TestArmorRegions:
    def test_mediterranean_has_armor(self):
        armor = get_armor_for_region("Mediterranean")
        assert len(armor) >= 1

    def test_north_atlantic_has_all_tiers(self):
        armor = get_armor_for_region("North Atlantic")
        types = {a.armor_type for a in armor}
        assert "light" in types
        assert "medium" in types
        assert "heavy" in types

    def test_cuirass_only_in_north_atlantic(self):
        cuirass = ARMOR["cuirass"]
        assert cuirass.available_regions == ("North Atlantic",)

    def test_unknown_region_returns_empty(self):
        assert get_armor_for_region("Atlantis") == []


# ---------------------------------------------------------------------------
# Combat integration
# ---------------------------------------------------------------------------

class TestArmorCombat:
    def test_armor_dr_reduces_damage(self):
        """Damage should be reduced by armor DR."""
        from portlight.content.armor import ARMOR
        armored = create_player_combatant(armor_id="chain_shirt")
        unarmored = create_player_combatant()
        assert armored.armor_dr == ARMOR["chain_shirt"].damage_reduction
        assert unarmored.armor_dr == 0

    def test_no_armor_no_dr(self):
        state = create_player_combatant()
        assert state.armor_dr == 0
        assert state.dodge_stamina_penalty == 0

    def test_heavy_armor_stamina_penalty(self):
        state = create_player_combatant(armor_id="cuirass")
        no_armor = create_player_combatant()
        assert state.stamina_max < no_armor.stamina_max

    def test_heavy_armor_dodge_penalty(self):
        state = create_player_combatant(armor_id="cuirass")
        assert state.dodge_stamina_penalty == 2

    def test_light_armor_no_stamina_penalty(self):
        state = create_player_combatant(armor_id="leather_vest")
        no_armor = create_player_combatant()
        assert state.stamina_max == no_armor.stamina_max

    def test_invalid_armor_id_no_crash(self):
        state = create_player_combatant(armor_id="nonexistent_armor")
        assert state.armor_dr == 0

    def test_dr_applied_in_combat_round(self):
        """Armor DR should reduce incoming damage during combat resolution."""
        rng = random.Random(100)
        # Create armored player with DR 3 (cuirass)
        player = create_player_combatant(armor_id="cuirass")
        opponent = CombatantState(hp=10, hp_max=10, stamina=6, stamina_max=6)

        # Run several rounds, compare damage taken
        total_dmg_armored = 0
        for _ in range(20):
            rng_copy = random.Random(rng.random())
            result = resolve_combat_round("thrust", player, opponent, "aggressive", rng_copy)
            total_dmg_armored += result.damage_to_player
            # Reset HP for next round
            player.hp = player.hp_max
            opponent.hp = opponent.hp_max

        # Do same without armor
        rng2 = random.Random(100)
        player_naked = create_player_combatant()
        total_dmg_naked = 0
        for _ in range(20):
            rng_copy = random.Random(rng2.random())
            result = resolve_combat_round("thrust", player_naked, opponent, "aggressive", rng_copy)
            total_dmg_naked += result.damage_to_player
            player_naked.hp = player_naked.hp_max
            opponent.hp = opponent.hp_max

        # Armored should take less total damage
        assert total_dmg_armored <= total_dmg_naked
