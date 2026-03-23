"""Loot engine — roll drops after combat victories.

Loot is supplemental to trade. Pirates carry realistic stolen goods
proportional to their strength. Named captains have themed loot
matching their faction's preferred_goods.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from portlight.content.loot_tables import (
    CAPTAIN_LOOT_OVERRIDES,
    get_loot_table_for_strength,
)

if TYPE_CHECKING:
    from portlight.engine.models import Captain


def roll_loot(
    opponent_strength: int,
    opponent_id: str | None,
    rng: random.Random,
    num_drops: int = 2,
) -> list[dict]:
    """Roll on loot table after combat victory.

    Returns list of {item_type, item_id, quantity} dicts.
    Always includes at least one silver drop.
    """
    # Named captain override or strength-based table
    if opponent_id and opponent_id in CAPTAIN_LOOT_OVERRIDES:
        table = CAPTAIN_LOOT_OVERRIDES[opponent_id]
    else:
        table = get_loot_table_for_strength(opponent_strength)

    # Scale drops: stronger opponents drop more items
    if opponent_strength >= 9:
        num_drops = 3
    elif opponent_strength >= 7:
        num_drops = max(num_drops, 2)

    entries = table.entries
    weights = [e.weight for e in entries]

    drops: list[dict] = []
    seen_types: set[str] = set()

    # Always include silver
    silver_entries = [e for e in entries if e.item_type == "silver"]
    if silver_entries:
        se = silver_entries[0]
        qty = rng.randint(se.quantity_min, se.quantity_max)
        drops.append({"item_type": "silver", "item_id": "silver", "quantity": qty})
        seen_types.add("silver")

    # Roll remaining drops
    for _ in range(num_drops):
        chosen = rng.choices(entries, weights=weights, k=1)[0]
        if chosen.item_type == "silver" and "silver" in seen_types:
            # Don't double-roll silver, add to existing
            drops[0]["quantity"] += rng.randint(chosen.quantity_min, chosen.quantity_max)
            continue

        qty = rng.randint(chosen.quantity_min, chosen.quantity_max)
        drops.append({
            "item_type": chosen.item_type,
            "item_id": chosen.item_id,
            "quantity": qty,
        })

    return drops


def apply_loot(captain: "Captain", loot: list[dict]) -> list[str]:
    """Apply loot drops to captain state. Returns flavor text lines."""
    messages: list[str] = []
    gear = captain.combat_gear

    for drop in loot:
        item_type = drop["item_type"]
        item_id = drop["item_id"]
        qty = drop["quantity"]

        if item_type == "silver":
            captain.silver += qty
            messages.append(f"+{qty} silver")

        elif item_type == "cargo":
            from portlight.engine.models import CargoItem
            # Add to cargo (merge if same good already in hold)
            existing = next((c for c in captain.cargo if c.good_id == item_id), None)
            if existing:
                existing.quantity += qty
            else:
                captain.cargo.append(CargoItem(
                    good_id=item_id, quantity=qty, cost_basis=0,
                    acquired_port="loot", acquired_region="pirate",
                ))
            from portlight.content.goods import GOODS
            good_name = GOODS[item_id].name if item_id in GOODS else item_id
            messages.append(f"+{qty} {good_name}")

        elif item_type == "melee_weapon":
            gear.melee_weapon = item_id
            from portlight.content.melee_weapons import MELEE_WEAPONS
            name = MELEE_WEAPONS[item_id].name if item_id in MELEE_WEAPONS else item_id
            messages.append(f"Found: {name}")

        elif item_type == "armor":
            gear.armor = item_id
            from portlight.content.armor import ARMOR
            name = ARMOR[item_id].name if item_id in ARMOR else item_id
            messages.append(f"Found: {name}")

        elif item_type == "ranged_weapon":
            from portlight.content.ranged_weapons import RANGED_WEAPONS
            weapon = RANGED_WEAPONS.get(item_id)
            if weapon:
                if weapon.weapon_type == "firearm":
                    gear.firearm = item_id
                elif weapon.weapon_type == "mechanical":
                    gear.mechanical_weapon = item_id
                messages.append(f"Found: {weapon.name}")

        elif item_type == "ammo":
            from portlight.content.ranged_weapons import AMMO
            ammo = AMMO.get(item_id)
            if ammo:
                if ammo.weapon_type == "firearm":
                    gear.firearm_ammo += ammo.quantity * qty
                elif ammo.weapon_type == "mechanical":
                    gear.mechanical_ammo += ammo.quantity * qty
                messages.append(f"+{ammo.quantity * qty} {ammo.name}")

    return messages
