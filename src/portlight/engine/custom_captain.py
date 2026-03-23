"""Custom captain builder — the 9th character option.

Players distribute 10 skill points across 4 categories, choose a home port,
a cultural background, a faction alignment, and an NPC mentor. The builder
generates a CaptainTemplate with modifiers derived from those choices.

Design principle: every choice should be a TRADE-OFF, not an optimization
puzzle. Points in Trade mean you can't have points in Sailing. A Shadow Ports
home means legitimacy is harder. There's no "best build" — only the build
that matches the story you want to tell.

Point allocation (10 points to distribute):
  Trade      — buy/sell/luxury/port fees
  Sailing    — speed/provisions/storm/cargo
  Shadow     — inspection evasion/underworld standing
  Reputation — starting trust/regional standing
"""

from __future__ import annotations

from dataclasses import dataclass

from portlight.engine.captain_identity import (
    CaptainTemplate,
    CaptainType,
    InspectionProfile,
    PricingModifiers,
    ReputationSeed,
    VoyageModifiers,
)


# ---------------------------------------------------------------------------
# Skill point effects per point invested
# ---------------------------------------------------------------------------

# Each point in a category adjusts modifiers by these amounts:
TRADE_PER_POINT = {
    "buy_price_mult": -0.01,         # 1% cheaper buys per point
    "sell_price_mult": 0.01,         # 1% better sells per point
    "luxury_sell_bonus": 0.03,       # 3% luxury bonus per point
    "port_fee_mult": -0.03,          # 3% cheaper port fees per point
}

SAILING_PER_POINT = {
    "provision_burn": -0.03,         # 3% less provision burn per point
    "speed_bonus": 0.3,             # +0.3 speed per point
    "storm_resist_bonus": 0.015,    # 1.5% storm resistance per point
    "cargo_damage_mult": -0.03,     # 3% less cargo damage per point
}

SHADOW_PER_POINT = {
    "inspection_chance_mult": -0.06, # 6% fewer inspections per point
    "underworld_per_faction": 5,     # +5 underworld standing per point (in chosen faction)
}

REPUTATION_PER_POINT = {
    "commercial_trust": 2,           # +2 trust per point
    "regional_standing": 2,          # +2 standing in chosen region per point
}

# Starting silver by home region
REGION_STARTING_SILVER = {
    "Mediterranean": 500,
    "North Atlantic": 450,
    "West Africa": 450,
    "East Indies": 400,
    "South Seas": 350,
}

TOTAL_SKILL_POINTS = 10
MAX_POINTS_PER_CATEGORY = 7  # can't dump everything in one bucket


@dataclass
class CustomCaptainSpec:
    """Player's custom captain choices — input to the builder."""
    name: str = "Captain"
    title: str = "Freelance Captain"
    home_port_id: str = "porto_novo"
    home_region: str = "Mediterranean"
    # Point allocation
    trade_points: int = 0
    sailing_points: int = 0
    shadow_points: int = 0
    reputation_points: int = 0
    # Faction/bloc alignment
    bloc_alignment: str = ""          # trade bloc id or empty
    faction_alignment: str = ""       # pirate faction id or empty
    # NPC mentor
    mentor_npc_id: str = ""
    # Player-written backstory
    backstory: str = ""


def validate_spec(spec: CustomCaptainSpec) -> list[str]:
    """Validate a custom captain spec. Returns list of error messages (empty = valid)."""
    errors: list[str] = []

    total = spec.trade_points + spec.sailing_points + spec.shadow_points + spec.reputation_points

    if total != TOTAL_SKILL_POINTS:
        errors.append(f"Must allocate exactly {TOTAL_SKILL_POINTS} points (allocated {total})")

    for cat_name, pts in [
        ("Trade", spec.trade_points),
        ("Sailing", spec.sailing_points),
        ("Shadow", spec.shadow_points),
        ("Reputation", spec.reputation_points),
    ]:
        if pts < 0:
            errors.append(f"{cat_name} points cannot be negative")
        if pts > MAX_POINTS_PER_CATEGORY:
            errors.append(f"{cat_name} points cannot exceed {MAX_POINTS_PER_CATEGORY} (got {pts})")

    from portlight.content.ports import PORTS
    if spec.home_port_id not in PORTS:
        errors.append(f"Unknown home port: '{spec.home_port_id}'")
    else:
        port = PORTS[spec.home_port_id]
        if port.region != spec.home_region:
            errors.append(f"Port '{spec.home_port_id}' is in {port.region}, not {spec.home_region}")

    valid_regions = {"Mediterranean", "North Atlantic", "West Africa", "East Indies", "South Seas"}
    if spec.home_region not in valid_regions:
        errors.append(f"Unknown region: '{spec.home_region}'")

    if spec.bloc_alignment:
        from portlight.content.port_politics import TRADE_BLOCS
        if spec.bloc_alignment not in TRADE_BLOCS:
            errors.append(f"Unknown trade bloc: '{spec.bloc_alignment}'")

    if spec.faction_alignment:
        from portlight.content.factions import FACTIONS
        if spec.faction_alignment not in FACTIONS:
            errors.append(f"Unknown pirate faction: '{spec.faction_alignment}'")

    if spec.mentor_npc_id:
        from portlight.content.port_institutions import ALL_NPCS
        if spec.mentor_npc_id not in ALL_NPCS:
            errors.append(f"Unknown mentor NPC: '{spec.mentor_npc_id}'")
        else:
            mentor = ALL_NPCS[spec.mentor_npc_id]
            if mentor.port_id != spec.home_port_id:
                errors.append(
                    f"Mentor '{spec.mentor_npc_id}' is at {mentor.port_id}, "
                    f"not at your home port {spec.home_port_id}"
                )

    return errors


