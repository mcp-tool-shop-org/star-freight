"""Tests for the Print-and-Play PDF generator."""

from __future__ import annotations

from pathlib import Path

import pytest



class TestAssets:
    """Test tabletop scaling constants."""

    def test_route_movement_cost_tiers(self):
        from portlight.printandplay.assets import route_movement_cost

        assert route_movement_cost(14) == 1   # short intra-region
        assert route_movement_cost(22) == 1   # upper bound short
        assert route_movement_cost(36) == 2   # medium cross-region
        assert route_movement_cost(44) == 2   # upper bound medium
        assert route_movement_cost(56) == 3   # long haul
        assert route_movement_cost(64) == 3   # upper bound long
        assert route_movement_cost(72) == 4   # extreme shortcut
        assert route_movement_cost(80) == 4   # max distance

    def test_tabletop_price_scaling(self):
        from portlight.printandplay.assets import tabletop_price

        assert tabletop_price(12) == 2     # grain
        assert tabletop_price(70) == 14    # silk
        assert tabletop_price(95) == 19    # pearls
        assert tabletop_price(5) == 1      # minimum 1
        assert tabletop_price(0) == 1      # floor at 1

    def test_ship_tabletop_all_ships_present(self):
        from portlight.printandplay.assets import SHIP_TABLETOP
        from portlight.content.ships import SHIPS

        for ship_id in SHIPS:
            assert ship_id in SHIP_TABLETOP, f"Missing tabletop stats for {ship_id}"

    def test_captain_tabletop_all_present(self):
        from portlight.printandplay.assets import CAPTAIN_TABLETOP

        assert "merchant" in CAPTAIN_TABLETOP
        assert "navigator" in CAPTAIN_TABLETOP
        assert "smuggler" in CAPTAIN_TABLETOP

    def test_region_colors_all_regions(self):
        from portlight.printandplay.assets import REGION_COLORS
        from portlight.content.ports import PORTS

        regions = {p.region for p in PORTS.values()}
        for region in regions:
            assert region in REGION_COLORS, f"Missing color for region {region}"


class TestContentSourcing:
    """Test that all content data is accessible for the generator."""

    def test_ports_have_map_coordinates(self):
        from portlight.content.ports import PORTS

        for pid, port in PORTS.items():
            assert hasattr(port, "map_x"), f"{pid} missing map_x"
            assert hasattr(port, "map_y"), f"{pid} missing map_y"

    def test_goods_have_base_price(self):
        from portlight.content.goods import GOODS

        for gid, good in GOODS.items():
            assert good.base_price > 0, f"{gid} has invalid base_price"

    def test_routes_have_distance(self):
        from portlight.content.routes import ROUTES

        for route in ROUTES:
            assert route.distance > 0
            assert route.port_a
            assert route.port_b

    def test_contracts_have_required_fields(self):
        from portlight.content.contracts import TEMPLATES

        for tmpl in TEMPLATES:
            assert tmpl.goods_pool
            assert tmpl.quantity_min > 0
            assert tmpl.quantity_max >= tmpl.quantity_min
            assert tmpl.reward_per_unit > 0
            assert tmpl.deadline_days > 0
            assert tmpl.trust_requirement


try:
    import fpdf  # noqa: F401
    _has_fpdf = True
except ImportError:
    _has_fpdf = False


@pytest.mark.skipif(not _has_fpdf, reason="fpdf2 not installed — PDF generation is optional")
class TestGenerator:
    """Test full PDF generation (requires fpdf2)."""

    def test_generate_creates_pdf(self, tmp_path: Path):
        from portlight.printandplay.generator import generate

        output = tmp_path / "test.pdf"
        result = generate(output)

        assert result == output
        assert output.exists()
        assert output.stat().st_size > 1000  # should be substantial

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

        assert result.name == "portlight-print-and-play.pdf"
        assert result.exists()

    def test_event_deck_size(self):
        from portlight.printandplay.generator import _build_event_deck

        events = _build_event_deck()
        assert len(events) == 40
        categories = {e["category"] for e in events}
        assert "Weather" in categories
        assert "Pirates" in categories
        assert "Inspection" in categories
        assert "Trade" in categories
        assert "Culture" in categories
