"""Tests for sea culture — route encounters, NPC sightings, lore, crew morale."""

from portlight.content.ports import PORTS
from portlight.content.routes import ROUTES
from portlight.content.sea_culture import (
    CREW_MOODS,
    NPC_SIGHTINGS,
    REGION_ENCOUNTERS,
    ROUTE_ENCOUNTERS,
    SEA_SUPERSTITIONS,
    WEATHER_NARRATIVES,
    get_crew_moods,
    get_npc_sightings,
    get_region_encounters,
    get_route_encounters,
    get_superstitions,
    get_weather_narrative,
)


class TestRouteEncounters:
    """All named routes must have encounter tables."""

    def test_all_named_routes_have_encounters(self):
        named = [r for r in ROUTES if r.lore_name]
        for route in named:
            table = get_route_encounters(route.lore_name)
            assert table is not None, f"Missing encounters for '{route.lore_name}'"

    def test_encounter_tables_not_empty(self):
        for name, table in ROUTE_ENCOUNTERS.items():
            assert len(table.encounters) >= 3, f"'{name}' needs >= 3 encounters, has {len(table.encounters)}"

    def test_encounters_have_text(self):
        for name, table in ROUTE_ENCOUNTERS.items():
            for enc in table.encounters:
                assert enc.text, f"Empty text in '{name}'"
                assert enc.category, f"Empty category in '{name}'"

    def test_encounter_categories_valid(self):
        valid = {"sighting", "lore", "weather", "crew", "encounter"}
        for name, table in ROUTE_ENCOUNTERS.items():
            for enc in table.encounters:
                assert enc.category in valid, f"Invalid category '{enc.category}' in '{name}'"

    def test_fifteen_named_routes(self):
        assert len(ROUTE_ENCOUNTERS) == 15


class TestRegionEncounters:
    """All 5 regions must have default encounters."""

    REGIONS = ["Mediterranean", "North Atlantic", "West Africa", "East Indies", "South Seas"]

    def test_all_regions_have_encounters(self):
        for region in self.REGIONS:
            table = get_region_encounters(region)
            assert table is not None, f"Missing region encounters for '{region}'"

    def test_region_tables_not_empty(self):
        for name, table in REGION_ENCOUNTERS.items():
            assert len(table.encounters) >= 3, f"'{name}' needs >= 3 encounters"

    def test_five_regions(self):
        assert len(REGION_ENCOUNTERS) == 5


class TestEncounterVariety:
    """Each route should have multiple encounter categories."""

    def test_long_routes_have_mixed_categories(self):
        """Routes with 5+ encounters should span multiple categories."""
        for name, table in ROUTE_ENCOUNTERS.items():
            if len(table.encounters) >= 5:
                cats = {e.category for e in table.encounters}
                assert len(cats) >= 3, f"'{name}' has {len(table.encounters)} encounters but only {len(cats)} categories"


class TestNPCSightings:
    """NPC sightings at sea for all 5 regions."""

    REGIONS = ["Mediterranean", "North Atlantic", "West Africa", "East Indies", "South Seas"]

    def test_all_regions_have_sightings(self):
        for region in self.REGIONS:
            sightings = get_npc_sightings(region)
            assert len(sightings) >= 3, f"'{region}' needs >= 3 NPC sightings"

    def test_sightings_reference_valid_ports(self):
        for region, sightings in NPC_SIGHTINGS.items():
            for s in sightings:
                assert s.port_id in PORTS, f"Sighting for '{s.npc_name}' references unknown port '{s.port_id}'"

    def test_sightings_have_text(self):
        for region, sightings in NPC_SIGHTINGS.items():
            for s in sightings:
                assert s.text, f"Empty text for '{s.npc_name}' sighting"
                assert s.npc_name, f"Empty npc_name in {region}"

    def test_sightings_match_region(self):
        for region, sightings in NPC_SIGHTINGS.items():
            for s in sightings:
                assert s.region == region, f"'{s.npc_name}' region mismatch: {s.region} != {region}"

    def test_total_sightings(self):
        total = sum(len(s) for s in NPC_SIGHTINGS.values())
        assert total >= 20, f"Need >= 20 total sightings, have {total}"


