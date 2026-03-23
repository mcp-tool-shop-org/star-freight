"""Tests for cultural voyage events."""

import random

from portlight.engine.models import Captain, CargoItem, Ship
from portlight.engine.voyage import (
    EventType,
    VoyageEvent,
    _EVENT_WEIGHTS,
    _pick_event,
    _resolve_event,
)


def _test_captain(captain_type: str = "merchant") -> Captain:
    return Captain(
        name="Test",
        captain_type=captain_type,
        silver=500,
        ship=Ship(
            template_id="brigantine_standard",
            name="Test Ship",
            hull=100,
            hull_max=100,
            cargo_capacity=80,
            speed=6.0,
            crew=8,
            crew_max=10,
        ),
        cargo=[CargoItem(good_id="grain", quantity=10)],
        provisions=30,
    )


class TestCulturalEventTypes:
    """All 8 cultural event types must exist and be weighted."""

    CULTURAL_TYPES = [
        EventType.FOREIGN_VESSEL,
        EventType.CULTURAL_WATERS,
        EventType.SEA_CEREMONY,
        EventType.WHALE_SIGHTING,
        EventType.LIGHTHOUSE,
        EventType.MUSICIAN_ABOARD,
        EventType.DRIFTING_OFFERING,
        EventType.STAR_NAVIGATION,
    ]

    def test_all_cultural_types_in_enum(self):
        for et in self.CULTURAL_TYPES:
            assert et in EventType

    def test_all_cultural_types_in_weights(self):
        weighted_types = {e for e, _ in _EVENT_WEIGHTS}
        for et in self.CULTURAL_TYPES:
            assert et in weighted_types, f"{et} missing from _EVENT_WEIGHTS"

    def test_cultural_weights_sum_reasonable(self):
        cultural_sum = sum(
            w for e, w in _EVENT_WEIGHTS if e in self.CULTURAL_TYPES
        )
        assert 0.08 <= cultural_sum <= 0.15, f"Cultural weight sum {cultural_sum} outside 8-15%"

    def test_nothing_weight_reduced(self):
        nothing_w = next(w for e, w in _EVENT_WEIGHTS if e == EventType.NOTHING)
        assert nothing_w < 0.35, "NOTHING should be reduced from original 35%"

    def test_total_weights_sum_to_1(self):
        total = sum(w for _, w in _EVENT_WEIGHTS)
        assert abs(total - 1.0) < 0.001


class TestCulturalEventResolution:
    """Each cultural event resolves without error and produces valid output."""

    def test_foreign_vessel_resolves(self):
        captain = _test_captain()
        event = _resolve_event(EventType.FOREIGN_VESSEL, random.Random(42), captain, captain.ship)
        assert event.event_type == EventType.FOREIGN_VESSEL
        assert event.message
        assert event.hull_delta == 0
        assert event.silver_delta == 0

    def test_cultural_waters_resolves(self):
        captain = _test_captain()
        event = _resolve_event(EventType.CULTURAL_WATERS, random.Random(42), captain, captain.ship)
        assert event.event_type == EventType.CULTURAL_WATERS
        assert event.message
        assert event.flavor

    def test_sea_ceremony_costs_provision(self):
        captain = _test_captain()
        event = _resolve_event(EventType.SEA_CEREMONY, random.Random(42), captain, captain.ship)
        assert event.event_type == EventType.SEA_CEREMONY
        assert event.provision_delta == -1

    def test_whale_sighting_no_effect(self):
        captain = _test_captain()
        event = _resolve_event(EventType.WHALE_SIGHTING, random.Random(42), captain, captain.ship)
        assert event.event_type == EventType.WHALE_SIGHTING
        assert event.hull_delta == 0
        assert event.silver_delta == 0
        assert event.provision_delta == 0
        assert event.speed_modifier == 1.0

    def test_lighthouse_speed_bonus(self):
        captain = _test_captain()
        event = _resolve_event(EventType.LIGHTHOUSE, random.Random(42), captain, captain.ship)
        assert event.event_type == EventType.LIGHTHOUSE
        assert event.speed_modifier == 1.1

    def test_musician_aboard_no_effect(self):
        captain = _test_captain()
        event = _resolve_event(EventType.MUSICIAN_ABOARD, random.Random(42), captain, captain.ship)
        assert event.event_type == EventType.MUSICIAN_ABOARD
        assert event.hull_delta == 0
        assert event.speed_modifier == 1.0

    def test_drifting_offering_no_effect(self):
        captain = _test_captain()
        event = _resolve_event(EventType.DRIFTING_OFFERING, random.Random(42), captain, captain.ship)
        assert event.event_type == EventType.DRIFTING_OFFERING
        assert event.hull_delta == 0

    def test_star_navigation_navigator_bonus(self):
        captain = _test_captain("navigator")
        event = _resolve_event(EventType.STAR_NAVIGATION, random.Random(42), captain, captain.ship)
        assert event.event_type == EventType.STAR_NAVIGATION
        assert event.speed_modifier == 1.2

    def test_star_navigation_non_navigator_bonus(self):
        captain = _test_captain("merchant")
        event = _resolve_event(EventType.STAR_NAVIGATION, random.Random(42), captain, captain.ship)
        assert event.event_type == EventType.STAR_NAVIGATION
        assert event.speed_modifier == 1.05


class TestVoyageEventFlavor:
    """Cultural events should have flavor text."""

    def test_flavor_field_exists(self):
        event = VoyageEvent(EventType.NOTHING, "test", flavor="some flavor")
        assert event.flavor == "some flavor"

    def test_flavor_defaults_empty(self):
        event = VoyageEvent(EventType.NOTHING, "test")
        assert event.flavor == ""

    def test_cultural_events_have_flavor(self):
        captain = _test_captain()
        rng = random.Random(42)
        cultural_types = [
            EventType.CULTURAL_WATERS,
            EventType.SEA_CEREMONY,
            EventType.WHALE_SIGHTING,
            EventType.LIGHTHOUSE,
            EventType.DRIFTING_OFFERING,
            EventType.STAR_NAVIGATION,
        ]
        for et in cultural_types:
            event = _resolve_event(et, rng, captain, captain.ship)
            assert event.flavor, f"{et} should have flavor text"


class TestCulturalEventPicking:
    """Cultural events should appear in the event picker."""

    def test_cultural_events_can_be_picked(self):
        """Over many picks, at least one cultural event should appear."""
        rng = random.Random(99)
        cultural = {
            EventType.FOREIGN_VESSEL, EventType.CULTURAL_WATERS,
            EventType.SEA_CEREMONY, EventType.WHALE_SIGHTING,
            EventType.LIGHTHOUSE, EventType.MUSICIAN_ABOARD,
            EventType.DRIFTING_OFFERING, EventType.STAR_NAVIGATION,
        }
        found = set()
        for _ in range(2000):
            et = _pick_event(0.1, rng)
            if et in cultural:
                found.add(et)
        assert len(found) >= 3, f"Only found {found} cultural events in 2000 picks"
