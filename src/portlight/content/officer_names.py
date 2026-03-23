"""Officer name and trait generation — gives personality to specialist crew.

Officers are named crew members: navigators, surgeons, gunners, marines,
quartermasters. Sailors remain anonymous. Names are region-flavored.
"""

from __future__ import annotations

import random

# Regional name pools
_NAMES: dict[str, list[str]] = {
    "Mediterranean": [
        "Marco", "Sophia", "Nikolaos", "Fatima", "Lorenzo",
        "Valentina", "Dimitri", "Leila", "Antonio", "Isadora",
    ],
    "North Atlantic": [
        "William", "Margaret", "Henrik", "Brigitte", "Duncan",
        "Eleanor", "Gunnar", "Astrid", "Thomas", "Catherine",
    ],
    "West Africa": [
        "Kwame", "Aminata", "Kofi", "Adaeze", "Sekou",
        "Mariam", "Ousmane", "Aisha", "Yusuf", "Zara",
    ],
    "East Indies": [
        "Rajan", "Mei Lin", "Arjun", "Suki", "Bao",
        "Padma", "Kenji", "Lien", "Haruki", "Kamala",
    ],
    "South Seas": [
        "Tane", "Moana", "Rangi", "Leilani", "Makoa",
        "Aroha", "Koa", "Nalani", "Ioane", "Mele",
    ],
}

_TRAITS = [
    "loyal", "cautious", "bold", "superstitious", "sharp-eyed",
    "steady", "hot-tempered", "quiet", "gregarious", "shrewd",
    "resourceful", "fearless", "meticulous", "jovial", "stoic",
]


def generate_officer_name(region: str, rng: random.Random) -> str:
    """Generate a region-flavored officer name."""
    pool = _NAMES.get(region, _NAMES["Mediterranean"])
    return rng.choice(pool)


def generate_officer_trait(rng: random.Random) -> str:
    """Pick a random personality trait."""
    return rng.choice(_TRAITS)
