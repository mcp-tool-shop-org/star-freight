"""Rulebook pages for the Print-and-Play PDF.

Renders the game rules as formatted PDF pages.
Feels like a printed shipping manual with sea flavor.
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
    """Section heading — serif-feel via bold Helvetica."""
    pdf.set_font("Helvetica", "B", FONT_HEADING)
    pdf.set_text_color(*INK)
    pdf.ln(4)
    pdf.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
    # Subtle rule line
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
    pdf.set_font("Helvetica", "", FONT_BODY)
    pdf.set_text_color(*INK)
    pdf.multi_cell(0, 4, text)
    pdf.ln(1)


def _bullet(pdf: FPDF, text: str) -> None:
    pdf.set_font("Helvetica", "", FONT_BODY)
    pdf.set_text_color(*INK)
    pdf.get_x()
    pdf.cell(5, 4, "-")
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

    # Title block
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(*INK)
    pdf.set_xy(MARGIN, 60)
    pdf.cell(PAGE_W - 2 * MARGIN, 15, "PORTLIGHT", align="C")

    pdf.set_font("Helvetica", "", FONT_TITLE)
    pdf.set_xy(MARGIN, 80)
    pdf.cell(PAGE_W - 2 * MARGIN, 10, "Print-and-Play Merchant Adventure", align="C")

    # Divider
    pdf.set_draw_color(*MEDIUM_GRAY)
    pdf.set_line_width(0.5)
    pdf.line(MARGIN + 40, 100, PAGE_W - MARGIN - 40, 100)

    # Tagline
    pdf.set_font("Helvetica", "", FONT_BODY)
    pdf.set_xy(MARGIN + 20, 110)
    pdf.multi_cell(PAGE_W - 2 * MARGIN - 40, 5,
                   "Sail between ports. Read shifting markets. Fulfill contracts. "
                   "Manage reputation and customs heat. Outmaneuver rivals. "
                   "Survive weather and danger.", align="C")

    # Game info
    pdf.set_font("Helvetica", "B", FONT_SUBHEADING)
    pdf.set_xy(MARGIN, 145)
    pdf.cell(PAGE_W - 2 * MARGIN, 8, "2-4 Players  |  ~90 Minutes  |  Ages 14+", align="C")

    # Footer
    pdf.set_font("Helvetica", "", FONT_SMALL)
    pdf.set_text_color(*MEDIUM_GRAY)
    pdf.set_xy(MARGIN, PAGE_H - 30)
    pdf.multi_cell(PAGE_W - 2 * MARGIN, 4,
                   "Generated from Portlight v2.0.0 world data.\n"
                   "For the digital game: pip install portlight", align="C")


def render_rules(pdf: FPDF) -> None:
    """Render the complete rulebook (multiple pages)."""
    pdf.add_page()

    _heading(pdf, "Round Structure")
    _body(pdf, "Each round has 4 phases, played in order:")
    _bullet(pdf, "Phase 1 - PORT: Buy/sell goods, take contracts, buy ships/infrastructure, repair, provision.")
    _bullet(pdf, "Phase 2 - SAIL: Move along routes using movement points. Multi-round voyages track remaining distance.")
    _bullet(pdf, "Phase 3 - ENCOUNTER: All players who sailed draw 1 event card. At Heat 5+, draw an extra Inspection.")
    _bullet(pdf, "Phase 4 - RESOLUTION: Complete contracts, tick deadlines, decay heat, pay upkeep, refill markets/contracts, advance season.")

    _check_page(pdf, 60)
    _heading(pdf, "Movement")
    _body(pdf, "Ships have speed (movement points per round). Routes have cost (1-4). "
          "If the route cost exceeds your remaining movement, place your ship on the route and continue next round. "
          "While at sea: skip Port phase, still draw Encounter cards. Season cards may add +1 to certain route costs.")

    _check_page(pdf, 50)
    _heading(pdf, "Market")
    _body(pdf, "Each port has a market display of 3-4 face-up goods cards. "
          "Port reference cards show which goods are cheap (buy here) and which are in demand (sell high here). "
          "Flood rule: selling 3+ of the same good at one port in one round reduces price by 2 silver per extra unit.")

    _check_page(pdf, 50)
    _heading(pdf, "Contracts")
    _body(pdf, "The contract board shows 4 face-up contracts. Each has goods required, destination, deadline (rounds), "
          "reward, and trust requirement. Hold up to 3 active contracts. Deadlines tick down each round. "
          "Deliver goods to the destination to collect reward and gain Trust. Failed contracts lose Trust.")

    _subheading(pdf, "Trust Ladder")
    _body(pdf, "Unproven (start) > New (1 completed) > Credible (3) > Reliable (6) > Trusted (10). "
          "Higher tiers unlock premium contracts.")

    _check_page(pdf, 60)
    _heading(pdf, "Reputation & Heat")

    _subheading(pdf, "Reputation (0-20)")
    _body(pdf, "+1 per contract completed. +1 per first lawful trade at a new port. "
          "Required for some infrastructure and victory paths.")

    _subheading(pdf, "Heat (0-20)")
    _body(pdf, "+1 per contraband carried per round. +1 per luxury sold above 10 silver margin. +2 per failed inspection. "
          "Decays -1 per round if no heat gained. -2 per round at Safe Harbor doing nothing.")
    _bullet(pdf, "Heat 5+: Draw extra Inspection event each round.")
    _bullet(pdf, "Heat 10+: Roll 2d6 on port arrival. 6 or less = denied entry.")
    _bullet(pdf, "Heat 15+: All sell prices reduced by 3 silver.")

    _check_page(pdf, 50)
    _heading(pdf, "Combat & Inspections")

    _subheading(pdf, "Pirate Encounter")
    _bullet(pdf, "FIGHT: Roll 2d6 + ship cannons vs pirate strength. Win = reward. Lose = lose 1-3 cargo + 2 hull.")
    _bullet(pdf, "PAY TRIBUTE: Lose silver (amount on card).")
    _bullet(pdf, "FLEE: Roll 2d6 >= (12 - ship speed). Success = escape. Fail = lose 1 cargo + 1 hull.")

    _subheading(pdf, "Inspection")
    _body(pdf, "Roll 2d6 - Heat (minimum 2). 7+ = passed. Below 7 = seized (lose all contraband, Heat +2). "
          "Smuggler captain rolls 2d6 and takes the better die.")

    _check_page(pdf, 50)
    _heading(pdf, "Ships")
    _body(pdf, "Start with a Sloop. Buy better ships at Shipyard ports. "
          "Sell your old ship for half price when upgrading. "
          "See Ship cards for full stats: Cargo (hand limit), Speed (movement), Hull (damage), Crew Cost (upkeep).")

    _check_page(pdf, 40)
    _heading(pdf, "Infrastructure")
    _body(pdf, "Warehouse (15 silver): store 5 goods at a port. "
          "Broker Office (25 silver): +1 silver on all trades in the region. "
          "License (10 silver): access restricted contracts/goods. "
          "All cost 1 silver/round upkeep. Max 1 of each per port.")

    _check_page(pdf, 40)
    _heading(pdf, "Seasons")
    _body(pdf, "Every 3 rounds the season advances: Spring > Summer > Autumn > Winter. "
          "Each season modifies one region's route costs and one good's demand. See Season cards.")

    _check_page(pdf, 60)
    _heading(pdf, "Victory")
    _body(pdf, "First player to complete a victory path wins immediately. "
          "If no one wins by round 15, highest score wins: Silver + (Reputation x 2) - Heat.")

    _subheading(pdf, "Lawful Trade House")
    _body(pdf, "Trust at Trusted + Reputation 12+ + Heat 3 or less + 3 contracts completed + 50 silver.")

    _subheading(pdf, "Shadow Network")
    _body(pdf, "2 contraband deliveries + Heat sustained at 8+ for 3 consecutive rounds + 40 silver + survived a seizure.")

    _subheading(pdf, "Oceanic Reach")
    _body(pdf, "Visited 4+ regions + Brigantine or better + contract completed in East Indies + 40 silver.")

    _subheading(pdf, "Commercial Empire")
    _body(pdf, "Infrastructure in 3+ regions + Trust at Reliable + 3 contracts completed + 60 silver.")


def render_player_aid(pdf: FPDF) -> None:
    """Render a one-page player aid / quick reference."""
    pdf.add_page()

    pdf.set_font("Helvetica", "B", FONT_HEADING)
    pdf.set_text_color(*INK)
    pdf.cell(0, 8, "PLAYER AID - Quick Reference", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    _subheading(pdf, "Turn Order")
    _body(pdf, "PORT > SAIL > ENCOUNTER > RESOLUTION")

    _subheading(pdf, "Port Actions")
    _bullet(pdf, "Buy goods: pay base price (modified by demand)")
    _bullet(pdf, "Sell goods: receive sell price. Flood if 3+ same good.")
    _bullet(pdf, "Take contract: must meet trust tier. Max 3 active.")
    _bullet(pdf, "Buy ship: Shipyard ports only. Sell old for half.")
    _bullet(pdf, "Buy infrastructure: Warehouse 15, Broker 25, License 10.")
    _bullet(pdf, "Repair: 1 silver per hull point.")
    _bullet(pdf, "Provision: 1 silver per 2 provisions.")

    _subheading(pdf, "Sailing")
    _bullet(pdf, "Movement points = ship speed. Route cost = 1-4.")
    _bullet(pdf, "At sea: skip Port phase, draw Encounter cards.")
    _bullet(pdf, "1 provision per round at sea. Out = lose 1 silver/round.")

    _subheading(pdf, "Heat Thresholds")
    _bullet(pdf, "5+ = extra Inspection each round")
    _bullet(pdf, "10+ = port denial risk (roll 2d6, 6- = denied)")
    _bullet(pdf, "15+ = all sell prices -3 silver")

    _subheading(pdf, "Trust Ladder")
    _body(pdf, "Unproven > New (1) > Credible (3) > Reliable (6) > Trusted (10)")

    _subheading(pdf, "Victory Paths")
    _bullet(pdf, "Lawful Trade House: Trusted + Rep 12+ + Heat <=3 + 3 contracts + 50 silver")
    _bullet(pdf, "Shadow Network: 2 contraband + Heat 8+ x3 rounds + 40 silver + survived seizure")
    _bullet(pdf, "Oceanic Reach: 4 regions + Brigantine+ + EI contract + 40 silver")
    _bullet(pdf, "Commercial Empire: 3 region infra + Reliable + 3 contracts + 60 silver")
    _bullet(pdf, "Round 15 fallback: Silver + (Rep x 2) - Heat")


def render_score_tracks(pdf: FPDF) -> None:
    """Render printable score track sheets."""
    pdf.add_page()

    pdf.set_font("Helvetica", "B", FONT_HEADING)
    pdf.set_text_color(*INK)
    pdf.cell(0, 8, "SCORE TRACKS", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Draw track grids for each player (4 players)
    for player_num in range(1, 5):
        _check_page(pdf, 55)
        pdf.set_font("Helvetica", "B", FONT_SUBHEADING)
        pdf.cell(0, 6, f"Player {player_num}: ________________", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

        y = pdf.get_y()
        _draw_track(pdf, MARGIN, y, "Silver", 20, step=5)
        _draw_track(pdf, MARGIN, y + 10, "Reputation", 20)
        _draw_track(pdf, MARGIN, y + 20, "Heat", 20)
        _draw_track(pdf, MARGIN, y + 30, "Trust", 5,
                    labels=["Unproven", "New", "Credible", "Reliable", "Trusted"])
        pdf.set_y(y + 45)


def _draw_track(
    pdf: FPDF,
    x: float,
    y: float,
    label: str,
    max_val: int,
    step: int = 1,
    labels: list[str] | None = None,
) -> None:
    """Draw a numbered track row."""
    pdf.set_font("Helvetica", "B", FONT_SMALL)
    pdf.set_text_color(*INK)
    pdf.set_xy(x, y)
    pdf.cell(22, 8, label)

    box_w = min(8, (PAGE_W - 2 * MARGIN - 24) / (max_val + 1))
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
        for i in range(0, max_val + 1, step):
            pdf.set_draw_color(*MEDIUM_GRAY)
            pdf.set_line_width(0.2)
            idx = i // step
            pdf.rect(bx + idx * (box_w + 1), y, box_w, 8, style="D")
            pdf.set_xy(bx + idx * (box_w + 1), y + 1)
            pdf.cell(box_w, 6, str(i), align="C")
