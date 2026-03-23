"""Narrative engine — story beats, encounters, and quest hooks.

Narrative events are triggered by game state milestones and world conditions.
They don't replace the economy — they give meaning to commercial achievements.

Hero's Journey structure:
  1. The Call (first voyage, first trade)
  2. Crossing the Threshold (first new region)
  3. Tests and Allies (rival captains, mentor encounters, pirate threats)
  4. The Ordeal (storm survival, cargo seizure, near-bankruptcy)
  5. The Reward (first big contract, ship upgrade, reputation milestone)
  6. The Return (mastery, empire building, legacy)

Each narrative beat fires once per game and is tracked by ID.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from portlight.engine.models import Captain, WorldState
    from portlight.engine.contracts import ContractBoard
    from portlight.engine.infrastructure import InfrastructureState
    from portlight.receipts.models import ReceiptLedger


class NarrativePhase(str, Enum):
    """Hero's journey phases."""
    THE_CALL = "the_call"
    THRESHOLD = "threshold"
    TESTS = "tests"
    ORDEAL = "ordeal"
    REWARD = "reward"
    THE_RETURN = "the_return"


@dataclass
class NarrativeBeat:
    """A single story moment that fires once."""
    id: str
    phase: NarrativePhase
    title: str
    text: str
    flavor: str = ""           # Optional atmospheric detail
    hint: str = ""             # Gameplay hint embedded in story


@dataclass
class NarrativeState:
    """Tracks which story beats have fired."""
    fired: list[str] = field(default_factory=list)
    journal: list[JournalEntry] = field(default_factory=list)


@dataclass
class JournalEntry:
    """A narrative beat that was triggered, with context."""
    beat_id: str
    day: int
    port_id: str = ""
    region: str = ""


# ---------------------------------------------------------------------------
# Beat definitions
# ---------------------------------------------------------------------------

