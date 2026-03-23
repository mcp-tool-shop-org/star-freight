"""Crew binding spine — the thesis seam of Star Freight.

A crew member is a single campaign object that affects trade, tactics, and plot.
Presence, injury, morale, absence, and loyalty all have cross-system consequences.
The player feels the missing slot, not just reads about it.

This is NOT a bonus system. This is a dependency system.
A crew member is WHY you can do something, not a modifier on something you can already do.

Pure functions — callers decide what to mutate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Civilization(str, Enum):
    """The five civilizations of Star Freight."""
    COMPACT = "compact"
    KETH = "keth"
    VESHAN = "veshan"
    ORRYN = "orryn"
    REACH = "reach"


class CrewRole(str, Enum):
    """Crew specialization — determines ship ability and ground combat style."""
    GUNNER = "gunner"
    ENGINEER = "engineer"
    PILOT = "pilot"
    MEDIC = "medic"
    BROKER = "broker"
    FACE = "face"
    TECH = "tech"


class LoyaltyTier(str, Enum):
    """Loyalty progression — one-way. Once trusted, cannot revert."""
    STRANGER = "stranger"      # 0-30 pts
    TRUSTED = "trusted"        # 31-65 pts
    BONDED = "bonded"          # 66-100 pts


class CrewStatus(str, Enum):
    """Current availability state."""
    ACTIVE = "active"          # Available for all duties
    INJURED = "injured"        # Cannot fight, ship ability degraded
    RECOVERING = "recovering"  # Healing, limited duties
    DEPARTED = "departed"      # Gone permanently


# ---------------------------------------------------------------------------
# Core crew dataclass
# ---------------------------------------------------------------------------

@dataclass
class CrewMember:
    """A named crew member who is a binding constraint across all systems.

    This is not a stat block with bonuses. Every field here is something that
    changes what the player CAN DO, not how well they do it.
    """
    id: str                              # unique identifier
    name: str
    civilization: Civilization
    role: CrewRole

    # --- Combat identity ---
    hp: int = 100
    hp_max: int = 100
    speed: int = 3                       # grid tiles per turn
    abilities: list[str] = field(default_factory=list)  # 3 ability IDs; [2] locked until trusted
    ship_skill: str = ""                 # ability contributed to ship combat

    # --- Morale (0-100) ---
    morale: int = 45                     # starts low (stranger)
    morale_streak: int = 0               # consecutive days below departure threshold

    # --- Loyalty (one-way progression) ---
    loyalty_tier: LoyaltyTier = LoyaltyTier.STRANGER
    loyalty_points: int = 0              # 0-100

    # --- Status ---
    status: CrewStatus = CrewStatus.ACTIVE
    injury_days_remaining: int = 0       # 0 = not injured

    # --- Economy ---
    pay_rate: int = 50                   # credits per 30 days

    # --- Narrative ---
    narrative_hooks: list[str] = field(default_factory=list)  # active story hooks
    personal_quest_available: bool = False  # unlocked at TRUSTED
    loyalty_mission_available: bool = False  # unlocked at BONDED

    # --- Opinions (crew values — what they care about) ---
    opinions: dict[str, int] = field(default_factory=dict)  # topic -> -10..+10


# ---------------------------------------------------------------------------
# Roster (max 6)
# ---------------------------------------------------------------------------

MAX_CREW = 6

@dataclass
class CrewRosterState:
    """The player's active crew roster. Source of truth for crew state."""
    members: list[CrewMember] = field(default_factory=list)
    departed: list[str] = field(default_factory=list)  # IDs of crew who left permanently


# ---------------------------------------------------------------------------
# Recruitment
# ---------------------------------------------------------------------------

def can_recruit(
    roster: CrewRosterState,
    crew_id: str,
    player_credits: int,
    hire_cost: int,
) -> str | None:
    """Check if a crew member can be recruited. Returns error message or None."""
    if len(active_crew(roster)) >= MAX_CREW:
        return f"Crew is full (max {MAX_CREW})."

    if any(m.id == crew_id for m in roster.members):
        return f"Already in your crew."

    if crew_id in roster.departed:
        return "They left. They won't come back."

    if player_credits < hire_cost:
        return f"Need {hire_cost}₡ to recruit. You have {player_credits}₡."

    return None


def recruit(
    roster: CrewRosterState,
    member: CrewMember,
) -> None:
    """Add a crew member to the roster."""
    roster.members.append(member)


def dismiss(
    roster: CrewRosterState,
    crew_id: str,
) -> CrewMember | None:
    """Remove a crew member. Returns the removed member or None."""
    for i, m in enumerate(roster.members):
        if m.id == crew_id:
            removed = roster.members.pop(i)
            removed.status = CrewStatus.DEPARTED
            roster.departed.append(crew_id)
            return removed
    return None


