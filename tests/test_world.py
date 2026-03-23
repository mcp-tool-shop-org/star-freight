"""Tests for world creation and content integrity."""

from portlight.content.goods import GOODS
from portlight.content.ports import PORTS
from portlight.content.routes import ROUTES
from portlight.content.ships import SHIPS
from portlight.content.world import new_game
from portlight.engine.models import VoyageStatus


class TestContentIntegrity:
    def test_all_goods_have_positive_base_price(self):
        for good in GOODS.values():
            assert good.base_price > 0, f"{good.id} has non-positive price"

    def test_port_count(self):
        assert len(PORTS) == 20

    def test_good_count(self):
        assert len(GOODS) == 18  # 17 original + pelts

    def test_ship_count(self):
        assert len(SHIPS) == 5

    def test_all_port_goods_exist(self):
        """Every good_id in a port market must be in the GOODS table."""
        for port in PORTS.values():
            for slot in port.market:
                assert slot.good_id in GOODS, f"{port.id} references unknown good {slot.good_id}"

    def test_all_route_ports_exist(self):
        """Every port in a route must be in the PORTS table."""
        for route in ROUTES:
            assert route.port_a in PORTS, f"Route references unknown port {route.port_a}"
            assert route.port_b in PORTS, f"Route references unknown port {route.port_b}"

    def test_all_routes_have_positive_distance(self):
        for route in ROUTES:
            assert route.distance > 0

    def test_ship_progression_price_order(self):
        """Ships should get more expensive as they get bigger."""
        sloop = SHIPS["coastal_sloop"]
        cutter = SHIPS["swift_cutter"]
        brig = SHIPS["trade_brigantine"]
        galleon = SHIPS["merchant_galleon"]
        mow = SHIPS["royal_man_of_war"]
        assert sloop.price < cutter.price < brig.price < galleon.price < mow.price

    def test_ship_progression_capacity_order(self):
        sloop = SHIPS["coastal_sloop"]
        cutter = SHIPS["swift_cutter"]
        brig = SHIPS["trade_brigantine"]
        galleon = SHIPS["merchant_galleon"]
        mow = SHIPS["royal_man_of_war"]
        assert sloop.cargo_capacity < cutter.cargo_capacity < brig.cargo_capacity < galleon.cargo_capacity < mow.cargo_capacity


class TestNewGame:
    def test_creates_world(self):
        world = new_game("Hawk")
        assert world.captain.name == "Hawk"
        assert world.captain.silver == 550  # Merchant starting silver
        assert world.captain.ship is not None
        assert world.day == 1

    def test_starts_in_port(self):
        world = new_game()
        assert world.voyage is not None
        assert world.voyage.status == VoyageStatus.IN_PORT
        assert world.voyage.destination_id == "porto_novo"

    def test_starting_ship_is_sloop(self):
        world = new_game()
        assert world.captain.ship.template_id == "coastal_sloop"

    def test_prices_computed(self):
        world = new_game()
        for port in world.ports.values():
            for slot in port.market:
                assert slot.buy_price > 0, f"{port.id}/{slot.good_id} has no buy price"
                assert slot.sell_price > 0, f"{port.id}/{slot.good_id} has no sell price"

    def test_custom_starting_port(self):
        world = new_game(starting_port="jade_port")
        assert world.voyage.destination_id == "jade_port"
