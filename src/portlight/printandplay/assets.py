"""Visual constants for the Print-and-Play PDF kit.

Design law: late-18th-century merchant ledger + modern board game usability.
Grayscale-first. Color is a bonus layer. Information-dominant.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Page dimensions (mm) — Letter size
# ---------------------------------------------------------------------------
PAGE_W = 215.9
PAGE_H = 279.4
MARGIN = 12.0

# ---------------------------------------------------------------------------
# Color palette — muted region accents, system colors
# ---------------------------------------------------------------------------

# Base colors (RGB tuples)
INK = (40, 40, 40)          # charcoal
LIGHT_GRAY = (180, 180, 180)
MEDIUM_GRAY = (120, 120, 120)
PAPER = (252, 250, 245)     # warm off-white
WHITE = (255, 255, 255)

# Region accent colors (low-saturation)
REGION_COLORS: dict[str, tuple[int, int, int]] = {
    "Mediterranean":  (100, 120, 150),  # slate blue
    "North Atlantic": (160, 110, 100),  # muted rust
    "West Africa":    (170, 145, 90),   # ochre
    "East Indies":    (90, 140, 120),   # sea green
    "South Seas":     (100, 135, 140),  # dusky teal
}

# System colors
HEAT_COLOR = (180, 60, 50)       # red family
TRUST_COLOR = (60, 130, 90)      # green family
DAMAGE_COLOR = (140, 40, 40)     # dark red
SILVER_COLOR = (150, 145, 120)   # gold-gray

# ---------------------------------------------------------------------------
# Typography — sizes in points
# ---------------------------------------------------------------------------
FONT_TITLE = 18
FONT_HEADING = 14
FONT_SUBHEADING = 11
FONT_BODY = 9
FONT_SMALL = 7
FONT_TINY = 6

# ---------------------------------------------------------------------------
# Card dimensions (mm) — standard poker size (63.5 x 88.9)
# ---------------------------------------------------------------------------
CARD_W = 63.5
CARD_H = 88.9
CARD_PADDING = 3.0
CARD_CORNER_R = 2.0

# Compact card (half-height, for port references)
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
# Route distance tiers (digital days -> tabletop movement cost)
# ---------------------------------------------------------------------------
def route_movement_cost(distance_days: int) -> int:
    """Convert digital route distance to tabletop movement points."""
    if distance_days <= 22:
        return 1  # Short (same region)
    elif distance_days <= 44:
        return 2  # Medium (adjacent regions)
    elif distance_days <= 64:
        return 3  # Long (cross-region)
    else:
        return 4  # Extreme (dangerous shortcuts)


# ---------------------------------------------------------------------------
# Ship stat scaling (digital -> tabletop)
# ---------------------------------------------------------------------------
SHIP_TABLETOP: dict[str, dict[str, int]] = {
    "coastal_sloop":      {"cargo": 5,  "speed": 4, "hull": 6,  "crew_cost": 0, "price": 0,   "cannons": 0},
    "swift_cutter":       {"cargo": 7,  "speed": 5, "hull": 7,  "crew_cost": 1, "price": 20,  "cannons": 1},
    "trade_brigantine":   {"cargo": 10, "speed": 3, "hull": 10, "crew_cost": 2, "price": 40,  "cannons": 3},
    "merchant_galleon":   {"cargo": 15, "speed": 2, "hull": 16, "crew_cost": 3, "price": 80,  "cannons": 6},
    "royal_man_of_war":   {"cargo": 20, "speed": 1, "hull": 22, "crew_cost": 4, "price": 150, "cannons": 10},
}

# ---------------------------------------------------------------------------
# Goods price scaling (digital base_price -> tabletop price)
# Divide by ~5 and round to keep arithmetic manageable
# ---------------------------------------------------------------------------
def tabletop_price(digital_price: int) -> int:
    """Scale digital good price to tabletop silver."""
    return max(1, round(digital_price / 5))


# ---------------------------------------------------------------------------
# Captain starting conditions (tabletop-specific)
# ---------------------------------------------------------------------------
CAPTAIN_TABLETOP: dict[str, dict] = {
    "merchant": {
        "name": "Merchant",
        "home_port": "Porto Novo",
        "silver": 25,
        "provisions": 6,
        "heat": 0,
        "ability": "+1 silver on all sell transactions. Contracts cost 1 fewer trust tier to accept.",
        "weakness": "Heat penalties are doubled.",
    },
    "navigator": {
        "name": "Navigator",
        "home_port": "Monsoon Reach",
        "silver": 20,
        "provisions": 5,
        "heat": 0,
        "ability": "+1 movement point. May peek at top event card before choosing route.",
        "weakness": "Sees 1 fewer contract on the board.",
    },
    "smuggler": {
        "name": "Smuggler",
        "home_port": "Corsair's Rest",
        "silver": 15,
        "provisions": 4,
        "heat": 3,
        "ability": "May buy/sell contraband. Inspections: roll 2 dice, take better result.",
        "weakness": "Starts with Heat 3. Cannot take Lawful contracts until trust reaches Credible.",
    },
}
