"""Ship stat resolution — compute effective stats from base template + upgrades.

Ship dataclass fields hold base values from the template. These functions
compute effective values by applying upgrade bonuses. Call these at the
point where the stat matters (voyage speed, naval combat, etc.).

Pure functions — no state mutation.
"""

from __future__ import annotations

import random

from portlight.engine.models import (
    CrewRole,
    CrewRoster,
    Ship,
    ShipTemplate,
    UpgradeTemplate,
)


def resolve_speed(
    ship: Ship,
    upgrades_catalog: dict[str, UpgradeTemplate],
) -> float:
    """Effective speed = base + upgrade bonuses - penalties."""
    bonus = 0.0
    penalty = 0.0
    for inst in ship.upgrades:
        tmpl = upgrades_catalog.get(inst.upgrade_id)
        if tmpl:
            bonus += tmpl.speed_bonus
            penalty += tmpl.speed_penalty
    return max(0.5, ship.speed + bonus - penalty)


def resolve_hull_max(
    ship: Ship,
    upgrades_catalog: dict[str, UpgradeTemplate],
) -> int:
    """Effective hull max = base + upgrade bonuses."""
    bonus = 0
    for inst in ship.upgrades:
        tmpl = upgrades_catalog.get(inst.upgrade_id)
        if tmpl:
            bonus += tmpl.hull_max_bonus
    return ship.hull_max + bonus


def resolve_cargo_capacity(
    ship: Ship,
    upgrades_catalog: dict[str, UpgradeTemplate],
) -> int:
    """Effective cargo capacity = base + upgrade bonuses."""
    bonus = 0
    for inst in ship.upgrades:
        tmpl = upgrades_catalog.get(inst.upgrade_id)
        if tmpl:
            bonus += tmpl.cargo_bonus
    return ship.cargo_capacity + bonus


def resolve_cannons(
    ship: Ship,
    upgrades_catalog: dict[str, UpgradeTemplate],
) -> int:
    """Effective cannon count = base + upgrade bonuses."""
    bonus = 0
    for inst in ship.upgrades:
        tmpl = upgrades_catalog.get(inst.upgrade_id)
        if tmpl:
            bonus += tmpl.cannon_bonus
    return ship.cannons + bonus


def resolve_maneuver(
    ship: Ship,
    upgrades_catalog: dict[str, UpgradeTemplate],
) -> float:
    """Effective maneuver = base + upgrade bonuses, clamped to [0, 1]."""
    bonus = 0.0
    for inst in ship.upgrades:
        tmpl = upgrades_catalog.get(inst.upgrade_id)
        if tmpl:
            bonus += tmpl.maneuver_bonus
    return max(0.0, min(1.0, ship.maneuver + bonus))


def resolve_storm_resist(
    ship: Ship,
    template: ShipTemplate,
    upgrades_catalog: dict[str, UpgradeTemplate],
) -> float:
    """Effective storm resistance = template base + upgrade bonuses, capped at 0.9."""
    bonus = 0.0
    for inst in ship.upgrades:
        tmpl = upgrades_catalog.get(inst.upgrade_id)
        if tmpl:
            bonus += tmpl.storm_resist_bonus
    return min(0.9, template.storm_resist + bonus)


def resolve_crew_max(
    ship: Ship,
    upgrades_catalog: dict[str, UpgradeTemplate],
) -> int:
    """Effective crew max = base + upgrade bonuses."""
    bonus = 0
    for inst in ship.upgrades:
        tmpl = upgrades_catalog.get(inst.upgrade_id)
        if tmpl:
            bonus += tmpl.crew_max_bonus
    return ship.crew_max + bonus


def has_special(
    ship: Ship,
    special: str,
    upgrades_catalog: dict[str, UpgradeTemplate],
) -> bool:
    """Check if any installed upgrade has the given special tag."""
    for inst in ship.upgrades:
        tmpl = upgrades_catalog.get(inst.upgrade_id)
        if tmpl and tmpl.special == special:
            return True
    return False


def resolved_ship(
    ship: Ship,
    upgrades_catalog: dict[str, UpgradeTemplate],
) -> Ship:
    """Return a copy of the ship with effective stats applied.

    Use this at the boundary when passing a ship to pure combat/voyage
    functions that read stats directly from the Ship object.
    The returned copy shares the same upgrades list (not a deep copy).
    """
    return Ship(
        template_id=ship.template_id,
        name=ship.name,
        hull=ship.hull,
        hull_max=resolve_hull_max(ship, upgrades_catalog),
        cargo_capacity=resolve_cargo_capacity(ship, upgrades_catalog),
        speed=resolve_speed(ship, upgrades_catalog),
        crew=ship.crew,
        crew_max=resolve_crew_max(ship, upgrades_catalog),
        cannons=resolve_cannons(ship, upgrades_catalog),
        maneuver=resolve_maneuver(ship, upgrades_catalog),
        upgrades=ship.upgrades,
        upgrade_slots=ship.upgrade_slots,
    )


def resolve_all(
    ship: Ship,
    template: ShipTemplate,
    upgrades_catalog: dict[str, UpgradeTemplate],
) -> dict:
    """Compute all resolved stats as a dict. Useful for views."""
    return {
        "speed": resolve_speed(ship, upgrades_catalog),
        "hull_max": resolve_hull_max(ship, upgrades_catalog),
        "cargo_capacity": resolve_cargo_capacity(ship, upgrades_catalog),
        "cannons": resolve_cannons(ship, upgrades_catalog),
        "maneuver": resolve_maneuver(ship, upgrades_catalog),
        "storm_resist": resolve_storm_resist(ship, template, upgrades_catalog),
        "crew_max": resolve_crew_max(ship, upgrades_catalog),
    }


