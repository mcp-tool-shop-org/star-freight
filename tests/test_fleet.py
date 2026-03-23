"""Tests for fleet management — multi-ship ownership."""

from pathlib import Path

from portlight.engine.models import (
    Captain,
    CargoItem,
    OwnedShip,
    Ship,
    max_fleet_size,
)
from portlight.engine.fleet import (
    board_ship,
    dock_ship,
    fleet_daily_wages,
    sell_docked_ship,
    transfer_cargo,
)
from portlight.content.ships import SHIPS, create_ship_from_template
from portlight.content.world import new_game
from portlight.engine.save import (
    CURRENT_SAVE_VERSION,
    load_game,
    migrate_save,
    save_game,
)


def _make_ship(template_id="trade_brigantine", name="Test Ship", **kw) -> Ship:
    defaults = dict(
        template_id=template_id, name=name,
        hull=100, hull_max=100, cargo_capacity=80,
        speed=6.0, crew=15, crew_max=20,
        cannons=6, maneuver=0.5, upgrade_slots=4,
    )
    defaults.update(kw)
    return Ship(**defaults)


# ---------------------------------------------------------------------------
# Fleet size limits
# ---------------------------------------------------------------------------

class TestFleetSizeLimits:
    def test_low_trust_allows_2(self):
        assert max_fleet_size(0) == 2
        assert max_fleet_size(10) == 2

    def test_mid_trust_allows_3(self):
        assert max_fleet_size(11) == 3
        assert max_fleet_size(25) == 3

    def test_high_trust_allows_5(self):
        assert max_fleet_size(26) == 5
        assert max_fleet_size(100) == 5


# ---------------------------------------------------------------------------
# Dock and board
# ---------------------------------------------------------------------------

class TestDockAndBoard:
    def _captain_with_fleet(self) -> Captain:
        cap = Captain(name="Test", silver=1000)
        cap.ship = _make_ship(name="Flagship")
        cap.cargo = [CargoItem("grain", 10)]
        cap.fleet = [
            OwnedShip(
                ship=_make_ship(name="Docked One", template_id="swift_cutter"),
                docked_port_id="porto_novo",
                cargo=[CargoItem("silk", 5)],
            ),
        ]
        return cap

    def test_dock_ship_swaps_flagship(self):
        cap = self._captain_with_fleet()
        err = dock_ship(cap, "porto_novo")
        assert err is None
        assert cap.ship.name == "Docked One"
        assert cap.cargo[0].good_id == "silk"
        assert cap.fleet[0].ship.name == "Flagship"
        assert cap.fleet[0].cargo[0].good_id == "grain"

    def test_dock_ship_no_other_ship(self):
        cap = Captain(name="Test", silver=1000)
        cap.ship = _make_ship(name="Flagship")
        cap.fleet = []
        err = dock_ship(cap, "porto_novo")
        assert err is not None

    def test_dock_ship_wrong_port(self):
        cap = self._captain_with_fleet()
        err = dock_ship(cap, "al_manar")
        assert err is not None

    def test_board_ship_by_name(self):
        cap = self._captain_with_fleet()
        err = board_ship(cap, "Docked One", "porto_novo")
        assert err is None
        assert cap.ship.name == "Docked One"
        assert cap.fleet[0].ship.name == "Flagship"

    def test_board_ship_not_found(self):
        cap = self._captain_with_fleet()
        err = board_ship(cap, "Nonexistent", "porto_novo")
        assert err is not None


# ---------------------------------------------------------------------------
# Cargo transfer
# ---------------------------------------------------------------------------

class TestCargoTransfer:
    def _captain_with_fleet(self) -> Captain:
        cap = Captain(name="Test", silver=1000)
        cap.ship = _make_ship(name="Flagship", cargo_capacity=80)
        cap.cargo = [CargoItem("grain", 20, cost_basis=200, acquired_port="porto_novo")]
        cap.fleet = [
            OwnedShip(
                ship=_make_ship(name="Storage", cargo_capacity=80),
                docked_port_id="porto_novo",
                cargo=[],
            ),
        ]
        return cap

    def test_transfer_cargo_between_ships(self):
        cap = self._captain_with_fleet()
        err = transfer_cargo(cap, "grain", 10, "Flagship", "Storage", "porto_novo")
        assert err is None
        assert cap.cargo[0].quantity == 10
        assert cap.fleet[0].cargo[0].good_id == "grain"
        assert cap.fleet[0].cargo[0].quantity == 10

    def test_transfer_insufficient_cargo(self):
        cap = self._captain_with_fleet()
        err = transfer_cargo(cap, "grain", 100, "Flagship", "Storage", "porto_novo")
        assert err is not None

    def test_transfer_insufficient_space(self):
        cap = self._captain_with_fleet()
        cap.fleet[0].ship.cargo_capacity = 5
        err = transfer_cargo(cap, "grain", 10, "Flagship", "Storage", "porto_novo")
        assert err is not None

    def test_transfer_nonexistent_good(self):
        cap = self._captain_with_fleet()
        err = transfer_cargo(cap, "silk", 5, "Flagship", "Storage", "porto_novo")
        assert err is not None


