"""Skill engine — learning, leveling, and effect application.

Pure functions — callers decide what to mutate.
"""

from __future__ import annotations

from portlight.content.skills import (
    SKILLS,
    get_blacksmith_effects,
    get_trainers_at_port,
)


# ---------------------------------------------------------------------------
# Learning
# ---------------------------------------------------------------------------

def can_learn_skill(
    skills: dict[str, int],
    silver: int,
    current_port_id: str,
    skill_id: str,
) -> str | None:
    """Check if captain can learn/advance this skill. Returns error or None."""
    skill = SKILLS.get(skill_id)
    if skill is None:
        return f"Unknown skill: {skill_id}"

    current_level = skills.get(skill_id, 0)
    if current_level >= skill.max_level:
        return f"Already at maximum {skill.name} level ({skill.levels[current_level - 1].name})."

    next_level = skill.levels[current_level]  # 0-indexed: level 0->levels[0], etc.

    # Check trainer at port
    trainers = get_trainers_at_port(current_port_id, skill_id)
    if not trainers:
        return f"No {skill.name} trainer at this port."

    # Check trainer can teach this level
    max_teach = max(t.max_teach_level for t in trainers)
    if current_level + 1 > max_teach:
        best_trainer = max(trainers, key=lambda t: t.max_teach_level)
        return f"{best_trainer.name} can only teach up to level {max_teach}. Find a more skilled trainer."

    if silver < next_level.silver_cost:
        return f"{next_level.name} training costs {next_level.silver_cost} silver. You have {silver}."

    return None


def learn_skill(
    skills: dict[str, int],
    silver: int,
    skill_id: str,
) -> tuple[dict[str, int], int, int]:
    """Apply skill learning. Returns (updated_skills, remaining_silver, training_days)."""
    skill = SKILLS[skill_id]
    current_level = skills.get(skill_id, 0)
    next_level = skill.levels[current_level]

    new_skills = dict(skills)
    new_skills[skill_id] = current_level + 1
    return new_skills, silver - next_level.silver_cost, next_level.training_days


def get_skill_level(skills: dict[str, int], skill_id: str) -> int:
    """Get current skill level (0 = untrained)."""
    return skills.get(skill_id, 0)


def get_skill_display(skills: dict[str, int], skill_id: str) -> str:
    """Get display string for a skill level."""
    skill = SKILLS.get(skill_id)
    if skill is None:
        return "Unknown"
    level = skills.get(skill_id, 0)
    if level == 0:
        return "Untrained"
    return skill.levels[level - 1].name


# ---------------------------------------------------------------------------
# Blacksmith-specific effect application
# ---------------------------------------------------------------------------

def apply_maintenance_discount(
    base_cost: int,
    blacksmith_level: int,
) -> int:
    """Apply blacksmith skill discount to maintenance cost."""
    effects = get_blacksmith_effects(blacksmith_level)
    discount = effects["maintenance_discount"]
    return max(1, int(base_cost * (1 - discount)))


def apply_upgrade_discount(
    base_cost: int,
    blacksmith_level: int,
) -> int:
    """Apply blacksmith skill discount to smith upgrade cost."""
    effects = get_blacksmith_effects(blacksmith_level)
    discount = effects["upgrade_discount"]
    return max(1, int(base_cost * (1 - discount)))


def get_degrade_threshold_bonus(blacksmith_level: int) -> int:
    """Get extra uses before degradation from blacksmith skill.

    Returns additional uses to add to the base threshold.
    E.g. base 10, level 3 (60% slow) -> +6 extra uses -> effective threshold 16.
    """
    effects = get_blacksmith_effects(blacksmith_level)
    slow = effects["degrade_slow"]
    # Convert percentage slow to extra uses (based on melee threshold of 10)
    return int(10 * slow)


def can_field_repair(blacksmith_level: int) -> bool:
    """Check if captain can repair weapons at sea (level 2+)."""
    effects = get_blacksmith_effects(blacksmith_level)
    return effects["field_repair"]


def get_field_repair_max_quality(blacksmith_level: int) -> str:
    """Get maximum quality achievable through field repair."""
    effects = get_blacksmith_effects(blacksmith_level)
    return effects["field_max_quality"]


def field_repair_weapon(
    weapon_id: str,
    weapon_quality: dict[str, str],
    weapon_usage: dict[str, int],
    blacksmith_level: int,
) -> tuple[bool, str | None]:
    """Attempt field repair at sea. Returns (success, error_or_None).

    Field repair resets usage counter and can restore worn->standard (level 2+).
    """
    if not can_field_repair(blacksmith_level):
        return False, "Need Journeyman blacksmith skill to repair at sea."

    max_quality = get_field_repair_max_quality(blacksmith_level)
    current = weapon_quality.get(weapon_id, "standard")

    # Reset usage
    weapon_usage[weapon_id] = 0

    # Restore quality if below field max
    from portlight.engine.weapon_quality import _QUALITY_INDEX
    current_idx = _QUALITY_INDEX.get(current, 2)
    max_idx = _QUALITY_INDEX.get(max_quality, 2)

    if current_idx < max_idx:
        weapon_quality[weapon_id] = max_quality
        return True, None

    return True, None
