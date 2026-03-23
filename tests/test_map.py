"""Tests for the world map view and CLI command."""

from io import StringIO

from rich.console import Console

from portlight.app import views
from portlight.content.ports import PORTS
from portlight.content.routes import ROUTES


def _render(renderable) -> str:
    """Render a Rich renderable to plain text for assertions."""
    buf = StringIO()
    console = Console(file=buf, width=140, no_color=True)
    console.print(renderable)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Bresenham line drawing
# ---------------------------------------------------------------------------

def test_bresenham_horizontal():
    pts = views._bresenham(0, 0, 5, 0)
    assert len(pts) == 4  # excludes endpoints
    assert all(y == 0 for _, y in pts)


def test_bresenham_vertical():
    pts = views._bresenham(0, 0, 0, 5)
    assert len(pts) == 4
    assert all(x == 0 for x, _ in pts)


def test_bresenham_diagonal():
    pts = views._bresenham(0, 0, 3, 3)
    assert len(pts) == 2  # (1,1), (2,2) — excludes (0,0) and (3,3)


def test_bresenham_single_step():
    pts = views._bresenham(0, 0, 1, 0)
    assert pts == []  # adjacent points, no interior


# ---------------------------------------------------------------------------
# World map rendering
# ---------------------------------------------------------------------------

def test_world_map_renders_all_ports():
    """All 20 port names should appear in the rendered map."""
    panel = views.world_map_view(None, player_port_id=None, show_routes=False)
    text = _render(panel)
    for port in PORTS.values():
        assert port.name in text, f"Port {port.name} missing from map"


def test_world_map_renders_with_player():
    """Player position marker should appear."""
    panel = views.world_map_view(None, player_port_id="porto_novo", show_routes=False)
    text = _render(panel)
    assert "Porto Novo" in text
    assert "Docked: Porto Novo" in text


def test_world_map_renders_with_routes():
    """Route rendering should not crash and should include legend."""
    panel = views.world_map_view(None, player_port_id=None, show_routes=True)
    text = _render(panel)
    assert "Sloop" in text
    assert "Brigantine" in text
    assert "Galleon" in text


def test_world_map_region_filter():
    """Region filter should only show ports from that region."""
    panel = views.world_map_view(None, player_port_id=None, show_routes=False, region_filter="med")
    text = _render(panel)
    assert "Porto Novo" in text
    assert "Al-Manar" in text
    # East Indies ports should NOT appear
    assert "Jade Port" not in text
    assert "Silk Haven" not in text


def test_world_map_region_filter_atlantic():
    panel = views.world_map_view(None, player_port_id=None, show_routes=False, region_filter="atl")
    text = _render(panel)
    assert "Ironhaven" in text
    assert "Stormwall" in text
    assert "Porto Novo" not in text


def test_world_map_legend_contains_regions():
    """Legend should list all 5 region abbreviations."""
    panel = views.world_map_view(None, player_port_id=None, show_routes=False)
    text = _render(panel)
    assert "MED" in text
    assert "ATL" in text
    assert "AFR" in text
    assert "IND" in text
    assert "SEA" in text


def test_world_map_legend_player_marker():
    """Legend should show 'You' when player is docked."""
    panel = views.world_map_view(None, player_port_id="ironhaven", show_routes=False)
    text = _render(panel)
    assert "You" in text


def test_world_map_no_crash_unknown_region():
    """Unknown region filter should produce empty map without crashing."""
    panel = views.world_map_view(None, player_port_id=None, show_routes=False, region_filter="nonexistent")
    text = _render(panel)
    # Should still render — just no ports
    assert "The Known World" not in text  # title changes to region name


def test_world_map_port_count():
    """Verify all 20 ports exist in the content data."""
    assert len(PORTS) == 20


def test_world_map_all_routes_reference_valid_ports():
    """Every route should reference ports that exist."""
    for route in ROUTES:
        assert route.port_a in PORTS, f"Route references unknown port: {route.port_a}"
        assert route.port_b in PORTS, f"Route references unknown port: {route.port_b}"
