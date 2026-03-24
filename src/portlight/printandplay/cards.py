"""Card rendering for the Star Freight Print-and-Play kit.

Each function draws a single card type onto the PDF at a given (x, y) position.
Cards follow the unified frame: title band > type tag > content > stats footer.

Seven card types:
- Captain  -- player board: posture, life description, starting conditions
- Vessel  -- campaign posture ship: cargo/burn/hull/hardpoints
- Goods  -- trade commodity with origin civilization and political weight
- Contract  -- hauling job with trust gate, deadline, and pressure
- Pressure  -- replaces "event": institutional/scarcity/hazard encounter
- Quarter  -- replaces "season": world-state rhythm (shortage, convoy, sanctions)
- Station  -- replaces "port": civilization territory with services and market identity
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from portlight.printandplay.assets import (
    CARD_H,
    CARD_PADDING,
    CARD_W,
    COMPACT_CARD_H,
    CREDITS_COLOR,
    FONT_BODY,
    FONT_SMALL,
    FONT_SUBHEADING,
    FONT_TINY,
    HEAT_COLOR,
    INK,
    LIGHT_GRAY,
    MEDIUM_GRAY,
    SECTOR_COLORS,
    STANDING_COLOR,
    WHITE,
)

if TYPE_CHECKING:
    from fpdf import FPDF


def _set_ink(pdf: FPDF) -> None:
    pdf.set_text_color(*INK)


def _draw_card_frame(pdf: FPDF, x: float, y: float, h: float = CARD_H) -> None:
    """Draw a card outline."""
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
# Goods card  -- trade commodity with political origin
# ---------------------------------------------------------------------------

def draw_goods_card(
    pdf: FPDF,
    x: float,
    y: float,
    name: str,
    category: str,
    base_price: int,
    tabletop_price: int,
    origin_civ: str = "",
) -> None:
    """Draw a single goods card."""
    _draw_card_frame(pdf, x, y)

    cat_colors = {
        "commodity":  (100, 100, 95),    # industrial gray
        "luxury":     (130, 110, 130),   # dusted violet
        "provision":  (100, 120, 90),    # supply green
        "military":   (140, 90, 80),     # martial red
        "tech":       (80, 100, 120),    # cold blue
        "contraband": (60, 58, 55),      # near-black
    }
    color = cat_colors.get(category.lower(), INK)

    cy = _draw_title_band(pdf, x, y, name, category[:5].upper(), color)

    # Price display
    pdf.set_font("Helvetica", "B", 24)
    _set_ink(pdf)
    pdf.set_xy(x + CARD_PADDING, cy + 6)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 12, f"{tabletop_price}", align="C")

    pdf.set_font("Helvetica", "", FONT_BODY)
    pdf.set_xy(x + CARD_PADDING, cy + 18)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 5, "credits (base)", align="C")

    # Origin civilization
    if origin_civ:
        civ_names = {
            "compact": "Terran Compact", "keth": "Keth Communion",
            "veshan": "Veshan Principalities", "orryn": "Orryn Drift",
            "reach": "Sable Reach",
        }
        pdf.set_font("Helvetica", "", FONT_SMALL)
        pdf.set_text_color(*MEDIUM_GRAY)
        pdf.set_xy(x + CARD_PADDING, cy + 26)
        pdf.cell(CARD_W - 2 * CARD_PADDING, 5,
                 civ_names.get(origin_civ, origin_civ), align="C")
        _set_ink(pdf)
    else:
        pdf.set_font("Helvetica", "", FONT_SMALL)
        pdf.set_text_color(*MEDIUM_GRAY)
        pdf.set_xy(x + CARD_PADDING, cy + 26)
        pdf.cell(CARD_W - 2 * CARD_PADDING, 5, category.title(), align="C")
        _set_ink(pdf)

    _draw_stats_footer(pdf, x, y + CARD_H - 6, [
        ("Wt", "1"),
        ("Type", category[:5]),
    ])


# ---------------------------------------------------------------------------
# Contract card  -- hauling order with pressure
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
        f"Reward: {reward} credits",
        f"Deadline: {deadline} quarters",
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
        ("Qtrs", deadline),
    ])


# ---------------------------------------------------------------------------
# Pressure card  -- replaces "event": institutional + scarcity + hazard
# ---------------------------------------------------------------------------

def draw_pressure_card(
    pdf: FPDF,
    x: float,
    y: float,
    title: str,
    category: str,
    effect: str,
    flavor: str = "",
) -> None:
    """Draw a single pressure card (replaces event card)."""
    _draw_card_frame(pdf, x, y)

    cat_colors = {
        "Inspection":   (95, 105, 125),   # compact slate  -- authority
        "Scarcity":     (140, 130, 80),   # amber  -- shortage urgency
        "Piracy":       (85, 80, 75),     # reach carbon  -- lawless
        "Convoy":       (110, 140, 100),  # keth green  -- managed movement
        "Hazard":       (130, 95, 80),    # rust  -- debris, lane danger
        "Political":    (155, 100, 80),   # veshan sienna  -- house pressure
        "Market":       (130, 120, 145),  # orryn violet  -- trade shift
    }
    color = cat_colors.get(category, INK)
    cy = _draw_title_band(pdf, x, y, title, category[:7].upper(), color)

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


# Backward compat alias
draw_event_card = draw_pressure_card


# ---------------------------------------------------------------------------
# Vessel card  -- campaign posture ship
# ---------------------------------------------------------------------------

def draw_vessel_card(
    pdf: FPDF,
    x: float,
    y: float,
    name: str,
    vessel_class: str,
    stats: dict[str, int],
    flavor: str = "",
) -> None:
    """Draw a single vessel card."""
    _draw_card_frame(pdf, x, y)
    cy = _draw_title_band(pdf, x, y, name, vessel_class.upper(), (80, 85, 95))

    pdf.set_font("Helvetica", "", FONT_BODY)
    _set_ink(pdf)
    stat_lines = [
        f"Cargo Capacity: {stats.get('cargo', 0)} units",
        f"Burn Rate: {stats.get('burn', 0)} fuel/lane",
        f"Hull: {stats.get('hull', 0)} damage threshold",
        f"Crew Slots: {stats.get('crew_slots', 0)}",
        f"Hardpoints: {stats.get('hardpoints', 0)}",
    ]
    price = stats.get("price", 0)
    if price > 0:
        stat_lines.append(f"Price: {price} credits")
    else:
        stat_lines.append("Price: Starting vessel")

    for i, line in enumerate(stat_lines):
        pdf.set_xy(x + CARD_PADDING, cy + 3 + i * 5)
        pdf.cell(CARD_W - 2 * CARD_PADDING, 5, line)

    if flavor:
        pdf.set_font("Helvetica", "I", FONT_TINY)
        pdf.set_text_color(*MEDIUM_GRAY)
        pdf.set_xy(x + CARD_PADDING, cy + 35)
        pdf.multi_cell(CARD_W - 2 * CARD_PADDING, 3, flavor[:100])
        _set_ink(pdf)

    _draw_stats_footer(pdf, x, y + CARD_H - 6, [
        ("Cargo", str(stats.get("cargo", 0))),
        ("Burn", str(stats.get("burn", 0))),
        ("Hull", str(stats.get("hull", 0))),
        ("HP", str(stats.get("hardpoints", 0))),
    ])


# Backward compat alias
def draw_ship_card(pdf, x, y, name, ship_class, stats):
    draw_vessel_card(pdf, x, y, name, ship_class, stats)


# ---------------------------------------------------------------------------
# Captain card  -- player board: posture, life, starting conditions
# ---------------------------------------------------------------------------

def draw_captain_card(
    pdf: FPDF,
    x: float,
    y: float,
    name: str,
    home_station: str = "",
    credits: int = 0,
    fuel: int = 0,
    heat: int = 0,
    ability: str = "",
    weakness: str = "",
    life: str = "",
    **kwargs,
) -> None:
    """Draw a captain player board card."""
    # Accept old kwarg names for backward compat
    home_station = home_station or kwargs.get("home_port", "")
    credits = credits or kwargs.get("silver", 0)
    fuel = fuel or kwargs.get("provisions", 0)

    _draw_card_frame(pdf, x, y)
    cy = _draw_title_band(pdf, x, y, name, "CAPTAIN", (70, 75, 90))

    pdf.set_font("Helvetica", "B", FONT_SMALL)
    _set_ink(pdf)
    pdf.set_xy(x + CARD_PADDING, cy + 2)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 4, f"Home: {home_station}")

    pdf.set_font("Helvetica", "", FONT_SMALL)
    pdf.set_xy(x + CARD_PADDING, cy + 7)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 4,
             f"Credits: {credits}  Fuel: {fuel}  Heat: {heat}")

    # Life description (what kind of captain you become)
    if life:
        pdf.set_font("Helvetica", "I", FONT_TINY)
        pdf.set_text_color(*MEDIUM_GRAY)
        pdf.set_xy(x + CARD_PADDING, cy + 12)
        pdf.multi_cell(CARD_W - 2 * CARD_PADDING, 3, life[:100])
        _set_ink(pdf)

    # Ability
    ability_y = cy + 22 if life else cy + 14
    pdf.set_xy(x + CARD_PADDING, ability_y)
    pdf.set_font("Helvetica", "B", FONT_TINY)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 3, "ABILITY:")
    pdf.set_font("Helvetica", "", FONT_TINY)
    pdf.set_xy(x + CARD_PADDING, ability_y + 3)
    pdf.multi_cell(CARD_W - 2 * CARD_PADDING, 3, ability[:150])

    # Weakness
    weak_y = ability_y + 16
    pdf.set_xy(x + CARD_PADDING, weak_y)
    pdf.set_font("Helvetica", "B", FONT_TINY)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 3, "WEAKNESS:")
    pdf.set_font("Helvetica", "", FONT_TINY)
    pdf.set_xy(x + CARD_PADDING, weak_y + 3)
    pdf.multi_cell(CARD_W - 2 * CARD_PADDING, 3, weakness[:150])

    _draw_stats_footer(pdf, x, y + CARD_H - 6, [
        ("Cr", str(credits)),
        ("Fuel", str(fuel)),
        ("Heat", str(heat)),
    ])


# ---------------------------------------------------------------------------
# Station reference card  -- civilization territory, market identity
# ---------------------------------------------------------------------------

def draw_station_card(
    pdf: FPDF,
    x: float,
    y: float,
    name: str,
    civilization: str = "",
    services: list[str] | None = None,
    produces: list[str] | None = None,
    demands: list[str] | None = None,
    docking_fee: int = 0,
    **kwargs,
) -> None:
    """Draw a compact station reference card."""
    # Accept old kwarg names
    region = civilization or kwargs.get("region", "")
    features = kwargs.get("features", [])
    exports = produces if produces is not None else kwargs.get("exports", [])
    imports = demands if demands is not None else kwargs.get("imports", [])
    port_fee = docking_fee or kwargs.get("port_fee", 0)

    h = COMPACT_CARD_H
    _draw_card_frame(pdf, x, y, h)

    color = SECTOR_COLORS.get(region, INK)
    band_h = 6.0
    pdf.set_fill_color(*color)
    pdf.rect(x, y, CARD_W, band_h, style="F")
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", FONT_SMALL)
    pdf.set_xy(x + CARD_PADDING, y + 0.5)
    pdf.cell(CARD_W - 2 * CARD_PADDING - 15, band_h - 1, name, align="L")

    # Service tags
    svc = services or []
    feat_list = [getattr(f, "value", str(f)) for f in features]
    all_svc = svc + feat_list
    svc_chars = []
    if "drydock" in all_svc or "shipyard" in all_svc:
        svc_chars.append("[D]")
    if "black_market" in all_svc:
        svc_chars.append("[B]")
    if "contracts" in all_svc:
        svc_chars.append("[C]")
    svc_str = " ".join(svc_chars)
    pdf.set_font("Helvetica", "", FONT_TINY)
    pdf.set_xy(x + CARD_W - CARD_PADDING - 15, y + 1)
    pdf.cell(15, band_h - 2, svc_str, align="R")

    _set_ink(pdf)
    cy = y + band_h + 1

    # Civilization name
    civ_names = {
        "compact": "Compact", "keth": "Keth", "veshan": "Veshan",
        "orryn": "Orryn", "reach": "Reach",
    }
    pdf.set_font("Helvetica", "", FONT_TINY)
    pdf.set_xy(x + CARD_PADDING, cy)
    pdf.cell(CARD_W - 2 * CARD_PADDING, 3,
             f"Sector: {civ_names.get(region, region)}  |  Dock: {port_fee} cr")

    # Exports (what they sell cheap)
    pdf.set_xy(x + CARD_PADDING, cy + 4)
    pdf.set_font("Helvetica", "B", FONT_TINY)
    pdf.cell(14, 3, "SELLS:")
    pdf.set_font("Helvetica", "", FONT_TINY)
    export_names = [_short_good_name(e) for e in exports[:4]]
    pdf.cell(CARD_W - 2 * CARD_PADDING - 14, 3, ", ".join(export_names))

    # Imports (what they buy high)
    pdf.set_xy(x + CARD_PADDING, cy + 7.5)
    pdf.set_font("Helvetica", "B", FONT_TINY)
    pdf.cell(14, 3, "WANTS:")
    pdf.set_font("Helvetica", "", FONT_TINY)
    import_names = [_short_good_name(i) for i in imports[:4]]
    pdf.cell(CARD_W - 2 * CARD_PADDING - 14, 3, ", ".join(import_names))


# Backward compat alias
def draw_port_card(pdf, x, y, name, region="", features=None, exports=None,
                   imports=None, port_fee=0):
    draw_station_card(
        pdf, x, y, name,
        civilization=region,
        features=features or [],
        produces=exports or [],
        demands=imports or [],
        docking_fee=port_fee,
    )


# ---------------------------------------------------------------------------
# Quarter card  -- world-state rhythm (replaces season)
# ---------------------------------------------------------------------------

def draw_quarter_card(
    pdf: FPDF,
    x: float,
    y: float,
    quarter: str,
    rounds: str,
    effects: list[str],
) -> None:
    """Draw a quarter card (world-state rhythm)."""
    _draw_card_frame(pdf, x, y)

    quarter_colors = {
        "Scarcity":     (140, 120, 70),    # amber  -- shortage pressure
        "Convoy":       (90, 120, 100),    # muted green  -- managed movement
        "Sanctions":    (120, 90, 90),     # rust  -- restriction
        "Claims":       (100, 100, 125),   # cold blue  -- institutional
    }
    color = quarter_colors.get(quarter, INK)
    cy = _draw_title_band(pdf, x, y, quarter, f"Rounds {rounds}", color)

    pdf.set_font("Helvetica", "", FONT_BODY)
    _set_ink(pdf)
    for i, effect in enumerate(effects):
        pdf.set_xy(x + CARD_PADDING, cy + 3 + i * 5)
        pdf.multi_cell(CARD_W - 2 * CARD_PADDING, 4, f"- {effect}")


# Backward compat alias
draw_season_card = draw_quarter_card


def _short_good_name(good_id: str) -> str:
    """Convert a good_id to a short display name."""
    name_map = {
        "compact_alloys": "Alloys",
        "keth_biocrystal": "Bio-Crystal",
        "keth_organics": "Organics",
        "veshan_weapons": "Arms",
        "veshan_minerals": "Minerals",
        "orryn_data": "Data Pkgs",
        "orryn_brokered_goods": "Brokered",
        "medical_supplies": "Med Supply",
        "ancestor_tech": "Ancestor",
        "reach_contraband": "Salvage",
        "keth_bioweapons": "Bio-Agents",
        "unsealed_weapons": "Unsealed",
        "brood_silk": "Brood Silk",
        "black_seal_resin": "Seal Resin",
        "bond_plate": "Bond Plate",
        "reserve_grain": "Rsv Grain",
        "ration_grain": "Ration",
        "coolant_ampoules": "Coolant",
    }
    return name_map.get(good_id, good_id.replace("_", " ").title()[:12])
