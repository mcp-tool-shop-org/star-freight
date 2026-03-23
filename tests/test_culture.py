"""Tests for the cultural content system."""

import random

from portlight.content.culture import PORT_CULTURES, REGION_CULTURES
from portlight.content.goods import GOODS
from portlight.content.ports import PORTS
from portlight.content.routes import ROUTES
from portlight.engine.culture_engine import (
    ArrivalFlavor,
    activate_festival,
    check_festival_trigger,
    check_forbidden_good_penalty,
    check_sacred_good_bonus,
    expire_festivals,
    generate_arrival_flavor,
    get_cultural_good_note,
    record_cultural_encounter,
    record_port_visit,
)
from portlight.engine.models import CulturalState
from portlight.engine.narrative import _BEATS_BY_ID


class TestRegionCultures:
    """All 5 regions must have complete cultural identity."""

    EXPECTED_REGIONS = [
        "Mediterranean", "North Atlantic", "West Africa",
        "East Indies", "South Seas",
    ]

    def test_all_regions_defined(self):
        for region in self.EXPECTED_REGIONS:
            assert region in REGION_CULTURES, f"Missing culture for {region}"

    def test_no_extra_regions(self):
        for region in REGION_CULTURES:
            assert region in self.EXPECTED_REGIONS, f"Unexpected culture: {region}"

    def test_region_ids_unique(self):
        ids = [rc.id for rc in REGION_CULTURES.values()]
        assert len(ids) == len(set(ids))

    def test_sacred_goods_valid(self):
        for name, rc in REGION_CULTURES.items():
            for gid in rc.sacred_goods:
                assert gid in GOODS, f"{name} sacred good '{gid}' not in GOODS"

    def test_forbidden_goods_valid(self):
        for name, rc in REGION_CULTURES.items():
            for gid in rc.forbidden_goods:
                assert gid in GOODS, f"{name} forbidden good '{gid}' not in GOODS"

    def test_prized_goods_valid(self):
        for name, rc in REGION_CULTURES.items():
            for gid in rc.prized_goods:
                assert gid in GOODS, f"{name} prized good '{gid}' not in GOODS"

    def test_all_regions_have_text_fields(self):
        for name, rc in REGION_CULTURES.items():
            assert rc.cultural_name, f"{name} missing cultural_name"
            assert rc.ethos, f"{name} missing ethos"
            assert rc.trade_philosophy, f"{name} missing trade_philosophy"
            assert rc.greeting, f"{name} missing greeting"
            assert rc.farewell, f"{name} missing farewell"
            assert rc.proverb, f"{name} missing proverb"

    def test_all_regions_have_weather_flavor(self):
        for name, rc in REGION_CULTURES.items():
            assert len(rc.weather_flavor) >= 3, f"{name} needs >=3 weather_flavor"

    def test_all_regions_have_festivals(self):
        for name, rc in REGION_CULTURES.items():
            assert len(rc.festivals) >= 1, f"{name} needs at least 1 festival"


class TestFestivals:
    """Festivals must reference valid goods and have sane values."""

    def test_festival_ids_unique(self):
        all_ids = []
        for rc in REGION_CULTURES.values():
            for f in rc.festivals:
                all_ids.append(f.id)
        assert len(all_ids) == len(set(all_ids))

    def test_festival_market_effects_valid(self):
        for rc in REGION_CULTURES.values():
            for f in rc.festivals:
                for gid in f.market_effects:
                    assert gid in GOODS, f"Festival '{f.id}' references unknown good '{gid}'"

    def test_festival_market_effects_positive(self):
        for rc in REGION_CULTURES.values():
            for f in rc.festivals:
                for gid, mult in f.market_effects.items():
                    assert mult > 0, f"Festival '{f.id}' has non-positive multiplier for '{gid}'"

    def test_festival_frequency_sane(self):
        for rc in REGION_CULTURES.values():
            for f in rc.festivals:
                assert 30 <= f.frequency_days <= 180, (
                    f"Festival '{f.id}' frequency {f.frequency_days} outside 30-180 range"
                )

    def test_festival_duration_sane(self):
        for rc in REGION_CULTURES.values():
            for f in rc.festivals:
                assert 1 <= f.duration_days <= 10, (
                    f"Festival '{f.id}' duration {f.duration_days} outside 1-10 range"
                )

    def test_festival_region_matches_parent(self):
        for rc in REGION_CULTURES.values():
            for f in rc.festivals:
                assert f.region == rc.region_name, (
                    f"Festival '{f.id}' region '{f.region}' != parent '{rc.region_name}'"
                )


