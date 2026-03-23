"""Port political ecosystem — trade blocs, rivalries, and embargoes.

The 20 ports aren't just markets — they're political actors. Ports form
trade blocs based on shared interests, and these blocs have relationships
with each other. Trading consistently with one bloc builds your standing
there but can cost you elsewhere.

Design principle: port politics create ROUTE decisions. A captain allied
with the Exchange Alliance gets better prices in the Mediterranean but
pays a premium at Shadow Ports. A captain who trades with everyone pays
no premium — but earns no loyalty either.

Trade blocs:
  Exchange Alliance   — Porto Novo, Al-Manar, Silva Bay (Med establishment)
  Iron Pact           — Ironhaven, Stormwall (NA military-industrial)
  Gold Coast Compact  — Sun Harbor, Palm Cove, Iron Point, Pearl Shallows (WA)
  Silk Circle         — Jade Port, Silk Haven, Dragon's Gate (EI dynasties)
  Free Ports          — Crosswind Isle, Monsoon Reach, Thornport (neutral)
  Shadow Ports        — Corsair's Rest, Spice Narrows (black market)
  Coral Crown         — Ember Isle, Typhoon Anchorage, Coral Throne (SS kingdom)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TradeBloc:
    """A political alliance of ports with shared trade interests."""
    id: str
    name: str
    port_ids: list[str]
    description: str
    trade_philosophy: str            # how this bloc views commerce
    preferred_partners: list[str]    # bloc_ids they cooperate with
    rivals: list[str]                # bloc_ids they compete with
    hostile_to: list[str]            # bloc_ids they actively oppose
    loyalty_bonus: float             # price bonus for high-standing captains (0.05 = 5%)
    disloyalty_penalty: float        # price penalty for captains allied with hostile blocs


@dataclass(frozen=True)
class PortPoliticalProfile:
    """Political identity for a single port — its bloc, local rivalries, and rules."""
    port_id: str
    bloc_id: str
    local_rival_port: str | None     # specific port this one competes with
    rivalry_reason: str              # why they compete
    trade_embargo: list[str]         # good_ids this port refuses from rival-allied captains
    political_flavor: str            # one-liner about this port's political stance
    port_grudge: str                 # historical grievance (flavor)


@dataclass(frozen=True)
class BlocRelationship:
    """How two trade blocs view each other."""
    bloc_a: str
    bloc_b: str
    disposition: str                 # allied / neutral / rival / hostile
    description: str
    spillover: float                 # standing spillover coefficient (-1.0 to +0.5)


# ---------------------------------------------------------------------------
# Trade Blocs
# ---------------------------------------------------------------------------

TRADE_BLOCS: dict[str, TradeBloc] = {tb.id: tb for tb in [
    TradeBloc(
        id="exchange_alliance",
        name="The Exchange Alliance",
        port_ids=["porto_novo", "al_manar", "silva_bay"],
        description=(
            "The Mediterranean old guard. Three ports bound by centuries of "
            "contract law, shared weights and measures, and a mutual commitment "
            "to fair dealing. They despise smugglers and distrust the East."
        ),
        trade_philosophy="Contracts are sacred. Prices are posted. Cheats are remembered.",
        preferred_partners=["iron_pact"],
        rivals=["silk_circle"],
        hostile_to=["shadow_ports"],
        loyalty_bonus=0.08,
        disloyalty_penalty=0.10,
    ),
    TradeBloc(
        id="iron_pact",
        name="The Iron Pact",
        port_ids=["ironhaven", "stormwall"],
        description=(
            "Military-industrial alliance. Ironhaven's foundries supply Stormwall's "
            "garrison. They control the North Atlantic's weapons trade and view "
            "anyone selling weapons to pirates as a traitor."
        ),
        trade_philosophy="Strength through industry. Trade serves the fortress.",
        preferred_partners=["exchange_alliance"],
        rivals=["gold_coast"],
        hostile_to=["shadow_ports"],
        loyalty_bonus=0.06,
        disloyalty_penalty=0.12,
    ),
    TradeBloc(
        id="gold_coast",
        name="The Gold Coast Compact",
        port_ids=["sun_harbor", "palm_cove", "iron_point", "pearl_shallows"],
        description=(
            "West Africa's communal trading network. Four ports bound by kinship, "
            "shared harvests, and the principle that trade is relationship, not "
            "transaction. They distrust industrial powers and welcome all who "
            "trade honestly."
        ),
        trade_philosophy="Generosity first, then business. The coast remembers.",
        preferred_partners=["free_ports", "coral_crown"],
        rivals=["iron_pact"],
        hostile_to=[],
        loyalty_bonus=0.06,
        disloyalty_penalty=0.05,
    ),
    TradeBloc(
        id="silk_circle",
        name="The Silk Circle",
        port_ids=["jade_port", "silk_haven", "dragons_gate"],
        description=(
            "The Eastern dynasties. Ancient, hierarchical, and fiercely protective "
            "of their luxury goods. They control porcelain, silk, and the finest tea. "
            "They view Western merchants as barbarians — useful barbarians, but barbarians."
        ),
        trade_philosophy="Quality over quantity. Hierarchy governs all.",
        preferred_partners=["coral_crown"],
        rivals=["exchange_alliance"],
        hostile_to=["iron_pact"],
        loyalty_bonus=0.10,
        disloyalty_penalty=0.08,
    ),
    TradeBloc(
        id="free_ports",
        name="The Free Ports",
        port_ids=["crosswind_isle", "monsoon_reach", "thornport"],
        description=(
            "The neutrals. Three ports that refuse to join any bloc, trade with "
            "everyone, and profit from every conflict. They anger the blocs by "
            "refusing to take sides — but everyone needs a neutral ground."
        ),
        trade_philosophy="All flags fly here. No nation claims us.",
        preferred_partners=["gold_coast"],
        rivals=[],
        hostile_to=[],
        loyalty_bonus=0.03,
        disloyalty_penalty=0.0,
    ),
    TradeBloc(
        id="shadow_ports",
        name="The Shadow Ports",
        port_ids=["corsairs_rest", "spice_narrows"],
        description=(
            "The black market. Two ports outside all legitimate trade agreements. "
            "They answer to pirate factions, not merchant guilds. The legitimate "
            "blocs despise them; the smart captains use them."
        ),
        trade_philosophy="No names, no questions, no manifests.",
        preferred_partners=[],
        rivals=[],
        hostile_to=["exchange_alliance", "iron_pact"],
        loyalty_bonus=0.12,
        disloyalty_penalty=0.0,
    ),
    TradeBloc(
        id="coral_crown",
        name="The Coral Crown",
        port_ids=["ember_isle", "typhoon_anchorage", "coral_throne"],
        description=(
            "The South Seas kingdom. Three island ports under the Coral King's "
            "authority. Trade here is tribute — you give what the king demands "
            "and receive what he allows. Disrespect means exile."
        ),
        trade_philosophy="Tribute earns trade. The reef remembers.",
        preferred_partners=["gold_coast", "silk_circle"],
        rivals=[],
        hostile_to=[],
        loyalty_bonus=0.08,
        disloyalty_penalty=0.06,
    ),
]}


# ---------------------------------------------------------------------------
# Bloc Relationships
# ---------------------------------------------------------------------------

BLOC_RELATIONSHIPS: list[BlocRelationship] = [
    # Exchange Alliance relationships
    BlocRelationship("exchange_alliance", "iron_pact", "allied",
        "United by shared commitment to order, law, and recorded trade. The Alliance supplies grain; the Pact supplies iron.",
        spillover=0.3),
    BlocRelationship("exchange_alliance", "gold_coast", "neutral",
        "Distant but respectful. Cotton and dyes flow north; manufactured goods flow south.",
        spillover=0.0),
    BlocRelationship("exchange_alliance", "silk_circle", "rival",
        "The old rivalry. Both claim to be the cradle of civilization. Both want to set the terms of East-West trade.",
        spillover=-0.15),
    BlocRelationship("exchange_alliance", "free_ports", "neutral",
        "The Alliance resents their neutrality but needs their trade routes.",
        spillover=0.0),
    BlocRelationship("exchange_alliance", "shadow_ports", "hostile",
        "Smugglers undermine everything the Alliance stands for. Captains who trade at Corsair's Rest lose standing fast.",
        spillover=-0.3),
    BlocRelationship("exchange_alliance", "coral_crown", "neutral",
        "Too distant to care much. The Crown's pearls are welcome; their politics aren't.",
        spillover=0.0),

    # Iron Pact relationships
    BlocRelationship("iron_pact", "gold_coast", "rival",
        "The Pact wants West Africa's iron ore. The Compact wants fair prices, not industrial exploitation.",
        spillover=-0.1),
    BlocRelationship("iron_pact", "silk_circle", "hostile",
        "The Silk Circle bans weapons imports. The Pact's entire economy is weapons. Fundamental conflict.",
        spillover=-0.25),
    BlocRelationship("iron_pact", "free_ports", "neutral",
        "Thornport trades tea and tobacco with Ironhaven. Practical, not political.",
        spillover=0.0),
    BlocRelationship("iron_pact", "shadow_ports", "hostile",
        "Pirates arm themselves with stolen Pact weapons. The garrison takes this personally.",
        spillover=-0.3),
    BlocRelationship("iron_pact", "coral_crown", "neutral",
        "The Crown wants weapons. The Pact wants pearls. A transaction, not an alliance.",
        spillover=0.0),

    # Gold Coast relationships
    BlocRelationship("gold_coast", "silk_circle", "neutral",
        "Cotton for silk, dyes for porcelain. Distant but mutually profitable.",
        spillover=0.0),
    BlocRelationship("gold_coast", "free_ports", "allied",
        "Shared philosophy: trade is relationship, not domination. The Compact and the Free Ports understand each other.",
        spillover=0.2),
    BlocRelationship("gold_coast", "shadow_ports", "neutral",
        "The coast doesn't judge. They trade with everyone who trades honestly — even pirates, sometimes.",
        spillover=0.0),
    BlocRelationship("gold_coast", "coral_crown", "allied",
        "Kinship across the water. Pearl divers from both shores share techniques and ceremonies.",
        spillover=0.25),

    # Silk Circle relationships
    BlocRelationship("silk_circle", "free_ports", "neutral",
        "The Circle tolerates neutrals. Crosswind Isle is useful as a buffer zone.",
        spillover=0.0),
    BlocRelationship("silk_circle", "shadow_ports", "rival",
        "The Spice Lords at Spice Narrows are a thorn. They undercut Silk Circle prices with stolen goods.",
        spillover=-0.15),
    BlocRelationship("silk_circle", "coral_crown", "allied",
        "Ancient cultural ties. The Crown's pearls and medicines complement the Circle's silk and porcelain.",
        spillover=0.2),

    # Free Ports relationships
    BlocRelationship("free_ports", "shadow_ports", "neutral",
        "The Free Ports don't judge — but they don't protect smugglers either.",
        spillover=0.0),
    BlocRelationship("free_ports", "coral_crown", "neutral",
        "Distant. Monsoon Reach trades with the Crown occasionally, but no formal ties.",
        spillover=0.0),

    # Shadow Ports <-> Coral Crown
    BlocRelationship("shadow_ports", "coral_crown", "neutral",
        "The Crown doesn't care about your morals, only your tribute. Shadow Ports are welcome if they pay.",
        spillover=0.0),
]


# ---------------------------------------------------------------------------
# Port Political Profiles (20 ports)
# ---------------------------------------------------------------------------

PORT_POLITICS: dict[str, PortPoliticalProfile] = {pp.port_id: pp for pp in [
    # === EXCHANGE ALLIANCE ===
    PortPoliticalProfile(
        port_id="porto_novo",
        bloc_id="exchange_alliance",
        local_rival_port="al_manar",
        rivalry_reason="Both claim to be the Mediterranean's premier trading port. The grain exchange vs. the spice bazaar — centuries of competition.",
        trade_embargo=[],
        political_flavor="Porto Novo is the Alliance's heart. The Exchange Guild sets policy here.",
        port_grudge="Al-Manar once tried to impose a spice tariff on Porto Novo grain ships. Porto Novo responded by raising port fees for Al-Manar flagged vessels. The tariff lasted three days.",
    ),
    PortPoliticalProfile(
        port_id="al_manar",
        bloc_id="exchange_alliance",
        local_rival_port="porto_novo",
        rivalry_reason="The Spice Merchants' Circle wants Al-Manar to lead the Alliance, not Porto Novo. The rivalry is genteel but real.",
        trade_embargo=[],
        political_flavor="Al-Manar is the Alliance's soul — older, prouder, and convinced it should be in charge.",
        port_grudge="Porto Novo got the Alliance headquarters. Al-Manar got the better harbor. Neither has forgiven the other.",
    ),
    PortPoliticalProfile(
        port_id="silva_bay",
        bloc_id="exchange_alliance",
        local_rival_port=None,
        rivalry_reason="",
        trade_embargo=[],
        political_flavor="Silva Bay stays out of politics and builds ships. The Alliance needs them too much to push.",
        port_grudge="The Shipwrights' Brotherhood refused to build warships for the Iron Pact. Stormwall hasn't forgotten.",
    ),

    # === IRON PACT ===
    PortPoliticalProfile(
        port_id="ironhaven",
        bloc_id="iron_pact",
        local_rival_port="iron_point",
        rivalry_reason="Both export iron. Ironhaven's is refined; Iron Point's is raw and cheaper. The foundry masters resent the undercutting.",
        trade_embargo=["weapons"],  # won't sell weapons to captains who trade with Shadow Ports
        political_flavor="Ironhaven IS the Pact. The Iron Guild's word is law north of the strait.",
        port_grudge="A shipment of Ironhaven weapons was found at Corsair's Rest. The merchant who sold them was never seen again.",
    ),
    PortPoliticalProfile(
        port_id="stormwall",
        bloc_id="iron_pact",
        local_rival_port=None,
        rivalry_reason="",
        trade_embargo=[],
        political_flavor="Stormwall enforces the Pact's will. The garrison answers to the Pact, not the crown.",
        port_grudge="The garrison commander's daughter married a trader from Corsair's Rest. He hasn't spoken to her since.",
    ),

    # === GOLD COAST COMPACT ===
    PortPoliticalProfile(
        port_id="sun_harbor",
        bloc_id="gold_coast",
        local_rival_port=None,
        rivalry_reason="",
        trade_embargo=[],
        political_flavor="Sun Harbor is the Compact's voice. The Weighers speak for all four ports at trade councils.",
        port_grudge="An Iron Pact mining consortium tried to buy Iron Point. The Compact blocked it. Relations have been cool since.",
    ),
    PortPoliticalProfile(
        port_id="palm_cove",
        bloc_id="gold_coast",
        local_rival_port=None,
        rivalry_reason="",
        trade_embargo=[],
        political_flavor="Palm Cove doesn't do politics. They make rum and share it. That's their entire foreign policy.",
        port_grudge="None. Palm Cove is incapable of holding a grudge. It's a cultural impossibility.",
    ),
    PortPoliticalProfile(
        port_id="iron_point",
        bloc_id="gold_coast",
        local_rival_port="ironhaven",
        rivalry_reason="Same ore, different prices. Iron Point sells raw; Ironhaven sells refined at triple the markup. The miners feel cheated by industrial middlemen.",
        trade_embargo=[],
        political_flavor="Iron Point's miners vote with the Compact but dream of selling direct to the East.",
        port_grudge="Ironhaven called Iron Point ore 'unrefined swamp metal' at a trade fair. The Red Hand has a long memory.",
    ),
    PortPoliticalProfile(
        port_id="pearl_shallows",
        bloc_id="gold_coast",
        local_rival_port="typhoon_anchorage",
        rivalry_reason="Both export pearls. The Breath-Holders consider Typhoon Anchorage divers reckless and their pearls inferior. The feeling is mutual.",
        trade_embargo=[],
        political_flavor="Pearl Shallows guards its diving traditions fiercely. They share nothing with outsiders.",
        port_grudge="Typhoon Anchorage divers poached Pearl Shallows' reef three seasons ago. The Breath-Holders haven't spoken to the Storm Riders since.",
    ),

    # === SILK CIRCLE ===
    PortPoliticalProfile(
        port_id="jade_port",
        bloc_id="silk_circle",
        local_rival_port=None,
        rivalry_reason="",
        trade_embargo=[],
        political_flavor="Jade Port is the Circle's elder. The Kiln Masters have shaped Eastern trade policy for a thousand years.",
        port_grudge="A Western merchant once dropped a porcelain bowl. The Kiln Masters banned his entire family from trade for three generations.",
    ),
    PortPoliticalProfile(
        port_id="silk_haven",
        bloc_id="silk_circle",
        local_rival_port="jade_port",
        rivalry_reason="Silk vs. porcelain — which is the supreme art? The weavers and the potters have argued for centuries. Both are convinced they're right.",
        trade_embargo=[],
        political_flavor="Silk Haven believes art matters more than politics. They're wrong, but their silk is too good to argue with.",
        port_grudge="Jade Port once called silk 'decorated thread.' The Silk Weavers' Guild responded by weaving a tapestry depicting the Kiln Masters' ancestors as monkeys. It hangs in the Loom Quarter to this day.",
    ),
    PortPoliticalProfile(
        port_id="dragons_gate",
        bloc_id="silk_circle",
        local_rival_port=None,
        rivalry_reason="",
        trade_embargo=["weapons"],  # weapons banned by the Gate Wardens
        political_flavor="Dragon's Gate enforces the Circle's weapons ban. The Gate Wardens are the Circle's iron fist.",
        port_grudge="The Iron Wolves tried to smuggle weapons through the Gate. Fifteen Wolf sailors are still chained to the seabed.",
    ),

    # === FREE PORTS ===
    PortPoliticalProfile(
        port_id="crosswind_isle",
        bloc_id="free_ports",
        local_rival_port=None,
        rivalry_reason="",
        trade_embargo=[],
        political_flavor="Crosswind Isle is neutral or dead. The Free Port Council enforces exactly one rule: no one rules.",
        port_grudge="Someone tried to claim the isle for an eastern dynasty. Every captain in harbor trained their guns on his ship. He left.",
    ),
    PortPoliticalProfile(
        port_id="monsoon_reach",
        bloc_id="free_ports",
        local_rival_port=None,
        rivalry_reason="",
        trade_embargo=[],
        political_flavor="Monsoon Reach trades with everyone and judges no one. The Wind Temple monks believe commerce is prayer.",
        port_grudge="The Monsoon Brotherhood predicted a typhoon that saved a Silk Circle fleet. The Circle offered alliance. The monks declined. 'We read the wind, not politics.'",
    ),
    PortPoliticalProfile(
        port_id="thornport",
        bloc_id="free_ports",
        local_rival_port=None,
        rivalry_reason="",
        trade_embargo=[],
        political_flavor="Thornport is too practical for politics. They sell tea and tobacco to anyone with silver.",
        port_grudge="Stormwall once tried to tax Thornport's tea trade. Thornport stopped selling tea to soldiers. The tax lasted two weeks.",
    ),

    # === SHADOW PORTS ===
    PortPoliticalProfile(
        port_id="corsairs_rest",
        bloc_id="shadow_ports",
        local_rival_port="porto_novo",
        rivalry_reason="Corsair's Rest exists because Porto Novo's laws are too strict. Every smuggler at the Rest is a trader Porto Novo drove away.",
        trade_embargo=[],
        political_flavor="Corsair's Rest has no politics. It has silence, silver, and the understanding that names are optional.",
        port_grudge="Porto Novo's harbor master publicly burned a cargo manifest from Corsair's Rest. The Brotherhood of the Cove took his favorite ship. He got it back — without the cargo.",
    ),
    PortPoliticalProfile(
        port_id="spice_narrows",
        bloc_id="shadow_ports",
        local_rival_port="jade_port",
        rivalry_reason="The Spice Lords undercut Jade Port's legitimate spice trade with smuggled goods at lower prices. The Kiln Masters are furious.",
        trade_embargo=[],
        political_flavor="Spice Narrows is where the rules end and the real prices begin.",
        port_grudge="A Jade Port customs agent infiltrated the Narrows. The Spice Lords sent him back — alive, but with every piece of intelligence he'd gathered tattooed on his forehead.",
    ),

    # === CORAL CROWN ===
    PortPoliticalProfile(
        port_id="ember_isle",
        bloc_id="coral_crown",
        local_rival_port=None,
        rivalry_reason="",
        trade_embargo=[],
        political_flavor="Ember Isle serves the Crown but keeps its own counsel. The volcano doesn't care about politics.",
        port_grudge="The Ember Keepers refused to share their medicine recipes with the Iron Pact. 'The mountain teaches us. It didn't teach you.'",
    ),
    PortPoliticalProfile(
        port_id="typhoon_anchorage",
        bloc_id="coral_crown",
        local_rival_port="pearl_shallows",
        rivalry_reason="Pearl rivalries run deep. The Storm Riders dive deeper and in worse conditions. The Breath-Holders say they lack the sacred technique.",
        trade_embargo=[],
        political_flavor="Typhoon Anchorage obeys the Coral King but takes pride in surviving what kills everyone else.",
        port_grudge="Pearl Shallows accused Typhoon Anchorage of reef poaching. The Storm Riders responded by diving the deepest reef in the South Seas and bringing up a pearl the size of a fist. Case closed.",
    ),
    PortPoliticalProfile(
        port_id="coral_throne",
        bloc_id="coral_crown",
        local_rival_port=None,
        rivalry_reason="",
        trade_embargo=[],
        political_flavor="The Coral Throne IS the Crown. The king's word shapes trade from Ember Isle to Typhoon Anchorage.",
        port_grudge="A Western merchant refused to pay tribute. The Coral King displayed his ship's nameplate in the palace as a decoration. The merchant swam home.",
    ),
]}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def get_port_bloc(port_id: str) -> TradeBloc | None:
    """Get the trade bloc a port belongs to."""
    profile = PORT_POLITICS.get(port_id)
    if profile is None:
        return None
    return TRADE_BLOCS.get(profile.bloc_id)


def get_bloc_relationship(bloc_a: str, bloc_b: str) -> BlocRelationship | None:
    """Get relationship between two blocs (order-independent)."""
    for rel in BLOC_RELATIONSHIPS:
        if (rel.bloc_a == bloc_a and rel.bloc_b == bloc_b) or \
           (rel.bloc_a == bloc_b and rel.bloc_b == bloc_a):
            return rel
    return None


def get_port_relationship(port_a: str, port_b: str) -> str:
    """Get the political disposition between two ports.

    Returns: 'allied', 'neutral', 'rival', or 'hostile'
    """
    prof_a = PORT_POLITICS.get(port_a)
    prof_b = PORT_POLITICS.get(port_b)
    if prof_a is None or prof_b is None:
        return "neutral"

    # Same bloc = allied
    if prof_a.bloc_id == prof_b.bloc_id:
        return "allied"

    # Check bloc relationship first (hostile overrides local rivalry)
    rel = get_bloc_relationship(prof_a.bloc_id, prof_b.bloc_id)
    bloc_disposition = rel.disposition if rel else "neutral"

    # Local rival escalates neutral to rival, but doesn't downgrade hostile
    if prof_a.local_rival_port == port_b or prof_b.local_rival_port == port_a:
        if bloc_disposition in ("neutral", "rival"):
            return "rival"

    return bloc_disposition


def get_bloc_enemies(bloc_id: str) -> list[str]:
    """Get bloc_ids that are hostile to the given bloc."""
    bloc = TRADE_BLOCS.get(bloc_id)
    if bloc is None:
        return []
    return list(bloc.hostile_to)


def get_bloc_allies(bloc_id: str) -> list[str]:
    """Get bloc_ids that are allied with the given bloc."""
    allies = []
    for rel in BLOC_RELATIONSHIPS:
        if rel.disposition == "allied":
            if rel.bloc_a == bloc_id:
                allies.append(rel.bloc_b)
            elif rel.bloc_b == bloc_id:
                allies.append(rel.bloc_a)
    return allies
