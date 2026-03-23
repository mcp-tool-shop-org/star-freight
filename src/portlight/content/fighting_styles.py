"""Fighting styles --- regional martial traditions of the 16th century.

Five styles, one per trade region. Each grants passive combat bonuses
and a unique special action. Learned from masters at specific ports.

Design: styles are content data, not engine logic. The combat engine
reads these definitions to apply effects.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StyleAction:
    """A special combat action unlocked by learning a fighting style."""
    id: str
    name: str
    action_type: str          # "attack", "counter", "utility"
    stamina_cost: int
    beats: tuple[str, ...]    # actions this beats (use tuple for frozen)
    loses_to: tuple[str, ...]
    damage_bonus: int
    flavor: str
    cooldown: int             # turns before reuse (0 = every turn)


@dataclass(frozen=True)
class FightingStyle:
    """A regional martial tradition that modifies personal combat."""
    id: str
    name: str
    region: str
    description: str
    historical_note: str
    # Passive combat bonuses (applied every round)
    passive_thrust_bonus: int = 0
    passive_slash_bonus: int = 0
    passive_parry_bonus: int = 0        # extra stamina restored on parry
    passive_hp_bonus: int = 0
    passive_dodge_counter: int = 0      # damage dealt when dodging
    passive_ranged_accuracy: float = 0.0
    passive_injury_bonus: float = 0.0   # added to injury infliction chance
    # Special action
    special_action: StyleAction | None = None
    # Learning requirements
    training_port_ids: tuple[str, ...] = ()
    silver_cost: int = 0
    training_days: int = 0
    prerequisite_styles: int = 0        # how many styles must be known first
    required_body_parts: tuple[str, ...] = ()  # injuries to these block style


@dataclass(frozen=True)
class StyleMaster:
    """An NPC who teaches a fighting style at a specific port."""
    id: str
    name: str
    style_id: str
    port_id: str
    description: str
    dialog: str


# ---------------------------------------------------------------------------
# Style definitions
# ---------------------------------------------------------------------------

FIGHTING_STYLES: dict[str, FightingStyle] = {
    "la_destreza": FightingStyle(
        id="la_destreza",
        name="La Destreza",
        region="Mediterranean",
        description=(
            "The Spanish science of defense. Every movement calculated, "
            "every thrust placed with geometric precision."
        ),
        historical_note=(
            "Systematized by Jeronimo Sanchez de Carranza in 1569. "
            "The first European martial art treated as an academic discipline."
        ),
        passive_thrust_bonus=1,
        passive_parry_bonus=1,
        special_action=StyleAction(
            id="estocada",
            name="Estocada",
            action_type="attack",
            stamina_cost=3,
            beats=("parry", "slash"),
            loses_to=("dodge",),
            damage_bonus=2,
            flavor=(
                "A geometric thrust \u2014 the blade finds the only open line."
            ),
            cooldown=2,
        ),
        training_port_ids=("porto_novo", "al_manar"),
        silver_cost=80,
        training_days=5,
        prerequisite_styles=0,
        required_body_parts=("hand", "arm"),
    ),
    "highland_broadsword": FightingStyle(
        id="highland_broadsword",
        name="Highland Broadsword",
        region="North Atlantic",
        description=(
            "The broadsword tradition of the Scottish Highlands and Norse "
            "raiders. No finesse, no subtlety \u2014 overwhelming force."
        ),
        historical_note=(
            "Highland sword-and-targe techniques documented across Scotland "
            "and Scandinavia. The two-handed claymore was already legendary "
            "by the 1500s."
        ),
        passive_slash_bonus=1,
        passive_hp_bonus=2,
        special_action=StyleAction(
            id="cleave",
            name="Cleave",
            action_type="attack",
            stamina_cost=2,
            beats=("parry",),
            loses_to=("thrust", "dodge"),
            damage_bonus=4,
            flavor=(
                "A devastating overhead arc that shatters guards and bones "
                "alike."
            ),
            cooldown=1,
        ),
        training_port_ids=("ironhaven", "thornport"),
        silver_cost=100,
        training_days=7,
        prerequisite_styles=0,
        required_body_parts=("arm",),
    ),
    "dambe": FightingStyle(
        id="dambe",
        name="Dambe",
        region="West Africa",
        description=(
            "The fighting art of the Hausa people. The lead fist is the "
            "spear, the rear hand is the shield, and the legs finish every "
            "fight."
        ),
        historical_note=(
            "Practiced across West Africa since at least the 15th century. "
            "Dambe bouts were a central part of harvest festivals and market "
            "days."
        ),
        passive_dodge_counter=1,
        special_action=StyleAction(
            id="leg_sweep",
            name="Leg Sweep",
            action_type="counter",
            stamina_cost=2,
            beats=("thrust",),
            loses_to=("slash", "dodge"),
            damage_bonus=1,
            flavor=(
                "A low spinning sweep \u2014 the opponent's legs are taken "
                "from under them. They crash to the deck."
            ),
            cooldown=3,
        ),
        training_port_ids=("sun_harbor", "pearl_shallows"),
        silver_cost=60,
        training_days=6,
        prerequisite_styles=0,
        required_body_parts=("leg",),
    ),
    "silat": FightingStyle(
        id="silat",
        name="Silat",
        region="East Indies",
        description=(
            "The blade and grappling art of the Malay Archipelago. Low "
            "stances, curved blades, trapping hands, and devastating "
            "close-range techniques."
        ),
        historical_note=(
            "Pencak Silat was already ancient when Portuguese traders first "
            "documented it in the 1500s. The kris dagger is both weapon and "
            "cultural artifact."
        ),
        passive_ranged_accuracy=0.15,
        special_action=StyleAction(
            id="keris_strike",
            name="Keris Strike",
            action_type="attack",
            stamina_cost=3,
            beats=("slash",),
            loses_to=("parry", "dodge"),
            damage_bonus=1,
            flavor=(
                "The curved kris finds the gap between guard and grip \u2014 "
                "the opponent's weapon arm goes numb."
            ),
            cooldown=2,
        ),
        training_port_ids=("jade_port", "monsoon_reach"),
        silver_cost=120,
        training_days=8,
        prerequisite_styles=1,
        required_body_parts=("hand", "leg"),
    ),
    "lua": FightingStyle(
        id="lua",
        name="Lua",
        region="South Seas",
        description=(
            "The bone-breaking art of Polynesia. Joint locks, pressure "
            "points, and techniques designed not to wound but to permanently "
            "disable."
        ),
        historical_note=(
            "Hawaiian Lua was restricted to the warrior class. Its techniques "
            "were so dangerous that training was conducted in secret, at "
            "night, under oath."
        ),
        passive_injury_bonus=0.20,
        passive_parry_bonus=1,
        special_action=StyleAction(
            id="joint_lock",
            name="Joint Lock",
            action_type="utility",
            stamina_cost=3,
            beats=("parry",),
            loses_to=("thrust", "slash"),
            damage_bonus=0,
            flavor=(
                "You seize the opponent's arm and twist. Bone grinds against "
                "joint. They can only writhe and dodge."
            ),
            cooldown=3,
        ),
        training_port_ids=("coral_throne", "typhoon_anchorage"),
        silver_cost=150,
        training_days=10,
        prerequisite_styles=1,
        required_body_parts=("hand", "arm"),
    ),
}

# ---------------------------------------------------------------------------
# Style masters (2 per style, 10 total)
# ---------------------------------------------------------------------------

STYLE_MASTERS: dict[str, StyleMaster] = {
    "maestro_luciano": StyleMaster(
        id="maestro_luciano",
        name="Maestro Luciano",
        style_id="la_destreza",
        port_id="porto_novo",
        description=(
            "A retired fencing master who teaches the Spanish school from a "
            "warehouse overlooking the harbor."
        ),
        dialog=(
            "\"The sword is a compass. Your body is the circle. Step "
            "correctly and no blade can touch you.\""
        ),
    ),
    "senora_vega": StyleMaster(
        id="senora_vega",
        name="Se\u00f1ora Vega",
        style_id="la_destreza",
        port_id="al_manar",
        description=(
            "A Castilian expatriate who runs the only fencing school east "
            "of Gibraltar."
        ),
        dialog=(
            "\"You fight like a dockhand. I will teach you to fight like "
            "a mathematician.\""
        ),
    ),
    "red_hamish": StyleMaster(
        id="red_hamish",
        name="Red Hamish",
        style_id="highland_broadsword",
        port_id="ironhaven",
        description=(
            "A massive Scotsman with arms like anchor chains. He teaches "
            "broadsword in the foundry yard, sparking steel against iron."
        ),
        dialog=(
            "\"Ye dinnae need fancy footwork when ye can split a man's "
            "shield in two. Hit harder. Again.\""
        ),
    ),
    "jarl_solveig": StyleMaster(
        id="jarl_solveig",
        name="Jarl Solveig",
        style_id="highland_broadsword",
        port_id="thornport",
        description=(
            "A Norse shieldmaiden who settled in Thornport after twenty "
            "years of raiding. She teaches the old ways."
        ),
        dialog=(
            "\"The broadsword is not a weapon. It is a statement. When you "
            "swing, mean it.\""
        ),
    ),
    "kolo_the_fist": StyleMaster(
        id="kolo_the_fist",
        name="Kolo the Fist",
        style_id="dambe",
        port_id="sun_harbor",
        description=(
            "A retired champion whose wrapped fists have broken more guards "
            "than any siege engine. He teaches on the beach at dawn."
        ),
        dialog=(
            "\"The spear fist strikes. The shield hand protects. The leg "
            "decides. Simple. Now do it a thousand times.\""
        ),
    ),
    "nneka_ironfist": StyleMaster(
        id="nneka_ironfist",
        name="Nneka Ironfist",
        style_id="dambe",
        port_id="pearl_shallows",
        description=(
            "A woman who earned her name in the fighting circles of the "
            "Gold Coast. She teaches with bruises, not words."
        ),
        dialog=(
            "\"You think fighting is about your arms? Your legs carry the "
            "fight. Everything begins from the ground.\""
        ),
    ),
    "pak_reza": StyleMaster(
        id="pak_reza",
        name="Pak Reza",
        style_id="silat",
        port_id="jade_port",
        description=(
            "An elderly silat master who moves like smoke. His school is "
            "hidden behind a porcelain shop."
        ),
        dialog=(
            "\"The kris is not a sword. It does not cut \u2014 it finds. "
            "Every body has openings. I will teach you to see them.\""
        ),
    ),
    "dewi_ayu": StyleMaster(
        id="dewi_ayu",
        name="Dewi Ayu",
        style_id="silat",
        port_id="monsoon_reach",
        description=(
            "A trader's daughter who learned silat from her grandmother. "
            "She teaches in the monsoon rain because 'the deck is always "
            "wet.'"
        ),
        dialog=(
            "\"Western fencing stands tall and proud. Silat crouches low "
            "and survives. Which do you think lasts longer at sea?\""
        ),
    ),
    "kahoku_the_elder": StyleMaster(
        id="kahoku_the_elder",
        name="Kahoku the Elder",
        style_id="lua",
        port_id="coral_throne",
        description=(
            "An ancient warrior-priest whose hands have set more bones than "
            "any doctor \u2014 because he broke them first."
        ),
        dialog=(
            "\"Lua was never meant for sport. Every hold is designed to end "
            "a fight permanently. Are you certain you want this knowledge?\""
        ),
    ),
    "leilani_bonecatcher": StyleMaster(
        id="leilani_bonecatcher",
        name="Leilani Bonecatcher",
        style_id="lua",
        port_id="typhoon_anchorage",
        description=(
            "A young woman with an old name. She learned Lua from her "
            "grandfather and teaches it to those the sea has tested."
        ),
        dialog=(
            "\"The bones tell you everything. How strong they are, where "
            "they bend, where they break. Listen to the bones.\""
        ),
    ),
}
