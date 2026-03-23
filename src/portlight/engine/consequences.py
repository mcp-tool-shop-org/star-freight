"""Consequence engine — your past decisions shape your future encounters.

Every trade, every duel, every broken contract, every faction alliance
is tracked. This engine reads that history and generates encounters that
feel PERSONAL. Not random — earned.

Design principles:
  1. Consequences should surprise the player with how much the world remembers
  2. Good decisions should produce rewards that feel earned, not given
  3. Bad decisions should produce threats that feel fair, not punitive
  4. The player should learn: in this world, EVERYTHING counts

Two categories:
  - Sea consequences: encounters during voyages
  - Port consequences: encounters when docking

Contract:
  check_sea_consequences(world, route, ledger, board, rng) -> list[Consequence]
  check_port_consequences(world, port_id, ledger, board, rng) -> list[Consequence]
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from portlight.engine.contracts import ContractBoard
    from portlight.engine.models import Route, WorldState
    from portlight.receipts.models import ReceiptLedger


@dataclass
class Consequence:
    """A consequence encounter triggered by the player's history."""
    id: str
    category: str                    # "sea" or "port"
    trigger: str                     # what historical fact triggered this
    text: str                        # what the player sees
    effect_type: str                 # "reward", "threat", "information", "neutral"
    silver_delta: int = 0
    standing_delta: int = 0          # regional standing change
    heat_delta: int = 0
    trust_delta: int = 0
    region: str = ""                 # which region is affected


# ---------------------------------------------------------------------------
# Sea Consequences
# ---------------------------------------------------------------------------

