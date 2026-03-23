"""Cultural knowledge system — Star Freight Phase 3.

Cultural knowledge changes available choices, not just text.
Civilizations differ in play grammar — different kinds of asks, mistakes,
leverage, insult, trust-building, and opportunity.

This is NOT a codex meter. This is social logic that the player navigates.
Knowledge enters the game through crew (portable) and experience (earned).

Design laws:
- No knowledge: risky/default interaction
- Crew-assisted knowledge: better option appears
- Higher knowledge: deeper option appears
- Wrong move: consequence is real and legible
- Same system affects trade, encounter resolution, and narrative access

Pure functions. Callers decide mutations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from portlight.engine.crew import (
    CrewRosterState,
    Civilization,
    cultural_knowledge_level,
    crew_by_civ,
)


# ---------------------------------------------------------------------------
# Interaction model
# ---------------------------------------------------------------------------

class InteractionOutcome(str, Enum):
    """How a cultural interaction resolved."""
    SUCCESS = "success"            # Player navigated correctly
    PARTIAL = "partial"            # Acceptable but not ideal
    NEUTRAL = "neutral"            # No cultural weight
    MISSTEP = "misstep"            # Mistake, recoverable
    OFFENSE = "offense"            # Serious violation


@dataclass
class CulturalOption:
    """One available choice in a cultural interaction."""
    id: str
    label: str                       # What the player sees
    description: str                 # Why this matters (if knowledge sufficient)
    knowledge_required: int          # 0-3 minimum to see this option
    outcome: InteractionOutcome
    reputation_delta: int = 0        # change to civ standing
    trade_modifier: float = 0.0      # price modifier this interaction
    narrative_unlock: str = ""       # narrative hook unlocked
    consequence_tag: str = ""        # tag for consequence engine
    crew_advice: str = ""            # what a crew member from this civ would say


@dataclass
class CulturalInteraction:
    """A situation where cultural knowledge matters."""
    id: str
    civilization: Civilization
    context: str                     # trade | encounter | station | transit
    situation: str                   # Human-readable description
    options: list[CulturalOption] = field(default_factory=list)
    knowledge_hint: str = ""         # What a knowledgeable player would notice
    ignorance_risk: str = ""         # What an ignorant player might stumble into


@dataclass
class InteractionResult:
    """What happened after a cultural choice."""
    option_chosen: str
    outcome: InteractionOutcome
    reputation_delta: int
    trade_modifier: float
    narrative_unlock: str
    consequence_tag: str
    feedback: str                    # What the player learns from this
    crew_warned: bool                # Whether crew member gave advice before choice


# ---------------------------------------------------------------------------
# Evaluation engine
# ---------------------------------------------------------------------------

def evaluate_interaction(
    interaction: CulturalInteraction,
    choice_id: str,
    roster: CrewRosterState,
    base_knowledge: dict[str, int],
) -> InteractionResult:
    """Evaluate a cultural choice.

    This is the core evaluation. It:
    1. Checks what knowledge level the player has (base + crew)
    2. Finds the chosen option
    3. Determines if crew gave advice
    4. Computes the result
    """
    civ = interaction.civilization
    knowledge = cultural_knowledge_level(roster, civ, base_knowledge)
    civ_crew = crew_by_civ(roster, civ)
    crew_warned = len(civ_crew) > 0

    # Find chosen option
    chosen = None
    for opt in interaction.options:
        if opt.id == choice_id:
            chosen = opt
            break

    if chosen is None:
        return InteractionResult(
            option_chosen=choice_id,
            outcome=InteractionOutcome.NEUTRAL,
            reputation_delta=0,
            trade_modifier=0.0,
            narrative_unlock="",
            consequence_tag="",
            feedback="That option wasn't available.",
            crew_warned=False,
        )

    # Generate feedback based on outcome and knowledge
    if chosen.outcome == InteractionOutcome.SUCCESS:
        feedback = f"Well handled. Your understanding of the {civ.value.title()} served you."
        if crew_warned:
            feedback = f"{civ_crew[0].name} nods approvingly. You read the room correctly."
    elif chosen.outcome == InteractionOutcome.PARTIAL:
        feedback = f"Acceptable, but a deeper understanding of the {civ.value.title()} would have opened better options."
    elif chosen.outcome == InteractionOutcome.MISSTEP:
        feedback = f"The {civ.value.title()} notice your mistake. It's not fatal, but they'll remember."
        if crew_warned and knowledge >= chosen.knowledge_required:
            feedback = f"{civ_crew[0].name} warned you, and you chose wisely. The {civ.value.title()} notice your restraint."
    elif chosen.outcome == InteractionOutcome.OFFENSE:
        feedback = f"You've caused serious offense. The {civ.value.title()} will not forget this."
        if crew_warned:
            feedback = f"{civ_crew[0].name} tried to warn you. This will cost."
    else:
        feedback = "No cultural significance."

    return InteractionResult(
        option_chosen=choice_id,
        outcome=chosen.outcome,
        reputation_delta=chosen.reputation_delta,
        trade_modifier=chosen.trade_modifier,
        narrative_unlock=chosen.narrative_unlock,
        consequence_tag=chosen.consequence_tag,
        feedback=feedback,
        crew_warned=crew_warned,
    )


def get_visible_options(
    interaction: CulturalInteraction,
    roster: CrewRosterState,
    base_knowledge: dict[str, int],
) -> list[CulturalOption]:
    """Get options the player can see based on their knowledge level.

    Higher knowledge reveals better options. Options below knowledge level
    are visible. Options above are hidden (the player doesn't know they exist).
    """
    civ = interaction.civilization
    knowledge = cultural_knowledge_level(roster, civ, base_knowledge)
    return [opt for opt in interaction.options if opt.knowledge_required <= knowledge]


def get_crew_advice(
    interaction: CulturalInteraction,
    roster: CrewRosterState,
    base_knowledge: dict[str, int],
) -> str | None:
    """Get advice from a crew member about this interaction, if available.

    Crew from the civilization can warn about hidden risks or suggest
    the best option from their cultural perspective.
    """
    civ = interaction.civilization
    civ_crew = crew_by_civ(roster, civ)
    if not civ_crew:
        return None

    knowledge = cultural_knowledge_level(roster, civ, base_knowledge)
    crew_name = civ_crew[0].name

    # Find the best option the crew would recommend
    best_option = None
    for opt in interaction.options:
        if opt.crew_advice:
            if best_option is None or opt.outcome.value < best_option.outcome.value:
                best_option = opt

    if best_option and best_option.crew_advice:
        return f"{crew_name}: \"{best_option.crew_advice}\""

    # Generic advice based on risks
    risky_options = [o for o in interaction.options if o.outcome in (InteractionOutcome.MISSTEP, InteractionOutcome.OFFENSE)]
    if risky_options:
        return f"{crew_name}: \"Be careful here. The {civ.value.title()} have specific expectations.\""

    return None


# ---------------------------------------------------------------------------
# Keth civilization — Seasonal Protocols
# ---------------------------------------------------------------------------

class KethSeason(str, Enum):
    """Keth biological calendar. 360-day cycle, 90 days per season."""
    EMERGENCE = "emergence"    # days 0-89: celebratory, generous, open
    HARVEST = "harvest"        # days 90-179: gift-giving opens doors, productive
    DORMANCY = "dormancy"      # days 180-269: slow, pushing deals is offensive
    SPAWNING = "spawning"      # days 270-359: outsiders restricted, inner stations closed


def get_keth_season(day: int) -> KethSeason:
    """Derive current Keth season from game day."""
    phase = ((day - 1) % 360)
    if phase < 90:
        return KethSeason.EMERGENCE
    elif phase < 180:
        return KethSeason.HARVEST
    elif phase < 270:
        return KethSeason.DORMANCY
    else:
        return KethSeason.SPAWNING


def keth_season_visible(knowledge: int) -> bool:
    """At level 0, the player doesn't even know which season it is."""
    return knowledge >= 1


@dataclass
class KethSeasonalEffect:
    """How the current Keth season affects interactions."""
    season: KethSeason
    trade_modifier: float            # price modifier at Keth stations
    gift_effectiveness: float        # multiplier on gift-giving reputation gain
    deal_pressure_penalty: int       # reputation cost of pushing deals
    outsider_restriction: bool       # whether inner stations are restricted
    mood: str                        # general atmosphere


KETH_SEASONAL_EFFECTS: dict[KethSeason, KethSeasonalEffect] = {
    KethSeason.EMERGENCE: KethSeasonalEffect(
        season=KethSeason.EMERGENCE,
        trade_modifier=-0.10,        # 10% discount — celebratory
        gift_effectiveness=1.5,
        deal_pressure_penalty=0,
        outsider_restriction=False,
        mood="The Keth are celebrating. New growth, open markets, generous spirits.",
    ),
    KethSeason.HARVEST: KethSeasonalEffect(
        season=KethSeason.HARVEST,
        trade_modifier=-0.05,        # slight discount — productive period
        gift_effectiveness=2.0,      # gifts are most effective here
        deal_pressure_penalty=-2,
        outsider_restriction=False,
        mood="Harvest season. The Keth are busy but receptive. Gifts carry weight.",
    ),
    KethSeason.DORMANCY: KethSeasonalEffect(
        season=KethSeason.DORMANCY,
        trade_modifier=0.15,         # surcharge — business is slow
        gift_effectiveness=0.5,
        deal_pressure_penalty=-8,    # pushing deals is seriously offensive
        outsider_restriction=False,
        mood="Dormancy. The Keth are quiet. Patience is expected. Pressure is remembered.",
    ),
    KethSeason.SPAWNING: KethSeasonalEffect(
        season=KethSeason.SPAWNING,
        trade_modifier=0.25,         # heavy surcharge — restricted access
        gift_effectiveness=0.0,      # gifts are inappropriate
        deal_pressure_penalty=-15,   # pushing is catastrophic
        outsider_restriction=True,   # inner stations closed
        mood="Spawning season. Outsiders should tread carefully. Some stations are closed entirely.",
    ),
}


def keth_trade_interaction(
    day: int,
    is_pushing_deal: bool,
    is_offering_gift: bool,
    knowledge: int,
) -> CulturalInteraction:
    """Generate a Keth trade interaction based on current season.

    This is not a template — it produces different social logic depending
    on the season. Harvest gift-giving is smart. Dormancy gift-giving is
    awkward. Spawning gift-giving is offensive.
    """
    season = get_keth_season(day)
    effects = KETH_SEASONAL_EFFECTS[season]
    options: list[CulturalOption] = []

    # Option 1: Standard trade (always visible)
    options.append(CulturalOption(
        id="standard_trade",
        label="Trade at posted prices",
        description="Accept the market rate without cultural engagement.",
        knowledge_required=0,
        outcome=InteractionOutcome.NEUTRAL,
        reputation_delta=1,
        trade_modifier=effects.trade_modifier,
        consequence_tag="keth_standard_trade",
    ))

    # Option 2: Push for a deal (always visible, risky during dormancy/spawning)
    if season in (KethSeason.DORMANCY, KethSeason.SPAWNING):
        push_outcome = InteractionOutcome.OFFENSE if season == KethSeason.SPAWNING else InteractionOutcome.MISSTEP
        options.append(CulturalOption(
            id="push_deal",
            label="Press for better terms",
            description="Negotiate aggressively for a discount." if knowledge < 1 else
                        f"The Keth are in {season.value}. Pushing now will be remembered.",
            knowledge_required=0,
            outcome=push_outcome,
            reputation_delta=effects.deal_pressure_penalty,
            trade_modifier=effects.trade_modifier - 0.05,  # slight discount but at cost
            consequence_tag=f"keth_pushed_during_{season.value}",
            crew_advice=f"Don't push. It's {season.value}. The Communion doesn't forget pressure during this cycle.",
        ))
    else:
        options.append(CulturalOption(
            id="push_deal",
            label="Negotiate firmly",
            description="The Keth respect directness during active seasons.",
            knowledge_required=0,
            outcome=InteractionOutcome.PARTIAL,
            reputation_delta=0,
            trade_modifier=effects.trade_modifier - 0.05,
            consequence_tag="keth_negotiated",
        ))

    # Option 3: Offer a gift (knowledge >= 1, effectiveness varies by season)
    if season == KethSeason.SPAWNING:
        options.append(CulturalOption(
            id="offer_gift",
            label="Offer a cultural gift",
            description="Present a gift to the Communion elder." if knowledge < 2 else
                        "Gifts during spawning are taboo. This will offend.",
            knowledge_required=1,
            outcome=InteractionOutcome.OFFENSE,
            reputation_delta=-10,
            consequence_tag="keth_gift_during_spawning",
            crew_advice="No gifts. Not during spawning. It implies you think they need help — that's an insult.",
        ))
    elif season == KethSeason.HARVEST:
        options.append(CulturalOption(
            id="offer_gift",
            label="Offer a harvest gift",
            description="Present a gift during harvest — the traditional time for exchange.",
            knowledge_required=1,
            outcome=InteractionOutcome.SUCCESS,
            reputation_delta=5,
            trade_modifier=-0.10,  # significant discount
            narrative_unlock="keth_harvest_trust",
            consequence_tag="keth_harvest_gift",
            crew_advice="Gift now. Harvest is when the Communion values exchange most. This opens doors.",
        ))
    else:
        rep_gain = 3 if season == KethSeason.EMERGENCE else 1
        options.append(CulturalOption(
            id="offer_gift",
            label="Offer a cultural gift",
            description="Present a gift to build goodwill.",
            knowledge_required=1,
            outcome=InteractionOutcome.SUCCESS if season == KethSeason.EMERGENCE else InteractionOutcome.PARTIAL,
            reputation_delta=rep_gain,
            trade_modifier=-0.05,
            consequence_tag=f"keth_gift_{season.value}",
            crew_advice="Gifts are welcome now, though harvest would be better timing.",
        ))

    # Option 4: Wait for the right season (knowledge >= 2)
    if season in (KethSeason.DORMANCY, KethSeason.SPAWNING):
        options.append(CulturalOption(
            id="wait_season",
            label="Acknowledge the season and defer",
            description="Tell the Keth you'll return when the time is right.",
            knowledge_required=2,
            outcome=InteractionOutcome.SUCCESS,
            reputation_delta=3,
            consequence_tag="keth_seasonal_respect",
            crew_advice="Showing you know their calendar earns more respect than any trade.",
        ))

    return CulturalInteraction(
        id=f"keth_trade_{season.value}",
        civilization=Civilization.KETH,
        context="trade",
        situation=effects.mood if knowledge >= 1 else "You're at a Keth trading station.",
        options=options,
        knowledge_hint=f"The Keth are in {season.value} season." if knowledge >= 1 else "",
        ignorance_risk="You don't know the Keth seasonal calendar. Some actions may have unexpected consequences.",
    )


# ---------------------------------------------------------------------------
# Veshan civilization — Debt Ledger
# ---------------------------------------------------------------------------

@dataclass
class VeshanDebt:
    """A single debt in the Veshan honor economy."""
    id: str
    house: str                       # drashan, vekhari, solketh
    weight: str                      # minor, standard, major
    direction: str                   # owed (you owe them) or held (they owe you)
    description: str
    day_created: int
    age_days: int = 0                # how old the debt is (updated by caller)


def veshan_debt_visible(knowledge: int, weight: str) -> bool:
    """Whether the player understands the weight of a debt.

    At level 0: you can't tell minor from major. Dangerous.
    At level 1: you can tell the category.
    At level 2: you understand the implications.
    """
    if knowledge >= 1:
        return True
    # At level 0, minor debts look the same as major ones
    return False


def veshan_encounter_interaction(
    player_debts: list[VeshanDebt],
    house: str,
    knowledge: int,
    is_challenged: bool,
) -> CulturalInteraction:
    """Generate a Veshan encounter interaction.

    Veshan interactions revolve around honor, debts, and directness.
    The Debt Ledger is not a flavor system — it's leverage.
    """
    options: list[CulturalOption] = []

    # Check if player has debts with this house
    debts_owed = [d for d in player_debts if d.house == house and d.direction == "owed"]
    debts_held = [d for d in player_debts if d.house == house and d.direction == "held"]
    has_major_owed = any(d.weight == "major" for d in debts_owed)
    has_held = len(debts_held) > 0

    if is_challenged:
        # Veshan challenge scenario

        # Option 1: Accept the challenge (always visible)
        options.append(CulturalOption(
            id="accept_challenge",
            label="Accept the challenge",
            description="Face the Veshan directly. They respect this above all." if knowledge >= 1 else
                        "They seem to expect a fight.",
            knowledge_required=0,
            outcome=InteractionOutcome.SUCCESS,
            reputation_delta=5,
            consequence_tag="veshan_challenge_accepted",
            crew_advice="Accept. Among the Veshan, refusing a direct challenge marks you as unworthy of any further dealing.",
        ))

        # Option 2: Refuse (always visible, always bad)
        options.append(CulturalOption(
            id="refuse_challenge",
            label="Decline the challenge",
            description="Walk away." if knowledge < 1 else
                        "Refusing a Veshan challenge is a permanent mark of cowardice.",
            knowledge_required=0,
            outcome=InteractionOutcome.OFFENSE,
            reputation_delta=-15,
            consequence_tag="veshan_challenge_refused",
            crew_advice="Don't refuse. You will never trade in Veshan space again if you refuse a direct challenge.",
        ))

        # Option 3: Invoke a debt (knowledge >= 1, must hold a debt)
        if has_held:
            best_debt = max(debts_held, key=lambda d: {"minor": 1, "standard": 2, "major": 3}[d.weight])
            options.append(CulturalOption(
                id="invoke_debt",
                label=f"Invoke your {best_debt.weight} debt with House {house.title()}",
                description=f"Call in the debt: \"{best_debt.description}\"." if knowledge >= 2 else
                            "You hold a debt with this house. It may give you leverage.",
                knowledge_required=1,
                outcome=InteractionOutcome.SUCCESS,
                reputation_delta=2 if best_debt.weight != "minor" else -3,  # wasting a minor debt on this is gauche
                narrative_unlock=f"veshan_debt_invoked_{house}",
                consequence_tag="veshan_debt_invoked",
                crew_advice=f"Invoke the {best_debt.weight} debt. The Veshan honor the ledger above all. "
                            f"{'But a minor debt for this is wasteful — they will notice.' if best_debt.weight == 'minor' else 'This is the right use of leverage.'}",
            ))

        # Option 4: Acknowledge honor (knowledge >= 2)
        options.append(CulturalOption(
            id="honor_greeting",
            label="Offer the formal honor acknowledgment",
            description="Use the Veshan greeting of respect between equals.",
            knowledge_required=2,
            outcome=InteractionOutcome.SUCCESS,
            reputation_delta=3,
            consequence_tag="veshan_honor_acknowledged",
            crew_advice="The formal greeting changes the temperature. They'll still challenge, but on better terms.",
        ))

    else:
        # Veshan trade/negotiation scenario

        # Option 1: Standard trade (always visible)
        options.append(CulturalOption(
            id="direct_deal",
            label="Propose a deal directly",
            description="State what you want and what you'll pay. Veshan respect directness.",
            knowledge_required=0,
            outcome=InteractionOutcome.PARTIAL if knowledge < 1 else InteractionOutcome.SUCCESS,
            reputation_delta=1,
            trade_modifier=-0.05,
            consequence_tag="veshan_direct_trade",
            crew_advice="Directness is good. But if you don't mention the ledger, they'll think you're ignorant of it.",
        ))

        # Option 2: Indirect/evasive (always visible, always bad with Veshan)
        options.append(CulturalOption(
            id="indirect_approach",
            label="Negotiate indirectly, feel out the terms",
            description="Try to gauge what they want before committing." if knowledge < 1 else
                        "The Veshan despise indirectness. This will be read as deception.",
            knowledge_required=0,
            outcome=InteractionOutcome.MISSTEP,
            reputation_delta=-5,
            trade_modifier=0.10,  # surcharge for being evasive
            consequence_tag="veshan_indirect_trade",
            crew_advice="Don't hedge. The Veshan read indirectness as lying. Say what you mean.",
        ))

        # Option 3: Reference the debt ledger (knowledge >= 1)
        if has_major_owed:
            options.append(CulturalOption(
                id="acknowledge_debt",
                label=f"Acknowledge your debt to House {house.title()}",
                description="Show awareness of your obligations before asking for trade terms.",
                knowledge_required=1,
                outcome=InteractionOutcome.SUCCESS,
                reputation_delta=3,
                trade_modifier=-0.10,  # better terms for honoring the ledger
                consequence_tag="veshan_debt_acknowledged",
                crew_advice="Mention the debt first. It shows respect for the ledger. They'll give you better terms.",
            ))
        elif has_held:
            options.append(CulturalOption(
                id="leverage_debt",
                label=f"Mention what House {house.title()} owes you",
                description="Remind them of their obligation — carefully.",
                knowledge_required=1,
                outcome=InteractionOutcome.SUCCESS if knowledge >= 2 else InteractionOutcome.PARTIAL,
                reputation_delta=1,
                trade_modifier=-0.15,  # significant leverage
                consequence_tag="veshan_leverage_applied",
                crew_advice="You can use this. But mention it as fact, not threat. The Veshan know what they owe.",
            ))

        # Option 4: House-specific approach (knowledge >= 2)
        if house == "drashan":
            options.append(CulturalOption(
                id="martial_respect",
                label="Open with your combat record",
                description="House Drashan values martial achievement above trade skill.",
                knowledge_required=2,
                outcome=InteractionOutcome.SUCCESS,
                reputation_delta=4,
                trade_modifier=-0.10,
                narrative_unlock="drashan_warrior_regard",
                consequence_tag="veshan_martial_approach",
                crew_advice="Drashan respects fighters. Lead with your record — they'll treat you as a peer, not a trader.",
            ))
        elif house == "vekhari":
            options.append(CulturalOption(
                id="prosperity_talk",
                label="Discuss mutual prosperity opportunities",
                description="House Vekhari is the mercantile house — they think in portfolios.",
                knowledge_required=2,
                outcome=InteractionOutcome.SUCCESS,
                reputation_delta=3,
                trade_modifier=-0.12,
                narrative_unlock="vekhari_trade_circle",
                consequence_tag="veshan_prosperity_approach",
                crew_advice="Vekhari think in networks, not transactions. Propose ongoing value, not a single deal.",
            ))

    return CulturalInteraction(
        id=f"veshan_{'challenge' if is_challenged else 'trade'}_{house}",
        civilization=Civilization.VESHAN,
        context="encounter" if is_challenged else "trade",
        situation="A Veshan warrior from House {} has challenged you.".format(house.title()) if is_challenged else
                  f"You're negotiating with House {house.title()} representatives.",
        options=options,
        knowledge_hint="The Veshan value directness, honor, and the Debt Ledger above all." if knowledge >= 1 else "",
        ignorance_risk="You don't understand Veshan customs. Missteps here have long consequences.",
    )


# ---------------------------------------------------------------------------
# Generic cultural check (for wiring into other systems)
# ---------------------------------------------------------------------------

def cultural_trade_modifier(
    civ: Civilization,
    roster: CrewRosterState,
    base_knowledge: dict[str, int],
    day: int = 1,
) -> float:
    """Get the trade price modifier for cultural standing.

    This feeds into the economy engine. Higher knowledge = better prices.
    """
    knowledge = cultural_knowledge_level(roster, civ, base_knowledge)
    base = 0.0

    # Knowledge discount
    if knowledge >= 3:
        base = -0.15
    elif knowledge >= 2:
        base = -0.10
    elif knowledge >= 1:
        base = -0.05

    # Keth seasonal modifier stacks
    if civ == Civilization.KETH:
        season = get_keth_season(day)
        base += KETH_SEASONAL_EFFECTS[season].trade_modifier

    return base


def cultural_encounter_options(
    civ: Civilization,
    roster: CrewRosterState,
    base_knowledge: dict[str, int],
) -> dict:
    """What cultural options are available during an encounter with this civ.

    This feeds into the combat/encounter system. Higher knowledge =
    more options for avoiding or shaping combat.
    """
    knowledge = cultural_knowledge_level(roster, civ, base_knowledge)

    options = {
        "can_negotiate": knowledge >= 1,        # can attempt to talk instead of fight
        "can_surrender_terms": knowledge >= 1,   # knows how surrender works in this culture
        "can_cultural_leverage": knowledge >= 2,  # can use cultural knowledge for advantage
        "can_inner_circle": knowledge >= 3,       # can invoke deep cultural connections
        "knowledge_level": knowledge,
    }

    # Civ-specific encounter options
    if civ == Civilization.VESHAN:
        options["can_honor_challenge"] = True  # Veshan always offer this
        options["can_invoke_debt"] = knowledge >= 1  # need to know the system
    elif civ == Civilization.KETH:
        options["can_invoke_communion"] = knowledge >= 2  # appeal to collective judgment
        options["seasonal_awareness"] = knowledge >= 1

    return options