def build_custom_template(spec: CustomCaptainSpec) -> CaptainTemplate:
    """Build a CaptainTemplate from a validated CustomCaptainSpec.

    Call validate_spec() first — this function assumes the spec is valid.
    """
    # --- Pricing from Trade points ---
    pricing = PricingModifiers(
        buy_price_mult=round(1.0 + TRADE_PER_POINT["buy_price_mult"] * spec.trade_points, 3),
        sell_price_mult=round(1.0 + TRADE_PER_POINT["sell_price_mult"] * spec.trade_points, 3),
        luxury_sell_bonus=round(TRADE_PER_POINT["luxury_sell_bonus"] * spec.trade_points, 3),
        port_fee_mult=round(max(0.5, 1.0 + TRADE_PER_POINT["port_fee_mult"] * spec.trade_points), 3),
    )

    # --- Voyage from Sailing points ---
    voyage = VoyageModifiers(
        provision_burn=round(max(0.5, 1.0 + SAILING_PER_POINT["provision_burn"] * spec.sailing_points), 3),
        speed_bonus=round(SAILING_PER_POINT["speed_bonus"] * spec.sailing_points, 2),
        storm_resist_bonus=round(SAILING_PER_POINT["storm_resist_bonus"] * spec.sailing_points, 3),
        cargo_damage_mult=round(max(0.5, 1.0 + SAILING_PER_POINT["cargo_damage_mult"] * spec.sailing_points), 3),
    )

    # --- Inspection from Shadow points ---
    inspection = InspectionProfile(
        inspection_chance_mult=round(max(0.3, 1.0 + SHADOW_PER_POINT["inspection_chance_mult"] * spec.shadow_points), 3),
        seizure_risk=0.0,  # custom captains don't start with seizure risk
        fine_mult=round(max(0.4, 1.0 - 0.06 * spec.shadow_points), 3),
    )

    # --- Reputation from Reputation points ---
    trust = REPUTATION_PER_POINT["commercial_trust"] * spec.reputation_points
    standing = REPUTATION_PER_POINT["regional_standing"] * spec.reputation_points

    # Underworld standing from Shadow points + faction alignment
    underworld: dict[str, int] | None = None
    if spec.shadow_points > 0 and spec.faction_alignment:
        uw_standing = SHADOW_PER_POINT["underworld_per_faction"] * spec.shadow_points
        underworld = {spec.faction_alignment: uw_standing}

    # Region standing goes to chosen home region
    region_standing = {
        "mediterranean": standing if spec.home_region == "Mediterranean" else 0,
        "north_atlantic": standing if spec.home_region == "North Atlantic" else 0,
        "west_africa": standing if spec.home_region == "West Africa" else 0,
        "east_indies": standing if spec.home_region == "East Indies" else 0,
        "south_seas": standing if spec.home_region == "South Seas" else 0,
    }

    reputation_seed = ReputationSeed(
        commercial_trust=trust,
        customs_heat=0,
        mediterranean=region_standing["mediterranean"],
        north_atlantic=region_standing["north_atlantic"],
        west_africa=region_standing["west_africa"],
        east_indies=region_standing["east_indies"],
        south_seas=region_standing["south_seas"],
        underworld=underworld,
    )

    # Starting silver from region
    starting_silver = REGION_STARTING_SILVER.get(spec.home_region, 400)

    # Build strengths/weaknesses from point allocation
    strengths: list[str] = []
    weaknesses: list[str] = []

    if spec.trade_points >= 4:
        strengths.append(f"Strong trader ({spec.trade_points} points in Trade)")
    elif spec.trade_points == 0:
        weaknesses.append("No trade advantages")

    if spec.sailing_points >= 4:
        strengths.append(f"Expert sailor ({spec.sailing_points} points in Sailing)")
    elif spec.sailing_points == 0:
        weaknesses.append("No sailing advantages")

    if spec.shadow_points >= 4:
        strengths.append(f"Shadow operative ({spec.shadow_points} points in Shadow)")
    elif spec.shadow_points == 0:
        weaknesses.append("No underworld connections")

    if spec.reputation_points >= 4:
        strengths.append(f"Well-connected ({spec.reputation_points} points in Reputation)")
    elif spec.reputation_points == 0:
        weaknesses.append("No starting reputation")

    if not strengths:
        strengths.append("Balanced — jack of all trades")
    if not weaknesses:
        weaknesses.append("No clear specialty — master of none")

    # Backstory
    backstory = spec.backstory or (
        f"A captain from {spec.home_region} who chose their own path. "
        f"The world doesn't know your name yet. That's about to change."
    )

    # Faction alignment dict
    faction_dict: dict[str, int] = {}
    if spec.faction_alignment and underworld:
        faction_dict = dict(underworld)

    return CaptainTemplate(
        id=CaptainType.CUSTOM,
        name=spec.name,
        title=spec.title,
        description=backstory,
        home_region=spec.home_region,
        home_port_id=spec.home_port_id,
        starting_silver=starting_silver,
        starting_ship_id="coastal_sloop",
        starting_provisions=30,
        pricing=pricing,
        voyage=voyage,
        inspection=inspection,
        reputation_seed=reputation_seed,
        strengths=strengths,
        weaknesses=weaknesses,
        backstory=backstory,
        mentor_npc_id=spec.mentor_npc_id,
        bloc_alignment=spec.bloc_alignment,
        faction_alignment=faction_dict,
    )