def check_sea_consequences(
    world: "WorldState",
    route: "Route | None",
    ledger: "ReceiptLedger",
    board: "ContractBoard",
    rng: random.Random,
) -> list[Consequence]:
    """Check for history-based encounters at sea.

    ~15% chance of firing per day. Only one consequence per day maximum.
    """
    if rng.random() > 0.15:
        return []

    captain = world.captain
    consequences: list[Consequence] = []
    dest_port = world.ports.get(world.voyage.destination_id) if world.voyage else None
    dest_region = dest_port.region if dest_port else "Mediterranean"

    # --- REWARD: Merchant you traded fairly with sends a gift ---
    if ledger.total_sells >= 10 and captain.standing.commercial_trust >= 10:
        if rng.random() < 0.3:
            silver_gift = rng.randint(10, 30)
            consequences.append(Consequence(
                id="fair_trader_gift",
                category="sea",
                trigger=f"Completed {ledger.total_sells} honest trades with trust {captain.standing.commercial_trust}",
                text=(
                    f"A merchant vessel approaches flying a friendly flag. The captain shouts: "
                    f"'You traded fairly with us at port — my employer sends {silver_gift} silver "
                    f"as a thank-you and an invitation to do business again.' A crate of silver "
                    f"is swung across on a rope."
                ),
                effect_type="reward",
                silver_delta=silver_gift,
            ))
            return consequences

    # --- THREAT: Faction you've angered sends a warning ---
    for fid, standing in captain.standing.underworld_standing.items():
        if standing < 5 and rng.random() < 0.4:
            from portlight.content.factions import FACTIONS
            faction = FACTIONS.get(fid)
            if faction and dest_region in faction.territory_regions:
                consequences.append(Consequence(
                    id="faction_warning",
                    category="sea",
                    trigger=f"Low standing ({standing}) with {faction.name} in their territory",
                    text=(
                        f"A ship flying the {faction.name}'s colors crosses your bow — close, "
                        f"deliberate, threatening. A signal flag spells out: 'UNWELCOME.' "
                        f"They don't attack. Not today. But the message is clear: you are being "
                        f"watched, and the next encounter might not end with a warning."
                    ),
                    effect_type="threat",
                    heat_delta=2,
                    region=dest_region,
                ))
                return consequences

    # --- REWARD: Pirate captain you spared remembers ---
    if world.pirates.duels_won >= 1:
        for encounter in world.pirates.encounters:
            if encounter.outcome == "duel_win" and rng.random() < 0.2:
                from portlight.content.factions import PIRATE_CAPTAINS
                pirate = PIRATE_CAPTAINS.get(encounter.captain_id)
                if pirate:
                    consequences.append(Consequence(
                        id="spared_pirate_gratitude",
                        category="sea",
                        trigger=f"Won a duel against {pirate.name} and let them live",
                        text=(
                            f"A familiar sail on the horizon — {pirate.name}'s ship. Your crew "
                            f"tenses. But instead of approaching, the ship changes course — "
                            f"away from you, revealing a navy patrol that was behind them. "
                            f"They spotted the patrol and warned you by drawing its attention. "
                            f"A debt repaid."
                        ),
                        effect_type="reward",
                    ))
                    return consequences

    # --- THREAT: Nemesis is hunting you ---
    if world.pirates.nemesis_id:
        if rng.random() < 0.3:
            from portlight.content.factions import PIRATE_CAPTAINS
            nemesis = PIRATE_CAPTAINS.get(world.pirates.nemesis_id)
            if nemesis:
                consequences.append(Consequence(
                    id="nemesis_shadow",
                    category="sea",
                    trigger=f"Nemesis {nemesis.name} is tracking you",
                    text=(
                        f"Your lookout spots a ship matching your course — same heading, same "
                        f"speed, keeping distance. {nemesis.name}'s vessel. They're not attacking. "
                        f"They're FOLLOWING. Learning your route, your schedule, your patterns. "
                        f"The next time they appear, they'll be ready."
                    ),
                    effect_type="threat",
                ))
                return consequences

    # --- INFORMATION: A captain you've traded with shares intelligence ---
    if len(ledger.receipts) >= 20 and rng.random() < 0.25:
        # Pick a port you've traded at and share a market tip
        traded_ports = {r.port_id for r in ledger.receipts}
        if traded_ports:
            tip_port = rng.choice(list(traded_ports))
            port_obj = world.ports.get(tip_port)
            if port_obj and port_obj.market:
                slot = rng.choice(port_obj.market)
                if slot.stock_current < slot.stock_target * 0.5:
                    consequences.append(Consequence(
                        id="trade_intelligence",
                        category="sea",
                        trigger=f"Traded at {len(traded_ports)} ports, earned trust",
                        text=(
                            f"A passing merchant hails you: 'Captain! We've traded before — "
                            f"at {port_obj.name}, yes? I have news: {slot.good_id} is running "
                            f"scarce there. Prices will climb. If you have any, now's the time.' "
                            f"He tips his hat and sails on. Information freely given — because "
                            f"you earned it with honest trade."
                        ),
                        effect_type="information",
                    ))
                    return consequences

    # --- THREAT: Contract you broke haunts you ---
    failed_contracts = [o for o in board.completed if o.outcome_type in ("expired", "abandoned")]
    if failed_contracts and rng.random() < 0.3:
        failed = rng.choice(failed_contracts)
        consequences.append(Consequence(
            id="broken_contract_haunts",
            category="sea",
            trigger=f"Failed contract: {failed.summary}",
            text=(
                "A merchant vessel pulls alongside. The captain's face is stone. "
                "'You were supposed to deliver. You didn't. My employer lost silver. "
                "I lost my commission. Word travels, Captain. The exchanges are "
                "talking about you — and what they're saying isn't good.' He turns "
                "away without waiting for a response."
            ),
            effect_type="threat",
            trust_delta=-1,
        ))
        return consequences

    # --- REWARD: High standing in a region brings escort offers ---
    regional_standing = captain.standing.regional_standing.get(dest_region, 0)
    if regional_standing >= 15 and rng.random() < 0.2:
        consequences.append(Consequence(
            id="regional_escort",
            category="sea",
            trigger=f"High standing ({regional_standing}) in {dest_region}",
            text=(
                f"A patrol vessel from {dest_region} approaches — not to inspect, but to "
                f"escort. 'Captain, your reputation precedes you. We'll see you safely to "
                f"port.' They fall in alongside. For the next stretch, the danger drops "
                f"to zero. This is what standing buys: not immunity, but protection."
            ),
            effect_type="reward",
        ))
        return consequences

    # --- THREAT: Contraband history catches up ---
    contraband_trades = sum(
        1 for r in ledger.receipts if r.good_id in ("opium", "black_powder", "stolen_cargo")
    )
    if contraband_trades >= 3 and captain.standing.customs_heat.get(dest_region, 0) >= 10:
        if rng.random() < 0.3:
            consequences.append(Consequence(
                id="contraband_reputation",
                category="sea",
                trigger=f"Traded contraband {contraband_trades} times with heat {captain.standing.customs_heat.get(dest_region, 0)}",
                text=(
                    "A customs cutter appears from behind an island — fast, purposeful, "
                    "heading straight for you. They don't inspect. They circle your ship "
                    "slowly, noting your hull number, your heading, your cargo profile. "
                    "Then they leave. But now they know your route. Next time, the "
                    "inspection will be thorough."
                ),
                effect_type="threat",
                heat_delta=3,
                region=dest_region,
            ))
            return consequences

    # --- NEUTRAL: Crew you dismissed remembers you ---
    if captain.day > 100 and rng.random() < 0.15:
        consequences.append(Consequence(
            id="old_crew_memory",
            category="sea",
            trigger=f"Veteran captain (day {captain.day})",
            text=(
                "A fishing boat hails you. At the tiller, a face you half-recognize — "
                "a sailor who served under you months ago. He waves. 'Captain! Still "
                "sailing! I tell everyone I served with you. Some are impressed. Some "
                "aren't.' He laughs and heads on. The sea is full of people who "
                "remember you."
            ),
            effect_type="neutral",
        ))
        return consequences

    return consequences


