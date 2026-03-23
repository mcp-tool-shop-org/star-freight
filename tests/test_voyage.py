"""Tests for the voyage engine — departure, travel, events, arrival."""

import random

from portlight.content.world import new_game
from portlight.engine.models import VoyageStatus
from portlight.engine.voyage import advance_day, arrive, depart, find_route


class TestRouteNetwork:
    def test_find_route_exists(self):
        world = new_game()
        route = find_route(world, "porto_novo", "al_manar")
        assert route is not None
        assert route.distance == 24

    def test_find_route_bidirectional(self):
        world = new_game()
        r1 = find_route(world, "porto_novo", "al_manar")
        r2 = find_route(world, "al_manar", "porto_novo")
        assert r1 is r2  # same route object

    def test_find_route_nonexistent(self):
        world = new_game()
        route = find_route(world, "porto_novo", "jade_port")
        assert route is None  # no direct route


class TestDeparture:
    def test_depart_success(self):
        world = new_game()
        result = depart(world, "al_manar")
        assert not isinstance(result, str)
        assert result.status == VoyageStatus.AT_SEA
        assert result.destination_id == "al_manar"

    def test_depart_no_route(self):
        world = new_game()
        result = depart(world, "jade_port")
        assert isinstance(result, str)
        assert "No route" in result

    def test_depart_same_port(self):
        world = new_game()
        result = depart(world, "porto_novo")
        assert isinstance(result, str)

    def test_depart_deducts_port_fee(self):
        world = new_game()
        silver_before = world.captain.silver
        port_fee = world.ports["porto_novo"].port_fee
        # Merchant pays 70% port fees (fee_mult=0.7)
        expected_fee = max(1, int(port_fee * 0.7))
        depart(world, "al_manar")
        assert world.captain.silver == silver_before - expected_fee

    def test_depart_insufficient_port_fee(self):
        world = new_game()
        world.captain.silver = 0
        result = depart(world, "al_manar")
        assert isinstance(result, str)
        assert "port fee" in result.lower()


class TestVoyageProgress:
    def test_advance_day_makes_progress(self):
        world = new_game()
        depart(world, "al_manar")
        rng = random.Random(42)
        events = advance_day(world, rng)
        assert len(events) > 0
        assert world.voyage.progress > 0
        assert world.voyage.days_elapsed == 1

    def test_provisions_consumed_daily(self):
        world = new_game()
        depart(world, "al_manar")
        provisions_before = world.captain.provisions
        advance_day(world, random.Random(42))
        assert world.captain.provisions < provisions_before

    def test_voyage_completes(self):
        world = new_game()
        depart(world, "silva_bay")  # short route, distance=16, speed=8
        rng = random.Random(1)
        # Should arrive in ~2 days (16/8) unless slowed
        for _ in range(10):
            advance_day(world, rng)
            if world.voyage.status == VoyageStatus.ARRIVED:
                break
        assert world.voyage.status == VoyageStatus.ARRIVED

    def test_arrival_sets_in_port(self):
        world = new_game()
        depart(world, "silva_bay")
        rng = random.Random(1)
        for _ in range(10):
            advance_day(world, rng)
            if world.voyage.status == VoyageStatus.ARRIVED:
                break
        result = arrive(world)
        assert result is None
        assert world.voyage.status == VoyageStatus.IN_PORT

    def test_day_counter_advances(self):
        world = new_game()
        depart(world, "al_manar")
        advance_day(world, random.Random(42))
        assert world.day == 2
        assert world.captain.day == 2


class TestVoyageEvents:
    def test_events_have_messages(self):
        world = new_game()
        depart(world, "al_manar")
        events = advance_day(world, random.Random(42))
        for e in events:
            assert len(e.message) > 0

    def test_storm_damages_hull(self):
        """Run enough voyages that we eventually get a storm."""
        world = new_game()
        depart(world, "al_manar")
        got_storm = False
        for seed in range(100):
            world_copy = new_game()
            depart(world_copy, "al_manar")
            events = advance_day(world_copy, random.Random(seed))
            for e in events:
                if e.event_type.value == "storm":
                    assert e.hull_delta < 0
                    got_storm = True
                    break
            if got_storm:
                break
        assert got_storm, "No storm event in 100 seeds"

    def test_starvation_when_no_provisions(self):
        world = new_game()
        world.captain.provisions = 0
        depart(world, "al_manar")
        events = advance_day(world, random.Random(42))
        # Should have a starvation event
        starvation = [e for e in events if "provisions" in e.message.lower() or "crew" in e.message.lower()]
        assert len(starvation) > 0

    def test_recent_events_tracked(self):
        """Voyage should track recent event types for dedup."""
        world = new_game()
        depart(world, "al_manar")
        advance_day(world, random.Random(42))
        assert len(world.voyage.recent_events) > 0
        assert len(world.voyage.recent_events) <= 5

    def test_recent_events_capped_at_5(self):
        """Recent events list should never exceed 5."""
        world = new_game()
        depart(world, "al_manar")
        for seed in range(10):
            advance_day(world, random.Random(seed))
            if world.voyage.status == VoyageStatus.ARRIVED:
                break
        assert len(world.voyage.recent_events) <= 5


