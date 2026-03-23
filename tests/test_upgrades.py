"""Tests for ship upgrade models, content catalog, and save serialization."""

from pathlib import Path

from portlight.engine.models import (
    InstalledUpgrade,
    ShipClass,
    UPGRADE_SLOTS,
    UpgradeCategory,
)
from portlight.content.upgrades import UPGRADES
from portlight.content.ships import SHIPS, create_ship_from_template
from portlight.content.world import new_game
from portlight.engine.save import (
    CURRENT_SAVE_VERSION,
    load_game,
    migrate_save,
    save_game,
)


# ---------------------------------------------------------------------------
# Content catalog validation
# ---------------------------------------------------------------------------

class TestUpgradeCatalog:
    def test_all_upgrades_have_unique_ids(self):
        ids = [u.id for u in UPGRADES.values()]
        assert len(ids) == len(set(ids))

    def test_all_upgrades_have_valid_category(self):
        for u in UPGRADES.values():
            assert isinstance(u.category, UpgradeCategory)

    def test_all_upgrades_have_positive_price(self):
        for u in UPGRADES.values():
            assert u.price > 0, f"{u.id} has non-positive price"

    def test_catalog_has_18_upgrades(self):
        assert len(UPGRADES) == 18

    def test_every_category_has_three_upgrades(self):
        for cat in UpgradeCategory:
            count = sum(1 for u in UPGRADES.values() if u.category == cat)
            assert count == 3, f"{cat.value} has {count} upgrades, expected 3"

    def test_price_curve_range(self):
        prices = [u.price for u in UPGRADES.values()]
        assert min(prices) >= 50, "Cheapest upgrade should cost at least 50"
        assert max(prices) <= 600, "Most expensive upgrade should be under 600"


# ---------------------------------------------------------------------------
# Upgrade slot mapping
# ---------------------------------------------------------------------------

class TestUpgradeSlots:
    def test_slot_counts_per_class(self):
        assert UPGRADE_SLOTS[ShipClass.SLOOP] == 2
        assert UPGRADE_SLOTS[ShipClass.CUTTER] == 3
        assert UPGRADE_SLOTS[ShipClass.BRIGANTINE] == 4
        assert UPGRADE_SLOTS[ShipClass.GALLEON] == 5
        assert UPGRADE_SLOTS[ShipClass.MAN_OF_WAR] == 6

    def test_all_ship_classes_have_slots(self):
        for sc in ShipClass:
            assert sc in UPGRADE_SLOTS

    def test_create_ship_sets_upgrade_slots(self):
        for template in SHIPS.values():
            ship = create_ship_from_template(template)
            expected = UPGRADE_SLOTS[template.ship_class]
            assert ship.upgrade_slots == expected, (
                f"{template.id}: got {ship.upgrade_slots}, expected {expected}"
            )


# ---------------------------------------------------------------------------
# InstalledUpgrade model
# ---------------------------------------------------------------------------

class TestInstalledUpgrade:
    def test_basic_creation(self):
        u = InstalledUpgrade(upgrade_id="iron_strapping", installed_day=10)
        assert u.upgrade_id == "iron_strapping"
        assert u.installed_day == 10

    def test_defaults(self):
        u = InstalledUpgrade(upgrade_id="lateen_rigging")
        assert u.installed_day == 0


# ---------------------------------------------------------------------------
# Ship with upgrades
# ---------------------------------------------------------------------------

class TestShipUpgrades:
    def test_ship_starts_with_no_upgrades(self):
        ship = create_ship_from_template(SHIPS["coastal_sloop"])
        assert ship.upgrades == []

    def test_ship_can_hold_upgrades(self):
        ship = create_ship_from_template(SHIPS["trade_brigantine"])
        ship.upgrades.append(InstalledUpgrade(upgrade_id="iron_strapping", installed_day=5))
        assert len(ship.upgrades) == 1
        assert ship.upgrades[0].upgrade_id == "iron_strapping"

    def test_upgrade_slots_match_class(self):
        sloop = create_ship_from_template(SHIPS["coastal_sloop"])
        assert sloop.upgrade_slots == 2
        galleon = create_ship_from_template(SHIPS["merchant_galleon"])
        assert galleon.upgrade_slots == 5


# ---------------------------------------------------------------------------
# Save/load with upgrades
# ---------------------------------------------------------------------------

class TestUpgradeSave:
    def test_round_trip_ship_with_upgrades(self, tmp_path: Path):
        world = new_game("Trader")
        world.captain.ship.upgrades = [
            InstalledUpgrade(upgrade_id="iron_strapping", installed_day=3),
            InstalledUpgrade(upgrade_id="lateen_rigging", installed_day=7),
        ]
        world.captain.ship.upgrade_slots = 4
        save_game(world, base_path=tmp_path)
        loaded, *_ = load_game(base_path=tmp_path)
        assert len(loaded.captain.ship.upgrades) == 2
        assert loaded.captain.ship.upgrades[0].upgrade_id == "iron_strapping"
        assert loaded.captain.ship.upgrades[0].installed_day == 3
        assert loaded.captain.ship.upgrades[1].upgrade_id == "lateen_rigging"
        assert loaded.captain.ship.upgrade_slots == 4

    def test_round_trip_ship_no_upgrades(self, tmp_path: Path):
        world = new_game("Sailor")
        save_game(world, base_path=tmp_path)
        loaded, *_ = load_game(base_path=tmp_path)
        assert loaded.captain.ship.upgrades == []
        assert loaded.captain.ship.upgrade_slots == 2  # sloop default

    def test_save_version_is_current(self):
        assert CURRENT_SAVE_VERSION >= 7


# ---------------------------------------------------------------------------
# Migration v6 → v7
# ---------------------------------------------------------------------------

class TestMigrationV6ToV7:
    def test_v6_string_upgrades_migrated(self):
        data = {
            "version": 6,
            "captain": {
                "ship": {
                    "template_id": "coastal_sloop",
                    "name": "Test",
                    "hull": 60, "hull_max": 60,
                    "cargo_capacity": 30, "speed": 8,
                    "crew": 5, "crew_max": 8,
                    "cannons": 0, "maneuver": 0.9,
                    "upgrades": ["iron_strapping", "lateen_rigging"],
                },
            },
        }
        migrated = migrate_save(data)
        assert migrated["version"] == CURRENT_SAVE_VERSION
        ship = migrated["captain"]["ship"]
        assert len(ship["upgrades"]) == 2
        assert ship["upgrades"][0] == {"upgrade_id": "iron_strapping", "installed_day": 0}
        assert ship["upgrades"][1] == {"upgrade_id": "lateen_rigging", "installed_day": 0}
        assert ship["upgrade_slots"] == 2

    def test_v6_empty_upgrades_migrated(self):
        data = {
            "version": 6,
            "captain": {
                "ship": {
                    "template_id": "trade_brigantine",
                    "name": "Test",
                    "hull": 100, "hull_max": 100,
                    "cargo_capacity": 80, "speed": 6,
                    "crew": 10, "crew_max": 20,
                    "cannons": 6, "maneuver": 0.5,
                    "upgrades": [],
                },
            },
        }
        migrated = migrate_save(data)
        assert migrated["version"] == CURRENT_SAVE_VERSION
        assert migrated["captain"]["ship"]["upgrades"] == []
        assert migrated["captain"]["ship"]["upgrade_slots"] == 2

    def test_v6_no_ship_migrated(self):
        data = {
            "version": 6,
            "captain": {},
        }
        migrated = migrate_save(data)
        assert migrated["version"] == CURRENT_SAVE_VERSION