# ---------------------------------------------------------------------------
# Crew role effects
# ---------------------------------------------------------------------------

def gunner_damage_mult(roster: CrewRoster) -> float:
    """Broadside damage multiplier from gunners. +10% per gunner, max 3."""
    return 1.0 + 0.10 * min(roster.gunners, 3)


def navigator_speed_bonus(roster: CrewRoster) -> float:
    """Speed bonus from having a navigator."""
    return 0.5 if roster.navigators >= 1 else 0.0


def navigator_storm_resist_bonus(roster: CrewRoster) -> float:
    """Storm resistance bonus from navigator."""
    return 0.05 if roster.navigators >= 1 else 0.0


def surgeon_death_reduction(roster: CrewRoster) -> float:
    """Fraction of crew death events prevented by surgeon."""
    return 0.30 if roster.surgeons >= 1 else 0.0


def marine_boarding_bonus(roster: CrewRoster) -> float:
    """Boarding effectiveness bonus from marines. +20% per marine, max 4."""
    return 0.20 * min(roster.marines, 4)


def quartermaster_wage_discount(roster: CrewRoster) -> float:
    """Fraction discount on daily wages from quartermaster."""
    return 0.10 if roster.quartermasters >= 1 else 0.0


def quartermaster_sell_bonus(roster: CrewRoster) -> float:
    """Sell price bonus fraction from quartermaster."""
    return 0.05 if roster.quartermasters >= 1 else 0.0


def compute_daily_wages(roster: CrewRoster, ship_daily_wage: int = 1) -> int:
    """Total daily wage bill from roster composition.

    Sailors use the ship's template daily_wage (bigger ships cost more to crew).
    Specialists use their own role-specific wage rates.
    Quartermaster applies a 10% discount.
    """
    from portlight.content.crew_roles import ROLE_SPECS
    base = (
        roster.sailors * max(ship_daily_wage, ROLE_SPECS[CrewRole.SAILOR].wage)
        + roster.gunners * max(ship_daily_wage, ROLE_SPECS[CrewRole.GUNNER].wage)
        + roster.navigators * max(ship_daily_wage, ROLE_SPECS[CrewRole.NAVIGATOR].wage)
        + roster.surgeons * max(ship_daily_wage, ROLE_SPECS[CrewRole.SURGEON].wage)
        + roster.marines * max(ship_daily_wage, ROLE_SPECS[CrewRole.MARINE].wage)
        + roster.quartermasters * max(ship_daily_wage, ROLE_SPECS[CrewRole.QUARTERMASTER].wage)
    )
    if roster.quartermasters >= 1:
        base = int(base * 0.90)
    return base


def select_casualty(
    roster: CrewRoster,
    context: str,
    rng: random.Random,
) -> CrewRole | None:
    """Pick which role loses a crew member. Returns None if roster is empty.

    Context affects weights: marines/sailors die first in boarding,
    sailors die first in storms.
    """
    weights: dict[CrewRole, float] = {}
    if roster.sailors > 0:
        weights[CrewRole.SAILOR] = 3.0
    if roster.gunners > 0:
        weights[CrewRole.GUNNER] = 1.5
    if roster.navigators > 0:
        weights[CrewRole.NAVIGATOR] = 0.5
    if roster.surgeons > 0:
        weights[CrewRole.SURGEON] = 0.5
    if roster.marines > 0:
        weights[CrewRole.MARINE] = 2.0
    if roster.quartermasters > 0:
        weights[CrewRole.QUARTERMASTER] = 0.5

    if not weights:
        return None

    # Context adjustments
    if context == "boarding" and CrewRole.MARINE in weights:
        weights[CrewRole.MARINE] *= 2.0
    if context == "storm" and CrewRole.SAILOR in weights:
        weights[CrewRole.SAILOR] *= 2.0

    roles = list(weights.keys())
    w = [weights[r] for r in roles]
    return rng.choices(roles, weights=w, k=1)[0]


# ---------------------------------------------------------------------------
# Crew morale
# ---------------------------------------------------------------------------

def morale_speed_modifier(morale: int) -> float:
    """Speed multiplier based on crew morale.

    High morale (>70): +10% speed (crew works hard)
    Normal (30-70): no effect
    Low morale (<30): -20% speed (crew drags feet)
    """
    if morale > 70:
        return 1.10
    elif morale < 30:
        return 0.80
    return 1.0


def tick_morale_at_sea(
    ship: Ship,
    wages_paid: bool,
    provisions_ok: bool,
    days_since_port: int,
) -> int:
    """Update morale for one day at sea. Returns new morale value.

    Positive: wages paid (+1), provisions ok (no change)
    Negative: unpaid wages (-5), no provisions (-3), long voyage (-1 after day 10)
    """
    delta = 0
    if wages_paid:
        delta += 1
    else:
        delta -= 5
    if not provisions_ok:
        delta -= 3
    if days_since_port > 10:
        delta -= 1  # crew gets restless
    new_morale = max(0, min(100, ship.morale + delta))
    return new_morale


def tick_morale_at_port(ship: Ship, has_officers_cabin: bool = False) -> int:
    """Update morale when arriving at port. Always positive.

    Base: +5, Officer's Cabin: +5 extra
    """
    bonus = 5
    if has_officers_cabin:
        bonus += 5
    return max(0, min(100, ship.morale + bonus))