# ---------------------------------------------------------------------------
# Next upgrade display
# ---------------------------------------------------------------------------

class TestInspectionFee:
    """Inspection fee should reflect what captain can actually pay."""

    def test_inspection_fee_capped_to_silver(self):
        """When captain has less silver than the fee, only take what they have."""
        from portlight.engine.voyage import _resolve_event, EventType
        world = new_game()
        depart(world, "al_manar")
        world.captain.silver = 3  # less than any possible fee (min 5)
        event = _resolve_event(
            EventType.INSPECTION, random.Random(42),
            world.captain, world.captain.ship,
            world=world, voyage=world.voyage,
        )
        assert event.silver_delta >= -3, \
            f"Fee should be capped to captain's 3 silver, got {event.silver_delta}"
        assert "only" in event.message.lower(), \
            "Message should note partial collection"

    def test_inspection_fee_full_when_affordable(self):
        """When captain can afford the fee, take the full amount."""
        from portlight.engine.voyage import _resolve_event, EventType
        world = new_game()
        depart(world, "al_manar")
        world.captain.silver = 500  # plenty
        event = _resolve_event(
            EventType.INSPECTION, random.Random(42),
            world.captain, world.captain.ship,
            world=world, voyage=world.voyage,
        )
        assert event.silver_delta < 0, "Should deduct silver"
        assert "only" not in event.message.lower(), \
            "Message should not mention partial collection"


class TestEncounterBypass:
    """Pirate encounters must block advancement until resolved."""

    def test_advance_blocked_when_pending_duel(self):
        """advance_day returns empty when a pirate encounter is pending."""
        world = new_game()
        depart(world, "al_manar")
        # Simulate a pending pirate encounter
        from portlight.engine.models import PendingDuel
        world.pirates.pending_duel = PendingDuel(
            captain_id="gnaw",
            captain_name="Gnaw",
            faction_id="red_tide",
            personality="aggressive",
            strength=3,
            region="West Africa",
        )
        progress_before = world.voyage.progress
        events = advance_day(world, random.Random(42))
        assert events == [], "advance_day should return no events with pending duel"
        assert world.voyage.progress == progress_before, "voyage should not progress"

    def test_advance_resumes_after_duel_cleared(self):
        """Once pending_duel is cleared, advancement resumes normally."""
        world = new_game()
        depart(world, "al_manar")
        from portlight.engine.models import PendingDuel
        world.pirates.pending_duel = PendingDuel(
            captain_id="gnaw",
            captain_name="Gnaw",
            faction_id="red_tide",
            personality="aggressive",
            strength=3,
            region="West Africa",
        )
        # Blocked
        events = advance_day(world, random.Random(42))
        assert events == []
        # Clear the encounter
        world.pirates.pending_duel = None
        # Now should advance
        events = advance_day(world, random.Random(42))
        assert len(events) > 0, "advance_day should produce events after duel cleared"
        assert world.voyage.progress > 0

    def test_pending_duel_not_overwritten(self):
        """A second advance must not overwrite the pending duel captain."""
        world = new_game()
        depart(world, "al_manar")
        from portlight.engine.models import PendingDuel
        world.pirates.pending_duel = PendingDuel(
            captain_id="gnaw",
            captain_name="Gnaw",
            faction_id="red_tide",
            personality="aggressive",
            strength=3,
            region="West Africa",
        )
        advance_day(world, random.Random(99))
        assert world.pirates.pending_duel.captain_id == "gnaw", \
            "pending duel should not be overwritten by advance"


class TestNextUpgrade:
    def test_next_upgrade_is_actually_upgrade(self):
        """_next_upgrade should return a ship costing more than current."""
        from portlight.app.views import _next_upgrade
        from portlight.content.ships import SHIPS
        from portlight.engine.models import Ship

        # Simulate a player with a Trade Brigantine (price 800)
        brig = SHIPS.get("trade_brigantine")
        assert brig is not None
        ship = Ship(template_id="trade_brigantine", hull=100, hull_max=100,
                    cargo_capacity=80, speed=6, cannons=8, maneuver=0.3,
                    crew=8, crew_max=20, name="Test Ship")
        upgrade = _next_upgrade(ship, 2000)
        assert upgrade is not None
        assert upgrade.price > brig.price, f"Got {upgrade.id} at {upgrade.price}, expected > {brig.price}"

    def test_no_downgrade_offered(self):
        """A galleon owner should not be offered a sloop."""
        from portlight.app.views import _next_upgrade
        from portlight.content.ships import SHIPS
        from portlight.engine.models import Ship

        galleon = SHIPS.get("merchant_galleon")
        assert galleon is not None
        ship = Ship(template_id="merchant_galleon", hull=160, hull_max=160,
                    cargo_capacity=150, speed=4, cannons=16, maneuver=0.2,
                    crew=15, crew_max=40, name="Big Ship")
        upgrade = _next_upgrade(ship, 5000)
        if upgrade:
            assert upgrade.price > galleon.price
