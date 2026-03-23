"""Pirate factions and named captains — the underworld political ecosystem.

Four factions carve the Known World's lawless waters. Each has territory,
goods preferences, a code, and named captains who become recurring characters
in the player's story. Your standing with each faction determines whether
they attack, trade, or ally.

Design principle: pirates are PEOPLE, not random encounters. Every captain
has a personality, and every faction has rules. The underworld has its own
politics, and the smart smuggler navigates them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from portlight.engine.models import Season


@dataclass(frozen=True)
class PirateFaction:
    """A named pirate organization with territory and agenda."""
    id: str
    name: str
    territory_regions: list[str]
    base_port_id: str | None         # home port (BLACK_MARKET) or None for nomadic
    preferred_goods: list[str]       # goods they trade/steal
    contraband_specialty: str        # which contraband they deal in most
    description: str
    ethos: str                       # one-liner philosophy
    smuggler_attitude: str           # friendly / neutral / hostile toward smugglers
    merchant_attitude: str           # toward merchants
    seasonal_activity: dict[Season, float] = field(default_factory=dict)  # season -> mult
    encounter_flavor: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PirateCaptain:
    """A named pirate captain who becomes a recurring character."""
    id: str
    name: str
    faction_id: str
    personality: str                 # aggressive / defensive / balanced / wild
    strength: int                    # 1-10, duel difficulty
    description: str
    encounter_text: str              # what you see when they appear
    deal_text: str                   # what they say when offering a deal
    attack_text: str                 # what they say when attacking
    retreat_text: str                # when they back off (high standing)
    # Duel flavor
    duel_opening: str = ""
    duel_win_line: str = ""          # they win a round
    duel_loss_line: str = ""         # they lose a round
    duel_defeat: str = ""            # player beats them
    duel_victory: str = ""           # they beat the player


# ---------------------------------------------------------------------------
# The Four Factions
# ---------------------------------------------------------------------------

FACTIONS: dict[str, PirateFaction] = {f.id: f for f in [
    PirateFaction(
        id="crimson_tide",
        name="The Crimson Tide",
        territory_regions=["Mediterranean", "North Atlantic"],
        base_port_id="corsairs_rest",
        preferred_goods=["weapons", "rum", "black_powder"],
        contraband_specialty="black_powder",
        description=(
            "The largest pirate fleet in the Mediterranean. Organized, militaristic, "
            "and ruthlessly efficient. They run a protection racket on the major trade "
            "lanes and sell black powder to anyone who can pay."
        ),
        ethos="Pay tribute or pay blood. We control the strait.",
        smuggler_attitude="neutral",
        merchant_attitude="hostile",
        seasonal_activity={
            Season.SPRING: 1.0,
            Season.SUMMER: 1.3,   # peak: calm seas, more targets
            Season.AUTUMN: 1.1,
            Season.WINTER: 0.6,   # they shelter too
        },
        encounter_flavor=[
            "A ship flying crimson pennants emerges from behind the headland.",
            "Three sails on the horizon — Crimson Tide formation. They've spotted you.",
            "A warning shot across the bow. The Crimson Tide wants your attention.",
        ],
    ),

    PirateFaction(
        id="monsoon_syndicate",
        name="The Monsoon Syndicate",
        territory_regions=["East Indies"],
        base_port_id="spice_narrows",
        preferred_goods=["spice", "silk", "opium"],
        contraband_specialty="opium",
        description=(
            "The power behind the Spice Lords. They control the opium trade and have "
            "informants in every port east of Crosswind Isle. They don't fight when "
            "they can bribe, and they don't bribe when they can blackmail."
        ),
        ethos="Information is currency. We know what you carry before you dock.",
        smuggler_attitude="friendly",
        merchant_attitude="tolerant",
        seasonal_activity={
            Season.SPRING: 0.8,
            Season.SUMMER: 1.5,   # monsoon: patrols shelter, Syndicate thrives
            Season.AUTUMN: 1.2,
            Season.WINTER: 0.9,
        },
        encounter_flavor=[
            "A junk with no flag slides alongside. The crew watches you in silence.",
            "A sampan approaches from the mist. The man at the bow knows your name.",
            "Signal lanterns flash from behind the islands. The Syndicate is watching.",
        ],
    ),

    PirateFaction(
        id="deep_reef",
        name="The Deep Reef Brotherhood",
        territory_regions=["South Seas", "West Africa"],
        base_port_id=None,  # nomadic fleet
        preferred_goods=["pearls", "medicines", "stolen_cargo"],
        contraband_specialty="stolen_cargo",
        description=(
            "Small crews, fast ships, and a code of honor that puts most navies to shame. "
            "They respect courage above all else. Prove yourself in a fight and they'll "
            "trade with you as equals. Run, and they'll take everything."
        ),
        ethos="The reef tests everyone. Those who earn it, keep it.",
        smuggler_attitude="respectful",
        merchant_attitude="prey",
        seasonal_activity={
            Season.SPRING: 1.2,   # diving season, reef active
            Season.SUMMER: 0.6,   # typhoon — even they shelter
            Season.AUTUMN: 1.3,   # peak activity
            Season.WINTER: 1.0,
        },
        encounter_flavor=[
            "An outrigger war canoe appears from behind the reef. Fast. Too fast.",
            "Painted sails — the Brotherhood's mark. They're circling you.",
            "A horn blast from the reef. The Deep Reef Brotherhood announces itself.",
        ],
    ),

    PirateFaction(
        id="iron_wolves",
        name="The Iron Wolves",
        territory_regions=["North Atlantic"],
        base_port_id=None,  # no port loyalty
        preferred_goods=["iron", "weapons", "black_powder"],
        contraband_specialty="black_powder",
        description=(
            "Former garrison soldiers who deserted when the pay stopped. They target "
            "military supply routes with professional precision. No wasted movement, "
            "no theatrics. They board, take what they want, and vanish into the fog."
        ),
        ethos="We were soldiers once. Now we're better paid.",
        smuggler_attitude="business",
        merchant_attitude="primary_target",
        seasonal_activity={
            Season.SPRING: 1.0,
            Season.SUMMER: 1.2,
            Season.AUTUMN: 1.1,
            Season.WINTER: 0.8,   # even wolves respect the Atlantic winter
        },
        encounter_flavor=[
            "A grey-hulled ship cuts through the fog. No flag, no warning. Iron Wolves.",
            "The ship matches your speed exactly. Professional pursuit. Wolves hunting.",
            "A signal lamp from the grey ship. Military precision — they want parley or plunder.",
        ],
    ),
]}


# ---------------------------------------------------------------------------
# Named Pirate Captains (2 per faction)
# ---------------------------------------------------------------------------

PIRATE_CAPTAINS: dict[str, PirateCaptain] = {pc.id: pc for pc in [
    # === CRIMSON TIDE ===
    PirateCaptain(
        id="scarlet_ana",
        name="Scarlet Ana",
        faction_id="crimson_tide",
        personality="balanced",
        strength=6,
        description="Captain of the Crimson Tide's diplomatic fleet. She prefers a deal to a fight, but fights well when she must.",
        encounter_text="A woman in a crimson coat stands at the bow of the approaching ship. Scarlet Ana. She's smiling — that could mean anything.",
        deal_text="\"Captain. Let's not waste each other's time. I have goods, you have silver. Or we can do this the other way.\"",
        attack_text="\"I gave you a chance. Remember that.\" She draws her saber.",
        retreat_text="\"A friend of the Tide. Safe passage, Captain. We'll talk business next time.\"",
        duel_opening="Scarlet Ana unsheathes a curved saber. \"Let's see if you trade steel as well as silk.\"",
        duel_win_line="\"Too slow, Captain. Commerce requires quicker thinking.\"",
        duel_loss_line="She staggers back, surprised. \"You've got fire. I respect that.\"",
        duel_defeat="Ana lowers her blade. \"Well fought. You've earned the Tide's respect today.\"",
        duel_victory="\"Your cargo is my commission. Don't take it personally — it's just business.\"",
    ),
    PirateCaptain(
        id="the_butcher",
        name="The Butcher",
        faction_id="crimson_tide",
        personality="aggressive",
        strength=8,
        description="The Crimson Tide's enforcer. No diplomacy, no deals. He takes what he wants and enjoys the taking.",
        encounter_text="A scarred man with a meat cleaver at his belt stands on the deck of a blood-stained ship. The Butcher has found you.",
        deal_text="\"Deal? I don't deal. I take. But you can buy your hull back with silver.\"",
        attack_text="\"I've been hungry all morning. Your cargo looks like breakfast.\"",
        retreat_text="\"The boss says you're a friend. Today you live. Don't make me remember your face.\"",
        duel_opening="The Butcher pulls a heavy cutlass from his belt. \"This won't take long.\"",
        duel_win_line="He grins through bloody teeth. \"That all you've got?\"",
        duel_loss_line="He snarls, pressing a hand to the wound. \"Lucky. Won't happen twice.\"",
        duel_defeat="The Butcher spits blood on the deck. \"Fine. You bought yourself today. Tomorrow's a different story.\"",
        duel_victory="\"Your ship. Your cargo. Your dignity. I'll take all three.\"",
    ),

    # === MONSOON SYNDICATE ===
    PirateCaptain(
        id="raj_the_quiet",
        name="Raj the Quiet",
        faction_id="monsoon_syndicate",
        personality="defensive",
        strength=5,
        description="The Syndicate's spymaster. He knows what's in your hold before you open it. He fights like he trades — patiently.",
        encounter_text="A sampan glides alongside with no sound. A thin man in grey silk sits cross-legged on the deck. Raj the Quiet already knows your name.",
        deal_text="\"I know what you carry. I know what it's worth. Let us skip the negotiations and arrive at the fair price.\"",
        attack_text="\"You were warned.\" He gestures. Three more ships emerge from the mist.",
        retreat_text="\"The Syndicate remembers its friends. Sail well, Captain. We are watching — protectively.\"",
        duel_opening="Raj draws a slender blade. He says nothing. His eyes do the talking.",
        duel_win_line="A slight nod, nothing more. His blade was faster than you expected.",
        duel_loss_line="He adjusts his stance, unhurried. \"Patience is a weapon too.\"",
        duel_defeat="Raj sheathes his blade and bows. \"You have earned the Syndicate's attention. Use it wisely.\"",
        duel_victory="\"Your cargo will fund operations. Your life is... a courtesy. This time.\"",
    ),
    PirateCaptain(
        id="typhoon_mei",
        name="Typhoon Mei",
        faction_id="monsoon_syndicate",
        personality="wild",
        strength=7,
        description="The monsoon in human form. Unpredictable, explosive, and impossible to outrun. She controls the eastern sea lanes with chaos.",
        encounter_text="A ship erupts from behind the island at impossible speed, sails full of monsoon wind. Typhoon Mei. She's already laughing.",
        deal_text="\"Trade! Trade is boring! But if you have opium, I'll pretend to be civilized for five minutes.\"",
        attack_text="\"CATCH ME IF YOU CAN! Or better — let me catch you!\"",
        retreat_text="\"Ohhh, you're one of Raj's friends. Fine. FINE. No fun today. But next time, we race!\"",
        duel_opening="Mei draws two short blades and spins them. \"Dance with me, Captain!\"",
        duel_win_line="\"HA! Too slow! The monsoon waits for no one!\"",
        duel_loss_line="\"OW! That was GOOD! Do it again!\" She's still smiling.",
        duel_defeat="Mei stops, chest heaving, grinning. \"You're FUN. I'm keeping you alive. The sea needs more fun people.\"",
        duel_victory="\"I win! I WIN! Your cargo is my prize and your pride is my dessert!\"",
    ),

    # === DEEP REEF BROTHERHOOD ===
    PirateCaptain(
        id="old_coral",
        name="Old Coral",
        faction_id="deep_reef",
        personality="defensive",
        strength=6,
        description="The Brotherhood's elder. Fifty years on the reef. He's seen everything and forgotten nothing. He respects courage and punishes cowardice.",
        encounter_text="An ancient outrigger approaches. The man at the tiller has coral-white hair and hands like ship rope. Old Coral. He's watching you with the patience of the reef.",
        deal_text="\"Young captain. The reef provides for those who respect it. I have medicines and pearls. What do you offer in return?\"",
        attack_text="\"You enter our waters without respect. The reef teaches its lessons hard.\"",
        retreat_text="\"A friend of the Brotherhood. The reef remembers. Sail safe, young one.\"",
        duel_opening="Old Coral draws a blade carved from coral-stone. \"I've fought a hundred captains. Show me something new.\"",
        duel_win_line="\"Predictable. The young always are.\" Not a boast — an observation.",
        duel_loss_line="He staggers but doesn't fall. \"Not bad, young one. Not bad at all.\"",
        duel_defeat="Old Coral nods slowly. \"The reef approves. You've earned what you carry.\"",
        duel_victory="\"You'll live. But your cargo stays with the reef. Come back stronger.\"",
    ),
    PirateCaptain(
        id="the_diver",
        name="The Diver",
        faction_id="deep_reef",
        personality="aggressive",
        strength=7,
        description="Lightning fast, in and out. She dives under your hull, boards from the waterline, and is gone before your crew draws steel.",
        encounter_text="Nothing. Then a thud against the hull. Then a rope. Then The Diver is standing on your deck, dripping wet, blade drawn.",
        deal_text="\"I don't usually talk. But you have medicines, and the Brotherhood needs them. Quick trade. Then I disappear.\"",
        attack_text="She doesn't speak. She's already moving.",
        retreat_text="A nod. She slips over the rail and is gone. The water closes over her without a ripple.",
        duel_opening="The Diver is already in fighting stance. Barefoot, blade low. She moves like water.",
        duel_win_line="She's behind you before you realize she moved. A cut appears on your arm.",
        duel_loss_line="She tumbles, rolls, comes up bleeding. Her eyes narrow. Respect.",
        duel_defeat="The Diver lowers her blade. No words. She dives overboard. When you look over the rail, she's gone.",
        duel_victory="She takes what she came for and vanishes over the side. You never hear the splash.",
    ),

    # === IRON WOLVES ===
    PirateCaptain(
        id="sergeant_kruze",
        name="Sergeant Kruze",
        faction_id="iron_wolves",
        personality="balanced",
        strength=7,
        description="Former garrison sergeant, now the Iron Wolves' commander. Professional, disciplined, and terrifyingly competent. He runs piracy like a military operation.",
        encounter_text="The grey ship pulls alongside with parade-ground precision. A man in a faded military coat stands at the rail. Sergeant Kruze. He's assessing your defenses.",
        deal_text="\"Captain. I need iron and powder. You need safe passage through my waters. Let's negotiate like officers.\"",
        attack_text="\"Boarding party, go.\" No drama. No speeches. Just the order.",
        retreat_text="\"You have the Wolves' mark. My patrols will leave you alone. Professional courtesy.\"",
        duel_opening="Kruze draws a military saber with practiced ease. \"Standard rules. First blood or surrender.\"",
        duel_win_line="\"Your footwork needs work. Drill it.\" He sounds like he's training a recruit.",
        duel_loss_line="He grunts, adjusting his guard. \"Good form. Who trained you?\"",
        duel_defeat="Kruze salutes with his blade. \"You've earned this day. The Wolves respect a soldier.\"",
        duel_victory="\"Stand down, Captain. Your cargo is requisitioned. No hard feelings.\"",
    ),
    PirateCaptain(
        id="gnaw",
        name="Gnaw",
        faction_id="iron_wolves",
        personality="aggressive",
        strength=9,
        description="The most feared pirate in the North Atlantic. He destroys what he can't take. Ships that resist him are found drifting, empty. He never explains.",
        encounter_text="The ship that appears has no name painted on its hull. Just claw marks gouged into the wood. Gnaw. Your crew goes quiet.",
        deal_text="\"I don't trade. But I'll take tribute. Half your hold. Then you live. Counteroffer: I take all of it.\"",
        attack_text="Silence. Then the grappling hooks fly.",
        retreat_text="He watches you pass. His crew stands ready. He lets you go — but his eyes follow you until you're over the horizon.",
        duel_opening="Gnaw draws a weapon that was once a boarding axe. Modified. Worse. \"Last chance to surrender.\"",
        duel_win_line="He doesn't speak. He just hits harder.",
        duel_loss_line="A sound between a growl and a laugh. He's enjoying this.",
        duel_defeat="Gnaw stares at you for a long moment. Then he turns and walks back to his ship. No words. That's the highest compliment he gives.",
        duel_victory="Gnaw takes your cargo, your silver, and your ship's nameplate. \"Remember this.\"",
    ),
]}


def get_faction_for_region(region: str) -> list[PirateFaction]:
    """Get all factions active in a region."""
    return [f for f in FACTIONS.values() if region in f.territory_regions]


def get_captains_for_faction(faction_id: str) -> list[PirateCaptain]:
    """Get all named captains in a faction."""
    return [c for c in PIRATE_CAPTAINS.values() if c.faction_id == faction_id]


# ---------------------------------------------------------------------------
# Faction Relationships — the political map of the underworld
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FactionRelationship:
    """How two factions view each other. Static reference data."""
    faction_a: str
    faction_b: str
    disposition: str          # allied / neutral / rival / hostile
    description: str          # flavor text explaining why
    spillover: float          # how much standing with A affects B (-1.0 to +0.5)
    vendetta_trigger: str     # what action triggers a vendetta from B when you help A


# Disposition key:
#   allied:   helping one helps the other (spillover +0.3 to +0.5)
#   neutral:  no strong feelings (spillover 0.0)
#   rival:    business competition (spillover -0.1 to -0.3)
#   hostile:  active conflict (spillover -0.3 to -0.5)

FACTION_RELATIONSHIPS: list[FactionRelationship] = [
    # === CRIMSON TIDE <-> MONSOON SYNDICATE ===
    FactionRelationship(
        faction_a="crimson_tide",
        faction_b="monsoon_syndicate",
        disposition="rival",
        description=(
            "Business rivals who respect each other's territory — barely. "
            "The Tide wants to control the Mediterranean-to-East route. "
            "The Syndicate wants to control all Eastern trade. "
            "They cooperate when it suits them and undercut when it doesn't."
        ),
        spillover=-0.15,
        vendetta_trigger="Running opium for the Syndicate through Tide waters.",
    ),

    # === CRIMSON TIDE <-> DEEP REEF ===
    FactionRelationship(
        faction_a="crimson_tide",
        faction_b="deep_reef",
        disposition="hostile",
        description=(
            "Fundamental incompatibility. The Tide runs a protection racket — "
            "pay or suffer. The Brotherhood answers to no one and attacks "
            "anyone who claims authority over the sea. They've been killing "
            "each other's captains for decades."
        ),
        spillover=-0.4,
        vendetta_trigger="Supplying weapons to the Tide that get used against Brotherhood ships.",
    ),

    # === CRIMSON TIDE <-> IRON WOLVES ===
    FactionRelationship(
        faction_a="crimson_tide",
        faction_b="iron_wolves",
        disposition="rival",
        description=(
            "Former allies who split over territory. Both are organized and "
            "militaristic, but the Wolves left when the Tide's leader demanded "
            "tribute from their operations. Now they compete for the same "
            "weapons trade in overlapping waters."
        ),
        spillover=-0.2,
        vendetta_trigger="Selling black powder to the Tide that was meant for the Wolves.",
    ),

    # === MONSOON SYNDICATE <-> DEEP REEF ===
    FactionRelationship(
        faction_a="monsoon_syndicate",
        faction_b="deep_reef",
        disposition="neutral",
        description=(
            "Different worlds, different rules. The Syndicate operates through "
            "information and politics in the East. The Brotherhood sails the "
            "Southern reefs on honor and courage. They rarely cross paths, "
            "and when they do, they nod and move on."
        ),
        spillover=0.0,
        vendetta_trigger="None — they don't care about each other.",
    ),

    # === MONSOON SYNDICATE <-> IRON WOLVES ===
    FactionRelationship(
        faction_a="monsoon_syndicate",
        faction_b="iron_wolves",
        disposition="hostile",
        description=(
            "The Wolves tried to muscle into the Eastern weapons trade. "
            "Raj the Quiet fed their fleet positions to a navy patrol. "
            "Three Wolf ships burned. The Wolves have never forgiven — "
            "or forgotten. Syndicate informants are killed on sight."
        ),
        spillover=-0.35,
        vendetta_trigger="Sharing intelligence with the Syndicate about Wolf positions.",
    ),

    # === DEEP REEF <-> IRON WOLVES ===
    FactionRelationship(
        faction_a="deep_reef",
        faction_b="iron_wolves",
        disposition="hostile",
        description=(
            "Mutual contempt. The Brotherhood sees the Wolves as soulless "
            "mercenaries who fight without honor. The Wolves see the Brotherhood "
            "as romantic fools who'll die for principles instead of profit. "
            "They attack each other whenever their paths cross."
        ),
        spillover=-0.3,
        vendetta_trigger="Fencing stolen cargo from Brotherhood raids through Wolf contacts.",
    ),
]


def get_relationship(faction_a: str, faction_b: str) -> FactionRelationship | None:
    """Get the relationship between two factions (order-independent)."""
    for rel in FACTION_RELATIONSHIPS:
        if (rel.faction_a == faction_a and rel.faction_b == faction_b) or \
           (rel.faction_a == faction_b and rel.faction_b == faction_a):
            return rel
    return None


def get_allies(faction_id: str) -> list[str]:
    """Get faction IDs that are allied with the given faction."""
    allies = []
    for rel in FACTION_RELATIONSHIPS:
        if rel.disposition == "allied":
            if rel.faction_a == faction_id:
                allies.append(rel.faction_b)
            elif rel.faction_b == faction_id:
                allies.append(rel.faction_a)
    return allies


def get_enemies(faction_id: str) -> list[str]:
    """Get faction IDs that are hostile to the given faction."""
    enemies = []
    for rel in FACTION_RELATIONSHIPS:
        if rel.disposition == "hostile":
            if rel.faction_a == faction_id:
                enemies.append(rel.faction_b)
            elif rel.faction_b == faction_id:
                enemies.append(rel.faction_a)
    return enemies


def get_rivals(faction_id: str) -> list[str]:
    """Get faction IDs that are rivals (competitive but not at war)."""
    rivals = []
    for rel in FACTION_RELATIONSHIPS:
        if rel.disposition == "rival":
            if rel.faction_a == faction_id:
                rivals.append(rel.faction_b)
            elif rel.faction_b == faction_id:
                rivals.append(rel.faction_a)
    return rivals