# ---------------------------------------------------------------------------
# Port Consequences
# ---------------------------------------------------------------------------

def check_port_consequences(
    world: "WorldState",
    port_id: str,
    ledger: "ReceiptLedger",
    board: "ContractBoard",
    rng: random.Random,
) -> list[Consequence]:
    """Check for history-based encounters when arriving at a port.

    ~25% chance of firing per arrival. Only one consequence per arrival.
    """
    if rng.random() > 0.25:
        return []

    captain = world.captain
    port = world.ports.get(port_id)
    if port is None:
        return []

    consequences: list[Consequence] = []
    region = port.region

    # --- REWARD: Port remembers you traded well here ---
    port_trades = [r for r in ledger.receipts if r.port_id == port_id]
    if len(port_trades) >= 5:
        profitable_trades = sum(1 for r in port_trades if r.action.value == "sell")
        if profitable_trades >= 3 and rng.random() < 0.4:
            discount = rng.randint(5, 15)
            consequences.append(Consequence(
                id="loyal_customer",
                category="port",
                trigger=f"Traded {len(port_trades)} times at {port.name}",
                text=(
                    f"A dockworker recognizes your ship. 'Captain! You're back!' Word "
                    f"spreads quickly. By the time you've tied up, the harbor master has "
                    f"reduced your docking fee by {discount} silver. 'Loyal customers "
                    f"get loyal treatment,' he says. The port remembers who keeps coming back."
                ),
                effect_type="reward",
                silver_delta=discount,
            ))
            return consequences

    # --- THREAT: You abandoned a contract from this port ---
    port_failures = [
        o for o in board.completed
        if o.outcome_type in ("expired", "abandoned")
        and any(r.port_id == port_id for r in ledger.receipts)
    ]
    if port_failures and rng.random() < 0.4:
        consequences.append(Consequence(
            id="contract_shame",
            category="port",
            trigger=f"Failed contract visible at {port.name}",
            text=(
                "As you dock, you notice the market board. Your name is on it — "
                "in the 'defaulted contracts' section. The merchants at the exchange "
                "glance at you and look away. The broker's desk has a shorter list "
                "of offers today. Word travels. Trust is the hardest thing to rebuild."
            ),
            effect_type="threat",
            trust_delta=-1,
        ))
        return consequences

    # --- REWARD: Faction you're allied with offers a deal ---
    from portlight.engine.underworld import get_dominant_faction_for_region
    dominant_faction = get_dominant_faction_for_region(region)
    if dominant_faction:
        faction_standing = captain.standing.underworld_standing.get(dominant_faction, 0)
        if faction_standing >= 25 and rng.random() < 0.35:
            from portlight.content.factions import FACTIONS
            faction = FACTIONS.get(dominant_faction)
            if faction:
                silver_offer = rng.randint(20, 50)
                consequences.append(Consequence(
                    id="faction_favor",
                    category="port",
                    trigger=f"Standing {faction_standing} with {faction.name} at their port",
                    text=(
                        f"A figure in {faction.name} colors approaches as you dock. "
                        f"No introduction -- they know who you are. '{faction.name} "
                        f"appreciates your loyalty. A small token.' They press {silver_offer} "
                        f"silver into your hand. 'There's more where that came from. "
                        f"Keep trading with us.' They vanish into the crowd."
                    ),
                    effect_type="reward",
                    silver_delta=silver_offer,
                ))
                return consequences

    # --- THREAT: High heat port has extra scrutiny ---
    port_heat = captain.standing.customs_heat.get(region, 0)
    if port_heat >= 20 and rng.random() < 0.4:
        consequences.append(Consequence(
            id="heat_scrutiny",
            category="port",
            trigger=f"Customs heat {port_heat} in {region}",
            text=(
                "Before your anchor hits bottom, a customs launch is alongside. "
                "Two inspectors, not one. They don't wait for you to present a "
                "manifest — they board directly. 'Routine inspection,' the lead "
                "says, without making eye contact. It's not routine. Your reputation "
                "has preceded you."
            ),
            effect_type="threat",
            heat_delta=2,
            region=region,
        ))
        return consequences

    # --- INFORMATION: NPC from your cross-port network shares gossip ---
    if captain.standing.commercial_trust >= 8 and rng.random() < 0.3:
        from portlight.content.cross_port_networks import get_relationships_for_port
        rels = get_relationships_for_port(port_id)
        if rels:
            rel = rng.choice(rels)
            # The NPC at this port mentions their connection
            local_name = rel.npc_a_name if rel.npc_a_port == port_id else rel.npc_b_name
            remote_name = rel.npc_b_name if rel.npc_a_port == port_id else rel.npc_a_name
            remote_port = rel.npc_b_port if rel.npc_a_port == port_id else rel.npc_a_port
            remote_port_obj = world.ports.get(remote_port)
            remote_port_name = remote_port_obj.name if remote_port_obj else remote_port
            consequences.append(Consequence(
                id="network_gossip",
                category="port",
                trigger=f"Trust {captain.standing.commercial_trust}, {local_name} shares network intelligence",
                text=(
                    f"At the exchange, {local_name} pulls you aside. 'I heard from "
                    f"{remote_name} at {remote_port_name} — they mentioned your name. "
                    f"You're building a reputation, Captain. The people who matter are "
                    f"starting to notice.' A pause. 'That can be good or bad. Depends "
                    f"on what you do next.'"
                ),
                effect_type="information",
            ))
            return consequences

    # --- REWARD: Return to your home port after a long voyage ---
    try:
        from portlight.engine.captain_identity import CAPTAIN_TEMPLATES, CaptainType
        ct = CaptainType(captain.captain_type)
        template = CAPTAIN_TEMPLATES.get(ct)
        if template and template.home_port_id == port_id and captain.day > 30:
            visit_count = world.culture.port_visits.get(port_id, 0)
            if visit_count <= 2 and rng.random() < 0.5:
                consequences.append(Consequence(
                    id="homecoming",
                    category="port",
                    trigger=f"Returning to home port {port.name} after {captain.day} days",
                    text=(
                        "You're home. The harbor looks different after weeks at sea — "
                        "smaller somehow, but warmer. A dockworker you've known since "
                        "childhood spots your ship and shouts to the others. By the time "
                        "you tie up, a small crowd has gathered. You left as a captain "
                        "with a sloop and a dream. You've returned as someone the port "
                        "talks about. The feeling is... complicated."
                    ),
                    effect_type="reward",
                    standing_delta=2,
                    region=region,
                ))
                return consequences
    except (ValueError, KeyError):
        pass

    # --- NEUTRAL: First visit to a new port ---
    visit_count = world.culture.port_visits.get(port_id, 0)
    if visit_count == 0 and rng.random() < 0.5:
        consequences.append(Consequence(
            id="first_visit",
            category="port",
            trigger=f"First visit to {port.name}",
            text=(
                "Everything is new. The smells, the sounds, the way the dockworkers "
                "move — it's all different from what you know. A port you've never "
                "visited before. Every stall is a question, every face is a stranger, "
                "and every price is a test. This is why you sail: for the moment "
                "when the world shows you something you haven't seen."
            ),
            effect_type="neutral",
        ))
        return consequences

    return consequences


# ---------------------------------------------------------------------------
# Apply consequences
# ---------------------------------------------------------------------------

def apply_consequence(world: "WorldState", consequence: Consequence) -> None:
    """Apply a consequence's mechanical effects to the world state."""
    captain = world.captain

    if consequence.silver_delta != 0:
        captain.silver = max(0, captain.silver + consequence.silver_delta)

    if consequence.trust_delta != 0:
        captain.standing.commercial_trust = max(
            0, captain.standing.commercial_trust + consequence.trust_delta
        )

    if consequence.standing_delta != 0 and consequence.region:
        current = captain.standing.regional_standing.get(consequence.region, 0)
        captain.standing.regional_standing[consequence.region] = max(
            -20, current + consequence.standing_delta
        )

    if consequence.heat_delta != 0 and consequence.region:
        current = captain.standing.customs_heat.get(consequence.region, 0)
        captain.standing.customs_heat[consequence.region] = max(
            0, min(100, current + consequence.heat_delta)
        )
