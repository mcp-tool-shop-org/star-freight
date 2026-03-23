"""Grid combat engine — Star Freight Phase 2.

Ship combat on a small hex-free grid. Ships are characters with big numbers.
Same engine works for ground combat later (different entities, same rules).

Design laws:
- Position matters (range, cover, hazards)
- Crew state matters (abilities from crew binding spine)
- Resolution matters (victory/loss/retreat write back to campaign)
- Tempo matters (5-8 turns typical)

This is NOT a tactics game engine. This is a captain's problem solver.
Combat is a campaign event, not a mode switch.

Pure functions where possible. CombatState is the mutable truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
import random as _random


# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------

GRID_WIDTH = 8
GRID_HEIGHT = 6


@dataclass(frozen=True)
class Pos:
    """Grid position. (0,0) is top-left."""
    x: int
    y: int

    def distance_to(self, other: Pos) -> int:
        """Chebyshev distance (king moves)."""
        return max(abs(self.x - other.x), abs(self.y - other.y))

    def in_bounds(self) -> bool:
        return 0 <= self.x < GRID_WIDTH and 0 <= self.y < GRID_HEIGHT


class TileType(str, Enum):
    EMPTY = "empty"
    ASTEROID = "asteroid"     # blocks movement and shots
    DEBRIS = "debris"         # half cover (+25% evasion)
    NEBULA = "nebula"         # hides occupant (no targeting beyond range 1)


@dataclass
class Tile:
    tile_type: TileType = TileType.EMPTY


# ---------------------------------------------------------------------------
# Combatants (ships or ground units — same interface)
# ---------------------------------------------------------------------------

class Team(str, Enum):
    PLAYER = "player"
    ENEMY = "enemy"


@dataclass
class CombatAbility:
    """An ability available during combat, sourced from crew binding."""
    id: str
    name: str
    description: str
    action_cost: int = 1         # actions consumed
    cooldown: int = 0            # turns between uses
    range_min: int = 0
    range_max: int = 99
    effect_type: str = "damage"  # damage | heal | buff | debuff | move | special
    effect_value: int = 0
    crew_source: str = ""        # crew_id that provides this (empty = innate)
    degraded: bool = False       # True if crew is injured (half effect)


@dataclass
class Combatant:
    """A ship or unit on the grid."""
    id: str
    name: str
    team: Team
    pos: Pos

    # Stats
    hp: int
    hp_max: int
    shield: int = 0
    shield_max: int = 0
    speed: int = 2               # tiles per move action
    evasion: float = 0.0         # 0.0–1.0 base dodge chance
    armor: int = 0               # flat damage reduction

    # Actions
    actions_per_turn: int = 2
    actions_remaining: int = 2

    # Weapons (base, always available)
    base_attack_damage: int = 150
    base_attack_range: int = 3

    # Abilities (from crew or innate)
    abilities: list[CombatAbility] = field(default_factory=list)
    ability_cooldowns: dict[str, int] = field(default_factory=dict)  # ability_id -> turns remaining

    # State
    alive: bool = True
    retreating: bool = False
    retreat_progress: int = 0    # turns spent retreating (need 2 to escape)
    buffs: dict[str, int] = field(default_factory=dict)  # buff_id -> turns remaining

    @property
    def effective_evasion(self) -> float:
        """Evasion including buffs."""
        bonus = 0.15 if "evasive" in self.buffs else 0.0
        return min(0.75, self.evasion + bonus)


RETREAT_TURNS_REQUIRED = 2


# ---------------------------------------------------------------------------
# Combat state
# ---------------------------------------------------------------------------

class CombatPhase(str, Enum):
    ACTIVE = "active"
    VICTORY = "victory"
    DEFEAT = "defeat"
    RETREAT = "retreat"
    DRAW = "draw"


@dataclass
class CombatEvent:
    """One thing that happened during combat."""
    turn: int
    actor_id: str
    action: str
    target_id: str = ""
    damage: int = 0
    heal: int = 0
    description: str = ""
    position: Pos | None = None


@dataclass
class CombatState:
    """Complete state of an active combat encounter."""
    grid: list[list[Tile]] = field(default_factory=lambda: [
        [Tile() for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)
    ])
    combatants: dict[str, Combatant] = field(default_factory=dict)
    turn: int = 1
    phase: CombatPhase = CombatPhase.ACTIVE
    turn_order: list[str] = field(default_factory=list)
    current_actor_idx: int = 0
    events: list[CombatEvent] = field(default_factory=list)
    rng: _random.Random = field(default_factory=_random.Random)

    @property
    def current_actor(self) -> Combatant | None:
        if not self.turn_order:
            return None
        if self.current_actor_idx >= len(self.turn_order):
            return None
        cid = self.turn_order[self.current_actor_idx]
        return self.combatants.get(cid)

    def player_ships(self) -> list[Combatant]:
        return [c for c in self.combatants.values() if c.team == Team.PLAYER and c.alive]

    def enemy_ships(self) -> list[Combatant]:
        return [c for c in self.combatants.values() if c.team == Team.ENEMY and c.alive]


# ---------------------------------------------------------------------------
# Grid helpers
# ---------------------------------------------------------------------------

def line_of_sight(state: CombatState, a: Pos, b: Pos) -> bool:
    """Check if there's a clear line between two positions (no asteroids blocking)."""
    # Simple: check tiles along the line for asteroids
    dx = b.x - a.x
    dy = b.y - a.y
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return True
    for i in range(1, steps):
        t = i / steps
        cx = round(a.x + dx * t)
        cy = round(a.y + dy * t)
        if 0 <= cy < GRID_HEIGHT and 0 <= cx < GRID_WIDTH:
            if state.grid[cy][cx].tile_type == TileType.ASTEROID:
                return False
    return True