# ---------------------------------------------------------------------------
# Active crew queries (the dependency surface)
# ---------------------------------------------------------------------------

def active_crew(roster: CrewRosterState) -> list[CrewMember]:
    """Crew members who are present and not departed."""
    return [m for m in roster.members if m.status != CrewStatus.DEPARTED]


def fit_crew(roster: CrewRosterState) -> list[CrewMember]:
    """Crew members who can fight (active and not injured)."""
    return [m for m in roster.members
            if m.status == CrewStatus.ACTIVE]


def crew_by_role(roster: CrewRosterState, role: CrewRole) -> CrewMember | None:
    """Find the first active crew member with a specific role."""
    for m in active_crew(roster):
        if m.role == role:
            return m
    return None


def crew_by_civ(roster: CrewRosterState, civ: Civilization) -> list[CrewMember]:
    """All active crew from a specific civilization."""
    return [m for m in active_crew(roster) if m.civilization == civ]


# ---------------------------------------------------------------------------
# Ship abilities (crew → ship binding)
# ---------------------------------------------------------------------------

def get_ship_abilities(roster: CrewRosterState) -> list[dict]:
    """Get the ship abilities provided by active, non-injured crew.

    Returns list of {crew_id, crew_name, ability, degraded}.
    An injured crew member's ability is degraded (half effect).
    A departed crew member provides nothing.
    """
    abilities = []
    for m in roster.members:
        if m.status == CrewStatus.DEPARTED:
            continue
        if not m.ship_skill:
            continue
        abilities.append({
            "crew_id": m.id,
            "crew_name": m.name,
            "ability": m.ship_skill,
            "degraded": m.status in (CrewStatus.INJURED, CrewStatus.RECOVERING),
        })
    return abilities


def ship_ability_available(roster: CrewRosterState, ability: str) -> bool:
    """Check if a specific ship ability is available (any crew provides it, undegraded)."""
    for m in roster.members:
        if m.status == CrewStatus.ACTIVE and m.ship_skill == ability:
            return True
    return False


def ship_ability_degraded(roster: CrewRosterState, ability: str) -> bool:
    """Check if a ship ability exists but is degraded (crew injured)."""
    for m in roster.members:
        if m.ship_skill == ability and m.status in (CrewStatus.INJURED, CrewStatus.RECOVERING):
            return True
    return False


# ---------------------------------------------------------------------------
# Cultural knowledge (crew → trade/culture binding)
# ---------------------------------------------------------------------------

def cultural_knowledge_level(
    roster: CrewRosterState,
    civ: Civilization,
    base_knowledge: dict[str, int],
) -> int:
    """Get effective cultural knowledge level for a civilization.

    Rules from State Dictionary:
    - Base knowledge from player experience (0-3)
    - Having an active crew member from that civ grants minimum level 1
    - Knowledge cannot exceed 3

    Args:
        roster: Current crew roster
        civ: Civilization to check
        base_knowledge: Player's own knowledge dict (civ_id -> 0-3)

    Returns:
        Effective knowledge level (0-3)
    """
    base = base_knowledge.get(civ.value, 0)
    has_civ_crew = any(
        m.civilization == civ and m.status != CrewStatus.DEPARTED
        for m in roster.members
    )
    if has_civ_crew:
        return max(base, 1)
    return base


def cultural_access_check(
    roster: CrewRosterState,
    civ: Civilization,
    base_knowledge: dict[str, int],
    required_level: int,
) -> tuple[bool, str]:
    """Check if the player has cultural access to something.

    Returns (has_access, reason).
    """
    level = cultural_knowledge_level(roster, civ, base_knowledge)
    if level >= required_level:
        if level == 0:
            return True, "Basic access."
        civ_crew = crew_by_civ(roster, civ)
        if civ_crew and level == 1:
            name = civ_crew[0].name
            return True, f"{name} provides cultural access."
        return True, f"Your knowledge of the {civ.value.title()} grants access."
    else:
        deficit = required_level - level
        if deficit == 1 and not crew_by_civ(roster, civ):
            return False, f"Need a {civ.value.title()} crew member or deeper knowledge."
        return False, f"Requires {civ.value.title()} knowledge level {required_level}. You have {level}."


# ---------------------------------------------------------------------------
# Combat abilities (crew → tactics binding)
# ---------------------------------------------------------------------------

def get_combat_abilities(roster: CrewRosterState) -> list[dict]:
    """Get ground combat abilities from fit crew.

    Returns list of {crew_id, crew_name, abilities, role}.
    Only fit (active, not injured) crew contribute.
    Third ability is locked until loyalty tier is TRUSTED.
    """
    result = []
    for m in fit_crew(roster):
        available = list(m.abilities[:2])  # first two always available
        if len(m.abilities) >= 3 and m.loyalty_tier != LoyaltyTier.STRANGER:
            available.append(m.abilities[2])
        result.append({
            "crew_id": m.id,
            "crew_name": m.name,
            "abilities": available,
            "role": m.role.value,
        })
    return result


