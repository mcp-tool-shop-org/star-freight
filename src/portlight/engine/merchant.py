"""Merchant engine — inventory lookup and purchase logic for NPC shops.

Merchants sell region-filtered items with a price markup. The armory CLI
command remains as a no-markup quick-buy; merchants add flavor and personality.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from portlight.content.armor import get_armor_for_region
from portlight.content.melee_weapons import get_melee_weapons_for_region
from portlight.content.merchants import MerchantDef, get_merchant
from portlight.content.ranged_weapons import (
    AMMO,
    RANGED_WEAPONS,
    get_ammo_for_region,
    get_weapons_for_region,
)

if TYPE_CHECKING:
    from portlight.engine.models import Captain


def get_merchant_inventory(merchant: MerchantDef, port_region: str) -> list[dict]:
    """Build a merchant's inventory based on their types and port region.

    Returns list of dicts: {item_type, item_id, name, silver_cost, description}
    where silver_cost includes the merchant's markup.
    """
    items: list[dict] = []

    if "melee" in merchant.inventory_types:
        for w in get_melee_weapons_for_region(port_region):
            items.append({
                "item_type": "melee",
                "item_id": w.id,
                "name": w.name,
                "silver_cost": _markup(w.silver_cost, merchant.price_markup),
                "description": f"{w.weapon_class} — +{w.damage_bonus} dmg",
            })

    if "armor" in merchant.inventory_types:
        for a in get_armor_for_region(port_region):
            items.append({
                "item_type": "armor",
                "item_id": a.id,
                "name": a.name,
                "silver_cost": _markup(a.silver_cost, merchant.price_markup),
                "description": f"{a.armor_type} — DR {a.damage_reduction}",
            })

    if "ranged" in merchant.inventory_types:
        for w in get_weapons_for_region(port_region):
            items.append({
                "item_type": "ranged",
                "item_id": w.id,
                "name": w.name,
                "silver_cost": _markup(w.silver_cost, merchant.price_markup),
                "description": f"{w.weapon_type} — {w.damage_min}-{w.damage_max} dmg",
            })

    if "ammo" in merchant.inventory_types:
        for a in get_ammo_for_region(port_region):
            items.append({
                "item_type": "ammo",
                "item_id": a.id,
                "name": f"{a.name} (x{a.quantity})",
                "silver_cost": _markup(a.silver_cost, merchant.price_markup),
                "description": f"for {a.weapon_type}",
            })

    return items


def buy_from_merchant(
    captain: "Captain",
    merchant_id: str,
    item_id: str,
    qty: int,
    port_region: str,
) -> str | dict:
    """Buy an item from a merchant.

    Returns error string on failure, or dict {item_type, item_id, qty, total_cost} on success.
    Mutates captain.silver and captain.combat_gear.
    """
    merchant = get_merchant(merchant_id)
    if merchant is None:
        return "Unknown merchant"

    inventory = get_merchant_inventory(merchant, port_region)
    entry = next((i for i in inventory if i["item_id"] == item_id), None)
    if entry is None:
        return f"{merchant.name} doesn't sell {item_id}"

    total_cost = entry["silver_cost"] * qty
    if total_cost > captain.silver:
        return f"Need {total_cost} silver, have {captain.silver}"

    # Apply purchase
    captain.silver -= total_cost
    _apply_item(captain, entry["item_type"], item_id, qty)

    return {
        "item_type": entry["item_type"],
        "item_id": item_id,
        "qty": qty,
        "total_cost": total_cost,
        "item_name": entry["name"],
    }


def _markup(base_cost: int, markup: float) -> int:
    """Apply merchant markup, minimum 1 silver."""
    return max(1, round(base_cost * markup))


def _apply_item(captain: "Captain", item_type: str, item_id: str, qty: int) -> None:
    """Apply a purchased item to captain's gear."""
    gear = captain.combat_gear

    if item_type == "melee":
        gear.melee_weapon = item_id
    elif item_type == "armor":
        gear.armor = item_id
    elif item_type == "ranged":
        weapon = RANGED_WEAPONS.get(item_id)
        if weapon:
            if weapon.weapon_type == "firearm":
                gear.firearm = item_id
            elif weapon.weapon_type == "mechanical":
                gear.mechanical_weapon = item_id
            elif weapon.weapon_type == "thrown":
                gear.throwing_weapons[item_id] = gear.throwing_weapons.get(item_id, 0) + qty
    elif item_type == "ammo":
        ammo = AMMO.get(item_id)
        if ammo:
            if ammo.weapon_type == "firearm":
                gear.firearm_ammo += ammo.quantity * qty
            elif ammo.weapon_type == "mechanical":
                gear.mechanical_ammo += ammo.quantity * qty