def tile_at(state: CombatState, pos: Pos) -> Tile:
    """Get the tile at a position."""
    if not pos.in_bounds():
        return Tile(tile_type=TileType.ASTEROID)  # out of bounds = wall
    return state.grid[pos.y][pos.x]


def combatant_at(state: CombatState, pos: Pos) -> Combatant | None:
    """Get the combatant at a position, if any."""
    for c in state.combatants.values():
        if c.alive and c.pos == pos:
            return c
    return None


def in_cover(state: CombatState, pos: Pos) -> bool:
    """Check if a position has debris cover."""
    return tile_at(state, pos).tile_type == TileType.DEBRIS


def in_nebula(state: CombatState, pos: Pos) -> bool:
    """Check if a position is in a nebula."""
    return tile_at(state, pos).tile_type == TileType.NEBULA


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def init_combat(
    player_ships: list[Combatant],
    enemy_ships: list[Combatant],
    hazards: dict[Pos, TileType] | None = None,
    seed: int = 0,
) -> CombatState:
    """Initialize a combat encounter."""
    state = CombatState(rng=_random.Random(seed))

    # Place hazards
    if hazards:
        for pos, tt in hazards.items():
            if pos.in_bounds():
                state.grid[pos.y][pos.x] = Tile(tile_type=tt)

    # Register combatants
    for ship in player_ships + enemy_ships:
        state.combatants[ship.id] = ship

    # Turn order: alternating player/enemy by speed (descending)
    all_ships = sorted(
        [s for s in state.combatants.values()],
        key=lambda s: (-s.speed, s.id),
    )
    state.turn_order = [s.id for s in all_ships]
    state.current_actor_idx = 0

    return state


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------

def get_valid_moves(state: CombatState, combatant_id: str) -> list[Pos]:
    """Get all positions a combatant can move to."""
    c = state.combatants[combatant_id]
    if c.actions_remaining < 1:
        return []

    moves = []
    for dy in range(-c.speed, c.speed + 1):
        for dx in range(-c.speed, c.speed + 1):
            target = Pos(c.pos.x + dx, c.pos.y + dy)
            if not target.in_bounds():
                continue
            if target == c.pos:
                continue
            if c.pos.distance_to(target) > c.speed:
                continue
            tile = tile_at(state, target)
            if tile.tile_type == TileType.ASTEROID:
                continue
            if combatant_at(state, target) is not None:
                continue
            moves.append(target)
    return moves


