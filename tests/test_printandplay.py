"""Tests for the Star Freight Print-and-Play PDF generator."""

from __future__ import annotations

from pathlib import Path

import pytest


class TestAssets:
    """Test tabletop scaling constants."""

    def test_lane_burn_cost_tiers(self):
        from portlight.printandplay.assets import lane_burn_cost

        assert lane_burn_cost(2) == 1   # local hop
        assert lane_burn_cost(3) == 2   # cross-sector
        assert lane_burn_cost(4) == 3   # long haul
        assert lane_burn_cost(5) == 4   # deep run
        assert lane_burn_cost(1) == 1   # minimum

    def test_backward_compat_route_movement_cost(self):
        from portlight.printandplay.assets import route_movement_cost

        # route_movement_cost is an alias for lane_burn_cost
        assert route_movement_cost(2) == 1
        assert route_movement_cost(5) == 4

    def test_tabletop_price_scaling(self):
        from portlight.printandplay.assets import tabletop_price

        assert tabletop_price(80) == 8      # compact alloys
        assert tabletop_price(250) == 25    # bio-crystal
        assert tabletop_price(500) == 50    # ancestor tech
        assert tabletop_price(5) == 1       # minimum 1
        assert tabletop_price(0) == 1       # floor at 1

    def test_vessel_tabletop_all_present(self):
        from portlight.printandplay.assets import VESSEL_TABLETOP

        expected = {"rustbucket", "hauler", "runner", "warbird", "bulkframe"}
        assert set(VESSEL_TABLETOP.keys()) == expected

    def test_vessel_tabletop_posture_variety(self):
        from portlight.printandplay.assets import VESSEL_TABLETOP

        postures = {v["posture"] for v in VESSEL_TABLETOP.values()}
        # Each vessel supports a different captain life
        assert len(postures) == len(VESSEL_TABLETOP)

    def test_ship_tabletop_backward_compat(self):
        from portlight.printandplay.assets import SHIP_TABLETOP

        # SHIP_TABLETOP is derived from VESSEL_TABLETOP for backward compat
        assert len(SHIP_TABLETOP) == 5
        for ship_id, stats in SHIP_TABLETOP.items():
            assert "cargo" in stats
            assert "speed" in stats
            assert "hull" in stats
            assert "crew_cost" in stats
            assert "price" in stats
            assert "cannons" in stats

    def test_captain_tabletop_star_freight_archetypes(self):
        from portlight.printandplay.assets import CAPTAIN_TABLETOP

        assert "relief" in CAPTAIN_TABLETOP
        assert "gray" in CAPTAIN_TABLETOP
        assert "honor" in CAPTAIN_TABLETOP

        # Each captain has required fields
        for cap_id, cap in CAPTAIN_TABLETOP.items():
            assert "name" in cap
            assert "home_station" in cap
            assert "credits" in cap
            assert "fuel" in cap
            assert "heat" in cap
            assert "ability" in cap
            assert "weakness" in cap
            assert "life" in cap

    def test_sector_colors_all_civilizations(self):
        from portlight.printandplay.assets import SECTOR_COLORS

        expected = {"compact", "keth", "veshan", "orryn", "reach"}
        assert set(SECTOR_COLORS.keys()) == expected

    def test_region_colors_backward_compat(self):
        from portlight.printandplay.assets import REGION_COLORS, SECTOR_COLORS

        # REGION_COLORS is an alias for SECTOR_COLORS
        assert REGION_COLORS is SECTOR_COLORS

    def test_palette_not_ocean(self):
        """The palette should be industrial/political, not ocean blue."""
        from portlight.printandplay.assets import SECTOR_COLORS

        # No civilization should have a dominant blue like ocean slate
        for civ, (r, g, b) in SECTOR_COLORS.items():
            # "Ocean blue" would be something like (80, 120, 180)
            # where blue dominates by 40+ over both others
            blue_dominance = b - max(r, g)
            assert blue_dominance < 30, (
                f"{civ} color {(r, g, b)} is too ocean-blue"
            )


