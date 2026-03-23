"""Hunting engine — forage for provisions, pelts, and silver.

Survival mechanic: gives captains a way to gather provisions when starving,
earn silver from pelts/catches when broke, and take risks for bigger rewards.

Contract:
  - hunt(captain, location, crew_count, rng) -> HuntResult
  - location: "port" (reliable, safe) or "sea" (risky, higher reward)

Dangers (sea only):
  - Crew injury (lost crew member)
  - Hull damage (minor scrape from rocky outcrop)
  - Gear loss (nets/equipment damaged)
  - Predator encounter (shark, crocodile — morale hit)
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from portlight.engine.models import Captain


@dataclass
class HuntResult:
    """Outcome of a hunting expedition."""
    success: bool
    provisions_gained: int = 0
    pelts_gained: int = 0
    silver_gained: int = 0
    morale_cost: int = 0
    crew_lost: int = 0
    hull_damage: int = 0
    flavor: str = ""
    danger_text: str = ""


# ---------------------------------------------------------------------------
# Flavor text pools
# ---------------------------------------------------------------------------

_PORT_SUCCESS = [
    "Your crew hauls in a decent catch from the harbor waters. Fresh fish for everyone.",
    "The nearby woods yield rabbits and wild herbs. The cook is pleased.",
    "Local trappers trade tips with your crew. A productive morning.",
    "Shore birds and shellfish — not glamorous, but the provisions hold is fuller.",
    "A fishmonger buys your surplus catch. A few coins earned.",
    "The crew finds a beached whale carcass — blubber, bone, and oil to sell.",
]

_PORT_FAIL = [
    "The crew spends the day fishing but catches nothing worth keeping.",
    "Rain drives the hunting party back early. A wasted effort.",
    "The harbor waters are fished out. Other crews got here first.",
]

_SEA_SUCCESS = [
    "A school of fish passes beneath the hull. The crew drops nets and hauls aboard a good catch.",
    "The lookout spots a seal colony on a rocky outcrop. Your crew returns with pelts and meat.",
    "Drifting kelp beds teem with crabs and small fish. Easy pickings for hungry sailors.",
    "A large tuna breaks the surface. Your best harpooner doesn't miss.",
    "Seabirds circle a bait ball. Where there are birds, there are fish. The nets come up full.",
]

_SEA_FAIL = [
    "The sea gives nothing today. Your crew stares at empty nets.",
    "A promising fishing spot turns up nothing but jellyfish and seaweed.",
    "The waters are too deep and too cold. Nothing bites.",
    "A sudden squall forces the fishing party back aboard. No catch today.",
]

# Danger events (sea only, ~15% chance on any sea hunt)
_SEA_DANGERS = [
    {
        "text": "A shark tears through the nets, dragging a sailor overboard. He's pulled back but badly cut.",
        "crew_lost": 0, "hull_damage": 0, "morale_cost": 5,
    },
    {
        "text": "The rowboat scrapes against a submerged rock. Minor hull damage, but the catch is lost.",
        "crew_lost": 0, "hull_damage": 3, "morale_cost": 2,
    },
    {
        "text": "A rogue wave swamps the fishing party. One sailor doesn't surface.",
        "crew_lost": 1, "hull_damage": 0, "morale_cost": 8,
    },
    {
        "text": "The nets snag on coral and tear apart. Equipment lost, nothing to show for the effort.",
        "crew_lost": 0, "hull_damage": 0, "morale_cost": 3,
    },
    {
        "text": "A saltwater crocodile lunges from a mangrove island. The crew rows back in terror.",
        "crew_lost": 0, "hull_damage": 0, "morale_cost": 6,
    },
]


def hunt(
    captain: "Captain",
    location: str,
    crew_count: int,
    rng: random.Random,
) -> HuntResult:
    """Hunt for provisions, pelts, and silver.

    Args:
        captain: The player captain (day is advanced).
        location: "port" (80% success, safe) or "sea" (50% success, dangers possible).
        crew_count: Number of crew members (affects yield).
        rng: Random number generator.

    Returns:
        HuntResult with provisions/pelts/silver gained and any dangers.
    """
    if location == "port":
        success_chance = 0.8
        base_morale_cost = 0
    else:
        success_chance = 0.5
        base_morale_cost = 3

    success = rng.random() < success_chance
    crew_bonus = min(crew_count // 3, 2)  # up to +2 from large crew

    silver = 0
    provisions = 0
    pelts = 0
    danger_text = ""
    crew_lost = 0
    hull_damage = 0
    extra_morale = 0

    if success:
        if location == "port":
            provisions = rng.randint(2, 4) + crew_bonus
            pelts = rng.randint(0, 2)
            # Port hunting can earn a little silver from selling surplus
            silver = rng.randint(1, 3) if rng.random() < 0.4 else 0
            flavor = rng.choice(_PORT_SUCCESS)
        else:
            provisions = rng.randint(1, 3) + crew_bonus
            pelts = rng.randint(0, 2)
            # Sea hunting can earn more silver (valuable catches)
            silver = rng.randint(2, 6) if rng.random() < 0.5 else 0
            flavor = rng.choice(_SEA_SUCCESS)
    else:
        provisions = 0
        pelts = 0
        flavor = rng.choice(_PORT_FAIL if location == "port" else _SEA_FAIL)

    # Sea dangers (~15% chance, independent of success)
    if location == "sea" and rng.random() < 0.15:
        danger = rng.choice(_SEA_DANGERS)
        danger_text = danger["text"]
        crew_lost = danger["crew_lost"]
        hull_damage = danger["hull_damage"]
        extra_morale = danger["morale_cost"]
        # Danger wipes out any catch on failure
        if not success:
            provisions = 0
            pelts = 0
            silver = 0

    captain.day += 1

    return HuntResult(
        success=success,
        provisions_gained=provisions,
        pelts_gained=pelts,
        silver_gained=silver,
        morale_cost=base_morale_cost + extra_morale,
        crew_lost=crew_lost,
        hull_damage=hull_damage,
        flavor=flavor,
        danger_text=danger_text,
    )