def action_move(state: CombatState, combatant_id: str, target: Pos) -> CombatEvent | None:
    """Move a combatant to a new position. Costs 1 action."""
    c = state.combatants[combatant_id]
    if c.actions_remaining < 1:
        return None
    if target not in get_valid_moves(state, combatant_id):
        return None

    old_pos = c.pos
    c.pos = target
    c.actions_remaining -= 1

    # Moving cancels retreat
    if c.retreating:
        c.retreating = False
        c.retreat_progress = 0

    return CombatEvent(
        turn=state.turn, actor_id=combatant_id, action="move",
        description=f"{c.name} moves to ({target.x},{target.y}).",
        position=target,
    )


def get_valid_targets(state: CombatState, combatant_id: str) -> list[str]:
    """Get all combatants that can be attacked."""
    c = state.combatants[combatant_id]
    if c.actions_remaining < 1:
        return []

    targets = []
    for t in state.combatants.values():
        if t.team == c.team or not t.alive:
            continue
        dist = c.pos.distance_to(t.pos)
        if dist > c.base_attack_range:
            continue
        if not line_of_sight(state, c.pos, t.pos):
            continue
        # Can't target nebula beyond range 1
        if in_nebula(state, t.pos) and dist > 1:
            continue
        targets.append(t.id)
    return targets


def action_attack(state: CombatState, combatant_id: str, target_id: str) -> CombatEvent | None:
    """Basic attack. Costs 1 action."""
    c = state.combatants[combatant_id]
    if c.actions_remaining < 1:
        return None
    if target_id not in get_valid_targets(state, combatant_id):
        return None

    t = state.combatants[target_id]
    c.actions_remaining -= 1

    # Calculate hit
    evasion = t.effective_evasion
    if in_cover(state, t.pos):
        evasion = min(0.75, evasion + 0.25)

    if state.rng.random() < evasion:
        event = CombatEvent(
            turn=state.turn, actor_id=combatant_id, action="attack",
            target_id=target_id, damage=0,
            description=f"{c.name} fires at {t.name} — miss!",
        )
        state.events.append(event)
        return event

    # Damage: base - armor, minimum 10
    raw_damage = c.base_attack_damage
    damage = max(10, raw_damage - t.armor)

    # Apply to shield first, then hull
    shield_absorbed = min(t.shield, damage)
    t.shield -= shield_absorbed
    hull_damage = damage - shield_absorbed
    t.hp = max(0, t.hp - hull_damage)

    if t.hp <= 0:
        t.alive = False

    desc = f"{c.name} hits {t.name} for {damage} damage"
    if shield_absorbed > 0:
        desc += f" ({shield_absorbed} absorbed by shields)"
    if not t.alive:
        desc += f" — {t.name} destroyed!"

    event = CombatEvent(
        turn=state.turn, actor_id=combatant_id, action="attack",
        target_id=target_id, damage=damage,
        description=desc + ".",
    )
    state.events.append(event)
    return event


def action_defend(state: CombatState, combatant_id: str) -> CombatEvent:
    """Brace for impact. Costs 1 action. Grants evasion buff until next turn."""
    c = state.combatants[combatant_id]
    c.actions_remaining -= 1
    c.buffs["evasive"] = 1  # lasts 1 turn

    event = CombatEvent(
        turn=state.turn, actor_id=combatant_id, action="defend",
        description=f"{c.name} takes evasive action.",
    )
    state.events.append(event)
    return event


def action_retreat(state: CombatState, combatant_id: str) -> CombatEvent:
    """Begin or continue retreating. Costs all remaining actions.

    Takes RETREAT_TURNS_REQUIRED turns to escape.
    Moving cancels retreat progress.
    """
    c = state.combatants[combatant_id]
    c.actions_remaining = 0

    if not c.retreating:
        c.retreating = True
        c.retreat_progress = 1
        desc = f"{c.name} begins retreating!"
    else:
        c.retreat_progress += 1
        desc = f"{c.name} continues retreating ({c.retreat_progress}/{RETREAT_TURNS_REQUIRED})."

    event = CombatEvent(
        turn=state.turn, actor_id=combatant_id, action="retreat",
        description=desc,
    )
    state.events.append(event)
    return event