class TestStarFreightContent:
    """Test that Star Freight content data is accessible for the generator."""

    def test_stations_have_coordinates(self):
        from portlight.content.star_freight import SLICE_STATIONS

        for sid, station in SLICE_STATIONS.items():
            assert hasattr(station, "x"), f"{sid} missing x"
            assert hasattr(station, "y"), f"{sid} missing y"

    def test_stations_have_civilization(self):
        from portlight.content.star_freight import SLICE_STATIONS

        valid_civs = {"compact", "keth", "veshan", "orryn", "reach"}
        for sid, station in SLICE_STATIONS.items():
            assert station.civilization in valid_civs, (
                f"{sid} has invalid civilization: {station.civilization}"
            )

    def test_goods_have_base_price(self):
        from portlight.content.star_freight import SLICE_GOODS

        for gid, good in SLICE_GOODS.items():
            assert good.base_price > 0, f"{gid} has invalid base_price"

    def test_goods_have_categories(self):
        from portlight.content.star_freight import SLICE_GOODS

        valid_cats = {"commodity", "luxury", "provision", "military",
                      "tech", "contraband"}
        for gid, good in SLICE_GOODS.items():
            assert good.category in valid_cats, (
                f"{gid} has invalid category: {good.category}"
            )

    def test_lanes_have_distance(self):
        from portlight.content.star_freight import SLICE_LANES

        for lid, lane in SLICE_LANES.items():
            assert lane.distance_days > 0, f"{lid} has invalid distance"
            assert lane.station_a, f"{lid} missing station_a"
            assert lane.station_b, f"{lid} missing station_b"

    def test_lanes_reference_valid_stations(self):
        from portlight.content.star_freight import SLICE_LANES, SLICE_STATIONS

        station_ids = set(SLICE_STATIONS.keys())
        for lid, lane in SLICE_LANES.items():
            assert lane.station_a in station_ids, (
                f"Lane {lid} references unknown station_a: {lane.station_a}"
            )
            assert lane.station_b in station_ids, (
                f"Lane {lid} references unknown station_b: {lane.station_b}"
            )

    def test_contracts_have_required_fields(self):
        from portlight.content.contracts import TEMPLATES

        for tmpl in TEMPLATES:
            assert tmpl.goods_pool
            assert tmpl.quantity_min > 0
            assert tmpl.quantity_max >= tmpl.quantity_min
            assert tmpl.reward_per_unit > 0
            assert tmpl.deadline_days > 0
            assert tmpl.trust_requirement


class TestPressureDeck:
    """Test the pressure deck (replaces event deck)."""

    def test_pressure_deck_size(self):
        from portlight.printandplay.generator import _build_pressure_deck

        pressures = _build_pressure_deck()
        assert len(pressures) >= 35  # substantial deck

    def test_pressure_categories_are_star_freight(self):
        from portlight.printandplay.generator import _build_pressure_deck

        pressures = _build_pressure_deck()
        categories = {p["category"] for p in pressures}

        # Must have Star Freight pressure types
        assert "Inspection" in categories
        assert "Scarcity" in categories
        assert "Piracy" in categories
        assert "Convoy" in categories
        assert "Hazard" in categories
        assert "Political" in categories
        assert "Market" in categories

        # Must NOT have Portlight maritime types
        assert "Weather" not in categories
        assert "Season" not in categories

    def test_pressure_cards_have_required_fields(self):
        from portlight.printandplay.generator import _build_pressure_deck

        for p in _build_pressure_deck():
            assert "title" in p
            assert "category" in p
            assert "effect" in p
            assert len(p["effect"]) > 10

    def test_backward_compat_event_deck(self):
        from portlight.printandplay.generator import _build_event_deck

        events = _build_event_deck()
        assert len(events) >= 35


class TestQuarterDeck:
    """Test the quarter deck (replaces season deck)."""

    def test_quarter_deck_size(self):
        from portlight.printandplay.generator import _build_quarter_deck

        quarters = _build_quarter_deck()
        assert len(quarters) == 4

    def test_quarter_names_are_star_freight(self):
        from portlight.printandplay.generator import _build_quarter_deck

        names = {q["quarter"] for q in _build_quarter_deck()}
        assert "Scarcity" in names
        assert "Convoy" in names
        assert "Sanctions" in names
        assert "Claims" in names

        # Must NOT have Portlight season names
        assert "Spring" not in names
        assert "Summer" not in names
        assert "Monsoon" not in names

    def test_quarters_have_effects(self):
        from portlight.printandplay.generator import _build_quarter_deck

        for q in _build_quarter_deck():
            assert "effects" in q
            assert len(q["effects"]) >= 2


try:
    import fpdf  # noqa: F401
    _has_fpdf = True
except ImportError:
    _has_fpdf = False


@pytest.mark.skipif(not _has_fpdf, reason="fpdf2 not installed")
class TestGenerator:
    """Test full PDF generation (requires fpdf2)."""

    def test_generate_creates_pdf(self, tmp_path: Path):
        from portlight.printandplay.generator import generate

        output = tmp_path / "test.pdf"
        result = generate(output)

        assert result == output
        assert output.exists()
        assert output.stat().st_size > 1000

    def test_generate_pdf_starts_with_header(self, tmp_path: Path):
        from portlight.printandplay.generator import generate

        output = tmp_path / "test.pdf"
        generate(output)

        with open(output, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_generate_default_output(self, tmp_path: Path, monkeypatch):
        from portlight.printandplay.generator import generate

        monkeypatch.chdir(tmp_path)
        result = generate()

        assert result.name == "star-freight-print-and-play.pdf"
        assert result.exists()