_BEATS: list[NarrativeBeat] = [
    # === THE CALL ===
    NarrativeBeat(
        id="first_trade",
        phase=NarrativePhase.THE_CALL,
        title="The First Deal",
        text=(
            "You count the silver from your first sale. It's not much, but it's yours. "
            "Every fortune in history started with a single trade."
        ),
        hint="Watch the market affinities — buy where goods are plentiful, sell where they're scarce.",
    ),
    NarrativeBeat(
        id="first_voyage",
        phase=NarrativePhase.THE_CALL,
        title="Into Open Water",
        text=(
            "The harbor shrinks behind you. The wind fills your sails and the crew "
            "settles into their watches. Whatever happens next, you've left the dock."
        ),
        hint="Keep provisions stocked. Running out at sea is a death sentence.",
    ),
    NarrativeBeat(
        id="first_profit",
        phase=NarrativePhase.THE_CALL,
        title="Profit and Promise",
        text=(
            "Your ledger shows a profit for the first time. The crew notices — "
            "a captain who can turn silver gets loyalty that gold can't buy."
        ),
    ),

    # === CROSSING THE THRESHOLD ===
    NarrativeBeat(
        id="new_region",
        phase=NarrativePhase.THRESHOLD,
        title="Strange Waters",
        text=(
            "The flags are unfamiliar. The language changes. The goods on the docks "
            "are things you've only heard about in tavern stories. "
            "You've crossed into a new world."
        ),
        hint="Build standing in new regions by trading consistently. Reputation opens doors.",
    ),
    NarrativeBeat(
        id="first_contract",
        phase=NarrativePhase.THRESHOLD,
        title="A Binding Word",
        text=(
            "You sign your name on a contract for the first time. The obligation weighs "
            "heavier than any cargo. Deliver on time, and doors open. Fail, and they close."
        ),
    ),
    NarrativeBeat(
        id="ship_upgrade",
        phase=NarrativePhase.THRESHOLD,
        title="A Bigger Ship",
        text=(
            "The new ship sits heavy in the water, her hold cavernous compared to your old sloop. "
            "Routes that were suicide runs become trade routes. "
            "The game just changed."
        ),
    ),

    # === TESTS AND ALLIES ===
    NarrativeBeat(
        id="survived_storm",
        phase=NarrativePhase.TESTS,
        title="Through the Tempest",
        text=(
            "The storm broke three spars and swept a man overboard. But you held the wheel, "
            "and the ship held together. The crew will never forget this night."
        ),
        flavor="The sea tests every captain. Those who survive earn something money can't buy.",
    ),
    NarrativeBeat(
        id="survived_pirates",
        phase=NarrativePhase.TESTS,
        title="Blood in the Water",
        text=(
            "Pirates spotted your cargo and gave chase. Whether by speed, guile, or luck, "
            "you kept your goods and your life. Not everyone on these waters can say the same."
        ),
    ),
    NarrativeBeat(
        id="first_inspection",
        phase=NarrativePhase.TESTS,
        title="The Customs Man",
        text=(
            "An inspector boards your vessel, ledger in hand. His eyes miss nothing. "
            "The nature of your cargo and the cleanness of your record decide what happens next."
        ),
    ),
    NarrativeBeat(
        id="rival_encounter",
        phase=NarrativePhase.TESTS,
        title="A Familiar Sail",
        text=(
            "You spot a ship you recognize — another captain working the same routes, "
            "chasing the same margins. The sea is big, but the profitable corners of it aren't."
        ),
        flavor="Competition sharpens instinct. Watch what others trade and find the gaps.",
    ),
    NarrativeBeat(
        id="mentor_wisdom",
        phase=NarrativePhase.TESTS,
        title="Words from an Old Hand",
        text=(
            "An old captain shares a drink with you in a portside tavern. "
            "\"The sea doesn't care about your plans,\" he says. "
            "\"She only respects the captains who listen.\""
        ),
        hint="Diversify your routes. Relying on one trade lane is fragile.",
    ),

    # === THE ORDEAL ===
    NarrativeBeat(
        id="cargo_seized",
        phase=NarrativePhase.ORDEAL,
        title="Seized",
        text=(
            "They took your cargo. Every crate, inspected and confiscated. "
            "Your crew watches in silence as months of work vanish into a customs warehouse. "
            "The question isn't whether you'll recover. It's whether you'll try."
        ),
    ),
    NarrativeBeat(
        id="near_bankruptcy",
        phase=NarrativePhase.ORDEAL,
        title="The Abyss",
        text=(
            "Silver: almost nothing. Provisions: running low. The crew looks at you "
            "with eyes that ask whether this is the end. "
            "Every great merchant hit bottom once. The difference is what they did next."
        ),
        hint="Small trades, short routes. Rebuild from the ground up. The market always has opportunity.",
    ),
    NarrativeBeat(
        id="contract_failed",
        phase=NarrativePhase.ORDEAL,
        title="Broken Promise",
        text=(
            "The deadline passed. The goods never arrived. Your name is mud at the exchange, "
            "and the trust you built evaporates like morning fog. "
            "Reputation is the hardest thing to rebuild."
        ),
    ),

    # === THE REWARD ===
    NarrativeBeat(
        id="first_big_contract",
        phase=NarrativePhase.REWARD,
        title="The Big Score",
        text=(
            "A contract worth more than everything you've earned so far. "
            "The kind of deal that turns a trader into a merchant house. "
            "All those small runs were preparation for this moment."
        ),
    ),
    NarrativeBeat(
        id="east_indies_arrival",
        phase=NarrativePhase.REWARD,
        title="The Spice Quarter",
        text=(
            "The East Indies. Every merchant's dream, every navigator's test. "
            "The air smells of spice and possibility. Silk and porcelain fill warehouses "
            "that stretch to the horizon. You've arrived."
        ),
    ),
    NarrativeBeat(
        id="south_seas_discovery",
        phase=NarrativePhase.REWARD,
        title="Beyond the Charts",
        text=(
            "The South Seas. Your charts have blank spaces here. "
            "Pearls gleam in the shallows, volcanic islands smoke on the horizon, "
            "and kings you've never heard of trade in goods the Old World craves. "
            "This is the frontier."
        ),
    ),
    NarrativeBeat(
        id="wealth_milestone",
        phase=NarrativePhase.REWARD,
        title="A Captain of Substance",
        text=(
            "Your silver reserves have crossed a line that separates traders from merchants. "
            "Ships, warehouses, contracts — you're no longer surviving. You're building."
        ),
    ),

    # === THE RETURN ===
    NarrativeBeat(
        id="trade_house",
        phase=NarrativePhase.THE_RETURN,
        title="The House You Built",
        text=(
            "Brokers in three regions know your name. Warehouses hold your goods "
            "in ports you haven't visited in weeks. Contracts arrive without you asking. "
            "You didn't just trade — you built something that will outlast you."
        ),
    ),
    NarrativeBeat(
        id="galleon_master",
        phase=NarrativePhase.THE_RETURN,
        title="Master of the Long Haul",
        text=(
            "Your galleon cuts through waters that would sink lesser ships. "
            "Routes that terrified you as a sloop captain are now your daily bread. "
            "The sea hasn't changed. You have."
        ),
    ),
    NarrativeBeat(
        id="five_regions",
        phase=NarrativePhase.THE_RETURN,
        title="The Known World",
        text=(
            "You've traded in every region the maps can show. From the Mediterranean "
            "to the South Seas, from the North Atlantic to the East Indies. "
            "Few captains can say they've seen it all. You can."
        ),
    ),

    # === CULTURAL BEATS ===
    NarrativeBeat(
        id="cultural_awakening",
        phase=NarrativePhase.THRESHOLD,
        title="More Than Ledgers",
        text=(
            "The world is bigger than your ledger. Every port has a story older than "
            "your ship. Every good you carry means something to someone beyond its price."
        ),
        flavor="You begin to see the cultures behind the commerce.",
        hint="Watch for cultural events at sea — they reveal the world's personality.",
    ),
    NarrativeBeat(
        id="festival_trader",
        phase=NarrativePhase.TESTS,
        title="Festival Fortune",
        text=(
            "The market swells with festival crowds. Prices soar, competition is fierce, "
            "and the locals remember who traded fairly during the celebration. "
            "Commerce and culture are the same thing here."
        ),
    ),
    NarrativeBeat(
        id="sacred_cargo",
        phase=NarrativePhase.TESTS,
        title="What They Revere",
        text=(
            "You carry what they revere. Handle it with care — this cargo is worth "
            "more than silver to the people who receive it. Your standing grows "
            "not because you traded well, but because you traded right."
        ),
        hint="Sacred goods earn standing bonuses in their home regions.",
    ),
    NarrativeBeat(
        id="forbidden_trade",
        phase=NarrativePhase.ORDEAL,
        title="The Weight of Taboo",
        text=(
            "They didn't say anything when you sold. But the silence was heavy. "
            "You've broken a cultural rule, and customs heat rises. "
            "Some profits cost more than silver."
        ),
    ),
    NarrativeBeat(
        id="cultural_bridge",
        phase=NarrativePhase.REWARD,
        title="Bridge Between Worlds",
        text=(
            "You belong everywhere and nowhere. The merchant who speaks every tongue "
            "and respects every custom is trusted by all. "
            "Three regions greet you as one of their own."
        ),
    ),
    NarrativeBeat(
        id="festival_patron",
        phase=NarrativePhase.REWARD,
        title="Friend of the Festivals",
        text=(
            "Word spreads along the trade routes: you are a friend of the festivals. "
            "Not just a buyer who arrives when prices rise, but a captain who "
            "respects the celebration. The ports remember."
        ),
    ),
    NarrativeBeat(
        id="the_known_world_culture",
        phase=NarrativePhase.THE_RETURN,
        title="A Citizen of the Sea",
        text=(
            "From the columned exchanges of the Mediterranean to the coral thrones "
            "of the South Seas, you've seen how every people makes meaning from trade. "
            "Commerce isn't just numbers. It's the story of how strangers become neighbors."
        ),
    ),
    NarrativeBeat(
        id="proverb_collector",
        phase=NarrativePhase.THE_RETURN,
        title="Wisdom of the Ports",
        text=(
            "Every port taught you something. You carry their wisdom like ballast — "
            "invisible, but it keeps you steady. The proverbs of twenty harbors "
            "live in your captain's log."
        ),
    ),

    # === SEASONAL BEATS ===
    NarrativeBeat(
        id="first_winter",
        phase=NarrativePhase.TESTS,
        title="The Cold Season",
        text=(
            "Winter closes in. The northern ports grow quiet and the sea turns grey. "
            "Experienced captains planned for this — they stocked medicines and tea "
            "when prices were low. The unprepared pay winter rates."
        ),
        hint="Watch the seasons. Buy goods when abundant, sell when scarce.",
    ),
    NarrativeBeat(
        id="monsoon_survivor",
        phase=NarrativePhase.TESTS,
        title="Through the Monsoon",
        text=(
            "The monsoon season tried to swallow your ship whole. Rain so heavy "
            "it felt solid, waves that blocked out the sky. But you kept the crew alive "
            "and the cargo dry. The East Indies respect a captain who dares the monsoon."
        ),
    ),
    NarrativeBeat(
        id="harvest_trader",
        phase=NarrativePhase.REWARD,
        title="Riding the Harvest",
        text=(
            "You timed it perfectly. When the harvest flooded the market with cheap grain "
            "and cotton, you were there to buy. When winter drove demand through the roof, "
            "you were there to sell. The calendar is a captain's secret weapon."
        ),
    ),
    NarrativeBeat(
        id="four_seasons_captain",
        phase=NarrativePhase.THE_RETURN,
        title="Captain for All Seasons",
        text=(
            "You've sailed through spring calms and winter gales, monsoon fury and "
            "autumn harvests. The sea has shown you every face it has. "
            "You trade with the rhythm of the world, not against it."
        ),
    ),

    # === PIRATE / UNDERWORLD BEATS ===
    NarrativeBeat(
        id="first_contraband",
        phase=NarrativePhase.THRESHOLD,
        title="Crossing the Line",
        text=(
            "You bought something the law says you shouldn't have. It sits in your "
            "hold like a secret — valuable, dangerous, and impossible to un-know. "
            "The legitimate world just got a little smaller."
        ),
        hint="Contraband can only be sold at BLACK_MARKET ports. Plan your route carefully.",
    ),
    NarrativeBeat(
        id="underworld_contact",
        phase=NarrativePhase.TESTS,
        title="A Name in the Dark",
        text=(
            "Word travels in the underworld. A pirate faction knows your name — "
            "not as prey, but as someone worth talking to. "
            "The line between trader and smuggler just blurred."
        ),
    ),
    NarrativeBeat(
        id="pirate_deal",
        phase=NarrativePhase.TESTS,
        title="Trading with Wolves",
        text=(
            "You traded with a pirate captain on the open sea. No port, no witnesses, "
            "no manifest. Just two captains, a price, and a handshake. "
            "The underworld does business differently."
        ),
    ),
    NarrativeBeat(
        id="first_duel_win",
        phase=NarrativePhase.TESTS,
        title="Blood and Steel",
        text=(
            "Your blade found its mark. The pirate captain yielded, and for a "
            "heartbeat the world narrowed to two people and a single truth: "
            "you earned what you carry. The crew looks at you differently now."
        ),
    ),
    NarrativeBeat(
        id="nemesis_born",
        phase=NarrativePhase.ORDEAL,
        title="A Grudge on the Water",
        text=(
            "A pirate captain remembers you. Not as a trade partner or a neutral ship — "
            "as an enemy. They'll be watching for your sails, and next time, "
            "the conversation starts with steel."
        ),
    ),
    NarrativeBeat(
        id="faction_trusted",
        phase=NarrativePhase.REWARD,
        title="The Shadow's Trust",
        text=(
            "A pirate faction trusts you completely. Their captains greet you as an ally, "
            "their ports treat you as family. You've earned what money alone can't buy: "
            "a place in the underworld's inner circle."
        ),
    ),
    NarrativeBeat(
        id="duel_master",
        phase=NarrativePhase.REWARD,
        title="Blade of the Sea",
        text=(
            "Five captains have felt your steel. Your name is spoken with respect "
            "in every pirate port and with fear on every patrol ship. "
            "The blade is part of who you are now."
        ),
    ),
    NarrativeBeat(
        id="shadow_master",
        phase=NarrativePhase.THE_RETURN,
        title="Lord of the Grey",
        text=(
            "Three factions count you as a friend. The underworld's politics flow "
            "through your hold as surely as the legitimate trade. You've built something "
            "no customs inspector can confiscate: a network that spans every shadow port "
            "in the Known World."
        ),
    ),

    # === FACTION POLITICS BEATS ===
    NarrativeBeat(
        id="faction_spillover",
        phase=NarrativePhase.TESTS,
        title="The Price of Friends",
        text=(
            "You helped one faction, and another noticed. In the underworld, "
            "every friendship casts a shadow. The enemies of your friends are now "
            "watching you with different eyes."
        ),
        hint="Standing with one faction affects your reputation with their rivals and enemies.",
    ),
    NarrativeBeat(
        id="vendetta_declared",
        phase=NarrativePhase.ORDEAL,
        title="Blood in the Ledger",
        text=(
            "A faction has declared vendetta. Your alliance with their enemy "
            "has made you a target — not just a stranger, but a marked captain. "
            "Their ships will hunt you in their waters. Choose your routes carefully."
        ),
    ),
    NarrativeBeat(
        id="political_survivor",
        phase=NarrativePhase.REWARD,
        title="Walking the Wire",
        text=(
            "You've navigated the underworld's politics without being destroyed by them. "
            "Trade partners on one side, enemies on the other, and you in the middle — "
            "still sailing, still trading, still alive. That's an achievement few can claim."
        ),
    ),
    NarrativeBeat(
        id="faction_diplomat",
        phase=NarrativePhase.THE_RETURN,
        title="The Pirate's Diplomat",
        text=(
            "Factions that hate each other both trust you. You've done what no "
            "navy, no governor, no merchant guild has managed: earned standing "
            "on both sides of a pirate war. The sea's politics flow through you."
        ),
    ),
]

