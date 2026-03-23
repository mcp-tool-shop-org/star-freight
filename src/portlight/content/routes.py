"""Expanded route network — 5 regions, tiered access.

Route design creates five archetype tiers:
  Tier 1 (Sloop): Mediterranean and North Atlantic internal. Short, safe, low margins.
  Tier 2 (Brigantine): Cross-region bridges (Med<->WA, Med<->NA, WA internal).
    Medium distance, moderate risk. Bulk commodity routes become viable.
  Tier 3 (Galleon): Long-haul East Indies, South Seas, and cross-region shortcuts.
    High distance, high danger, but luxury margins justify the investment.
  Tier 4 (Man-of-War): Dangerous shortcuts and South Seas deep routes.

Hero's journey progression:
  Mediterranean -> North Atlantic (early expansion)
  Mediterranean -> West Africa (mid-game)
  West Africa -> East Indies (late mid-game)
  East Indies -> South Seas (endgame exploration)
  Direct long-haul shortcuts reward the bold
"""

from portlight.engine.models import Route

ROUTES: list[Route] = [
    # =========================================================================
    # MEDITERRANEAN internal (Sloop-safe)
    # =========================================================================
    Route("porto_novo",     "al_manar",          distance=24,  danger=0.12,  min_ship_class="sloop",
          lore_name="The Grain Road", lore="The oldest trade route in the Mediterranean. Grain ships have sailed this lane since before memory."),
    Route("porto_novo",     "silva_bay",         distance=16,  danger=0.08,  min_ship_class="sloop",
          lore_name="The Timber Run", lore="Short and safe — the shipwrights' lifeline. Silva Bay's timber built Porto Novo's fleet."),
    Route("al_manar",       "silva_bay",         distance=20,  danger=0.10,  min_ship_class="sloop"),
    Route("porto_novo",     "corsairs_rest",     distance=18,  danger=0.18,  min_ship_class="sloop",
          lore_name="The Shadow Lane", lore="Every merchant denies using it. Every merchant uses it. The line between trade and smuggling runs through these waters."),
    Route("silva_bay",      "corsairs_rest",     distance=14,  danger=0.15,  min_ship_class="sloop"),

    # =========================================================================
    # NORTH ATLANTIC internal (Sloop-safe)
    # =========================================================================
    Route("ironhaven",      "stormwall",         distance=20,  danger=0.09,  min_ship_class="sloop",
          lore_name="The Iron Strait", lore="Iron from the foundries, soldiers from the fortress. This lane never sleeps."),
    Route("ironhaven",      "thornport",         distance=22,  danger=0.08,  min_ship_class="sloop"),
    Route("stormwall",      "thornport",         distance=18,  danger=0.10,  min_ship_class="sloop",
          lore_name="The Tea and Tobacco Road", lore="Thornport's warmth heading to Stormwall's cold. The northern comfort trade."),

    # =========================================================================
    # MEDITERRANEAN <-> NORTH ATLANTIC (Brigantine recommended)
    # =========================================================================
    Route("porto_novo",     "ironhaven",         distance=36,  danger=0.12,  min_ship_class="brigantine"),
    Route("silva_bay",      "ironhaven",         distance=32,  danger=0.11,  min_ship_class="brigantine"),
    Route("corsairs_rest",  "stormwall",         distance=40,  danger=0.15,  min_ship_class="brigantine"),

    # =========================================================================
    # MEDITERRANEAN <-> WEST AFRICA (Brigantine recommended)
    # =========================================================================
    Route("porto_novo",     "sun_harbor",        distance=40,  danger=0.12,  min_ship_class="brigantine",
          lore_name="The Cotton Crossing", lore="Mediterranean grain south, Gold Coast cotton north. The route that clothed an empire."),
    Route("al_manar",       "sun_harbor",        distance=48,  danger=0.15,  min_ship_class="brigantine"),
    Route("silva_bay",      "palm_cove",         distance=44,  danger=0.13,  min_ship_class="brigantine"),

    # =========================================================================
    # WEST AFRICA internal (Sloop-safe)
    # =========================================================================
    Route("sun_harbor",     "palm_cove",         distance=20,  danger=0.10,  min_ship_class="sloop"),
    Route("sun_harbor",     "iron_point",        distance=18,  danger=0.09,  min_ship_class="sloop"),
    Route("palm_cove",      "iron_point",        distance=22,  danger=0.11,  min_ship_class="sloop"),
    Route("sun_harbor",     "pearl_shallows",    distance=24,  danger=0.10,  min_ship_class="sloop"),
    Route("palm_cove",      "pearl_shallows",    distance=20,  danger=0.09,  min_ship_class="sloop"),

    # =========================================================================
    # WEST AFRICA <-> EAST INDIES (Galleon-class voyages)
    # =========================================================================
    Route("sun_harbor",     "crosswind_isle",    distance=64,  danger=0.18,  min_ship_class="galleon",
          lore_name="The Long Crossing", lore="Months of open water. The route that separates traders from merchants. Many set out. Fewer arrive."),
    Route("iron_point",     "crosswind_isle",    distance=60,  danger=0.16,  min_ship_class="brigantine"),
    Route("pearl_shallows", "crosswind_isle",    distance=56,  danger=0.15,  min_ship_class="brigantine"),

    # =========================================================================
    # EAST INDIES internal (short coastal routes sloop-safe, longer ones brigantine)
    # =========================================================================
    Route("crosswind_isle", "jade_port",         distance=28,  danger=0.10,  min_ship_class="sloop",
          lore_name="The Porcelain Lane", lore="From the free port to the kiln masters. Every piece of porcelain in the west passed through here."),
    Route("crosswind_isle", "monsoon_reach",     distance=24,  danger=0.09,  min_ship_class="sloop"),
    Route("crosswind_isle", "silk_haven",        distance=32,  danger=0.12,  min_ship_class="brigantine"),
    Route("crosswind_isle", "dragons_gate",      distance=30,  danger=0.11,  min_ship_class="brigantine"),
    Route("jade_port",      "monsoon_reach",     distance=20,  danger=0.08,  min_ship_class="sloop"),
    Route("jade_port",      "silk_haven",        distance=18,  danger=0.07,  min_ship_class="sloop",
          lore_name="The Silk Road by Sea", lore="Where porcelain meets silk. The two oldest trades in the East, connected by the shortest route."),
    Route("jade_port",      "dragons_gate",      distance=22,  danger=0.09,  min_ship_class="sloop"),
    Route("monsoon_reach",  "silk_haven",        distance=22,  danger=0.10,  min_ship_class="sloop"),
    Route("monsoon_reach",  "spice_narrows",     distance=26,  danger=0.13,  min_ship_class="brigantine"),
    Route("silk_haven",     "spice_narrows",     distance=20,  danger=0.11,  min_ship_class="brigantine"),
    Route("dragons_gate",   "spice_narrows",     distance=28,  danger=0.14,  min_ship_class="brigantine"),

    # =========================================================================
    # EAST INDIES <-> SOUTH SEAS (Galleon-class — endgame exploration)
    # =========================================================================
    Route("monsoon_reach",  "typhoon_anchorage", distance=52,  danger=0.20,  min_ship_class="galleon",
          lore_name="Typhoon Alley", lore="Named for obvious reasons. The monsoon winds funnel through here like a gauntlet. Timing is survival."),
    Route("spice_narrows",  "ember_isle",        distance=48,  danger=0.18,  min_ship_class="galleon",
          lore_name="The Volcanic Passage", lore="Warm currents and sulfur air. The locals say the sea boils near the islands on bad days."),
    Route("crosswind_isle", "ember_isle",        distance=56,  danger=0.19,  min_ship_class="galleon"),

    # =========================================================================
    # SOUTH SEAS internal (short island-hopping sloop-safe)
    # =========================================================================
    Route("ember_isle",     "typhoon_anchorage", distance=24,  danger=0.14,  min_ship_class="sloop"),
    Route("ember_isle",     "coral_throne",      distance=28,  danger=0.15,  min_ship_class="sloop"),
    Route("typhoon_anchorage", "coral_throne",   distance=22,  danger=0.13,  min_ship_class="brigantine"),

    # =========================================================================
    # DANGEROUS LONG-HAUL SHORTCUTS (Galleon only)
    # =========================================================================
    Route("al_manar",       "monsoon_reach",     distance=72,  danger=0.22,  min_ship_class="galleon",
          lore_name="The Monsoon Shortcut", lore="Timing is everything. Catch the monsoon right and you fly. Catch it wrong and you drown."),
    Route("corsairs_rest",  "spice_narrows",     distance=80,  danger=0.25,  min_ship_class="galleon",
          lore_name="The Smuggler's Run", lore="Only the desperate or the bold sail this direct. Pirate kings once controlled both ends."),
    Route("ironhaven",      "jade_port",         distance=76,  danger=0.22,  min_ship_class="galleon",
          lore_name="The Northern Passage", lore="Iron west, porcelain east. The longest profitable route in the world."),
    Route("pearl_shallows", "coral_throne",      distance=68,  danger=0.20,  min_ship_class="galleon",
          lore_name="The Deep South Run", lore="Pearl to pearl. The divers of the shallows and the divers of the reef — same craft, different kingdoms."),
]
