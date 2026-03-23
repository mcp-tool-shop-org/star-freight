"""Injury catalog — combat wounds with mechanical consequences.

Injuries are sustained in personal combat when a single round deals 4+
damage. Attack type determines the injury pool. Injuries affect combat
capabilities and can block fighting styles that require injured body parts.

Severity tiers:
  minor    — heals in 10-15 days, small combat penalty
  major    — heals in 30-45 days, significant penalty, may need silver
  crippling — 60+ days or permanent, severe penalty, blocks styles
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InjuryDef:
    """Static injury definition — content data."""
    id: str
    name: str
    description: str
    severity: str                     # "minor", "major", "crippling"
    body_part: str                    # "hand", "arm", "leg", "eye", "torso"
    # Combat effects
    melee_damage_mod: int = 0         # added to melee damage dealt (negative = penalty)
    stamina_max_mod: int = 0          # added to max stamina
    hp_max_mod: int = 0               # added to max HP
    ranged_accuracy_mod: float = 0.0  # added to ranged accuracy
    can_dodge: bool = True            # False = DODGE action disabled
    can_use_firearms: bool = True     # False = SHOOT action disabled
    thrust_multiplier: float = 1.0    # multiplier on thrust damage (0.5 = halved)
    # Healing
    heal_days: int | None = None      # None = permanent
    heal_silver: int = 0              # silver cost for doctor treatment
    # Style blocking
    blocked_body_parts: tuple[str, ...] = ()  # styles requiring these parts are blocked
    # Trigger
    attack_types: tuple[str, ...] = ()  # which attack types can cause this ("slash", "thrust", "shoot")


# ---------------------------------------------------------------------------
# Injury catalog
# ---------------------------------------------------------------------------

INJURIES: dict[str, InjuryDef] = {i.id: i for i in [
    InjuryDef(
        id="cut_hand",
        name="Cut Hand",
        description="A deep cut across the palm. Grip weakened.",
        severity="minor",
        body_part="hand",
        melee_damage_mod=-1,
        heal_days=10,
        blocked_body_parts=("hand",),
        attack_types=("slash",),
    ),
    InjuryDef(
        id="bruised_ribs",
        name="Bruised Ribs",
        description="Cracked ribs from a heavy blow. Every breath hurts.",
        severity="minor",
        body_part="torso",
        stamina_max_mod=-1,
        heal_days=15,
        blocked_body_parts=("torso",),
        attack_types=("slash", "thrust"),
    ),
    InjuryDef(
        id="deep_slash",
        name="Deep Slash",
        description="A long cut down the sword arm. Two-handed techniques are impossible.",
        severity="major",
        body_part="arm",
        melee_damage_mod=-1,
        heal_days=30,
        blocked_body_parts=("arm",),
        attack_types=("slash",),
    ),
    InjuryDef(
        id="shattered_knee",
        name="Shattered Knee",
        description="The kneecap is cracked. Footwork is agony.",
        severity="major",
        body_part="leg",
        can_dodge=False,
        stamina_max_mod=-1,
        heal_days=45,
        blocked_body_parts=("leg",),
        attack_types=("slash", "thrust"),
    ),
    InjuryDef(
        id="blinded_eye",
        name="Blinded Eye",
        description="One eye gone. Depth perception ruined.",
        severity="crippling",
        body_part="eye",
        ranged_accuracy_mod=-0.15,
        heal_days=None,  # permanent
        blocked_body_parts=("eye",),
        attack_types=("slash", "thrust"),
    ),
    InjuryDef(
        id="broken_sword_arm",
        name="Broken Sword Arm",
        description="The sword arm is shattered. Fighting is barely possible.",
        severity="crippling",
        body_part="arm",
        melee_damage_mod=-2,
        thrust_multiplier=0.5,
        heal_days=60,
        heal_silver=200,
        blocked_body_parts=("arm",),
        attack_types=("slash", "thrust"),
    ),
    InjuryDef(
        id="gunshot_wound",
        name="Gunshot Wound",
        description="A musket ball lodged near the ribs. Movement is agony.",
        severity="major",
        body_part="torso",
        hp_max_mod=-2,
        stamina_max_mod=-2,
        heal_days=30,
        heal_silver=100,
        blocked_body_parts=("torso",),
        attack_types=("shoot",),
    ),
    InjuryDef(
        id="severed_fingers",
        name="Severed Fingers",
        description="Two fingers lost. Grip is weak. Trigger pull impossible.",
        severity="crippling",
        body_part="hand",
        can_use_firearms=False,
        melee_damage_mod=-1,
        heal_days=None,  # permanent
        blocked_body_parts=("hand",),
        attack_types=("slash",),
    ),
]}


def get_injury_pool(attack_type: str) -> list[InjuryDef]:
    """Get injuries that can be caused by a given attack type."""
    return [inj for inj in INJURIES.values() if attack_type in inj.attack_types]


def get_injured_body_parts(injury_ids: list[str]) -> set[str]:
    """Get the set of body parts affected by a list of active injuries."""
    parts: set[str] = set()
    for iid in injury_ids:
        inj = INJURIES.get(iid)
        if inj:
            parts.add(inj.body_part)
    return parts
