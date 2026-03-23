"""Underworld engine — pirate faction standing, access checks, and hostility.

Parallel to the legitimate reputation system, the underworld has its own
standing mechanics. High underworld standing opens smuggling contracts,
pirate trade deals, and safer passage through faction territory. Low standing
makes you prey. Betraying factions raises underworld_heat (snitch factor).

Pure functions — callers decide what to mutate.
"""

from __future__ import annotations

from portlight.content.factions import (
    FACTION_RELATIONSHIPS,
    FACTIONS,
    get_enemies,
    get_faction_for_region,
)


# ---------------------------------------------------------------------------
# Standing thresholds
# ---------------------------------------------------------------------------

THRESHOLD_PREY = 10        # below this: faction attacks on sight
THRESHOLD_NEUTRAL = 10     # 10-24: ignored
THRESHOLD_TRADE = 25       # 25-49: trade partner
THRESHOLD_TRUSTED = 50     # 50+: trusted ally


def get_standing(underworld_standing: dict[str, int], faction_id: str) -> int:
    """Get current standing with a faction (default 0)."""
    return underworld_standing.get(faction_id, 0)


def get_faction_hostility(
    underworld_standing: dict[str, int],
    faction_id: str,
    captain_type: str,
) -> str:
    """Determine faction's attitude toward the player.

    Returns: "attack", "neutral", "trade", or "allied"
    """
    standing = get_standing(underworld_standing, faction_id)
    faction = FACTIONS.get(faction_id)

    # Smuggler bonus: factions with friendly smuggler_attitude give +5 effective standing
    if faction and captain_type == "smuggler":
        if faction.smuggler_attitude in ("friendly", "cooperative", "respectful"):
            standing += 5

    if standing >= THRESHOLD_TRUSTED:
        return "allied"
    elif standing >= THRESHOLD_TRADE:
        return "trade"
    elif standing >= THRESHOLD_NEUTRAL:
        return "neutral"
    else:
        return "attack"


def record_contraband_trade(
    underworld_standing: dict[str, int],
    faction_id: str,
    good_id: str,
    qty: int,
) -> int:
    """Record a contraband trade. Returns standing delta."""
    faction = FACTIONS.get(faction_id)
    if faction is None:
        return 0

    # Trading a faction's specialty contraband gives more standing
    delta = 1
    if good_id == faction.contraband_specialty:
        delta = 3
    elif good_id in faction.preferred_goods:
        delta = 2

    # Volume bonus
    if qty >= 5:
        delta += 1

    current = underworld_standing.get(faction_id, 0)
    underworld_standing[faction_id] = min(100, current + delta)
    return delta


def record_pirate_trade(
    underworld_standing: dict[str, int],
    faction_id: str,
) -> int:
    """Record a successful at-sea trade with a pirate captain."""
    delta = 2
    current = underworld_standing.get(faction_id, 0)
    underworld_standing[faction_id] = min(100, current + delta)
    return delta


def record_duel_outcome(
    underworld_standing: dict[str, int],
    faction_id: str,
    player_won: bool,
    spared: bool = False,
) -> int:
    """Record a duel outcome. Winning earns respect. Sparing earns more."""
    if player_won:
        delta = 5 if spared else 2
    else:
        delta = -2
    current = underworld_standing.get(faction_id, 0)
    underworld_standing[faction_id] = max(0, min(100, current + delta))
    return delta


def record_betrayal(
    underworld_standing: dict[str, int],
    underworld_heat: int,
    faction_id: str,
) -> tuple[int, int]:
    """Record betrayal (informing on a faction). Returns (standing_delta, heat_delta)."""
    standing_delta = -15
    heat_delta = 5
    current = underworld_standing.get(faction_id, 0)
    underworld_standing[faction_id] = max(0, current + standing_delta)
    return standing_delta, heat_delta


def get_contraband_price_bonus(
    underworld_standing: dict[str, int],
    faction_id: str,
) -> float:
    """Get sell price bonus for contraband at a faction's port."""
    standing = get_standing(underworld_standing, faction_id)
    if standing >= THRESHOLD_TRUSTED:
        return 0.30  # 30% bonus
    elif standing >= THRESHOLD_TRADE:
        return 0.15  # 15% bonus
    return 0.0