class TestPortCultures:
    """All 20 ports must have cultural flavor entries."""

    def test_all_ports_have_culture(self):
        for port_id in PORTS:
            assert port_id in PORT_CULTURES, f"Missing PortCulture for '{port_id}'"

    def test_no_extra_port_cultures(self):
        for port_id in PORT_CULTURES:
            assert port_id in PORTS, f"PortCulture for unknown port '{port_id}'"

    def test_port_cultures_have_text(self):
        for port_id, pc in PORT_CULTURES.items():
            assert pc.landmark, f"{port_id} missing landmark"
            assert pc.local_custom, f"{port_id} missing local_custom"
            assert pc.atmosphere, f"{port_id} missing atmosphere"
            assert pc.dock_scene, f"{port_id} missing dock_scene"
            assert pc.tavern_rumor, f"{port_id} missing tavern_rumor"

    def test_port_cultures_have_groups(self):
        for port_id, pc in PORT_CULTURES.items():
            assert pc.cultural_group, f"{port_id} missing cultural_group"
            assert pc.cultural_group_description, f"{port_id} missing cultural_group_description"

    def test_cultural_group_names_unique(self):
        names = [pc.cultural_group for pc in PORT_CULTURES.values()]
        assert len(names) == len(set(names)), "Duplicate cultural_group names"


class TestArrivalFlavor:
    """Arrival flavor generation for all ports."""

    def test_all_ports_generate_flavor(self):
        cs = CulturalState()
        for port_id, port in PORTS.items():
            flavor = generate_arrival_flavor(port_id, port.region, 10, 1, cs)
            assert flavor is not None, f"No arrival flavor for {port_id}"
            assert isinstance(flavor, ArrivalFlavor)

    def test_standing_affects_greeting(self):
        cs = CulturalState()
        low = generate_arrival_flavor("porto_novo", "Mediterranean", -5, 1, cs)
        high = generate_arrival_flavor("porto_novo", "Mediterranean", 25, 1, cs)
        assert low is not None and high is not None
        assert low.greeting != high.greeting

    def test_unknown_port_returns_none(self):
        cs = CulturalState()
        assert generate_arrival_flavor("nonexistent", "Mediterranean", 10, 1, cs) is None


class TestFestivalEngine:
    """Festival triggering and expiry."""

    def test_festival_can_trigger(self):
        cs = CulturalState()
        # Run many checks to ensure at least one triggers
        triggered = False
        for _ in range(500):
            result = check_festival_trigger("Mediterranean", 30, random.Random(), cs)
            if result:
                triggered = True
                break
        assert triggered, "No festival triggered in 500 attempts"

    def test_activate_and_expire(self):
        cs = CulturalState()
        rc = REGION_CULTURES["Mediterranean"]
        festival = rc.festivals[0]
        af = activate_festival(festival, "porto_novo", 10, cs)
        assert len(cs.active_festivals) == 1
        assert af.start_day == 10
        assert af.end_day == 10 + festival.duration_days

        # Not expired yet
        expired = expire_festivals(11, cs)
        assert len(expired) == 0
        assert len(cs.active_festivals) == 1

        # Now expire
        expired = expire_festivals(10 + festival.duration_days + 1, cs)
        assert len(expired) == 1
        assert len(cs.active_festivals) == 0

    def test_no_double_trigger(self):
        cs = CulturalState()
        rc = REGION_CULTURES["Mediterranean"]
        festival = rc.festivals[0]
        activate_festival(festival, "porto_novo", 10, cs)
        # Should not trigger same festival again
        for _ in range(200):
            result = check_festival_trigger("Mediterranean", 15, random.Random(), cs)
            for f, _ in result:
                assert f.id != festival.id, "Festival triggered while already active"