# ---------------------------------------------------------------------------
# Crew abilities in combat
# ---------------------------------------------------------------------------

def get_available_abilities(state: CombatState, combatant_id: str) -> list[CombatAbility]:
    """Get abilities that can be used this turn."""
    c = state.combatants[combatant_id]
    if c.actions_remaining < 1:
        return []

    available = []
    for ab in c.abilities:
        if ab.action_cost > c.actions_remaining:
            continue
        cd_remaining = c.ability_cooldowns.get(ab.id, 0)
        if cd_remaining > 0:
            continue
        available.append(ab)
    return available


def action_ability(
    state: CombatState,
    combatant_id: str,
    ability_id: str,
    target_id: str = "",
) -> CombatEvent | None:
    """Use a crew-sourced ability."""
    c = state.combatants[combatant_id]
    ab = None
    for a in c.abilities:
        if a.id == ability_id:
            ab = a
            break
    if ab is None:
        return None
    if ab.action_cost > c.actions_remaining:
        return None
    if c.ability_cooldowns.get(ability_id, 0) > 0:
        return None

    c.actions_remaining -= ab.action_cost
    if ab.cooldown > 0:
        c.ability_cooldowns[ability_id] = ab.cooldown

    # Apply effect
    effect_mult = 0.5 if ab.degraded else 1.0
    value = int(ab.effect_value * effect_mult)

    if ab.effect_type == "heal" and target_id:
        t = state.combatants.get(target_id, c)
        old_hp = t.hp
        t.hp = min(t.hp_max, t.hp + value)
        actual = t.hp - old_hp
        desc = f"{c.name} uses {ab.name} on {t.name} — repairs {actual} hull."
        if ab.degraded:
            desc += " (degraded — crew injured)"
        event = CombatEvent(
            turn=state.turn, actor_id=combatant_id, action="ability",
            target_id=target_id, heal=actual, description=desc,
        )
    elif ab.effect_type == "damage" and target_id:
        t = state.combatants[target_id]
        dist = c.pos.distance_to(t.pos)
        if dist < ab.range_min or dist > ab.range_max:
            return None
        if not line_of_sight(state, c.pos, t.pos):
            return None

        shield_absorbed = min(t.shield, value)
        t.shield -= shield_absorbed
        hull_damage = value - shield_absorbed
        t.hp = max(0, t.hp - hull_damage)
        if t.hp <= 0:
            t.alive = False

        desc = f"{c.name} uses {ab.name} — {value} damage to {t.name}."
        if ab.degraded:
            desc += " (degraded)"
        if not t.alive:
            desc += f" {t.name} destroyed!"
        event = CombatEvent(
            turn=state.turn, actor_id=combatant_id, action="ability",
            target_id=target_id, damage=value, description=desc,
        )
    elif ab.effect_type == "buff":
        c.buffs[ability_id] = ab.effect_value  # value = duration in turns
        desc = f"{c.name} uses {ab.name}."
        if ab.degraded:
            desc += " (degraded)"
        event = CombatEvent(
            turn=state.turn, actor_id=combatant_id, action="ability",
            description=desc,
        )
    else:
        # Generic ability
        desc = f"{c.name} uses {ab.name}."
        event = CombatEvent(
            turn=state.turn, actor_id=combatant_id, action="ability",
            description=desc,
        )

    state.events.append(event)
    return event


# ---------------------------------------------------------------------------
# Turn management
# ---------------------------------------------------------------------------

def start_turn(state: CombatState) -> None:
    """Begin a new turn. Reset actions, tick cooldowns and buffs."""
    for c in state.combatants.values():
        if not c.alive:
            continue
        c.actions_remaining = c.actions_per_turn

        # Tick cooldowns
        expired_cd = []
        for ab_id, remaining in c.ability_cooldowns.items():
            c.ability_cooldowns[ab_id] = max(0, remaining - 1)
            if c.ability_cooldowns[ab_id] == 0:
                expired_cd.append(ab_id)
        for ab_id in expired_cd:
            del c.ability_cooldowns[ab_id]

        # Tick buffs
        expired_buffs = []
        for buff_id, remaining in c.buffs.items():
            c.buffs[buff_id] = max(0, remaining - 1)
            if c.buffs[buff_id] == 0:
                expired_buffs.append(buff_id)
        for buff_id in expired_buffs:
            del c.buffs[buff_id]