# ---------------------------------------------------------------------------
# Sell docked ship
# ---------------------------------------------------------------------------

class TestSellDockedShip:
    def test_sell_docked_ship(self):
        cap = Captain(name="Test", silver=100)
        cap.ship = _make_ship(name="Flagship")
        brig = create_ship_from_template(SHIPS["trade_brigantine"])
        brig.name = "For Sale"
        cap.fleet = [OwnedShip(ship=brig, docked_port_id="porto_novo")]
        result = sell_docked_ship(cap, "For Sale", "porto_novo")
        assert isinstance(result, tuple)
        silver_gained, name = result
        assert silver_gained > 0
        assert name == "For Sale"
        assert len(cap.fleet) == 0

    def test_sell_ship_with_cargo_blocked(self):
        cap = Captain(name="Test", silver=100)
        cap.ship = _make_ship(name="Flagship")
        cap.fleet = [OwnedShip(
            ship=_make_ship(name="Loaded"),
            docked_port_id="porto_novo",
            cargo=[CargoItem("grain", 10)],
        )]
        result = sell_docked_ship(cap, "Loaded", "porto_novo")
        assert isinstance(result, str)
        assert "cargo" in result.lower()

    def test_sell_ship_not_found(self):
        cap = Captain(name="Test", silver=100)
        cap.ship = _make_ship(name="Flagship")
        cap.fleet = []
        result = sell_docked_ship(cap, "Ghost", "porto_novo")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Fleet daily wages
# ---------------------------------------------------------------------------

class TestFleetWages:
    def test_no_fleet_no_extra_wages(self):
        cap = Captain(name="Test")
        cap.fleet = []
        assert fleet_daily_wages(cap) == 0

    def test_docked_crews_cost_wages(self):
        cap = Captain(name="Test")
        brig = create_ship_from_template(SHIPS["trade_brigantine"])
        brig.crew = 10
        cap.fleet = [OwnedShip(ship=brig, docked_port_id="porto_novo")]
        wages = fleet_daily_wages(cap)
        assert wages == 20  # brigantine daily_wage=2 * 10 crew


# ---------------------------------------------------------------------------
# Save/load with fleet
# ---------------------------------------------------------------------------

class TestFleetSave:
    def test_round_trip_with_fleet(self, tmp_path: Path):
        world = new_game("Admiral")
        brig = create_ship_from_template(SHIPS["trade_brigantine"])
        brig.name = "Reserve Ship"
        world.captain.fleet = [
            OwnedShip(
                ship=brig,
                docked_port_id="porto_novo",
                cargo=[CargoItem("silk", 5, cost_basis=350)],
            ),
        ]
        save_game(world, base_path=tmp_path)
        loaded, *_ = load_game(base_path=tmp_path)
        assert len(loaded.captain.fleet) == 1
        owned = loaded.captain.fleet[0]
        assert owned.ship.name == "Reserve Ship"
        assert owned.docked_port_id == "porto_novo"
        assert len(owned.cargo) == 1
        assert owned.cargo[0].good_id == "silk"

    def test_round_trip_empty_fleet(self, tmp_path: Path):
        world = new_game("Solo")
        save_game(world, base_path=tmp_path)
        loaded, *_ = load_game(base_path=tmp_path)
        assert loaded.captain.fleet == []

    def test_save_version_is_current(self):
        assert CURRENT_SAVE_VERSION >= 8


# ---------------------------------------------------------------------------
# Migration v7 → v8
# ---------------------------------------------------------------------------

class TestMigrationV7ToV8:
    def test_v7_gets_empty_fleet(self):
        data = {
            "version": 7,
            "captain": {
                "name": "Test",
                "ship": {
                    "template_id": "coastal_sloop",
                    "name": "Test", "hull": 60, "hull_max": 60,
                    "cargo_capacity": 30, "speed": 8,
                    "crew": 5, "crew_max": 8,
                    "cannons": 0, "maneuver": 0.9,
                    "upgrades": [], "upgrade_slots": 2,
                },
            },
        }
        migrated = migrate_save(data)
        assert migrated["version"] == CURRENT_SAVE_VERSION
        assert migrated["captain"]["fleet"] == []
