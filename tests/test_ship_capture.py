"""Tests for ship capture — prize-taking from naval victories."""

from portlight.engine.models import (
    Captain,
    EncounterState,
    OwnedShip,
    Ship,
    max_fleet_size,
)
from portlight.engine.encounter import (
    can_capture_prize,
    capture_prize,
    prize_template_id,
)
from portlight.content.ships import SHIPS


def _make_ship(template_id="trade_brigantine", name="Test Ship", **kw) -> Ship:
    defaults = dict(
        template_id=template_id, name=name,
        hull=100, hull_max=100, cargo_capacity=80,
        speed=6.0, crew=15, crew_max=20,
        cannons=6, maneuver=0.5, upgrade_slots=4,
    )
    defaults.update(kw)
    return Ship(**defaults)


def _make_encounter(strength=5, hull=30, crew=5) -> EncounterState:
    return EncounterState(
        enemy_captain_id="pirate_1",
        enemy_captain_name="Blackjack",
        enemy_faction_id="faction_1",
        enemy_strength=strength,
        enemy_ship_hull=hull,
        enemy_ship_hull_max=100,
        enemy_ship_cannons=4,
        enemy_ship_maneuver=0.5,
        enemy_ship_speed=6.0,
        enemy_ship_crew=crew,
        enemy_ship_crew_max=15,
        phase="resolved",
    )


# ---------------------------------------------------------------------------
# Prize template mapping
# ---------------------------------------------------------------------------

class TestPrizeTemplateMapping:
    def test_low_strength_sloop(self):
        assert prize_template_id(1) == "coastal_sloop"
        assert prize_template_id(3) == "coastal_sloop"

    def test_mid_strength_cutter(self):
        assert prize_template_id(4) == "swift_cutter"
        assert prize_template_id(5) == "swift_cutter"

    def test_high_strength_brigantine(self):
        assert prize_template_id(6) == "trade_brigantine"
        assert prize_template_id(7) == "trade_brigantine"

    def test_max_strength_galleon(self):
        assert prize_template_id(8) == "merchant_galleon"
        assert prize_template_id(9) == "merchant_galleon"
        assert prize_template_id(10) == "merchant_galleon"


# ---------------------------------------------------------------------------
# Can capture
# ---------------------------------------------------------------------------

class TestCanCapture:
    def test_can_capture_with_enough_crew(self):
        cap = Captain(name="Test", silver=1000)
        cap.ship = _make_ship(crew=20)
        enc = _make_encounter(strength=5)
        can, reason = can_capture_prize(cap, enc, max_fleet_size(0))
        assert can
        assert reason == ""

    def test_cannot_capture_fleet_full(self):
        cap = Captain(name="Test", silver=1000)
        cap.ship = _make_ship(crew=20)
        cap.fleet = [OwnedShip(ship=_make_ship(name="Docked"), docked_port_id="porto_novo")]
        enc = _make_encounter(strength=5)
        # Fleet limit = 2 (trust=0), already have 2 ships (1 flagship + 1 fleet)
        can, reason = can_capture_prize(cap, enc, max_fleet_size(0))
        assert not can
        assert "full" in reason.lower()

    def test_cannot_capture_insufficient_crew(self):
        cap = Captain(name="Test", silver=1000)
        cap.ship = _make_ship(template_id="trade_brigantine", crew=3)  # brigantine min=8
        enc = _make_encounter(strength=5)  # cutter min=5 → need 13 total
        can, reason = can_capture_prize(cap, enc, max_fleet_size(20))
        assert not can
        assert "crew" in reason.lower()


# ---------------------------------------------------------------------------
# Capture prize
# ---------------------------------------------------------------------------

class TestCapturePrize:
    def test_capture_creates_owned_ship(self):
        cap = Captain(name="Test", silver=1000)
        cap.ship = _make_ship(crew=20)
        enc = _make_encounter(strength=5, hull=30)
        owned = capture_prize(cap, enc, crew_to_prize=5)
        assert isinstance(owned, OwnedShip)
        assert owned.ship.template_id == "swift_cutter"
        assert owned.ship.hull == 30  # combat-end hull
        assert owned.ship.crew == 5
        assert cap.ship.crew == 15  # 20 - 5

    def test_capture_hull_capped_at_template_max(self):
        cap = Captain(name="Test", silver=1000)
        cap.ship = _make_ship(crew=20)
        enc = _make_encounter(strength=2, hull=200)  # sloop max=60
        owned = capture_prize(cap, enc, crew_to_prize=3)
        assert owned.ship.hull <= SHIPS["coastal_sloop"].hull_max

    def test_capture_prize_name(self):
        cap = Captain(name="Test", silver=1000)
        cap.ship = _make_ship(crew=20)
        enc = _make_encounter(strength=5)
        enc.enemy_captain_name = "Red Roger"
        owned = capture_prize(cap, enc, crew_to_prize=5)
        assert "Red Roger" in owned.ship.name

    def test_capture_no_upgrades(self):
        cap = Captain(name="Test", silver=1000)
        cap.ship = _make_ship(crew=20)
        enc = _make_encounter(strength=7)
        owned = capture_prize(cap, enc, crew_to_prize=8)
        assert owned.ship.upgrades == []

    def test_capture_sale_value(self):
        """Prize ships sell for 30% of template price * hull ratio."""
        cap = Captain(name="Test", silver=1000)
        cap.ship = _make_ship(crew=20)
        enc = _make_encounter(strength=5, hull=50)  # cutter template
        owned = capture_prize(cap, enc, crew_to_prize=5)
        from portlight.engine.fleet import sell_docked_ship
        owned.docked_port_id = "porto_novo"
        cap.fleet.append(owned)
        result = sell_docked_ship(cap, owned.ship.name, "porto_novo")
        assert isinstance(result, tuple)
        silver_gained, _ = result
        # Cutter price=450, 30% = 135, hull ratio varies
        assert 0 < silver_gained <= 135
