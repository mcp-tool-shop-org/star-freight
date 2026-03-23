"""Game board rendering — port map with route connections.

The board is the cleanest part of the kit:
- Pale background, crisp route lines, strong port nodes
- Sea = negative space, not decorative water texture
- Port names readable from across a table
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from portlight.printandplay.assets import (
    FONT_HEADING,
    FONT_SMALL,
    FONT_TINY,
    INK,
    LIGHT_GRAY,
    MARGIN,
    MEDIUM_GRAY,
    PAPER,
    REGION_COLORS,
    WHITE,
    route_movement_cost,
)

if TYPE_CHECKING:
    from fpdf import FPDF


def draw_board(
    pdf: FPDF,
    ports: dict,
    routes: list,
) -> None:
    """Draw the game board on a new landscape page.

    Ports must have .name, .region, .map_x, .map_y, .features attributes.
    Routes must have .origin, .destination, .distance attributes.
    """
    pdf.add_page(orientation="L")

    # Background
    pdf.set_fill_color(*PAPER)
    pdf.rect(0, 0, pdf.w, pdf.h, style="F")

    # Title
    pdf.set_font("Helvetica", "B", FONT_HEADING)
    pdf.set_text_color(*INK)
    pdf.set_xy(MARGIN, 5)
    pdf.cell(pdf.w - 2 * MARGIN, 8, "PORTLIGHT - Trade Routes of the Known Seas", align="C")

    # Board area
    bx = MARGIN
    by = 16
    bw = pdf.w - 2 * MARGIN
    bh = pdf.h - by - 20  # leave room for legend

    # Light border
    pdf.set_draw_color(*LIGHT_GRAY)
    pdf.set_line_width(0.3)
    pdf.rect(bx, by, bw, bh, style="D")

    # Map coordinate system: use port map_x (0-50) and map_y (0-36)
    # Scale to board area
    x_scale = bw / 52.0
    y_scale = bh / 38.0

    def port_pos(port) -> tuple[float, float]:
        return (bx + (port.map_x + 1) * x_scale, by + (port.map_y + 1) * y_scale)

    # Build port lookup
    port_map = {pid: p for pid, p in ports.items()}

    # Draw routes (lines between ports)
    for route in routes:
        p1 = port_map.get(route.port_a)
        p2 = port_map.get(route.port_b)
        if not p1 or not p2:
            continue

        x1, y1 = port_pos(p1)
        x2, y2 = port_pos(p2)

        cost = route_movement_cost(route.distance)

        # Line style based on cost
        if cost <= 1:
            pdf.set_draw_color(*LIGHT_GRAY)
            pdf.set_line_width(0.2)
        elif cost == 2:
            pdf.set_draw_color(*MEDIUM_GRAY)
            pdf.set_line_width(0.3)
        elif cost == 3:
            pdf.set_draw_color(*INK)
            pdf.set_line_width(0.4)
        else:
            pdf.set_draw_color(*INK)
            pdf.set_line_width(0.5)
            # Dashed for extreme routes — draw as dotted segments
            _draw_dashed_line(pdf, x1, y1, x2, y2, dash_len=3, gap_len=2)
            continue

        pdf.line(x1, y1, x2, y2)

        # Route cost label at midpoint
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        pdf.set_font("Helvetica", "", FONT_TINY)
        pdf.set_text_color(*MEDIUM_GRAY)
        pdf.set_xy(mx - 2, my - 1.5)
        pdf.cell(4, 3, str(cost), align="C")

    # Draw ports (nodes on top of routes)
    for pid, port in port_map.items():
        px, py = port_pos(port)
        color = REGION_COLORS.get(port.region, INK)

        # Port dot
        pdf.set_fill_color(*color)
        pdf.set_draw_color(*INK)
        pdf.set_line_width(0.2)
        pdf.ellipse(px - 2.5, py - 2.5, 5, 5, style="FD")

        # Feature marker inside dot
        feat_char = ""
        for f in port.features:
            fv = f.value if hasattr(f, "value") else str(f)
            if fv == "shipyard":
                feat_char = "S"
            elif fv == "black_market":
                feat_char = "B"
            elif fv == "safe_harbor":
                feat_char = "H"
        if feat_char:
            pdf.set_font("Helvetica", "B", 4)
            pdf.set_text_color(*WHITE)
            pdf.set_xy(px - 1.5, py - 1.5)
            pdf.cell(3, 3, feat_char, align="C")

        # Port name label
        pdf.set_font("Helvetica", "B", FONT_TINY)
        pdf.set_text_color(*INK)
        label = port.name
        label_w = pdf.get_string_width(label)

        # Try to place label to the right; if near edge, place left
        if px + 4 + label_w < bx + bw - 2:
            pdf.set_xy(px + 4, py - 2)
        else:
            pdf.set_xy(px - 4 - label_w, py - 2)
        pdf.cell(label_w + 1, 4, label)

    # Legend bar at bottom
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
    """Draw the board legend bar."""
    pdf.set_font("Helvetica", "B", FONT_SMALL)
    pdf.set_text_color(*INK)
    pdf.set_xy(x, y)
    pdf.cell(15, 4, "Legend:")

    cx = x + 16
    # Region colors
    for region, color in REGION_COLORS.items():
        pdf.set_fill_color(*color)
        pdf.rect(cx, y + 0.5, 3, 3, style="F")
        pdf.set_font("Helvetica", "", FONT_TINY)
        abbr = {"Mediterranean": "MED", "North Atlantic": "ATL", "West Africa": "AFR",
                "East Indies": "IND", "South Seas": "SEA"}.get(region, region[:3])
        pdf.set_xy(cx + 4, y)
        pdf.cell(10, 4, abbr)
        cx += 18

    # Features
    cx += 5
    for label, char in [("[S] Shipyard", "S"), ("[B] Black Market", "B"), ("[H] Safe Harbor", "H")]:
        pdf.set_font("Helvetica", "", FONT_TINY)
        pdf.set_xy(cx, y)
        pdf.cell(25, 4, label)
        cx += 28

    # Route costs
    cx += 5
    pdf.set_font("Helvetica", "B", FONT_TINY)
    pdf.set_xy(cx, y)
    pdf.cell(12, 4, "Routes:")
    cx += 13
    for cost, desc in [(1, "Short"), (2, "Medium"), (3, "Long"), (4, "Extreme")]:
        pdf.set_font("Helvetica", "", FONT_TINY)
        pdf.set_xy(cx, y)
        pdf.cell(18, 4, f"{cost}={desc}")
        cx += 20