def end_turn(state: CombatState) -> None:
    """Advance to next actor or next turn. Check for combat end."""
    # Check for retreat completion
    for c in state.combatants.values():
        if c.retreating and c.retreat_progress >= RETREAT_TURNS_REQUIRED and c.team == Team.PLAYER:
            state.phase = CombatPhase.RETREAT
            return

    # Check victory/defeat
    player_alive = any(c.alive for c in state.combatants.values() if c.team == Team.PLAYER)
    enemy_alive = any(c.alive for c in state.combatants.values() if c.team == Team.ENEMY)

    if not player_alive:
        state.phase = CombatPhase.DEFEAT
        return
    if not enemy_alive:
        state.phase = CombatPhase.VICTORY
        return

    # Advance to next living actor
    state.current_actor_idx += 1
    while state.current_actor_idx < len(state.turn_order):
        cid = state.turn_order[state.current_actor_idx]
        c = state.combatants.get(cid)
        if c and c.alive:
            return
        state.current_actor_idx += 1

    # All actors acted — next turn
    state.turn += 1
    state.current_actor_idx = 0
    start_turn(state)

    # Skip dead actors at start of new turn
    while state.current_actor_idx < len(state.turn_order):
        cid = state.turn_order[state.current_actor_idx]
        c = state.combatants.get(cid)
        if c and c.alive:
            return
        state.current_actor_idx += 1


# ---------------------------------------------------------------------------
# Enemy AI (simple, deterministic-seed)
# ---------------------------------------------------------------------------

def enemy_act(state: CombatState, combatant_id: str) -> list[CombatEvent]:
    """Simple enemy AI. Returns list of events produced.

    Strategy:
    1. If in range of a player ship, attack the weakest one.
    2. If not in range, move toward the nearest player ship.
    3. If badly damaged (<25% hp), try to flee (but enemies don't escape — they just defend).
    """
    c = state.combatants[combatant_id]
    events = []

    while c.actions_remaining > 0 and c.alive:
        # Find targets
        targets = get_valid_targets(state, combatant_id)

        # Badly damaged? Defend.
        if c.hp < c.hp_max * 0.25:
            events.append(action_defend(state, combatant_id))
            continue

        if targets:
            # Attack weakest target
            weakest = min(targets, key=lambda tid: state.combatants[tid].hp)
            event = action_attack(state, combatant_id, weakest)
            if event:
                events.append(event)
            else:
                break
        else:
            # Move toward nearest player ship
            player_ships = state.player_ships()
            if not player_ships:
                break
            nearest = min(player_ships, key=lambda p: c.pos.distance_to(p.pos))
            moves = get_valid_moves(state, combatant_id)
            if moves:
                best = min(moves, key=lambda m: m.distance_to(nearest.pos))
                event = action_move(state, combatant_id, best)
                if event:
                    events.append(event)
                else:
                    break
            else:
                # Can't move, defend
                events.append(action_defend(state, combatant_id))

    return events


# ---------------------------------------------------------------------------
# Campaign writeback
# ---------------------------------------------------------------------------

@dataclass
class CombatResult:
    """What combat returns to the campaign. This is the contract.

    Every field here changes what happens next in the captain's life.
    """
    outcome: CombatPhase                 # victory | defeat | retreat
    turns_taken: int
    player_hull_remaining: int
    player_hull_max: int
    player_shield_remaining: int
    enemy_destroyed: bool

    # Campaign consequences
    hull_damage_taken: int               # absolute hull damage to repair
    shield_damage_taken: int
    crew_injuries: list[str]             # crew_ids that should be injured
    cargo_lost: list[str]               # good_ids jettisoned on retreat
    reputation_delta: dict[str, int]     # faction_id -> change
    credits_gained: int                  # salvage/loot on victory
    consequence_tags: list[str]          # tags for consequence engine

    # Events log for display
    events: list[CombatEvent] = field(default_factory=list)


