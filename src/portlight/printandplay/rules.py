"""Rulebook pages for the Star Freight Print-and-Play.

This is not a terminology patch of a maritime game.
The rules teach a space merchant-political world where:
- lanes are governed corridors under different kinds of pressure
- stations belong to civilizations with different social logic
- inspections, seizures, and convoys are institutional forces
- scarcity reshapes route value and contract urgency
- crew composition determines access, not just bonuses
- the captain's posture (relief / gray / honor) emerges from choices
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from portlight.printandplay.assets import (
    FONT_BODY,
    FONT_HEADING,
    FONT_SMALL,
    FONT_SUBHEADING,
    FONT_TINY,
    FONT_TITLE,
    INK,
    MARGIN,
    MEDIUM_GRAY,
    PAGE_H,
    PAGE_W,
    PAPER,
)

if TYPE_CHECKING:
    from fpdf import FPDF


def _heading(pdf: FPDF, text: str) -> None:
    """Section heading."""
    pdf.set_font("Helvetica", "B", FONT_HEADING)
    pdf.set_text_color(*INK)
    pdf.ln(4)
    pdf.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
    y = pdf.get_y()
    pdf.set_draw_color(*MEDIUM_GRAY)
    pdf.set_line_width(0.3)
    pdf.line(MARGIN, y, PAGE_W - MARGIN, y)
    pdf.ln(2)


def _subheading(pdf: FPDF, text: str) -> None:
    pdf.set_font("Helvetica", "B", FONT_SUBHEADING)
    pdf.set_text_color(*INK)
    pdf.ln(2)
    pdf.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def _body(pdf: FPDF, text: str) -> None:
    _check_page(pdf, 12)
    pdf.set_font("Helvetica", "", FONT_BODY)
    pdf.set_text_color(*INK)
    pdf.set_x(MARGIN)
    pdf.multi_cell(PAGE_W - 2 * MARGIN, 4, text)
    pdf.ln(1)


def _bullet(pdf: FPDF, text: str) -> None:
    _check_page(pdf, 10)
    pdf.set_font("Helvetica", "", FONT_BODY)
    pdf.set_text_color(*INK)
    x = MARGIN
    y = pdf.get_y()
    pdf.set_xy(x, y)
    pdf.cell(5, 4, "-")
    pdf.set_xy(x + 5, y)
    pdf.multi_cell(PAGE_W - 2 * MARGIN - 5, 4, text)


def _check_page(pdf: FPDF, needed: float = 30) -> None:
    """Add a new page if we're running low on space."""
    if pdf.get_y() > PAGE_H - MARGIN - needed:
        pdf.add_page()


def render_cover(pdf: FPDF) -> None:
    """Render the cover page."""
    pdf.add_page()
    pdf.set_fill_color(*PAPER)
    pdf.rect(0, 0, PAGE_W, PAGE_H, style="F")

    # Title
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(*INK)
    pdf.set_xy(MARGIN, 55)
    pdf.cell(PAGE_W - 2 * MARGIN, 15, "STAR FREIGHT", align="C")

    pdf.set_font("Helvetica", "", FONT_TITLE)
    pdf.set_xy(MARGIN, 75)
    pdf.cell(PAGE_W - 2 * MARGIN, 10,
             "Print-and-Play Space Merchant RPG", align="C")

    # Divider
    pdf.set_draw_color(*MEDIUM_GRAY)
    pdf.set_line_width(0.5)
    pdf.line(MARGIN + 40, 95, PAGE_W - MARGIN - 40, 95)

    # Tagline
    pdf.set_font("Helvetica", "", FONT_BODY)
    pdf.set_xy(MARGIN + 15, 105)
    pdf.multi_cell(PAGE_W - 2 * MARGIN - 30, 5,
                   "Five civilizations. One star system. No neutral ground. "
                   "Haul freight through governed lanes where inspections, "
                   "shortages, and house politics reshape every run. "
                   "Your crew determines your access. Your reputation "
                   "determines your life.", align="C")

    # Game info
    pdf.set_font("Helvetica", "B", FONT_SUBHEADING)
    pdf.set_xy(MARGIN, 145)
    pdf.cell(PAGE_W - 2 * MARGIN, 8,
             "2-4 Players  |  ~90 Minutes  |  Ages 14+", align="C")

    # Subtitle
    pdf.set_font("Helvetica", "", FONT_SMALL)
    pdf.set_text_color(*MEDIUM_GRAY)
    pdf.set_xy(MARGIN, 160)
    pdf.multi_cell(PAGE_W - 2 * MARGIN, 4,
                   "Trade. Decide. Survive.", align="C")

    # Footer
    pdf.set_font("Helvetica", "", FONT_SMALL)
    pdf.set_text_color(*MEDIUM_GRAY)
    pdf.set_xy(MARGIN, PAGE_H - 30)
    pdf.multi_cell(PAGE_W - 2 * MARGIN, 4,
                   "Generated from Star Freight world data.\n"
                   "Digital game: pip install portlight[tui]", align="C")