class TestSeaSuperstitions:
    """Sea lore and superstitions."""

    def test_superstitions_exist(self):
        assert len(get_superstitions()) >= 10

    def test_superstitions_have_text(self):
        for s in SEA_SUPERSTITIONS:
            assert s.text, f"Empty text for superstition '{s.id}'"
            assert s.crew_reaction, f"Empty crew_reaction for '{s.id}'"
            assert s.trigger, f"Empty trigger for '{s.id}'"

    def test_superstition_ids_unique(self):
        ids = [s.id for s in SEA_SUPERSTITIONS]
        assert len(ids) == len(set(ids))

    def test_first_region_superstitions(self):
        """Key regions should have first-entry superstitions."""
        triggers = {s.trigger for s in SEA_SUPERSTITIONS}
        assert "first_region_East Indies" in triggers
        assert "first_region_South Seas" in triggers


class TestCrewMoods:
    """Crew morale and voice system."""

    def test_moods_exist(self):
        assert len(get_crew_moods()) >= 8

    def test_moods_have_text(self):
        for mood in CREW_MOODS:
            assert mood.condition, f"Empty condition for '{mood.id}'"
            assert len(mood.flavor_texts) >= 1, f"'{mood.id}' needs at least 1 flavor text"

    def test_mood_ids_unique(self):
        ids = [m.id for m in CREW_MOODS]
        assert len(ids) == len(set(ids))

    def test_key_moods_exist(self):
        """Essential moods should be defined."""
        mood_ids = {m.id for m in CREW_MOODS}
        assert "prosperous" in mood_ids
        assert "struggling" in mood_ids
        assert "carrying_contraband" in mood_ids
        assert "first_voyage" in mood_ids
        assert "veteran" in mood_ids


class TestWeatherNarratives:
    """Seasonal weather narratives for all 20 region/season combos."""

    REGIONS = ["Mediterranean", "North Atlantic", "West Africa", "East Indies", "South Seas"]
    SEASONS = ["spring", "summer", "autumn", "winter"]

    def test_all_20_combinations_defined(self):
        for region in self.REGIONS:
            for season in self.SEASONS:
                narrative = get_weather_narrative(region, season)
                assert narrative is not None, f"Missing weather narrative: {region}/{season}"

    def test_twenty_total(self):
        assert len(WEATHER_NARRATIVES) == 20

    def test_all_have_departure_text(self):
        for key, n in WEATHER_NARRATIVES.items():
            assert n.departure_text, f"{key} missing departure_text"

    def test_all_have_mid_voyage_texts(self):
        for key, n in WEATHER_NARRATIVES.items():
            assert len(n.mid_voyage_texts) >= 3, f"{key} needs >= 3 mid_voyage_texts"

    def test_all_have_arrival_text(self):
        for key, n in WEATHER_NARRATIVES.items():
            assert n.arrival_text, f"{key} missing arrival_text"

    def test_all_have_night_text(self):
        for key, n in WEATHER_NARRATIVES.items():
            assert n.night_text, f"{key} missing night_text"

    def test_all_have_crew_reaction(self):
        for key, n in WEATHER_NARRATIVES.items():
            assert n.crew_weather_reaction, f"{key} missing crew_weather_reaction"

    def test_winter_atlantic_is_dramatic(self):
        n = get_weather_narrative("North Atlantic", "winter")
        assert n is not None
        assert len(n.mid_voyage_texts) >= 4, "Winter Atlantic should be the most described"

    def test_monsoon_is_dramatic(self):
        n = get_weather_narrative("East Indies", "summer")
        assert n is not None
        assert len(n.mid_voyage_texts) >= 4, "Monsoon should be extensively described"

    def test_south_seas_winter_is_peaceful(self):
        n = get_weather_narrative("South Seas", "winter")
        assert n is not None
        assert "peace" in n.crew_weather_reaction.lower() or "rest" in n.crew_weather_reaction.lower()
