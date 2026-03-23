"""Tests for the sea culture engine — wiring content into the voyage system."""

import random

from portlight.content.world import new_game
from portlight.engine.captain_identity import CaptainType
from portlight.engine.models import CulturalState, VoyageState, VoyageStatus
from portlight.engine.sea_culture_engine import (
    check_superstitions,
    enrich_voyage_day,
    get_arrival_weather,
    get_departure_weather,
    get_night_weather,
)
from portlight.engine.voyage import EventType, VoyageEvent, find_route


def _make_world(captain_type: str = "merchant"):
    ct = CaptainType(captain_type)
    world = new_game(captain_type=ct)
    # Put the captain at sea
    world.voyage = VoyageState(
        origin_id="porto_novo",
        destination_id="al_manar",
        distance=24,
        progress=5,
        days_elapsed=1,
        status=VoyageStatus.AT_SEA,
    )
    return world


class TestEnrichVoyageDay:
    """enrich_voyage_day adds flavor to base events."""

    def test_returns_base_events_unchanged(self):
        world = _make_world()
        base = [VoyageEvent(EventType.NOTHING, "An uneventful day.")]
        rng = random.Random(42)
        route = find_route(world, "porto_novo", "al_manar")
        enriched = enrich_voyage_day(world, route, base, rng)
        assert enriched[0] is base[0], "Base events should be preserved"

    def test_enrichment_adds_events(self):
        """Over many iterations, enrichment should add at least some flavor events."""
        world = _make_world()
        base = [VoyageEvent(EventType.NOTHING, "An uneventful day.")]
        route = find_route(world, "porto_novo", "al_manar")
        total_added = 0
        for seed in range(100):
            rng = random.Random(seed)
            enriched = enrich_voyage_day(world, route, base, rng)
            total_added += len(enriched) - 1  # subtract the base event
        assert total_added > 20, f"Expected flavor events over 100 iterations, got {total_added}"

    def test_named_route_gets_specific_encounters(self):
        """The Grain Road should produce Grain Road-specific encounters."""
        world = _make_world()
        base = [VoyageEvent(EventType.NOTHING, "Base.")]
        route = find_route(world, "porto_novo", "al_manar")
        assert route is not None
        assert route.lore_name == "The Grain Road"

        grain_encounters = 0
        for seed in range(200):
            rng = random.Random(seed)
            enriched = enrich_voyage_day(world, route, base, rng)
            for e in enriched[1:]:
                if "grain" in e.message.lower() or "exchange" in e.message.lower():
                    grain_encounters += 1
        assert grain_encounters > 0, "Grain Road should produce grain-themed encounters"

    def test_npc_sightings_appear(self):
        """NPC sightings should occasionally appear."""
        world = _make_world()
        base = [VoyageEvent(EventType.NOTHING, "Base.")]
        route = find_route(world, "porto_novo", "al_manar")
        npc_sightings = 0
        for seed in range(200):
            rng = random.Random(seed)
            enriched = enrich_voyage_day(world, route, base, rng)
            for e in enriched[1:]:
                if e.event_type == EventType.FOREIGN_VESSEL:
                    npc_sightings += 1
        assert npc_sightings > 0, "NPC sightings should appear"

    def test_weather_flavor_appears(self):
        """Weather flavor should occasionally appear."""
        world = _make_world()
        base = [VoyageEvent(EventType.NOTHING, "Base.")]
        route = find_route(world, "porto_novo", "al_manar")
        weather_events = 0
        for seed in range(200):
            rng = random.Random(seed)
            enriched = enrich_voyage_day(world, route, base, rng)
            for e in enriched[1:]:
                if e.flavor == "[weather]":
                    weather_events += 1
        assert weather_events > 0, "Weather flavor should appear"

    def test_crew_mood_appears(self):
        """Crew mood should appear when conditions match."""
        world = _make_world()
        # Make the captain rich to trigger "prosperous" mood
        world.captain.silver = 3000
        base = [VoyageEvent(EventType.NOTHING, "Base.")]
        route = find_route(world, "porto_novo", "al_manar")
        crew_events = 0
        for seed in range(200):
            rng = random.Random(seed)
            enriched = enrich_voyage_day(world, route, base, rng)
            for e in enriched[1:]:
                if e.flavor == "[crew]":
                    crew_events += 1
        assert crew_events > 0, "Crew mood should appear for prosperous captain"


class TestDepartureArrivalWeather:
    """Weather narrative for departure and arrival."""

    def test_departure_weather_exists(self):
        text = get_departure_weather("Mediterranean", 1)  # Spring
        assert text, "Should have departure weather for Med spring"

    def test_arrival_weather_exists(self):
        text = get_arrival_weather("East Indies", 150)  # Summer (monsoon)
        assert text, "Should have arrival weather for EI monsoon"

    def test_night_weather_exists(self):
        text = get_night_weather("South Seas", 350)  # Winter
        assert text, "Should have night weather for SS winter"

    def test_all_regions_have_departure(self):
        for region in ["Mediterranean", "North Atlantic", "West Africa", "East Indies", "South Seas"]:
            for day in [1, 100, 200, 300]:
                text = get_departure_weather(region, day)
                assert text, f"Missing departure weather for {region} day {day}"

    def test_unknown_region_returns_empty(self):
        text = get_departure_weather("Atlantis", 1)
        assert text == ""


class TestSuperstitions:
    """Sea superstitions fire correctly as one-time events."""

    def test_contraband_superstition_fires(self):
        world = _make_world()
        from portlight.engine.models import CargoItem
        world.captain.cargo.append(CargoItem(good_id="opium", quantity=5))
        cultural_state = CulturalState()
        fired_set: set[str] = set()
        result = check_superstitions(world, cultural_state, fired_set)
        contraband_fired = [s for s in result if s.id == "contraband_nerves"]
        assert len(contraband_fired) == 1

    def test_superstition_fires_only_once(self):
        world = _make_world()
        from portlight.engine.models import CargoItem
        world.captain.cargo.append(CargoItem(good_id="opium", quantity=5))
        cultural_state = CulturalState()
        fired_set: set[str] = set()
        result1 = check_superstitions(world, cultural_state, fired_set)
        result2 = check_superstitions(world, cultural_state, fired_set)
        # Should fire first time but not second
        assert len(result1) >= 1
        contraband_in_2 = [s for s in result2 if s.id == "contraband_nerves"]
        assert len(contraband_in_2) == 0

    def test_day_100_fires(self):
        world = _make_world()
        world._day_override = 100
        world.day = 100
        cultural_state = CulturalState()
        fired_set: set[str] = set()
        result = check_superstitions(world, cultural_state, fired_set)
        day_100 = [s for s in result if s.id == "hundredth_day"]
        assert len(day_100) == 1

    def test_all_regions_visited_fires(self):
        world = _make_world()
        cultural_state = CulturalState()
        cultural_state.regions_entered = [
            "Mediterranean", "North Atlantic", "West Africa",
            "East Indies", "South Seas",
        ]
        fired_set: set[str] = set()
        result = check_superstitions(world, cultural_state, fired_set)
        all_regions = [s for s in result if s.id == "fifth_region"]
        assert len(all_regions) == 1


class TestNoEnrichmentWhenNotAtSea:
    """Enrichment should handle edge cases gracefully."""

    def test_no_voyage_no_crash(self):
        world = _make_world()
        world.voyage = None
        base = [VoyageEvent(EventType.NOTHING, "Base.")]
        enriched = enrich_voyage_day(world, None, base, random.Random(42))
        assert len(enriched) >= 1  # at least the base event