def render_rules(pdf: FPDF) -> None:
    """Render the complete rulebook."""
    pdf.add_page()

    # --- ROUND STRUCTURE ---
    _heading(pdf, "Round Structure")
    _body(pdf, "Each round has 4 phases, played in order:")
    _bullet(pdf, "Phase 1 - DOCK: Buy/sell goods, take contracts, hire crew, "
            "repair hull, refuel. Station services and prices depend on the "
            "civilization that governs it.")
    _bullet(pdf, "Phase 2 - LAUNCH: Choose a lane and burn fuel to travel. "
            "Burn cost depends on lane distance and your vessel. Multi-round "
            "transits track remaining distance. While in transit: skip Dock, "
            "still draw Pressure cards.")
    _bullet(pdf, "Phase 3 - PRESSURE: All players in transit draw 1 Pressure "
            "card. At Heat 5+, draw an additional Inspection card. Lane "
            "identity may trigger specific pressure types.")
    _bullet(pdf, "Phase 4 - RESOLVE: Complete contracts, tick deadlines, "
            "decay Heat (-1 if no new Heat), pay crew wages, advance the "
            "Quarter track, apply scarcity/convoy shifts.")

    # --- LANES ---
    _check_page(pdf, 60)
    _heading(pdf, "Lanes")
    _body(pdf, "Lanes connect stations. Each lane has a burn cost (1-4 fuel), "
          "a controlling civilization, and a pressure identity that tells you "
          "what kind of corridor you're entering:")
    _bullet(pdf, "INSPECTED  -- Compact-monitored. High contraband risk. Safe from "
            "piracy but your manifest better be clean.")
    _bullet(pdf, "CONVOY  -- Protected relief routes. Safe but schedule-bound. "
            "You move when the convoy moves. Contraband is suicidal.")
    _bullet(pdf, "CONTESTED  -- Disputed territory. Multiple factions claim "
            "jurisdiction. Ambush risk. Political consequences for fighting.")
    _bullet(pdf, "HAZARD  -- Debris fields, asteroid belts, nebulae. Hull damage "
            "risk. Navigation skill matters. Cover for smuggling.")
    _bullet(pdf, "GRAY  -- Unpoliced. Nobody watches, nobody helps. The Reach "
            "operates here. Highest danger, lowest scrutiny.")
    _body(pdf, "If your burn cost exceeds remaining fuel, you are stranded. "
          "Stranded vessels draw 2 Pressure cards per round until rescued or "
          "refueled by another player.")

    # --- STATIONS ---
    _check_page(pdf, 60)
    _heading(pdf, "Stations")
    _body(pdf, "Every station belongs to a civilization. That civilization's "
          "social logic governs what you can buy, who you can hire, and how "
          "trade works. Station reference cards show what each station sells "
          "cheap and buys high.")
    _subheading(pdf, "Civilization Summary")
    _bullet(pdf, "TERRAN COMPACT: Bureaucratic. Permits gate access. Safe "
            "markets, tight margins, heavy paperwork. Your disgrace started here.")
    _bullet(pdf, "KETH COMMUNION: Seasonal biology. Trade follows the Keth "
            "calendar. Harvest opens doors. Spawning restricts outsiders. "
            "Cultural missteps spread fast through all Keth stations.")
    _bullet(pdf, "VESHAN PRINCIPALITIES: Feudal honor. Direct confrontation, "
            "the Debt Ledger, house rivalries. They respect combat record "
            "and kept promises. Deception is the worst offense.")
    _bullet(pdf, "ORRYN DRIFT: Mobile brokers. Trade with everyone. The Telling "
            "(radical honesty ritual) gates access. Cutting them out saves "
            "money but costs intelligence and goodwill.")
    _bullet(pdf, "SABLE REACH: No law. Pirate factions, salvagers, outlaws. "
            "Reputation is the only currency. Highest risk, highest reward, "
            "only source of Ancestor tech.")

    # --- TRADE ---
    _check_page(pdf, 50)
    _heading(pdf, "Trade")
    _body(pdf, "Each station has a goods display of 3-4 face-up goods cards. "
          "Station cards show which goods are produced (buy cheap) and which "
          "are demanded (sell high). Goods carry political weight  -- carrying "
          "Veshan arms through Compact space is contraband. Carrying medical "
          "supplies during a shortage draws scrutiny about who authorized you.")
    _subheading(pdf, "Flood Rule")
    _body(pdf, "Selling 3+ of the same good at one station in one round "
          "reduces price by 2 credits per extra unit. Markets have memory.")

    # --- CONTRACTS ---
    _check_page(pdf, 50)
    _heading(pdf, "Contracts")
    _body(pdf, "The contract board shows 4 face-up contracts. Each has cargo "
          "required, destination, deadline (in quarters), reward, and a trust "
          "gate. Hold up to 3 active contracts. Deadlines tick down each round. "
          "Deliver goods to the destination to collect reward and gain Standing. "
          "Failed contracts lose Standing and may trigger seizure of bonded cargo.")
    _subheading(pdf, "Trust Ladder")
    _body(pdf, "Unknown (start) > Recognized (1 completed) > Credible (3) > "
          "Reliable (6) > Bonded (10). Higher tiers unlock premium contracts "
          "and convoy access. Trust is per-civilization, not global.")

    # --- STANDING AND HEAT ---
    _check_page(pdf, 60)
    _heading(pdf, "Standing & Heat")

    _subheading(pdf, "Standing (per civilization, -10 to +20)")
    _body(pdf, "Starts at 0 for most civilizations. Compact starts at -5 "
          "(your disgrace). +1 per contract completed for that civilization. "
          "+1 for first legitimate trade at a new station. Standing gates "
          "access: crew recruitment, restricted goods, premium contracts, "
          "and civilization-specific content.")

    _subheading(pdf, "Heat (0-20)")
    _body(pdf, "+1 per contraband carried per round. +1 per goods sold above "
          "threshold margin. +2 per failed inspection. +3 per seizure resisted. "
          "Decays -1 per round if no new Heat. -2 per round at a Drydock "
          "station doing nothing.")
    _bullet(pdf, "Heat 5+: Draw extra Inspection pressure card each round.")
    _bullet(pdf, "Heat 10+: Roll 2d6 on station arrival. 6 or less = denied "
            "docking at Compact and Keth stations.")
    _bullet(pdf, "Heat 15+: All sell prices reduced by 3 credits. Convoy "
            "access revoked.")

    # --- INSPECTIONS AND SEIZURES ---
    _check_page(pdf, 60)
    _heading(pdf, "Inspections & Seizures")

    _subheading(pdf, "Inspection")
    _body(pdf, "Roll 2d6 - Heat (minimum result 2). 7+ = passed. Below 7 = "
          "cargo flagged. Flagged cargo triggers a seizure check on next "
          "Compact station visit. Gray Runner captains may spend a falsified "
          "manifest to auto-pass one inspection per quarter.")

    _subheading(pdf, "Seizure")
    _body(pdf, "When flagged cargo reaches a Compact station: all contraband "
          "confiscated, Heat +3, Standing with Compact -2. If carrying bonded "
          "freight without a valid Bond Plate, lose the bonded cargo too. "
          "Seizure is not combat  -- it is paperwork. You cannot fight it at "
          "the station. You can contest it later at Registry Spindle if you "
          "have crew with Compact institutional knowledge.")

    # --- COMBAT ---
    _check_page(pdf, 50)
    _heading(pdf, "Combat")

    _subheading(pdf, "Pirate Encounter")
    _bullet(pdf, "FIGHT: Roll 2d6 + hardpoints vs pirate strength. Win = "
            "salvage reward. Lose = lose 1-3 cargo + hull damage.")
    _bullet(pdf, "PAY TOLL: Lose credits (amount on card). No Heat change.")
    _bullet(pdf, "EVADE: Roll 2d6 >= (12 - vessel speed). Success = escape. "
            "Fail = lose 1 cargo + 1 hull damage.")

    _subheading(pdf, "Veshan Challenge")
    _body(pdf, "Veshan pressure cards may issue an honor challenge. Accept: "
          "fight 1v1 (2d6 + hardpoints vs challenge strength). Win = +3 "
          "Standing with the issuing house. Lose = -1 Standing but respect "
          "earned. Refuse = -3 Standing with ALL Veshan houses.")

    # --- VESSELS ---
    _check_page(pdf, 50)
    _heading(pdf, "Vessels")
    _body(pdf, "Start with a Rustbucket. Buy better vessels at Drydock "
          "stations. Sell your old vessel for half price when upgrading. "
          "Vessels are not just stat blocks  -- they support different captain "
          "postures:")
    _bullet(pdf, "HAULER (Dray-Class): Volume freight. Convoy-compatible. "
            "The Relief captain's ship.")
    _bullet(pdf, "RUNNER (Kite-Class): Fast, light, forgettable. "
            "The Gray runner's ship.")
    _bullet(pdf, "WARBIRD (Talon-Class): Combat-ready. Escort and bounty "
            "work. The Honor captain's ship.")
    _bullet(pdf, "BULKFRAME (Mule-Class): Capital freight. The empire "
            "builder's ship.")

    # --- CREW ---
    _check_page(pdf, 40)
    _heading(pdf, "Crew")
    _body(pdf, "Your vessel has crew slots. Each crew member comes from a "
          "civilization and opens access to that civilization's restricted "
          "content  -- markets, contracts, cultural events. Crew is not a "
          "stat bonus. Crew is WHY you can dock, trade, and survive in "
          "territory that would otherwise lock you out. Crew wages are paid "
          "each round. Unpaid crew leave.")

    # --- QUARTERS ---
    _check_page(pdf, 40)
    _heading(pdf, "Quarters")
    _body(pdf, "Every 3 rounds the quarter advances. Quarters model "
          "world-state pressure, not generic seasons:")
    _bullet(pdf, "SCARCITY: Shortage spikes demand for provision goods. "
            "Route values shift. Scrutiny on who moves critical cargo.")
    _bullet(pdf, "CONVOY: Relief priority. Convoy lanes get escort. "
            "Non-convoy routes see increased piracy.")
    _bullet(pdf, "SANCTIONS: Compact restricts cross-border trade. "
            "Gray bypass lanes become profitable. Inspection rates rise.")
    _bullet(pdf, "CLAIMS: House activity. Veshan debt calls, Compact audits, "
            "institutional pressure. Standing checks more frequent.")

    # --- VICTORY ---
    _check_page(pdf, 60)
    _heading(pdf, "Victory")
    _body(pdf, "First player to complete a victory path wins. "
          "If no one wins by round 15, highest score: "
          "Credits + (highest Standing x 3) - Heat.")

    _subheading(pdf, "Bonded House (Relief path)")
    _body(pdf, "Trust at Bonded with any civilization + Standing 12+ with "
          "that civilization + Heat 3 or less + 4 contracts completed + "
          "50 credits.")

    _subheading(pdf, "Shadow Network (Gray path)")
    _body(pdf, "2 falsified manifests used + Heat sustained at 8+ for 3 "
          "consecutive rounds + 40 credits + survived a seizure without "
          "losing all cargo.")

    _subheading(pdf, "Threshold Reach (Explorer path)")
    _body(pdf, "Visited 4+ civilization sectors + Warbird or better vessel + "
          "contract completed in Sable Reach + 40 credits.")

    _subheading(pdf, "Commercial Empire (Builder path)")
    _body(pdf, "Crew from 3+ civilizations + Trust at Reliable with 2+ "
          "civilizations + 5 contracts completed + Bulkframe vessel + "
          "60 credits.")


