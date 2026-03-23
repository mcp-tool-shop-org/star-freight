"""Tests for convoy mechanics — fleet ships sailing together."""

from portlight.engine.models import (
    OwnedShip,
    VoyageStatus,
)
from portlight.content.ships import SHIPS, create_ship_from_template
from portlight.content.world import new_game
from portlight.engine.voyage import advance_day, arrive, depart
import random


def _make_fleet_ship(template_id="trade_brigantine", name="Escort", port_id="porto_novo") -> OwnedShip:
    ship = create_ship_from_template(SHIPS[template_id])
    ship.name = name
    return OwnedShip(ship=ship, docked_port_id=port_id)


class TestConvoyDepart:
    def test_fleet_ships_join_convoy(self):
        world = new_game("Admiral")
        world.captain.fleet = [_make_fleet_ship(port_id="porto_novo")]
        depart(world, "al_manar")
        # Fleet ship should be in transit (docked_port_id = "")
        assert world.captain.fleet[0].docked_port_id == ""

    def test_fleet_ships_at_different_port_stay(self):
        world = new_game("Admiral")
        world.captain.fleet = [_make_fleet_ship(port_id="silva_bay")]
        depart(world, "al_manar")
        # Ship at Silva Bay should NOT join convoy
        assert world.captain.fleet[0].docked_port_id == "silva_bay"

    def test_mixed_fleet_only_local_joins(self):
        world = new_game("Admiral")
        world.captain.fleet = [
            _make_fleet_ship(name="Local", port_id="porto_novo"),
            _make_fleet_ship(name="Remote", port_id="silva_bay"),
        ]
        depart(world, "al_manar")
        assert world.captain.fleet[0].docked_port_id == ""  # joined
        assert world.captain.fleet[1].docked_port_id == "silva_bay"  # stayed


class TestConvoyArrive:
    def test_convoy_ships_dock_at_destination(self):
        world = new_game("Admiral")
        world.captain.fleet = [_make_fleet_ship(port_id="porto_novo")]
        depart(world, "al_manar")
        # Simulate voyage completion
        world.voyage.progress = world.voyage.distance
        world.voyage.status = VoyageStatus.ARRIVED
        arrive(world)
        assert world.captain.fleet[0].docked_port_id == "al_manar"


class TestConvoySpeed:
    def test_convoy_speed_limited_by_slowest(self):
        world = new_game("Admiral")
        # Flagship is sloop (speed 8), add a galleon (speed 4) to convoy
        galleon = _make_fleet_ship(template_id="merchant_galleon", port_id="porto_novo")
        world.captain.fleet = [galleon]
        depart(world, "al_manar")

        # Track progress with convoy vs without
        rng = random.Random(42)
        advance_day(world, rng)
        # Progress should be limited by galleon speed (4) not sloop speed (8)
        # Can't assert exact value due to events, but progress should be small
        assert world.voyage.progress <= 6  # galleon speed 4 + navigator bonus at most


class TestConvoyDamage:
    def test_convoy_ships_take_storm_damage(self):
        world = new_game("Admiral")
        escort = _make_fleet_ship(port_id="porto_novo")
        world.captain.fleet = [escort]
        depart(world, "al_manar")

        # Run multiple days to hit a storm
        damaged = False
        for seed in range(100):
            world2 = new_game("Admiral")
            e2 = _make_fleet_ship(port_id="porto_novo")
            world2.captain.fleet = [e2]
            depart(world2, "al_manar")
            advance_day(world2, random.Random(seed))
            if e2.ship.hull < e2.ship.hull_max:
                damaged = True
                break

        assert damaged, "Convoy ship should take storm damage in at least one of 100 seeds"
