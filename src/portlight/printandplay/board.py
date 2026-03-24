"""Game board rendering  -- star lanes of the Threshold.

The board is a political map, not a scenic one.
- Lanes read as corridors under different kinds of pressure
- Stations sit in governed territory, not neutral space
- Lane identity (inspection, convoy, contested, hazard, gray) is visible
- The board implies jurisdiction, not open travel
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from portlight.printandplay.assets import (
    FONT_HEADING,
    FONT_SMALL,
    FONT_TINY,
    INK,
    LANE_CONTESTED,
    LANE_CONVOY,
    LANE_GRAY,
    LANE_HAZARD,
    LANE_INSPECTION,
    LIGHT_GRAY,
    MARGIN,
    MEDIUM_GRAY,
    PAPER,
    SECTOR_COLORS,
    WHITE,
    lane_burn_cost,
)

if TYPE_CHECKING:
    from fpdf import FPDF


def _lane_identity(lane) -> tuple[str, tuple[int, int, int]]:
    """Classify a lane's pressure identity for visual rendering.

    Returns (label, color) based on the lane's mechanical identity.
    This is not cosmetic  -- it tells the player what kind of corridor they're entering.
    """
    # Contraband risk dominates  -- this is a monitored corridor
    cr = getattr(lane, "contraband_risk", 0.0)
    danger = getattr(lane, "danger", 0.0)
    controlled = getattr(lane, "controlled_by", "")
    terrain = getattr(lane, "terrain", "open")

    if cr >= 0.25:
        return "INSPECTED", LANE_INSPECTION
    if controlled == "reach" or controlled == "disputed":
        if danger >= 0.20:
            return "CONTESTED", LANE_CONTESTED
        return "GRAY", LANE_GRAY
    if cr >= 0.15 and danger <= 0.05:
        return "CONVOY", LANE_CONVOY
    if terrain in ("debris_field", "asteroid_field", "nebula"):
        return "HAZARD", LANE_HAZARD
    if danger <= 0.05:
        return "SAFE", LIGHT_GRAY
    return "", MEDIUM_GRAY


def draw_board(
    pdf: FPDF,
    stations: dict,
    lanes: list | dict,
) -> None:
    """Draw the star lane map on a new landscape page.

    Stations must have .name, .civilization/.sector, .x, .y attributes.
    Lanes must have .station_a, .station_b, .distance_days attributes.
    """
    pdf.add_page(orientation="L")

    # Background
    pdf.set_fill_color(*PAPER)
    pdf.rect(0, 0, pdf.w, pdf.h, style="F")

    # Title
    pdf.set_font("Helvetica", "B", FONT_HEADING)
    pdf.set_text_color(*INK)
    pdf.set_xy(MARGIN, 5)
    pdf.cell(pdf.w - 2 * MARGIN, 8,
             "STAR FREIGHT  -- Lanes of the Threshold", align="C")

    # Board area
    bx = MARGIN
    by = 16
    bw = pdf.w - 2 * MARGIN
    bh = pdf.h - by - 22  # room for legend

    # Board border
    pdf.set_draw_color(*LIGHT_GRAY)
    pdf.set_line_width(0.3)
    pdf.rect(bx, by, bw, bh, style="D")

    # Coordinate scaling  -- station x (0-8), y (0-8) to board area
    x_scale = bw / 10.0
    y_scale = bh / 9.0

    def station_pos(station) -> tuple[float, float]:
        sx = getattr(station, "x", 0) or getattr(station, "map_x", 0) or 0
        sy = getattr(station, "y", 0) or getattr(station, "map_y", 0) or 0
        return (bx + (sx + 1) * x_scale, by + (sy + 1) * y_scale)

    # Build station lookup
    station_map = {}
    if isinstance(stations, dict):
        station_map = {sid: s for sid, s in stations.items()}
    else:
        for s in stations:
            station_map[s.id] = s

    # Normalize lanes to list
    lane_list = lanes if isinstance(lanes, list) else list(lanes.values())

    # --- Draw lanes (connections with identity) ---
    for lane in lane_list:
        a_id = getattr(lane, "station_a", None) or getattr(lane, "port_a", None)
        b_id = getattr(lane, "station_b", None) or getattr(lane, "port_b", None)
        s1 = station_map.get(a_id)
        s2 = station_map.get(b_id)
        if not s1 or not s2:
            continue

        x1, y1 = station_pos(s1)
        x2, y2 = station_pos(s2)

        dist = getattr(lane, "distance_days", 0) or getattr(lane, "distance", 0)
        cost = lane_burn_cost(dist)

        identity_label, identity_color = _lane_identity(lane)

        # Line style based on lane identity
        pdf.set_draw_color(*identity_color)
        terrain = getattr(lane, "terrain", "open")

        if terrain in ("debris_field", "asteroid_field"):
            pdf.set_line_width(0.4)
            _draw_dashed_line(pdf, x1, y1, x2, y2, dash_len=2.5, gap_len=1.5)
        elif terrain == "nebula":
            pdf.set_line_width(0.3)
            _draw_dashed_line(pdf, x1, y1, x2, y2, dash_len=4, gap_len=2)
        else:
            if cost <= 1:
                pdf.set_line_width(0.2)
            elif cost == 2:
                pdf.set_line_width(0.35)
            else:
                pdf.set_line_width(0.5)
            pdf.line(x1, y1, x2, y2)

        # Burn cost + identity label at midpoint
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        pdf.set_font("Helvetica", "B", FONT_TINY)
        pdf.set_text_color(*identity_color)
        pdf.set_xy(mx - 4, my - 3)
        pdf.cell(8, 3, str(cost), align="C")

        if identity_label:
            pdf.set_font("Helvetica", "", 4)
            pdf.set_xy(mx - 8, my)
            pdf.cell(16, 2.5, identity_label, align="C")

    # --- Draw stations (nodes on top of lanes) ---
    for sid, station in station_map.items():
        px, py = station_pos(station)

        # Determine civilization
        civ = (getattr(station, "civilization", None)
               or getattr(station, "sector", None)
               or getattr(station, "region", None)
               or "reach")
        color = SECTOR_COLORS.get(civ, INK)

        # Station node  -- hexagonal feel via slightly larger diamond
        pdf.set_fill_color(*color)
        pdf.set_draw_color(*INK)
        pdf.set_line_width(0.25)
        pdf.ellipse(px - 3, py - 3, 6, 6, style="FD")

        # Service marker inside node
        services = getattr(station, "services", [])
        features = getattr(station, "features", [])
        svc_char = ""
        if "drydock" in services or "shipyard" in [
            getattr(f, "value", f) for f in features
        ]:
            svc_char = "D"
        elif "black_market" in services or "black_market" in [
            getattr(f, "value", f) for f in features
        ]:
            svc_char = "B"
        elif "contracts" in services:
            svc_char = "C"

        if svc_char:
            pdf.set_font("Helvetica", "B", 4)
            pdf.set_text_color(*WHITE)
            pdf.set_xy(px - 1.5, py - 1.5)
            pdf.cell(3, 3, svc_char, align="C")

        # Station name label
        name = getattr(station, "name", sid)
        pdf.set_font("Helvetica", "B", FONT_TINY)
        pdf.set_text_color(*INK)
        label_w = pdf.get_string_width(name)

        if px + 5 + label_w < bx + bw - 2:
            pdf.set_xy(px + 5, py - 2)
        else:
            pdf.set_xy(px - 5 - label_w, py - 2)
        pdf.cell(label_w + 1, 4, name)

    # Legend
    _draw_legend(pdf, bx, by + bh + 2, bw)
    pdf.set_text_color(*INK)


def _draw_dashed_line(
    pdf: FPDF,
    x1: float, y1: float,
    x2: float, y2: float,
    dash_len: float = 3,
    gap_len: float = 2,
) -> None:
    """Draw a dashed line between two points."""
    import math
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)
    if length < 0.1:
        return

    ux, uy = dx / length, dy / length
    pos = 0.0
    drawing = True

    while pos < length:
        seg = dash_len if drawing else gap_len
        end = min(pos + seg, length)
        if drawing:
            sx = x1 + ux * pos
            sy = y1 + uy * pos
            ex = x1 + ux * end
            ey = y1 + uy * end
            pdf.line(sx, sy, ex, ey)
        pos = end
        drawing = not drawing


def _draw_legend(pdf: FPDF, x: float, y: float, w: float) -> None:
    """Draw the board legend  -- civilizations + lane identities."""
    pdf.set_font("Helvetica", "B", FONT_SMALL)
    pdf.set_text_color(*INK)
    pdf.set_xy(x, y)
    pdf.cell(15, 4, "Sectors:")

    cx = x + 16
    civ_abbr = {
        "compact": "CMP", "keth": "KTH", "veshan": "VSH",
        "orryn": "ORN", "reach": "RCH",
    }
    for civ, color in SECTOR_COLORS.items():
        pdf.set_fill_color(*color)
        pdf.rect(cx, y + 0.5, 3, 3, style="F")
        pdf.set_font("Helvetica", "", FONT_TINY)
        pdf.set_xy(cx + 4, y)
        pdf.cell(10, 4, civ_abbr.get(civ, civ[:3].upper()))
        cx += 16

    # Lane identity legend
    cx += 6
    pdf.set_font("Helvetica", "B", FONT_TINY)
    pdf.set_xy(cx, y)
    pdf.cell(12, 4, "Lanes:")
    cx += 13

    lane_legend = [
        ("Inspected", LANE_INSPECTION),
        ("Convoy", LANE_CONVOY),
        ("Contested", LANE_CONTESTED),
        ("Hazard", LANE_HAZARD),
        ("Gray", LANE_GRAY),
    ]
    for label, color in lane_legend:
        pdf.set_draw_color(*color)
        pdf.set_line_width(0.4)
        pdf.line(cx, y + 2, cx + 5, y + 2)
        pdf.set_font("Helvetica", "", FONT_TINY)
        pdf.set_text_color(*INK)
        pdf.set_xy(cx + 6, y)
        pdf.cell(14, 4, label)
        cx += 22

    # Service markers
    cx += 4
    for label, char in [("[D] Drydock", "D"), ("[B] Black Mkt", "B"), ("[C] Contracts", "C")]:
        pdf.set_font("Helvetica", "", FONT_TINY)
        pdf.set_xy(cx, y)
        pdf.cell(20, 4, label)
        cx += 22
