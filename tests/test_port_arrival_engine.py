"""Tests for port arrival engine — NPC greetings, dock scenes, weather."""

from portlight.content.world import new_game
from portlight.engine.captain_identity import CaptainType
from portlight.engine.port_arrival_engine import (
    PortArrivalExperience,
    format_arrival_text,
    generate_arrival,
)


def _make_world(captain_type: str = "merchant"):
    return new_game(captain_type=CaptainType(captain_type))


class TestArrivalExperience:
    """generate_arrival produces complete arrival data."""

    def test_porto_novo_has_dock_scene(self):
        world = _make_world()
        exp = generate_arrival(world, "porto_novo")
        assert exp.dock_scene, "Porto Novo should have a dock scene"

    def test_porto_novo_has_harbor_master(self):
        world = _make_world()
        exp = generate_arrival(world, "porto_novo")
        assert exp.harbor_master_name, "Porto Novo should have a harbor master"
        assert exp.harbor_master_greeting, "Harbor master should greet"

    def test_porto_novo_has_exchange(self):
        world = _make_world()
        exp = generate_arrival(world, "porto_novo")
        assert exp.exchange_name, "Porto Novo should have an exchange factor"

    def test_porto_novo_has_tavern(self):
        world = _make_world()
        exp = generate_arrival(world, "porto_novo")
        assert exp.tavern_name, "Porto Novo should have a tavern keeper"

    def test_porto_novo_has_culture(self):
        world = _make_world()
        exp = generate_arrival(world, "porto_novo")
        assert exp.local_custom
        assert exp.landmark
        assert exp.cultural_group

    def test_porto_novo_has_politics(self):
        world = _make_world()
        exp = generate_arrival(world, "porto_novo")
        assert exp.political_flavor

    def test_arrival_weather_exists(self):
        world = _make_world()
        exp = generate_arrival(world, "porto_novo")
        assert exp.arrival_weather, "Should have arrival weather text"

    def test_unknown_port_returns_minimal(self):
        world = _make_world()
        exp = generate_arrival(world, "nonexistent")
        assert exp.port_name == "Unknown"


class TestStandingAffectsGreetings:
    """NPC greetings change based on captain standing."""

    def test_merchant_gets_friendly_at_home(self):
        world = _make_world("merchant")
        # Merchant starts with 10 Med standing — should get friendly greetings
        exp = generate_arrival(world, "porto_novo")
        assert exp.harbor_master_greeting  # should have a greeting

    def test_low_standing_different_greeting(self):
        world = _make_world("merchant")
        # Tank standing
        world.captain.standing.regional_standing["Mediterranean"] = -10
        exp_hostile = generate_arrival(world, "porto_novo")
        # Reset standing
        world.captain.standing.regional_standing["Mediterranean"] = 20
        exp_friendly = generate_arrival(world, "porto_novo")
        # Greetings should differ
        assert exp_hostile.harbor_master_greeting != exp_friendly.harbor_master_greeting


class TestMentorGreeting:
    """Captain's mentor should greet them at home port."""

    def test_merchant_mentor_at_home(self):
        world = _make_world("merchant")
        exp = generate_arrival(world, "porto_novo")
        # Merchant's mentor is pn_marta (Marta Soares) at Porto Novo
        assert exp.mentor_name, "Merchant should have a mentor greeting at Porto Novo"

    def test_no_mentor_at_foreign_port(self):
        world = _make_world("merchant")
        exp = generate_arrival(world, "al_manar")
        # Merchant's mentor is at Porto Novo, not Al-Manar
        assert exp.mentor_greeting == ""

    def test_corsair_mentor_at_corsairs_rest(self):
        world = _make_world("corsair")
        exp = generate_arrival(world, "corsairs_rest")
        assert exp.mentor_name, "Corsair should have a mentor at Corsair's Rest"


class TestAllPortsHaveArrivals:
    """Every port should produce a non-empty arrival experience."""

    def test_all_20_ports_produce_arrivals(self):
        from portlight.content.ports import PORTS
        world = _make_world()
        for port_id in PORTS:
            exp = generate_arrival(world, port_id)
            assert exp.port_name != "Unknown", f"{port_id} returned unknown"
            assert exp.dock_scene, f"{port_id} missing dock_scene"
            assert exp.harbor_master_greeting or exp.landmark, f"{port_id} has no NPC or landmark"


class TestFormatArrivalText:
    """format_arrival_text produces readable output."""

    def test_basic_formatting(self):
        exp = PortArrivalExperience(
            port_id="test", port_name="Test Port", region="Mediterranean",
            dock_scene="Ships at dock.",
            harbor_master_greeting="Welcome.",
            harbor_master_name="Test HM",
        )
        lines = format_arrival_text(exp)
        assert any("Test Port" in line for line in lines)
        assert any("Welcome" in line for line in lines)

    def test_festival_banner(self):
        exp = PortArrivalExperience(
            port_id="test", port_name="Test Port", region="Mediterranean",
            active_festival_name="Test Festival",
            active_festival_description="A great celebration!",
        )
        lines = format_arrival_text(exp)
        assert any("FESTIVAL" in line for line in lines)
