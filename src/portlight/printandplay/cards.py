"""Card rendering for the Print-and-Play PDF kit.

Each function draws a single card type onto the PDF at a given (x, y) position.
Cards follow the unified frame: title band > type tag > content > stats footer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from portlight.printandplay.assets import (
    CARD_H,
    CARD_PADDING,
    CARD_W,
    COMPACT_CARD_H,
    FONT_BODY,
    FONT_SMALL,
    FONT_SUBHEADING,
    FONT_TINY,
    INK,
    LIGHT_GRAY,
    MEDIUM_GRAY,
    REGION_COLORS,
    WHITE,
)

if TYPE_CHECKING:
    from fpdf import FPDF


def _set_ink(pdf: FPDF) -> None:
    pdf.set_text_color(*INK)


def _draw_card_frame(pdf: FPDF, x: float, y: float, h: float = CARD_H) -> None:
    """Draw a card outline with rounded corners."""
    pdf.set_draw_color(*MEDIUM_GRAY)
    pdf.set_line_width(0.3)
    pdf.rect(x, y, CARD_W, h, style="D")


def _draw_title_band(
    pdf: FPDF,
    x: float,
    y: float,
    title: str,
    tag: str = "",
    color: tuple[int, int, int] = INK,
) -> float:
    """Draw the title band at the top of a card. Returns y after the band."""
    band_h = 8.0
    pdf.set_fill_color(*color)
    pdf.rect(x, y, CARD_W, band_h, style="F")

    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", FONT_SUBHEADING)
    pdf.set_xy(x + CARD_PADDING, y + 1)
    pdf.cell(CARD_W - 2 * CARD_PADDING - 20, band_h - 2, title, align="L")

    if tag:
        pdf.set_font("Helvetica", "", FONT_TINY)
        pdf.set_xy(x + CARD_W - CARD_PADDING - 20, y + 1.5)
        pdf.cell(20, band_h - 3, tag, align="R")

    _set_ink(pdf)
    return y + band_h


def _draw_stats_footer(
    pdf: FPDF,
    x: float,
    y: float,
    stats: list[tuple[str, str]],
) -> None:
    """Draw a stats strip at the bottom of a card."""
    footer_h = 6.0
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.rect(x, y, CARD_W, footer_h, style="F")

    col_w = (CARD_W - 2 * CARD_PADDING) / max(len(stats), 1)
    pdf.set_font("Helvetica", "", FONT_TINY)
    _set_ink(pdf)
    for i, (label, value) in enumerate(stats):
        cx = x + CARD_PADDING + i * col_w
        pdf.set_xy(cx, y + 0.5)
        pdf.cell(col_w, 3, label, align="C")
        pdf.set_xy(cx, y + 3)
        pdf.set_font("Helvetica", "B", FONT_SMALL)
        pdf.cell(col_w, 3, value, align="C")
        pdf.set_font("Helvetica", "", FONT_TINY)


# ---------------------------------------------------------------------------
# Goods card — inventory slip style
# ---------------------------------------------------------------------------

def draw_goods_card(
    pdf: FPDF,
    x: float,
    y: float,
    name: str,
    category: str,
    base_price: int,
    tabletop_price: int,
) -> None:
    """Draw a single goods card."""
    _draw_card_frame(pdf, x, y)

    # Category determines band color
    cat_colors = {
        "COMMODITY": (120, 130, 110),
        "LUXURY": (140, 110, 130),
        "PROVISION": (110, 125, 100),
        "MILITARY": (130, 110, 110),
        "MEDICINE": (100, 120, 130),
        "CONTRABAND": (60, 60, 60),
    }
    color = cat_colors.get(category, INK)

    cy = _draw_title_band(pdf, x, y, name, category[:4].upper(), color)

    # Price display
    pdf.set_font("Helvetica", "B", 24)
    _set_ink(pdf)
    pdf.set_xy(x + CARD_PADDING, cy + 8)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 12, f"{tabletop_price}", align="C")

    pdf.set_font("Helvetica", "", FONT_BODY)
    pdf.set_xy(x + CARD_PADDING, cy + 20)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 5, "silver (base)", align="C")

    # Category tag
    pdf.set_font("Helvetica", "", FONT_SMALL)
    pdf.set_text_color(*MEDIUM_GRAY)
    pdf.set_xy(x + CARD_PADDING, cy + 30)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 5, category.title(), align="C")
    _set_ink(pdf)

    # Footer
    _draw_stats_footer(pdf, x, y + CARD_H - 6, [
        ("Weight", "1"),
        ("Type", category[:5]),
    ])


# ---------------------------------------------------------------------------
# Contract card — shipping order style
# ---------------------------------------------------------------------------

def draw_contract_card(
    pdf: FPDF,
    x: float,
    y: float,
    title: str,
    goods: str,
    qty_range: str,
    reward: str,
    deadline: str,
    trust: str,
    flavor: str = "",
) -> None:
    """Draw a single contract card."""
    _draw_card_frame(pdf, x, y)
    cy = _draw_title_band(pdf, x, y, title[:20], "CONTRACT", (100, 90, 70))

    pdf.set_font("Helvetica", "B", FONT_BODY)
    _set_ink(pdf)
    lines = [
        f"Cargo: {goods} x{qty_range}",
        f"Reward: {reward} silver",
        f"Deadline: {deadline} rounds",
        f"Trust: {trust}",
    ]
    for i, line in enumerate(lines):
        pdf.set_xy(x + CARD_PADDING, cy + 2 + i * 5)
        pdf.cell(CARD_W - 2 * CARD_PADDING, 5, line)

    if flavor:
        pdf.set_font("Helvetica", "I", FONT_TINY)
        pdf.set_text_color(*MEDIUM_GRAY)
        pdf.set_xy(x + CARD_PADDING, cy + 24)
        pdf.multi_cell(CARD_W - 2 * CARD_PADDING, 3, flavor[:120])
        _set_ink(pdf)

    _draw_stats_footer(pdf, x, y + CARD_H - 6, [
        ("Goods", goods[:6]),
        ("Qty", qty_range),
        ("Days", deadline),
    ])


# ---------------------------------------------------------------------------
# Event card — incident notice style
# ---------------------------------------------------------------------------

def draw_event_card(
    pdf: FPDF,
    x: float,
    y: float,
    title: str,
    category: str,
    effect: str,
    flavor: str = "",
) -> None:
    """Draw a single event card."""
    _draw_card_frame(pdf, x, y)

    cat_colors = {
        "Weather": (90, 120, 150),
        "Pirates": (140, 80, 70),
        "Inspection": (130, 120, 80),
        "Trade": (90, 130, 100),
        "Culture": (120, 110, 130),
    }
    color = cat_colors.get(category, INK)
    cy = _draw_title_band(pdf, x, y, title, category[:6].upper(), color)

    pdf.set_font("Helvetica", "", FONT_BODY)
    _set_ink(pdf)
    pdf.set_xy(x + CARD_PADDING, cy + 3)
    pdf.multi_cell(CARD_W - 2 * CARD_PADDING, 4, effect[:200])

    if flavor:
        pdf.set_font("Helvetica", "I", FONT_TINY)
        pdf.set_text_color(*MEDIUM_GRAY)
        pdf.set_xy(x + CARD_PADDING, y + CARD_H - 16)
        pdf.multi_cell(CARD_W - 2 * CARD_PADDING, 3, flavor[:100])
        _set_ink(pdf)


# ---------------------------------------------------------------------------
# Ship card — registry document style
# ---------------------------------------------------------------------------

def draw_ship_card(
    pdf: FPDF,
    x: float,
    y: float,
    name: str,
    ship_class: str,
    stats: dict[str, int],
) -> None:
    """Draw a single ship card."""
    _draw_card_frame(pdf, x, y)
    cy = _draw_title_band(pdf, x, y, name, ship_class.upper(), (80, 90, 100))

    pdf.set_font("Helvetica", "", FONT_BODY)
    _set_ink(pdf)
    stat_lines = [
        f"Cargo Capacity: {stats['cargo']} cards",
        f"Speed: {stats['speed']} movement points",
        f"Hull: {stats['hull']} damage threshold",
        f"Crew Cost: {stats['crew_cost']} silver/round",
        f"Cannons: {stats['cannons']}",
        f"Price: {stats['price']} silver" if stats['price'] > 0 else "Price: Free (starting ship)",
    ]
    for i, line in enumerate(stat_lines):
        pdf.set_xy(x + CARD_PADDING, cy + 3 + i * 5)
        pdf.cell(CARD_W - 2 * CARD_PADDING, 5, line)

    _draw_stats_footer(pdf, x, y + CARD_H - 6, [
        ("Cargo", str(stats["cargo"])),
        ("Speed", str(stats["speed"])),
        ("Hull", str(stats["hull"])),
        ("Cost", str(stats["price"])),
    ])


# ---------------------------------------------------------------------------
# Captain card — player board style (strongest visual presence)
# ---------------------------------------------------------------------------

def draw_captain_card(
    pdf: FPDF,
    x: float,
    y: float,
    name: str,
    home_port: str,
    silver: int,
    provisions: int,
    heat: int,
    ability: str,
    weakness: str,
) -> None:
    """Draw a captain player board card (uses full card height)."""
    _draw_card_frame(pdf, x, y)
    cy = _draw_title_band(pdf, x, y, name, "CAPTAIN", (70, 80, 110))

    pdf.set_font("Helvetica", "B", FONT_SMALL)
    _set_ink(pdf)
    pdf.set_xy(x + CARD_PADDING, cy + 2)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 4, f"Home: {home_port}")

    pdf.set_font("Helvetica", "", FONT_SMALL)
    pdf.set_xy(x + CARD_PADDING, cy + 7)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 4, f"Silver: {silver}  Prov: {provisions}  Heat: {heat}")

    # Ability
    pdf.set_xy(x + CARD_PADDING, cy + 14)
    pdf.set_font("Helvetica", "B", FONT_TINY)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 3, "ABILITY:")
    pdf.set_font("Helvetica", "", FONT_TINY)
    pdf.set_xy(x + CARD_PADDING, cy + 17)
    pdf.multi_cell(CARD_W - 2 * CARD_PADDING, 3, ability)

    # Weakness
    pdf.set_xy(x + CARD_PADDING, cy + 32)
    pdf.set_font("Helvetica", "B", FONT_TINY)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 3, "WEAKNESS:")
    pdf.set_font("Helvetica", "", FONT_TINY)
    pdf.set_xy(x + CARD_PADDING, cy + 35)
    pdf.multi_cell(CARD_W - 2 * CARD_PADDING, 3, weakness)

    _draw_stats_footer(pdf, x, y + CARD_H - 6, [
        ("Silver", str(silver)),
        ("Prov", str(provisions)),
        ("Heat", str(heat)),
    ])


# ---------------------------------------------------------------------------
# Port reference card — compact, market profile
# ---------------------------------------------------------------------------

def draw_port_card(
    pdf: FPDF,
    x: float,
    y: float,
    name: str,
    region: str,
    features: list[str],
    exports: list[str],
    imports: list[str],
    port_fee: int,
) -> None:
    """Draw a compact port reference card."""
    h = COMPACT_CARD_H
    _draw_card_frame(pdf, x, y, h)

    color = REGION_COLORS.get(region, INK)
    band_h = 6.0
    pdf.set_fill_color(*color)
    pdf.rect(x, y, CARD_W, band_h, style="F")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", FONT_SMALL)
    pdf.set_xy(x + CARD_PADDING, y + 0.5)
    pdf.cell(CARD_W - 2 * CARD_PADDING - 15, band_h - 1, name, align="L")

    # Features tag
    feat_str = " ".join(f"[{f[0].upper()}]" for f in features) if features else ""
    pdf.set_font("Helvetica", "", FONT_TINY)
    pdf.set_xy(x + CARD_W - CARD_PADDING - 15, y + 1)
    pdf.cell(15, band_h - 2, feat_str, align="R")

    _set_ink(pdf)
    cy = y + band_h + 1

    pdf.set_font("Helvetica", "", FONT_TINY)
    pdf.set_xy(x + CARD_PADDING, cy)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 3, f"Region: {region}  |  Fee: {port_fee} silver")

    pdf.set_xy(x + CARD_PADDING, cy + 4)
    pdf.set_font("Helvetica", "B", FONT_TINY)
    pdf.cell(12, 3, "BUY:")
    pdf.set_font("Helvetica", "", FONT_TINY)
    pdf.cell(CARD_W - 2 * CARD_PADDING - 12, 3, ", ".join(exports[:5]))

    pdf.set_xy(x + CARD_PADDING, cy + 7.5)
    pdf.set_font("Helvetica", "B", FONT_TINY)
    pdf.cell(12, 3, "SELL:")
    pdf.set_font("Helvetica", "", FONT_TINY)
    pdf.cell(CARD_W - 2 * CARD_PADDING - 12, 3, ", ".join(imports[:5]))


# ---------------------------------------------------------------------------
# Season card
# ---------------------------------------------------------------------------

def draw_season_card(
    pdf: FPDF,
    x: float,
    y: float,
    season: str,
    rounds: str,
    effects: list[str],
) -> None:
    """Draw a season card."""
    _draw_card_frame(pdf, x, y)

    season_colors = {
        "Spring": (100, 140, 90),
        "Summer": (160, 130, 70),
        "Autumn": (150, 110, 70),
        "Winter": (90, 110, 140),
    }
    color = season_colors.get(season, INK)
    cy = _draw_title_band(pdf, x, y, season, f"Rounds {rounds}", color)

    pdf.set_font("Helvetica", "", FONT_BODY)
    _set_ink(pdf)
    for i, effect in enumerate(effects):
        pdf.set_xy(x + CARD_PADDING, cy + 3 + i * 5)
        pdf.multi_cell(CARD_W - 2 * CARD_PADDING, 4, f"- {effect}")