def render_player_aid(pdf: FPDF) -> None:
    """Render a one-page player aid / quick reference."""
    pdf.add_page()

    pdf.set_font("Helvetica", "B", FONT_HEADING)
    pdf.set_text_color(*INK)
    pdf.cell(0, 8, "PLAYER AID - Quick Reference", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    _subheading(pdf, "Turn Order")
    _body(pdf, "DOCK > LAUNCH > PRESSURE > RESOLVE")

    _subheading(pdf, "Dock Actions")
    _bullet(pdf, "Buy goods: pay base price (station card shows what's cheap)")
    _bullet(pdf, "Sell goods: receive sell price. Flood rule if 3+ same good.")
    _bullet(pdf, "Take contract: must meet trust gate. Max 3 active.")
    _bullet(pdf, "Buy vessel: Drydock stations only. Sell old for half.")
    _bullet(pdf, "Hire crew: pay hire cost. Crew opens civilization access.")
    _bullet(pdf, "Repair: 2 credits per hull point.")
    _bullet(pdf, "Refuel: 1 credit per 2 fuel units.")

    _subheading(pdf, "Transit")
    _bullet(pdf, "Fuel = vessel's base supply. Burn = lane cost.")
    _bullet(pdf, "In transit: skip Dock, draw Pressure cards.")
    _bullet(pdf, "1 fuel consumed per round in transit beyond lane cost.")

    _subheading(pdf, "Heat Thresholds")
    _bullet(pdf, "5+ = extra Inspection each round")
    _bullet(pdf, "10+ = docking denial risk at Compact/Keth (roll 2d6, 6- = denied)")
    _bullet(pdf, "15+ = all sell prices -3 credits, convoy access revoked")

    _subheading(pdf, "Trust Ladder (per civilization)")
    _body(pdf, "Unknown > Recognized (1) > Credible (3) > Reliable (6) > Bonded (10)")

    _subheading(pdf, "Victory Paths")
    _bullet(pdf, "Bonded House: Bonded trust + Standing 12+ + Heat <=3 + 4 contracts + 50 cr")
    _bullet(pdf, "Shadow Network: 2 falsified + Heat 8+ x3 rounds + 40 cr + survived seizure")
    _bullet(pdf, "Threshold Reach: 4 sectors + Warbird+ + Reach contract + 40 cr")
    _bullet(pdf, "Commercial Empire: 3 civ crew + Reliable x2 + 5 contracts + Bulkframe + 60 cr")
    _bullet(pdf, "Round 15 fallback: Credits + (best Standing x 3) - Heat")

    _subheading(pdf, "Captain Postures")
    _bullet(pdf, "Relief: convoy access, provision bonuses, inspection scrutiny")
    _bullet(pdf, "Gray: falsified manifests, timing arbitrage, seizure exposure")
    _bullet(pdf, "Honor: challenge rights, escort premiums, volatile standing")


def render_score_tracks(pdf: FPDF) -> None:
    """Render printable score track sheets."""
    pdf.add_page()

    pdf.set_font("Helvetica", "B", FONT_HEADING)
    pdf.set_text_color(*INK)
    pdf.cell(0, 8, "SCORE TRACKS", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    for player_num in range(1, 5):
        _check_page(pdf, 65)
        pdf.set_font("Helvetica", "B", FONT_SUBHEADING)
        pdf.cell(0, 6, f"Player {player_num}: ________________",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

        y = pdf.get_y()
        _draw_track(pdf, MARGIN, y, "Credits", 20, step=5)
        _draw_track(pdf, MARGIN, y + 10, "Heat", 20)

        # Per-civilization standing tracks
        _draw_track(pdf, MARGIN, y + 20, "Compact", 20, offset=-5)
        _draw_track(pdf, MARGIN, y + 28, "Keth", 20)
        _draw_track(pdf, MARGIN, y + 36, "Veshan", 20)
        _draw_track(pdf, MARGIN, y + 44, "Orryn", 20)
        _draw_track(pdf, MARGIN, y + 52, "Reach", 20)

        _draw_track(pdf, MARGIN, y + 62, "Trust", 5,
                    labels=["Unknown", "Recog.", "Credible", "Reliable", "Bonded"])
        pdf.set_y(y + 75)


def _draw_track(
    pdf: FPDF,
    x: float,
    y: float,
    label: str,
    max_val: int,
    step: int = 1,
    labels: list[str] | None = None,
    offset: int = 0,
) -> None:
    """Draw a numbered track row."""
    pdf.set_font("Helvetica", "B", FONT_SMALL)
    pdf.set_text_color(*INK)
    pdf.set_xy(x, y)
    pdf.cell(22, 8, label)

    box_w = min(7, (PAGE_W - 2 * MARGIN - 24) / (max_val + 1))
    bx = x + 24

    if labels:
        pdf.set_font("Helvetica", "", FONT_TINY)
        for i, lbl in enumerate(labels):
            pdf.set_draw_color(*MEDIUM_GRAY)
            pdf.set_line_width(0.2)
            pdf.rect(bx + i * (box_w + 1), y, box_w, 8, style="D")
            pdf.set_xy(bx + i * (box_w + 1), y + 1)
            pdf.cell(box_w, 6, lbl, align="C")
    else:
        pdf.set_font("Helvetica", "", FONT_TINY)
        start = offset if offset else 0
        for i in range(start, max_val + 1, step):
            pdf.set_draw_color(*MEDIUM_GRAY)
            pdf.set_line_width(0.2)
            idx = (i - start) // step
            pdf.rect(bx + idx * (box_w + 1), y, box_w, 8, style="D")
            pdf.set_xy(bx + idx * (box_w + 1), y + 1)
            pdf.cell(box_w, 6, str(i), align="C")
