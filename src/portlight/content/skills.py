"""Skill catalog — trainable captain abilities.

Skills are learned from NPCs at specific ports and improve through practice.
Each skill has 3 levels (apprentice, journeyman, master) with escalating
costs and increasingly powerful effects.

Skills follow the same pattern as fighting styles: content defines the data,
engine functions check prerequisites and apply effects.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillLevel:
    """One level of a skill with its effects and costs."""
    level: int              # 1, 2, 3
    name: str               # "Apprentice", "Journeyman", "Master"
    silver_cost: int
    training_days: int
    description: str


@dataclass(frozen=True)
class SkillDef:
    """Static skill definition."""
    id: str
    name: str
    description: str
    training_port_feature: str    # PortFeature required (e.g. "shipyard")
    levels: tuple[SkillLevel, ...]
    max_level: int = 3


@dataclass(frozen=True)
class SkillTrainer:
    """NPC who teaches a skill at a port."""
    id: str
    name: str
    skill_id: str
    port_id: str
    max_teach_level: int      # can teach up to this level
    description: str
    dialog: str


# ---------------------------------------------------------------------------
# Skill definitions
# ---------------------------------------------------------------------------

SKILLS: dict[str, SkillDef] = {s.id: s for s in [
    SkillDef(
        id="blacksmith",
        name="Blacksmithing",
        description="The art of metalwork — maintaining, repairing, and improving weapons and armor.",
        training_port_feature="shipyard",
        levels=(
            SkillLevel(
                level=1, name="Apprentice",
                silver_cost=50, training_days=3,
                description="Basic maintenance. Reduce maintenance costs by 25%. Degradation slowed by 20%.",
            ),
            SkillLevel(
                level=2, name="Journeyman",
                silver_cost=150, training_days=5,
                description="Field repairs at sea. Reduce maintenance costs by 50%. Degradation slowed by 40%. Can restore worn weapons to standard at sea.",
            ),
            SkillLevel(
                level=3, name="Master",
                silver_cost=400, training_days=8,
                description="Master craftsman. Maintenance costs halved. Degradation slowed by 60%. Smith upgrades cost 25% less. Field repairs restore to standard.",
            ),
        ),
    ),
]}


# ---------------------------------------------------------------------------
# Skill effect constants (blacksmith)
# ---------------------------------------------------------------------------

BLACKSMITH_EFFECTS = {
    0: {"maintenance_discount": 0.0, "degrade_slow": 0.0, "upgrade_discount": 0.0, "field_repair": False, "field_max_quality": "rusted"},
    1: {"maintenance_discount": 0.25, "degrade_slow": 0.20, "upgrade_discount": 0.0, "field_repair": False, "field_max_quality": "rusted"},
    2: {"maintenance_discount": 0.50, "degrade_slow": 0.40, "upgrade_discount": 0.0, "field_repair": True, "field_max_quality": "standard"},
    3: {"maintenance_discount": 0.50, "degrade_slow": 0.60, "upgrade_discount": 0.25, "field_repair": True, "field_max_quality": "standard"},
}


def get_blacksmith_effects(level: int) -> dict:
    """Get blacksmith skill effects for a given level."""
    return BLACKSMITH_EFFECTS.get(min(level, 3), BLACKSMITH_EFFECTS[0])


# ---------------------------------------------------------------------------
# Trainers
# ---------------------------------------------------------------------------

SKILL_TRAINERS: dict[str, SkillTrainer] = {t.id: t for t in [
    SkillTrainer(
        id="forge_master_erik",
        name="Forge Master Erik",
        skill_id="blacksmith",
        port_id="ironhaven",
        max_teach_level=3,
        description="The best smith in the North Atlantic. His blades hold an edge for years.",
        dialog="\"Steel remembers every hammer blow. I'll teach your hands to speak its language.\"",
    ),
    SkillTrainer(
        id="old_vasquez",
        name="Old Vasquez",
        skill_id="blacksmith",
        port_id="porto_novo",
        max_teach_level=2,
        description="A retired armorer who sharpens blades in the harbor market. Fast and cheap, but not a master.",
        dialog="\"I can teach you to keep a blade sharp and a pistol clean. That's worth more than fancy swordplay.\"",
    ),
    SkillTrainer(
        id="silva_bay_smiths",
        name="The Silva Bay Smithy",
        skill_id="blacksmith",
        port_id="silva_bay",
        max_teach_level=3,
        description="A family of shipwrights who also forge the finest blades in the Mediterranean.",
        dialog="\"We build ships and swords from the same iron. Both need to survive the sea.\"",
    ),
    SkillTrainer(
        id="monsoon_tinker",
        name="Rajan the Tinker",
        skill_id="blacksmith",
        port_id="monsoon_reach",
        max_teach_level=2,
        description="An East Indies metalworker who repairs anything from kris daggers to Portuguese cannons.",
        dialog="\"Every weapon that passes through this port, I have fixed. Bring me yours.\"",
    ),
    SkillTrainer(
        id="typhoon_smith",
        name="Kai the Shaper",
        skill_id="blacksmith",
        port_id="typhoon_anchorage",
        max_teach_level=1,
        description="A young smith who learned from sailors. Basic work, but honest.",
        dialog="\"I'm no master, but I can keep your steel from rusting in the salt air. That's something.\"",
    ),
]}


def get_trainers_at_port(port_id: str, skill_id: str | None = None) -> list[SkillTrainer]:
    """Get skill trainers at a port, optionally filtered by skill."""
    trainers = [t for t in SKILL_TRAINERS.values() if t.port_id == port_id]
    if skill_id:
        trainers = [t for t in trainers if t.skill_id == skill_id]
    return trainers