def combat_ability_available(roster: CrewRosterState, ability_id: str) -> bool:
    """Check if a specific combat ability is available from any fit crew member."""
    for entry in get_combat_abilities(roster):
        if ability_id in entry["abilities"]:
            return True
    return False


# ---------------------------------------------------------------------------
# Narrative hooks (crew → plot binding)
# ---------------------------------------------------------------------------

def get_narrative_hooks(roster: CrewRosterState) -> list[dict]:
    """Get all active narrative hooks from crew.

    Returns list of {crew_id, crew_name, hooks, quest_available, mission_available}.
    """
    result = []
    for m in active_crew(roster):
        if m.narrative_hooks or m.personal_quest_available or m.loyalty_mission_available:
            result.append({
                "crew_id": m.id,
                "crew_name": m.name,
                "hooks": list(m.narrative_hooks),
                "quest_available": m.personal_quest_available,
                "mission_available": m.loyalty_mission_available,
            })
    return result


# ---------------------------------------------------------------------------
# Morale system
# ---------------------------------------------------------------------------

DEPARTURE_THRESHOLD = 25
DEPARTURE_STREAK_DAYS = 3


def apply_morale_change(
    member: CrewMember,
    delta: int,
    reason: str,
) -> dict:
    """Apply a morale change to a crew member.

    Returns {crew_id, old_morale, new_morale, delta, reason, departure_risk}.
    """
    old = member.morale
    member.morale = max(0, min(100, member.morale + delta))

    # Track departure streak
    if member.morale < DEPARTURE_THRESHOLD:
        member.morale_streak += 1
    else:
        member.morale_streak = 0

    return {
        "crew_id": member.id,
        "old_morale": old,
        "new_morale": member.morale,
        "delta": delta,
        "reason": reason,
        "departure_risk": member.morale_streak >= DEPARTURE_STREAK_DAYS,
    }


def check_departures(roster: CrewRosterState) -> list[dict]:
    """Check if any crew members should depart due to sustained low morale.

    Departure triggers at morale < 25 for 3+ consecutive days.
    Returns list of {crew_id, crew_name, reason}.
    """
    departures = []
    remaining = []

    for m in roster.members:
        if m.status == CrewStatus.DEPARTED:
            continue
        if m.morale_streak >= DEPARTURE_STREAK_DAYS:
            m.status = CrewStatus.DEPARTED
            roster.departed.append(m.id)
            departures.append({
                "crew_id": m.id,
                "crew_name": m.name,
                "reason": f"{m.name} has had enough. They leave at the next station.",
            })
        else:
            remaining.append(m)

    return departures


# ---------------------------------------------------------------------------
# Injury system
# ---------------------------------------------------------------------------

