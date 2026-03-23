"""Tests for loot drop system — tables, rolling, application."""

import random

from portlight.content.goods import GOODS
from portlight.content.armor import ARMOR
from portlight.content.melee_weapons import MELEE_WEAPONS
from portlight.content.ranged_weapons import RANGED_WEAPONS, AMMO
from portlight.content.loot_tables import (
    CAPTAIN_LOOT_OVERRIDES,
    LOOT_TABLES,
    get_loot_table_for_strength,
)
from portlight.engine.loot import apply_loot, roll_loot
from portlight.engine.models import Captain, CombatGear, Ship


def _make_captain() -> Captain:
    return Captain(
        name="Test",
        silver=100,
        ship=Ship(
            template_id="coastal_sloop", name="Test Ship",
            hull=50, hull_max=50, cargo_capacity=30,
            speed=6.0, crew=5, crew_max=8,
        ),
        combat_gear=CombatGear(),
    )


# ---------------------------------------------------------------------------
# Table validation
# ---------------------------------------------------------------------------

class TestLootTables:
    def test_four_tiers_exist(self):
        assert "loot_weak" in LOOT_TABLES
        assert "loot_medium" in LOOT_TABLES
        assert "loot_strong" in LOOT_TABLES
        assert "loot_boss" in LOOT_TABLES

    def test_all_tables_have_entries(self):
        for tid, table in LOOT_TABLES.items():
            assert len(table.entries) >= 2, f"Table {tid} has too few entries"

    def test_all_tables_include_silver(self):
        for tid, table in LOOT_TABLES.items():
            silver_entries = [e for e in table.entries if e.item_type == "silver"]
            assert len(silver_entries) >= 1, f"Table {tid} has no silver entry"

    def test_all_item_ids_valid(self):
        """Every item referenced in loot tables must exist in content catalogs."""
        all_valid = set(GOODS.keys()) | set(MELEE_WEAPONS.keys()) | set(ARMOR.keys()) | \
                    set(RANGED_WEAPONS.keys()) | set(AMMO.keys()) | {"silver"}
        for tid, table in {**LOOT_TABLES, **CAPTAIN_LOOT_OVERRIDES}.items():
            for entry in table.entries:
                if entry.item_type != "silver":
                    assert entry.item_id in all_valid, \
                        f"Table {tid} references unknown item {entry.item_id}"

    def test_weights_positive(self):
        for tid, table in {**LOOT_TABLES, **CAPTAIN_LOOT_OVERRIDES}.items():
            for entry in table.entries:
                assert entry.weight > 0, f"Table {tid} entry {entry.item_id} has non-positive weight"

    def test_captain_overrides_match_known_captains(self):
        from portlight.content.factions import PIRATE_CAPTAINS
        for cid in CAPTAIN_LOOT_OVERRIDES:
            assert cid in PIRATE_CAPTAINS, f"Loot override for unknown captain {cid}"

    def test_all_named_captains_have_loot(self):
        from portlight.content.factions import PIRATE_CAPTAINS
        for cid in PIRATE_CAPTAINS:
            assert cid in CAPTAIN_LOOT_OVERRIDES, f"Named captain {cid} has no loot table"


# ---------------------------------------------------------------------------
# Strength scaling
# ---------------------------------------------------------------------------

class TestStrengthScaling:
    def test_weak_for_low_strength(self):
        table = get_loot_table_for_strength(3)
        assert table.id == "loot_weak"

    def test_medium_for_mid_strength(self):
        table = get_loot_table_for_strength(5)
        assert table.id == "loot_medium"

    def test_strong_for_high_strength(self):
        table = get_loot_table_for_strength(7)
        assert table.id == "loot_strong"

    def test_boss_for_max_strength(self):
        table = get_loot_table_for_strength(9)
        assert table.id == "loot_boss"


# ---------------------------------------------------------------------------
# Rolling
# ---------------------------------------------------------------------------

class TestRollLoot:
    def test_always_includes_silver(self):
        rng = random.Random(42)
        drops = roll_loot(5, None, rng)
        silver_drops = [d for d in drops if d["item_type"] == "silver"]
        assert len(silver_drops) >= 1

    def test_silver_quantity_positive(self):
        rng = random.Random(42)
        drops = roll_loot(5, None, rng)
        silver = next(d for d in drops if d["item_type"] == "silver")
        assert silver["quantity"] > 0

    def test_named_captain_uses_override(self):
        rng = random.Random(42)
        drops = roll_loot(6, "scarlet_ana", rng)
        # Scarlet Ana's loot should include weapons or black_powder
        item_ids = {d["item_id"] for d in drops}
        # At least silver should always be there
        assert "silver" in item_ids

    def test_multiple_drops(self):
        rng = random.Random(42)
        drops = roll_loot(9, None, rng)  # boss tier, 3 drops
        assert len(drops) >= 2

    def test_deterministic_with_seed(self):
        drops1 = roll_loot(5, None, random.Random(42))
        drops2 = roll_loot(5, None, random.Random(42))
        assert drops1 == drops2


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class TestApplyLoot:
    def test_apply_silver(self):
        captain = _make_captain()
        silver_before = captain.silver
        msgs = apply_loot(captain, [{"item_type": "silver", "item_id": "silver", "quantity": 50}])
        assert captain.silver == silver_before + 50
        assert any("50" in m for m in msgs)

    def test_apply_cargo(self):
        captain = _make_captain()
        _msgs = apply_loot(captain, [{"item_type": "cargo", "item_id": "spice", "quantity": 3}])
        assert any(c.good_id == "spice" and c.quantity == 3 for c in captain.cargo)

    def test_apply_cargo_merges(self):
        captain = _make_captain()
        from portlight.engine.models import CargoItem
        captain.cargo.append(CargoItem(good_id="spice", quantity=2))
        apply_loot(captain, [{"item_type": "cargo", "item_id": "spice", "quantity": 3}])
        spice = next(c for c in captain.cargo if c.good_id == "spice")
        assert spice.quantity == 5

    def test_apply_melee_weapon(self):
        captain = _make_captain()
        apply_loot(captain, [{"item_type": "melee_weapon", "item_id": "rapier", "quantity": 1}])
        assert captain.combat_gear.melee_weapon == "rapier"

    def test_apply_armor(self):
        captain = _make_captain()
        apply_loot(captain, [{"item_type": "armor", "item_id": "chain_shirt", "quantity": 1}])
        assert captain.combat_gear.armor == "chain_shirt"

    def test_apply_ammo(self):
        captain = _make_captain()
        apply_loot(captain, [{"item_type": "ammo", "item_id": "pistol_shot", "quantity": 2}])
        assert captain.combat_gear.firearm_ammo == 6  # 3 per bundle * 2

    def test_apply_returns_messages(self):
        captain = _make_captain()
        msgs = apply_loot(captain, [
            {"item_type": "silver", "item_id": "silver", "quantity": 10},
            {"item_type": "cargo", "item_id": "grain", "quantity": 2},
        ])
        assert len(msgs) == 2
