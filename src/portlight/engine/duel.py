"""Sword duel engine — stance-based combat inspired by Uncharted Waters: New Horizons.

Three stances form a rock-paper-scissors triangle:
  Thrust beats Slash
  Slash beats Parry
  Parry beats Thrust

Opponent AI uses personality-driven stance selection:
  - Aggressive: favors Thrust (60/20/20)
  - Defensive: favors Parry (20/20/60)
  - Balanced: adapts to player patterns (40/30/30 then counters)
  - Wild: pure random (33/33/33)

Each round produces flavor text tied to the specific captain.
Duels have real consequences: silver, standing, cargo.

Contract:
  - resolve_round(player_stance, opponent, rng) -> DuelRound
  - pick_opponent_stance(opponent, player_history, rng) -> str
  - resolve_duel(player_stances, opponent, rng) -> DuelResult
"""

from __future__ import annotations

import random

from portlight.engine.models import DuelResult, DuelRound


# ---------------------------------------------------------------------------
# Stance triangle
# ---------------------------------------------------------------------------

STANCES = ("thrust", "slash", "parry")

# stance -> what it beats
_BEATS = {
    "thrust": "slash",
    "slash": "parry",
    "parry": "thrust",
}


def stance_outcome(player: str, opponent: str) -> str:
    """Return 'win', 'lose', or 'draw'."""
    if player == opponent:
        return "draw"
    if _BEATS.get(player) == opponent:
        return "win"
    return "lose"


# ---------------------------------------------------------------------------
# Opponent AI
# ---------------------------------------------------------------------------

_PERSONALITY_WEIGHTS: dict[str, tuple[float, float, float]] = {
    # (thrust, slash, parry)
    "aggressive": (0.60, 0.25, 0.15),
    "defensive":  (0.15, 0.25, 0.60),
    "balanced":   (0.35, 0.35, 0.30),
    "wild":       (0.33, 0.34, 0.33),
}


def pick_opponent_stance(
    personality: str,
    player_history: list[str],
    rng: random.Random,
) -> str:
    """Pick opponent stance based on personality and player pattern.

    Balanced personality adapts: if player repeats a stance 2+ times,
    opponent shifts to counter it.
    """
    base_weights = list(_PERSONALITY_WEIGHTS.get(personality, (0.33, 0.34, 0.33)))

    # Balanced AI adapts to player patterns
    if personality == "balanced" and len(player_history) >= 2:
        last_two = player_history[-2:]
        if last_two[0] == last_two[1]:
            # Player is repeating — counter it
            repeated = last_two[0]
            # Map repeated stance to counter index: parry beats thrust (idx 2),
            # thrust beats slash (idx 0), slash beats parry (idx 1)
            counter_idx = {"thrust": 2, "slash": 0, "parry": 1}
            if repeated in counter_idx:
                idx = counter_idx[repeated]
                base_weights[idx] += 0.30  # heavy bias toward counter

    return rng.choices(STANCES, weights=base_weights, k=1)[0]


# ---------------------------------------------------------------------------
# Round resolution
# ---------------------------------------------------------------------------

_STANCE_FLAVOR = {
    ("thrust", "win"):  "Your blade finds its mark — a clean thrust past their guard.",
    ("thrust", "lose"): "You lunge forward, but their parry turns your blade aside.",
    ("thrust", "draw"): "Both blades extend. Steel rings against steel. Neither gives ground.",
    ("slash", "win"):   "A wide arc catches them mid-parry. The cut connects.",
    ("slash", "lose"):  "Your slash meets empty air — they were already thrusting.",
    ("slash", "draw"):  "Blades cross in a shower of sparks. Matched power.",
    ("parry", "win"):   "You read the thrust perfectly. Their blade slides past as yours finds the opening.",
    ("parry", "lose"):  "You brace for a thrust that never comes — the slash catches your side.",
    ("parry", "draw"):  "Both hold their ground, blades locked. A test of strength.",
}


def resolve_round(
    player_stance: str,
    opponent_stance: str,
    rng: random.Random,
    crew_bonus: int = 0,
) -> DuelRound:
    """Resolve one round of combat. Returns DuelRound with damage and flavor."""
    outcome = stance_outcome(player_stance, opponent_stance)

    if outcome == "win":
        base_dmg = rng.randint(2, 3)
        dmg_to_opponent = base_dmg + min(crew_bonus // 5, 1)  # slight crew edge
        dmg_to_player = 0
    elif outcome == "lose":
        dmg_to_opponent = 0
        dmg_to_player = rng.randint(2, 3)
    else:
        dmg_to_opponent = 1
        dmg_to_player = 1

    flavor = _STANCE_FLAVOR.get((player_stance, outcome), "Blades clash.")

    return DuelRound(
        player_stance=player_stance,
        opponent_stance=opponent_stance,
        damage_to_opponent=dmg_to_opponent,
        damage_to_player=dmg_to_player,
        flavor=flavor,
    )


# ---------------------------------------------------------------------------
# Full duel resolution (automated for engine/balance testing)
# ---------------------------------------------------------------------------

def resolve_duel(
    player_stances: list[str],
    opponent_id: str,
    opponent_name: str,
    opponent_personality: str,
    opponent_strength: int,
    rng: random.Random,
    player_crew: int = 5,
) -> DuelResult:
    """Resolve a complete duel given a sequence of player stances.

    The opponent picks stances via AI. Duel ends when either HP reaches 0
    or player stances are exhausted.

    opponent_strength affects starting HP: base 10 + (strength - 5).
    Player always starts at 10 HP.
    """
    player_hp = 10
    opponent_hp = 10 + (opponent_strength - 5)  # strength 5 = 10HP, strength 9 = 14HP
    opponent_hp = max(6, opponent_hp)  # floor

    crew_bonus = max(0, player_crew - 5)
    rounds: list[DuelRound] = []
    player_history: list[str] = []

    for stance in player_stances:
        if player_hp <= 0 or opponent_hp <= 0:
            break

        opp_stance = pick_opponent_stance(opponent_personality, player_history, rng)
        round_result = resolve_round(stance, opp_stance, rng, crew_bonus)
        rounds.append(round_result)
        player_history.append(stance)

        player_hp -= round_result.damage_to_player
        opponent_hp -= round_result.damage_to_opponent

    player_won = opponent_hp <= 0 and player_hp > 0
    draw = player_hp <= 0 and opponent_hp <= 0

    # Consequences
    if player_won:
        silver_delta = 20 + opponent_strength * 5
        standing_delta = 5  # base, sparing adds more via underworld
    elif draw:
        silver_delta = 0
        standing_delta = 2  # mutual respect
    else:
        silver_delta = -(15 + opponent_strength * 3)
        standing_delta = -2

    return DuelResult(
        opponent_id=opponent_id,
        opponent_name=opponent_name,
        player_won=player_won,
        draw=draw,
        rounds=rounds,
        silver_delta=silver_delta,
        standing_delta=standing_delta,
    )