_BEATS_BY_ID: dict[str, NarrativeBeat] = {b.id: b for b in _BEATS}


# ---------------------------------------------------------------------------
# Evaluation — check game state, fire beats
# ---------------------------------------------------------------------------

def evaluate_narrative(
    state: NarrativeState,
    captain: "Captain",
    world: "WorldState",
    board: "ContractBoard",
    infra: "InfrastructureState",
    ledger: "ReceiptLedger",
    current_port_id: str | None = None,
    events_this_turn: list | None = None,
) -> list[NarrativeBeat]:
    """Check all unfired beats against current game state. Returns newly fired beats."""
    fired = set(state.fired)
    newly_fired = []

    def _fire(beat_id: str, port_id: str = "", region: str = "") -> None:
        if beat_id not in fired and beat_id in _BEATS_BY_ID:
            beat = _BEATS_BY_ID[beat_id]
            newly_fired.append(beat)
            state.fired.append(beat_id)
            state.journal.append(JournalEntry(
                beat_id=beat_id,
                day=world.day,
                port_id=port_id or (current_port_id or ""),
                region=region,
            ))
            fired.add(beat_id)

    port = world.ports.get(current_port_id) if current_port_id else None
    region = port.region if port else ""

    # === THE CALL ===
    if ledger.total_sells > 0:
        _fire("first_trade", region=region)

    from portlight.engine.models import VoyageStatus
    if world.voyage and world.voyage.status != VoyageStatus.IN_PORT:
        _fire("first_voyage")

    if ledger.net_profit > 0:
        _fire("first_profit")

    # === CROSSING THE THRESHOLD ===
    regions_visited = set()
    for r in ledger.receipts:
        p = world.ports.get(r.port_id)
        if p:
            regions_visited.add(p.region)
    if len(regions_visited) >= 2:
        _fire("new_region", region=region)

    if any(o.outcome_type in ("completed", "completed_bonus") for o in board.completed):
        _fire("first_contract")

    from portlight.content.ships import SHIPS
    if captain.ship:
        tmpl = SHIPS.get(captain.ship.template_id)
        if tmpl and tmpl.ship_class.value != "sloop":
            _fire("ship_upgrade")

    # === TESTS ===
    if events_this_turn:
        from portlight.engine.voyage import EventType
        for evt in events_this_turn:
            if evt.event_type == EventType.STORM:
                _fire("survived_storm")
            elif evt.event_type == EventType.PIRATES:
                _fire("survived_pirates")
            elif evt.event_type == EventType.INSPECTION:
                _fire("first_inspection")

    # Rival encounter: triggers after 20+ trades
    if len(ledger.receipts) >= 20:
        _fire("rival_encounter")

    # Mentor: triggers after visiting 3+ ports
    ports_visited = {r.port_id for r in ledger.receipts}
    if len(ports_visited) >= 3:
        _fire("mentor_wisdom")

    # === THE ORDEAL ===
    # Cargo seized (check reputation incidents)
    for inc in captain.standing.recent_incidents:
        if "seizure" in inc.incident_type.lower() or "seize" in inc.description.lower():
            _fire("cargo_seized")
            break

    if captain.silver < 50 and world.day > 10:
        _fire("near_bankruptcy")

    failed_contracts = [o for o in board.completed if o.outcome_type in ("expired", "abandoned")]
    if failed_contracts:
        _fire("contract_failed")

    # === THE REWARD ===
    successful = [o for o in board.completed if "completed" in o.outcome_type]
    big_contracts = [o for o in successful if o.silver_delta >= 500]
    if big_contracts:
        _fire("first_big_contract")

    if port and port.region == "East Indies" and "east_indies_arrival" not in fired:
        _fire("east_indies_arrival", region="East Indies")

    if port and port.region == "South Seas" and "south_seas_discovery" not in fired:
        _fire("south_seas_discovery", region="South Seas")

    if captain.silver >= 2000:
        _fire("wealth_milestone")

    # === THE RETURN ===
    broker_regions = set()
    for b in infra.brokers:
        if b.active:
            broker_regions.add(b.region)
    if len(broker_regions) >= 3:
        _fire("trade_house")

    if captain.ship:
        tmpl = SHIPS.get(captain.ship.template_id)
        if tmpl and tmpl.ship_class.value in ("galleon", "man_of_war"):
            _fire("galleon_master")

    standing_regions = {r for r, v in captain.standing.regional_standing.items() if v >= 5}
    if len(standing_regions) >= 5:
        _fire("five_regions")

    # === CULTURAL BEATS ===
    culture = world.culture

    # Cultural awakening: first cultural encounter at sea
    if culture.cultural_encounters >= 1:
        _fire("cultural_awakening")

    # Festival trader: traded during a festival (check if in port during active festival)
    if culture.active_festivals and current_port_id:
        for af in culture.active_festivals:
            if af.port_id == current_port_id and ledger.total_sells > 0:
                _fire("festival_trader")
                break

    # Sacred cargo: checked externally when selling sacred goods (fired via culture_engine)
    # We check if the beat should fire based on standing gains
    if events_this_turn:
        from portlight.engine.voyage import EventType
        for evt in events_this_turn:
            if evt.event_type in (
                EventType.FOREIGN_VESSEL, EventType.CULTURAL_WATERS,
                EventType.SEA_CEREMONY, EventType.WHALE_SIGHTING,
                EventType.LIGHTHOUSE, EventType.MUSICIAN_ABOARD,
                EventType.DRIFTING_OFFERING, EventType.STAR_NAVIGATION,
            ):
                # Record the cultural encounter for awakening beat
                pass  # Already counted in culture_engine

    # Cultural bridge: standing 15+ in 3 regions
    high_standing = {r for r, v in captain.standing.regional_standing.items() if v >= 15}
    if len(high_standing) >= 3:
        _fire("cultural_bridge")

    # Festival patron: lifetime festival arrivals (tracked in CulturalState)
    if culture.festivals_visited >= 3:
        _fire("festival_patron")

    # Known world culture: cultural encounters in all 5 regions
    if len(culture.regions_entered) >= 5 and culture.cultural_encounters >= 5:
        _fire("the_known_world_culture")

    # Proverb collector: visited 15+ unique ports
    if len(culture.port_visits) >= 15:
        _fire("proverb_collector")

    # === SEASONAL BEATS ===
    from portlight.engine.models import Season, get_season
    current_season = get_season(world.day)

    # First winter: fire when player experiences their first winter
    if current_season == Season.WINTER and world.day >= 271:
        _fire("first_winter")

    # Monsoon survivor: sailed in East Indies during summer (monsoon)
    if current_season == Season.SUMMER and region == "East Indies":
        _fire("monsoon_survivor")

    # Harvest trader: traded in autumn (harvest season) with good profit
    if current_season == Season.AUTUMN and ledger.net_profit >= 500:
        _fire("harvest_trader")

    # Four seasons captain: played through all 4 seasons (day > 360)
    if world.day > 360:
        _fire("four_seasons_captain")

    # === PIRATE / UNDERWORLD BEATS ===
    pirates = world.pirates
    uw_standing = captain.standing.underworld_standing

    # First contraband: player has contraband in cargo
    has_contraband = any(
        c.good_id in ("opium", "black_powder", "stolen_cargo")
        for c in captain.cargo
    )
    if has_contraband:
        _fire("first_contraband")

    # Underworld contact: standing 10+ with any faction
    if any(v >= 10 for v in uw_standing.values()):
        _fire("underworld_contact")

    # Pirate deal: at-sea trade recorded in encounter history
    if any(e.outcome == "trade" for e in pirates.encounters):
        _fire("pirate_deal")

    # First duel win
    if pirates.duels_won >= 1:
        _fire("first_duel_win")

    # Nemesis born
    if pirates.nemesis_id is not None:
        _fire("nemesis_born")

    # Faction trusted: standing 50+ with any faction
    if any(v >= 50 for v in uw_standing.values()):
        _fire("faction_trusted")

    # Duel master: 5+ duel wins
    if pirates.duels_won >= 5:
        _fire("duel_master")

    # Shadow master: standing 25+ with 3+ factions
    factions_with_standing = sum(1 for v in uw_standing.values() if v >= 25)
    if factions_with_standing >= 3:
        _fire("shadow_master")

    # === FACTION POLITICS BEATS ===
    from portlight.engine.underworld import check_vendetta

    # Spillover: standing 15+ with any faction (they have enemies who noticed)
    if any(v >= 15 for v in uw_standing.values()):
        _fire("faction_spillover")

    # Vendetta declared: any faction holds a vendetta
    for fid in uw_standing:
        vendettas = check_vendetta(uw_standing, fid)
        if vendettas:
            _fire("vendetta_declared")
            break

    # Political survivor: standing 10+ with 2+ factions that are enemies of each other
    from portlight.content.factions import get_enemies
    factions_above_10 = [fid for fid, v in uw_standing.items() if v >= 10]
    for i, a in enumerate(factions_above_10):
        for b in factions_above_10[i + 1:]:
            enemies_of_a = get_enemies(a)
            if b in enemies_of_a:
                _fire("political_survivor")

    # Faction diplomat: standing 25+ with 2 factions that are hostile to each other
    factions_above_25 = [fid for fid, v in uw_standing.items() if v >= 25]
    for i, a in enumerate(factions_above_25):
        for b in factions_above_25[i + 1:]:
            enemies_of_a = get_enemies(a)
            if b in enemies_of_a:
                _fire("faction_diplomat")

    return newly_fired
