"""Visual constants for the Star Freight Print-and-Play kit.

Design law: industrial freight manifest + political tension + worn utility.
Not ocean, not clean sci-fi. A working star system under pressure.
Color is political  -- each civilization reads as a governed territory, not a scenic region.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Page dimensions (mm)  -- Letter size
# ---------------------------------------------------------------------------
PAGE_W = 215.9
PAGE_H = 279.4
MARGIN = 12.0

# ---------------------------------------------------------------------------
# Color palette  -- political, industrial, slightly tense
# ---------------------------------------------------------------------------

# Base colors (RGB tuples)
INK = (35, 35, 40)           # near-black with blue tint  -- institutional
LIGHT_GRAY = (175, 175, 170)
MEDIUM_GRAY = (115, 115, 110)
PAPER = (245, 243, 238)      # warm gray  -- recycled-paper feel
WHITE = (255, 255, 255)

# Civilization accent colors  -- each carries political identity
SECTOR_COLORS: dict[str, tuple[int, int, int]] = {
    "compact":  (95, 105, 125),   # slate  -- bureaucratic, cold, institutional
    "keth":     (110, 140, 100),  # muted chlorophyll  -- organic, seasonal, alive
    "veshan":   (155, 100, 80),   # burnt sienna  -- martial, stone, heat
    "orryn":    (130, 120, 145),  # dusty violet  -- shifting, broker, ambiguous
    "reach":    (85, 80, 75),     # carbon  -- no law, no color, just material
}

# Backward compat alias  -- board.py and cards.py reference this
REGION_COLORS = SECTOR_COLORS

# System colors
HEAT_COLOR = (170, 55, 45)       # red  -- scrutiny, exposure
STANDING_COLOR = (60, 120, 85)   # green  -- legitimacy, access
DAMAGE_COLOR = (140, 40, 40)     # dark red  -- hull, injury
CREDITS_COLOR = (160, 150, 100)  # tarnished gold  -- money is dirty

# Lane identity colors (for board iconography)
LANE_INSPECTION = (95, 105, 125)   # compact blue  -- monitored
LANE_CONVOY = (110, 140, 100)      # keth green  -- protected
LANE_CONTESTED = (155, 100, 80)    # veshan red  -- disputed
LANE_HAZARD = (140, 130, 80)       # amber  -- debris, terrain
LANE_GRAY = (85, 80, 75)          # reach dark  -- unpoliced

# ---------------------------------------------------------------------------
# Typography  -- sizes in points
# ---------------------------------------------------------------------------
FONT_TITLE = 18
FONT_HEADING = 14
FONT_SUBHEADING = 11
FONT_BODY = 9
FONT_SMALL = 7
FONT_TINY = 6

# ---------------------------------------------------------------------------
# Card dimensions (mm)  -- standard poker size (63.5 x 88.9)
# ---------------------------------------------------------------------------
CARD_W = 63.5
CARD_H = 88.9
CARD_PADDING = 3.0
CARD_CORNER_R = 2.0

# Compact card (half-height, for station references)
COMPACT_CARD_H = 44.0

# ---------------------------------------------------------------------------
# Board dimensions
# ---------------------------------------------------------------------------
BOARD_W = PAGE_W - 2 * MARGIN
BOARD_H = PAGE_H - 2 * MARGIN - 20  # leave room for title

# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------
CARDS_PER_ROW = 3
CARD_GAP = 3.0

# How many cards fit on a page
ROWS_PER_PAGE = int((PAGE_H - 2 * MARGIN) // (CARD_H + CARD_GAP))

# Compact cards per page
COMPACT_ROWS_PER_PAGE = int((PAGE_H - 2 * MARGIN) // (COMPACT_CARD_H + CARD_GAP))


# ---------------------------------------------------------------------------
# Lane distance tiers (travel days -> tabletop burn cost)
# ---------------------------------------------------------------------------
def lane_burn_cost(distance_days: int) -> int:
    """Convert digital lane distance to tabletop fuel burn (movement cost).

    Burn represents fuel + time + crew strain. Not just distance  --
    longer lanes cost more in every dimension.
    """
    if distance_days <= 2:
        return 1  # Local  -- same-sector hop
    elif distance_days <= 3:
        return 2  # Cross-sector  -- adjacent civilizations
    elif distance_days <= 4:
        return 3  # Long haul  -- remote or contested
    else:
        return 4  # Deep run  -- hostile or extreme distance


# Backward compat alias
route_movement_cost = lane_burn_cost


# ---------------------------------------------------------------------------
# Vessel stat blocks (tabletop-scaled)
# ---------------------------------------------------------------------------
# Posture vessels  -- each supports a different captain life.
# Not renamed galleons. Different campaign shapes.
VESSEL_TABLETOP: dict[str, dict[str, int | str]] = {
    "rustbucket": {
        "name": "Rustbucket",
        "class": "Starter",
        "cargo": 6,
        "burn": 3,       # fuel per lane segment
        "hull": 6,
        "crew_slots": 2,
        "price": 0,
        "hardpoints": 0,
        "posture": "desperate",
        "flavor": "What you start with. What you're trying to leave behind.",
    },
    "hauler": {
        "name": "Dray-Class Hauler",
        "class": "Freight",
        "cargo": 10,
        "burn": 4,
        "hull": 8,
        "crew_slots": 3,
        "price": 25,
        "hardpoints": 1,
        "posture": "relief",
        "flavor": "Volume carrier. Convoys want you. Pirates want what you carry.",
    },
    "runner": {
        "name": "Kite-Class Runner",
        "class": "Fast",
        "cargo": 5,
        "burn": 2,
        "hull": 5,
        "crew_slots": 2,
        "price": 20,
        "hardpoints": 1,
        "posture": "gray",
        "flavor": "Fast, light, forgettable. You arrive before anyone asks questions.",
    },
    "warbird": {
        "name": "Talon-Class Warbird",
        "class": "Combat",
        "cargo": 4,
        "burn": 3,
        "hull": 10,
        "crew_slots": 4,
        "price": 35,
        "hardpoints": 3,
        "posture": "honor",
        "flavor": "Built for escorts and bounties. Veshan houses respect the hull.",
    },
    "bulkframe": {
        "name": "Mule-Class Bulkframe",
        "class": "Capital",
        "cargo": 15,
        "burn": 5,
        "hull": 14,
        "crew_slots": 5,
        "price": 60,
        "hardpoints": 2,
        "posture": "empire",
        "flavor": "The ship you buy when you have something to protect.",
    },
}

# Backward compat alias for generator
SHIP_TABLETOP = {
    k: {
        "cargo": v["cargo"],
        "speed": max(1, 5 - v["burn"]),  # invert burn to speed for card display
        "hull": v["hull"],
        "crew_cost": max(0, v["crew_slots"] - 1),
        "price": v["price"],
        "cannons": v["hardpoints"],
    }
    for k, v in VESSEL_TABLETOP.items()
}


# ---------------------------------------------------------------------------
# Goods price scaling (digital credits -> tabletop credits)
# Divide by ~10 and round to keep arithmetic manageable at the table
# ---------------------------------------------------------------------------
def tabletop_price(digital_price: int) -> int:
    """Scale digital good price to tabletop credits."""
    return max(1, round(digital_price / 10))


# ---------------------------------------------------------------------------
# Captain archetypes  -- three captain lives, not three classes
# ---------------------------------------------------------------------------
CAPTAIN_TABLETOP: dict[str, dict] = {
    "relief": {
        "name": "Relief Captain",
        "home_station": "Queue of Flags",
        "credits": 30,
        "fuel": 6,
        "heat": 0,
        "ability": (
            "Convoy access: may join any convoy lane at no extra burn cost. "
            "+2 credits when delivering provision goods to stations in shortage."
        ),
        "weakness": (
            "Scrutiny magnet: inspection checks are +1 difficulty. "
            "Cannot refuse convoy scheduling delays."
        ),
        "posture": "legitimacy",
        "life": (
            "You keep people fed. You get trapped by the schedule, "
            "the paperwork, and the question of who decides who eats first."
        ),
    },
    "gray": {
        "name": "Gray Runner",
        "home_station": "Grand Drift",
        "credits": 20,
        "fuel": 5,
        "heat": 2,
        "ability": (
            "Paper leverage: may falsify manifests once per quarter "
            "(avoid one inspection). Timing abuse: +1 credit on any trade "
            "where you arrive before the shortage is public."
        ),
        "weakness": (
            "Starts at Heat 2. Seizure exposure: if caught with falsified "
            "manifests, lose all cargo and gain +3 Heat."
        ),
        "posture": "evasion",
        "life": (
            "You make money by being hard to read. You fear the moment "
            "someone reads you clearly."
        ),
    },
    "honor": {
        "name": "Honor Captain",
        "home_station": "Drashan Citadel",
        "credits": 15,
        "fuel": 4,
        "heat": 0,
        "ability": (
            "Challenge right: may issue or accept Veshan honor challenges. "
            "Winning grants +3 standing with the challenged house. "
            "Escort premium: +3 credits on escort and bounty contracts."
        ),
        "weakness": (
            "Refusing a challenge costs -3 standing with ALL Veshan houses. "
            "Volatile: standing swings are doubled."
        ),
        "posture": "confrontation",
        "life": (
            "You solve problems face-to-face. You fear the day "
            "you can't afford the fight."
        ),
    },
}
