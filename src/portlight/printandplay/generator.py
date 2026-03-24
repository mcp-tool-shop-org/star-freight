"""Main PDF generator for the Star Freight Print-and-Play kit.

Orchestrates all components: cover, rulebook, board, cards, tracks.
Pulls content from Star Freight's structured dataclasses where available,
falls back to tabletop-specific data in assets.py for game elements
that exist only in the board game layer.

Content sources:
- Star Freight stations, lanes, goods, contracts → SLICE data
- Vessel stats, captain archetypes → assets.py (tabletop-specific)
- Pressure deck → built here (institutional + scarcity + hazard events)
- Quarter deck → built here (world-state rhythm)
"""

from __future__ import annotations

from pathlib import Path

from portlight.printandplay.assets import (
    CARD_GAP,
    CARD_H,
    CARD_W,
    CARDS_PER_ROW,
    COMPACT_CARD_H,
    FONT_HEADING,
    INK,
    MARGIN,
    PAGE_H,
    VESSEL_TABLETOP,
    CAPTAIN_TABLETOP,
    tabletop_price,
)


def generate(output: Path | None = None) -> Path:
    """Generate the complete Star Freight Print-and-Play PDF kit.

    Returns the path to the generated PDF.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        raise RuntimeError(
            "fpdf2 is required for PDF generation. "
            "Install it with: pip install portlight[printandplay]"
        )

    # --- Content sourcing ---
    # Try Star Freight content first, fall back to Portlight legacy
    try:
        from portlight.content.star_freight import (
            SLICE_STATIONS as SF_STATIONS,
            SLICE_LANES as SF_LANES,
            SLICE_GOODS as SF_GOODS,
        )
        stations = SF_STATIONS
        lanes = SF_LANES
        goods = SF_GOODS
        use_star_freight = True
    except ImportError:
        from portlight.content.ports import PORTS as stations
        from portlight.content.routes import ROUTES as lanes
        from portlight.content.goods import GOODS as goods
        use_star_freight = False

    # Contracts  -- try Star Freight, fall back to Portlight
    try:
        from portlight.content.contracts import TEMPLATES
        contracts = TEMPLATES
    except ImportError:
        contracts = []

    from portlight.printandplay.board import draw_board
    from portlight.printandplay.cards import (
        draw_captain_card,
        draw_contract_card,
        draw_pressure_card,
        draw_goods_card,
        draw_station_card,
        draw_quarter_card,
        draw_vessel_card,
    )
    from portlight.printandplay.rules import (
        render_cover,
        render_player_aid,
        render_rules,
        render_score_tracks,
    )

    pdf = FPDF(unit="mm", format="Letter")
    pdf.set_auto_page_break(auto=True, margin=MARGIN)

    # --- Cover ---
    render_cover(pdf)

    # --- Rulebook ---
    render_rules(pdf)

    # --- Game Board (landscape) ---
    draw_board(pdf, stations, lanes)

    # --- Captain Cards ---
    _add_section_header(pdf, "CAPTAIN CARDS")
    col = 0
    for cap_id, cap in CAPTAIN_TABLETOP.items():
        x = MARGIN + col * (CARD_W + CARD_GAP)
        y = pdf.get_y()
        draw_captain_card(
            pdf, x, y,
            name=cap["name"],
            home_station=cap.get("home_station", cap.get("home_port", "")),
            credits=cap.get("credits", cap.get("silver", 0)),
            fuel=cap.get("fuel", cap.get("provisions", 0)),
            heat=cap["heat"],
            ability=cap["ability"],
            weakness=cap["weakness"],
            life=cap.get("life", ""),
        )
        col += 1
        if col >= CARDS_PER_ROW:
            col = 0
            pdf.set_y(y + CARD_H + CARD_GAP)

    # --- Vessel Cards ---
    _add_section_header(pdf, "VESSEL CARDS")
    col = 0
    row_y = pdf.get_y()
    for vessel_id, vessel in VESSEL_TABLETOP.items():
        if col >= CARDS_PER_ROW:
            col = 0
            row_y += CARD_H + CARD_GAP
            if row_y + CARD_H > PAGE_H - MARGIN:
                pdf.add_page()
                row_y = MARGIN + 10
        x = MARGIN + col * (CARD_W + CARD_GAP)
        draw_vessel_card(
            pdf, x, row_y,
            name=vessel["name"],
            vessel_class=vessel["class"],
            stats={
                "cargo": vessel["cargo"],
                "burn": vessel["burn"],
                "hull": vessel["hull"],
                "crew_slots": vessel["crew_slots"],
                "price": vessel["price"],
                "hardpoints": vessel["hardpoints"],
            },
            flavor=vessel.get("flavor", ""),
        )
        col += 1
    pdf.set_y(row_y + CARD_H + CARD_GAP)

    # --- Goods Cards (2 copies each) ---
    _add_section_header(pdf, "GOODS CARDS")
    col = 0
    row_y = pdf.get_y()
    for good_id, good in goods.items():
        # Get good properties (handle both dataclass and dict-like)
        g_name = getattr(good, "name", good_id.replace("_", " ").title())
        g_cat = getattr(good, "category", "commodity")
        if hasattr(g_cat, "value"):
            g_cat = g_cat.value
        g_price = getattr(good, "base_price", 10)
        g_origin = getattr(good, "origin_civ", "")

        for _copy in range(2):
            if col >= CARDS_PER_ROW:
                col = 0
                row_y += CARD_H + CARD_GAP
                if row_y + CARD_H > PAGE_H - MARGIN:
                    pdf.add_page()
                    row_y = MARGIN + 2
            x = MARGIN + col * (CARD_W + CARD_GAP)
            draw_goods_card(
                pdf, x, row_y,
                name=g_name,
                category=g_cat,
                base_price=g_price,
                tabletop_price=tabletop_price(g_price),
                origin_civ=g_origin,
            )
            col += 1
    pdf.set_y(row_y + CARD_H + CARD_GAP)

    # --- Contract Cards ---
    _add_section_header(pdf, "CONTRACT CARDS")
    col = 0
    row_y = pdf.get_y()
    for tmpl in contracts[:24]:
        if col >= CARDS_PER_ROW:
            col = 0
            row_y += CARD_H + CARD_GAP
            if row_y + CARD_H > PAGE_H - MARGIN:
                pdf.add_page()
                row_y = MARGIN + 2
        x = MARGIN + col * (CARD_W + CARD_GAP)
        goods_name = tmpl.goods_pool[0].replace("_", " ").title() if tmpl.goods_pool else "Mixed"
        qty = f"{tmpl.quantity_min}-{tmpl.quantity_max}"
        reward = str(max(1, round(tmpl.reward_per_unit * (tmpl.quantity_min + tmpl.quantity_max) / 2 / 10)))
        deadline = str(max(2, round(tmpl.deadline_days / 8)))
        flavor = getattr(tmpl, "cultural_flavor", "") or ""
        draw_contract_card(
            pdf, x, row_y,
            title=tmpl.title_pattern.replace("{destination}", "Dest"),
            goods=goods_name,
            qty_range=qty,
            reward=reward,
            deadline=deadline,
            trust=tmpl.trust_requirement,
            flavor=flavor,
        )
        col += 1
    pdf.set_y(row_y + CARD_H + CARD_GAP)

    # --- Pressure Cards (replaces Event Cards) ---
    _add_section_header(pdf, "PRESSURE CARDS")
    pressures = _build_pressure_deck()
    col = 0
    row_y = pdf.get_y()
    for p in pressures:
        if col >= CARDS_PER_ROW:
            col = 0
            row_y += CARD_H + CARD_GAP
            if row_y + CARD_H > PAGE_H - MARGIN:
                pdf.add_page()
                row_y = MARGIN + 2
        x = MARGIN + col * (CARD_W + CARD_GAP)
        draw_pressure_card(pdf, x, row_y, **p)
        col += 1
    pdf.set_y(row_y + CARD_H + CARD_GAP)

    # --- Quarter Cards (replaces Season Cards) ---
    _add_section_header(pdf, "QUARTER CARDS")
    quarters = _build_quarter_deck()
    col = 0
    row_y = pdf.get_y()
    for q in quarters:
        if col >= CARDS_PER_ROW:
            col = 0
            row_y += CARD_H + CARD_GAP
            if row_y + CARD_H > PAGE_H - MARGIN:
                pdf.add_page()
                row_y = MARGIN + 2
        x = MARGIN + col * (CARD_W + CARD_GAP)
        draw_quarter_card(pdf, x, row_y, **q)
        col += 1
    pdf.set_y(row_y + CARD_H + CARD_GAP)

    # --- Station Reference Cards (compact) ---
    _add_section_header(pdf, "STATION REFERENCE CARDS")
    col = 0
    row_y = pdf.get_y()
    for sid, station in stations.items():
        if col >= CARDS_PER_ROW:
            col = 0
            row_y += COMPACT_CARD_H + CARD_GAP
            if row_y + COMPACT_CARD_H > PAGE_H - MARGIN:
                pdf.add_page()
                row_y = MARGIN + 2
        x = MARGIN + col * (CARD_W + CARD_GAP)

        # Handle both Star Freight Station and Portlight Port objects
        s_name = getattr(station, "name", sid)
        s_civ = (getattr(station, "civilization", None)
                 or getattr(station, "sector", None)
                 or getattr(station, "region", None)
                 or "")
        s_services = getattr(station, "services", [])
        s_produces = getattr(station, "produces", [])
        s_demands = getattr(station, "demands", [])
        s_fee = getattr(station, "docking_fee", 0) or getattr(station, "port_fee", 0)

        # If Portlight port, derive exports/imports from market affinity
        if not s_produces and hasattr(station, "market"):
            s_produces = [
                slot.good_id.replace("_", " ").title()
                for slot in station.market
                if slot.local_affinity >= 1.3
            ]
            s_demands = [
                slot.good_id.replace("_", " ").title()
                for slot in station.market
                if slot.local_affinity <= 0.65
            ]

        draw_station_card(
            pdf, x, row_y,
            name=s_name,
            civilization=s_civ,
            services=s_services,
            produces=s_produces,
            demands=s_demands,
            docking_fee=s_fee,
        )
        col += 1

    # --- Player Aid ---
    render_player_aid(pdf)

    # --- Score Tracks ---
    render_score_tracks(pdf)

    # --- Output ---
    if output is None:
        output = Path("star-freight-print-and-play.pdf")
    pdf.output(str(output))
    return output


def _add_section_header(pdf, title: str) -> None:
    """Add a section header, starting a new page if needed."""
    if pdf.get_y() > PAGE_H - MARGIN - 30:
        pdf.add_page()
    else:
        pdf.ln(4)
    pdf.set_font("Helvetica", "B", FONT_HEADING)
    pdf.set_text_color(*INK)
    pdf.cell(0, 8, title, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def _build_pressure_deck() -> list[dict]:
    """Build the ~40 card pressure deck.

    NOT weather with space nouns. These are the forces that shape
    a working captain's life in the Threshold:
    - Inspection (institutional authority reaching into your hold)
    - Scarcity (shortage economics reshaping route value)
    - Piracy (lawless violence from the Reach and contested lanes)
    - Convoy (managed movement  -- protection that costs freedom)
    - Hazard (lane terrain  -- debris, radiation, navigation danger)
    - Political (house challenges, debt calls, factional pressure)
    - Market (trade shifts, broker intelligence, supply disruption)
    """
    pressures: list[dict] = []

    # --- Inspection (8)  -- authority reaching into your hold ---
    inspection = [
        ("Customs Sweep", "Roll 2d6 - Heat (min 2). 7+ = passed. Below 7 = cargo flagged for seizure at next Compact station. Heat +1."),
        ("Customs Sweep", "Roll 2d6 - Heat (min 2). 7+ = passed. Below 7 = cargo flagged for seizure at next Compact station. Heat +1."),
        ("Customs Sweep", "Roll 2d6 - Heat (min 2). 7+ = passed. Below 7 = cargo flagged for seizure at next Compact station. Heat +1."),
        ("Bonded Cargo Audit", "If carrying goods without a Bond Plate, lose 1 cargo card and Heat +2. With Bond Plate: no effect."),
        ("Manifest Discrepancy", "Roll 2d6 - Heat - 1 (min 2). 7+ = clerical error, no penalty. Below 7 = cargo held pending review. Skip next Dock phase."),
        ("Seizure Order", "If Heat 8+: all contraband confiscated, Heat +3, Standing with Compact -2. If Heat below 8: routine check, no effect."),
        ("Diplomatic Clearance", "Heat -2 (min 0). An Orryn broker vouches for your cargo. Standing with Orryn +1."),
        ("Patrol Hail", "Heat +1. Compact patrol logs your position and heading. No other effect  -- but they're watching."),
    ]
    for title, effect in inspection:
        pressures.append({"title": title, "category": "Inspection", "effect": effect})

    # --- Scarcity (7)  -- shortage economics ---
    scarcity = [
        ("Shortage Spike", "Provision goods sell for +3 credits at your destination this round. Demand is visible  -- everyone adjusts."),
        ("Shortage Spike", "Provision goods sell for +3 credits at your destination this round. Demand is visible  -- everyone adjusts."),
        ("Supply Chain Break", "Remove 1 goods card from the nearest station's market display. Scarcity cascades."),
        ("Rationing Declared", "All provision goods at Compact and Keth stations cost +2 credits to buy. Lasts until next Quarter change."),
        ("Relief Priority", "If carrying provision goods: skip to front of any convoy queue. If not: lose 1 turn waiting."),
        ("Profiteer Scrutiny", "If you sold provision goods above base price last round: Heat +2. The system remembers."),
        ("Coolant Crisis", "Stations without Coolant Ampoules in their market close repair services this round. Plan accordingly."),
    ]
    for title, effect in scarcity:
        pressures.append({"title": title, "category": "Scarcity", "effect": effect})

    # --- Piracy (7)  -- lawless violence ---
    piracy = [
        ("Pirate Ambush", "Pirate strength: 8. Fight (2d6 + hardpoints >= 8), Pay Toll (5 credits), or Evade (2d6 >= 12 - speed)."),
        ("Pirate Ambush", "Pirate strength: 10. Fight (2d6 + hardpoints >= 10), Pay Toll (8 credits), or Evade (2d6 >= 12 - speed)."),
        ("Pirate Raid", "Pirate strength: 12. Fight (2d6 + hardpoints >= 12), Pay Toll (10 credits), or Evade (2d6 >= 12 - speed). Win reward: 8 credits salvage."),
        ("Lane Blockade", "Pay 4 credit toll or reroute: add +1 burn to current lane. Reach factions don't negotiate."),
        ("Lane Blockade", "Pay 6 credit toll or reroute: add +1 burn to current lane. Reach factions don't negotiate."),
        ("Black Market Opening", "A Reach contact offers contraband at half price. Buy 1 contraband card for half base. Heat +1."),
        ("Pirate Parley", "A pirate captain offers a deal: deliver 1 cargo to a Reach station. Accept: Heat -2, gain 5 credits. Refuse: no penalty but they remember."),
    ]
    for title, effect in piracy:
        pressures.append({"title": title, "category": "Piracy", "effect": effect})

    # --- Convoy (5)  -- managed movement ---
    convoy = [
        ("Convoy Assignment", "You are assigned convoy escort priority. +2 credits if you reach destination this round. Cannot deviate from lane."),
        ("Convoy Delay", "Convoy schedule slips. Lose 1 fuel waiting. If you break formation: Heat +1 and convoy bonus lost."),
        ("Convoy Refusal", "Your priority is bumped. Another captain's cargo was deemed more critical. Lose your convoy slot. Find another route or wait."),
        ("Escort Premium", "If traveling a Convoy lane: +3 credits on any contract completed this round. Safety has value."),
        ("Formation Scan", "All cargo in convoy formation is scanned. If carrying contraband in a convoy lane: auto-flagged. No roll."),
    ]
    for title, effect in convoy:
        pressures.append({"title": title, "category": "Convoy", "effect": effect})

    # --- Hazard (5)  -- lane terrain ---
    hazard = [
        ("Debris Field", "Lose 1 hull point. If hull at 0, vessel disabled  -- towed to nearest station, pay 10 credits."),
        ("Debris Field", "Lose 1 hull point. If hull at 0, vessel disabled  -- towed to nearest station, pay 10 credits."),
        ("Radiation Pocket", "Lose 1 cargo card (your choice) OR 2 hull points. Shielded cargo (Bond Plate) is protected."),
        ("Comms Blackout", "Cannot trade, take contracts, or communicate this round. You're blind. Skip to Resolve."),
        ("Navigation Hazard", "Your current lane costs +1 burn. If you can't pay, you are stranded."),
    ]
    for title, effect in hazard:
        pressures.append({"title": title, "category": "Hazard", "effect": effect})

    # --- Political (4)  -- house + faction pressure ---
    political = [
        ("House Challenge", "A Veshan house issues an honor challenge. Accept: fight 2d6 + hardpoints vs 8. Win = +3 Veshan standing. Lose = -1 but respected. Refuse = -3 ALL Veshan houses."),
        ("Debt Call", "A Veshan house calls in a debt. Pay 5 credits or deliver 1 cargo to their station within 2 rounds. Failure: -3 Veshan standing."),
        ("Keth Calendar Shift", "The Keth season changes. If at a Keth station: market display refreshes. If carrying Keth goods: demand shifts by +2 or -2 credits (flip a coin)."),
        ("Compact Audit", "If Standing with Compact is negative: pay 3 credits administrative fine or Heat +2. If Standing is positive: no effect."),
    ]
    for title, effect in political:
        pressures.append({"title": title, "category": "Political", "effect": effect})

    # --- Market (4)  -- trade shifts ---
    market = [
        ("Broker Intelligence", "An Orryn contact reveals: peek at top 2 goods cards. Place one on any station's market display."),
        ("Broker Intelligence", "An Orryn contact reveals: peek at top 2 goods cards. Place one on any station's market display."),
        ("Trade Wind", "If you complete a contract this round: +2 credits bonus. Timing rewards."),
        ("Salvage Find", "Draw 1 card from the goods deck. Add it to your cargo for free (if you have space). The Threshold provides."),
    ]
    for title, effect in market:
        pressures.append({"title": title, "category": "Market", "effect": effect})

    return pressures


def _build_quarter_deck() -> list[dict]:
    """Build the 4-card quarter deck (world-state rhythm).

    NOT seasons renamed. These are pressure windows that reshape
    which routes are valuable, which contracts are urgent, and
    which institutions are paying attention.
    """
    return [
        {
            "quarter": "Scarcity",
            "rounds": "1-3",
            "effects": [
                "Provision goods demand +3 credits at all stations",
                "Convoy lanes activate: escorts available, schedule-bound",
                "Compact inspections +1 frequency on non-convoy routes",
            ],
        },
        {
            "quarter": "Convoy",
            "rounds": "4-6",
            "effects": [
                "Convoy priority contracts appear: +2 reward for escorted delivery",
                "Non-convoy routes: piracy encounter rate +1 card",
                "Orryn broker fees reduced by 1 credit (they're flush)",
            ],
        },
        {
            "quarter": "Sanctions",
            "rounds": "7-9",
            "effects": [
                "Compact restricts cross-border trade: +2 burn on Compact-Reach lanes",
                "Gray bypass lanes open: lower burn but higher piracy risk",
                "Inspection rate doubles on Inspected lanes",
            ],
        },
        {
            "quarter": "Claims",
            "rounds": "10-12",
            "effects": [
                "Veshan house debt calls: all players with Veshan standing check debt",
                "Compact audit cycle: all players with negative Compact standing pay fine",
                "Keth emergence: bio-crystal prices peak, cultural access opens",
            ],
        },
    ]


# Backward compat
def _build_event_deck() -> list[dict]:
    """Backward-compatible alias for _build_pressure_deck."""
    return _build_pressure_deck()
