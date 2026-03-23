"""Training engine --- learning fighting styles from regional masters.

Pure functions --- callers decide what to mutate.
"""

from __future__ import annotations

from portlight.content.fighting_styles import FIGHTING_STYLES, STYLE_MASTERS


def can_learn_style(
    learned_styles: list[str],
    injured_body_parts: set[str],
    silver: int,
    current_port_id: str,
    style_id: str,
) -> str | None:
    """Check if captain can learn this style. Returns error message or None (success)."""
    style = FIGHTING_STYLES.get(style_id)
    if style is None:
        return f"Unknown fighting style: {style_id}"
    if style_id in learned_styles:
        return f"You already know {style.name}."
    if current_port_id not in style.training_port_ids:
        return f"No {style.name} master at this port."
    if silver < style.silver_cost:
        return f"Not enough silver. {style.name} training costs {style.silver_cost} silver."
    if len(learned_styles) < style.prerequisite_styles:
        return f"{style.name} requires knowledge of {style.prerequisite_styles} other style(s) first."
    # Check injuries don't block required body parts
    blocked = injured_body_parts & set(style.required_body_parts)
    if blocked:
        parts = ", ".join(sorted(blocked))
        return f"Your injuries ({parts}) prevent learning {style.name}."
    return None


def learn_style(
    learned_styles: list[str],
    silver: int,
    style_id: str,
) -> tuple[list[str], int]:
    """Apply learning. Returns (updated_styles_list, remaining_silver)."""
    style = FIGHTING_STYLES[style_id]
    new_styles = learned_styles + [style_id]
    return new_styles, silver - style.silver_cost


def get_available_training(port_id: str) -> list[str]:
    """Get fighting style IDs available for training at this port."""
    return [sid for sid, s in FIGHTING_STYLES.items() if port_id in s.training_port_ids]


def get_masters_at_port(port_id: str) -> list:
    """Get StyleMaster objects at this port."""
    return [m for m in STYLE_MASTERS.values() if m.port_id == port_id]


def check_style_usable(style_id: str, injured_body_parts: set[str]) -> bool:
    """Check if a style can be used given current injuries."""
    style = FIGHTING_STYLES.get(style_id)
    if style is None:
        return False
    blocked = injured_body_parts & set(style.required_body_parts)
    return len(blocked) == 0