class TestCulturalState:
    """CulturalState tracking."""

    def test_record_port_visit(self):
        cs = CulturalState()
        record_port_visit("porto_novo", "Mediterranean", cs)
        assert cs.port_visits["porto_novo"] == 1
        assert "Mediterranean" in cs.regions_entered

    def test_record_port_visit_increment(self):
        cs = CulturalState()
        record_port_visit("porto_novo", "Mediterranean", cs)
        record_port_visit("porto_novo", "Mediterranean", cs)
        assert cs.port_visits["porto_novo"] == 2
        assert cs.regions_entered.count("Mediterranean") == 1

    def test_record_cultural_encounter(self):
        cs = CulturalState()
        record_cultural_encounter(cs)
        record_cultural_encounter(cs)
        assert cs.cultural_encounters == 2


class TestCulturalNarrativeBeats:
    """Cultural narrative beats exist and are well-formed."""

    CULTURAL_BEAT_IDS = [
        "cultural_awakening", "festival_trader", "sacred_cargo",
        "forbidden_trade", "cultural_bridge", "festival_patron",
        "the_known_world_culture", "proverb_collector",
    ]

    def test_all_cultural_beats_defined(self):
        for beat_id in self.CULTURAL_BEAT_IDS:
            assert beat_id in _BEATS_BY_ID, f"Missing narrative beat: {beat_id}"

    def test_cultural_beats_have_text(self):
        for beat_id in self.CULTURAL_BEAT_IDS:
            beat = _BEATS_BY_ID[beat_id]
            assert beat.title, f"{beat_id} missing title"
            assert beat.text, f"{beat_id} missing text"


class TestRouteLore:
    """Named routes should have lore text."""

    def test_key_routes_have_lore(self):
        named = [r for r in ROUTES if r.lore_name]
        assert len(named) >= 10, f"Only {len(named)} named routes, expected >= 10"

    def test_lore_routes_have_text(self):
        for r in ROUTES:
            if r.lore_name:
                assert r.lore, f"Route '{r.lore_name}' has name but no lore text"

    def test_lore_names_unique(self):
        names = [r.lore_name for r in ROUTES if r.lore_name]
        assert len(names) == len(set(names)), "Duplicate lore_name values"


class TestCulturalGoodsEngine:
    """Sacred/forbidden good checks."""

    def test_grain_sacred_in_mediterranean(self):
        assert check_sacred_good_bonus("grain", "Mediterranean") > 0

    def test_medicines_sacred_in_north_atlantic(self):
        assert check_sacred_good_bonus("medicines", "North Atlantic") > 0

    def test_pearls_sacred_in_west_africa(self):
        assert check_sacred_good_bonus("pearls", "West Africa") > 0

    def test_weapons_forbidden_in_east_indies(self):
        assert check_forbidden_good_penalty("weapons", "East Indies") > 0

    def test_non_sacred_good_no_bonus(self):
        assert check_sacred_good_bonus("iron", "Mediterranean") == 0

    def test_non_forbidden_good_no_penalty(self):
        assert check_forbidden_good_penalty("silk", "East Indies") == 0

    def test_cultural_note_sacred(self):
        note = get_cultural_good_note("grain", "Mediterranean")
        assert note is not None
        assert "sacred" in note

    def test_cultural_note_forbidden(self):
        note = get_cultural_good_note("weapons", "East Indies")
        assert note is not None
        assert "forbidden" in note

    def test_cultural_note_prized(self):
        note = get_cultural_good_note("spice", "Mediterranean")
        assert note == "prized"

    def test_cultural_note_none_for_unremarkable(self):
        note = get_cultural_good_note("timber", "Mediterranean")
        assert note is None
