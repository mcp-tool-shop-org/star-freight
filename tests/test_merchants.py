"""Tests for NPC merchant system — catalog, inventory, purchases."""

from portlight.content.merchants import MERCHANTS, get_merchant, get_merchants_at_port
from portlight.content.ports import PORTS
from portlight.engine.merchant import buy_from_merchant, get_merchant_inventory
from portlight.engine.models import Captain, CombatGear, Ship


def _make_captain(silver: int = 500) -> Captain:
    """Create a test captain with given silver."""
    return Captain(
        name="Test",
        silver=silver,
        ship=Ship(
            template_id="coastal_sloop", name="Test Ship",
            hull=50, hull_max=50, cargo_capacity=30,
            speed=6.0, crew=5, crew_max=8,
        ),
        combat_gear=CombatGear(),
    )


# ---------------------------------------------------------------------------
# Catalog validation
# ---------------------------------------------------------------------------

class TestMerchantCatalog:
    def test_merchants_exist(self):
        assert len(MERCHANTS) >= 14

    def test_all_merchants_have_valid_ports(self):
        for mid, m in MERCHANTS.items():
            assert m.port_id in PORTS, f"Merchant {mid} at unknown port {m.port_id}"

    def test_all_merchants_have_inventory_types(self):
        valid_types = {"melee", "armor", "ranged", "ammo"}
        for mid, m in MERCHANTS.items():
            assert len(m.inventory_types) >= 1, f"Merchant {mid} sells nothing"
            for t in m.inventory_types:
                assert t in valid_types, f"Merchant {mid} has invalid type {t}"

    def test_all_merchants_have_personality(self):
        for mid, m in MERCHANTS.items():
            assert m.personality, f"Merchant {mid} has no personality"
            assert m.greeting, f"Merchant {mid} has no greeting"

    def test_price_markup_reasonable(self):
        for mid, m in MERCHANTS.items():
            assert 1.0 <= m.price_markup <= 1.3, f"Merchant {mid} markup {m.price_markup} out of range"

    def test_get_merchant_by_id(self):
        m = get_merchant("marco_the_blade")
        assert m is not None
        assert m.name == "Marco"

    def test_get_unknown_merchant(self):
        assert get_merchant("nonexistent") is None


# ---------------------------------------------------------------------------
# Port coverage
# ---------------------------------------------------------------------------

class TestMerchantPorts:
    def test_porto_novo_has_merchant(self):
        merchants = get_merchants_at_port("porto_novo")
        assert len(merchants) >= 1

    def test_major_ports_have_merchants(self):
        major_ports = ["porto_novo", "ironhaven", "sun_harbor", "jade_port", "coral_throne"]
        for port_id in major_ports:
            merchants = get_merchants_at_port(port_id)
            assert len(merchants) >= 1, f"Major port {port_id} has no merchant"

    def test_empty_port_returns_empty(self):
        merchants = get_merchants_at_port("nonexistent_port")
        assert merchants == []


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

class TestMerchantInventory:
    def test_inventory_returns_items(self):
        m = get_merchant("marco_the_blade")
        items = get_merchant_inventory(m, "Mediterranean")
        assert len(items) >= 1

    def test_inventory_has_required_fields(self):
        m = get_merchant("marco_the_blade")
        items = get_merchant_inventory(m, "Mediterranean")
        for item in items:
            assert "item_type" in item
            assert "item_id" in item
            assert "name" in item
            assert "silver_cost" in item
            assert item["silver_cost"] > 0

    def test_markup_applied(self):
        m = get_merchant("fatima_armorworks")  # 1.15 markup
        items = get_merchant_inventory(m, "Mediterranean")
        # Find an armor item and verify markup
        armor_items = [i for i in items if i["item_type"] == "armor"]
        if armor_items:
            from portlight.content.armor import ARMOR
            item = armor_items[0]
            base = ARMOR[item["item_id"]].silver_cost
            assert item["silver_cost"] >= base  # markup applied

    def test_region_filtering_works(self):
        m = get_merchant("marco_the_blade")  # Porto Novo, Mediterranean
        items = get_merchant_inventory(m, "Mediterranean")
        item_ids = {i["item_id"] for i in items}
        # Cutlass is available everywhere, should be present
        assert "cutlass" in item_ids


# ---------------------------------------------------------------------------
# Purchase
# ---------------------------------------------------------------------------

class TestMerchantPurchase:
    def test_buy_melee_weapon(self):
        captain = _make_captain(500)
        result = buy_from_merchant(captain, "marco_the_blade", "cutlass", 1, "Mediterranean")
        assert isinstance(result, dict)
        assert captain.combat_gear.melee_weapon == "cutlass"
        assert captain.silver < 500

    def test_buy_armor(self):
        captain = _make_captain(500)
        result = buy_from_merchant(captain, "fatima_armorworks", "leather_vest", 1, "Mediterranean")
        assert isinstance(result, dict)
        assert captain.combat_gear.armor == "leather_vest"

    def test_buy_insufficient_silver(self):
        captain = _make_captain(1)
        result = buy_from_merchant(captain, "marco_the_blade", "cutlass", 1, "Mediterranean")
        assert isinstance(result, str)
        assert "silver" in result.lower()

    def test_buy_unknown_item(self):
        captain = _make_captain(500)
        result = buy_from_merchant(captain, "marco_the_blade", "laser_gun", 1, "Mediterranean")
        assert isinstance(result, str)

    def test_buy_unknown_merchant(self):
        captain = _make_captain(500)
        result = buy_from_merchant(captain, "nobody", "cutlass", 1, "Mediterranean")
        assert isinstance(result, str)

    def test_buy_ammo_adds_quantity(self):
        captain = _make_captain(500)
        captain.combat_gear.firearm = "matchlock_pistol"
        result = buy_from_merchant(captain, "marco_the_blade", "pistol_shot", 2, "Mediterranean")
        assert isinstance(result, dict)
        assert captain.combat_gear.firearm_ammo >= 6  # 3 per bundle * 2

    def test_buy_replaces_weapon(self):
        captain = _make_captain(500)
        captain.combat_gear.melee_weapon = "dagger"
        buy_from_merchant(captain, "marco_the_blade", "cutlass", 1, "Mediterranean")
        assert captain.combat_gear.melee_weapon == "cutlass"