def resolve_combat(
    state: CombatState,
    encounter_faction: str = "",
    cargo_at_risk: list[str] | None = None,
    escalation_factor: float = 0.0,
) -> CombatResult:
    """Produce campaign-facing result from completed combat.

    This is the writeback contract. The campaign reads this and updates
    credits, reputation, crew injuries, ship damage, cargo, and consequences.
    """
    player = None
    for c in state.combatants.values():
        if c.team == Team.PLAYER:
            player = c
            break

    if player is None:
        # Shouldn't happen, but safety
        return CombatResult(
            outcome=state.phase, turns_taken=state.turn,
            player_hull_remaining=0, player_hull_max=0,
            player_shield_remaining=0, enemy_destroyed=False,
            hull_damage_taken=0, shield_damage_taken=0,
            crew_injuries=[], cargo_lost=[], reputation_delta={},
            credits_gained=0, consequence_tags=[], events=state.events,
        )

    hull_damage = player.hp_max - player.hp
    shield_damage = player.shield_max - player.shield
    enemy_destroyed = not any(c.alive for c in state.enemy_ships())

    # --- Outcome-specific consequences ---
    crew_injuries: list[str] = []
    cargo_lost: list[str] = []
    rep_delta: dict[str, int] = {}
    credits = 0
    tags: list[str] = []

    if state.phase == CombatPhase.VICTORY:
        # Salvage credits based on enemy size, diminished by escalation
        salvage_mult = max(0.2, 1.0 - escalation_factor)
        for c in state.combatants.values():
            if c.team == Team.ENEMY:
                credits += int(c.hp_max * 0.38 * salvage_mult)

        # Reputation: positive with your faction, negative with enemy's
        if encounter_faction:
            rep_delta[encounter_faction] = -5  # they hate you more
            rep_delta["compact"] = 2  # general lawfulness credit

        # Crew injury chance: base 20%, escalation adds up to 30% more
        injury_chance = 0.2 + escalation_factor * 0.3
        damage_threshold = max(0.15, 0.4 - escalation_factor * 0.25)
        if hull_damage > player.hp_max * damage_threshold:
            tags.append("heavy_damage")
            for ab in player.abilities:
                if ab.crew_source and state.rng.random() < injury_chance:
                    crew_injuries.append(ab.crew_source)

        # Escalation hull wear: consecutive fights grind the ship down
        if escalation_factor > 0:
            wear = int(player.hp_max * escalation_factor * 0.05)
            player.hp = max(1, player.hp - wear)
            tags.append("escalation_wear")

        tags.append("combat_victory")

    elif state.phase == CombatPhase.DEFEAT:
        # Cargo seized
        cargo_lost = list(cargo_at_risk or [])

        # Reputation hit
        if encounter_faction:
            rep_delta[encounter_faction] = 3  # they respect the fight
        rep_delta["compact"] = -3  # failure hurts standing

        # Crew injury: 40% per crew
        for ab in player.abilities:
            if ab.crew_source and state.rng.random() < 0.4:
                crew_injuries.append(ab.crew_source)

        tags.extend(["combat_defeat", "cargo_seized"])

    elif state.phase == CombatPhase.RETREAT:
        # Jettison some cargo to escape
        if cargo_at_risk:
            jettison_count = max(1, len(cargo_at_risk) // 3)
            cargo_lost = cargo_at_risk[:jettison_count]

        # Reputation: coward
        if encounter_faction:
            rep_delta[encounter_faction] = -2
        rep_delta["compact"] = -1  # slight shame

        # Crew morale hit (handled by campaign, not here)
        tags.extend(["combat_retreat", "cargo_jettisoned"])

    return CombatResult(
        outcome=state.phase,
        turns_taken=state.turn,
        player_hull_remaining=player.hp,
        player_hull_max=player.hp_max,
        player_shield_remaining=player.shield,
        enemy_destroyed=enemy_destroyed,
        hull_damage_taken=hull_damage,
        shield_damage_taken=shield_damage,
        crew_injuries=list(set(crew_injuries)),  # dedupe
        cargo_lost=cargo_lost,
        reputation_delta=rep_delta,
        credits_gained=credits,
        consequence_tags=tags,
        events=state.events,
    )