def get_dominant_faction_for_region(region: str) -> str | None:
    """Get the faction_id of the dominant faction in a region."""
    factions = get_faction_for_region(region)
    if not factions:
        return None
    return factions[0].id


def apply_standing_spillover(
    underworld_standing: dict[str, int],
    source_faction_id: str,
    delta: int,
) -> dict[str, int]:
    """Apply spillover effects to related factions when standing changes.

    When you gain standing with a faction, their enemies lose respect for you
    and their allies gain respect. Returns dict of {faction_id: spillover_delta}.

    This creates the core political tension: you can't be friends with everyone.
    """
    spillovers: dict[str, int] = {}
    for rel in FACTION_RELATIONSHIPS:
        other_id = None
        if rel.faction_a == source_faction_id:
            other_id = rel.faction_b
        elif rel.faction_b == source_faction_id:
            other_id = rel.faction_a
        else:
            continue

        # spillover: positive delta with source -> negative effect on enemies
        raw_spillover = int(delta * rel.spillover)
        if raw_spillover == 0 and rel.spillover != 0.0 and abs(delta) >= 3:
            # Ensure meaningful deltas produce at least ±1 spillover
            raw_spillover = 1 if rel.spillover > 0 else -1

        if raw_spillover != 0:
            current = underworld_standing.get(other_id, 0)
            new_val = max(0, min(100, current + raw_spillover))
            underworld_standing[other_id] = new_val
            spillovers[other_id] = raw_spillover

    return spillovers


def check_vendetta(
    underworld_standing: dict[str, int],
    source_faction_id: str,
) -> list[str]:
    """Check if gaining standing with source_faction triggers vendettas.

    Returns list of faction_ids that now hold a vendetta against the player.
    A vendetta triggers when:
      - You have standing 25+ with a faction
      - That faction has a hostile enemy
      - Your standing with the enemy is below 10 (already prey status)
    """
    source_standing = get_standing(underworld_standing, source_faction_id)
    if source_standing < THRESHOLD_TRADE:
        return []  # not close enough to trigger political consequences

    vendetta_factions = []
    enemies = get_enemies(source_faction_id)
    for enemy_id in enemies:
        enemy_standing = get_standing(underworld_standing, enemy_id)
        if enemy_standing < THRESHOLD_PREY:
            vendetta_factions.append(enemy_id)

    return vendetta_factions


def get_political_summary(underworld_standing: dict[str, int]) -> list[str]:
    """Generate a human-readable summary of the player's political position.

    Returns list of situation descriptions for display.
    """
    lines = []
    for fid, faction in FACTIONS.items():
        standing = get_standing(underworld_standing, fid)
        if standing >= THRESHOLD_TRUSTED:
            lines.append(f"{faction.name} considers you a trusted ally.")
        elif standing >= THRESHOLD_TRADE:
            lines.append(f"{faction.name} will trade with you.")
        elif standing >= THRESHOLD_NEUTRAL:
            lines.append(f"{faction.name} ignores you — for now.")
        elif standing > 0:
            lines.append(f"{faction.name} views you as prey.")
        # Don't mention factions with 0 standing (not yet encountered)

    # Check for active vendettas
    for fid in FACTIONS:
        vendettas = check_vendetta(underworld_standing, fid)
        for enemy_id in vendettas:
            enemy = FACTIONS.get(enemy_id)
            source = FACTIONS.get(fid)
            if enemy and source:
                lines.append(
                    f"VENDETTA: {enemy.name} hunts you for your alliance with {source.name}."
                )

    return lines


def tick_underworld(
    underworld_standing: dict[str, int],
    underworld_heat: int,
    days: int = 1,
) -> int:
    """Daily tick: underworld heat decays slowly. Returns new heat value."""
    for _ in range(days):
        if underworld_heat > 0:
            underworld_heat = max(0, underworld_heat - 1)
    return underworld_heat