def injure(member: CrewMember, recovery_days: int) -> dict:
    """Injure a crew member. Returns state change summary.

    An injured crew member:
    - Cannot participate in ground combat
    - Ship ability is degraded (half effect)
    - Morale drops
    """
    old_status = member.status
    member.status = CrewStatus.INJURED
    member.injury_days_remaining = recovery_days
    member.hp = max(1, member.hp // 2)  # injuries reduce HP

    # Injury morale hit
    morale_result = apply_morale_change(member, -5, "injured in the line of duty")

    return {
        "crew_id": member.id,
        "crew_name": member.name,
        "old_status": old_status.value,
        "new_status": CrewStatus.INJURED.value,
        "recovery_days": recovery_days,
        "morale_change": morale_result,
        "effects": {
            "ground_combat": "unavailable",
            "ship_ability": "degraded",
        },
    }


def recover_day(member: CrewMember) -> dict | None:
    """Advance one day of recovery. Returns event dict if status changes, else None."""
    if member.status not in (CrewStatus.INJURED, CrewStatus.RECOVERING):
        return None

    member.injury_days_remaining = max(0, member.injury_days_remaining - 1)

    if member.injury_days_remaining <= 0:
        member.status = CrewStatus.ACTIVE
        member.hp = member.hp_max
        return {
            "crew_id": member.id,
            "crew_name": member.name,
            "event": "recovered",
            "message": f"{member.name} has recovered and is ready for duty.",
        }

    # Transition from injured to recovering at halfway point
    if member.status == CrewStatus.INJURED and member.injury_days_remaining <= 3:
        member.status = CrewStatus.RECOVERING
        return {
            "crew_id": member.id,
            "crew_name": member.name,
            "event": "recovering",
            "message": f"{member.name} is recovering. A few more days.",
        }

    return None


# ---------------------------------------------------------------------------
# Loyalty system (one-way progression)
# ---------------------------------------------------------------------------

LOYALTY_TRUSTED_THRESHOLD = 31
LOYALTY_BONDED_THRESHOLD = 66


def add_loyalty_points(member: CrewMember, points: int, reason: str) -> dict:
    """Add loyalty points. Tiers are one-way — cannot decrease.

    Returns {crew_id, old_tier, new_tier, points_added, total_points, unlocks}.
    """
    old_tier = member.loyalty_tier
    member.loyalty_points = min(100, member.loyalty_points + points)

    # Check tier progression (one-way)
    unlocks = []
    if member.loyalty_points >= LOYALTY_BONDED_THRESHOLD and member.loyalty_tier != LoyaltyTier.BONDED:
        member.loyalty_tier = LoyaltyTier.BONDED
        member.loyalty_mission_available = True
        unlocks.append("loyalty_mission")
        if len(member.abilities) >= 3:
            unlocks.append(f"ability:{member.abilities[2]}")

    elif member.loyalty_points >= LOYALTY_TRUSTED_THRESHOLD and member.loyalty_tier == LoyaltyTier.STRANGER:
        member.loyalty_tier = LoyaltyTier.TRUSTED
        member.personal_quest_available = True
        unlocks.append("personal_quest")
        if len(member.abilities) >= 3:
            unlocks.append(f"ability:{member.abilities[2]}")

    return {
        "crew_id": member.id,
        "crew_name": member.name,
        "old_tier": old_tier.value,
        "new_tier": member.loyalty_tier.value,
        "points_added": points,
        "total_points": member.loyalty_points,
        "reason": reason,
        "unlocks": unlocks,
    }


def daily_loyalty_tick(member: CrewMember) -> dict | None:
    """Daily loyalty accumulation. Morale > 50 for sustained periods builds loyalty.

    Returns loyalty event dict or None.
    """
    if member.status == CrewStatus.DEPARTED:
        return None
    if member.morale > 50:
        return add_loyalty_points(member, 1, "sustained high morale")
    return None


# ---------------------------------------------------------------------------
# Pay system
# ---------------------------------------------------------------------------

def calculate_crew_pay(roster: CrewRosterState) -> int:
    """Calculate total monthly crew pay for all active crew."""
    return sum(m.pay_rate for m in active_crew(roster))


def apply_pay_result(
    roster: CrewRosterState,
    paid: bool,
) -> list[dict]:
    """Apply payday results to all crew.

    paid=True: +2 morale each
    paid=False: -8 morale each (severe)
    """
    results = []
    for m in active_crew(roster):
        if paid:
            results.append(apply_morale_change(m, 2, "paid on time"))
        else:
            results.append(apply_morale_change(m, -8, "pay missed"))
    return results


# ---------------------------------------------------------------------------
# Cross-system impact query (the thesis test)
# ---------------------------------------------------------------------------

def crew_impact_report(
    roster: CrewRosterState,
    base_knowledge: dict[str, int],
) -> dict:
    """Generate a full cross-system impact report for the current crew state.

    This is the thesis in queryable form. It answers:
    - What can I do in combat because of my crew?
    - What ship abilities do I have?
    - What cultural access do I have?
    - What narrative threads are active?
    - What am I missing?
    """
    # Combat
    combat = get_combat_abilities(roster)
    combat_count = sum(len(e["abilities"]) for e in combat)

    # Ship
    ship = get_ship_abilities(roster)
    ship_active = [a for a in ship if not a["degraded"]]
    ship_degraded = [a for a in ship if a["degraded"]]

    # Cultural
    cultural = {}
    for civ in Civilization:
        level = cultural_knowledge_level(roster, civ, base_knowledge)
        civ_crew = crew_by_civ(roster, civ)
        cultural[civ.value] = {
            "level": level,
            "crew_source": [m.name for m in civ_crew],
            "access_reason": "crew member" if civ_crew and level == 1 else "player knowledge" if level > 0 else "none",
        }

    # Narrative
    narrative = get_narrative_hooks(roster)

    # Gaps
    missing_roles = [r for r in CrewRole if crew_by_role(roster, r) is None]
    missing_civs = [c for c in Civilization if not crew_by_civ(roster, c) and base_knowledge.get(c.value, 0) == 0]

    return {
        "combat_abilities_available": combat_count,
        "combat_crew": combat,
        "ship_abilities_active": ship_active,
        "ship_abilities_degraded": ship_degraded,
        "cultural_access": cultural,
        "narrative_hooks": narrative,
        "crew_count": len(active_crew(roster)),
        "fit_count": len(fit_crew(roster)),
        "missing_roles": [r.value for r in missing_roles],
        "missing_cultural_access": [c.value for c in missing_civs],
        "monthly_pay": calculate_crew_pay(roster),
    }
