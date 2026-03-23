"""Crew role specifications — wages, limits, and effect coefficients.

Each role provides specific bonuses when present on the ship.
Sailors are the baseline — cheap, unlimited, no special bonus.
Specialists cost more but provide powerful effects.
"""

from __future__ import annotations

from dataclasses import dataclass

from portlight.engine.models import CrewRole, CrewRoster


@dataclass
class RoleSpec:
    """Static definition of a crew role."""
    role: CrewRole
    name: str
    wage: int                    # silver per day per unit
    max_per_ship: int | None     # None = unlimited (sailors)
    description: str


ROLE_SPECS: dict[CrewRole, RoleSpec] = {
    CrewRole.SAILOR: RoleSpec(
        role=CrewRole.SAILOR,
        name="Sailor",
        wage=1,
        max_per_ship=None,
        description="Basic crew. Cheap, essential for sailing.",
    ),
    CrewRole.GUNNER: RoleSpec(
        role=CrewRole.GUNNER,
        name="Gunner",
        wage=2,
        max_per_ship=3,
        description="+10% broadside damage per gunner (max 3).",
    ),
    CrewRole.NAVIGATOR: RoleSpec(
        role=CrewRole.NAVIGATOR,
        name="Navigator",
        wage=3,
        max_per_ship=1,
        description="+0.5 speed, +5% storm resistance.",
    ),
    CrewRole.SURGEON: RoleSpec(
        role=CrewRole.SURGEON,
        name="Surgeon",
        wage=3,
        max_per_ship=1,
        description="Heals injuries at sea. -30% crew death from events.",
    ),
    CrewRole.MARINE: RoleSpec(
        role=CrewRole.MARINE,
        name="Marine",
        wage=2,
        max_per_ship=4,
        description="+20% boarding effectiveness per marine (max 4).",
    ),
    CrewRole.QUARTERMASTER: RoleSpec(
        role=CrewRole.QUARTERMASTER,
        name="Quartermaster",
        wage=2,
        max_per_ship=1,
        description="-10% crew wage bill, +5% sell prices.",
    ),
}


def get_role_count(roster: CrewRoster, role: CrewRole) -> int:
    """Get the count of a specific role from the roster."""
    field_map = {
        CrewRole.SAILOR: "sailors",
        CrewRole.GUNNER: "gunners",
        CrewRole.NAVIGATOR: "navigators",
        CrewRole.SURGEON: "surgeons",
        CrewRole.MARINE: "marines",
        CrewRole.QUARTERMASTER: "quartermasters",
    }
    return getattr(roster, field_map[role], 0)


def set_role_count(roster: CrewRoster, role: CrewRole, count: int) -> None:
    """Set the count of a specific role on the roster."""
    field_map = {
        CrewRole.SAILOR: "sailors",
        CrewRole.GUNNER: "gunners",
        CrewRole.NAVIGATOR: "navigators",
        CrewRole.SURGEON: "surgeons",
        CrewRole.MARINE: "marines",
        CrewRole.QUARTERMASTER: "quartermasters",
    }
    setattr(roster, field_map[role], max(0, count))
