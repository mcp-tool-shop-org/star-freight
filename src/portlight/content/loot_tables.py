"""Loot table catalog — what pirates carry and what you take when you win.

Loot is supplemental to trade — it won't replace arbitrage as the wealth
engine, but stronger pirates carry realistic stolen goods. Winning a fight
against a strength-8 captain should feel rewarding.

Named pirate captains get unique override tables themed to their faction's
preferred_goods.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LootEntry:
    """One possible drop from a loot table."""
    item_type: str              # "silver", "cargo", "melee_weapon", "armor", "ranged_weapon", "ammo"
    item_id: str                # specific item ID, or "silver" for silver
    quantity_min: int
    quantity_max: int
    weight: float               # relative probability weight


@dataclass(frozen=True)
class LootTable:
    """A named loot table with weighted entries."""
    id: str
    entries: tuple[LootEntry, ...]


# ---------------------------------------------------------------------------
# Tier-based loot tables (selected by opponent strength)
# ---------------------------------------------------------------------------

LOOT_TABLES: dict[str, LootTable] = {t.id: t for t in [
    # --- Weak pirates (strength 1-4) ---
    LootTable(
        id="loot_weak",
        entries=(
            LootEntry("silver", "silver", 5, 20, 4.0),
            LootEntry("cargo", "grain", 1, 3, 2.0),
            LootEntry("cargo", "rum", 1, 2, 1.5),
            LootEntry("ammo", "pistol_shot", 1, 1, 1.0),
        ),
    ),

    # --- Medium pirates (strength 5-6) ---
    LootTable(
        id="loot_medium",
        entries=(
            LootEntry("silver", "silver", 15, 45, 4.0),
            LootEntry("cargo", "iron", 1, 3, 2.0),
            LootEntry("cargo", "cotton", 2, 5, 1.5),
            LootEntry("cargo", "rum", 1, 3, 1.5),
            LootEntry("ammo", "pistol_shot", 1, 2, 1.5),
            LootEntry("melee_weapon", "cutlass", 1, 1, 0.8),
            LootEntry("melee_weapon", "dagger", 1, 1, 1.0),
        ),
    ),

    # --- Strong pirates (strength 7-8) ---
    LootTable(
        id="loot_strong",
        entries=(
            LootEntry("silver", "silver", 30, 80, 4.0),
            LootEntry("cargo", "spice", 1, 3, 2.0),
            LootEntry("cargo", "silk", 1, 2, 1.5),
            LootEntry("cargo", "tea", 2, 4, 1.5),
            LootEntry("cargo", "weapons", 1, 2, 1.0),
            LootEntry("ammo", "pistol_shot", 1, 3, 1.5),
            LootEntry("melee_weapon", "rapier", 1, 1, 0.5),
            LootEntry("melee_weapon", "boarding_axe", 1, 1, 0.6),
            LootEntry("armor", "leather_vest", 1, 1, 0.4),
            LootEntry("armor", "chain_shirt", 1, 1, 0.2),
        ),
    ),

    # --- Boss pirates (strength 9+) ---
    LootTable(
        id="loot_boss",
        entries=(
            LootEntry("silver", "silver", 60, 150, 4.0),
            LootEntry("cargo", "pearls", 1, 3, 2.0),
            LootEntry("cargo", "silk", 2, 5, 1.5),
            LootEntry("cargo", "porcelain", 1, 3, 1.5),
            LootEntry("melee_weapon", "rapier", 1, 1, 0.8),
            LootEntry("melee_weapon", "kris", 1, 1, 0.6),
            LootEntry("armor", "chain_shirt", 1, 1, 0.5),
            LootEntry("armor", "brigandine", 1, 1, 0.3),
            LootEntry("ranged_weapon", "wheellock_pistol", 1, 1, 0.3),
            LootEntry("ammo", "pistol_shot", 2, 4, 1.5),
        ),
    ),
]}


# ---------------------------------------------------------------------------
# Named captain override tables (faction-themed loot)
# ---------------------------------------------------------------------------

CAPTAIN_LOOT_OVERRIDES: dict[str, LootTable] = {t.id: t for t in [
    LootTable(
        id="scarlet_ana",  # Crimson Tide — weapons and powder
        entries=(
            LootEntry("silver", "silver", 40, 90, 3.0),
            LootEntry("cargo", "weapons", 2, 5, 2.5),
            LootEntry("cargo", "black_powder", 1, 3, 1.5),
            LootEntry("melee_weapon", "cutlass", 1, 1, 1.0),
            LootEntry("armor", "chain_shirt", 1, 1, 0.5),
        ),
    ),
    LootTable(
        id="the_butcher",  # Crimson Tide — aggressive, more silver
        entries=(
            LootEntry("silver", "silver", 60, 120, 4.0),
            LootEntry("cargo", "weapons", 3, 6, 2.0),
            LootEntry("melee_weapon", "boarding_axe", 1, 1, 1.0),
            LootEntry("armor", "leather_vest", 1, 1, 0.8),
        ),
    ),
    LootTable(
        id="raj_the_quiet",  # Monsoon Syndicate — spice and silk
        entries=(
            LootEntry("silver", "silver", 30, 70, 3.0),
            LootEntry("cargo", "spice", 2, 5, 3.0),
            LootEntry("cargo", "silk", 1, 3, 2.0),
            LootEntry("cargo", "opium", 1, 2, 1.0),
            LootEntry("melee_weapon", "kris", 1, 1, 0.8),
        ),
    ),
    LootTable(
        id="typhoon_mei",  # Monsoon Syndicate — wild, mixed loot
        entries=(
            LootEntry("silver", "silver", 50, 100, 3.5),
            LootEntry("cargo", "spice", 1, 4, 2.0),
            LootEntry("cargo", "tea", 2, 5, 1.5),
            LootEntry("melee_weapon", "kris", 1, 1, 0.6),
            LootEntry("armor", "brigandine", 1, 1, 0.4),
        ),
    ),
    LootTable(
        id="old_coral",  # Deep Reef Brotherhood — pearls and medicines
        entries=(
            LootEntry("silver", "silver", 25, 60, 3.0),
            LootEntry("cargo", "pearls", 2, 4, 3.0),
            LootEntry("cargo", "medicines", 1, 3, 2.0),
            LootEntry("melee_weapon", "dagger", 1, 2, 1.0),
        ),
    ),
    LootTable(
        id="the_diver",  # Deep Reef Brotherhood — aggressive, pearls
        entries=(
            LootEntry("silver", "silver", 40, 80, 3.5),
            LootEntry("cargo", "pearls", 1, 3, 2.5),
            LootEntry("cargo", "stolen_cargo", 1, 2, 1.5),
            LootEntry("melee_weapon", "cutlass", 1, 1, 0.8),
        ),
    ),
    LootTable(
        id="sergeant_kruze",  # Iron Wolves — iron and heavy gear
        entries=(
            LootEntry("silver", "silver", 50, 100, 3.0),
            LootEntry("cargo", "iron", 3, 6, 2.5),
            LootEntry("cargo", "weapons", 2, 4, 2.0),
            LootEntry("melee_weapon", "boarding_axe", 1, 1, 1.0),
            LootEntry("armor", "chain_shirt", 1, 1, 0.6),
        ),
    ),
    LootTable(
        id="gnaw",  # Iron Wolves — aggressive brute, heavy loot
        entries=(
            LootEntry("silver", "silver", 80, 150, 3.5),
            LootEntry("cargo", "iron", 2, 5, 2.0),
            LootEntry("cargo", "black_powder", 2, 4, 1.5),
            LootEntry("melee_weapon", "halberd", 1, 1, 0.5),
            LootEntry("armor", "chain_shirt", 1, 1, 0.4),
        ),
    ),
]}


def get_loot_table_for_strength(strength: int) -> LootTable:
    """Select the appropriate loot table tier based on opponent strength."""
    if strength >= 9:
        return LOOT_TABLES["loot_boss"]
    elif strength >= 7:
        return LOOT_TABLES["loot_strong"]
    elif strength >= 5:
        return LOOT_TABLES["loot_medium"]
    return LOOT_TABLES["loot_weak"]
