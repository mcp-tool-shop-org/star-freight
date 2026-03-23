"""Captain memory — persistent NPC agency for pirate captains.

Each of the 8 named pirate captains remembers encounters with the player,
forms opinions along 4 axes (respect, fear, grudge, familiarity), and
acts autonomously between encounters based on their relationship state.

Cherry-picked from ai-rpg-engine's npc-agency.ts, adapted for Portlight's
maritime context.

Pure functions — callers decide what to mutate.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CaptainRelationship:
    """Four-axis relationship model for a pirate captain toward the player.

    respect:     -100..100  Earned in combat, trade, mercy. Lost by fleeing.
    fear:        0..100     From decisive victories, sinking ships.
    grudge:      0..100     From killing crew, refusing mercy, betrayal.
    familiarity: 0..100     Always increases per encounter.
    """
    respect: int = 0
    fear: int = 0
    grudge: int = 0
    familiarity: int = 0


@dataclass
class EncounterMemory:
    """Record of one encounter between captain and player."""
    day: int = 0
    region: str = ""
    outcome: str = ""        # player_won, player_lost, fled, negotiated, traded, ship_sunk
    player_spared: bool = False
    player_used_firearm: bool = False
    crew_killed: int = 0
    respect_delta: int = 0
    fear_delta: int = 0
    grudge_delta: int = 0
    familiarity_delta: int = 0


@dataclass
class CaptainMemory:
    """Persistent memory for one pirate captain."""
    captain_id: str = ""
    encounters: list[EncounterMemory] = field(default_factory=list)
    relationship: CaptainRelationship = field(default_factory=CaptainRelationship)
    last_seen_day: int = 0
    last_seen_region: str = ""
    times_spared: int = 0
    times_defeated_by_player: int = 0
    times_defeated_player: int = 0
    player_sank_their_ship: bool = False


# ---------------------------------------------------------------------------
# Breakpoints
# ---------------------------------------------------------------------------

BREAKPOINTS = ("ally", "rival", "prey", "nemesis", "neutral")


def derive_breakpoint(rel: CaptainRelationship) -> str:
    """Derive loyalty breakpoint from relationship axes. Top-to-bottom rules."""
    if rel.respect >= 50 and rel.grudge < 20:
        return "ally"
    if rel.grudge >= 50 or (rel.grudge >= 30 and rel.fear < 20):
        return "nemesis"
    if rel.fear >= 50 and rel.grudge < 40:
        return "prey"
    if rel.respect >= 30 and rel.familiarity >= 40:
        return "rival"
    return "neutral"


# ---------------------------------------------------------------------------
# Encounter recording
# ---------------------------------------------------------------------------

# Delta tables: outcome -> (respect, fear, grudge, familiarity)
_OUTCOME_DELTAS: dict[str, tuple[int, int, int, int]] = {
    "player_won":       (15, 10, 5, 10),
    "player_won_spared": (25, 5, -10, 15),
    "player_lost":      (5, -5, 0, 10),
    "ship_sunk":        (5, 20, 15, 10),
    "fled":             (-10, -10, 0, 5),
    "negotiated":       (5, 0, 0, 5),
    "traded":           (10, 0, -5, 10),
}

# Modifiers applied on top of base deltas
_FIREARM_MODIFIER = (-5, 10, 5, 0)  # dishonorable but scary
_HEAVY_CREW_KILL_MODIFIER = (0, 15, 20, 0)  # killing 5+ crew


def record_encounter(
    memory: CaptainMemory,
    day: int,
    region: str,
    outcome: str,
    player_spared: bool = False,
    player_used_firearm: bool = False,
    crew_killed: int = 0,
) -> EncounterMemory:
    """Record an encounter and update the captain's relationship.

    Returns the EncounterMemory created.
    """
    # Look up base deltas
    if player_spared and outcome == "player_won":
        key = "player_won_spared"
    else:
        key = outcome
    base = _OUTCOME_DELTAS.get(key, (0, 0, 0, 5))
    r_delta, f_delta, g_delta, fam_delta = base

    # Apply modifiers
    if player_used_firearm:
        r_delta += _FIREARM_MODIFIER[0]
        f_delta += _FIREARM_MODIFIER[1]
        g_delta += _FIREARM_MODIFIER[2]

    if crew_killed >= 5:
        r_delta += _HEAVY_CREW_KILL_MODIFIER[0]
        f_delta += _HEAVY_CREW_KILL_MODIFIER[1]
        g_delta += _HEAVY_CREW_KILL_MODIFIER[2]

    # Create memory
    enc = EncounterMemory(
        day=day, region=region, outcome=outcome,
        player_spared=player_spared,
        player_used_firearm=player_used_firearm,
        crew_killed=crew_killed,
        respect_delta=r_delta, fear_delta=f_delta,
        grudge_delta=g_delta, familiarity_delta=fam_delta,
    )

    # Apply to relationship
    rel = memory.relationship
    rel.respect = max(-100, min(100, rel.respect + r_delta))
    rel.fear = max(0, min(100, rel.fear + f_delta))
    rel.grudge = max(0, min(100, rel.grudge + g_delta))
    rel.familiarity = max(0, min(100, rel.familiarity + fam_delta))

    # Update tracking
    memory.encounters.append(enc)
    memory.last_seen_day = day
    memory.last_seen_region = region
    if player_spared:
        memory.times_spared += 1
    if outcome in ("player_won", "player_won_spared", "ship_sunk"):
        memory.times_defeated_by_player += 1
    if outcome == "player_lost":
        memory.times_defeated_player += 1
    if outcome == "ship_sunk":
        memory.player_sank_their_ship = True

    return enc


# ---------------------------------------------------------------------------
# Goal derivation
# ---------------------------------------------------------------------------

@dataclass
class CaptainGoal:
    """A goal a pirate captain wants to pursue."""
    verb: str           # challenge, warn, trade_offer, ambush, retreat, extort, gift, rumor
    priority: float     # 0.0..1.0
    reason: str         # human-readable


def derive_goals(
    memory: CaptainMemory,
    captain_region: str,
    player_region: str,
    player_silver: int,
    current_day: int,
) -> list[CaptainGoal]:
    """Generate priority-sorted goals for a captain."""
    rel = memory.relationship
    bp = derive_breakpoint(rel)
    goals: list[CaptainGoal] = []
    same_region = captain_region == player_region
    days_since = current_day - memory.last_seen_day if memory.last_seen_day > 0 else 999

    if bp == "ally":
        if same_region:
            goals.append(CaptainGoal("warn", 0.7, "Ally in your waters — wants to keep you safe"))
        if rel.respect >= 40:
            goals.append(CaptainGoal("trade_offer", 0.5, "Respects you enough to deal"))
        if rel.respect >= 60 and days_since > 20:
            goals.append(CaptainGoal("gift", 0.3, "Hasn't seen you in a while — sending regards"))

    elif bp == "rival":
        if same_region and rel.familiarity >= 40:
            goals.append(CaptainGoal("challenge", 0.6, "Wants to test you again"))
        if rel.respect >= 30:
            goals.append(CaptainGoal("trade_offer", 0.4, "Rival's respect — a deal between equals"))

    elif bp == "nemesis":
        if same_region:
            goals.append(CaptainGoal("ambush", 0.85, "Hunting you"))
        if rel.grudge >= 60:
            goals.append(CaptainGoal("bounty", 0.5, "Put a price on your head"))

    elif bp == "prey":
        if same_region:
            goals.append(CaptainGoal("retreat", 0.7, "Fears you — avoiding your waters"))

    else:  # neutral
        if same_region and player_silver > 300:
            goals.append(CaptainGoal("extort", 0.4, "Sees a fat purse"))

    # Universal: high familiarity generates tavern rumors
    if rel.familiarity >= 30:
        goals.append(CaptainGoal("rumor", 0.2, "Your name comes up in conversation"))

    goals.sort(key=lambda g: g.priority, reverse=True)
    return goals[:2]


# ---------------------------------------------------------------------------
# Autonomous action resolution
# ---------------------------------------------------------------------------

@dataclass
class CaptainAction:
    """An autonomous action taken by a pirate captain."""
    captain_id: str
    captain_name: str
    verb: str
    message: str          # player-facing text
    effect_type: str      # "message", "encounter", "contract", "silver", "reputation"
    effect_value: int = 0  # silver amount, etc.


def resolve_action(
    goal: CaptainGoal,
    memory: CaptainMemory,
    captain_name: str,
    faction_name: str,
) -> CaptainAction | None:
    """Resolve a captain goal into a concrete action. Returns None if no action."""
    cid = memory.captain_id

    if goal.verb == "warn":
        return CaptainAction(
            cid, captain_name, "warn",
            f"Word reaches you from {captain_name}: \"Watch your back in these waters. "
            f"{faction_name} isn't the only danger.\"",
            "message",
        )

    elif goal.verb == "trade_offer":
        return CaptainAction(
            cid, captain_name, "trade_offer",
            f"{captain_name} has left word at the dockmaster's office — "
            f"a private trade arrangement, captain to captain.",
            "contract",
        )

    elif goal.verb == "ambush":
        return CaptainAction(
            cid, captain_name, "ambush",
            f"Sails on the horizon — {captain_name} has found you. "
            f"There will be no negotiation this time.",
            "encounter",
        )

    elif goal.verb == "challenge":
        return CaptainAction(
            cid, captain_name, "challenge",
            f"A messenger arrives: {captain_name} challenges you to a duel. "
            f"\"Meet me at sea. Let's settle this properly.\"",
            "encounter",
        )

    elif goal.verb == "retreat":
        return CaptainAction(
            cid, captain_name, "retreat",
            f"The dockhand mentions that {captain_name}'s ship was spotted "
            f"heading out of the region in a hurry.",
            "message",
        )

    elif goal.verb == "extort":
        tribute = 30 + memory.relationship.familiarity
        return CaptainAction(
            cid, captain_name, "extort",
            f"{captain_name} sends a runner: \"Tribute. {tribute} silver. "
            f"Or we do this the other way.\"",
            "message", tribute,
        )

    elif goal.verb == "gift":
        gift = 15 + memory.times_spared * 10
        return CaptainAction(
            cid, captain_name, "gift",
            f"A crate arrives at your berth, marked with {captain_name}'s seal. "
            f"Inside: {gift} silver and a note — \"The sea remembers its friends.\"",
            "silver", gift,
        )

    elif goal.verb == "rumor":
        bp = derive_breakpoint(memory.relationship)
        opinion = {
            "ally": "speaks highly of",
            "rival": "respects but watches closely",
            "nemesis": "has a grudge against",
            "prey": "avoids any mention of",
            "neutral": "has crossed paths with",
        }.get(bp, "knows of")
        return CaptainAction(
            cid, captain_name, "rumor",
            f"Tavern talk: \"{captain_name} {opinion} a captain called "
            f"{'{'}player_name{'}'}.\"",
            "message",
        )

    return None


# ---------------------------------------------------------------------------
# Tick (called per day from session.advance)
# ---------------------------------------------------------------------------

def tick_captain_agency(
    memories: dict[str, CaptainMemory],
    player_region: str,
    player_silver: int,
    current_day: int,
    rng: random.Random,
) -> list[CaptainAction]:
    """Evaluate all captains, return 0-1 autonomous actions per day.

    Uses deterministic hash-based staggering so not all captains act at once.
    """
    from portlight.content.factions import FACTIONS, PIRATE_CAPTAINS

    actions: list[CaptainAction] = []

    for captain_id, captain_data in PIRATE_CAPTAINS.items():
        memory = memories.get(captain_id)
        if memory is None:
            continue  # no encounters yet, no agency
        if not memory.encounters:
            continue  # need at least one encounter to form opinions

        # Stagger: hash-based, ~1 action per 3-5 days per captain
        hash_input = f"{captain_id}:{current_day}"
        hash_val = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        bp = derive_breakpoint(memory.relationship)
        modulus = 3 if bp in ("nemesis", "ally") else 5
        if hash_val % modulus != 0:
            continue

        # Derive goals
        faction = FACTIONS.get(captain_data.faction_id)
        captain_region = memory.last_seen_region or (
            faction.territory_regions[0] if faction and faction.territory_regions else "Mediterranean"
        )

        goals = derive_goals(memory, captain_region, player_region, player_silver, current_day)
        if not goals:
            continue

        # Resolve top goal
        faction_name = faction.name if faction else "Unknown"
        action = resolve_action(goals[0], memory, captain_data.name, faction_name)
        if action:
            actions.append(action)

        if len(actions) >= 1:
            break  # max 1 action per day

    return actions


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_or_create_memory(
    memories: dict[str, CaptainMemory],
    captain_id: str,
) -> CaptainMemory:
    """Get existing memory or create a fresh one."""
    if captain_id not in memories:
        memories[captain_id] = CaptainMemory(captain_id=captain_id)
    return memories[captain_id]


def get_relationship_summary(memory: CaptainMemory) -> dict:
    """Get a summary dict for display purposes."""
    rel = memory.relationship
    bp = derive_breakpoint(rel)
    return {
        "breakpoint": bp,
        "respect": rel.respect,
        "fear": rel.fear,
        "grudge": rel.grudge,
        "familiarity": rel.familiarity,
        "encounters": len(memory.encounters),
        "times_spared": memory.times_spared,
        "last_seen_day": memory.last_seen_day,
    }
