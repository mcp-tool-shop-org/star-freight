"""Personal combat engine — interactive turn-based fighting.

Extends the original stance triangle (thrust/slash/parry) with:
  - Ranged weapons (shoot/throw) — the "magic equivalent"
  - Dodge — stamina-expensive evasion
  - Fighting style special actions — regional techniques
  - Stamina system — resource management across rounds
  - Injury risk — permanent consequences from heavy hits

The core triangle is preserved:
  Thrust beats Slash
  Slash beats Parry
  Parry beats Thrust

New interactions:
  Shoot — can't be parried, dodgeable, costs ammo + reload turn
  Throw — weaker, no reload, silent, dodgeable
  Dodge — avoids all melee + ranged, costs 2 stamina, 0 damage dealt
  Style actions — each has its own beats/loses_to, stamina cost, cooldown

Pure functions — callers decide what to mutate.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from portlight.content.fighting_styles import FIGHTING_STYLES, FightingStyle
from portlight.content.ranged_weapons import RANGED_WEAPONS
from portlight.engine.injuries import get_injury_effects, roll_injury


# ---------------------------------------------------------------------------
# Combat state
# ---------------------------------------------------------------------------

@dataclass
class CombatantState:
    """Mutable state of one combatant during a fight."""
    hp: int
    hp_max: int
    stamina: int
    stamina_max: int
    ammo: int = 0                       # firearm rounds
    throwing_weapons: int = 0           # total throwing items
    throwing_weapon_ids: list[str] = field(default_factory=list)  # ordered list of throw types
    active_style: str | None = None
    injury_ids: list[str] = field(default_factory=list)
    # Per-fight tracking
    reload_turns: int = 0               # turns until firearm ready (0 = ready)
    last_action: str | None = None      # for consecutive-dodge prevention
    style_cooldowns: dict[str, int] = field(default_factory=dict)
    stun_turns: int = 0                 # turns of stun remaining
    # Weapon metadata
    firearm_id: str | None = None
    mechanical_weapon_id: str | None = None
    mechanical_ammo: int = 0
    mechanical_reload: int = 0
    # Armor
    armor_dr: int = 0                   # flat damage reduction from armor
    dodge_stamina_penalty: int = 0      # extra dodge cost from armor
    # Melee weapon
    melee_weapon_id: str | None = None
    # Weapon quality
    melee_quality: str = "standard"
    ranged_quality: str = "standard"


# ---------------------------------------------------------------------------
# Combat round result
# ---------------------------------------------------------------------------

@dataclass
class CombatRound:
    """Result of one round of personal combat."""
    turn: int
    player_action: str
    opponent_action: str
    damage_to_opponent: int = 0
    damage_to_player: int = 0
    player_stamina_delta: int = 0
    opponent_stamina_delta: int = 0
    injury_inflicted: str | None = None     # injury_id if player took one
    opponent_injury: str | None = None      # injury_id if opponent took one
    flavor: str = ""
    style_effect: str | None = None


@dataclass
class CombatResult:
    """Outcome of a completed personal combat."""
    opponent_id: str
    opponent_name: str
    player_won: bool
    draw: bool = False
    rounds: list[CombatRound] = field(default_factory=list)
    silver_delta: int = 0
    standing_delta: int = 0
    injuries_sustained: list[str] = field(default_factory=list)
    opponent_injuries: list[str] = field(default_factory=list)
    ammo_spent: int = 0
    throwing_spent: int = 0


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CORE_ACTIONS = ("thrust", "slash", "parry")
RANGED_ACTIONS = ("shoot", "throw")
DEFENSIVE_ACTIONS = ("dodge",)
ALL_BASE_ACTIONS = CORE_ACTIONS + RANGED_ACTIONS + DEFENSIVE_ACTIONS

# Stance triangle (same as duel.py)
_BEATS = {
    "thrust": "slash",
    "slash": "parry",
    "parry": "thrust",
}

BASE_PLAYER_HP = 12
BASE_PLAYER_STAMINA = 8
BASE_OPPONENT_HP = 10
STAMINA_REGEN_PER_TURN = 1
PARRY_STAMINA_BONUS = 1

# Stamina costs
STAMINA_COSTS = {
    "thrust": 1,
    "slash": 1,
    "parry": 1,
    "shoot": 0,
    "throw": 0,
    "dodge": 2,
}


# ---------------------------------------------------------------------------
# Combatant initialization
# ---------------------------------------------------------------------------

def create_player_combatant(
    crew: int = 5,
    active_style: str | None = None,
    injury_ids: list[str] | None = None,
    firearm_id: str | None = None,
    firearm_ammo: int = 0,
    throwing_weapons: int = 0,
    throwing_weapon_ids: list[str] | None = None,
    mechanical_weapon_id: str | None = None,
    mechanical_ammo: int = 0,
    armor_id: str | None = None,
    melee_weapon_id: str | None = None,
    melee_quality: str = "standard",
    ranged_quality: str = "standard",
) -> CombatantState:
    """Create player combatant state from captain attributes."""
    injuries = injury_ids or []
    effects = get_injury_effects(injuries)

    crew_bonus = max(0, crew - 5)
    hp = BASE_PLAYER_HP + (crew_bonus // 5) + effects["hp_max_mod"]

    style_hp_bonus = 0
    style_stamina_bonus = 0
    if active_style:
        style = FIGHTING_STYLES.get(active_style)
        if style:
            style_hp_bonus = style.passive_hp_bonus

    hp += style_hp_bonus
    stamina = BASE_PLAYER_STAMINA + effects["stamina_max_mod"] + style_stamina_bonus

    # Armor effects
    armor_dr = 0
    dodge_pen = 0
    if armor_id:
        from portlight.content.armor import ARMOR
        armor_def = ARMOR.get(armor_id)
        if armor_def:
            armor_dr = armor_def.damage_reduction
            dodge_pen = armor_def.dodge_penalty
            stamina += armor_def.stamina_penalty  # negative for medium/heavy

    # Melee weapon speed modifier
    if melee_weapon_id:
        from portlight.content.melee_weapons import MELEE_WEAPONS
        weapon_def = MELEE_WEAPONS.get(melee_weapon_id)
        if weapon_def:
            stamina += weapon_def.speed_mod

    # Build throwing weapon ID list (expand dict into ordered list)
    tw_ids = list(throwing_weapon_ids) if throwing_weapon_ids else []
    if not tw_ids and throwing_weapons > 0:
        tw_ids = ["throwing_knife"] * throwing_weapons  # fallback

    return CombatantState(
        hp=max(1, hp),
        hp_max=max(1, hp),
        stamina=max(1, stamina),
        stamina_max=max(1, stamina),
        ammo=firearm_ammo,
        throwing_weapons=throwing_weapons,
        throwing_weapon_ids=tw_ids,
        active_style=active_style,
        injury_ids=list(injuries),
        firearm_id=firearm_id,
        mechanical_weapon_id=mechanical_weapon_id,
        mechanical_ammo=mechanical_ammo,
        armor_dr=armor_dr,
        dodge_stamina_penalty=dodge_pen,
        melee_weapon_id=melee_weapon_id,
        melee_quality=melee_quality,
        ranged_quality=ranged_quality,
    )


def create_opponent_combatant(
    strength: int,
    personality: str,
    active_style: str | None = None,
    ammo: int = 0,
    throwing_weapons: int = 0,
) -> CombatantState:
    """Create opponent combatant from pirate captain attributes."""
    hp = BASE_OPPONENT_HP + (strength - 5) * 2
    hp = max(6, hp)
    stamina = 6 + strength // 2

    return CombatantState(
        hp=hp,
        hp_max=hp,
        stamina=max(3, stamina),
        stamina_max=max(3, stamina),
        ammo=ammo,
        throwing_weapons=throwing_weapons,
        active_style=active_style,
    )


# ---------------------------------------------------------------------------
# Action validation
# ---------------------------------------------------------------------------

def get_available_actions(state: CombatantState) -> list[str]:
    """Get actions available to a combatant this turn."""
    if state.stun_turns > 0:
        return ["dodge"]  # stunned: can only dodge

    effects = get_injury_effects(state.injury_ids)
    actions: list[str] = []

    # Core triangle always available
    actions.extend(CORE_ACTIONS)

    # Ranged: shoot requires ammo and no reload cooldown and can_use_firearms
    if state.ammo > 0 and state.reload_turns <= 0 and effects["can_use_firearms"]:
        actions.append("shoot")
    if state.mechanical_ammo > 0 and state.mechanical_reload <= 0 and effects["can_use_firearms"]:
        if "shoot" not in actions:
            actions.append("shoot")

    # Throw requires throwing weapons
    if state.throwing_weapons > 0:
        actions.append("throw")

    # Dodge: not if can't dodge (shattered knee), not if used last turn
    if effects["can_dodge"] and state.last_action != "dodge":
        actions.append("dodge")

    # Style special action
    if state.active_style:
        style = FIGHTING_STYLES.get(state.active_style)
        if style and style.special_action:
            sa = style.special_action
            cooldown = state.style_cooldowns.get(sa.id, 0)
            if cooldown <= 0 and state.stamina >= sa.stamina_cost:
                actions.append(sa.id)

    return actions


# ---------------------------------------------------------------------------
# Stance/action outcome
# ---------------------------------------------------------------------------

def _resolve_melee_outcome(attacker_action: str, defender_action: str) -> str:
    """Resolve melee interaction. Returns 'win', 'lose', or 'draw'."""
    if attacker_action == defender_action:
        return "draw"
    if _BEATS.get(attacker_action) == defender_action:
        return "win"
    return "lose"


# ---------------------------------------------------------------------------
# Damage calculation
# ---------------------------------------------------------------------------

def _calc_melee_damage(
    action: str,
    outcome: str,
    rng: random.Random,
    style: FightingStyle | None = None,
    injury_effects: dict | None = None,
    melee_weapon_id: str | None = None,
    weapon_quality: str = "standard",
) -> int:
    """Calculate melee damage for an action that won its interaction."""
    if outcome != "win":
        return 0

    base = rng.randint(2, 3)
    bonus = 0

    if injury_effects:
        bonus += injury_effects.get("melee_damage_mod", 0)
        if action == "thrust":
            base = int(base * injury_effects.get("thrust_multiplier", 1.0))

    if style:
        if action == "thrust":
            bonus += style.passive_thrust_bonus
        elif action == "slash":
            bonus += style.passive_slash_bonus

    # Melee weapon bonuses
    if melee_weapon_id:
        from portlight.content.melee_weapons import MELEE_WEAPONS
        weapon = MELEE_WEAPONS.get(melee_weapon_id)
        if weapon:
            bonus += weapon.damage_bonus
            if action == "thrust":
                bonus += weapon.thrust_bonus
            elif action == "slash":
                bonus += weapon.slash_bonus
            # Style compatibility: +1 if active style matches weapon
            if style and style.id in weapon.compatible_styles:
                bonus += 1

    # Weapon quality modifier
    from portlight.engine.weapon_quality import get_quality_effects
    q_effects = get_quality_effects(weapon_quality)
    bonus += q_effects.damage_mod

    return max(0, base + bonus)


def _calc_ranged_damage(
    weapon_id: str | None,
    rng: random.Random,
    accuracy_mod: float = 0.0,
    weapon_quality: str = "standard",
) -> tuple[int, bool]:
    """Calculate ranged damage. Returns (damage, hit)."""
    if weapon_id is None:
        return 0, False

    weapon = RANGED_WEAPONS.get(weapon_id)
    if weapon is None:
        return 0, False

    from portlight.engine.weapon_quality import get_quality_effects
    q_effects = get_quality_effects(weapon_quality)
    accuracy = weapon.accuracy + accuracy_mod + q_effects.accuracy_mod
    if rng.random() > accuracy:
        return 0, False  # miss

    damage = rng.randint(weapon.damage_min, weapon.damage_max)
    return damage, True


def _calc_throw_damage(
    weapon_id: str | None,
    rng: random.Random,
    accuracy_mod: float = 0.0,
) -> tuple[int, bool, int]:
    """Calculate throwing weapon damage using actual weapon stats.

    Returns (damage, hit, stun_turns).
    Falls back to generic 2-3 / 0.70 if weapon not found.
    """
    weapon = RANGED_WEAPONS.get(weapon_id) if weapon_id else None
    if weapon is None:
        accuracy = 0.70 + accuracy_mod
        if rng.random() > accuracy:
            return 0, False, 0
        return rng.randint(2, 3), True, 0

    accuracy = weapon.accuracy + accuracy_mod
    if rng.random() > accuracy:
        return 0, False, 0
    damage = rng.randint(weapon.damage_min, weapon.damage_max)
    return damage, True, weapon.stun_turns


# ---------------------------------------------------------------------------
# Style action resolution
# ---------------------------------------------------------------------------

def _resolve_style_action(
    style_action_id: str,
    opponent_action: str,
    style: FightingStyle,
    rng: random.Random,
) -> tuple[str, int, str]:
    """Resolve a style special action vs opponent action.

    Returns (outcome, damage_bonus, effect_description).
    outcome: "win", "lose", "draw"
    """
    sa = style.special_action
    if sa is None or sa.id != style_action_id:
        return "draw", 0, ""

    if opponent_action in sa.beats:
        return "win", sa.damage_bonus, sa.flavor
    elif opponent_action in sa.loses_to:
        return "lose", 0, f"Your {sa.name} is countered!"
    else:
        return "draw", 0, f"Your {sa.name} meets resistance."


# ---------------------------------------------------------------------------
# Round resolution
# ---------------------------------------------------------------------------

_MELEE_FLAVOR = {
    ("thrust", "win"):  "Your blade finds its mark — a clean thrust past their guard.",
    ("thrust", "lose"): "You lunge forward, but their parry turns your blade aside.",
    ("thrust", "draw"): "Both blades extend. Steel rings against steel.",
    ("slash", "win"):   "A wide arc catches them mid-parry. The cut connects.",
    ("slash", "lose"):  "Your slash meets empty air — they were already thrusting.",
    ("slash", "draw"):  "Blades cross in a shower of sparks.",
    ("parry", "win"):   "You read the thrust perfectly. Your counter finds the opening.",
    ("parry", "lose"):  "You brace for a thrust that never comes — the slash catches your side.",
    ("parry", "draw"):  "Both hold their ground, blades locked.",
}


def resolve_combat_round(
    player_action: str,
    player_state: CombatantState,
    opponent_state: CombatantState,
    opponent_personality: str,
    rng: random.Random,
) -> CombatRound:
    """Resolve one round of personal combat.

    Handles the full action matrix: melee triangle, ranged, dodge, style actions.
    Returns CombatRound with damage, stamina changes, injuries, and flavor.
    """
    player_style = FIGHTING_STYLES.get(player_state.active_style) if player_state.active_style else None
    player_effects = get_injury_effects(player_state.injury_ids)

    # Opponent picks action
    opp_action = pick_opponent_action(
        opponent_personality, opponent_state, player_state,
        player_state.last_action, rng,
    )

    dmg_to_opponent = 0
    dmg_to_player = 0
    p_stamina_delta = 0
    o_stamina_delta = 0
    flavor = ""
    style_effect = None
    player_injury = None
    opponent_injury = None

    # --- Stamina costs ---
    p_cost = STAMINA_COSTS.get(player_action, 0)
    if player_action == "dodge":
        p_cost += player_state.dodge_stamina_penalty  # armor weight penalty
    if player_style and player_style.special_action and player_action == player_style.special_action.id:
        p_cost = player_style.special_action.stamina_cost
    p_stamina_delta -= p_cost

    o_cost = STAMINA_COSTS.get(opp_action, 0)
    o_stamina_delta -= o_cost

    # --- Resolve interactions ---

    # Both dodge
    if player_action == "dodge" and opp_action == "dodge":
        flavor = "Both fighters circle warily. Neither commits."

    # Player dodges
    elif player_action == "dodge":
        flavor = "You dive aside, avoiding the attack entirely."
        if player_style and player_style.passive_dodge_counter > 0:
            dmg_to_opponent = player_style.passive_dodge_counter
            flavor += f" Your counterstrike catches them for {dmg_to_opponent} damage."

    # Opponent dodges
    elif opp_action == "dodge":
        flavor = "They dodge your attack with practiced ease."

    # Player shoots
    elif player_action == "shoot":
        if opp_action == "dodge":
            flavor = "Your shot goes wide as they dive aside."
        else:
            # Determine which weapon to use
            weapon_id = player_state.firearm_id
            if weapon_id is None or player_state.ammo <= 0:
                weapon_id = player_state.mechanical_weapon_id

            accuracy_mod = player_effects.get("ranged_accuracy_mod", 0.0)
            if player_style:
                accuracy_mod += player_style.passive_ranged_accuracy

            dmg, hit = _calc_ranged_damage(weapon_id, rng, accuracy_mod, player_state.ranged_quality)
            if hit:
                dmg_to_opponent = dmg
                flavor = f"Your shot strikes true — {dmg} damage!"
                if opp_action == "parry":
                    flavor = f"They try to parry but a bullet cares nothing for steel. {dmg} damage!"
            else:
                flavor = "Your shot goes wide. The powder smoke stings your eyes."

            # Opponent still gets their action (unless they dodged, handled above)
            if opp_action in CORE_ACTIONS:
                opp_dmg = rng.randint(2, 3) if opp_action != "parry" else 0
                if opp_action == "thrust" or opp_action == "slash":
                    dmg_to_player = opp_dmg
                    flavor += f" But their {opp_action} finds you for {opp_dmg}."

    # Opponent shoots
    elif opp_action == "shoot":
        if player_action == "dodge":
            pass  # already handled above
        else:
            opp_dmg = rng.randint(4, 6)  # opponent generic ranged
            accuracy = 0.65
            if rng.random() <= accuracy:
                dmg_to_player = opp_dmg
                flavor = f"A gunshot cracks — {opp_dmg} damage!"
                if player_action == "parry":
                    flavor = f"You raise your guard but the bullet punches through. {opp_dmg} damage!"
            else:
                flavor = "A gunshot cracks but the ball goes wide."

            # Player still gets melee
            if player_action in CORE_ACTIONS and player_action != "parry":
                p_dmg = _calc_melee_damage(player_action, "win", rng, player_style, player_effects, player_state.melee_weapon_id, player_state.melee_quality)
                dmg_to_opponent = p_dmg
                if p_dmg > 0:
                    flavor += f" Your {player_action} connects for {p_dmg}."

    # Player throws
    elif player_action == "throw":
        if opp_action == "dodge":
            flavor = "Your throwing weapon sails past as they dodge."
        else:
            # Look up actual thrown weapon type
            throw_wid = player_state.throwing_weapon_ids[0] if player_state.throwing_weapon_ids else None
            accuracy_mod = player_effects.get("ranged_accuracy_mod", 0.0)
            if player_style:
                accuracy_mod += player_style.passive_ranged_accuracy
            dmg, hit, stun = _calc_throw_damage(throw_wid, rng, accuracy_mod)
            if hit:
                dmg_to_opponent = dmg
                weapon_name = throw_wid.replace("_", " ").title() if throw_wid else "blade"
                flavor = f"Your {weapon_name} strikes — {dmg} damage!"
                # Apply stun (bolas)
                if stun > 0:
                    opponent_state.stun_turns = max(opponent_state.stun_turns, stun)
                    flavor += f" They're tangled — stunned for {stun} turn!"
            else:
                flavor = "Your throw goes wide."

            if opp_action in CORE_ACTIONS:
                opp_dmg = rng.randint(2, 3) if opp_action != "parry" else 0
                if opp_action in ("thrust", "slash"):
                    dmg_to_player = opp_dmg
                    if opp_dmg > 0:
                        flavor += f" Their {opp_action} catches you for {opp_dmg}."

    # Opponent throws
    elif opp_action == "throw":
        opp_dmg = rng.randint(2, 3) if rng.random() < 0.70 else 0
        if opp_dmg > 0:
            dmg_to_player = opp_dmg
            flavor = f"A thrown blade catches you — {opp_dmg} damage!"
        else:
            flavor = "A thrown weapon clatters past you."

        if player_action in CORE_ACTIONS:
            outcome = "win"  # melee beats throw
            p_dmg = _calc_melee_damage(player_action, outcome, rng, player_style, player_effects, player_state.melee_weapon_id, player_state.melee_quality)
            dmg_to_opponent = p_dmg
            if p_dmg > 0:
                flavor += f" Your {player_action} connects for {p_dmg}."

    # Style action vs anything
    elif player_style and player_style.special_action and player_action == player_style.special_action.id:
        outcome, bonus_dmg, effect_desc = _resolve_style_action(
            player_action, opp_action, player_style, rng,
        )
        style_effect = effect_desc

        if outcome == "win":
            base = rng.randint(2, 3) + bonus_dmg
            base += player_effects.get("melee_damage_mod", 0)
            dmg_to_opponent = max(0, base)
            flavor = effect_desc
        elif outcome == "lose":
            opp_dmg = rng.randint(2, 3)
            dmg_to_player = opp_dmg
            flavor = effect_desc
        else:
            dmg_to_opponent = 1
            dmg_to_player = 1
            flavor = effect_desc or "A glancing exchange."

    # Both melee (core triangle)
    elif player_action in CORE_ACTIONS and opp_action in CORE_ACTIONS:
        outcome = _resolve_melee_outcome(player_action, opp_action)

        if outcome == "win":
            dmg_to_opponent = _calc_melee_damage(player_action, outcome, rng, player_style, player_effects, player_state.melee_weapon_id, player_state.melee_quality)
        elif outcome == "lose":
            dmg_to_player = rng.randint(2, 3)
        else:
            # Draw: both chose same stance — no damage exchanged
            dmg_to_opponent = 0
            dmg_to_player = 0

        flavor = _MELEE_FLAVOR.get((player_action, outcome), "Blades clash.")

        # Parry stamina bonus
        if player_action == "parry":
            parry_bonus = PARRY_STAMINA_BONUS
            if player_style:
                parry_bonus += player_style.passive_parry_bonus
            p_stamina_delta += parry_bonus
        if opp_action == "parry":
            o_stamina_delta += PARRY_STAMINA_BONUS

    # Fallback
    else:
        flavor = "An awkward exchange. Neither fighter gains ground."

    # --- Stamina regen ---
    p_stamina_delta += STAMINA_REGEN_PER_TURN
    o_stamina_delta += STAMINA_REGEN_PER_TURN

    # --- Armor DR (applied before injury rolls so DR prevents injuries too) ---
    if dmg_to_player > 0 and player_state.armor_dr > 0:
        dmg_to_player = max(0, dmg_to_player - player_state.armor_dr)
    if dmg_to_opponent > 0 and opponent_state.armor_dr > 0:
        dmg_to_opponent = max(0, dmg_to_opponent - opponent_state.armor_dr)

    # --- Injury rolls ---
    injury_bonus = 0.0
    if player_style:
        injury_bonus = player_style.passive_injury_bonus

    if dmg_to_player >= 4:
        attack_type = _attack_type_for_action(opp_action)
        player_injury = roll_injury(dmg_to_player, attack_type, rng)

    if dmg_to_opponent >= 4:
        attack_type = _attack_type_for_action(player_action)
        opponent_injury = roll_injury(dmg_to_opponent, attack_type, rng, injury_bonus)

    return CombatRound(
        turn=0,  # caller sets
        player_action=player_action,
        opponent_action=opp_action,
        damage_to_opponent=dmg_to_opponent,
        damage_to_player=dmg_to_player,
        player_stamina_delta=p_stamina_delta,
        opponent_stamina_delta=o_stamina_delta,
        injury_inflicted=player_injury,
        opponent_injury=opponent_injury,
        flavor=flavor,
        style_effect=style_effect,
    )


def _attack_type_for_action(action: str) -> str:
    """Map combat action to attack type for injury pool selection."""
    if action in ("shoot",):
        return "shoot"
    if action in ("slash", "cleave"):
        return "slash"
    return "thrust"  # default for thrust, style actions, throw


# ---------------------------------------------------------------------------
# Opponent AI
# ---------------------------------------------------------------------------

_COMBAT_AI_WEIGHTS: dict[str, dict[str, float]] = {
    "aggressive": {"thrust": 0.40, "slash": 0.30, "parry": 0.10, "shoot": 0.10, "throw": 0.05, "dodge": 0.05},
    "defensive":  {"thrust": 0.15, "slash": 0.15, "parry": 0.35, "shoot": 0.10, "throw": 0.05, "dodge": 0.20},
    "balanced":   {"thrust": 0.25, "slash": 0.25, "parry": 0.20, "shoot": 0.10, "throw": 0.05, "dodge": 0.15},
    "wild":       {"thrust": 0.20, "slash": 0.20, "parry": 0.15, "shoot": 0.15, "throw": 0.15, "dodge": 0.15},
}


def pick_opponent_action(
    personality: str,
    opponent_state: CombatantState,
    player_state: CombatantState,
    player_last_action: str | None,
    rng: random.Random,
) -> str:
    """Pick opponent combat action based on personality and state."""
    weights = dict(_COMBAT_AI_WEIGHTS.get(personality, _COMBAT_AI_WEIGHTS["balanced"]))

    # Can't shoot without ammo or while reloading
    if opponent_state.ammo <= 0 or opponent_state.reload_turns > 0:
        weights["shoot"] = 0.0

    # Can't throw without weapons
    if opponent_state.throwing_weapons <= 0:
        weights["throw"] = 0.0

    # Can't dodge twice in a row
    if opponent_state.last_action == "dodge":
        weights["dodge"] = 0.0

    # Not enough stamina for dodge
    if opponent_state.stamina < 2:
        weights["dodge"] = 0.0

    # Balanced adapts: counter repeated player actions
    if personality == "balanced" and player_last_action:
        if player_last_action == "thrust":
            weights["parry"] += 0.25
        elif player_last_action == "slash":
            weights["thrust"] += 0.25
        elif player_last_action == "parry":
            weights["slash"] += 0.25
        elif player_last_action == "shoot":
            weights["dodge"] += 0.30

    # Aggressive goes harder when opponent is low
    if personality == "aggressive" and player_state.hp < player_state.hp_max * 0.4:
        weights["thrust"] += 0.20
        weights["slash"] += 0.15

    # Defensive plays safe when low
    if personality == "defensive" and opponent_state.hp < opponent_state.hp_max * 0.4:
        weights["parry"] += 0.15
        weights["dodge"] += 0.20

    # Stunned: can only dodge
    if opponent_state.stun_turns > 0:
        return "dodge"

    actions = list(weights.keys())
    w = [max(0.0, weights[a]) for a in actions]
    total = sum(w)
    if total <= 0:
        return "thrust"
    return rng.choices(actions, weights=w, k=1)[0]


# ---------------------------------------------------------------------------
# State mutation helpers (applied by caller after round)
# ---------------------------------------------------------------------------

def apply_round_to_states(
    round_result: CombatRound,
    player_state: CombatantState,
    opponent_state: CombatantState,
) -> None:
    """Apply round results to mutable combatant states. Mutates in place."""
    # HP
    player_state.hp = max(0, player_state.hp - round_result.damage_to_player)
    opponent_state.hp = max(0, opponent_state.hp - round_result.damage_to_opponent)

    # Stamina
    player_state.stamina = max(0, min(
        player_state.stamina_max,
        player_state.stamina + round_result.player_stamina_delta,
    ))
    opponent_state.stamina = max(0, min(
        opponent_state.stamina_max,
        opponent_state.stamina + round_result.opponent_stamina_delta,
    ))

    # Track last action
    player_state.last_action = round_result.player_action
    opponent_state.last_action = round_result.opponent_action

    # Reload tick (before new reloads are set)
    if player_state.reload_turns > 0 and round_result.player_action != "shoot":
        player_state.reload_turns -= 1
    if player_state.mechanical_reload > 0 and round_result.player_action != "shoot":
        player_state.mechanical_reload -= 1
    if opponent_state.reload_turns > 0 and round_result.opponent_action != "shoot":
        opponent_state.reload_turns -= 1

    # Ammo consumption + new reload
    if round_result.player_action == "shoot":
        if player_state.ammo > 0:
            player_state.ammo -= 1
            weapon = RANGED_WEAPONS.get(player_state.firearm_id or "")
            if weapon:
                player_state.reload_turns = weapon.reload_turns
        elif player_state.mechanical_ammo > 0:
            player_state.mechanical_ammo -= 1
            weapon = RANGED_WEAPONS.get(player_state.mechanical_weapon_id or "")
            if weapon:
                player_state.mechanical_reload = weapon.reload_turns

    if round_result.player_action == "throw":
        player_state.throwing_weapons = max(0, player_state.throwing_weapons - 1)
        if player_state.throwing_weapon_ids:
            player_state.throwing_weapon_ids.pop(0)  # consume the first weapon

    if round_result.opponent_action == "shoot":
        opponent_state.ammo = max(0, opponent_state.ammo - 1)
    if round_result.opponent_action == "throw":
        opponent_state.throwing_weapons = max(0, opponent_state.throwing_weapons - 1)

    # Style cooldowns
    pa = round_result.player_action
    if player_state.active_style:
        style = FIGHTING_STYLES.get(player_state.active_style)
        if style and style.special_action and pa == style.special_action.id:
            player_state.style_cooldowns[pa] = style.special_action.cooldown
    # Tick all cooldowns down
    for key in list(player_state.style_cooldowns.keys()):
        if player_state.style_cooldowns[key] > 0:
            player_state.style_cooldowns[key] -= 1

    for key in list(opponent_state.style_cooldowns.keys()):
        if opponent_state.style_cooldowns[key] > 0:
            opponent_state.style_cooldowns[key] -= 1

    # Stun tick
    if player_state.stun_turns > 0:
        player_state.stun_turns -= 1
    if opponent_state.stun_turns > 0:
        opponent_state.stun_turns -= 1

    # Injuries
    if round_result.injury_inflicted:
        player_state.injury_ids.append(round_result.injury_inflicted)
    if round_result.opponent_injury:
        opponent_state.injury_ids.append(round_result.opponent_injury)


# ---------------------------------------------------------------------------
# Automated combat resolution (for balance harness)
# ---------------------------------------------------------------------------

def resolve_combat_automated(
    player_stances: list[str],
    opponent_id: str,
    opponent_name: str,
    opponent_personality: str,
    opponent_strength: int,
    rng: random.Random,
    player_crew: int = 5,
    player_style: str | None = None,
    player_injury_ids: list[str] | None = None,
    player_firearm: str | None = None,
    player_ammo: int = 0,
    player_throwing: int = 0,
) -> CombatResult:
    """Resolve a complete combat given pre-determined player actions.

    Used by the balance harness and as a legacy compatibility wrapper.
    """
    p_state = create_player_combatant(
        crew=player_crew,
        active_style=player_style,
        injury_ids=player_injury_ids,
        firearm_id=player_firearm,
        firearm_ammo=player_ammo,
        throwing_weapons=player_throwing,
    )
    o_state = create_opponent_combatant(
        strength=opponent_strength,
        personality=opponent_personality,
    )

    rounds: list[CombatRound] = []
    ammo_start = p_state.ammo
    throw_start = p_state.throwing_weapons

    for i, action in enumerate(player_stances):
        if p_state.hp <= 0 or o_state.hp <= 0:
            break

        result = resolve_combat_round(action, p_state, o_state, opponent_personality, rng)
        result.turn = i + 1
        rounds.append(result)
        apply_round_to_states(result, p_state, o_state)

    player_won = o_state.hp <= 0 and p_state.hp > 0
    draw = p_state.hp <= 0 and o_state.hp <= 0

    if player_won:
        silver_delta = 20 + opponent_strength * 5
        standing_delta = 5
    elif draw:
        silver_delta = 0
        standing_delta = 2
    else:
        silver_delta = -(15 + opponent_strength * 3)
        standing_delta = -2

    injuries = [r.injury_inflicted for r in rounds if r.injury_inflicted]
    opp_injuries = [r.opponent_injury for r in rounds if r.opponent_injury]

    return CombatResult(
        opponent_id=opponent_id,
        opponent_name=opponent_name,
        player_won=player_won,
        draw=draw,
        rounds=rounds,
        silver_delta=silver_delta,
        standing_delta=standing_delta,
        injuries_sustained=injuries,
        opponent_injuries=opp_injuries,
        ammo_spent=ammo_start - p_state.ammo,
        throwing_spent=throw_start - p_state.throwing_weapons,
    )
