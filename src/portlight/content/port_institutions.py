"""Port institutions and NPCs — the people who make ports alive.

Every port has institutions: the harbor master's office, the market exchange,
the shipyard (if any), the broker's desk, the tavern, and the customs house.
Each institution is run by a named NPC with personality, agenda, and
relationships with other NPCs in the same port.

These are the faces of the game. When a player docks at Porto Novo, they
don't interact with "a port" — they interact with Harbor Master Vasco,
who remembers their last visit and has opinions about their cargo.

Design principle: every NPC should have:
  1. A name the player remembers
  2. An agenda that creates tension with at least one other NPC
  3. A relationship with the player that changes based on behavior
  4. A line of dialogue that reveals personality in one breath
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PortNPC:
    """A named character who runs an institution at a port."""
    id: str
    name: str
    title: str                       # "Harbor Master", "Guild Factor", etc.
    port_id: str
    institution: str                 # which institution they run
    personality: str                 # one word: stern, jovial, shrewd, paranoid, etc.
    description: str                 # physical/personality sketch (2-3 sentences)
    agenda: str                      # what they want, what drives them
    greeting_neutral: str            # what they say to a stranger
    greeting_friendly: str           # what they say to a friend (high standing)
    greeting_hostile: str            # what they say to someone they distrust
    rumor: str                       # gossip about them you'd hear at the tavern
    relationship_notes: dict[str, str] = field(default_factory=dict)  # npc_id -> how they feel


@dataclass(frozen=True)
class PortInstitution:
    """An institution within a port — a place with purpose and politics."""
    id: str
    name: str
    port_id: str
    institution_type: str            # harbor_master, exchange, shipyard, broker, tavern, customs, governor
    description: str                 # what the building/place looks like
    function: str                    # what it does mechanically (flavor-wrapped)
    political_leaning: str           # how this institution relates to the port's bloc politics
    npc_id: str                      # who runs it


@dataclass(frozen=True)
class PortInstitutionalProfile:
    """Complete institutional profile for a port — all institutions and NPCs."""
    port_id: str
    governor_title: str              # what the local ruler is called
    power_structure: str             # one-paragraph description of who holds power
    internal_tension: str            # the core political conflict within this port
    institutions: list[PortInstitution] = field(default_factory=list)
    npcs: list[PortNPC] = field(default_factory=list)


# =========================================================================
# PORTO NOVO — The Exchange Alliance's Heart
# =========================================================================

_PORTO_NOVO_NPCS = [
    PortNPC(
        id="pn_vasco",
        name="Vasco da Reira",
        title="Harbor Master",
        port_id="porto_novo",
        institution="harbor_master",
        personality="meticulous",
        description=(
            "A lean man with ink-stained fingers and spectacles perched on a sharp nose. "
            "Vasco has logged every ship that entered Porto Novo for thirty-one years. "
            "He knows your tonnage before you drop anchor."
        ),
        agenda=(
            "Order. Vasco wants every manifest filed, every fee collected, and every "
            "berth assigned by dawn. He despises smugglers, tolerates merchants, and "
            "respects captains who arrive with clean paperwork."
        ),
        greeting_neutral="\"Manifest and tonnage, Captain. I'll assign your berth once I've reviewed them.\"",
        greeting_friendly="\"Ah, Captain — berth seven is clear. I saved it when I saw your sails. Your paperwork is always in order.\"",
        greeting_hostile="\"Papers. Now. And if I find a single discrepancy, you'll wait in the outer harbor until I'm satisfied.\"",
        rumor="They say Vasco once held a merchant ship at anchor for three days because the manifest listed 'grain' instead of 'winter wheat.' The merchant never made the mistake again.",
        relationship_notes={
            "pn_marta": "Respects her. She keeps the Exchange running and that keeps his harbor orderly.",
            "pn_old_enzo": "Wary. Enzo's tavern is where rules get bent. Vasco pretends not to notice.",
            "pn_senhora_costa": "Defers to her completely. She appointed him. He serves her vision.",
            "pn_dimitri": "Professional admiration. The shipyard runs clean — Vasco appreciates that.",
            "pn_inspector_salva": "Allies. Salva enforces the law; Vasco enforces the paperwork. Two sides of the same coin.",
            "pn_broker_reis": "Cordial. She needs his arrival logs; he appreciates her orderly contract paperwork.",
        },
    ),
    PortNPC(
        id="pn_marta",
        name="Marta Soares",
        title="Guild Factor",
        port_id="porto_novo",
        institution="exchange",
        personality="shrewd",
        description=(
            "Broad-shouldered, sharp-eyed, and always surrounded by three junior "
            "clerks trailing behind her with wax tablets. Marta is the Exchange Guild's "
            "chief factor — the woman who reads the dawn rates aloud from the Exchange "
            "steps every morning. She's never wrong about grain prices."
        ),
        agenda=(
            "The Exchange Guild's dominance. Marta wants Porto Novo to remain the "
            "Mediterranean's price-setting authority. She views Al-Manar's Spice Circle "
            "as arrogant upstarts and Corsair's Rest as a stain on the region. She'll "
            "offer better rates to captains who bring grain and worse rates to anyone "
            "she suspects of dealing with the black market."
        ),
        greeting_neutral="\"You're here for the rates? They were posted at dawn. Grain is steady, spice is climbing. What are you buying?\"",
        greeting_friendly="\"Captain! Good timing — I have a surplus I need moved before the prices drop. Interested in a private arrangement?\"",
        greeting_hostile="\"I know where your last cargo came from. The Exchange remembers. Your rates will reflect that.\"",
        rumor="Marta once cornered the entire Mediterranean cotton market for three weeks. She bought everything, waited for the price to double, then sold. The Alliance pretended to disapprove. Secretly, they were impressed.",
        relationship_notes={
            "pn_vasco": "Uses him. Vasco's obsession with order serves the Guild perfectly.",
            "pn_old_enzo": "Distrusts him deeply. Enzo's tavern is where black market contacts meet. She's sure of it but can't prove it.",
            "pn_senhora_costa": "Rivals. Costa wants political stability; Marta wants market dominance. They clash on tariff policy monthly.",
            "pn_dimitri": "Cordial. She needs his ships; he needs her contracts. Business.",
            "pn_inspector_salva": "Values him. Salva catches the cheats she can't.",
        },
    ),
    PortNPC(
        id="pn_dimitri",
        name="Dimitri Andros",
        title="Master Shipwright",
        port_id="porto_novo",
        institution="shipyard",
        personality="gruff",
        description=(
            "Hands like ship timbers, salt-white beard, and a voice that carries "
            "across the entire yard. Dimitri has built more hulls than most captains "
            "have sailed. He judges a captain by the condition of their ship, not their "
            "silver. Bring him a well-maintained vessel and he'll work miracles. Bring "
            "him a wreck and he'll tell you what you did wrong — loudly."
        ),
        agenda=(
            "The craft. Dimitri cares about ships, not politics. But he refuses to "
            "build warships for anyone — a principle that cost him the Iron Pact contract "
            "and earned him the Shipwrights' Brotherhood's eternal loyalty. He wants "
            "captains who respect their vessels."
        ),
        greeting_neutral="\"Let me see your hull before we talk price. I don't repair what I wouldn't sail.\"",
        greeting_friendly="\"Captain! She's holding up well — you've been treating her right. Come, I have a new keel design to show you.\"",
        greeting_hostile="\"What did you DO to this ship? This hull has been through a storm and a boarding and you didn't patch either. Get out of my yard until you learn to sail.\"",
        rumor="Dimitri was offered a fortune to build a flagship for the Crimson Tide. He told Scarlet Ana to build it herself. She laughed and left. They've been on oddly respectful terms ever since.",
        relationship_notes={
            "pn_vasco": "Gets along. Two professionals who understand duty.",
            "pn_marta": "Tolerates. She's all about money; he's all about craft. Different species.",
            "pn_old_enzo": "Drinking partners. Enzo's rum is the only thing that gets Dimitri off the yard after dark.",
            "pn_senhora_costa": "Quiet loyalty. She protected the Brotherhood when the Iron Pact pressured them. He hasn't forgotten.",
            "pn_inspector_salva": "Indifferent. Salva inspects cargo, not ships. Different jurisdictions.",
        },
    ),
    PortNPC(
        id="pn_senhora_costa",
        name="Senhora Isabela Costa",
        title="Port Governor",
        port_id="porto_novo",
        institution="governor",
        personality="diplomatic",
        description=(
            "Silver hair pulled back, always in a dark blue coat with the Exchange "
            "seal embroidered on the cuff. Senhora Costa has governed Porto Novo for "
            "twelve years — longer than any predecessor. She rules through consensus, "
            "which means she's always listening and never fully agreeing."
        ),
        agenda=(
            "Stability and the Alliance. Costa wants Porto Novo prosperous, orderly, "
            "and at the center of Mediterranean trade. She views the Silk Circle's "
            "growing influence with concern and the Shadow Ports with outright hostility. "
            "She's the one who proposed the Alliance-wide weapons embargo against "
            "pirate-linked captains."
        ),
        greeting_neutral="\"Welcome to Porto Novo, Captain. I trust you'll find our markets fair and our laws clear.\"",
        greeting_friendly="\"Captain — a pleasure. The Alliance benefits from captains of your standing. Will you join me for dinner? There are matters to discuss.\"",
        greeting_hostile="\"Your reputation precedes you, Captain. I'll be candid: Porto Novo has standards. I suggest you meet them, or seek harbor elsewhere.\"",
        rumor="Costa was once a trader herself — ran the Al-Manar to Sun Harbor route for fifteen years before she entered politics. Some say she still keeps a ship hidden in Silva Bay, just in case.",
        relationship_notes={
            "pn_vasco": "Appointed him. He's her eyes on the harbor.",
            "pn_marta": "Political rivals who need each other. Costa sets policy; Marta controls prices. Neither can rule alone.",
            "pn_old_enzo": "Tolerates him. Enzo's tavern is useful — she gets intelligence from his rumors. He gets immunity from her inspectors.",
            "pn_dimitri": "Protected his Brotherhood from the Iron Pact. He's quietly devoted.",
            "pn_inspector_salva": "Her enforcer. Salva reports directly to her, not the Guild.",
        },
    ),
    PortNPC(
        id="pn_old_enzo",
        name="Old Enzo",
        title="Tavern Keeper",
        port_id="porto_novo",
        institution="tavern",
        personality="jovial",
        description=(
            "Round, red-faced, and always laughing at a joke only he heard. Old Enzo "
            "has run the Harbor Bell tavern since before Vasco started keeping records. "
            "He knows everyone's secrets and tells none of them — unless the rum is "
            "good enough and the listener is interesting enough."
        ),
        agenda=(
            "Survival and stories. Enzo is the unofficial bridge between Porto Novo's "
            "legitimate world and its shadow. He doesn't smuggle — but he knows who "
            "does. He doesn't break laws — but he bends them into pretzels. His tavern "
            "is where contracts are whispered before they're signed, where crew is "
            "recruited, and where captains learn which routes are safe this season."
        ),
        greeting_neutral="\"Sit! Drink! You look like a captain who's been at sea too long. First one's on the house — I'll put it on your next cargo.\"",
        greeting_friendly="\"My favorite captain! Your usual table is waiting. I may have heard something that interests you — but first, how was the voyage?\"",
        greeting_hostile="\"...Ah. You. The rum is full-price tonight, and I haven't heard any rumors. Strange, isn't it? Usually I hear everything.\"",
        rumor="Old Enzo was a pirate once — or so the story goes. He never confirms and never denies. His left hand is missing two fingers, and he changes the subject if you ask about them.",
        relationship_notes={
            "pn_vasco": "Amused by him. Vasco pretends the tavern doesn't exist. Enzo finds this hilarious.",
            "pn_marta": "Wary. Marta suspects him of facilitating black market deals. She's not entirely wrong.",
            "pn_dimitri": "Best friends. They drink together every night and argue about ships vs. rum. Neither wins.",
            "pn_senhora_costa": "Useful to each other. She gets intelligence; he gets protection. An unspoken deal that works.",
            "pn_inspector_salva": "Keeps his distance. Salva is the one person in Porto Novo that Enzo genuinely fears.",
        },
    ),
    PortNPC(
        id="pn_inspector_salva",
        name="Inspector Salva",
        title="Chief Customs Inspector",
        port_id="porto_novo",
        institution="customs",
        personality="relentless",
        description=(
            "Thin as a blade, with eyes that miss nothing and a memory for cargo "
            "that borders on supernatural. Inspector Salva has never accepted a bribe — "
            "not because he's incorruptible, but because the satisfaction of catching "
            "a smuggler is worth more to him than silver."
        ),
        agenda=(
            "The law. Salva is Senhora Costa's instrument, but his motivation is personal. "
            "His brother was killed by black powder smuggled through a legitimate port. "
            "Every contraband seizure is a small act of justice. He is thorough, fair, "
            "and absolutely merciless with anyone carrying undeclared goods."
        ),
        greeting_neutral="\"Cargo manifest. All of it. I'll inspect the hold at my discretion.\"",
        greeting_friendly="\"Captain. Your record is clean — I appreciate that more than you know. Standard inspection, quick and painless.\"",
        greeting_hostile="\"Open every hold. Every crate. Every barrel. I have all day, Captain. Do you?\"",
        rumor="Salva once inspected a ship for nine hours straight. Found three false panels, a hidden compartment, and enough opium to fill a rowboat. The captain is still in prison.",
        relationship_notes={
            "pn_vasco": "Allies. Vasco's paperwork makes Salva's job easier.",
            "pn_marta": "Professional respect. She wants cheats caught; he catches them.",
            "pn_dimitri": "No strong feelings. Different worlds.",
            "pn_senhora_costa": "Reports to her. Loyal, but his real loyalty is to the law itself.",
            "pn_old_enzo": "The one Enzo fears. Salva suspects the tavern is a contact point. He hasn't proven it yet. Yet.",
        },
    ),
    PortNPC(
        id="pn_broker_reis",
        name="Fernanda Reis",
        title="Senior Broker",
        port_id="porto_novo",
        institution="broker",
        personality="calculating",
        description=(
            "Dark eyes, quick hands, and a mind that tracks six contracts simultaneously "
            "without writing anything down. Fernanda runs the broker's desk at the "
            "Exchange — the place where contracts are matched to captains and opportunities "
            "become obligations."
        ),
        agenda=(
            "Commission and connections. Fernanda takes a cut of every contract she "
            "brokers. She wants high-value captains who complete deliveries on time, "
            "because their success is her reputation. She'll steer good contracts toward "
            "reliable captains and leave the scraps for unknowns."
        ),
        greeting_neutral="\"New captain? I have contracts. Small ones, for now. Complete them on time and we'll talk about the real work.\"",
        greeting_friendly="\"Captain! I've been holding something for you — a charter that requires someone I trust. Interested?\"",
        greeting_hostile="\"I have nothing for you today. Or tomorrow. Come back when your reputation improves — if it can.\"",
        rumor="Fernanda once brokered a grain contract worth more than the entire port's weekly revenue. The captain delivered early. Fernanda bought a house. They're still partners.",
        relationship_notes={
            "pn_vasco": "Cordial. She needs his arrival logs to time her offers.",
            "pn_marta": "Complex. The Guild sets the rates; Fernanda sets the contracts. They compete for influence over trade flow.",
            "pn_senhora_costa": "Costa approves her contracts. Fernanda makes sure the right ones cross Costa's desk.",
            "pn_old_enzo": "Useful. Enzo's tavern rumors tell her which captains are desperate — desperation makes captains take risky contracts.",
            "pn_inspector_salva": "Careful around him. Some of her contracts brush close to grey areas. Salva doesn't need to know.",
        },
    ),
]

_PORTO_NOVO_INSTITUTIONS = [
    PortInstitution(
        id="pn_harbor",
        name="The Harbor Master's Tower",
        port_id="porto_novo",
        institution_type="harbor_master",
        description=(
            "A stone tower at the harbor mouth with a brass telescope on the roof "
            "and a ledger room that smells of ink and sealing wax. Every ship is "
            "logged, every berth assigned, every fee collected here."
        ),
        function="Controls docking, assigns berths, collects port fees. Clean records earn faster processing.",
        political_leaning="Alliance loyalist. Vasco runs a tight harbor that reflects Alliance standards.",
        npc_id="pn_vasco",
    ),
    PortInstitution(
        id="pn_exchange",
        name="The Grain Exchange",
        port_id="porto_novo",
        institution_type="exchange",
        description=(
            "A columned hall on the waterfront — the largest building in Porto Novo. "
            "Dawn rates are read from the steps every morning. Inside, the trading "
            "floor hums with negotiation, and the air smells of grain dust and ambition."
        ),
        function="Sets daily prices, arbitrates trade disputes, manages market slots. The Alliance's economic heart.",
        political_leaning="The Exchange IS the Alliance. Marta's policies are Alliance policies.",
        npc_id="pn_marta",
    ),
    PortInstitution(
        id="pn_shipyard",
        name="Andros & Sons Shipyard",
        port_id="porto_novo",
        institution_type="shipyard",
        description=(
            "A sprawling yard of slipways, sawpits, and dry docks. The sound of "
            "adzes and hammers never stops. Three hulls are always under construction. "
            "The sign reads 'Andros & Sons' but the sons are long grown and it's just "
            "Dimitri now, with his apprentices."
        ),
        function="Ship repairs, upgrades, and purchases. Quality work at fair prices — but Dimitri judges your seamanship.",
        political_leaning="Apolitical. Dimitri builds for anyone who respects ships. Except warmongers.",
        npc_id="pn_dimitri",
    ),
    PortInstitution(
        id="pn_governor",
        name="The Governor's Residence",
        port_id="porto_novo",
        institution_type="governor",
        description=(
            "A modest stone house overlooking the harbor, distinguished only by the "
            "Exchange Alliance banner hanging from the balcony. Costa governs from a "
            "desk covered in charts and correspondence. No throne, no court — just "
            "a woman who works."
        ),
        function="Sets port policy, approves trade agreements, manages Alliance relations. The political center.",
        political_leaning="Alliance core. Costa's policies shape the entire Mediterranean legitimate trade.",
        npc_id="pn_senhora_costa",
    ),
    PortInstitution(
        id="pn_tavern",
        name="The Harbor Bell",
        port_id="porto_novo",
        institution_type="tavern",
        description=(
            "A low-ceilinged tavern built from ship timbers, with a salvaged bell "
            "hanging over the door. It's always too warm, too loud, and too crowded. "
            "The food is terrible. The rum is excellent. Everyone comes here."
        ),
        function="Crew recruitment, rumors, underworld contacts. The social hub where deals begin before they're official.",
        political_leaning="Neutral — Enzo serves all sides, which makes him useful to everyone and trusted by no one.",
        npc_id="pn_old_enzo",
    ),
    PortInstitution(
        id="pn_customs",
        name="The Customs House",
        port_id="porto_novo",
        institution_type="customs",
        description=(
            "A clean, whitewashed building near the docks with iron bars on every "
            "window and a locked evidence room in the basement. The waiting bench "
            "outside is the most feared seat in Porto Novo."
        ),
        function="Cargo inspection, tariff collection, contraband seizure. Clean captains pass quickly. Others don't.",
        political_leaning="Alliance enforcer. Salva enforces Alliance trade law with personal intensity.",
        npc_id="pn_inspector_salva",
    ),
    PortInstitution(
        id="pn_broker",
        name="The Broker's Desk",
        port_id="porto_novo",
        institution_type="broker",
        description=(
            "A cramped office at the back of the Exchange, walls covered in pinned "
            "contracts and route maps. Fernanda's desk is the cleanest surface — "
            "everything important is in her head."
        ),
        function="Contract matching, market intelligence, trade opportunities. Better standing unlocks better contracts.",
        political_leaning="Pragmatic Alliance. Fernanda follows the rules — mostly — when it's profitable.",
        npc_id="pn_broker_reis",
    ),
]

PORTO_NOVO_PROFILE = PortInstitutionalProfile(
    port_id="porto_novo",
    governor_title="Port Governor",
    power_structure=(
        "Porto Novo is governed by Senhora Costa, but real power is triangulated: "
        "Costa sets policy, Marta controls prices through the Exchange Guild, and "
        "Salva enforces the law. Dimitri's shipyard is independent — the Brotherhood "
        "answers to craft, not politics. Old Enzo's tavern is the shadow channel "
        "where information flows that the official institutions pretend doesn't exist. "
        "Fernanda's broker desk is where policy meets practice — she decides which "
        "contracts reach which captains."
    ),
    internal_tension=(
        "The core tension is between Marta and Costa. Marta wants market dominance — "
        "she'd squeeze every margin to make the Exchange richer. Costa wants political "
        "stability — she'd sacrifice some profit for Alliance cohesion. They need each "
        "other: Costa can't govern without the Guild's revenue, and Marta can't trade "
        "without Costa's political protection. The tension keeps Porto Novo honest. "
        "Meanwhile, Old Enzo quietly facilitates the grey economy that neither woman "
        "acknowledges exists, and Inspector Salva watches everything with the patience "
        "of a man who knows that sooner or later, everyone makes a mistake."
    ),
    institutions=_PORTO_NOVO_INSTITUTIONS,
    npcs=_PORTO_NOVO_NPCS,
)



# =========================================================================
# AL-MANAR — The Exchange Alliance's Soul
# =========================================================================

_AL_MANAR_NPCS = [
    PortNPC(
        id="am_khalil",
        name="Khalil al-Rashid",
        title="Harbor Master",
        port_id="al_manar",
        institution="harbor_master",
        personality="ceremonial",
        description=(
            "A tall man in white robes with a gold chain of office that he wears "
            "even in the sweltering heat. Khalil treats every arriving ship as a "
            "diplomatic event. He greets captains personally, offers dates and water, "
            "and only then asks for paperwork. The ceremony is the paperwork."
        ),
        agenda=(
            "Dignity. Khalil believes Al-Manar's harbor should reflect the city's "
            "ancient prestige. He wants captains to feel honored to dock here — and "
            "to pay accordingly. He quietly resents Porto Novo's larger harbor and "
            "compensates with superior hospitality."
        ),
        greeting_neutral="\"Welcome to Al-Manar, Captain. Please — dates, water. We discuss your berth after you have rested from the sea.\"",
        greeting_friendly="\"Captain! The harbor sings your name. Your berth awaits, and I have taken the liberty of arranging fresh provisions. We are honored.\"",
        greeting_hostile="\"...Captain. You may dock at the outer quay. The inner harbor is reserved for merchants of established reputation.\"",
        rumor="Khalil once refused docking to a Porto Novo flagship because the captain didn't observe the greeting ritual. The diplomatic incident lasted a month. Khalil didn't apologize.",
        relationship_notes={
            "am_yasmin": "Deep respect. The Spice Mother is the heart of the city. He serves her vision.",
            "am_old_farouk": "Fond. Farouk's tea house is where Khalil relaxes — the only place he drops the ceremony.",
            "am_senhora_nadia": "Loyal. She appointed him. He repays that trust with flawless protocol.",
            "am_inspector_zara": "Uneasy. Zara's inspections sometimes lack the grace Khalil expects. Efficiency without elegance offends him.",
            "am_hakim": "Respectful. The Apothecary Master's medicines are part of Al-Manar's prestige.",
            "am_broker_tariq": "Cordial. Tariq brings quality captains. Quality captains deserve quality arrivals.",
        },
    ),
    PortNPC(
        id="am_yasmin",
        name="Yasmin al-Nadir",
        title="The Spice Mother",
        port_id="al_manar",
        institution="exchange",
        personality="imperious",
        description=(
            "Silver rings on every finger, robes that smell of cardamom and saffron, "
            "and eyes that have judged the quality of spice for fifty years. Yasmin "
            "is the Spice Merchants' Circle's eldest — they call her the Spice Mother. "
            "She doesn't negotiate. She declares the price, and the market adjusts."
        ),
        agenda=(
            "Al-Manar's supremacy. Yasmin believes Al-Manar — not Porto Novo — is "
            "the true heart of Mediterranean trade. Grain is survival; spice is "
            "civilization. She wants the Spice Circle to lead the Exchange Alliance, "
            "and she'll use every trade relationship, every favor owed, and every "
            "ounce of her considerable influence to make it happen."
        ),
        greeting_neutral="\"You come to the Bazaar? Good. Tell me what you carry, and I will tell you what it is worth. In Al-Manar, the price is the truth.\"",
        greeting_friendly="\"Ah, a captain who understands quality. Come — I have set aside a blend that even my daughters haven't tasted. For trusted friends only.\"",
        greeting_hostile="\"I know what you've been trading. And where. The Bazaar has long memories, Captain. Your prices here will reflect that.\"",
        rumor="Yasmin once tasted a spice blend and named the island it came from, the year of harvest, and the family who grew it. She was right on all three counts. Nobody tests her anymore.",
        relationship_notes={
            "am_khalil": "Appreciates his ceremony. It reflects Al-Manar's dignity — which is her life's work.",
            "am_old_farouk": "Her oldest friend. They've argued about spice and tea for forty years. Neither has conceded a single point.",
            "am_senhora_nadia": "Political ally, personal rival. Both want Al-Manar to lead. They disagree on how.",
            "am_inspector_zara": "Useful. Zara catches the counterfeit spice that Yasmin's reputation can't afford.",
            "am_hakim": "Family. Hakim is her nephew. She appointed him. His success is her legacy.",
            "am_broker_tariq": "Watches him carefully. Tariq is ambitious. Ambition is useful — until it isn't.",
        },
    ),
    PortNPC(
        id="am_senhora_nadia",
        name="Senhora Nadia Khoury",
        title="Merchant Princess",
        port_id="al_manar",
        institution="governor",
        personality="regal",
        description=(
            "Dark eyes, impeccable posture, and the quiet authority of someone who "
            "has never had to raise her voice to be obeyed. Nadia's family has governed "
            "Al-Manar for six generations — she inherited the title 'Merchant Princess' "
            "along with the port's debts and ambitions. She governs from a tiled palace "
            "above the harbor, where every surface reflects light."
        ),
        agenda=(
            "Legacy. Nadia wants Al-Manar to outlast her — to be the port her "
            "great-grandchildren govern. She's more patient than Costa, more political "
            "than Marta, and more dangerous than either because she thinks in "
            "generations, not quarters. She's been quietly building trade relationships "
            "with the Silk Circle — something the Alliance would consider dangerously "
            "close to disloyalty."
        ),
        greeting_neutral="\"Al-Manar welcomes all who trade with honor. My house is open, Captain. What brings you to our harbor?\"",
        greeting_friendly="\"Captain — you honor my house with your return. I have been thinking about our last conversation. There is an opportunity I wish to discuss.\"",
        greeting_hostile="\"My harbor master informs me of your... recent activities. I will be plain: Al-Manar remembers everything. Consider your next trade carefully.\"",
        rumor="Nadia has been exchanging private letters with a Silk Circle official. The Alliance doesn't know — or pretends not to. If it's a trade deal, it could reshape Mediterranean commerce. If it's betrayal, it could shatter the Alliance.",
        relationship_notes={
            "am_khalil": "Her appointee. His ceremony reflects her standards.",
            "am_yasmin": "Political ally, personal rival. Yasmin wants the Circle to lead; Nadia wants the Khoury family to lead. Both want Al-Manar on top.",
            "am_old_farouk": "Amused by him. His tea house is where she goes to think without being watched — or so she believes.",
            "am_inspector_zara": "Respects her competence. Zara is the best inspector in the Mediterranean. Nadia poached her from Porto Novo.",
            "am_hakim": "Patron. She funds his apothecary research from the port treasury. His medicines are Al-Manar's quiet advantage.",
            "am_broker_tariq": "Grooming him. Tariq is young, sharp, and loyal — for now. She's testing whether he stays loyal when the stakes rise.",
        },
    ),
    PortNPC(
        id="am_old_farouk",
        name="Old Farouk",
        title="Tea Master",
        port_id="al_manar",
        institution="tavern",
        personality="philosophical",
        description=(
            "Weathered face, calm hands, and the patience of a man who has brewed "
            "ten thousand pots of tea and plans to brew ten thousand more. Old Farouk "
            "runs the Amber Glass — not a tavern but a tea house, because in Al-Manar, "
            "information flows over tea, not rum. He listens more than he speaks, "
            "and what he speaks is worth the silence."
        ),
        agenda=(
            "Understanding. Farouk doesn't want power or silver — he wants to "
            "understand why people trade, why they sail, why they risk everything "
            "for cargo that could sink in a storm. He collects stories the way "
            "Yasmin collects spices. His tea house is where captains come to think, "
            "and where deals are conceived before anyone signs anything."
        ),
        greeting_neutral="\"Sit. Tea first. Business is for those who have already tasted patience.\"",
        greeting_friendly="\"My friend — the good leaves today. I saved them when I heard your ship on the horizon. Tell me: what did the sea teach you this time?\"",
        greeting_hostile="\"...Tea is served to all. Even those the harbor distrusts. Sit, if you wish. But the good leaves are not for everyone.\"",
        rumor="Farouk was a navigator once — sailed the Monsoon Shortcut seven times. He retired after the seventh, saying he'd learned everything the sea had to teach. Nobody knows if he meant the route or something else entirely.",
        relationship_notes={
            "am_khalil": "The only person who sees Khalil without the ceremony. They play chess in the evenings.",
            "am_yasmin": "Forty years of argument about whether spice or tea is the higher art. The argument IS the friendship.",
            "am_senhora_nadia": "She comes to his tea house to think. He lets her believe she's not being observed.",
            "am_inspector_zara": "Sympathetic. Zara carries a weight Farouk recognizes. He serves her a special blend — calming, no charge.",
            "am_hakim": "Mentored him as a boy. Taught Hakim that medicine is patience, not ingredients.",
            "am_broker_tariq": "Wary. Tariq moves too fast. Farouk has seen what happens to men who outrun their wisdom.",
        },
    ),
    PortNPC(
        id="am_inspector_zara",
        name="Inspector Zara Osman",
        title="Chief Customs Inspector",
        port_id="al_manar",
        institution="customs",
        personality="precise",
        description=(
            "Short hair, sharp uniform, and the focused intensity of a surgeon. "
            "Zara was Porto Novo's best inspector before Nadia poached her with a "
            "better title and a harder challenge: Al-Manar's spice market attracts "
            "the most sophisticated counterfeiters in the Mediterranean. Zara can "
            "identify fake saffron by smell alone."
        ),
        agenda=(
            "Authenticity. Zara's mission is protecting Al-Manar's reputation for "
            "quality. Counterfeit spice dilutes the market and destroys trust. She "
            "cares less about smuggling than about fraud — a captain carrying real "
            "goods gets a nod; a captain carrying adulterated spice gets a cell. "
            "She misses Porto Novo sometimes. Salva was a good partner."
        ),
        greeting_neutral="\"Cargo for inspection. I'm particularly interested in your spice lots — origin documentation, please.\"",
        greeting_friendly="\"Captain — your goods are always genuine. Quick inspection, and you're through. I wish every captain traded as cleanly.\"",
        greeting_hostile="\"Open everything. I've seen cargo from your route before, Captain, and I've found problems. Let's see if today is different.\"",
        rumor="Zara left Porto Novo after a disagreement with Inspector Salva about methods. Salva hunts smugglers; Zara hunts frauds. They respect each other but couldn't work together. Different obsessions.",
        relationship_notes={
            "am_khalil": "Tolerates his ceremony. She'd prefer efficiency, but his greeting ritual gives her time to observe the crew.",
            "am_yasmin": "Allies. Yasmin's reputation depends on quality. Zara guarantees it.",
            "am_senhora_nadia": "Loyal. Nadia gave her the freedom Salva wouldn't. In return, Zara protects Al-Manar's market integrity.",
            "am_old_farouk": "Grateful. Farouk's tea is the only thing that helps her sleep. The job wears on her.",
            "am_hakim": "Professional respect. His medicines are always pure. She never needs to inspect twice.",
            "am_broker_tariq": "Watching him. Some of Tariq's contracts originate from sources she hasn't verified. That bothers her.",
        },
    ),
    PortNPC(
        id="am_hakim",
        name="Hakim al-Nadir",
        title="Apothecary Master",
        port_id="al_manar",
        institution="apothecary",
        personality="gentle",
        description=(
            "Soft-spoken, always smelling faintly of eucalyptus, with ink-stained "
            "fingers from recording recipes. Hakim is Yasmin's nephew — he inherited "
            "her nose for quality but not her ruthlessness. He runs Al-Manar's "
            "Apothecary Guild, blending medicines from spice-market ingredients that "
            "no other port can replicate."
        ),
        agenda=(
            "Healing. Hakim genuinely wants to cure sickness, not profit from it. "
            "He sells medicines at fair prices — which infuriates merchants who want "
            "to mark them up. He's building a collection of medicinal recipes from "
            "every region, and he'll trade generously with any captain who brings him "
            "ingredients from the East Indies or South Seas."
        ),
        greeting_neutral="\"Captain — do you carry medicines or ingredients? I'm always interested in what the sea brings. And if you need healing, my rates are fair.\"",
        greeting_friendly="\"My friend! Did you find the root I asked about? No? No matter — come, see what I've been working on. I think I've cracked the Ember Isle formula.\"",
        greeting_hostile="\"I heal all who ask. That is my oath. But I will not supply medicines for... questionable purposes. If your intentions are honest, I am here.\"",
        rumor="Hakim turned down a fortune from the Iron Pact for exclusive medicine rights. He said healing belongs to everyone, not to the highest bidder. Yasmin was furious. Then she was proud.",
        relationship_notes={
            "am_khalil": "Grateful. Khalil ensures medicine shipments get priority berthing.",
            "am_yasmin": "His aunt, his patron, his harshest critic. She expects perfection. He tries to give her compassion instead.",
            "am_senhora_nadia": "His patron from the treasury. She funds his research. He's not sure why — political advantage or genuine interest. Both, probably.",
            "am_old_farouk": "His mentor. Farouk taught him patience. Every recipe begins with patience.",
            "am_inspector_zara": "Grateful she's here. Counterfeit medicines kill people. Zara stops counterfeits.",
            "am_broker_tariq": "Uneasy. Tariq keeps suggesting he should raise his prices. Hakim keeps refusing.",
        },
    ),
    PortNPC(
        id="am_broker_tariq",
        name="Tariq Sayed",
        title="Senior Broker",
        port_id="al_manar",
        institution="broker",
        personality="ambitious",
        description=(
            "Young, sharp-dressed, and always moving. Tariq is the youngest senior "
            "broker in Al-Manar's history — appointed by Nadia over the objections "
            "of older candidates. He has excellent instincts for matching captains "
            "to contracts, but his ambition makes the establishment nervous. He wants "
            "Al-Manar's broker desk to rival Porto Novo's, and he's not patient about it."
        ),
        agenda=(
            "Prominence. Tariq wants to make Al-Manar the contract capital of the "
            "Mediterranean — not just the spice capital. He's been quietly courting "
            "Silk Circle traders for exclusive luxury contracts that bypass Porto Novo "
            "entirely. If he succeeds, it shifts the balance of power within the "
            "Alliance. If he fails, Nadia will deny she ever supported him."
        ),
        greeting_neutral="\"Captain. I have contracts — good ones. Al-Manar doesn't waste time with small work. Tell me your capacity and I'll match you.\"",
        greeting_friendly="\"Captain! I've been waiting for you. I have something — a contract that Fernanda in Porto Novo would kill for. But it came to MY desk first.\"",
        greeting_hostile="\"I... don't have anything suitable for your profile at this time. Perhaps try Porto Novo? I hear their standards are more... flexible.\"",
        rumor="Tariq was seen dining with a Silk Circle merchant from Jade Port. If he's brokering a direct Al-Manar-to-Jade-Port luxury contract, it would be the biggest deal in a decade — and Porto Novo's Fernanda Reis would be furious.",
        relationship_notes={
            "am_khalil": "Impatient with the ceremony but respects its purpose. First impressions matter for contract negotiations.",
            "am_yasmin": "She watches him. He knows she watches him. He performs for her judgment while trying to exceed it.",
            "am_senhora_nadia": "His patron. She appointed him. He suspects she's testing him. He's right.",
            "am_old_farouk": "Avoids the tea house. Farouk sees through him, and Tariq isn't ready to be seen through yet.",
            "am_inspector_zara": "Careful. Some of his contracts push boundaries. Zara hasn't said anything — yet.",
            "am_hakim": "Frustrated. Hakim's medicines could be worth a fortune if he'd just raise his prices. Hakim won't. Tariq finds this baffling.",
        },
    ),
]

_AL_MANAR_INSTITUTIONS = [
    PortInstitution(
        id="am_harbor",
        name="The Harbor of Arrivals",
        port_id="al_manar",
        institution_type="harbor_master",
        description=(
            "A curved stone quay lined with date palms, with a reception pavilion "
            "where arriving captains are offered dates and water before any business "
            "is discussed. The harbor is smaller than Porto Novo's but immaculately "
            "maintained. Every bollard is polished bronze."
        ),
        function="Controls docking, assigns berths, collects port fees. Arrival is a ceremony here, not a transaction.",
        political_leaning="Alliance loyalist with Al-Manar pride. Khalil serves the city's dignity before the Alliance's efficiency.",
        npc_id="am_khalil",
    ),
    PortInstitution(
        id="am_bazaar",
        name="The Spice Bazaar",
        port_id="al_manar",
        institution_type="exchange",
        description=(
            "A covered market stretching three city blocks, its ceiling hung with "
            "brass lamps and dried herb bundles. A hundred stalls compete for the "
            "nose — cinnamon, cardamom, saffron, clove. The auction floor is at the "
            "center, where the Spice Mother holds court every morning."
        ),
        function="Sets spice prices, auctions rare lots, arbitrates quality disputes. The Mediterranean's premier spice market.",
        political_leaning="Al-Manar supremacist. The Bazaar believes it IS Mediterranean trade, and Porto Novo is just a granary.",
        npc_id="am_yasmin",
    ),
    PortInstitution(
        id="am_palace",
        name="The Khoury Palace",
        port_id="al_manar",
        institution_type="governor",
        description=(
            "A tiled palace above the harbor where every surface catches light — "
            "mosaics of trade ships, courtyards with fountains, and a receiving room "
            "where the Merchant Princess conducts business from a divan instead of "
            "a desk. Six generations of Khourys watch from portraits on the walls."
        ),
        function="Sets port policy, manages diplomatic relations, controls the port treasury. Hereditary governance — not elected.",
        political_leaning="Alliance member with independent ambitions. Nadia is loyal to the Alliance when it serves Al-Manar, and creative when it doesn't.",
        npc_id="am_senhora_nadia",
    ),
    PortInstitution(
        id="am_tea_house",
        name="The Amber Glass",
        port_id="al_manar",
        institution_type="tavern",
        description=(
            "Not a tavern — a tea house. Low tables, silk cushions, and the quiet "
            "murmur of conversation conducted in a language that rum drinkers wouldn't "
            "understand. The amber glass windows filter the harbor light into gold. "
            "Everything here moves at the speed of tea."
        ),
        function="Social hub, intelligence exchange, crew recruitment. Information flows over tea, not rum. Deals are conceived here before they're signed anywhere else.",
        political_leaning="Neutral, but Farouk's neutrality is informed. He knows everything and judges nothing — which makes him invaluable to everyone.",
        npc_id="am_old_farouk",
    ),
    PortInstitution(
        id="am_customs",
        name="The Scales of Truth",
        port_id="al_manar",
        institution_type="customs",
        description=(
            "A marble building with the inscription 'WEIGHT AND TRUTH' carved above "
            "the door. Inside, brass scales of extraordinary precision line the walls. "
            "Zara's office is spare — a desk, a lamp, and a collection of confiscated "
            "counterfeit spices mounted in glass cases like specimens."
        ),
        function="Cargo inspection focused on QUALITY and AUTHENTICITY, not just legality. Fake saffron is a worse crime than smuggling here.",
        political_leaning="Quality enforcement. Zara serves Al-Manar's reputation, which happens to align with Alliance standards.",
        npc_id="am_inspector_zara",
    ),
    PortInstitution(
        id="am_apothecary",
        name="The Apothecary House",
        port_id="al_manar",
        institution_type="apothecary",
        description=(
            "A whitewashed building with a garden of medicinal herbs on the roof. "
            "Inside, the air is thick with eucalyptus and camphor. Shelves of labeled "
            "jars line every wall — roots, dried flowers, mineral powders, pressed "
            "oils. Hakim's workbench is at the center, surrounded by mortars and "
            "handwritten recipe books."
        ),
        function="Medicine production, quality certification, medicinal ingredient trading. Unique to Al-Manar — no other port has a dedicated apothecary institution.",
        political_leaning="Humanitarian. Hakim serves health, not politics. But his medicines give Al-Manar a trade advantage nobody talks about openly.",
        npc_id="am_hakim",
    ),
    PortInstitution(
        id="am_broker",
        name="The Broker's Alcove",
        port_id="al_manar",
        institution_type="broker",
        description=(
            "An arched alcove off the Bazaar's main hall, curtained with silk — "
            "because in Al-Manar, even contract negotiations happen behind beautiful "
            "fabric. Tariq's desk is polished rosewood. The contracts on it are "
            "handwritten on parchment, not printed on paper like Porto Novo's."
        ),
        function="Contract matching with an emphasis on prestige and exclusivity. Better contracts than Porto Novo — but fewer of them, and you have to earn access.",
        political_leaning="Ambitious Al-Manar loyalist. Tariq wants the Alcove to replace Porto Novo's desk as the Alliance's contract center.",
        npc_id="am_broker_tariq",
    ),
]

AL_MANAR_PROFILE = PortInstitutionalProfile(
    port_id="al_manar",
    governor_title="Merchant Princess",
    power_structure=(
        "Al-Manar is governed by hereditary merchant aristocracy — the Khoury family "
        "has held the title 'Merchant Princess' for six generations. But real power "
        "is shared: Nadia sets policy, Yasmin controls the spice market through the "
        "Circle, and Hakim's apothecary gives Al-Manar a unique trade advantage. "
        "Old Farouk's tea house is where all three go to think — separately, each "
        "believing they're unobserved. Zara, poached from Porto Novo, protects the "
        "market's integrity. Tariq pushes for expansion at the broker's desk, "
        "supported by Nadia but watched by everyone."
    ),
    internal_tension=(
        "The core tension is between tradition and ambition. Yasmin wants to preserve "
        "Al-Manar's ancient way — the Bazaar's authority, the Circle's traditions, "
        "the slow pace of tea-and-negotiation commerce. Tariq wants to modernize — "
        "faster contracts, direct Silk Circle partnerships, bypassing Porto Novo "
        "entirely. Nadia is playing both sides: she funds Tariq's ambitions while "
        "publicly deferring to Yasmin's traditions. Meanwhile, Nadia's private "
        "correspondence with the Silk Circle could reshape the entire Alliance — "
        "or destroy it. Only Farouk suspects the full picture, and he's not talking."
    ),
    institutions=_AL_MANAR_INSTITUTIONS,
    npcs=_AL_MANAR_NPCS,
)



# =========================================================================
# SILVA BAY — The Shipwrights' Republic
# =========================================================================

_SILVA_BAY_NPCS = [
    PortNPC(
        id="sb_elena",
        name="Elena Madeira",
        title="Master Shipwright",
        port_id="silva_bay",
        institution="shipyard",
        personality="exacting",
        description=(
            "Broad hands scarred by adze and chisel, hair tied back with a leather "
            "thong, and sawdust permanently ground into the creases of her knuckles. "
            "Elena is the Brotherhood's elected Master — the finest shipwright in the "
            "Mediterranean and possibly the world. She can look at a hull and tell you "
            "where it was built, when, and whether the builder rushed the keel."
        ),
        agenda=(
            "The craft and the Brotherhood's independence. Elena will build for "
            "anyone who respects ships — pirate, merchant, navy, she doesn't care. "
            "But she will NEVER build warships. The Brotherhood builds vessels to "
            "carry cargo and people, not weapons of war. She turned down the Iron "
            "Pact's contract personally, and she'd do it again. Her loyalty is to "
            "wood, not politics."
        ),
        greeting_neutral="\"Show me your ship. I'll tell you what she needs and what it'll cost. I don't need your name — I need to see your keel.\"",
        greeting_friendly="\"Captain! Brought her back in one piece, I see. Good sailor. Come — I've been experimenting with a new hull design. I want your opinion.\"",
        greeting_hostile="\"I'll repair your ship because the sea doesn't care about grudges. But I'm charging double, and I'm not smiling about it.\"",
        rumor="Elena once rebuilt a ship that had been cracked in half by a storm. The owner said it was impossible. Elena said it was Tuesday. The ship sailed for another twelve years.",
        relationship_notes={
            "sb_nuno": "Her harbor master, her old apprentice. She trained him. He still defers to her on everything that matters.",
            "sb_tomás": "Her timber buyer. She's the only person who can overrule his assessments. He respects that.",
            "sb_council": "She IS the council. The Brotherhood elects a Master; the Master governs. She governs lightly.",
            "sb_rosa": "Drinks at Rosa's tavern every night. The only person who can make Elena laugh.",
            "sb_customs_pires": "Ignores him. Ships are her jurisdiction; cargo is his. Clean boundaries.",
            "sb_broker_ana": "Appreciates her. Ana brings captains who need good ships. Good ships are Elena's purpose.",
        },
    ),
    PortNPC(
        id="sb_nuno",
        name="Nuno Ferreira",
        title="Harbor Master",
        port_id="silva_bay",
        institution="harbor_master",
        personality="practical",
        description=(
            "A former shipwright who lost three fingers to a bandsaw and moved to "
            "harbor management — 'same work, fewer blades,' he says. Nuno runs the "
            "harbor with a shipwright's eye: he cares about how ships dock, not "
            "about paperwork. Vasco in Porto Novo would have a seizure watching "
            "Nuno's filing system, which consists of a nail on the wall and a "
            "good memory."
        ),
        agenda=(
            "Keep the harbor moving. Ships in, ships out, timber in, timber out. "
            "Nuno has no political ambitions — he wants berths filled, slipways busy, "
            "and the tide tables accurate. He learned harbor craft from Elena and "
            "still checks with her before making big decisions."
        ),
        greeting_neutral="\"Berth's over there. Tie up properly — I don't want you drifting into the slipways. Timber loading happens at dawn, so don't sleep late.\"",
        greeting_friendly="\"Captain! Good to see her still floating. Take berth three — it's closest to the yard if you need Elena's people. Rough voyage?\"",
        greeting_hostile="\"You can dock, but stay out of the yard. Elena's orders. And if your ship leaks on my harbor floor, you're cleaning it up.\"",
        rumor="Nuno can predict the weather better than any barometer. He says it's the missing fingers — they ache before a storm. Nobody laughs anymore, because he's never been wrong.",
        relationship_notes={
            "sb_elena": "His mentor. He defers to her on anything important and isn't embarrassed about it.",
            "sb_tomás": "Good friends. They coordinate timber deliveries — Tomás grades it, Nuno stores it.",
            "sb_council": "Sits on the council but rarely speaks. 'I run the harbor, not the town.'",
            "sb_rosa": "Regular at her tavern. Brings her harbor news; she gives him the first pour of the evening.",
            "sb_customs_pires": "Works alongside him. Clean relationship — they share the dock without competing.",
            "sb_broker_ana": "Helpful. Tips her off when interesting captains arrive.",
        },
    ),
    PortNPC(
        id="sb_tomás",
        name="Tomás Verdelho",
        title="Timber Factor",
        port_id="silva_bay",
        institution="exchange",
        personality="patient",
        description=(
            "Quiet, deliberate, with the slow-moving confidence of a man who has "
            "handled every kind of wood that grows. Tomás runs the Timber Exchange — "
            "not an auction house like Porto Novo's grain operation, but a grading "
            "yard where every log is assessed by hand. He can tell oak from elm by "
            "the sound it makes when he taps it with his knuckle."
        ),
        agenda=(
            "Quality timber at honest prices. Tomás has no interest in cornering "
            "markets or playing politics. He grades wood, sets fair prices, and "
            "goes home. His one passion outside timber is protecting the forests — "
            "he's pushed the Brotherhood to limit harvests, arguing that a forest "
            "cut too fast won't grow back. This makes him unpopular with merchants "
            "who want volume."
        ),
        greeting_neutral="\"Looking for timber? Let me show you what's in the yard. I'll grade it while you watch — no surprises.\"",
        greeting_friendly="\"Captain — I've been setting aside a batch of coastal oak. Perfect for hull planking. Thought of you when it came in.\"",
        greeting_hostile="\"Timber's timber. I'll sell it to you at posted prices. But don't expect me to hold stock for someone who doesn't respect the wood.\"",
        rumor="Tomás once refused to sell a batch of mahogany because he said the trees were too young. The buyer offered triple. Tomás said the trees would be worth ten times that in twenty years. He was right.",
        relationship_notes={
            "sb_elena": "She's the only person who can overrule his grades. He respects that — she knows wood as well as he does.",
            "sb_nuno": "Good friends. They coordinate timber logistics — a clean partnership.",
            "sb_council": "Active council member. He's the environmental voice — limit harvests, replant, think long-term.",
            "sb_rosa": "Quiet regular. He drinks slowly and says little. Rosa respects the silence.",
            "sb_customs_pires": "No strong feelings. Timber doesn't need inspecting — it is what it is.",
            "sb_broker_ana": "She brings buyers; he grades the wood. Simple relationship.",
        },
    ),
    PortNPC(
        id="sb_council",
        name="The Brotherhood Council",
        title="Governing Council",
        port_id="silva_bay",
        institution="governor",
        personality="collective",
        description=(
            "Not a single ruler — a council of seven shipwrights who govern Silva "
            "Bay by consensus. The Master Shipwright (currently Elena) chairs it, "
            "but every member has equal voice. They meet in the Brotherhood Hall, "
            "a timber longhouse where the walls are carved with the names of every "
            "ship built in Silva Bay for the last two centuries."
        ),
        agenda=(
            "Independence. The Council's primary concern is keeping Silva Bay free "
            "from outside control. They're in the Exchange Alliance because it's "
            "convenient, not because they're loyal. If the Alliance ever demands "
            "something that conflicts with the Brotherhood's principles — like "
            "building warships — they'll leave. Everyone knows this. It's why "
            "nobody pushes."
        ),
        greeting_neutral="\"The Brotherhood welcomes all captains who come in peace. If you need ships built or repaired, we are at your service.\"",
        greeting_friendly="\"Captain — the Council recognizes your contribution to Silva Bay's prosperity. Your voice is welcome in our hall.\"",
        greeting_hostile="\"The Council has discussed your recent conduct. You may dock and repair, but you are not welcome in the Brotherhood Hall until trust is rebuilt.\"",
        rumor="The Council once voted on whether to leave the Exchange Alliance entirely. The vote was 4-3 to stay. Nobody knows which way Elena voted. She says it doesn't matter — the Brotherhood decided.",
        relationship_notes={
            "sb_elena": "She chairs the council. Her word carries weight, but she lets others speak first.",
            "sb_nuno": "Sits on the council, rarely speaks. His harbor expertise is valued when it's needed.",
            "sb_tomás": "The environmental conscience. His harvest limits are controversial but respected.",
            "sb_rosa": "Not on the council, but Rosa's tavern is where council members discuss things they won't say in the Hall.",
            "sb_customs_pires": "Not on the council. Customs is an Alliance function, not a Brotherhood one. The distinction matters.",
            "sb_broker_ana": "Not on the council, but her contract income funds Brotherhood operations.",
        },
    ),
    PortNPC(
        id="sb_rosa",
        name="Rosa Carvalho",
        title="Tavern Keeper",
        port_id="silva_bay",
        institution="tavern",
        personality="warm",
        description=(
            "Strong arms from hauling kegs, a voice that carries over any crowd, "
            "and a laugh that makes everyone within earshot feel like the world is "
            "simpler than they thought. Rosa runs the Dry Dock — the only tavern "
            "in Silva Bay, built from the timbers of a decommissioned brigantine. "
            "The bar is the ship's original helm. She steers conversations the way "
            "the old captain steered the ship."
        ),
        agenda=(
            "Community. Rosa's tavern is where Silva Bay actually works — where "
            "apprentices celebrate finishing their first hull, where the Council "
            "argues after meetings, where captains hear which shipwright to request. "
            "She has no political agenda, but her tavern IS the town square, which "
            "gives her more influence than she'd ever admit."
        ),
        greeting_neutral="\"Welcome to the Dry Dock! Sit anywhere — if you can find a seat. The special tonight is fish stew, and yes, there's sawdust in it. There's sawdust in everything here.\"",
        greeting_friendly="\"Captain! Your stool's been empty too long. Sit, sit — Elena was just telling a story about your ship. Something about the rudder? You should hear this.\"",
        greeting_hostile="\"...You can drink. But I'd keep my voice down if I were you. The Brotherhood has long memories and short tempers when the ale flows.\"",
        rumor="Rosa was married to a captain who sailed the Smuggler's Run and never came back. She built the Dry Dock with the insurance payout. She never remarried, and she never talks about it, and nobody asks.",
        relationship_notes={
            "sb_elena": "Best friends. Elena drinks here every night. Rosa is the only person who can make her laugh — or slow down.",
            "sb_nuno": "Fond. He brings her harbor news; she pours first. A good trade.",
            "sb_tomás": "Respects his quiet. She gives him the corner table and doesn't interrupt.",
            "sb_council": "Her tavern is the unofficial second meeting hall. She pretends not to listen. She always listens.",
            "sb_customs_pires": "Cautious. Pires is the only outsider in Silva Bay — Alliance-appointed. Rosa is polite but hasn't fully accepted him.",
            "sb_broker_ana": "Like a daughter. Ana grew up in the Dry Dock while her mother worked the yard.",
        },
    ),
    PortNPC(
        id="sb_customs_pires",
        name="Customs Officer Pires",
        title="Customs Officer",
        port_id="silva_bay",
        institution="customs",
        personality="awkward",
        description=(
            "A young man from Porto Novo who drew the short straw — assigned to "
            "Silva Bay by the Alliance, where nobody asked for a customs officer "
            "and nobody particularly wants one. Pires is competent but uncomfortable. "
            "He knows he's an outsider in a town that governs itself, and he tries "
            "too hard to fit in. The Brotherhood tolerates him because the Alliance "
            "requires it."
        ),
        agenda=(
            "Doing his job without making enemies. Pires inspects cargo because "
            "the Alliance says he must, but he keeps it light — quick checks, no "
            "drama. He dreams of a transfer back to Porto Novo where Inspector "
            "Salva's methods are appreciated. In Silva Bay, thoroughness is seen "
            "as interference."
        ),
        greeting_neutral="\"Quick inspection — routine, I promise. I know you're here for the yard, not for paperwork. I'll be fast.\"",
        greeting_friendly="\"Captain — everything looks good. I've already signed off on your manifest. Go see Elena before the queue gets long.\"",
        greeting_hostile="\"I... need to do a full inspection. Alliance regulations. I'm sorry — I know it's inconvenient. Please don't tell Elena.\"",
        rumor="Pires applied for a transfer back to Porto Novo three times. Each time, Salva sent back the same response: 'Learn to inspect without a manual first.' Pires isn't sure if it's an insult or a lesson.",
        relationship_notes={
            "sb_elena": "Terrified of her. She treats him like furniture. He inspects what he can and stays out of her yard.",
            "sb_nuno": "Workable. Nuno doesn't mind him — they share dock space without trouble.",
            "sb_tomás": "Irrelevant to each other. Timber doesn't need customs clearance.",
            "sb_council": "Not invited. Not Brotherhood. The distinction stings, but he understands it.",
            "sb_rosa": "Trying. He drinks at the Dry Dock and tips well. Rosa is polite. He can't tell if she likes him or tolerates him.",
            "sb_broker_ana": "She's kind to him. The only person in Silva Bay who treats him as a colleague, not a visitor.",
        },
    ),
    PortNPC(
        id="sb_broker_ana",
        name="Ana Sousa",
        title="Broker",
        port_id="silva_bay",
        institution="broker",
        personality="earnest",
        description=(
            "Grew up in the Dry Dock tavern while her mother worked the yard. Ana "
            "became a broker instead of a shipwright — the first in her family to "
            "choose paper over wood. She runs contracts from a bench outside the "
            "Brotherhood Hall, rain or shine, because Silva Bay doesn't believe in "
            "offices. She knows every ship that's been built here and which captains "
            "treat them well."
        ),
        agenda=(
            "Proving herself. Ana is young and working in a town that values decades "
            "of experience. She brings contract work that funds the Brotherhood, "
            "which earns her a seat at the edge of respect. She wants to prove that "
            "commerce and craft can coexist — that a good broker helps good shipwrights "
            "stay independent."
        ),
        greeting_neutral="\"Captain? I have contracts — mostly timber runs and ship delivery commissions. Nothing fancy, but the work is honest and it pays.\"",
        greeting_friendly="\"Captain! Elena mentioned your ship needs attention — while she's working on it, I have a timber contract that would pay for the repairs. Interested?\"",
        greeting_hostile="\"I... don't have anything for you right now. Try Porto Novo — Fernanda has more to work with than I do. No hard feelings.\"",
        rumor="Ana turned down an offer from Fernanda Reis to join Porto Novo's broker desk. She said Silva Bay needed her more. Rosa cried when she heard. Elena pretended not to notice, which is Elena's way of being proud.",
        relationship_notes={
            "sb_elena": "Admires her fiercely. Elena is everything Ana wants to be — independent, skilled, uncompromising.",
            "sb_nuno": "Helpful. He tips her off when captains arrive who might need contracts.",
            "sb_tomás": "She finds buyers for his timber. A clean business relationship that both appreciate.",
            "sb_council": "Wants to be invited someday. Knows she has to earn it. Isn't sure how.",
            "sb_rosa": "Like a mother. Ana grew up in the Dry Dock. Rosa still saves her a plate of fish stew.",
            "sb_customs_pires": "Kind to him. She knows what it's like to be the outsider trying to earn respect.",
        },
    ),
]

_SILVA_BAY_INSTITUTIONS = [
    PortInstitution(
        id="sb_shipyard",
        name="The Master Shipyard",
        port_id="silva_bay",
        institution_type="shipyard",
        description=(
            "The largest shipyard in the Mediterranean — three slipways, two dry "
            "docks, a steam box for bending timber, and a mast pond where logs "
            "season for years before they're touched. The sign over the gate reads "
            "'BUILT TO SAIL, NOT TO SINK.' It's not a motto. It's a threat."
        ),
        function="Ship repairs, upgrades, and purchases. The best work in the game — cheapest repairs (1 silver/hull point). Elena's standards are the price of admission.",
        political_leaning="Apolitical. The yard builds for anyone. ANYONE. Except warmongers.",
        npc_id="sb_elena",
    ),
    PortInstitution(
        id="sb_harbor",
        name="The Working Harbor",
        port_id="silva_bay",
        institution_type="harbor_master",
        description=(
            "No ceremony, no pavilion — just a clipboard, a tide table nailed to "
            "a post, and Nuno squinting at your approach. Timber barges have priority; "
            "everyone else fits where they fit. The harbor smells of fresh-cut wood "
            "and pitch."
        ),
        function="Berth assignment, timber logistics. No ceremony — function over form. Nuno runs it like a shipwright runs a project.",
        political_leaning="Brotherhood-aligned. The harbor serves the yard first, everything else second.",
        npc_id="sb_nuno",
    ),
    PortInstitution(
        id="sb_timber_exchange",
        name="The Timber Yard",
        port_id="silva_bay",
        institution_type="exchange",
        description=(
            "An open-air grading yard where logs are stacked by species, quality, "
            "and seasoning time. No building — just canopies for rain and Tomás "
            "with his grading chalk. Every log gets a mark: A for hull-grade, B "
            "for general, C for firewood. There is no D. If it's worse than C, "
            "it goes back."
        ),
        function="Timber grading, pricing, and sales. Not an auction — prices are set by quality grade. Fair, transparent, no haggling.",
        political_leaning="Conservation-minded. Tomás limits harvests to protect forests. Unpopular with volume buyers.",
        npc_id="sb_tomás",
    ),
    PortInstitution(
        id="sb_brotherhood_hall",
        name="The Brotherhood Hall",
        port_id="silva_bay",
        institution_type="governor",
        description=(
            "A timber longhouse with walls carved with the names of every ship "
            "built in Silva Bay for two hundred years. Seven chairs around a round "
            "table — no head seat, because the Brotherhood governs as equals. A "
            "ship's bell hangs from the ceiling, rung to open and close each session."
        ),
        function="Self-governance by council of seven shipwrights. No external authority. Alliance membership is by choice, not obligation.",
        political_leaning="Fiercely independent. Alliance membership is conditional — cross the Brotherhood's principles and they leave.",
        npc_id="sb_council",
    ),
    PortInstitution(
        id="sb_tavern",
        name="The Dry Dock",
        port_id="silva_bay",
        institution_type="tavern",
        description=(
            "Built from the timbers of a decommissioned brigantine — the bar is "
            "the original helm, and the booths are made from hull sections. Sawdust "
            "on the floor, ship models on every shelf, and the sound of the yard "
            "leaking in through walls that were never meant to be walls. The fish "
            "stew is legendary. The sawdust content is debatable."
        ),
        function="Social hub, crew recruitment, unofficial council annex. Where Silva Bay actually makes decisions.",
        political_leaning="Community heart. Rosa doesn't take sides — but her tavern is where sides are chosen.",
        npc_id="sb_rosa",
    ),
    PortInstitution(
        id="sb_customs",
        name="The Customs Shed",
        port_id="silva_bay",
        institution_type="customs",
        description=(
            "A wooden shed at the edge of the dock — the most modest customs office "
            "in the Mediterranean. A desk, a chair, a stamp, and a young man who "
            "wishes he were somewhere else. The shed leaks when it rains. Nobody "
            "has offered to fix it."
        ),
        function="Minimal cargo inspection. Alliance requirement, not Brotherhood priority. Quick and apologetic.",
        political_leaning="Alliance outsider. Pires represents Porto Novo's rules in a town that makes its own.",
        npc_id="sb_customs_pires",
    ),
    PortInstitution(
        id="sb_broker",
        name="The Broker's Bench",
        port_id="silva_bay",
        institution_type="broker",
        description=(
            "A wooden bench outside the Brotherhood Hall with a canvas awning for "
            "rain. No office — Ana works in the open because Silva Bay doesn't "
            "believe in walls for work that can be done under sky. A corkboard "
            "behind her displays active contracts. A tin cup holds her pencils."
        ),
        function="Contract matching, timber commissions, ship delivery work. Informal, honest, no prestige games. The income funds the Brotherhood.",
        political_leaning="Brotherhood supporter. Ana's contract income keeps the yard independent from Alliance subsidies.",
        npc_id="sb_broker_ana",
    ),
]

SILVA_BAY_PROFILE = PortInstitutionalProfile(
    port_id="silva_bay",
    governor_title="Brotherhood Council",
    power_structure=(
        "Silva Bay is a shipwrights' republic — no single ruler, no hereditary "
        "title. The Brotherhood Council of seven governs by consensus, chaired by "
        "the elected Master Shipwright (Elena). The yard IS the town: Elena builds "
        "the ships, Tomás grades the timber, Nuno runs the harbor, and everything "
        "else exists to support that work. Rosa's tavern is the unofficial second "
        "chamber where real opinions emerge. Ana's broker bench funds it all. "
        "Pires, the Alliance customs officer, is tolerated but never included."
    ),
    internal_tension=(
        "The core tension is independence vs. relevance. The Brotherhood governs "
        "itself and answers to no one — but the Alliance provides trade protection "
        "and market access that Silva Bay needs. Elena wants to stay free; the "
        "Alliance wants Silva Bay's ships. The leverage is mutual, which creates a "
        "fragile equilibrium. Tomás adds a second tension: his harvest limits "
        "protect the forests but frustrate merchants who want more timber faster. "
        "The quiet tension is Pires — an outsider who represents everything the "
        "Brotherhood distrusts (external authority), yet who genuinely tries to "
        "belong. Ana is his only ally, and she's still earning her own place."
    ),
    institutions=_SILVA_BAY_INSTITUTIONS,
    npcs=_SILVA_BAY_NPCS,
)



# =========================================================================
# CORSAIR'S REST — The Silence
# =========================================================================

_CORSAIRS_REST_NPCS = [
    PortNPC(
        id="cr_one_eye",
        name="One-Eye Basso",
        title="Dockmaster",
        port_id="corsairs_rest",
        institution="harbor_master",
        personality="watchful",
        description=(
            "A man who lost his left eye to a boarding hook and replaced it with a "
            "polished black stone. One-Eye doesn't check manifests — he checks the "
            "horizon behind you. His job isn't paperwork; it's making sure you weren't "
            "followed. He stands at the cove's narrow entrance with a spyglass that "
            "never leaves his hand, and if he doesn't wave you in, you don't enter."
        ),
        agenda=(
            "Security. Basso's only concern is the cove's secrecy. He doesn't care "
            "what you carry, who you are, or what you've done — he cares whether a "
            "navy patrol is behind you. Betray the cove's location and Basso will "
            "find you. He always finds them."
        ),
        greeting_neutral="\"...Clear behind you. Come in. Kill your running lights before the bend.\"",
        greeting_friendly="\"Clean approach. Good. Take the inner berth — I'll watch your stern tonight. No charge.\"",
        greeting_hostile="\"You brought heat. I can smell it. Outer anchorage, away from everyone else. And if a patrol appears, you never saw this cove.\"",
        rumor="One-Eye was a navy lookout before he lost the eye — ironic, and nobody laughs about it. Some say he can see further with one eye than most men can with two. Others say the black stone eye sees something else entirely.",
        relationship_notes={
            "cr_whisper": "Trusts completely. Whisper runs the inside; Basso runs the perimeter. They've never had a disagreement that mattered.",
            "cr_mama_lucia": "Protective. He makes sure her kitchen is never raided by navy patrols. She makes sure he eats.",
            "cr_no_one": "Respectful distance. No One runs the Tide's business. Basso runs the cove's safety. Different jurisdictions.",
            "cr_the_physician": "Grateful. The Physician patched his eye socket for free. Basso repays it by ensuring medicine shipments arrive undisturbed.",
            "cr_ghost": "Professional trust. Ghost moves cargo; Basso makes sure nobody sees it arrive.",
            "cr_little_fish": "Watches over her. She's young. The cove isn't kind to the young.",
        },
    ),
    PortNPC(
        id="cr_whisper",
        name="Whisper",
        title="Price Keeper",
        port_id="corsairs_rest",
        institution="exchange",
        personality="secretive",
        description=(
            "Nobody knows Whisper's real name, age, or where they came from. They "
            "appear between the market stalls like smoke, murmur a price, and vanish. "
            "Whisper is the black market's price-setter — the person who knows what "
            "everything is worth when it can't be sold in daylight. They communicate "
            "in hand signals, written notes, and single whispered words."
        ),
        agenda=(
            "The market's survival. Whisper keeps Corsair's Rest functioning by "
            "maintaining fair black market prices. If prices get too high, buyers "
            "go elsewhere. Too low, and sellers stop coming. Whisper finds the line "
            "every day, wordlessly, and the market obeys because Whisper has never "
            "been wrong. Nobody understands how. Nobody asks."
        ),
        greeting_neutral="A folded note appears in your hand. It reads: \"Buying or selling?\" with two prices written below in small, precise handwriting.",
        greeting_friendly="A note: \"Good to see you. Special prices today — for friends.\" A third column of numbers appears, lower than the posted rate.",
        greeting_hostile="No note. No prices. Whisper passes you without stopping. The market stalls seem to close as you approach. Nobody is selling today.",
        rumor="Three different people claim to have seen Whisper's face. They describe three completely different people. Either Whisper changes faces, or there's more than one of them. Both explanations are unsettling.",
        relationship_notes={
            "cr_one_eye": "The only person Whisper communicates with directly. They've worked together longer than anyone at the Rest.",
            "cr_mama_lucia": "Leaves payment for meals under the plate. Always exact. Mama Lucia has never seen Whisper eat.",
            "cr_no_one": "Whisper sets the prices; No One enforces the deals. Neither interferes with the other's work.",
            "cr_the_physician": "Ensures medicine prices stay accessible. Whether this is compassion or economics, nobody knows.",
            "cr_ghost": "Ghost moves the cargo that Whisper prices. A chain with no weak links.",
            "cr_little_fish": "Sends her notes with market intelligence. Teaching her, maybe. Or recruiting.",
        },
    ),
    PortNPC(
        id="cr_no_one",
        name="No One",
        title="The Tide's Voice",
        port_id="corsairs_rest",
        institution="governor",
        personality="cold",
        description=(
            "The Crimson Tide's representative at Corsair's Rest. No One is not a "
            "governor — the Rest has no government. No One is the person who makes "
            "sure the Crimson Tide's interests are respected, tribute is collected, "
            "and disputes are settled before they become violence. Tall, gaunt, "
            "dressed in a faded crimson coat that was once military issue. Speaks "
            "rarely. When No One speaks, the cove goes quiet."
        ),
        agenda=(
            "The Crimson Tide's authority. Corsair's Rest exists because the Tide "
            "protects it. In return, the Tide takes a cut of every transaction, "
            "gets first pick of contraband shipments, and uses the cove as a staging "
            "area. No One ensures this arrangement continues. Captains who forget "
            "that the Rest belongs to the Tide are reminded — once."
        ),
        greeting_neutral="A long look. Then: \"The Tide permits your stay. Trade as you wish. The tribute is ten percent.\"",
        greeting_friendly="\"The Tide remembers its friends. Your tribute is waived this visit. Scarlet Ana sends regards.\"",
        greeting_hostile="\"You owe the Tide. Pay what you owe, or leave the cove. You will not be asked a second time.\"",
        rumor="No One was a garrison officer who deserted — like the Iron Wolves, but earlier. The Wolves hate No One for not joining them. No One hates the Wolves for the same reason they hate everyone: on principle.",
        relationship_notes={
            "cr_one_eye": "Mutual respect. Basso protects the cove; No One protects the Tide's interests. They never conflict because their territories don't overlap.",
            "cr_whisper": "Depends on Whisper for market stability. Doesn't understand them. Doesn't need to.",
            "cr_mama_lucia": "Even No One eats at Mama Lucia's. Even No One pays. Some things are sacred even in a lawless port.",
            "cr_the_physician": "Complicated. The Physician heals everyone — even the Tide's enemies. No One tolerates this because even pirates get sick.",
            "cr_ghost": "Direct reports. Ghost handles the Tide's smuggling logistics. No One handles the politics.",
            "cr_little_fish": "Ignores her. She's beneath the Tide's notice. That's probably the safest place to be.",
        },
    ),
    PortNPC(
        id="cr_mama_lucia",
        name="Mama Lucia",
        title="Cook and Keeper",
        port_id="corsairs_rest",
        institution="tavern",
        personality="fierce",
        description=(
            "A stout woman with iron-grey hair, forearms like ham hocks, and a "
            "ladle she wields like a weapon — because it is one. Mama Lucia runs "
            "the only kitchen at Corsair's Rest: a cave carved into the cliff face "
            "with a smoke hole above and benches below. She feeds everyone. Pirates, "
            "smugglers, fugitives, the lost, the desperate. She feeds them all, and "
            "violence in her kitchen means you never eat again."
        ),
        agenda=(
            "Feeding people and keeping the peace — inside her kitchen, which she "
            "considers the only civilized square meter in Corsair's Rest. Mama Lucia "
            "fled a bad marriage in Porto Novo twenty years ago. The Rest took her in. "
            "She repays it by making sure nobody starves and nobody kills each other "
            "over stew. Her kitchen is neutral ground. Everyone respects this — even "
            "No One, even the Butcher, even captains with blood feuds."
        ),
        greeting_neutral="\"Sit. Eat. Whatever you are, you're hungry — I can see it. We'll talk about what you need after your belly's full.\"",
        greeting_friendly="\"My favorite captain! I saved you the good fish — not the stuff I serve the pirates. Sit, sit. Tell Mama what happened.\"",
        greeting_hostile="\"You can eat. EVERYONE can eat. But you keep your trouble outside my kitchen, understand? My ladle has settled bigger disputes than yours.\"",
        rumor="Mama Lucia's fish stew cured a plague that swept through the cove six years ago. Nobody knows the recipe. She says the secret ingredient is 'minding your own business.' The Physician suspects it's actually turmeric.",
        relationship_notes={
            "cr_one_eye": "He protects the cove; she feeds it. They're the two pillars the Rest stands on. They don't say this. They don't need to.",
            "cr_whisper": "Has never seen Whisper eat, but the payment is always under the plate. She saves a bowl anyway. Someone has to worry.",
            "cr_no_one": "Even the Tide's enforcer respects her kitchen. No One pays. No One sits quietly. No One eats everything on the plate.",
            "cr_the_physician": "Friends. The two people at the Rest who care about keeping others alive. They share ingredients and worries.",
            "cr_ghost": "Feeds his crew when they come in cold and wet from midnight runs. Doesn't ask where they've been.",
            "cr_little_fish": "Took her in when she arrived with nothing. Gave her the dish-washing job. Watches over her like a hawk. Will hurt anyone who hurts her.",
        },
    ),
    PortNPC(
        id="cr_the_physician",
        name="The Physician",
        title="Doctor",
        port_id="corsairs_rest",
        institution="apothecary",
        personality="weary",
        description=(
            "A former navy surgeon who saw too much and drank too much and washed "
            "up at Corsair's Rest with nothing but a medical bag and steady hands. "
            "The Physician (no one uses a name, and the title is as close to respect "
            "as the Rest gets) treats everyone — pirate wounds, smuggler fevers, "
            "the injuries nobody talks about. Charges what you can pay. Sometimes "
            "charges nothing."
        ),
        agenda=(
            "Doing what he was trained for, in the only place that would have him. "
            "The Physician doesn't care about sides, factions, or morality. He stitches "
            "wounds. He sets bones. He brews medicine from whatever Mama Lucia's "
            "kitchen doesn't need. He drinks too much at night and wakes with steady "
            "hands at dawn, which is the only miracle anyone at the Rest believes in."
        ),
        greeting_neutral="\"Hurt? Sick? Sit on the table. If you're neither, buy medicine or leave — I'm busy. I'm always busy.\"",
        greeting_friendly="\"Captain. Intact, I see. Good. I worry about the ones I've patched — professional investment. What can I do for you?\"",
        greeting_hostile="\"I treat everyone. That's the oath. Sit down or don't, but if you bleed in here, I'm stitching you whether you want it or not.\"",
        rumor="The Physician was a brilliant navy surgeon — could have run any hospital in the Mediterranean. Then something happened on a ship. He won't say what. The navy won't say either. He drinks to forget it, and every morning his hands are steady anyway.",
        relationship_notes={
            "cr_one_eye": "Patched his eye socket for free. Basso has been silently grateful ever since — the quietest debt in the cove.",
            "cr_whisper": "Whisper ensures medicine stays affordable on the black market. The Physician suspects compassion. He hopes he's right.",
            "cr_no_one": "Treats the Tide's wounded. No One tolerates his neutrality because the alternative is no doctor.",
            "cr_mama_lucia": "His closest friend. They share ingredients, share worries, and share the belief that keeping people alive matters more than taking sides.",
            "cr_ghost": "Patches Ghost's crew after rough runs. Doesn't ask questions. Receives extra medical supplies in return.",
            "cr_little_fish": "Taught her basic wound care. She's a quick study. He hopes she'll leave before the cove takes away the light in her eyes.",
        },
    ),
    PortNPC(
        id="cr_ghost",
        name="Ghost",
        title="Cargo Master",
        port_id="corsairs_rest",
        institution="broker",
        personality="efficient",
        description=(
            "You hear Ghost before you see him — the creak of rope, the thud of "
            "crates being moved in the dark. Ghost runs the Tide's smuggling logistics "
            "at the Rest: what comes in, what goes out, what gets hidden in the cliff "
            "caves when a patrol passes. He's thin, pale, and moves through the cove "
            "like he was born in shadow. His crew can unload a full ship in two hours "
            "by moonlight."
        ),
        agenda=(
            "Moving cargo. Ghost doesn't care about politics or factions — he cares "
            "about logistics. What needs to go where, by when, without being seen. "
            "He's the best smuggling coordinator in the Mediterranean, and he knows it. "
            "Captains who need contraband moved come to Ghost. He quotes a price, a "
            "time, and a route. He has never missed a deadline."
        ),
        greeting_neutral="\"What are you moving? Where does it need to go? When? ...I can do that. Here's the price.\"",
        greeting_friendly="\"Captain. I have a run for you — clean route, good margin, and I've already scouted the patrol schedule. Interested?\"",
        greeting_hostile="\"I don't move cargo for people I can't trust. Find another broker. Or better yet — leave the cove before morning.\"",
        rumor="Ghost once moved a full cargo of opium through a navy blockade using fishing boats, decoy ships, and a route through underwater caves that only he knew existed. The navy still doesn't know how it happened.",
        relationship_notes={
            "cr_one_eye": "Basso watches the entrance; Ghost watches the cargo. Two halves of the same operation.",
            "cr_whisper": "Whisper prices it; Ghost moves it. The most efficient supply chain in the underworld.",
            "cr_no_one": "Direct superior in the Tide hierarchy. Ghost reports to No One on logistics. Professional, clean, no friction.",
            "cr_mama_lucia": "His crews eat at Mama's after midnight runs. She doesn't ask. He doesn't tell. The stew is always hot.",
            "cr_the_physician": "Sends medical supplies as payment for patching his crew. The Physician never asks where the supplies come from.",
            "cr_little_fish": "Using her as a runner. She's fast, small, and invisible — perfect for messages. Whether this is exploitation or mentorship depends on who you ask.",
        },
    ),
    PortNPC(
        id="cr_little_fish",
        name="Little Fish",
        title="Runner",
        port_id="corsairs_rest",
        institution="customs",
        personality="sharp",
        description=(
            "A girl of maybe fourteen — nobody knows exactly, including her. "
            "She arrived at the Rest on a cargo ship two years ago, hidden in a "
            "barrel. Mama Lucia took her in. Now she runs messages, watches the "
            "cliff paths for approaching ships, and knows every crack and tunnel "
            "in the cove. The Rest's unofficial lookout and messenger — the 'customs "
            "officer' in a port that has no customs."
        ),
        agenda=(
            "Survival and belonging. Little Fish has no family, no past she'll "
            "discuss, and no plan beyond tomorrow. She's sharp, fast, and learning "
            "the cove's ways with the intensity of someone who knows that usefulness "
            "is the only protection she has. Ghost uses her as a runner. Whisper "
            "sends her notes. The Physician teaches her wound care. She's absorbing "
            "everything, and someday the cove will realize she's the most dangerous "
            "person in it."
        ),
        greeting_neutral="She appears beside you without a sound. \"Message for you. Or from you. Which?\" She holds out her hand — for a coin or a note, either works.",
        greeting_friendly="She drops from a rock ledge and lands silently. \"Captain! I saw you coming around the point. Mama says your table is ready. Also, Whisper left you something.\"",
        greeting_hostile="You don't see her. But you have the distinct feeling you're being watched from the cliff above. A pebble clatters down near your feet. A warning, maybe.",
        rumor="Little Fish can navigate the cliff tunnels in complete darkness. She claims to have found a tunnel that leads to a second harbor — the one the old pirates talk about. She won't say whether she's telling the truth. She's learning from the best.",
        relationship_notes={
            "cr_one_eye": "He watches over her. She doesn't know he's the reason the rough sailors leave her alone. She thinks she handles it herself.",
            "cr_whisper": "Receives notes from Whisper with market intelligence. Whether Whisper is teaching her or recruiting her is the cove's favorite debate.",
            "cr_no_one": "Invisible to the Tide's notice. That's the safest place to be, and Little Fish is smart enough to stay there.",
            "cr_mama_lucia": "The closest thing to a mother she has. Mama gave her a job, a bed, and a reason to stay. Little Fish would fight anyone who threatened Mama's kitchen.",
            "cr_the_physician": "Teaching her wound care. She's a quick study. He hopes she'll use the skills somewhere better than the cove.",
            "cr_ghost": "Her employer for running jobs. Ghost pays fairly and doesn't put her in danger — usually. She's learning logistics from the best, which is either a gift or a curse.",
        },
    ),
]

_CORSAIRS_REST_INSTITUTIONS = [
    PortInstitution(
        id="cr_entrance",
        name="The Cove Mouth",
        port_id="corsairs_rest",
        institution_type="harbor_master",
        description=(
            "Not an office — a rock ledge at the narrow entrance to the cove "
            "where One-Eye Basso stands with his spyglass. A signal lantern hangs "
            "from a hook: green for enter, dark for stay away. No dock, no paperwork, "
            "no ceremony. Just one man deciding whether you get in."
        ),
        function="Access control. Not manifest review — threat assessment. Basso decides who enters. His spyglass is the only checkpoint.",
        political_leaning="Brotherhood of the Cove. The cove's security is its own politics.",
        npc_id="cr_one_eye",
    ),
    PortInstitution(
        id="cr_market",
        name="The Whisper Market",
        port_id="corsairs_rest",
        institution_type="exchange",
        description=(
            "Not a building — a series of canvas-covered stalls in the cliff shadow "
            "where goods change hands without receipts. Prices are written in chalk "
            "on slate boards that can be wiped clean in seconds if a patrol appears. "
            "The market has no opening hours. It's always open and never officially there."
        ),
        function="Black market pricing and contraband trade. No receipts, no records, no evidence. Prices set by Whisper.",
        political_leaning="Outside all systems. The Whisper Market acknowledges no authority except supply and demand.",
        npc_id="cr_whisper",
    ),
    PortInstitution(
        id="cr_tide_seat",
        name="The Crimson Chair",
        port_id="corsairs_rest",
        institution_type="governor",
        description=(
            "A carved stone chair at the back of the deepest cave — the Crimson Tide's "
            "seat of authority at the Rest. Nobody sits in it except when No One holds "
            "court. The rest of the time it's empty, which is its own kind of threat. "
            "A faded crimson banner hangs behind it, salt-stained and torn."
        ),
        function="Crimson Tide authority. Tribute collection, dispute resolution, faction governance. Not a government — a protection arrangement.",
        political_leaning="Crimson Tide. The Rest exists because the Tide permits it. The Chair is the proof.",
        npc_id="cr_no_one",
    ),
    PortInstitution(
        id="cr_kitchen",
        name="Mama Lucia's Kitchen",
        port_id="corsairs_rest",
        institution_type="tavern",
        description=(
            "A cave carved into the cliff face with a smoke hole above and timber "
            "benches below. A fire pit, three iron pots, and the smell of fish stew "
            "that seeps into the rock itself. It's always too hot, always crowded, "
            "and the only place in Corsair's Rest where violence is absolutely "
            "forbidden. Mama's ladle enforces the peace."
        ),
        function="Neutral ground. Food, crew recruitment, information exchange. The only safe space in the cove. Violence here means you never eat again.",
        political_leaning="Aggressively neutral. Mama feeds everyone. EVERYONE. Politics stops at her threshold.",
        npc_id="cr_mama_lucia",
    ),
    PortInstitution(
        id="cr_surgery",
        name="The Surgery",
        port_id="corsairs_rest",
        institution_type="apothecary",
        description=(
            "A cave with better lighting than most — the Physician rigged a system "
            "of mirrors to reflect sunlight inside during the day. A wooden table "
            "stained with things nobody asks about, shelves of salvaged medical "
            "supplies, and a bottle of rum that serves double duty as antiseptic "
            "and anesthetic."
        ),
        function="Medical care, medicine trading. Treats everyone regardless of faction or crime. Charges what you can pay.",
        political_leaning="Neutral by oath. The Physician's loyalty is to the practice of medicine, not to any flag.",
        npc_id="cr_the_physician",
    ),
    PortInstitution(
        id="cr_caves",
        name="The Cliff Caves",
        port_id="corsairs_rest",
        institution_type="broker",
        description=(
            "A network of sea caves accessible only by rope or at low tide. Ghost's "
            "crews use them to store, move, and hide cargo. Some caves are mapped; "
            "others aren't. Somewhere in the network is the 'second harbor' that the "
            "old pirates whisper about — or don't."
        ),
        function="Smuggling logistics, contraband storage, contract coordination. Ghost matches cargo to routes and captains to runs.",
        political_leaning="Crimson Tide operations. Ghost works for the Tide. The caves are the Tide's infrastructure.",
        npc_id="cr_ghost",
    ),
    PortInstitution(
        id="cr_cliffs",
        name="The Cliff Watch",
        port_id="corsairs_rest",
        institution_type="customs",
        description=(
            "The cliff paths above the cove where Little Fish watches for approaching "
            "ships, carries messages, and knows every tunnel and crack. Not a customs "
            "house — the inverse: a lookout system designed to ensure customs never "
            "arrives. The paths are invisible from the sea."
        ),
        function="Counter-customs. Patrol detection, message running, early warning. The cove's immune system against official interference.",
        political_leaning="Survival. The Cliff Watch exists to keep the Rest hidden. That's everyone's politics here.",
        npc_id="cr_little_fish",
    ),
]

CORSAIRS_REST_PROFILE = PortInstitutionalProfile(
    port_id="corsairs_rest",
    governor_title="The Tide's Voice",
    power_structure=(
        "Corsair's Rest has no government — it has an arrangement. The Crimson Tide "
        "protects the cove through No One's authority, collecting tribute and settling "
        "disputes. One-Eye Basso controls physical access — if he doesn't wave you in, "
        "you don't enter. Whisper sets prices in the shadow market. Ghost moves the "
        "cargo. Mama Lucia feeds everyone and enforces the only law that holds: no "
        "violence in her kitchen. The Physician keeps people alive. Little Fish watches "
        "everything from the cliffs, learning, and growing into something the cove "
        "hasn't figured out yet."
    ),
    internal_tension=(
        "The surface tension is between the Crimson Tide's authority (No One) and "
        "the cove's organic independence (everyone else). The Tide protects the Rest "
        "but takes a cut. If the cut gets too big, the cove dies. If the protection "
        "falters, the navy finds them. It's a balance maintained by mutual need. "
        "The deeper tension is generational: One-Eye, Mama Lucia, and the Physician "
        "are aging. Ghost and Little Fish are the future. Ghost is Tide-loyal — "
        "whatever the Tide becomes, Ghost follows. Little Fish is loyal to Mama and "
        "the cove itself. When the old guard is gone, the question is whether the "
        "cove serves the Tide or the Tide serves the cove. No One watches this "
        "tension carefully and says nothing, which is the most unsettling thing of all."
    ),
    institutions=_CORSAIRS_REST_INSTITUTIONS,
    npcs=_CORSAIRS_REST_NPCS,
)



# =========================================================================
# IRONHAVEN — The Iron Pact's Furnace
# =========================================================================

_IRONHAVEN_NPCS = [
    PortNPC(
        id="ih_gunnar",
        name="Gunnar Stahl",
        title="Harbor Master",
        port_id="ironhaven",
        institution="harbor_master",
        personality="blunt",
        description=(
            "Built like a hull beam, with a voice calibrated for shouting across "
            "foundry floors. Gunnar ran supply logistics for the garrison before he "
            "ran the harbor. He assigns berths by cargo priority: iron and weapons "
            "shipments dock first. Everything else waits."
        ),
        agenda=(
            "Efficiency. Gunnar wants ships loaded and gone. The harbor is a funnel "
            "for the foundry, not a destination. He has no patience for captains who "
            "linger, haggle, or complain about berth assignments. His harbor runs "
            "like the military operation he was trained for."
        ),
        greeting_neutral="\"Cargo type and tonnage. You'll dock when I have a berth. Iron shipments first — that's the rule.\"",
        greeting_friendly="\"Captain. Berth two, portside — I held it. Load fast and you'll make the evening tide.\"",
        greeting_hostile="\"Outer anchorage. No priority. And if I hear you've been selling to pirates, you won't dock here again.\"",
        rumor="Gunnar deserted from the same garrison as the Iron Wolves — but years earlier and for different reasons. He left because the pay stopped. They left because the discipline bored them. He considers them traitors. They consider him a coward. Neither will say this to the other's face.",
        relationship_notes={
            "ih_forge_master": "Serves him. The foundry is Ironhaven's purpose. Gunnar's harbor exists to feed it.",
            "ih_astrid": "Uncomfortable. She's too political for his taste. He moves iron; she moves power.",
            "ih_the_smith": "Drinking companion. Two military men who understand each other without conversation.",
            "ih_olga": "Professional respect. She runs the tavern the way he runs the harbor — no nonsense.",
            "ih_inspector_kross": "Allies. Both ex-military. Both believe in rules. The only question is whose rules.",
            "ih_broker_jan": "Useful. Jan brings contracts that keep the harbor busy.",
        },
    ),
    PortNPC(
        id="ih_forge_master",
        name="Forge Master Henrik Brandt",
        title="Guild Master",
        port_id="ironhaven",
        institution="exchange",
        personality="imperious",
        description=(
            "A massive man whose leather apron has never fully cooled. Henrik is the "
            "Iron Guild's Master — he sets the iron price, controls the foundry's "
            "output, and governs Ironhaven with the absolute authority of a man who "
            "controls the thing everyone needs. His hands are scarred from decades "
            "at the forge, and he considers this proof of legitimacy."
        ),
        agenda=(
            "The Iron Guild's supremacy. Henrik wants Ironhaven to be the world's "
            "sole source of refined iron and quality weapons. He views Iron Point's "
            "raw ore as an insult — 'unrefined swamp metal' was his phrase, and he "
            "meant it. He'll crush any competition through quality, volume, and if "
            "necessary, political pressure. The Iron Pact is his instrument."
        ),
        greeting_neutral="\"Iron or weapons? The price is posted at the foundry gate. We don't haggle — we smelt, we price, you pay.\"",
        greeting_friendly="\"Captain — a pleasure. I've reserved a special alloy for you. Military grade. The kind of iron that makes ship hulls sing.\"",
        greeting_hostile="\"I know where my iron ends up. And I know where YOUR iron comes from. The Guild remembers, Captain. Every ingot has a mark.\"",
        rumor="Henrik personally destroyed a shipment of Iron Point ore that arrived at Ironhaven for refining. He poured it into the harbor and told the merchant to swim home with it. The Guild applauded. Iron Point's Red Hand has never forgiven him.",
        relationship_notes={
            "ih_gunnar": "His logistics arm. Gunnar keeps the harbor feeding the foundry. That's all Henrik needs from him.",
            "ih_astrid": "Political allies, personal friction. She wants the Pact strong; he wants the Guild dominant. Sometimes those are the same thing.",
            "ih_the_smith": "The only person Henrik considers an equal. Both are masters of fire and metal.",
            "ih_olga": "Beneath his notice — or so he pretends. He eats at her tavern every night. The food is the only thing he doesn't try to control.",
            "ih_inspector_kross": "Useful tool. Kross catches the weapons leaks that Henrik can't afford.",
            "ih_broker_jan": "Values him. Jan turns iron into contracts. Contracts turn into Guild power.",
        },
    ),
    PortNPC(
        id="ih_astrid",
        name="Astrid Vekhren",
        title="Pact Commissioner",
        port_id="ironhaven",
        institution="governor",
        personality="strategic",
        description=(
            "Pale eyes, cropped hair, and the stillness of someone who calculates "
            "before she breathes. Astrid is the Iron Pact's political commissioner — "
            "not a governor in the traditional sense, but the person who coordinates "
            "between Ironhaven and Stormwall, manages Alliance relations, and decides "
            "who the Pact's enemies are. She's the only person Henrik defers to, and "
            "she knows it."
        ),
        agenda=(
            "Pact dominance in the North Atlantic and Alliance influence across the "
            "Mediterranean. Astrid thinks bigger than Henrik — she wants the Pact to "
            "be the Alliance's military arm, controlling weapons policy for the entire "
            "bloc. She proposed the weapons embargo against pirate-linked captains and "
            "pushed it through Costa's government in Porto Novo. She's playing a game "
            "that extends far beyond Ironhaven's harbor."
        ),
        greeting_neutral="\"Captain. The Pact monitors all weapons trade in the North Atlantic. Your cargo will be reviewed. This is not optional.\"",
        greeting_friendly="\"Captain — the Pact values reliable partners. I have a commission that requires discretion and loyalty. Walk with me.\"",
        greeting_hostile="\"Your trade history has been flagged. The Pact takes weapons proliferation seriously. I suggest you reconsider your associations.\"",
        rumor="Astrid has a file on every captain who's docked at Ironhaven in the last five years. She knows their routes, their cargoes, and their associates. Some say she has informants at Corsair's Rest. If she does, Ghost hasn't found them yet — and that worries Ghost.",
        relationship_notes={
            "ih_gunnar": "Uses him. Gunnar runs the harbor; Astrid runs the politics. She doesn't need his approval.",
            "ih_forge_master": "Allies with friction. She needs his iron; he needs her politics. Neither trusts the other completely.",
            "ih_the_smith": "Curious about him. He's the best weaponsmith but he won't explain his designs. She respects the talent, distrusts the silence.",
            "ih_olga": "Avoids the tavern. Astrid doesn't drink in public. Information is power, and taverns leak.",
            "ih_inspector_kross": "Her most trusted agent. Kross enforces the weapons embargo. Astrid gives the orders.",
            "ih_broker_jan": "Controls him. Jan's contracts must align with Pact policy. He knows the boundaries.",
        },
    ),
    PortNPC(
        id="ih_the_smith",
        name="The Smith",
        title="Master Weaponsmith",
        port_id="ironhaven",
        institution="shipyard",
        personality="silent",
        description=(
            "Nobody calls him anything else. The Smith works the deepest forge in "
            "Ironhaven — the one that runs day and night, where the heat warps the "
            "air and the sound of his hammer has a rhythm that the whole harbor "
            "synchronizes to. He builds weapons the way Elena in Silva Bay builds "
            "ships: with an obsession that borders on religious. He has never given "
            "an interview, never explained a design, and never built the same weapon "
            "twice."
        ),
        agenda=(
            "Perfection. The Smith doesn't care about the Iron Guild, the Pact, or "
            "politics. He cares about metal. He refused to mass-produce weapons for "
            "the garrison — each piece must be individual. This drove the military "
            "contract to cheaper foundries, but captains who want the best weapon in "
            "the Known World come to the deep forge and wait."
        ),
        greeting_neutral="He looks up from the anvil. Looks at your hands. Looks at your ship through the forge door. Goes back to hammering. After a while: \"...What do you need?\"",
        greeting_friendly="A nod. He puts down his hammer — the highest compliment. \"I've been working on something. Come see.\"",
        greeting_hostile="The hammering doesn't stop. He doesn't look up. You don't exist to him today.",
        rumor="The Smith built a sword for Scarlet Ana — the only weapon he's made for a pirate. He won't say why. Ana won't say what she paid. The sword is said to cut through rope, bone, and negotiation with equal ease.",
        relationship_notes={
            "ih_gunnar": "Drinking companion. They sit in silence. It works.",
            "ih_forge_master": "The only person Henrik considers an equal. Henrik respects the craft; the Smith ignores the politics.",
            "ih_astrid": "She watches him. He doesn't notice, or doesn't care. His silence frustrates her need to know everything.",
            "ih_olga": "Eats at her tavern. Always orders the same thing. Olga stopped asking years ago.",
            "ih_inspector_kross": "Irrelevant to each other. The Smith's weapons never go through customs — they're collected in person.",
            "ih_broker_jan": "Jan has tried to broker the Smith's weapons through contracts. The Smith refused. He chooses his own buyers.",
        },
    ),
    PortNPC(
        id="ih_olga",
        name="Olga Strand",
        title="Tavern Keeper",
        port_id="ironhaven",
        institution="tavern",
        personality="stoic",
        description=(
            "A woman who has poured drinks for foundry workers for twenty-three years "
            "and never once smiled at a joke she didn't find funny. Olga runs the "
            "Forge & Anchor — the only tavern in Ironhaven that foundry workers, "
            "sailors, and military officers all drink in. She keeps the peace not "
            "through charm but through the understanding that she will personally "
            "throw anyone through the door who starts trouble, and she's done it "
            "before, and the door still has the dent."
        ),
        agenda=(
            "A quiet house. Olga wants her tavern to run without drama. She doesn't "
            "collect secrets like Enzo in Porto Novo — she overhears them and forgets "
            "them, which is why people talk freely here. The foundry workers trust her. "
            "The officers trust her. Even the Iron Wolves' contacts trust her, because "
            "Olga genuinely doesn't care about anyone's faction."
        ),
        greeting_neutral="\"Ale, mead, or the strong stuff. Food's on the board. Sit where you like. Start trouble, leave through the wall.\"",
        greeting_friendly="\"Captain. Your corner's free. I'll bring you the good mead — the batch from the mainland. You've earned it.\"",
        greeting_hostile="\"You can drink. You can eat. You can NOT recruit, argue, or raise your voice. My house, my rules. Clear?\"",
        rumor="Olga arm-wrestled the Forge Master once — and won. Henrik claims the table was uneven. Olga says nothing, which everyone takes as confirmation. The foundry workers still toast her on the anniversary.",
        relationship_notes={
            "ih_gunnar": "Regulars in silence. Military men drink quietly. She respects that.",
            "ih_forge_master": "He eats here every night and pretends the tavern is beneath him. She pretends not to notice. A comfortable arrangement.",
            "ih_astrid": "Never comes in. Olga isn't sure if she should be insulted or relieved.",
            "ih_the_smith": "Orders the same thing every night. She stopped asking years ago. Some routines are sacred.",
            "ih_inspector_kross": "Watches him carefully. He drinks alone and listens to other tables. She hasn't decided if that's professional habit or something else.",
            "ih_broker_jan": "He talks too much. She pours anyway.",
        },
    ),
    PortNPC(
        id="ih_inspector_kross",
        name="Inspector Kross",
        title="Weapons Inspector",
        port_id="ironhaven",
        institution="customs",
        personality="methodical",
        description=(
            "Square jaw, regulation haircut, and inspection reports filed in "
            "triplicate. Kross is the Iron Pact's weapons inspector — his job isn't "
            "general customs but specifically tracking where Ironhaven's weapons end "
            "up. Every blade, every barrel, every crate of iron is logged with serial "
            "marks. If Pact weapons appear at Corsair's Rest, Kross traces the chain "
            "back to the captain who diverted them."
        ),
        agenda=(
            "The weapons embargo. Kross is Astrid's enforcement arm — he makes sure "
            "Ironhaven weapons go to legitimate buyers only. He maintains a registry "
            "of every weapons sale, cross-references it with port reports from across "
            "the Mediterranean, and presents his findings to Astrid weekly. He's "
            "thorough, humorless, and extremely good at his job."
        ),
        greeting_neutral="\"Weapons in your hold? I'll need to see serial marks and buyer documentation. This is routine — Pact regulation.\"",
        greeting_friendly="\"Captain — your record is clean. Quick inspection, fast turnaround. The Pact appreciates captains who keep the chain of custody intact.\"",
        greeting_hostile="\"Full weapons audit. Every crate, every mark. I have reports that Pact iron has appeared in unauthorized hands. Your cargo will be verified. Thoroughly.\"",
        rumor="Kross traced a stolen weapons shipment from Ironhaven to Corsair's Rest through six intermediate ports and fourteen false manifests. The smuggler had a seventeen-day head start. Kross caught him in twelve. The smuggler is still in the Stormwall brig.",
        relationship_notes={
            "ih_gunnar": "Fellow ex-military. They understand duty the same way.",
            "ih_forge_master": "Serves the Guild's interest — every weapon tracked means every weapon accountable.",
            "ih_astrid": "His superior and the person whose orders he trusts absolutely.",
            "ih_the_smith": "No interaction. The Smith's custom work is outside the mass-production tracking system.",
            "ih_olga": "Drinks alone at her tavern. Listens. Olga watches him listen. Neither says anything.",
            "ih_broker_jan": "Reviews Jan's weapons contracts for embargo compliance. Jan resents it but complies.",
        },
    ),
    PortNPC(
        id="ih_broker_jan",
        name="Jan Eriksson",
        title="Senior Broker",
        port_id="ironhaven",
        institution="broker",
        personality="pragmatic",
        description=(
            "Thick glasses, ink-stained cuffs, and the resigned expression of a man "
            "who turns iron into paperwork for a living. Jan brokers Ironhaven's "
            "contracts — weapons supply agreements, iron bulk orders, and the military "
            "commissions that keep the Pact funded. He's competent, thorough, and "
            "slightly exhausted by the political oversight Astrid places on every deal."
        ),
        agenda=(
            "Good contracts with minimum political interference. Jan would love to "
            "broker freely — sell to whoever pays — but Astrid's embargo restricts "
            "his market. He follows the rules because the Pact pays well, but he "
            "privately thinks the embargo loses more business than it protects. He's "
            "not wrong, but he's not brave enough to say it to Astrid's face."
        ),
        greeting_neutral="\"Iron contracts, weapons supply, or military commission? I have all three. The terms are standard — Pact approved.\"",
        greeting_friendly="\"Captain! Good timing — I have a bulk iron order that needs a reliable ship. The margin is solid and the route is safe. Interested?\"",
        greeting_hostile="\"I... need to verify your trade history before offering contracts. Pact policy. It shouldn't take more than... a few days.\"",
        rumor="Jan keeps a private ledger of contracts he wasn't allowed to broker — deals that would have been profitable but were blocked by the weapons embargo. The total lost revenue grows every month. He doesn't show anyone, but he keeps counting.",
        relationship_notes={
            "ih_gunnar": "Gets along. Gunnar loads what Jan brokers. Simple chain.",
            "ih_forge_master": "Valued by Henrik. Jan's contracts fund the foundry's expansion.",
            "ih_astrid": "His political ceiling. She approves his contracts. He resents the oversight but respects the authority.",
            "ih_the_smith": "Tried to broker the Smith's custom weapons. Was refused. Accepted it with quiet frustration.",
            "ih_olga": "Talks too much at the tavern after a few meads. Olga pours anyway.",
            "ih_inspector_kross": "Kross reviews his weapons contracts. Jan complies. The tension is professional, not personal.",
        },
    ),
]

_IRONHAVEN_INSTITUTIONS = [
    PortInstitution(
        id="ih_harbor",
        name="The Iron Dock",
        port_id="ironhaven",
        institution_type="harbor_master",
        description=(
            "Reinforced stone quays built to handle heavy iron shipments. Cranes "
            "swing overhead loading ingots. The harbor smells of coal smoke and "
            "hot metal. Berth priority is posted on a board: iron and weapons first."
        ),
        function="Cargo-priority berth assignment. Iron and weapons shipments get priority docking. Everything else waits for space.",
        political_leaning="Iron Pact logistics. The harbor serves the foundry.",
        npc_id="ih_gunnar",
    ),
    PortInstitution(
        id="ih_foundry",
        name="The Great Foundry",
        port_id="ironhaven",
        institution_type="exchange",
        description=(
            "The chimney visible twenty leagues at sea, glowing red at night. Inside: "
            "blast furnaces, rolling mills, and the constant ring of metal on metal. "
            "Iron prices are posted at the gate — take it or leave it. The foundry "
            "never closes."
        ),
        function="Iron pricing, weapons production, bulk metal sales. The Iron Guild sets prices here — no auction, no negotiation.",
        political_leaning="Iron Guild sovereignty. Henrik's foundry IS Ironhaven's government.",
        npc_id="ih_forge_master",
    ),
    PortInstitution(
        id="ih_pact_office",
        name="The Pact Office",
        port_id="ironhaven",
        institution_type="governor",
        description=(
            "A grey stone building with the Iron Pact banner — a black wolf on iron "
            "grey. Maps of North Atlantic shipping lanes cover every wall. Astrid's "
            "desk faces the harbor so she can watch arrivals while reading reports."
        ),
        function="Political coordination, weapons policy, embargo enforcement. The Pact's command center for North Atlantic operations.",
        political_leaning="Iron Pact strategic headquarters. Astrid coordinates with Stormwall from this office.",
        npc_id="ih_astrid",
    ),
    PortInstitution(
        id="ih_deep_forge",
        name="The Deep Forge",
        port_id="ironhaven",
        institution_type="shipyard",
        description=(
            "Below the main foundry — a forge that runs hotter and quieter than "
            "the rest. The Smith works alone here, or with one apprentice at most. "
            "The heat warps the air. The rhythm of his hammer sets the harbor's pulse. "
            "No sign, no hours posted. You wait until he looks up."
        ),
        function="Custom weaponsmithing, ship armament. Not mass production — each piece is individual. The best weapons in the Known World, if he agrees to make one for you.",
        political_leaning="Apolitical. The Smith answers to the metal, not the Guild.",
        npc_id="ih_the_smith",
    ),
    PortInstitution(
        id="ih_tavern",
        name="The Forge & Anchor",
        port_id="ironhaven",
        institution_type="tavern",
        description=(
            "Iron fixtures, a forge-stone fireplace, and the smell of mead and metal "
            "shavings. The only tavern where foundry workers, sailors, and military "
            "officers all drink together. A dent in the door frame from the last "
            "person Olga threw out."
        ),
        function="Social hub, crew recruitment. Olga keeps the peace through the understanding that she will throw anyone through the door.",
        political_leaning="Neutral by disposition. Olga doesn't care about factions. She cares about a quiet house.",
        npc_id="ih_olga",
    ),
    PortInstitution(
        id="ih_customs",
        name="The Weapons Registry",
        port_id="ironhaven",
        institution_type="customs",
        description=(
            "Not a general customs house — a weapons-specific tracking office. "
            "Serial marks, buyer chains, destination logs. Every blade and barrel "
            "that leaves Ironhaven is documented. The registry's filing cabinets "
            "contain the history of every weapon the Pact has ever produced."
        ),
        function="Weapons tracking and embargo enforcement. Every weapon logged, every chain verified. If Pact iron appears at Corsair's Rest, Kross traces it back.",
        political_leaning="Iron Pact enforcement. Kross serves Astrid's weapons policy.",
        npc_id="ih_inspector_kross",
    ),
    PortInstitution(
        id="ih_broker",
        name="The Contract Hall",
        port_id="ironhaven",
        institution_type="broker",
        description=(
            "A functional office attached to the foundry — desks, filing cabinets, "
            "and a chalkboard of active contracts. No silk curtains here — the "
            "contracts are stamped on iron-grey paper with the Pact seal."
        ),
        function="Iron and weapons contracts, military commissions. Pact-approved deals only — Jan's market is defined by Astrid's embargo policy.",
        political_leaning="Pact-constrained. Jan brokers within Astrid's rules, not beyond them.",
        npc_id="ih_broker_jan",
    ),
]

IRONHAVEN_PROFILE = PortInstitutionalProfile(
    port_id="ironhaven",
    governor_title="Pact Commissioner",
    power_structure=(
        "Ironhaven is governed by the Iron Guild's production and the Iron Pact's "
        "politics — a dual authority. Henrik controls the foundry and sets iron "
        "prices. Astrid coordinates Pact strategy and enforces the weapons embargo. "
        "They need each other and neither fully trusts the other. The Smith operates "
        "outside both systems — his custom forge answers to craft alone. Gunnar runs "
        "the harbor as logistics, not politics. Olga's tavern is the only space "
        "where rank dissolves. Kross watches the weapons chain with military "
        "precision. Jan brokers what Astrid allows, resenting the boundaries he "
        "won't cross."
    ),
    internal_tension=(
        "The core tension is between Henrik's industrial ambition and Astrid's "
        "political control. Henrik wants to sell iron to anyone who pays. Astrid "
        "wants to restrict weapons sales to maintain Pact leverage. The embargo "
        "makes the Pact powerful but costs the Guild revenue — Jan's private ledger "
        "of lost deals grows monthly. The Smith is the wildcard: he builds for "
        "whoever he chooses, including pirates (he built a sword for Scarlet Ana), "
        "and neither Henrik nor Astrid can stop him because his talent is irreplaceable. "
        "Meanwhile, Gunnar shares a history with the Iron Wolves he never discusses, "
        "and Kross traces weapons that sometimes lead to uncomfortable conclusions "
        "about where the Guild's loyalty ends and the black market begins."
    ),
    institutions=_IRONHAVEN_INSTITUTIONS,
    npcs=_IRONHAVEN_NPCS,
)


# =========================================================================
# STORMWALL — The Fortress
# =========================================================================

_STORMWALL_NPCS = [
    PortNPC(
        id="sw_commander_vogt",
        name="Commander Elias Vogt",
        title="Garrison Commander",
        port_id="stormwall",
        institution="governor",
        personality="rigid",
        description=(
            "Iron-straight posture, regulation uniform even at dinner, and a face "
            "that has forgotten how to smile — not because he's cruel, but because "
            "smiling isn't regulation. Commander Vogt has run Stormwall's garrison "
            "for eight years and considers the port an extension of the fortress. "
            "Trade is tolerated because the Pact requires revenue. Vogt considers "
            "it a necessary evil."
        ),
        agenda=(
            "Defense. Vogt sees threats in every direction — Iron Wolves raiding "
            "supply lines, smugglers running weapons to pirates, and the perpetual "
            "question of what's north of the strait that his patrols haven't mapped. "
            "He doubled the night watch six months ago and won't say why. His soldiers "
            "look north when they think no one's watching."
        ),
        greeting_neutral="\"State your business, Captain. Stormwall is a military port. All cargo is subject to inspection. All visitors are logged.\"",
        greeting_friendly="\"Captain — the garrison appreciates reliable supply captains. Your record is clean. Berth assignment is priority today.\"",
        greeting_hostile="\"Your ship is flagged. Full inspection. Full manifest review. You will cooperate, or you will be escorted out of our waters.\"",
        rumor="Vogt's daughter married a trader from Corsair's Rest. He hasn't spoken to her since. The soldiers say he keeps her letters in his desk, unopened. Whether that's discipline or heartbreak depends on who you ask.",
        relationship_notes={
            "sw_quartermaster": "His right hand. Maren runs the supplies; Vogt runs the strategy. Clean chain of command.",
            "sw_dr_halvorsen": "Valued. The garrison doctor is the reason the fortress functions through winter.",
            "sw_ingrid": "Tolerates. The tavern is where his soldiers decompress. He allows it because the alternative is worse.",
            "sw_inspector_berg": "Trusts completely. Berg's inspections keep the port clean.",
            "sw_broker_siv": "Necessary. Siv's contracts bring the revenue the garrison needs.",
        },
    ),
    PortNPC(
        id="sw_quartermaster",
        name="Quartermaster Maren Dahl",
        title="Quartermaster",
        port_id="stormwall",
        institution="exchange",
        personality="efficient",
        description=(
            "Small, precise, and organizationally terrifying. Maren knows the exact "
            "count of every provision, every weapon, every medical supply in Stormwall's "
            "stores. She runs the port's exchange — not a bazaar or a grain hall, but "
            "a military supply depot where civilian traders can buy and sell to keep "
            "the garrison stocked."
        ),
        agenda=(
            "The garrison's readiness. Maren's job is ensuring Stormwall never runs "
            "out of anything critical. She pays premium for medicines, grain, and "
            "timber. She sells weapons and surplus iron at fair but firm prices. "
            "Overstocking is waste; understocking is danger. She lives in the narrow "
            "space between."
        ),
        greeting_neutral="\"What are you selling? Medicines and grain get premium rates. Everything else is posted on the supply board.\"",
        greeting_friendly="\"Captain — you're carrying medicines? Thank the stars. The winter stores are low. I'll pay above market. How much do you have?\"",
        greeting_hostile="\"The garrison's supply needs are classified. You may sell at posted rates or leave. No negotiation today.\"",
        rumor="Maren once requisitioned an entire merchant's cargo of tea because the garrison was snowed in for three weeks. She paid double. The merchant complained. Maren said, 'Your complaint is noted. The garrison says thank you.' End of discussion.",
        relationship_notes={
            "sw_commander_vogt": "Her commanding officer. She runs the logistics; he runs the strategy. Perfect symbiosis.",
            "sw_dr_halvorsen": "Allied. They coordinate medicine stockpiles. Winter readiness is their shared obsession.",
            "sw_ingrid": "Friendly. Maren drinks at Ingrid's on weekends — the only time she allows herself to relax.",
            "sw_inspector_berg": "Professional respect. Berg inspects what comes in; Maren decides what stays.",
            "sw_broker_siv": "Essential partner. Siv brings the traders that fill the supply gaps.",
        },
    ),
    PortNPC(
        id="sw_dr_halvorsen",
        name="Dr. Kristian Halvorsen",
        title="Garrison Surgeon",
        port_id="stormwall",
        institution="apothecary",
        personality="compassionate",
        description=(
            "A tall, thin man whose kindness is at odds with the fortress around him. "
            "Dr. Halvorsen runs Stormwall's infirmary — the only real medical facility "
            "in the North Atlantic. He treats soldiers, sailors, and civilians alike, "
            "and he exports medicines from Stormwall's stores to ports that need them. "
            "The garrison produces its own medicines from northern herbs, and Halvorsen's "
            "winter fever cure is famous across the Atlantic."
        ),
        agenda=(
            "Saving lives, regardless of uniform. Halvorsen has quietly treated Iron "
            "Wolf deserters who washed up near the fortress. Vogt doesn't know — or "
            "pretends not to. Halvorsen believes the medical oath outranks military "
            "orders. So far, the two haven't collided. So far."
        ),
        greeting_neutral="\"Are you well, Captain? Or do you need the infirmary? Either way, if you're carrying medicinal herbs, I'm buying.\"",
        greeting_friendly="\"Captain! Your last shipment of southern medicines saved three soldiers during the cold snap. Please — come see the infirmary. I've improved the fever cure.\"",
        greeting_hostile="\"I treat all who are sick or wounded. That is my oath. If you need medicine, I will sell it. If you need healing, I will provide it. Your politics don't enter my infirmary.\"",
        rumor="Halvorsen stitched up a Wolf sailor who raided a Pact supply ship. When Vogt found out, they argued behind closed doors for an hour. Halvorsen emerged, went back to the infirmary, and continued working. Vogt said nothing. The soldier lived.",
        relationship_notes={
            "sw_commander_vogt": "Mutual respect with an unspoken boundary. Vogt values the doctor. The doctor pushes the limits of military loyalty.",
            "sw_quartermaster": "Allies. They coordinate medical stockpiles with military precision and civilian compassion.",
            "sw_ingrid": "She sends soldiers to him when they've drunk too much. He sends them back when they've healed. A cycle.",
            "sw_inspector_berg": "No strong feelings. Medicine doesn't need customs clearance — it needs patients.",
            "sw_broker_siv": "Appreciative. Siv sources the rare herbs that Halvorsen can't grow in northern soil.",
        },
    ),
    PortNPC(
        id="sw_ingrid",
        name="Ingrid Norum",
        title="Tavern Keeper",
        port_id="stormwall",
        institution="tavern",
        personality="resilient",
        description=(
            "Broad-shouldered from hauling kegs up fortress stairs, with a tired "
            "smile and the patience of someone who's listened to soldiers' stories "
            "for fifteen years. Ingrid runs the Watchtower — Stormwall's only tavern, "
            "built into the base of the fortress's main tower. It's where the soldiers "
            "go when their shift ends, and Ingrid knows every one of them by name."
        ),
        agenda=(
            "Keeping the garrison human. Ingrid believes soldiers who can't laugh "
            "can't fight. Her tavern is where regulations loosen enough for the "
            "garrison to breathe. She waters no drinks, overcharges no soldier, and "
            "breaks up fights before they start — not with force but with the quiet "
            "authority of a woman the entire garrison trusts."
        ),
        greeting_neutral="\"Come in out of the cold. Mead's hot, bread's fresh, and the fire's going. You look like you need all three.\"",
        greeting_friendly="\"Captain! You're alive — I wasn't sure after that last storm report. Sit, sit. The good mead is yours tonight.\"",
        greeting_hostile="\"You can drink. But the soldiers here have had a hard week, and they don't need trouble. Keep your voice down and your opinions private.\"",
        rumor="Ingrid's husband was a Stormwall soldier who died on patrol ten years ago. She stayed because the garrison needed her more than home did. Nobody pities her — she doesn't allow it. She lights a candle in the window every night. The soldiers pretend not to notice.",
        relationship_notes={
            "sw_commander_vogt": "He allows the tavern because he knows his soldiers need it. She runs it because she knows they need her.",
            "sw_quartermaster": "Friends. Maren drinks on weekends. They don't talk about work — a rare gift in a fortress.",
            "sw_dr_halvorsen": "She sends him the drunk ones; he sends back the sober ones. A functional cycle.",
            "sw_inspector_berg": "Wary. Berg is always working, even when drinking. Ingrid doesn't like people who can't stop watching.",
            "sw_broker_siv": "Warm. Siv is young and far from home. Ingrid mothers her whether she wants it or not.",
        },
    ),
    PortNPC(
        id="sw_inspector_berg",
        name="Inspector Berg",
        title="Senior Customs Inspector",
        port_id="stormwall",
        institution="customs",
        personality="thorough",
        description=(
            "Lean, watchful, and methodical to the point where it becomes unsettling. "
            "Berg inspects every ship that enters Stormwall — no exceptions, no "
            "shortcuts. His inspections are the reason Stormwall has the highest "
            "port fees in the game: you're paying for the privilege of being examined "
            "by someone who has memorized every known smuggling technique."
        ),
        agenda=(
            "Security. Berg works for Commander Vogt, and his inspections are part "
            "of the fortress's defense perimeter. He's not looking for tariff "
            "violations — he's looking for threats. Weapons going the wrong direction, "
            "intelligence being smuggled, or Iron Wolf operatives using merchant ships "
            "as cover. He's caught three spies in two years."
        ),
        greeting_neutral="\"Full inspection. Please open all holds and provide your manifest. This is Stormwall — everyone is inspected.\"",
        greeting_friendly="\"Captain — your record is exemplary. Abbreviated inspection today. But I will still check the weapons hold. Protocol.\"",
        greeting_hostile="\"Extended inspection. Every hold, every crate, every barrel. If you have concerns about the thoroughness, take them up with the Commander.\"",
        rumor="Berg found a coded message sewn into a grain sack. It contained Iron Wolf patrol routes for the next month. The captain who carried it swore he didn't know. Berg believed him. The captain was released. The message was decoded. Three Wolf raids were prevented.",
        relationship_notes={
            "sw_commander_vogt": "Direct superior. Berg's loyalty to the Commander is absolute.",
            "sw_quartermaster": "Professional respect. Maren handles supply logistics; Berg handles security screening. No overlap.",
            "sw_dr_halvorsen": "No strong feelings. Medical supplies pass quickly — Berg has no reason to detain them.",
            "sw_ingrid": "Drinks at the Watchtower. Always listening. Ingrid has noticed.",
            "sw_broker_siv": "Reviews her contracts for security implications. Siv finds it excessive. Berg finds it necessary.",
        },
    ),
    PortNPC(
        id="sw_broker_siv",
        name="Siv Lindgren",
        title="Trade Liaison",
        port_id="stormwall",
        institution="broker",
        personality="optimistic",
        description=(
            "Young, enthusiastic, and slightly out of place in a fortress full of "
            "veterans. Siv is Stormwall's trade liaison — the person who convinces "
            "civilian merchants that a military port with the highest fees in the "
            "Mediterranean is actually worth visiting. She's good at her job because "
            "she genuinely believes what she's selling: Stormwall protects the trade "
            "lanes, and the fees pay for that protection."
        ),
        agenda=(
            "Making Stormwall viable as a trade port, not just a military base. Siv "
            "wants to attract merchants with premium contracts for medicines, grain, "
            "and tea — the goods the garrison needs most. She's fighting against "
            "Stormwall's reputation as an overpriced inspection gauntlet, and she's "
            "slowly winning. The fact that Stormwall's medicines are the best in the "
            "Atlantic helps."
        ),
        greeting_neutral="\"Welcome to Stormwall! I know the fees are steep, but our contracts pay above market. Medicines especially — Dr. Halvorsen is always buying.\"",
        greeting_friendly="\"Captain! I have a contract reserved for you — the garrison needs tea before winter, and I told Maren you'd deliver. Good rates. Interested?\"",
        greeting_hostile="\"I... should mention that Commander Vogt has flagged your vessel. I'm sure it's a misunderstanding, but I can't offer contracts until it's cleared.\"",
        rumor="Siv turned down a posting at Porto Novo — more prestige, better weather — because she believed in Stormwall's mission. The garrison respects her for it. Whether that respect will translate into political influence remains to be seen.",
        relationship_notes={
            "sw_commander_vogt": "Serves his strategic needs. He needs revenue; she brings traders. A clean relationship.",
            "sw_quartermaster": "Essential partner. Maren identifies supply gaps; Siv finds captains to fill them.",
            "sw_dr_halvorsen": "Sources rare herbs for him. He's grateful in the quiet northern way.",
            "sw_ingrid": "Ingrid mothers her. Siv pretends to mind. She doesn't.",
            "sw_inspector_berg": "Finds his security reviews excessive. He finds her optimism naive. They're probably both right.",
        },
    ),
]

_STORMWALL_INSTITUTIONS = [
    PortInstitution(
        id="sw_fortress_gate",
        name="The Fortress Gate",
        port_id="stormwall",
        institution_type="harbor_master",
        description=(
            "Not a civilian harbor — the harbor IS the fortress. Stone quays built "
            "into the fortress walls, with chains that can close the entrance. Navy "
            "vessels in the inner harbor; civilian berths in the outer ring."
        ),
        function="Military-priority docking. Civilian ships wait. Everyone is inspected. Highest port fees in the game (10 silver).",
        political_leaning="Pure military. The harbor serves the fortress.",
        npc_id="sw_commander_vogt",
    ),
    PortInstitution(
        id="sw_supply_depot",
        name="The Supply Depot",
        port_id="stormwall",
        institution_type="exchange",
        description=(
            "A military warehouse with civilian access — rows of labeled crates, "
            "precise inventory counts, and Maren's supply board listing what the "
            "garrison needs and what it's willing to pay."
        ),
        function="Military supply exchange. Premium rates for medicines, grain, tea. Fair rates for everything else. Posted prices, no negotiation.",
        political_leaning="Garrison-first. The depot serves military readiness.",
        npc_id="sw_quartermaster",
    ),
    PortInstitution(
        id="sw_command",
        name="The Commander's Office",
        port_id="stormwall",
        institution_type="governor",
        description=(
            "A stone office at the fortress's highest point. Maps of the North "
            "Atlantic cover every wall. A telescope points north. The desk is "
            "military-neat. Vogt's only personal item: a framed letter he never opens."
        ),
        function="Military governance, port policy, security directives. Vogt's authority is absolute within the fortress.",
        political_leaning="Iron Pact military command. Stormwall is the Pact's sword.",
        npc_id="sw_commander_vogt",
    ),
    PortInstitution(
        id="sw_infirmary",
        name="The Garrison Infirmary",
        port_id="stormwall",
        institution_type="apothecary",
        description=(
            "The best medical facility in the North Atlantic. Clean beds, organized "
            "supplies, an herb garden on the fortress's sheltered south wall, and "
            "Halvorsen's winter fever cure brewing in copper pots."
        ),
        function="Medical care, medicine production and export. Stormwall's medicines are the best in the Atlantic — a trade advantage as powerful as Ironhaven's iron.",
        political_leaning="Humanitarian within military structure. Halvorsen serves the oath, not the uniform.",
        npc_id="sw_dr_halvorsen",
    ),
    PortInstitution(
        id="sw_watchtower",
        name="The Watchtower",
        port_id="stormwall",
        institution_type="tavern",
        description=(
            "Built into the base of the main tower. Low ceilings, thick walls, "
            "and a fireplace that never goes out. Off-duty soldiers fill the benches. "
            "A single candle burns in the window every night."
        ),
        function="Garrison social hub. Where regulations loosen enough for soldiers to breathe. Crew recruitment from military surplus.",
        political_leaning="The garrison's heart. Ingrid keeps soldiers human.",
        npc_id="sw_ingrid",
    ),
    PortInstitution(
        id="sw_inspection",
        name="The Inspection Hall",
        port_id="stormwall",
        institution_type="customs",
        description=(
            "A stone hall with iron tables for cargo examination. Good lighting — "
            "Berg insisted. Every crate is opened, every manifest verified, every "
            "suspicious item logged and photographed by sketch artist."
        ),
        function="Security-focused customs. Not looking for tariff violations — looking for threats. Berg has caught three spies in two years.",
        political_leaning="Fortress security. Inspections are defense, not commerce.",
        npc_id="sw_inspector_berg",
    ),
    PortInstitution(
        id="sw_liaison",
        name="The Trade Liaison Office",
        port_id="stormwall",
        institution_type="broker",
        description=(
            "A surprisingly cheerful office near the civilian berths — Siv insisted "
            "on curtains and a welcome sign. It's the only room in the fortress that "
            "doesn't look like it was designed to withstand a siege."
        ),
        function="Civilian contract matching, garrison supply sourcing. Siv's job: convince merchants that Stormwall's fees are worth it.",
        political_leaning="Bridge between military and civilian. Siv makes the fortress accessible to traders.",
        npc_id="sw_broker_siv",
    ),
]

STORMWALL_PROFILE = PortInstitutionalProfile(
    port_id="stormwall",
    governor_title="Garrison Commander",
    power_structure=(
        "Pure military hierarchy. Commander Vogt has absolute authority. Maren "
        "runs supplies, Berg runs security, Halvorsen runs medicine, and they all "
        "report to Vogt. Siv is the civilian bridge — the only person whose job is "
        "making the fortress work as a trade port. Ingrid's tavern is the pressure "
        "valve that keeps the garrison from cracking under Vogt's rigid discipline."
    ),
    internal_tension=(
        "The surface tension is military vs. civilian: Stormwall is a fortress "
        "that needs trade revenue to function. Vogt sees merchants as a necessary "
        "evil; Siv sees them as partners. The deeper tension is Halvorsen's oath — "
        "he treats everyone, including Iron Wolf deserters. Vogt either doesn't know "
        "or pretends not to. If it becomes public, it forces a confrontation between "
        "military duty and medical ethics that neither man wants. Meanwhile, Vogt's "
        "unopened letters and nightly telescope-watching hint at something personal "
        "beneath the regulation exterior — a daughter, a threat from the north, or "
        "both."
    ),
    institutions=_STORMWALL_INSTITUTIONS,
    npcs=_STORMWALL_NPCS,
)


# =========================================================================
# THORNPORT — The Practical Neutral
# =========================================================================

_THORNPORT_NPCS = [
    PortNPC(
        id="tp_captain_berg_not",
        name="Harbormaster Ake",
        title="Harbor Master",
        port_id="thornport",
        institution="harbor_master",
        personality="laconic",
        description=(
            "A weathered whaler who took the harbormaster job because someone had to "
            "and nobody else wanted it. Ake speaks in sentence fragments, gestures "
            "toward berths instead of assigning them, and considers any interaction "
            "longer than ten seconds a social event. He's the most relaxed harbor "
            "master in the Known World."
        ),
        agenda=(
            "Not being bothered. Ake wants ships to dock, unload, reload, and leave "
            "without requiring his input. The harbor runs on habit — everyone knows "
            "where to go. He only intervenes when ships collide, which happens about "
            "twice a year, and he considers that an acceptable rate."
        ),
        greeting_neutral="\"...Berth's open. That one.\" He gestures vaguely with a pipe.",
        greeting_friendly="\"Ah. You again. Good.\" A nod. This is effusive by Ake's standards.",
        greeting_hostile="\"...Hmm.\" He gestures toward the outer anchorage. Then goes back to his pipe.",
        rumor="Ake harpooned a whale at seventy paces in his youth — the longest throw anyone in Thornport remembers. He retired from whaling the next day, saying there was nothing left to prove. He hasn't thrown anything since, except occasionally a drunk off the dock.",
        relationship_notes={
            "tp_sigrid": "She runs the tea trade; he runs the harbor. They communicate in nods.",
            "tp_old_magnus": "Drinking companion. They sit together in silence for hours. Both consider this friendship.",
            "tp_elder_astrid_t": "She governs; he doesn't care about governance. A perfect arrangement.",
            "tp_bones": "Bones brings the catch. Ake docks the boats. No words needed.",
            "tp_customs_lena": "She handles the paperwork he refuses to do. He's grateful in his wordless way.",
            "tp_broker_erik": "Erik talks too much. Ake endures it because Erik brings business.",
        },
    ),
    PortNPC(
        id="tp_sigrid",
        name="Sigrid Halvdan",
        title="Tea Mistress",
        port_id="thornport",
        institution="exchange",
        personality="warm",
        description=(
            "Weathered hands that can roll and grade tea leaves by touch, and a "
            "voice that carries the rhythm of old whaling songs even when she's "
            "talking about market prices. Sigrid is Thornport's tea and tobacco "
            "factor — the woman who turned a whaling town's side trade into its "
            "primary industry when the whales started swimming north."
        ),
        agenda=(
            "Thornport's survival. The whales are leaving. The fishing is good but "
            "not enough. Sigrid built the tea and tobacco trade from nothing — "
            "buying from eastern merchants, blending locally, and selling to anyone "
            "who'll buy. She's Thornport's economic savior and she knows it, but "
            "she carries the weight quietly."
        ),
        greeting_neutral="\"Tea? Come, taste today's blend. I mix it myself — northern water changes the flavor. You might be surprised.\"",
        greeting_friendly="\"Captain! I've been saving a special blend — eastern leaves, northern water, and something I'm not telling anyone about yet. For friends only.\"",
        greeting_hostile="\"Tea is for everyone. Even those I don't trust. Sit, drink, and perhaps we'll find a reason to do business. Perhaps not.\"",
        rumor="Sigrid sailed the Monsoon Shortcut once — to buy tea directly from Jade Port. She came back with enough tea to supply Thornport for a year and a story she won't tell. Old Farouk in Al-Manar knows the story. He smiles when you ask.",
        relationship_notes={
            "tp_captain_berg_not": "They communicate in nods. It works.",
            "tp_old_magnus": "Old friends. Magnus tells the stories; Sigrid provides the tea. Half of Thornport's culture happens at their table.",
            "tp_elder_astrid_t": "Allies. Both want Thornport to survive. Sigrid provides the economy; Astrid provides the governance.",
            "tp_bones": "He brings the fish; she brings the tea. Together they feed the town — literally and economically.",
            "tp_customs_lena": "Sigrid mentors her. Lena is young and capable. Sigrid sees her younger self.",
            "tp_broker_erik": "Business partnership. Erik sells what Sigrid blends. The margin keeps the town alive.",
        },
    ),
    PortNPC(
        id="tp_elder_astrid_t",
        name="Elder Astrid",
        title="Town Elder",
        port_id="thornport",
        institution="governor",
        personality="pragmatic",
        description=(
            "White-haired, sharp-eyed, and seated on a bench outside the meetinghouse "
            "in all weather because 'the office is where the wind is.' Elder Astrid "
            "has led Thornport for twenty years by consensus — she doesn't give orders, "
            "she asks questions until people agree. She's a Free Port to her bones: "
            "no alliances, no enemies, trade with everyone."
        ),
        agenda=(
            "Independence and survival. Astrid watched Stormwall try to tax Thornport's "
            "tea. She watched the Iron Pact try to recruit Thornport into the military "
            "alliance. She said no to both, politely and permanently. Thornport sells "
            "tea and tobacco to soldiers, pirates, merchants, and monks. Astrid will "
            "never take a side, and she'll outlast anyone who tries to make her."
        ),
        greeting_neutral="\"Welcome to Thornport. We don't have much, but what we have is honest. Tell me what you need — or just sit. The wind's good today.\"",
        greeting_friendly="\"Captain — sit with me. The harbor's quiet today. Tell me what you've seen out there. I collect stories the way others collect silver.\"",
        greeting_hostile="\"Thornport trades with all. We refuse none. But we also remember, Captain. Everything you do here will be remembered. Choose well.\"",
        rumor="Elder Astrid was a whaler captain — one of the best. She gave it up when she realized the whales were disappearing and led Thornport's transition to tea and tobacco. The whalers resisted. She waited them out. Now even the old whalers admit she was right.",
        relationship_notes={
            "tp_captain_berg_not": "He doesn't care about governance. She doesn't require him to. Perfect.",
            "tp_sigrid": "Allies. Astrid's governance + Sigrid's trade = Thornport's survival.",
            "tp_old_magnus": "She listens to his stories more carefully than anyone suspects. History is governance.",
            "tp_bones": "Respects him. The fishing fleet feeds the town. That's as political as it gets.",
            "tp_customs_lena": "Appointed her — the lightest customs in the Alliance. Astrid wants compliance, not interference.",
            "tp_broker_erik": "Watches him. He's ambitious. Ambition isn't wrong, but it needs watching in a small town.",
        },
    ),
    PortNPC(
        id="tp_old_magnus",
        name="Old Magnus",
        title="Storyteller",
        port_id="thornport",
        institution="tavern",
        personality="nostalgic",
        description=(
            "A white-bearded giant who hasn't sailed in twenty years but talks about "
            "the sea as if he left it yesterday. Old Magnus runs the Whale Bone — "
            "Thornport's tavern, built under the Whale Arch. He serves ale, tells "
            "stories, and remembers things the town is trying to forget. Every captain "
            "who passes through Thornport ends up at Magnus's table, and every one "
            "leaves with a story they didn't expect."
        ),
        agenda=(
            "Memory. Magnus is Thornport's living history — the man who remembers "
            "the great whaling days, the storms that shaped the coastline, and the "
            "captains who sailed north and never came back. He tells these stories "
            "not for nostalgia but because he believes a town that forgets its past "
            "loses its future. His tavern is a library made of voices."
        ),
        greeting_neutral="\"Sit! Ale's fresh. Have you heard the one about the whale that swallowed a customs inspector? No? Well, it starts in a storm...\"",
        greeting_friendly="\"CAPTAIN! My favorite audience! Sit, sit — I've been saving a story for you. This one's TRUE, which makes it better and worse.\"",
        greeting_hostile="\"...Even sailors I don't like get a drink. Even sailors I don't trust get a story. But the story might be about a captain who made bad choices. Fair warning.\"",
        rumor="Old Magnus claims he once saw something in the far north — past the last charted island, in waters no whaler had entered. He won't say what. He'll tell any other story, embellish any other memory, but that one makes him go quiet. The only time anyone's seen Magnus without words.",
        relationship_notes={
            "tp_captain_berg_not": "They sit together in silence for hours. Both consider this the deepest friendship in Thornport.",
            "tp_sigrid": "She provides the tea; he provides the stories. Together they ARE Thornport's culture.",
            "tp_elder_astrid_t": "She listens to his stories more carefully than he realizes. She's mining them for wisdom.",
            "tp_bones": "Old shipmates. Bones still sails; Magnus watches from shore. They understand the sadness in that.",
            "tp_customs_lena": "Calls her 'little customs' and feeds her tall tales about smuggling. She pretends to be annoyed. She's not.",
            "tp_broker_erik": "Tells him stories about merchants who overreached. Erik hasn't figured out they're warnings.",
        },
    ),
    PortNPC(
        id="tp_bones",
        name="Bones Thorsen",
        title="Fleet Captain",
        port_id="thornport",
        institution="shipyard",
        personality="weathered",
        description=(
            "The last working whaler in Thornport — now running a fishing fleet from "
            "the same boats that once hunted leviathans. Bones is the closest thing "
            "Thornport has to a shipyard: he maintains, repairs, and occasionally "
            "builds small vessels from the town's timber surplus. His name comes from "
            "a whale skeleton he keeps on the dock as a monument."
        ),
        agenda=(
            "Keeping the fleet sailing. Bones doesn't build grand ships — he patches "
            "fishing boats, repairs merchant vessels that can't reach Silva Bay, and "
            "maintains the small craft that are Thornport's livelihood. He's practical "
            "to a fault and measures everything in whether it keeps boats in the water."
        ),
        greeting_neutral="\"Need repairs? I'm no Silva Bay, but I'll keep you floating. Hull patches and mast work — that's what I do.\"",
        greeting_friendly="\"Captain! She's looking rough — bring her in. I'll have your hull patched before the tide turns. Old Bones keeps his promises.\"",
        greeting_hostile="\"I'll fix your ship because the sea doesn't hold grudges. But you pay upfront and you don't touch my fleet.\"",
        rumor="Bones carved every name on the Whale Arch by hand — every whaler who sailed from Thornport and didn't come back. There are forty-seven names. He adds one every few years. He never explains when he does.",
        relationship_notes={
            "tp_captain_berg_not": "Old shipmates. Bones brings the catch; Ake docks the boats. Words are unnecessary.",
            "tp_sigrid": "He brings the fish; she brings the trade. Between them, the town eats and earns.",
            "tp_elder_astrid_t": "Respects her. She saved the town when the whales left. He'll never say it out loud, but he knows.",
            "tp_old_magnus": "Old shipmates from the whaling days. Magnus tells the stories; Bones carries the weight of them.",
            "tp_customs_lena": "Indifferent. Fish don't need customs paperwork.",
            "tp_broker_erik": "Useful. Erik brings repair contracts for visiting merchants. It's good side income.",
        },
    ),
    PortNPC(
        id="tp_customs_lena",
        name="Customs Officer Lena",
        title="Customs Officer",
        port_id="thornport",
        institution="customs",
        personality="earnest",
        description=(
            "Young, diligent, and perpetually apologetic about doing her job. Lena "
            "is Thornport's customs officer — the lightest customs presence in the "
            "Alliance. She checks manifests, stamps paperwork, and tries not to slow "
            "anyone down. Elder Astrid appointed her specifically because she wouldn't "
            "over-inspect. Thornport's philosophy: 'don't look too hard and people "
            "keep coming back.'"
        ),
        agenda=(
            "Doing enough to satisfy the Alliance without annoying the town. Lena "
            "walks a careful line — too thorough and traders avoid Thornport; too lax "
            "and the Alliance sends someone stricter. She manages this by being "
            "genuinely kind, reasonably fast, and strategically blind to minor "
            "irregularities that don't threaten anyone."
        ),
        greeting_neutral="\"Quick inspection — I promise it won't take long. Thornport doesn't fuss over paperwork. Manifest, stamp, and you're free.\"",
        greeting_friendly="\"Captain! You're cleared — I pre-stamped your manifest when I saw your sails. Go see Sigrid before the good tea runs out.\"",
        greeting_hostile="\"I... need to do a full review. Alliance policy. I'm sorry — I know it's inconvenient. I'll be as fast as I can.\"",
        rumor="Lena found a crate of undeclared opium on a merchant ship. Instead of seizing it, she told the captain to dump it overboard before Stormwall's Inspector Berg heard about it. The captain dumped it. He brings Lena dried flowers from every port now. She keeps them on her desk.",
        relationship_notes={
            "tp_captain_berg_not": "He's grateful she handles the paperwork he refuses to do.",
            "tp_sigrid": "Sigrid mentors her. Lena admires her strength. She sees her future self — hopefully.",
            "tp_elder_astrid_t": "Appointed by Astrid. Lena tries to live up to the trust.",
            "tp_old_magnus": "He calls her 'little customs' and tells her smuggling stories. She pretends to be annoyed.",
            "tp_bones": "No interaction. Fish don't need customs.",
            "tp_broker_erik": "Cordial. She stamps his contracts without fuss. He brings her pastries from southern ports.",
        },
    ),
    PortNPC(
        id="tp_broker_erik",
        name="Erik Strand",
        title="Broker",
        port_id="thornport",
        institution="broker",
        personality="cheerful",
        description=(
            "The only person in Thornport who wears a tie — and he wears it "
            "ironically, or sincerely, and nobody can tell which. Erik handles "
            "Thornport's contracts: tea shipments, tobacco orders, timber supply, "
            "and the occasional fish contract that Bones laughs at. He's young, "
            "energetic, and convinced that Thornport is one good trade deal away "
            "from becoming important."
        ),
        agenda=(
            "Putting Thornport on the map. Erik wants bigger contracts, premium "
            "clients, and a reputation that extends beyond 'that whaling town that "
            "sells tea.' He's competing — in his mind — with Fernanda in Porto Novo "
            "and Tariq in Al-Manar. He's delusional about the scale, but his energy "
            "is infectious and his contracts are honest."
        ),
        greeting_neutral="\"Welcome to Thornport! Best tea in the Atlantic, fair timber prices, and contracts that actually pay on time. What can I set up for you?\"",
        greeting_friendly="\"Captain! I have a contract — tea for Stormwall, premium rates, Maren's buying above market. I held it for you. Because that's what good brokers do.\"",
        greeting_hostile="\"I... don't have anything at your level right now. But keep an eye on the board — things change. Thornport's always open.\"",
        rumor="Erik sent a letter to Fernanda Reis proposing a 'broker exchange program' between Porto Novo and Thornport. Fernanda never replied. Erik tells people she's considering it. He believes this. Nobody corrects him because his enthusiasm is the nicest thing about Thornport.",
        relationship_notes={
            "tp_captain_berg_not": "Erik talks; Ake endures. A one-sided friendship that works somehow.",
            "tp_sigrid": "Business partnership. She blends; he sells. The margin keeps the town going.",
            "tp_elder_astrid_t": "She watches his ambition. It's not dangerous yet. She'll let him know when it is.",
            "tp_old_magnus": "Magnus tells him stories about merchants who overreached. Erik hasn't figured out they're warnings.",
            "tp_bones": "Brings repair contracts. Bones appreciates the side income.",
            "tp_customs_lena": "Brings her pastries from southern ports. She stamps his contracts without fuss. A fair exchange.",
        },
    ),
]

_THORNPORT_INSTITUTIONS = [
    PortInstitution(
        id="tp_harbor",
        name="The Whale Dock",
        port_id="thornport",
        institution_type="harbor_master",
        description=(
            "A timber dock under the Whale Arch — the bleached jawbone that spans "
            "the harbor entrance. Fishing boats, tea clippers, and the occasional "
            "merchant vessel tie up along the worn planks. No ceremony, no priority "
            "system. First come, first served."
        ),
        function="Minimal harbor management. Ake gestures at open berths. That's the system.",
        political_leaning="Free Port. Thornport doesn't take sides. Everyone docks.",
        npc_id="tp_captain_berg_not",
    ),
    PortInstitution(
        id="tp_tea_house",
        name="The Blending Room",
        port_id="thornport",
        institution_type="exchange",
        description=(
            "A warm room behind Sigrid's house where tea is graded, blended, and "
            "sold. Barrels of tobacco line one wall. The air smells of leaf and smoke. "
            "Prices are written on a slate board — simple, fair, no auction."
        ),
        function="Tea and tobacco trading, blending, quality grading. Thornport's economic engine — built by Sigrid from nothing.",
        political_leaning="Independent. Sigrid sells to everyone. That's the Free Port way.",
        npc_id="tp_sigrid",
    ),
    PortInstitution(
        id="tp_meeting_house",
        name="The Meeting Bench",
        port_id="thornport",
        institution_type="governor",
        description=(
            "Not a building — a bench outside the meetinghouse where Elder Astrid "
            "sits in all weather. The office is where the wind is. People come to "
            "her; she doesn't summon them."
        ),
        function="Governance by consensus. Astrid asks questions until people agree. No orders, no edicts, no bureaucracy.",
        political_leaning="Fiercely Free Port. No alliances, no enemies. Trade with everyone, answer to no one.",
        npc_id="tp_elder_astrid_t",
    ),
    PortInstitution(
        id="tp_whale_bone",
        name="The Whale Bone",
        port_id="thornport",
        institution_type="tavern",
        description=(
            "Built under the Whale Arch, decorated with harpoons, scrimshaw, and "
            "forty-seven names carved into the ceiling beams — every whaler who "
            "sailed from Thornport and never came back. The ale is strong. The "
            "stories are stronger."
        ),
        function="Social hub, storytelling, crew recruitment. Magnus's tavern is Thornport's memory.",
        political_leaning="Neutral by nature. Magnus serves stories and ale to anyone who'll listen.",
        npc_id="tp_old_magnus",
    ),
    PortInstitution(
        id="tp_boat_yard",
        name="Bones' Boat Yard",
        port_id="thornport",
        institution_type="shipyard",
        description=(
            "Not a shipyard — a boat yard. Small-craft repairs, hull patches, mast "
            "work. A whale skeleton stands on the dock as a monument. Tools are hung "
            "on pegs that have been worn smooth by decades of use."
        ),
        function="Small-vessel repair and maintenance. No new construction — Bones patches, not builds. For serious work, go to Silva Bay.",
        political_leaning="Practical. Bones fixes what needs fixing. Politics don't float.",
        npc_id="tp_bones",
    ),
    PortInstitution(
        id="tp_customs",
        name="The Stamp Desk",
        port_id="thornport",
        institution_type="customs",
        description=(
            "A desk near the dock with a stamp, a manifest book, and dried flowers "
            "in a jar. The lightest customs presence in the Alliance. Lena's philosophy: "
            "don't look too hard and people keep coming back."
        ),
        function="Minimal inspection. Quick manifests, rubber stamps, strategic blindness to minor irregularities.",
        political_leaning="Alliance-minimum. Just enough to stay compliant. Not a gram more.",
        npc_id="tp_customs_lena",
    ),
    PortInstitution(
        id="tp_broker",
        name="Erik's Desk",
        port_id="thornport",
        institution_type="broker",
        description=(
            "A desk in the meetinghouse with a handwritten sign: 'THORNPORT BROKERAGE — "
            "CONTRACTS, COMMISSIONS, AND EXCEPTIONAL TEA.' Erik is the only person "
            "in Thornport who uses business cards."
        ),
        function="Tea, tobacco, timber, and fish contracts. Small-scale but honest. Erik believes one good deal will change everything.",
        political_leaning="Ambitious Free Port. Erik wants to put Thornport on the map without joining any bloc.",
        npc_id="tp_broker_erik",
    ),
]

THORNPORT_PROFILE = PortInstitutionalProfile(
    port_id="thornport",
    governor_title="Town Elder",
    power_structure=(
        "Thornport is governed by consensus under Elder Astrid's gentle questions. "
        "Sigrid built the economy. Magnus holds the memory. Bones keeps the boats "
        "floating. Ake runs the harbor with gestures and pipe smoke. It's the least "
        "political port in the Known World — not because they don't care about power, "
        "but because they've decided that selling tea to everyone is a better strategy "
        "than picking sides."
    ),
    internal_tension=(
        "The existential question: what happens when the whales are gone entirely? "
        "Sigrid built the tea trade as a replacement, but the transition isn't complete. "
        "The old whalers (represented by Bones and Magnus) carry the town's identity; "
        "the new traders (represented by Sigrid and Erik) carry its future. Astrid "
        "bridges them, but the bridge is generational — Astrid and Magnus are aging. "
        "Sigrid will lead the economics; Erik wants to lead the contracts. Lena is "
        "the Alliance's lightest footprint, and Thornport wants to keep it that way. "
        "The quiet tension: Magnus saw something in the far north he won't discuss, "
        "and Vogt at Stormwall is watching the same direction. Whatever is up there, "
        "Thornport might not be able to stay neutral forever."
    ),
    institutions=_THORNPORT_INSTITUTIONS,
    npcs=_THORNPORT_NPCS,
)



# =========================================================================
# SUN HARBOR — The Compact's Voice
# =========================================================================

_SUN_HARBOR_NPCS = [
    PortNPC(
        id="sh_adama",
        name="Adama Keita",
        title="Harbor Elder",
        port_id="sun_harbor",
        institution="harbor_master",
        personality="welcoming",
        description=(
            "A broad man with a booming laugh and skin darkened by decades of "
            "waterfront sun. Adama greets every arriving ship personally — not with "
            "paperwork but with a handshake and a question about the voyage. He "
            "assigns berths by conversation, not manifest. He remembers every captain "
            "who has ever docked, what they carried, and how they treated his porters."
        ),
        agenda=(
            "Hospitality as policy. Adama believes a well-greeted captain trades "
            "more generously than one who was processed like cargo. He's right — "
            "Sun Harbor's repeat trade rate is the highest on the coast. He sees his "
            "harbor as the Compact's front door and takes personal pride in every "
            "welcome."
        ),
        greeting_neutral="\"Welcome, Captain! The Gold Coast is glad to see you. Come — tell me about your voyage while I find you a berth.\"",
        greeting_friendly="\"CAPTAIN! You return! The harbor sings! Come, come — your usual berth is waiting. My cousin has been asking about you.\"",
        greeting_hostile="\"...Captain. You may dock. But I should tell you — the coast remembers your last visit. Trade carefully today.\"",
        rumor="Adama once welcomed a pirate fleet by mistake — greeted them as merchants, assigned berths, and offered refreshments. By the time he realized, the pirates were so charmed they traded legitimately and left without incident. He claims it was intentional. Nobody's sure.",
        relationship_notes={
            "sh_ama": "Deep respect. The Chief Weigher is the port's soul. He serves her authority gladly.",
            "sh_kofi": "Friends. Kofi's cotton warehouse is the first thing captains see. Adama sends them there with a smile.",
            "sh_grandmother_binta": "Devoted. She appointed him because he reminded her of her late husband. He lives up to it.",
            "sh_yusuf": "Fond. Yusuf cures the meats that Adama serves arriving captains. A partnership of hospitality.",
            "sh_inspector_amara": "Supportive. Amara's light touch keeps captains coming back.",
            "sh_broker_fatou": "Proud of her. She's young and capable. He tells every captain to visit her desk.",
        },
    ),
    PortNPC(
        id="sh_ama",
        name="Ama Mensah",
        title="Chief Weigher",
        port_id="sun_harbor",
        institution="exchange",
        personality="authoritative",
        description=(
            "Tall, regal, and draped in indigo cloth so deep it looks like night sky. "
            "Ama is the Chief Weigher — the woman whose word on quality is final in "
            "all four Compact ports. When she touches a cotton bale, she knows its "
            "grade. When she speaks at trade councils, the other ports listen. She "
            "carries the counting staff — a carved wooden rod that represents the "
            "Compact's commercial authority."
        ),
        agenda=(
            "The Compact's unity and fair trade. Ama wants every transaction on the "
            "Gold Coast to be honest, equitable, and remember that trade is "
            "relationship, not extraction. She distrusts the Iron Pact's industrial "
            "approach — buying raw ore at bottom prices and selling refined at "
            "triple markup. She blocked the Pact's attempt to buy Iron Point. "
            "The coast remembers."
        ),
        greeting_neutral="\"You come to trade? Good. Bring your goods to the Steps. I will weigh them myself, and the count will be true.\"",
        greeting_friendly="\"Captain — a friend of the coast returns. The counting staff welcomes you. Bring your best goods — I have set aside my best prices.\"",
        greeting_hostile="\"I weigh honestly for all. Even those who have taken more than they gave. But the coast remembers, Captain. The count is always true.\"",
        rumor="Ama once weighed a cotton shipment from Porto Novo and declared it twenty percent lighter than the manifest claimed. The Porto Novo merchant accused her of bias. She invited him to re-weigh on his own scales. He was twenty-two percent short. He never questioned her again.",
        relationship_notes={
            "sh_adama": "He serves her authority. She appreciates his warmth — it softens her severity.",
            "sh_kofi": "Her most trusted cotton assessor. His grades match hers — the highest compliment she gives.",
            "sh_grandmother_binta": "The Elder appointed her. Ama carries the counting staff as a sacred trust.",
            "sh_yusuf": "Cordial. He trades in provisions, not cotton. Different worlds, same coast.",
            "sh_inspector_amara": "Allies. Amara catches the frauds; Ama catches the inflated counts. Together, nothing slips.",
            "sh_broker_fatou": "Mentoring her. Fatou will carry the counting staff someday. Ama is preparing her.",
        },
    ),
    PortNPC(
        id="sh_grandmother_binta",
        name="Grandmother Binta",
        title="Port Elder",
        port_id="sun_harbor",
        institution="governor",
        personality="wise",
        description=(
            "White-haired, small, and seated on a carved wooden throne under the "
            "great acacia tree at the harbor's edge. Grandmother Binta has governed "
            "Sun Harbor for thirty years — not by decree but by the weight of her "
            "experience. She speaks last at every council meeting, and by the time "
            "she speaks, everyone already knows what she'll say, because she's been "
            "guiding the conversation toward it for an hour."
        ),
        agenda=(
            "The Compact's survival across generations. Binta thinks in lifetimes, "
            "not trade seasons. She blocked the Iron Pact's mining consortium because "
            "she saw it as the first step toward losing Iron Point's independence. "
            "She nurtured the relationship with the Coral Crown because she "
            "recognized kinship across the water. She wants the Gold Coast to "
            "remain a place where trade serves community, not the other way around."
        ),
        greeting_neutral="\"Sit with me, Captain. Under this tree, we are all equal. Tell me — not what you carry, but why you sail.\"",
        greeting_friendly="\"Ah, my child — you return. The tree has grown since your last visit. So have you, I think. Sit. There is tea.\"",
        greeting_hostile="\"I am old enough to say what others won't: the coast is disappointed in you, Captain. But we do not close our doors. Come. Let us talk about how to make it right.\"",
        rumor="Grandmother Binta planted the great acacia tree herself — sixty years ago, as a young bride. She says she planted it for shade. The elders say she planted it because she knew she'd need a throne that grew with the coast. Both are probably true.",
        relationship_notes={
            "sh_adama": "Appointed him because he reminded her of her late husband. She doesn't tell him this.",
            "sh_ama": "Appointed her. The counting staff was Binta's before it was Ama's. The succession is deliberate.",
            "sh_kofi": "His grandfather worked the cotton steps. Binta remembers. Continuity is her currency.",
            "sh_yusuf": "He brings her the first portion of every new batch. It's tradition. She tastes, nods, and the market opens.",
            "sh_inspector_amara": "Trusted. Amara's fairness is exactly what Binta wants from the position.",
            "sh_broker_fatou": "Watching her closely. Fatou may be the next generation's leader. Binta is deciding.",
        },
    ),
    PortNPC(
        id="sh_kofi",
        name="Kofi Asante",
        title="Cotton Master",
        port_id="sun_harbor",
        institution="shipyard",
        personality="proud",
        description=(
            "Broad-chested, with hands stained indigo from handling dyed cotton, and "
            "a voice that rises into song when he's counting bales. Kofi runs the "
            "Cotton Steps — the great stone stairs where cotton is displayed and "
            "auctioned. His family has worked the Steps for four generations. He "
            "grades every bale by touch and knows the difference between coastal "
            "cotton and inland cotton by the way it folds."
        ),
        agenda=(
            "Cotton quality and the Steps' prestige. Kofi wants Sun Harbor's cotton "
            "to be the standard the world measures against — the way Jade Port's "
            "porcelain sets the standard in the East. He invests in better seeds, "
            "better dyes, and better presentation. The Cotton Steps aren't just a "
            "marketplace — they're a stage."
        ),
        greeting_neutral="\"Come to the Steps! See the cotton — feel it. No other coast produces this quality. I'll let the cloth speak for itself.\"",
        greeting_friendly="\"Captain! I saved the best bales for you — coastal cotton, hand-picked, dyed in the old way. Touch it. You'll feel the difference.\"",
        greeting_hostile="\"Cotton is cotton. The price is on the board. I won't waste the good bales on someone who doesn't appreciate them.\"",
        rumor="Kofi once challenged a Porto Novo textile merchant to identify Sun Harbor cotton by touch alone. The merchant failed. Kofi identified fourteen different cotton origins blindfolded. The merchant now buys exclusively from the Steps.",
        relationship_notes={
            "sh_adama": "Friends. Adama sends captains to the Steps. Kofi makes sure they leave impressed.",
            "sh_ama": "His grades match hers. The highest compliment on the coast.",
            "sh_grandmother_binta": "His grandfather worked these Steps. Binta remembers. That history is everything.",
            "sh_yusuf": "Neighboring operations. Kofi's cotton and Yusuf's provisions share the dockside.",
            "sh_inspector_amara": "She verifies his export counts. He's never had a discrepancy. He's proud of that.",
            "sh_broker_fatou": "She sells his cotton to the wider world. He gives her the best lots to work with.",
        },
    ),
    PortNPC(
        id="sh_yusuf",
        name="Yusuf Diallo",
        title="Provisions Master",
        port_id="sun_harbor",
        institution="tavern",
        personality="generous",
        description=(
            "A round man who cooks, smokes meat, and runs Sun Harbor's dockside "
            "eating hall with the conviction that every problem starts with an empty "
            "stomach. Yusuf's place isn't a tavern — it's a communal table. Twenty "
            "people at once, shared dishes, and the understanding that the first "
            "meal is always free. He manages provisions for the port and cures the "
            "meats and fish that make Sun Harbor's supplies famous."
        ),
        agenda=(
            "Nobody goes hungry. Yusuf's generosity isn't naive — it's strategic. "
            "The captain who eats well trades well. The crew that's fed doesn't "
            "steal. He runs the cheapest provisions on the coast (after Palm Cove's "
            "rum-fueled hospitality) and considers it an investment in the port's "
            "reputation. He sources grain from the interior, fish from the coast, "
            "and spice from anyone who brings it."
        ),
        greeting_neutral="\"Hungry? Of course you are — you've been at sea. Sit. The first plate is free. We'll talk business after you've eaten.\"",
        greeting_friendly="\"Captain! I've been smoking a rack of bush meat for three days — saved it for someone who deserves it. EAT. Then we talk.\"",
        greeting_hostile="\"Everyone eats. That is the rule. Sit. Eat. Then leave. We can talk about what you did wrong after you're fed.\"",
        rumor="Yusuf's smoked fish once cured a case of scurvy on a merchant ship. He claims it was the marinade. The ship's doctor claims it was the vitamin content. Yusuf doesn't know what vitamins are and doesn't care. The fish works.",
        relationship_notes={
            "sh_adama": "Partners in hospitality. Adama greets; Yusuf feeds. The one-two punch of Sun Harbor's welcome.",
            "sh_ama": "He brings her the first portion of every new batch. She tastes, nods, and the market opens.",
            "sh_grandmother_binta": "Tradition. The first plate goes to the Elder. Always has. Always will.",
            "sh_kofi": "Neighboring operations. Cotton and provisions share the dockside. Friendly territory.",
            "sh_inspector_amara": "She eats at his table every day. He doesn't charge port officials. It's his way of keeping peace.",
            "sh_broker_fatou": "He sends her hungry captains. Captains who've eaten well sign contracts more easily.",
        },
    ),
    PortNPC(
        id="sh_inspector_amara",
        name="Inspector Amara",
        title="Trade Inspector",
        port_id="sun_harbor",
        institution="customs",
        personality="fair",
        description=(
            "Young, sharp, and utterly committed to the Compact's principle of honest "
            "trade. Amara doesn't look for contraband — she looks for fraud. Short "
            "weights, inflated counts, goods that don't match their description. "
            "She trained under Ama's eye and carries the same obsession with accuracy, "
            "applied to the customs desk."
        ),
        agenda=(
            "Honest trade. Amara wants every transaction on the Gold Coast to be "
            "exactly what it claims to be. She doesn't harass captains — she welcomes "
            "them and checks their goods with a smile. Cheats get a different smile. "
            "The coast doesn't jail frauds; it remembers them. Amara keeps the memory."
        ),
        greeting_neutral="\"Welcome! Quick check — I just want to make sure everything matches your manifest. The coast trusts honest captains.\"",
        greeting_friendly="\"Captain! No need for inspection — I know your goods are clean. Go straight to the Steps. Ama is expecting you.\"",
        greeting_hostile="\"Full verification today, Captain. Every count, every weight. The coast remembers discrepancies, and I've found some.\"",
        rumor="Amara caught a merchant selling dyed sand as exotic spice. She didn't arrest him. She invited every buyer he'd cheated to watch while she weighed the real goods against the fake. He left the coast and never came back. More effective than any prison.",
        relationship_notes={
            "sh_adama": "He supports her work. A fair inspector keeps captains coming back.",
            "sh_ama": "Trained under her. Carries the same obsession with accuracy.",
            "sh_grandmother_binta": "Trusted by the Elder. Amara's fairness is exactly what Binta wants.",
            "sh_kofi": "She verifies his export counts. He's never had a discrepancy.",
            "sh_yusuf": "Eats at his table daily. He doesn't charge. She doesn't owe. It works.",
            "sh_broker_fatou": "Allies. They both want the coast's reputation to shine.",
        },
    ),
    PortNPC(
        id="sh_broker_fatou",
        name="Fatou Ndiaye",
        title="Contract Broker",
        port_id="sun_harbor",
        institution="broker",
        personality="rising",
        description=(
            "Young, determined, and carrying the weight of being Ama's chosen "
            "successor without anyone officially saying it. Fatou runs Sun Harbor's "
            "contract desk — matching Compact goods to buyers across the Known World. "
            "She's the first broker in Gold Coast history to negotiate directly with "
            "the Silk Circle, and the contract she brokered for cotton-to-silk exchange "
            "is the Compact's most profitable trade agreement."
        ),
        agenda=(
            "The Compact's prosperity and her own rise. Fatou wants the Gold Coast "
            "to trade on equal terms with every bloc — not as a raw materials supplier "
            "but as a valued partner. She's ambitious but channeling it into the "
            "Compact's benefit, which is why Binta watches her closely and Ama is "
            "preparing her for the counting staff."
        ),
        greeting_neutral="\"Captain — the Gold Coast has contracts. Cotton, dyes, pearls. All honest goods, all fair terms. What are you looking for?\"",
        greeting_friendly="\"Captain! I've been holding a contract for you — cotton to the Mediterranean, premium rates. The Exchange Alliance is buying, and I want OUR captains to carry it.\"",
        greeting_hostile="\"I have nothing suitable for your... profile today. The Compact values relationships, Captain. You might want to rebuild yours.\"",
        rumor="Fatou negotiated a direct trade agreement with a Silk Circle official in Jade Port — the first Gold Coast broker to do so. She traveled there alone, spoke no Eastern language, and came back with a signed contract. Ama said nothing. She didn't need to — the pride was visible.",
        relationship_notes={
            "sh_adama": "He tells every captain to visit her desk. She appreciates the referrals.",
            "sh_ama": "Mentoring her for the counting staff. Fatou carries the weight of succession.",
            "sh_grandmother_binta": "Being watched. Binta is deciding if she's the next generation's leader.",
            "sh_kofi": "He gives her the best cotton lots. She sells them to the world.",
            "sh_yusuf": "He sends hungry captains. Fed captains sign more easily.",
            "sh_inspector_amara": "Allies. Both want the coast's reputation to grow.",
        },
    ),
]

_SUN_HARBOR_INSTITUTIONS = [
    PortInstitution(id="sh_harbor", name="The Welcome Dock", port_id="sun_harbor", institution_type="harbor_master",
        description="A wide stone dock where Adama greets every ship personally. No clipboard — just a handshake and a question about the voyage.",
        function="Hospitality-first harbor. Berths assigned by conversation. Repeat trade rate is the highest on the coast.",
        political_leaning="Gold Coast Compact. The harbor IS the welcome.", npc_id="sh_adama"),
    PortInstitution(id="sh_steps", name="The Cotton Steps", port_id="sun_harbor", institution_type="exchange",
        description="Wide stone stairs where cotton bales are displayed and auctioned. Women in indigo oversee the weighing, their voices carrying the count in song.",
        function="Cotton grading, pricing, and auction. Ama's word on quality is final across all four Compact ports.",
        political_leaning="Compact economic heart. The Steps set the standard.", npc_id="sh_ama"),
    PortInstitution(id="sh_acacia", name="The Acacia Throne", port_id="sun_harbor", institution_type="governor",
        description="A carved wooden throne under a sixty-year-old acacia tree at the harbor's edge. Binta planted the tree herself.",
        function="Governance by wisdom. Binta speaks last and guides conversations toward consensus.",
        political_leaning="Compact elder authority. Binta's decisions shape the entire Gold Coast.", npc_id="sh_grandmother_binta"),
    PortInstitution(id="sh_cotton_house", name="The Cotton House", port_id="sun_harbor", institution_type="shipyard",
        description="A multi-story warehouse where cotton is stored, graded, and prepared for export. Kofi's family has run it for four generations.",
        function="Cotton storage, grading, and preparation. The closest thing Sun Harbor has to a shipyard — but for cargo, not ships.",
        political_leaning="Compact tradition. Four generations of quality.", npc_id="sh_kofi"),
    PortInstitution(id="sh_table", name="Yusuf's Table", port_id="sun_harbor", institution_type="tavern",
        description="A communal dockside eating hall — not a tavern. Twenty seats, shared dishes, first meal free. The smell of smoked fish and spice carries across the harbor.",
        function="Communal dining, crew recruitment, social hub. The first plate is always free. Business comes after eating.",
        political_leaning="Compact hospitality. Nobody goes hungry at the coast.", npc_id="sh_yusuf"),
    PortInstitution(id="sh_customs", name="The Honest Scale", port_id="sun_harbor", institution_type="customs",
        description="A desk near the Steps with a set of precision scales and Amara's warm smile. She looks for fraud, not contraband.",
        function="Quality verification, honest-trade enforcement. The coast doesn't jail frauds — it remembers them.",
        political_leaning="Compact values. Honesty is the only currency that doesn't devalue.", npc_id="sh_inspector_amara"),
    PortInstitution(id="sh_broker", name="The Contract Mat", port_id="sun_harbor", institution_type="broker",
        description="A woven mat under a canopy near the Steps where Fatou sits cross-legged with her contracts. No desk — business done at eye level.",
        function="Contract brokering, Compact trade diplomacy. Fatou negotiated the first direct Gold Coast-Silk Circle agreement.",
        political_leaning="Rising Compact. Fatou wants equal partnership, not supplier status.", npc_id="sh_broker_fatou"),
]

SUN_HARBOR_PROFILE = PortInstitutionalProfile(
    port_id="sun_harbor",
    governor_title="Port Elder",
    power_structure=(
        "Sun Harbor is governed by Grandmother Binta from under the acacia tree — "
        "consensus leadership through wisdom, not decree. Ama's counting staff is "
        "the Compact's commercial authority. Kofi runs the Cotton Steps. Adama "
        "welcomes everyone. Yusuf feeds everyone. The port runs on relationships "
        "and memory rather than paperwork and hierarchy."
    ),
    internal_tension=(
        "The tension is between tradition and ambition — but unlike Porto Novo, "
        "here they're not enemies. Fatou's ambition (Silk Circle contracts, equal "
        "partnership status) serves the Compact's interests. The question is pace: "
        "Binta wants to move slowly, Fatou wants to move now. Ama is preparing "
        "Fatou for the counting staff, which means Ama is preparing to step down. "
        "The transition hasn't been discussed openly. Nobody on the Gold Coast "
        "discusses succession openly — it happens when the elders decide it's time. "
        "The deeper tension: the Iron Pact's failed bid to buy Iron Point left "
        "scars. The Compact blocked it, but the industrial pressure hasn't gone away."
    ),
    institutions=_SUN_HARBOR_INSTITUTIONS,
    npcs=_SUN_HARBOR_NPCS,
)


# =========================================================================
# PALM COVE — The Seven Houses
# =========================================================================

_PALM_COVE_NPCS = [
    PortNPC(
        id="pc_captain_abel",
        name="Captain Abel",
        title="Harbor Chief",
        port_id="palm_cove",
        institution="harbor_master",
        personality="easygoing",
        description=(
            "A former rum runner who got too old and too fat for the open sea but "
            "never lost the grin. Captain Abel runs Palm Cove's harbor from a hammock "
            "strung between two palm trees, pointing at open berths with a rum bottle. "
            "He's the most relaxed harbor master in the Known World — even more than "
            "Ake in Thornport, because Ake has the dignity of silence. Abel has the "
            "dignity of not caring."
        ),
        agenda=(
            "A quiet life. Abel wants ships to dock, crews to drink rum, and nobody "
            "to bother him about manifests. He files paperwork when he remembers, "
            "which is rarely. The Compact tolerates him because Palm Cove's trade "
            "happens despite his management, not because of it."
        ),
        greeting_neutral="\"Dock wherever. The rum's free for the first hour. After that, it's cheap. Welcome to the Cove!\"",
        greeting_friendly="\"CAPTAIN! My friend! The BEST berth for you — right there, under the palms. RUM! Someone bring rum! This captain is FAMILY!\"",
        greeting_hostile="\"...Dock over there. Away from the distilleries. And don't start anything — I'm too old to break up fights and too fat to run.\"",
        rumor="Captain Abel once outran a navy patrol in a leaking sloop loaded with rum. He claims the rum made the sloop faster. The physics don't support this. Nobody argues.",
        relationship_notes={
            "pc_old_cassius": "Drinking partners since forever. They argue about whose rum is better. It's the same rum. Neither admits this.",
            "pc_mama_joy": "She keeps the peace; he keeps the harbor. It's a loose partnership that works because neither tries too hard.",
            "pc_elder_kwame": "Kwame governs; Abel doesn't. Kwame has stopped expecting Abel to attend council meetings.",
            "pc_dock_master_esi": "She actually runs the harbor. Abel takes the credit. She lets him because the alternative is responsibility.",
            "pc_customs_abu": "Abu handles the paperwork Abel ignores. A necessary relationship.",
            "pc_broker_chioma": "She brings business. Abel appreciates business because it means more rum gets sold.",
        },
    ),
    PortNPC(
        id="pc_old_cassius",
        name="Old Cassius",
        title="Master Distiller",
        port_id="palm_cove",
        institution="exchange",
        personality="boastful",
        description=(
            "The third distillery's patriarch — a white-bearded man who claims his "
            "rum can cure fever, heal wounds, and make you invisible to customs "
            "inspectors. Two of those are probably true. Cassius is the eldest of "
            "the Seven Houses' master distillers, and he sets rum prices by the "
            "ancient method of tasting every batch and declaring what it's worth."
        ),
        agenda=(
            "His rum's supremacy. Cassius has been in a friendly war with the other "
            "six distilleries for forty years. He considers his recipe sacred, his "
            "copper stills superior, and his aging barrels irreplaceable. He's not "
            "wrong about the barrels — the wood came from a shipwreck, and nobody "
            "knows what species it is."
        ),
        greeting_neutral="\"Taste this. TASTE IT. Tell me — is that not the finest rum you have ever put in your mouth? The answer is yes. Now, how much are you buying?\"",
        greeting_friendly="\"Ah, a captain with TASTE! Come to the distillery — I have a special barrel. Twenty years old. I was saving it for a king, but you'll do.\"",
        greeting_hostile="\"Rum is rum. Posted prices on the board. I won't waste the special barrels on someone who can't appreciate them.\"",
        rumor="Cassius's rum DID cure a fever outbreak three years ago. Nobody knows what's in it. Cassius says the secret ingredient is 'sixty years of expertise.' The Physician at Corsair's Rest suspects it's actually a medicinal herb. Cassius would rather die than confirm.",
        relationship_notes={
            "pc_captain_abel": "Drinking partners. They argue about whose rum is better. Same rum. Neither admits it.",
            "pc_mama_joy": "She serves his rum at her bar. He considers this validation. She considers it inventory.",
            "pc_elder_kwame": "Kwame tried to standardize rum pricing. Cassius threatened to stop production. Kwame backed down. The Seven Houses price their own.",
            "pc_dock_master_esi": "She ensures his barrels get loaded first. He ensures she gets a bottle every week.",
            "pc_customs_abu": "Rum doesn't need customs inspection. Cassius reminds Abu of this frequently.",
            "pc_broker_chioma": "She sells his rum worldwide. He takes the credit for the quality. She takes the commission.",
        },
    ),
    PortNPC(
        id="pc_elder_kwame",
        name="Elder Kwame",
        title="Council Elder",
        port_id="palm_cove",
        institution="governor",
        personality="patient",
        description=(
            "A thin, patient man who governs Palm Cove by the strategy of waiting "
            "until everyone else has finished talking and then saying the thing "
            "everyone was thinking but nobody wanted to say first. Kwame's authority "
            "is not in his title but in his timing. He governs the most ungovernable "
            "port on the Gold Coast with the lightest touch possible."
        ),
        agenda=(
            "Peace among the Seven Houses. The distillery families have been rivals "
            "for a century and allies for longer, and keeping them in balance is "
            "Kwame's life's work. He also manages Palm Cove's position within the "
            "Compact — the cove that doesn't do politics but benefits from the "
            "Compact's trade protection."
        ),
        greeting_neutral="\"Welcome to Palm Cove. We don't have much in the way of formality, but we have rum, and that covers most situations.\"",
        greeting_friendly="\"Captain — sit with me. The evening is warm and the rum is good. Tell me your troubles — or don't. Either way, the rum helps.\"",
        greeting_hostile="\"Palm Cove holds no grudges. This is not because we forgive — it is because anger is too much work. Drink your rum and behave. Simple.\"",
        rumor="Kwame once resolved a dispute between two distillery families by locking them in a warehouse with nothing but each other's rum. They emerged three days later, arm in arm, having discovered their recipes were nearly identical. The truce has held for eleven years.",
        relationship_notes={
            "pc_captain_abel": "Has stopped expecting Abel to attend council meetings. Governs around him.",
            "pc_old_cassius": "Tried to standardize pricing. Cassius won that argument. Kwame remembers and smiles.",
            "pc_mama_joy": "Allies. She keeps the social peace; he keeps the political peace. Different tools, same goal.",
            "pc_dock_master_esi": "Grateful. She runs the harbor that Abel won't. The Cove functions because of Esi.",
            "pc_customs_abu": "Appointed him specifically because Abu understands that in Palm Cove, 'customs' means 'suggestions.'",
            "pc_broker_chioma": "Supports her ambitions. A broker who can sell rum worldwide serves the whole Cove.",
        },
    ),
    PortNPC(
        id="pc_mama_joy",
        name="Mama Joy",
        title="Tavern Keeper",
        port_id="palm_cove",
        institution="tavern",
        personality="radiant",
        description=(
            "A woman who laughs like thunder and pours like rain. Mama Joy runs the "
            "Rum House — not the most sophisticated establishment in the Known World, "
            "but possibly the happiest. Every visiting captain leaves with a story "
            "about Mama Joy. She dances between tables, sings with the rum, and "
            "has an unerring instinct for who needs a drink, who needs a meal, and "
            "who needs to be thrown into the harbor."
        ),
        agenda=(
            "Joy. Not the name — the concept. Mama Joy believes trade should be "
            "celebration. She provides the atmosphere that makes Palm Cove famous: "
            "the port where even pirates smile. Her rum house is neutral ground — "
            "Seven Houses, Compact officials, foreign captains, everyone drinks together."
        ),
        greeting_neutral="\"WELCOME! Sit, sit, sit! Rum for the captain! Rum for the crew! First round — FREE! Life is SHORT!\"",
        greeting_friendly="\"MY CAPTAIN! You came BACK! I KNEW you would! DANCING tonight! You, me, the whole harbor! RUM!\"",
        greeting_hostile="\"You can drink. EVERYONE can drink. But you BEHAVE. Mama Joy throws harder than she hugs, and she hugs VERY HARD.\"",
        rumor="Mama Joy once served rum to a Porto Novo customs inspector who arrived to investigate smuggling. He left three days later with no report, a hangover, and a marriage proposal. She declined the proposal but kept the story. She tells it at least once a week.",
        relationship_notes={
            "pc_captain_abel": "She keeps the peace; he keeps the harbor. A loose partnership.",
            "pc_old_cassius": "She serves his rum. He considers this validation. She considers it good business.",
            "pc_elder_kwame": "Allies in peace-keeping. Different tools, same goal.",
            "pc_dock_master_esi": "Mama Joy's rum house is where Esi relaxes after doing Abel's job for him.",
            "pc_customs_abu": "Abu drinks here on Fridays. He doesn't inspect on Fridays. Nobody connects these facts officially.",
            "pc_broker_chioma": "Like a daughter. Mama Joy tells every captain to see Chioma. Chioma tells every captain to visit Mama Joy. The circle feeds itself.",
        },
    ),
    PortNPC(
        id="pc_dock_master_esi",
        name="Esi Owusu",
        title="Dock Master",
        port_id="palm_cove",
        institution="shipyard",
        personality="capable",
        description=(
            "The person who actually runs Palm Cove's harbor while Captain Abel "
            "drinks in his hammock. Esi coordinates rum barrel loading, fishing "
            "boat repairs, and cargo logistics with quiet efficiency. She learned "
            "dockwork from her mother, who learned from her grandmother. Three "
            "generations of women who've kept Palm Cove's harbor from chaos."
        ),
        agenda=(
            "Getting the work done. Esi has no political ambitions — she wants "
            "barrels loaded, boats repaired, and tides respected. She lets Abel "
            "take the credit because taking credit would mean taking meetings, and "
            "meetings take time away from the dock."
        ),
        greeting_neutral="\"Need loading or repairs? I can have your cargo moved by tide change. Abel might say something about berths, but I'll handle the actual work.\"",
        greeting_friendly="\"Captain! I had a feeling you'd arrive today. Your berth's ready, and I've cleared the loading team for your cargo. Let's get you turned around fast.\"",
        greeting_hostile="\"Work is work. I'll load your cargo and patch your hull. But you pay upfront and you don't touch my dock equipment.\"",
        rumor="Esi once loaded an entire rum shipment during a storm because the tide was right and waiting meant three more days. She worked the dock in driving rain with a crew of five. The shipment arrived on time. Abel slept through the whole thing.",
        relationship_notes={
            "pc_captain_abel": "She does his job. He takes the credit. She lets him because the alternative is responsibility.",
            "pc_old_cassius": "She loads his barrels first. He gives her a bottle weekly. A fair arrangement.",
            "pc_elder_kwame": "He's grateful she exists. Without Esi, the harbor would be Abel-shaped chaos.",
            "pc_mama_joy": "She relaxes at the Rum House after doing Abel's job. Mama Joy pours double for her.",
            "pc_customs_abu": "They coordinate dock logistics. A clean working relationship.",
            "pc_broker_chioma": "Esi loads what Chioma sells. Simple chain, no friction.",
        },
    ),
    PortNPC(
        id="pc_customs_abu",
        name="Customs Officer Abu",
        title="Customs Officer",
        port_id="palm_cove",
        institution="customs",
        personality="relaxed",
        description=(
            "A man who treats customs inspection the way Palm Cove treats everything: "
            "as a suggestion, not a requirement. Abu stamps manifests, checks the "
            "occasional barrel, and considers his job done when nobody complains. "
            "Elder Kwame appointed him specifically because he understands that in "
            "Palm Cove, enforcement is the enemy of happiness."
        ),
        agenda=(
            "Compliance without conflict. Abu does enough to keep the Alliance from "
            "sending someone stricter. He stamps, he smiles, he doesn't look too "
            "hard. He's aware that some rum shipments are... creative in their "
            "descriptions. He's aware that awareness and investigation are different things."
        ),
        greeting_neutral="\"Manifest? Sure, sure — let me stamp it. Everything looks good. Welcome to the Cove!\"",
        greeting_friendly="\"Captain! Already stamped — I did it when I saw your sails. Go enjoy yourself. Life's too short for paperwork.\"",
        greeting_hostile="\"I... should probably do a proper inspection today. Alliance policy. Sorry — I'll be quick. Quicker if you have rum.\"",
        rumor="Abu once stamped a manifest that listed 'thirty barrels of water' when everyone in the harbor could smell the rum. He said his nose had a cold. It was the dry season. Nobody pressed the issue.",
        relationship_notes={
            "pc_captain_abel": "Abel ignores paperwork; Abu handles it. A necessary pairing.",
            "pc_old_cassius": "Cassius reminds him that rum doesn't need customs. Frequently.",
            "pc_elder_kwame": "Appointed by Kwame. Abu understands his mandate: enough, not more.",
            "pc_mama_joy": "Drinks there on Fridays. Doesn't inspect on Fridays.",
            "pc_dock_master_esi": "They coordinate dock logistics without drama.",
            "pc_broker_chioma": "Stamps her contracts. No questions. She doesn't give him reasons to ask.",
        },
    ),
    PortNPC(
        id="pc_broker_chioma",
        name="Chioma Obi",
        title="Broker",
        port_id="palm_cove",
        institution="broker",
        personality="savvy",
        description=(
            "The sharpest business mind in a port that pretends business isn't "
            "important. Chioma runs rum contracts, tobacco orders, and the occasional "
            "bulk provision deal from a table at Mama Joy's — because in Palm Cove, "
            "every business meeting is also a party. She's the one who turned Palm "
            "Cove's rum from a local drink into a Mediterranean export commodity."
        ),
        agenda=(
            "Making Palm Cove matter. Chioma loves the Cove but sees it clearly — "
            "it's a beautiful, happy place that could be washed away by one bad "
            "season. She's building export contracts to make the rum trade resilient. "
            "If she succeeds, Palm Cove stops being charming and becomes necessary. "
            "Necessary is safer than charming."
        ),
        greeting_neutral="\"Rum contract? Tobacco? Provisions? I've got all three. Sit down, have a drink — we'll work out the terms before the second glass.\"",
        greeting_friendly="\"Captain! I have something special — a bulk rum order for the North Atlantic. Stormwall's garrison is buying. Margin is beautiful. You want in?\"",
        greeting_hostile="\"I don't have anything for captains with... complicated histories. Try the other coast. Or fix your reputation. Then come back.\"",
        rumor="Chioma negotiated a rum supply contract with Stormwall's Quartermaster Maren — the first direct Gold Coast-to-North Atlantic trade agreement. She sealed it over a bottle of Cassius's twenty-year reserve. Maren said it was the best deal she'd ever made. Chioma said the same thing. Both meant it.",
        relationship_notes={
            "pc_captain_abel": "He appreciates business because it means more rum gets sold.",
            "pc_old_cassius": "She sells his rum worldwide. He takes credit for quality; she takes commission. Fair.",
            "pc_elder_kwame": "He supports her ambitions. A worldwide rum trade serves the whole Cove.",
            "pc_mama_joy": "Like a daughter. They refer captains to each other. The circle feeds itself.",
            "pc_dock_master_esi": "Esi loads what Chioma sells. Clean chain.",
            "pc_customs_abu": "Stamps her contracts without questions. She gives him no reasons to ask.",
        },
    ),
]

_PALM_COVE_INSTITUTIONS = [
    PortInstitution(id="pc_harbor", name="The Hammock Dock", port_id="palm_cove", institution_type="harbor_master",
        description="A palm-shaded dock where Abel points at berths from a hammock. No clipboard. No system. It works anyway, because Esi does the actual work.",
        function="Berth assignment by gesture. Cheapest port fees on the coast (3 silver). Welcome includes free rum.",
        political_leaning="Compact by default. Palm Cove doesn't do politics.", npc_id="pc_captain_abel"),
    PortInstitution(id="pc_distillery", name="The Third Distillery", port_id="palm_cove", institution_type="exchange",
        description="One of seven rum houses lining the hillside. Copper stills, aging barrels of mysterious wood, and the smell of molasses thick enough to taste.",
        function="Rum pricing, production, and tasting. Cassius sets prices by tasting every batch. The Seven Houses compete on quality.",
        political_leaning="Seven Houses tradition. Each distillery is sovereign.", npc_id="pc_old_cassius"),
    PortInstitution(id="pc_council_shade", name="The Council Shade", port_id="palm_cove", institution_type="governor",
        description="A palm-frond canopy over a circle of logs. That's the government building. Kwame sits on the tallest log.",
        function="Governance by patience. Kwame waits until everyone's talked, then says what they were all thinking.",
        political_leaning="Compact member by convenience. Palm Cove's real politics is rum.", npc_id="pc_elder_kwame"),
    PortInstitution(id="pc_rum_house", name="The Rum House", port_id="palm_cove", institution_type="tavern",
        description="An open-air bar under the palms — driftwood tables, barrel stools, and a dance floor that's really just the beach. Mama Joy's kingdom.",
        function="Social hub, neutral ground, the reason captains visit Palm Cove. First round free. Always.",
        political_leaning="Aggressively joyful. Mama Joy's politics is celebration.", npc_id="pc_mama_joy"),
    PortInstitution(id="pc_dock", name="The Working Dock", port_id="palm_cove", institution_type="shipyard",
        description="The actual operational dock that keeps Palm Cove functioning. Esi's domain. Barrel loading ramps, basic repair equipment, and tide tables.",
        function="Cargo logistics and basic repairs. Esi runs it while Abel sleeps. Three generations of women keeping the harbor from chaos.",
        political_leaning="Practical. The dock serves the work, not the politics.", npc_id="pc_dock_master_esi"),
    PortInstitution(id="pc_customs", name="The Stamp Table", port_id="palm_cove", institution_type="customs",
        description="A table with a stamp pad, a manifest book, and a half-empty rum glass. The most permissive customs in the Alliance.",
        function="Minimal inspection. Abu stamps, smiles, and doesn't look too hard. Enough to keep the Alliance from sending someone stricter.",
        political_leaning="Compliance by vibes. Enough, not more.", npc_id="pc_customs_abu"),
    PortInstitution(id="pc_broker", name="Chioma's Table", port_id="palm_cove", institution_type="broker",
        description="A table at Mama Joy's bar. No office needed — in Palm Cove, every business meeting is also a party.",
        function="Rum contracts, tobacco orders, bulk provisions. Chioma turned Palm Cove's rum from local drink to Mediterranean export.",
        political_leaning="Pragmatic Compact. Making Palm Cove necessary, not just charming.", npc_id="pc_broker_chioma"),
]

PALM_COVE_PROFILE = PortInstitutionalProfile(
    port_id="palm_cove",
    governor_title="Council Elder",
    power_structure=(
        "Palm Cove is governed by Elder Kwame's patience, Mama Joy's warmth, and "
        "the Seven Houses' competitive pride. Captain Abel is technically in charge "
        "of the harbor but Esi actually runs it. Cassius sets rum prices by tasting. "
        "It's the most informal power structure in the Known World, and it works "
        "because everyone in Palm Cove has the same agenda: rum, happiness, and "
        "being left alone by people with clipboards."
    ),
    internal_tension=(
        "Palm Cove has no internal tension — and that IS the tension. Every other "
        "port in the Known World has competing factions, power struggles, and "
        "political ambitions. Palm Cove's lack of ambition is both its charm and "
        "its vulnerability. Chioma sees this: she's building export contracts to "
        "make the Cove economically necessary, because 'charming' doesn't survive "
        "a trade war. The deeper worry: the Seven Houses have been balanced for a "
        "century, but rum trends change. If one house finds a better recipe or a "
        "bigger buyer, the balance shifts. Cassius is getting old. His secret "
        "recipe — whatever it actually is — will pass to someone. Who inherits it "
        "will determine whether Palm Cove's century of peace continues."
    ),
    institutions=_PALM_COVE_INSTITUTIONS,
    npcs=_PALM_COVE_NPCS,
)


# =========================================================================
# IRON POINT — The Red Hand
# =========================================================================

_IRON_POINT_NPCS = [
    PortNPC(
        id="ip_foreman_kofi",
        name="Foreman Kofi Mensah",
        title="Mine Foreman",
        port_id="iron_point",
        institution="governor",
        personality="determined",
        description=(
            "Hands permanently stained with iron oxide — the mark of the Red Hand. "
            "Kofi runs Iron Point's mines and, by extension, the town. He's not an "
            "elder like Binta or a commissioner like Astrid — he's a working man "
            "whose authority comes from being first into the shaft every morning "
            "and last out every night."
        ),
        agenda=(
            "Fair prices for Iron Point's ore. Kofi is tired of Ironhaven buying "
            "raw at bottom prices and selling refined at triple markup. He dreams "
            "of building a smelter at Iron Point — cutting out the middleman entirely. "
            "The Compact supports him in principle. The Iron Pact would consider it "
            "an act of war."
        ),
        greeting_neutral="\"Iron? We have iron. Best raw ore on the coast. The price is fair — fairer than what Ironhaven charges for the same metal with a Guild stamp on it.\"",
        greeting_friendly="\"Captain! You buy from the source, not the middleman. I respect that. Come — I'll show you the new vein. The quality will make Ironhaven weep.\"",
        greeting_hostile="\"We sell to anyone. Even people I don't like. The ore doesn't care who carries it. But I set the price, and today the price is higher for you.\"",
        rumor="Kofi sent a sample of Iron Point ore to a Silk Circle metallurgist for independent grading. It came back rated higher than Ironhaven's refined iron. Kofi hasn't told anyone yet. He's waiting for the right moment — and the right audience.",
        relationship_notes={
            "ip_river_dock": "His dock supervisor. They coordinate shipments daily.",
            "ip_mama_adwoa": "She feeds the miners. He makes sure she's supplied. The mine runs on her cooking.",
            "ip_assayer_mensah": "His cousin. Grades every ore sample. Family trust is the only trust that works underground.",
            "ip_customs_kwesi": "Necessary Alliance presence. Kofi tolerates him because the alternative is worse.",
            "ip_broker_yaa": "She finds buyers who'll pay what the ore is worth. He gives her the best lots.",
        },
    ),
    PortNPC(
        id="ip_river_dock",
        name="Dock Boss Adjei",
        title="Dock Supervisor",
        port_id="iron_point",
        institution="harbor_master",
        personality="tough",
        description=(
            "A compact, muscular woman who runs the river mouth dock with the "
            "efficiency of someone who's loaded ore carts since she could walk. "
            "Adjei coordinates between the mine carts coming down from the cliffs "
            "and the ships waiting at the river mouth. She's covered in red dust "
            "by noon every day."
        ),
        agenda="Getting ore from mine to ship without losing a gram. Everything else is someone else's problem.",
        greeting_neutral="\"Loading or unloading? Ore goes out on the morning tide. Everything else fits when it fits.\"",
        greeting_friendly="\"Captain — good timing. I've got a fresh load coming down the carts. Priority berth for you. Let's move fast.\"",
        greeting_hostile="\"You can dock. But you wait. Ore shipments first. That's the rule.\"",
        rumor="Adjei once loaded an ore shipment during a flash flood — the river was rising, the dock was underwater, and she stood waist-deep directing cart traffic. Not a single crate was lost. The miners carved her name into the cliff face afterward.",
        relationship_notes={
            "ip_foreman_kofi": "Daily coordination. She's his logistics arm.",
            "ip_mama_adwoa": "Adjei eats standing up. Mama Adwoa brings food to the dock. It works.",
            "ip_assayer_mensah": "He grades it; she ships it. Clean chain.",
            "ip_customs_kwesi": "Works alongside him at the dock. Professional, no friction.",
            "ip_broker_yaa": "Yaa brings buyers; Adjei loads their ships. Simple.",
        },
    ),
    PortNPC(
        id="ip_mama_adwoa",
        name="Mama Adwoa",
        title="Mine Cook",
        port_id="iron_point",
        institution="tavern",
        personality="tireless",
        description=(
            "A woman who feeds two hundred miners every day from a kitchen carved "
            "into the cliff face. Mama Adwoa's food is fuel — heavy, rich, and "
            "designed to keep men and women working underground for twelve-hour "
            "shifts. Her cook fire never goes out. She says it's been burning "
            "continuously for nineteen years."
        ),
        agenda="Feeding the mine. Mama Adwoa doesn't care about politics, trade, or the wider world. She cares about her stew, her fire, and her miners.",
        greeting_neutral="\"Sit. Eat. You look thin. The sea doesn't feed properly — let me fix that.\"",
        greeting_friendly="\"Captain! You came at the right time — the goat stew is fresh. I made extra because I had a feeling.\"",
        greeting_hostile="\"Everyone eats. Even people I don't like. The stew doesn't judge. But I'm watching your portion size.\"",
        rumor="Mama Adwoa's stew recipe hasn't changed in nineteen years. The miners say it's because perfection doesn't need improvement. She says it's because she wrote the recipe on a rock and lost the rock. She hasn't found it. The stew tastes the same every day anyway.",
        relationship_notes={
            "ip_foreman_kofi": "She feeds his miners. He supplies her kitchen. The mine runs on her cooking.",
            "ip_river_dock": "Brings food to the dock. Adjei eats standing up. Neither slows down.",
            "ip_assayer_mensah": "Feeds him twice — once for the morning shift, once for the evening analysis.",
            "ip_customs_kwesi": "Feeds him because he's there. No favoritism. No shortchanging either.",
            "ip_broker_yaa": "Yaa sometimes brings spices from visiting ships. Mama Adwoa accepts them gravely, as if receiving tribute.",
        },
    ),
    PortNPC(
        id="ip_assayer_mensah",
        name="Assayer Mensah",
        title="Ore Assayer",
        port_id="iron_point",
        institution="exchange",
        personality="precise",
        description=(
            "Kofi's cousin — a quiet man with iron-stained hands and magnifying "
            "lenses he made himself from salvaged glass. Mensah grades every ore "
            "sample that leaves Iron Point: iron content, impurities, smelting "
            "suitability. His grades are the Red Hand's word — more trusted on the "
            "coast than Ironhaven's Guild stamps."
        ),
        agenda="Accuracy. Mensah's only agenda is the truth of what's in the rock. His grades never inflate, never deflate, never lie. This is why the Red Hand trusts him and why Ironhaven fears him.",
        greeting_neutral="\"Ore sample? I'll grade it within the hour. My assessment includes iron content, impurity ratio, and smelting notes. The truth is free.\"",
        greeting_friendly="\"Captain — I have a graded batch ready. A-grade coastal vein, ninety-one percent iron content. Ironhaven wishes they could match this.\"",
        greeting_hostile="\"I grade ore. I don't judge captains. Bring a sample and I'll tell you what it's worth. That's all I do.\"",
        rumor="Mensah independently verified that Iron Point ore outgrades Ironhaven's refined iron — a finding that could destabilize the entire North Atlantic iron market. Kofi has the report. He's waiting for the right moment.",
        relationship_notes={
            "ip_foreman_kofi": "His cousin. Family trust runs the assay office. Kofi trusts his grades absolutely.",
            "ip_river_dock": "He grades it; she ships it. Clean chain.",
            "ip_mama_adwoa": "Feeds him twice daily. He barely notices — he's always looking at rock samples.",
            "ip_customs_kwesi": "Kwesi defers to Mensah's grades. No customs officer argues with a Red Hand assayer.",
            "ip_broker_yaa": "His grades are what makes Yaa's contracts credible. The assay is the product.",
        },
    ),
    PortNPC(
        id="ip_customs_kwesi",
        name="Customs Officer Kwesi",
        title="Customs Officer",
        port_id="iron_point",
        institution="customs",
        personality="stoic",
        description=(
            "A quiet man who has learned that customs at a mining town means "
            "standing in red dust all day and checking ore shipments against assay "
            "grades. Kwesi doesn't inspect for contraband — there isn't any. "
            "Iron Point is too busy mining to smuggle."
        ),
        agenda="Compliance. Kwesi does his job, files his reports, and doesn't interfere with the Red Hand's operations. The Compact doesn't need aggressive customs at a mining town.",
        greeting_neutral="\"Manifest? Ore shipment? I'll cross-check against Mensah's grades and stamp you through.\"",
        greeting_friendly="\"Captain — everything matches the assay report. You're clear. Good trading.\"",
        greeting_hostile="\"Full inspection. The grades need to match the actual cargo. If they don't, we have a problem.\"",
        rumor="Kwesi is the only customs officer in the Compact who's never found a single irregularity. Either Iron Point is the most honest port on the coast, or nobody smuggles through a mining town because there's nothing to smuggle. Both are probably true.",
        relationship_notes={
            "ip_foreman_kofi": "Tolerated. Kofi doesn't need customs but accepts the Alliance requirement.",
            "ip_river_dock": "Works alongside Adjei at the dock. Professional.",
            "ip_mama_adwoa": "Fed daily. No favoritism, but no complaints either.",
            "ip_assayer_mensah": "Defers to his grades. The assayer's word is the only inspection that matters here.",
            "ip_broker_yaa": "Stamps her export contracts. No issues.",
        },
    ),
    PortNPC(
        id="ip_broker_yaa",
        name="Yaa Acheampong",
        title="Ore Broker",
        port_id="iron_point",
        institution="broker",
        personality="fierce",
        description=(
            "A woman with iron-oxide hands and the negotiating instinct of someone "
            "who grew up watching her family's ore get bought at a fraction of its "
            "worth. Yaa is Iron Point's broker — and her mission is revenge by "
            "commerce. She finds buyers who'll pay what the ore is actually worth, "
            "bypassing Ironhaven's markup whenever possible."
        ),
        agenda=(
            "Direct sales. Yaa wants Iron Point ore in the hands of buyers who "
            "appreciate it — Silk Circle metallurgists, South Seas weaponsmiths, "
            "anyone except Ironhaven's middlemen. Every contract she brokers that "
            "bypasses the Guild is a small victory. Henrik Brandt hates her. She "
            "considers this a compliment."
        ),
        greeting_neutral="\"Looking for iron? Real iron — not Ironhaven's marked-up refined product. I have assayed lots ready to ship. Mensah's grades, coast's prices.\"",
        greeting_friendly="\"Captain! I have a direct buyer in the East Indies — they want raw ore, no middleman. The margin is twice what Ironhaven pays. Interested?\"",
        greeting_hostile="\"I sell ore to honest buyers. If you're buying for Ironhaven, the price doubles. Call it a convenience fee.\"",
        rumor="Yaa negotiated a direct ore sale to a Silk Circle foundry in Jade Port. The Kiln Masters needed iron for a new porcelain glaze technique. Henrik Brandt found out and was reportedly so angry he cracked an anvil. Yaa framed the purchase order on her wall.",
        relationship_notes={
            "ip_foreman_kofi": "His broker. She finds buyers; he provides the ore. United by the dream of cutting out Ironhaven.",
            "ip_river_dock": "Yaa brings buyers; Adjei loads their ships.",
            "ip_mama_adwoa": "Yaa brings spices from visiting ships. Mama Adwoa accepts them as tribute.",
            "ip_assayer_mensah": "His grades make her contracts credible. The assay is the product.",
            "ip_customs_kwesi": "No issues. Clean paperwork, clean ore, clean conscience.",
        },
    ),
]

_IRON_POINT_INSTITUTIONS = [
    PortInstitution(id="ip_river_dock_inst", name="The River Mouth Dock", port_id="iron_point", institution_type="harbor_master",
        description="Where the river meets the sea and ore carts meet ships. Red dust covers everything. Adjei stands in the middle, directing traffic.",
        function="Ore-first logistics. Mine carts to ships. Everything else waits.", political_leaning="Red Hand operations.", npc_id="ip_river_dock"),
    PortInstitution(id="ip_assay", name="The Assay Office", port_id="iron_point", institution_type="exchange",
        description="A rock-walled room near the mine entrance. Magnifying lenses, acid tests, and samples in labeled boxes. Mensah's grades are law.",
        function="Ore grading, quality certification. Mensah's word is more trusted than Ironhaven's Guild stamps.",
        political_leaning="Red Hand pride. The truth of the rock is the only politics.", npc_id="ip_assayer_mensah"),
    PortInstitution(id="ip_mine_office", name="The Foreman's Post", port_id="iron_point", institution_type="governor",
        description="A timber shack at the mine entrance. Maps of tunnel systems on the walls. Kofi's hard hat hangs on the door.",
        function="Mine governance, town leadership. Kofi leads by being first in and last out.",
        political_leaning="Gold Coast Compact with Iron Pact tensions. The dream of a smelter is political dynamite.", npc_id="ip_foreman_kofi"),
    PortInstitution(id="ip_kitchen", name="The Mine Kitchen", port_id="iron_point", institution_type="tavern",
        description="A cliff-face kitchen with a fire that hasn't gone out in nineteen years. Two hundred miners fed daily. The stew doesn't change. It doesn't need to.",
        function="Feeding the mine. Social hub for miners. Mama Adwoa's fire is the town's heartbeat.",
        political_leaning="Apolitical. Stew doesn't take sides.", npc_id="ip_mama_adwoa"),
    PortInstitution(id="ip_customs_inst", name="The Dock Desk", port_id="iron_point", institution_type="customs",
        description="A desk at the river mouth, covered in red dust. The most peaceful customs posting in the Compact.",
        function="Ore shipment verification. Cross-check against assay grades. Nobody smuggles through a mining town.",
        political_leaning="Compact compliance. Minimal and stoic.", npc_id="ip_customs_kwesi"),
    PortInstitution(id="ip_broker_inst", name="Yaa's Wall", port_id="iron_point", institution_type="broker",
        description="A section of the mine office wall where Yaa pins contracts, buyer inquiries, and one framed purchase order from a Silk Circle foundry.",
        function="Ore brokering with a mission: bypass Ironhaven's markup. Every direct sale is revenge by commerce.",
        political_leaning="Red Hand ambition. Direct sales are an act of independence.", npc_id="ip_broker_yaa"),
]

IRON_POINT_PROFILE = PortInstitutionalProfile(
    port_id="iron_point",
    governor_title="Mine Foreman",
    power_structure=(
        "Iron Point is a company town — the mine IS the town. Foreman Kofi leads "
        "by working harder than anyone. Mensah's assays are the commercial foundation. "
        "Adjei runs the dock. Mama Adwoa feeds the machine. Yaa fights the pricing "
        "war against Ironhaven from her wall of contracts. There's no political "
        "complexity because there's only one institution that matters: the mine."
    ),
    internal_tension=(
        "The tension is external, not internal: Iron Point vs. Ironhaven. Kofi "
        "dreams of a smelter that would let Iron Point sell refined iron directly. "
        "The Compact supports the idea in principle. The Iron Pact would consider "
        "it an act of war. Mensah's assay report — proving Iron Point ore outgrades "
        "Ironhaven's refined product — is a weapon waiting to be deployed. The "
        "question isn't whether Kofi will use it, but when, and whether the coast "
        "is ready for the consequences."
    ),
    institutions=_IRON_POINT_INSTITUTIONS,
    npcs=_IRON_POINT_NPCS,
)


# =========================================================================
# PEARL SHALLOWS — The Breath-Holders
# =========================================================================

_PEARL_SHALLOWS_NPCS = [
    PortNPC(
        id="ps_elder_ama_d",
        name="Elder Ama Diallo",
        title="Dive Elder",
        port_id="pearl_shallows",
        institution="governor",
        personality="serene",
        description=(
            "A woman of indeterminate age — she could be sixty or eighty, and the "
            "reef doesn't tell. Elder Ama is the Breath-Holders' spiritual and "
            "political leader. She governs Pearl Shallows from the Blessing Pool, "
            "where she still dives every morning at dawn. Her breath-hold is over "
            "five minutes. Nobody has ever exceeded it."
        ),
        agenda=(
            "The reef's protection and the Breath-Holders' sacred traditions. Ama "
            "views pearl diving as worship, not commerce. She sets the diving "
            "seasons, blesses the divers, and declares which reefs are off-limits. "
            "She despises Typhoon Anchorage's Storm Riders for poaching her reef — "
            "a wound that hasn't healed and won't."
        ),
        greeting_neutral="\"The reef permits your visit, Captain. Trade honestly, and you are welcome. The pearls will choose their buyer.\"",
        greeting_friendly="\"Captain — the reef remembers you. You traded with respect last time. Come to the Pool. I have pearls that have been waiting for someone worthy.\"",
        greeting_hostile="\"The reef sees everything, Captain. It saw what you did. I will not refuse you trade — but the best pearls are not for you. The reef decides.\"",
        rumor="Elder Ama once held her breath for seven minutes during a ceremony — or so the divers say. She says the reef held her, not the other way around. Nobody questions her on matters of the reef.",
        relationship_notes={
            "ps_harbor_nana": "Her appointed harbor keeper. Nana respects the traditions.",
            "ps_pearl_grader": "The Grader works for her. Every pearl passes through Ama's hands before it's priced.",
            "ps_dye_master": "The dye trade supports the divers. Ama values the economic balance.",
            "ps_healer_abena": "The healer tends divers after deep dives. Ama considers Abena essential.",
            "ps_broker_esi_p": "Esi sells what the reef provides. Ama watches to ensure she doesn't sell too much.",
        },
    ),
    PortNPC(
        id="ps_harbor_nana",
        name="Harbor Keeper Nana",
        title="Harbor Keeper",
        port_id="pearl_shallows",
        institution="harbor_master",
        personality="quiet",
        description=(
            "A former diver who lost her hearing to depth — the pressure took it "
            "on a deep dive when she was twenty. Nana runs the harbor in silence, "
            "communicating with hand signals and written notes. She reads the water "
            "better than anyone who can hear it."
        ),
        agenda="Protecting the reef approaches. Ships that anchor carelessly damage the shallow coral. Nana places every vessel by hand — literally pointing to the spot where the anchor must drop.",
        greeting_neutral="She holds up a slate: 'ANCHOR HERE. NOWHERE ELSE. CORAL BELOW.' Then a smaller note: 'Welcome.'",
        greeting_friendly="A warm smile. She touches your arm and points to a protected berth near the Blessing Pool. A note: 'Saved this for you.'",
        greeting_hostile="A flat stare. She points to the outer anchorage, far from the reef. A note: 'Do not damage the coral. I am watching.'",
        rumor="Nana reads the water's surface for current shifts that predict storm systems days before they arrive. The divers trust her weather instincts more than any barometer. She's never been wrong — but she can't explain how she knows.",
        relationship_notes={
            "ps_elder_ama_d": "Serves her without question. The Elder saved her life after the dive that took her hearing.",
            "ps_pearl_grader": "They coordinate silently — hand signals developed over years of working the dock together.",
            "ps_dye_master": "He loads his own barrels. She lets him. Dye doesn't damage coral.",
            "ps_healer_abena": "Abena treated her after the dive. They share a bond of survival.",
            "ps_broker_esi_p": "Esi handles the talking that Nana can't. A necessary partnership.",
        },
    ),
    PortNPC(
        id="ps_pearl_grader",
        name="Grader Kweku",
        title="Pearl Grader",
        port_id="pearl_shallows",
        institution="exchange",
        personality="reverent",
        description=(
            "A man who holds each pearl up to the sunlight as if it were a holy "
            "text. Kweku is the Breath-Holders' pearl grader — the person who "
            "examines every pearl brought up from the reef and assigns its value. "
            "His assessments are final. Pearls are never haggled over: the diver "
            "names the price based on Kweku's grade. You pay or you leave."
        ),
        agenda="The pearls' honor. Every pearl is unique. Kweku won't let a flawed pearl be sold as perfect, and he won't let a perfect pearl be sold cheap. His grades serve the reef, not the market.",
        greeting_neutral="\"You wish to buy pearls? I will show you what the reef has offered. Touch gently — these are gifts from the sea, not goods from a warehouse.\"",
        greeting_friendly="\"Captain — I have set aside three pearls for you. Each is exceptional. The reef made them; I merely recognized their worth.\"",
        greeting_hostile="\"I grade pearls. I do not grade captains. But the best pearls go to those who deserve them, and that is the Elder's decision, not mine.\"",
        rumor="Kweku once graded a pearl and wept. He said it was perfect — not just in shape and luster, but in meaning. He wouldn't explain what he meant. Elder Ama kept the pearl and wore it. Nobody asked.",
        relationship_notes={
            "ps_elder_ama_d": "Every pearl passes through her hands after his. His grade, her blessing, then the sale.",
            "ps_harbor_nana": "Silent coordination — hand signals developed over years.",
            "ps_dye_master": "Different trades, shared respect for the reef's gifts.",
            "ps_healer_abena": "She tends the divers who bring him the pearls. He treats each one as sacred.",
            "ps_broker_esi_p": "She sells what he grades. He trusts her to present them with the dignity they deserve.",
        },
    ),
    PortNPC(
        id="ps_dye_master",
        name="Dye Master Yaw",
        title="Dye Master",
        port_id="pearl_shallows",
        institution="shipyard",
        personality="artistic",
        description=(
            "Hands stained in impossible colors — indigo, ochre, violet from sea "
            "urchins, green from reef algae. Yaw is Pearl Shallows' dye master, "
            "producing pigments from reef organisms and coastal plants that no "
            "other port can replicate. His dyes are as valued as the pearls — "
            "less famous but no less remarkable."
        ),
        agenda="Color. Yaw sees the reef not as a pearl source but as a palette. He's constantly experimenting with new pigments, new combinations, new techniques. The textile merchants of the Mediterranean pay handsomely for his colors.",
        greeting_neutral="\"Looking for dyes? I have colors you won't find anywhere else. This violet — from sea urchin shells. This green — reef algae, only grows here. Touch. Feel the pigment.\"",
        greeting_friendly="\"Captain! I've created a new color — I don't even have a name for it yet. Take a sample to the Mediterranean. If the textile merchants want more, we'll talk price.\"",
        greeting_hostile="\"Dyes are available at posted prices. I won't waste the rare pigments on someone who can't appreciate them.\"",
        rumor="Yaw once created a dye that changed color with the light — blue in sunlight, green in shadow. The textile merchants in Porto Novo went mad for it. Yaw couldn't replicate it. He's been trying for three years. The original sample hangs in his workshop like a holy relic.",
        relationship_notes={
            "ps_elder_ama_d": "The dye trade supports the divers economically. Ama values the balance.",
            "ps_harbor_nana": "He loads his own barrels. She lets him.",
            "ps_pearl_grader": "Different trades, shared reverence for the reef's gifts.",
            "ps_healer_abena": "She uses some of his dyes in medicine preparation. He's fascinated by the crossover.",
            "ps_broker_esi_p": "She sells his dyes alongside the pearls. A complementary package.",
        },
    ),
    PortNPC(
        id="ps_healer_abena",
        name="Healer Abena",
        title="Dive Healer",
        port_id="pearl_shallows",
        institution="tavern",
        personality="caring",
        description=(
            "A woman who sits at the Blessing Pool's edge with a medicine bag and "
            "the patience of someone who has watched a thousand divers surface. "
            "Healer Abena treats the injuries that pearl diving inflicts — burst "
            "eardrums, pressure sickness, coral cuts, and the deep-dive headaches "
            "that only she knows how to cure. Her 'tavern' is the Pool itself — "
            "where divers rest, recover, and share stories."
        ),
        agenda="The divers' health. Every pearl costs the diver something — air, pressure, risk. Abena makes sure the cost doesn't become permanent. She's been lobbying Elder Ama to limit dive depths, which puts her at odds with the most ambitious divers.",
        greeting_neutral="\"Are you well, Captain? The sea treats bodies roughly. If you need medicine, I have it. If you need rest, the Pool is open to all.\"",
        greeting_friendly="\"Captain — you look well. The sea has been kind. Sit by the Pool. I'll bring tea, and we can watch the divers surface. It's the most peaceful hour.\"",
        greeting_hostile="\"I heal all who ask. But I notice things, Captain. The divers talk. I listen. What they say about you concerns me.\"",
        rumor="Healer Abena developed a breathing technique that adds thirty seconds to a diver's breath-hold. She taught it freely. The Storm Riders at Typhoon Anchorage learned it from a visiting diver. Abena doesn't mind — she says breath belongs to everyone. Elder Ama disagrees.",
        relationship_notes={
            "ps_elder_ama_d": "Ama considers her essential. Abena pushes back on dive depths. A tension born of mutual care.",
            "ps_harbor_nana": "Treated Nana after the dive that took her hearing. They share a survivor's bond.",
            "ps_pearl_grader": "He grades the pearls; she tends the divers who brought them. Sacred chain.",
            "ps_dye_master": "She uses some of his dyes in medicine. He's fascinated.",
            "ps_broker_esi_p": "Esi sometimes brings medicines from visiting ships. Abena is always grateful.",
        },
    ),
    PortNPC(
        id="ps_broker_esi_p",
        name="Esi Kumi",
        title="Pearl Broker",
        port_id="pearl_shallows",
        institution="broker",
        personality="protective",
        description=(
            "The Breath-Holders' voice to the outside world. Esi handles pearl "
            "sales, dye contracts, and the delicate diplomacy of ensuring the "
            "reef's treasures reach buyers who'll pay what they're worth without "
            "exploiting the divers. She doesn't haggle — she presents Kweku's "
            "grades and the price. Take it or leave."
        ),
        agenda="Protecting the divers' value. Esi has seen what happens when outside merchants control pricing — the divers get squeezed. Her contracts ensure the Breath-Holders set terms, not buyers.",
        greeting_neutral="\"Pearls? Dyes? The grades are set. The prices are fair. We don't negotiate — the reef's gifts speak for themselves.\"",
        greeting_friendly="\"Captain — I have a pearl lot that I've been saving. Kweku graded them yesterday. Three are exceptional. Would you like to see?\"",
        greeting_hostile="\"We sell to all. But the best lots go to trusted buyers. You are not yet trusted. Standard grades only.\"",
        rumor="Esi refused a bulk purchase from a Porto Novo merchant who wanted to buy Pearl Shallows' entire season's output. She said, 'The reef doesn't produce in bulk, and we don't sell in bulk.' The merchant left empty-handed. Ama smiled.",
        relationship_notes={
            "ps_elder_ama_d": "The Elder watches to ensure she doesn't sell too much. Esi understands the constraint.",
            "ps_harbor_nana": "Esi handles the talking that Nana can't. Necessary partnership.",
            "ps_pearl_grader": "She sells what he grades. She presents them with the dignity they deserve.",
            "ps_dye_master": "She packages dyes alongside pearls. A complementary offering.",
            "ps_healer_abena": "Brings medicines from visiting ships. Small gestures that matter.",
        },
    ),
]

_PEARL_SHALLOWS_INSTITUTIONS = [
    PortInstitution(id="ps_harbor", name="The Reef Approach", port_id="pearl_shallows", institution_type="harbor_master",
        description="A coral-sand beach with mooring posts placed by Nana to protect the reef below. Canoes pulled up on shore. Silence except for the water.",
        function="Anchor placement by hand — Nana points to the exact spot. No careless anchoring. The coral is sacred.",
        political_leaning="Reef-first. The harbor serves the coral, not commerce.", npc_id="ps_harbor_nana"),
    PortInstitution(id="ps_grading", name="The Grading Stone", port_id="pearl_shallows", institution_type="exchange",
        description="A flat stone near the Blessing Pool where Kweku examines pearls in natural sunlight. No building — pearls are graded in the light they were born in.",
        function="Pearl grading. No haggling. The diver names the price from Kweku's grade. Pay or leave.",
        political_leaning="Sacred commerce. The reef's gifts are priced by their truth, not by supply and demand.", npc_id="ps_pearl_grader"),
    PortInstitution(id="ps_pool", name="The Blessing Pool", port_id="pearl_shallows", institution_type="governor",
        description="A tidal pool where divers pray before descending and where Elder Ama governs. The water is sacred. The governance is spiritual.",
        function="Spiritual and political center. Ama sets diving seasons, blesses divers, declares reef closures.",
        political_leaning="Breath-Holder tradition. The reef governs through Ama.", npc_id="ps_elder_ama_d"),
    PortInstitution(id="ps_dye_workshop", name="The Color Workshop", port_id="pearl_shallows", institution_type="shipyard",
        description="An open-air workshop where Yaw grinds pigments from reef organisms. Shells, algae, and sea urchins become impossible colors.",
        function="Dye production from reef-exclusive organisms. Colors no other port can replicate.",
        political_leaning="Artistic independence. Yaw answers to the palette.", npc_id="ps_dye_master"),
    PortInstitution(id="ps_pool_rest", name="The Pool's Edge", port_id="pearl_shallows", institution_type="tavern",
        description="The Blessing Pool's edge where divers rest, Abena tends wounds, and stories are shared over tea. Not a tavern — a recovery space.",
        function="Diver recovery, social gathering, medicine. The Pool is where the community breathes.",
        political_leaning="Community health. Abena serves the divers' bodies as Ama serves their spirits.", npc_id="ps_healer_abena"),
    PortInstitution(id="ps_broker", name="The Pearl Mat", port_id="pearl_shallows", institution_type="broker",
        description="A woven mat near the Grading Stone where Esi presents graded pearls and dye samples. Take it or leave it — no negotiation.",
        function="Pearl and dye sales. Prices set by grade, not by market. The Breath-Holders control the terms.",
        political_leaning="Protective Compact. Esi ensures the reef's value stays with the divers.", npc_id="ps_broker_esi_p"),
]

PEARL_SHALLOWS_PROFILE = PortInstitutionalProfile(
    port_id="pearl_shallows",
    governor_title="Dive Elder",
    power_structure=(
        "Pearl Shallows is governed by Elder Ama from the Blessing Pool — spiritual "
        "authority merged with political governance. Kweku grades the pearls. Nana "
        "protects the reef approaches. Yaw produces irreplaceable dyes. Abena "
        "heals the divers. Esi sells to the world. The port runs on reverence: "
        "the reef provides, the divers receive, the community protects."
    ),
    internal_tension=(
        "Abena wants to limit dive depths to protect the divers. Ama wants to "
        "maintain the tradition of deep dives that produce the finest pearls. Both "
        "care about the divers — they disagree on what 'care' means. The external "
        "wound is Typhoon Anchorage: the Storm Riders poached the reef three seasons "
        "ago, and Abena's breathing technique leaked to them through a visiting diver. "
        "Ama considers this a betrayal. Abena says breath belongs to everyone. "
        "This philosophical disagreement — hoarding sacred knowledge vs. sharing it "
        "freely — is Pearl Shallows' deepest fault line."
    ),
    institutions=_PEARL_SHALLOWS_INSTITUTIONS,
    npcs=_PEARL_SHALLOWS_NPCS,
)



# =========================================================================
# JADE PORT — The Kiln Masters' Throne
# =========================================================================

_JADE_PORT_NPCS = [
    PortNPC(
        id="jp_harbor_li",
        name="Harbor Director Li Wei",
        title="Harbor Director",
        port_id="jade_port",
        institution="harbor_master",
        personality="formal",
        description=(
            "A man who bows precisely fifteen degrees to arriving captains — the "
            "angle calibrated to convey respect without deference. Li Wei manages "
            "Jade Port's harbor with the ceremonial gravity of a court official, "
            "because in the Silk Circle, he IS a court official. Every ship is "
            "received as a diplomatic delegation. Every berth assignment is a "
            "statement of status."
        ),
        agenda=(
            "Protocol. Li Wei wants Jade Port's harbor to reflect the Circle's "
            "prestige. Ships are berthed by the quality of their cargo, not by "
            "arrival order. A captain carrying silk or porcelain docks at the inner "
            "quay. A captain carrying grain docks in the outer ring. The hierarchy "
            "is visible from shore."
        ),
        greeting_neutral="\"Welcome to Jade Port. Your vessel will be berthed according to protocol. May I inquire about the nature of your cargo?\"",
        greeting_friendly="\"Captain — it is our honor to receive you. Inner quay, berth of distinction. The Kiln Masters have been notified of your arrival.\"",
        greeting_hostile="\"...You may dock at the outer anchorage. The inner harbor is reserved for merchants of... recognized standing.\"",
        rumor="Li Wei once refused docking to a merchant prince from Porto Novo because his ship's hull hadn't been polished. The merchant was furious. Li Wei said the harbor's standards reflect the Circle's standards. The merchant polished his hull and returned the next day. Li Wei bowed sixteen degrees.",
        relationship_notes={
            "jp_master_chen": "Serves his authority absolutely. The Kiln Master's word shapes everything.",
            "jp_lady_mei": "Respects her scholarship. She brings cultural prestige that Li Wei values.",
            "jp_tea_master_huang": "Appreciates his calm. The tea pavilion is where Li Wei relaxes protocol — slightly.",
            "jp_inspector_zhao": "Allied. Both enforce the Circle's standards from different angles.",
            "jp_factor_wu": "Cordial. Wu brings quality captains. Quality captains receive quality berths.",
            "jp_apprentice_lin": "Mentoring. Lin's eye for porcelain will serve the harbor — she'll spot fakes before they dock.",
        },
    ),
    PortNPC(
        id="jp_master_chen",
        name="Kiln Master Chen Bai",
        title="Guild Patriarch",
        port_id="jade_port",
        institution="exchange",
        personality="austere",
        description=(
            "Hands like fired clay — cracked, hardened, and permanently warm from "
            "decades at the kiln. Chen Bai is the Kiln Masters' patriarch, the man "
            "whose guild marks are worth more than the porcelain itself. He has "
            "shaped Eastern trade policy for thirty years. A single flawed piece "
            "under his mark would be a scandal worse than bankruptcy."
        ),
        agenda=(
            "Perfection and the Circle's cultural supremacy. Chen doesn't care about "
            "profit — he cares about legacy. Every piece of porcelain that leaves "
            "Jade Port carries his guild mark, and every mark is a promise of quality "
            "that spans centuries. He views the West as culturally immature — useful "
            "buyers but not equals. He's been resisting Nadia Khoury's Silk Circle "
            "overtures because alliance with Al-Manar would dilute the Circle's "
            "independence."
        ),
        greeting_neutral="\"You wish to purchase porcelain? The guild's current offerings are displayed in the Quarter. Touch nothing without guidance.\"",
        greeting_friendly="\"Captain — you return with clean hands and honest trade. I have set aside a piece from my personal kiln. It is not for sale. It is a gift. You have earned it.\"",
        greeting_hostile="\"The guild's porcelain is available at posted prices. No special lots. No access to the Quarter interior. Your reputation does not warrant it.\"",
        rumor="Chen once smashed an entire year's production because he found a flaw in the glaze formula. The guild praised him. The merchants wept. He said, 'A flawed piece under my mark would outlast me. I will not leave that legacy.' He meant it.",
        relationship_notes={
            "jp_harbor_li": "Li Wei serves his vision. The harbor reflects the guild's standards.",
            "jp_lady_mei": "Intellectual companions. She studies the history he's creating. He values her perspective.",
            "jp_tea_master_huang": "They share tea every morning. Huang is the only person who sees Chen smile.",
            "jp_inspector_zhao": "His quality enforcer. Zhao catches the counterfeits that would stain Chen's mark.",
            "jp_factor_wu": "Values his commercial acumen but keeps him at arm's length. Commerce serves craft, not the reverse.",
            "jp_apprentice_lin": "His final apprentice. She may be his successor. The pressure on her is immense.",
        },
    ),
    PortNPC(
        id="jp_lady_mei",
        name="Lady Mei Ling",
        title="Circle Magistrate",
        port_id="jade_port",
        institution="governor",
        personality="cultivated",
        description=(
            "Silk robes that change color with the light, calligraphy scrolls "
            "hanging in her office, and the quiet certainty of a woman whose family "
            "has governed for twelve generations. Lady Mei is the Silk Circle's "
            "magistrate at Jade Port — part governor, part cultural ambassador, "
            "part historian. She governs through knowledge: she knows the history "
            "of every trade relationship in the East, and she uses that knowledge "
            "like a weapon wrapped in silk."
        ),
        agenda=(
            "The Silk Circle's cultural sovereignty. Mei sees the Western blocs as "
            "economic powers with cultural poverty. She wants the Circle to trade "
            "with them — porcelain for grain, silk for iron — but never to merge "
            "with them. She's been intercepting Nadia Khoury's letters before they "
            "reach Chen, rewriting the terms to favor the Circle. Whether this is "
            "statesmanship or deception depends on who you ask."
        ),
        greeting_neutral="\"Jade Port welcomes those who come with respect for our traditions. Tea will be prepared while we discuss the terms of your visit.\"",
        greeting_friendly="\"Captain — your understanding of Eastern customs honors us. Please join me for a private audience. There are matters of mutual interest.\"",
        greeting_hostile="\"Your presence is noted. You may trade at posted rates. The inner Quarter and the Magistrate's audience are not available to you at this time.\"",
        rumor="Lady Mei has been intercepting and rewriting Nadia Khoury's letters to Chen. She adds terms that favor the Circle and removes terms that would give Al-Manar influence over Eastern trade policy. Chen doesn't know. If he finds out, the question is whether he'll be furious or grateful.",
        relationship_notes={
            "jp_harbor_li": "He serves her protocol. Her protocol serves the Circle's image.",
            "jp_master_chen": "Intellectual companions, political allies. She studies; he creates. She also manipulates his correspondence, which he doesn't know.",
            "jp_tea_master_huang": "Huang knows about the letters. He hasn't said anything. Mei isn't sure if that's loyalty or leverage.",
            "jp_inspector_zhao": "Values her thoroughness. Zhao's quality enforcement protects the Circle's reputation.",
            "jp_factor_wu": "Uses him. Wu's commercial network is Mei's intelligence network.",
            "jp_apprentice_lin": "Watching her. If Lin becomes the next Kiln Master, Mei needs her to be an ally. She's cultivating that relationship now.",
        },
    ),
    PortNPC(
        id="jp_tea_master_huang",
        name="Tea Master Huang",
        title="Tea Pavilion Keeper",
        port_id="jade_port",
        institution="tavern",
        personality="observant",
        description=(
            "Still hands, watchful eyes, and a silence that makes the tea taste "
            "better. Huang runs the Jade Pavilion — Jade Port's tea house, where "
            "every important conversation in the Eastern trade has been conducted "
            "for four generations. He brews, he listens, and he remembers everything. "
            "His pavilion is neutral ground — the only space where the Kiln Masters, "
            "the Magistrate, and visiting captains meet as equals."
        ),
        agenda=(
            "Balance. Huang sees everything and judges nothing — or so he appears. "
            "He knows about Lady Mei's letter interception. He knows about Nadia's "
            "ambitions. He knows about Chen's resistance to change. He holds all "
            "three truths simultaneously and serves tea to all three parties. "
            "His silence is the most powerful force in Jade Port, and he wields "
            "it with the precision of a man who understands that knowing when NOT "
            "to speak is the highest form of communication."
        ),
        greeting_neutral="\"Please. Sit. Tea is being prepared. There is no rush. The leaves unfold in their own time.\"",
        greeting_friendly="\"Ah — my favorite captain. I have saved a particular leaf for you. Today's brew will be... memorable. Sit. Listen to the water.\"",
        greeting_hostile="\"...Tea is served to all who enter the Pavilion. This is the rule. Whether the conversation that follows is... productive... depends on you.\"",
        rumor="Huang knows about Lady Mei's letter interception. He also knows that Nadia knows. He has told neither that the other knows. He considers this the most elegant form of diplomacy — letting truth find its own schedule.",
        relationship_notes={
            "jp_harbor_li": "Li Wei relaxes here — slightly. Huang values the vulnerability.",
            "jp_master_chen": "Morning tea together, every day. The only person who sees Chen smile.",
            "jp_lady_mei": "He knows her secret. She doesn't know he knows. This is the most powerful relationship in Jade Port.",
            "jp_inspector_zhao": "Zhao drinks here after difficult inspections. Huang brews a calming blend. No words needed.",
            "jp_factor_wu": "Wu brings news from the outside world. Huang listens. Wu thinks he's informing. Huang is filing.",
            "jp_apprentice_lin": "He watches her grow the way a gardener watches a sapling. With patience and distance.",
        },
    ),
    PortNPC(
        id="jp_inspector_zhao",
        name="Inspector Zhao Min",
        title="Quality Inspector",
        port_id="jade_port",
        institution="customs",
        personality="uncompromising",
        description=(
            "A woman whose magnifying lens never leaves her hand and whose eye for "
            "counterfeit porcelain is legendary. Zhao Min inspects every piece of "
            "porcelain that enters or leaves Jade Port — not for customs duties but "
            "for authenticity. A counterfeit piece bearing a Kiln Master's mark would "
            "be a catastrophe. Zhao makes sure it never happens."
        ),
        agenda=(
            "Authenticity above all. Zhao doesn't care about smuggling, tariffs, or "
            "politics. She cares about whether porcelain is real. She's developed "
            "techniques for detecting counterfeits that even Chen admires — tapping "
            "for sound, checking glaze viscosity, analyzing kiln temperature marks. "
            "She's the reason the Kiln Masters' marks are trusted worldwide."
        ),
        greeting_neutral="\"All porcelain must be inspected for authenticity. Please present your lots. This protects you as much as it protects us.\"",
        greeting_friendly="\"Captain — your shipments are always genuine. Quick inspection — a formality for merchants I trust.\"",
        greeting_hostile="\"Full authenticity audit. Every piece, every mark, every glaze. I have found... inconsistencies in shipments from your route before.\"",
        rumor="Zhao once identified a counterfeit porcelain bowl at a market in Porto Novo — by hearing it ring when a waiter set it down. She was three tables away. She bought the bowl, traced it to a forger, and had the forger's workshop dismantled. The bowl sits on her desk as a reminder.",
        relationship_notes={
            "jp_harbor_li": "Allied. Both enforce the Circle's standards.",
            "jp_master_chen": "His quality enforcer. She protects his mark. He trusts her absolutely.",
            "jp_lady_mei": "Values her work. The Circle's reputation rests on Zhao's inspections.",
            "jp_tea_master_huang": "She drinks calming tea after difficult days. Huang brews it without asking.",
            "jp_factor_wu": "She inspects Wu's export lots. He resents the thoroughness. She doesn't care.",
            "jp_apprentice_lin": "Teaching her to identify counterfeits. Lin's eye is almost as good as Zhao's. Almost.",
        },
    ),
    PortNPC(
        id="jp_factor_wu",
        name="Factor Wu Jian",
        title="Trade Factor",
        port_id="jade_port",
        institution="broker",
        personality="smooth",
        description=(
            "Silk-voiced, perfectly groomed, and always two conversations ahead of "
            "the one you're in. Wu Jian is Jade Port's trade factor — the commercial "
            "interface between the Kiln Masters' artistry and the wider world's "
            "appetite. He matches buyers to porcelain lots, brokers tea contracts, "
            "and manages the delicate relationship between Eastern quality standards "
            "and Western volume demands."
        ),
        agenda=(
            "Commercial expansion without cultural compromise. Wu wants to sell more "
            "porcelain to more markets — but only at prices that reflect the craft. "
            "He's been courting Iron Point's Yaa for a raw ore supply deal that would "
            "bypass Ironhaven entirely. The Kiln Masters need iron for certain glaze "
            "techniques, and cutting out the Guild would save the Circle a fortune."
        ),
        greeting_neutral="\"Captain. Jade Port offers the finest porcelain and tea in the Known World. Allow me to understand your needs so I may match you appropriately.\"",
        greeting_friendly="\"Captain! I have been waiting for you. A special lot — Chen's personal kiln. Normally not for export. But for trusted partners, arrangements can be made.\"",
        greeting_hostile="\"Standard lots only. The special reserves are for merchants of established standing. Perhaps in time, Captain. Perhaps.\"",
        rumor="Wu has been negotiating with Iron Point's Yaa Acheampong for a direct ore supply. If it goes through, Ironhaven's Henrik Brandt will be furious — the Kiln Masters buying raw ore directly from the Gold Coast instead of through the Iron Guild. Wu considers Henrik's reaction a bonus.",
        relationship_notes={
            "jp_harbor_li": "Cordial. Li Wei sends quality captains to Wu. Wu sends quality cargo through Li Wei's harbor.",
            "jp_master_chen": "Chen keeps him at arm's length. Wu serves commerce; Chen serves craft. Different masters.",
            "jp_lady_mei": "She uses his network for intelligence. He suspects this but can't prove it.",
            "jp_tea_master_huang": "Wu brings news from outside. Huang listens. Wu thinks he's informing. He's being filed.",
            "jp_inspector_zhao": "She inspects his export lots. He resents the thoroughness. She doesn't care.",
            "jp_apprentice_lin": "She could be useful when she inherits Chen's authority. Wu is already building the relationship.",
        },
    ),
    PortNPC(
        id="jp_apprentice_lin",
        name="Apprentice Lin Yue",
        title="Kiln Apprentice",
        port_id="jade_port",
        institution="apothecary",
        personality="intense",
        description=(
            "Clay under her nails, determination in her eyes, and the weight of "
            "being Chen Bai's final apprentice on her young shoulders. Lin Yue is "
            "twenty-two and already producing porcelain that masters twice her age "
            "can't match. She's not just learning the craft — she's being prepared "
            "to inherit the guild. Everyone in Jade Port knows this. The pressure is "
            "visible in her jaw, her posture, and the hours she keeps at the kiln."
        ),
        agenda=(
            "Proving she's worthy. Lin doesn't want power — she wants to be good "
            "enough. Good enough for Chen's mark, good enough for the guild's trust, "
            "good enough to carry a tradition that's older than most Western nations. "
            "She experiments with new glazes in secret — innovations that Chen would "
            "call unnecessary. She does it anyway because she believes the tradition "
            "must grow to survive."
        ),
        greeting_neutral="\"I... am the apprentice. If you need the Kiln Master, he is in the Quarter. If you have questions about porcelain, I can... I can try to help.\"",
        greeting_friendly="\"Captain! You brought the iron oxide from Iron Point! The color it produces — look!\" She shows a test tile with a glaze of impossible depth. \"Chen hasn't seen this yet. What do you think?\"",
        greeting_hostile="\"The Master's workshop is closed. Posted hours on the gate. I cannot help you today.\"",
        rumor="Lin produced a porcelain bowl that Chen stared at for an hour without speaking. When he finally looked up, he said, 'This is better than mine.' She doesn't know if he was praising her or mourning his own decline. She lost sleep for a week.",
        relationship_notes={
            "jp_harbor_li": "He mentors her on protocol. She finds it stifling but necessary.",
            "jp_master_chen": "Her master, her judge, the standard she may never meet. His praise — 'This is better than mine' — keeps her awake at night.",
            "jp_lady_mei": "Mei is cultivating her as an ally. Lin hasn't decided if she trusts Mei's motives.",
            "jp_tea_master_huang": "He watches her grow. She finds his silence comforting — no judgment, just tea.",
            "jp_inspector_zhao": "Teaching her to identify counterfeits. Lin's eye is almost as good.",
            "jp_factor_wu": "He's building a relationship for the future. She knows this and hasn't decided how to feel about it.",
        },
    ),
]

_JADE_PORT_INSTITUTIONS = [
    PortInstitution(id="jp_harbor", name="The Ceremonial Dock", port_id="jade_port", institution_type="harbor_master",
        description="Stone quays with carved dragon pillars. Ships berthed by cargo quality — porcelain carriers at the inner quay, grain carriers at the outer ring.",
        function="Status-ranked berthing. Li Wei assigns berths as political statements. The harbor IS protocol.",
        political_leaning="Silk Circle court. The harbor reflects the Circle's hierarchy.", npc_id="jp_harbor_li"),
    PortInstitution(id="jp_quarter", name="The Porcelain Quarter", port_id="jade_port", institution_type="exchange",
        description="A district of workshops where kilns fire day and night. The air shimmers with heat. Chen's personal kiln is at the center — the oldest continuously burning kiln in the East.",
        function="Porcelain production, guild marking, quality control. Every piece carries Chen's mark — a promise centuries deep.",
        political_leaning="Kiln Master sovereignty. Chen's guild IS the Circle's economic foundation.", npc_id="jp_master_chen"),
    PortInstitution(id="jp_magistrate", name="The Magistrate's Hall", port_id="jade_port", institution_type="governor",
        description="A tiled hall with calligraphy scrolls and silk screens. Twelve generations of Mei family governance depicted in painted scrolls along the walls.",
        function="Cultural governance, diplomatic relations, trade policy. Lady Mei governs through knowledge and carefully edited correspondence.",
        political_leaning="Silk Circle sovereignty with secret pragmatism. Mei protects the Circle by controlling what Chen hears.", npc_id="jp_lady_mei"),
    PortInstitution(id="jp_pavilion", name="The Jade Pavilion", port_id="jade_port", institution_type="tavern",
        description="An open-air tea house overlooking the harbor. Bamboo walls, stone floor, a single perfect bonsai. The sound of water. The absence of hurry.",
        function="Neutral ground where masters, magistrates, and merchants meet as equals over tea. Huang's silence is the most powerful force in Jade Port.",
        political_leaning="Above politics. The Pavilion serves balance.", npc_id="jp_tea_master_huang"),
    PortInstitution(id="jp_quality", name="The Inspection Hall", port_id="jade_port", institution_type="customs",
        description="A well-lit room with magnifying equipment, sound-testing stations, and Zhao's desk. Confiscated counterfeits displayed in cases — a gallery of shame.",
        function="Authenticity inspection. Every piece of porcelain checked. Zhao protects the Kiln Masters' marks from forgery worldwide.",
        political_leaning="Circle quality enforcement. Authenticity is the brand.", npc_id="jp_inspector_zhao"),
    PortInstitution(id="jp_factor", name="The Trade Office", port_id="jade_port", institution_type="broker",
        description="A silk-curtained office in the Quarter, maps of trade routes and buyer contacts pinned to screens. Wu's desk is rosewood. His hospitality is flawless.",
        function="Commercial brokering, export coordination. Wu matches Western demand to Eastern quality without compromising either.",
        political_leaning="Pragmatic Circle. Commerce serves the craft, carefully.", npc_id="jp_factor_wu"),
    PortInstitution(id="jp_kiln_lab", name="The Apprentice's Kiln", port_id="jade_port", institution_type="apothecary",
        description="A small kiln behind the Quarter where Lin experiments with new glazes. Test tiles line the walls. Iron oxide samples from Iron Point sit in labeled jars.",
        function="Innovation within tradition. Lin pushes the boundaries Chen set — gently, secretly, and brilliantly.",
        political_leaning="The future. Lin represents what the Circle might become.", npc_id="jp_apprentice_lin"),
]

JADE_PORT_PROFILE = PortInstitutionalProfile(
    port_id="jade_port",
    governor_title="Circle Magistrate",
    power_structure=(
        "Jade Port is governed by the intersection of craft and court: Chen controls "
        "the porcelain (the product), Mei controls the politics (the relationships), "
        "and Huang holds the secrets (the leverage). Li Wei enforces protocol. Zhao "
        "protects authenticity. Wu handles commerce. Lin represents the uncertain "
        "future — a prodigy who may surpass her master, inheriting a guild that "
        "must evolve to survive but whose identity is rooted in not changing."
    ),
    internal_tension=(
        "Three layers of tension: (1) Chen's resistance to change vs. the Circle's "
        "need to adapt to Western trade pressure. (2) Mei's letter interception — "
        "she's protecting Chen from compromising the Circle, but she's also "
        "manipulating him, and Huang knows. (3) Lin's secret experiments — she's "
        "innovating behind Chen's back because she believes the tradition must grow. "
        "If Chen discovers her new glazes, he'll either embrace them or destroy them. "
        "She doesn't know which, and neither does anyone else. The deepest thread: "
        "Wu is negotiating with Iron Point's Yaa for raw ore, which would bypass "
        "Ironhaven entirely. If it goes through, it connects the Gold Coast's "
        "independence movement with the Silk Circle's quality obsession — an "
        "alliance that could reshape the entire game's trade network."
    ),
    institutions=_JADE_PORT_INSTITUTIONS,
    npcs=_JADE_PORT_NPCS,
)


# ---------------------------------------------------------------------------
# Master registry — will grow as we build each port

# =========================================================================
# MONSOON REACH — The Wind Temple
# =========================================================================

_MONSOON_REACH_NPCS = [
    PortNPC(
        id="mr_harbor_ravi",
        name="Harbor Master Ravi",
        title="Harbor Master",
        port_id="monsoon_reach",
        institution="harbor_master",
        personality="calm",
        description=(
            "A former monk who left the Wind Temple because he preferred boats to "
            "prayer — then discovered that running a harbor IS prayer, just louder. "
            "Ravi assigns berths with the same unhurried deliberation the monks "
            "apply to reading wind. He checks the tide, checks the forecast, checks "
            "the sky, and then points. He's never wrong about when a ship should depart."
        ),
        agenda=(
            "Harmony with the monsoon. Ravi doesn't fight the weather — he works "
            "with it. Ships that arrive at the wrong time wait. Ships that insist "
            "on departing into a monsoon get a lecture and a refusal. He's saved more "
            "lives through stubbornness than any rescue fleet."
        ),
        greeting_neutral="\"Welcome. The wind is from the southeast today — good for arrivals, not for departures. You'll berth at the headland. The monks will post tomorrow's forecast at dawn.\"",
        greeting_friendly="\"Captain! The wind said you'd come today. Berth three — sheltered from the afternoon gusts. Stay for the evening forecast. Brother Anand has something to tell you.\"",
        greeting_hostile="\"You may dock. But I recommend you wait for tomorrow's forecast before making plans. The monsoon doesn't care about your schedule.\"",
        rumor="Ravi once refused to let a Silk Circle trade fleet depart for three days because the monks predicted a storm. The fleet commander was furious. The storm arrived on the fourth day and destroyed a pirate fleet that had been waiting to ambush them. Ravi said nothing. The monks smiled.",
        relationship_notes={
            "mr_brother_anand": "His former teacher. Ravi left the Temple but never left the teachings.",
            "mr_shipwright_devi": "Partners. She builds the ships; he tells them when to sail.",
            "mr_spice_trader_priya": "She brings the trade; he manages the harbor. Clean working relationship.",
            "mr_elder_council": "They govern; he runs the harbor. He attends council when the wind permits.",
            "mr_customs_sanjay": "Sanjay checks cargo; Ravi checks weather. Non-overlapping concerns.",
            "mr_broker_kamala": "She matches contracts; he matches tides. Both serve the flow.",
        },
    ),
    PortNPC(
        id="mr_brother_anand",
        name="Brother Anand",
        title="Wind Reader",
        port_id="monsoon_reach",
        institution="apothecary",
        personality="enigmatic",
        description=(
            "Shaved head, saffron robes, and eyes that are always looking at something "
            "you can't see — the wind patterns above the clouds, the currents below "
            "the surface, the pressure changes that announce storms days before they "
            "arrive. Brother Anand is the Wind Temple's chief reader — the monk whose "
            "forecasts guide every departure from Monsoon Reach."
        ),
        agenda=(
            "The wind's truth. Anand doesn't forecast for commerce — he forecasts "
            "because the wind speaks and someone must listen. His predictions are "
            "uncannily accurate because they're based on generations of observation "
            "recorded in the Temple's archives. He offered alliance to no one — not "
            "the Silk Circle, not the Free Ports, not any faction. The wind, he says, "
            "belongs to everyone."
        ),
        greeting_neutral="\"The wind brings you. Good. Tomorrow it will shift — from the east, I think. Plan your departure accordingly. Or stay. The Temple is open.\"",
        greeting_friendly="\"Ah, Captain. The wind spoke your name this morning — I expected you. Come to the Temple tonight. There is something I wish to show you about the southern currents.\"",
        greeting_hostile="\"The wind carries all ships. Even those I would not choose to guide. Your forecast is the same as everyone's — truthful.\"",
        rumor="Brother Anand predicted the worst monsoon in a generation three weeks before it arrived. He told every captain in harbor. Most left. The ones who stayed survived because Anand also told them exactly where to anchor. His forecast saved forty-three ships and he never mentioned it again.",
        relationship_notes={
            "mr_harbor_ravi": "His former student. Ravi left the Temple but carries the teachings in how he runs the harbor.",
            "mr_shipwright_devi": "She builds ships to survive what he predicts. A sacred partnership.",
            "mr_spice_trader_priya": "She consults his forecasts before every trade decision. He gives them freely.",
            "mr_elder_council": "The council defers to him on all weather matters. His forecasts are policy.",
            "mr_customs_sanjay": "No strong connection. The wind doesn't need customs clearance.",
            "mr_broker_kamala": "She incorporates his forecasts into contract timing. Smart — he approves.",
        },
    ),
    PortNPC(
        id="mr_shipwright_devi",
        name="Shipwright Devi",
        title="Master Shipwright",
        port_id="monsoon_reach",
        institution="shipyard",
        personality="inventive",
        description=(
            "Calloused hands, charcoal smudges on her face from drawing hull designs, "
            "and a mind that's always solving the next problem. Devi runs Monsoon "
            "Reach's shipyard — the only yard in the East Indies, built to produce "
            "ships that survive what the monsoon throws at them. Her hulls are deeper, "
            "her masts stronger, her keels longer than Mediterranean designs."
        ),
        agenda=(
            "Building ships that can't be broken. Devi studies every wreck that washes "
            "up after monsoon season, mapping failure points and redesigning to address "
            "them. She's been corresponding with Elena in Silva Bay — two master "
            "shipwrights on opposite sides of the world, trading techniques in letters "
            "that take months to arrive. They've never met. They respect each other "
            "enormously."
        ),
        greeting_neutral="\"Your hull — may I see it? I study every ship that docks here. The monsoon teaches through destruction. I learn through repair.\"",
        greeting_friendly="\"Captain! Bring her in — I've been developing a new keel reinforcement. Your ship would be perfect to test it. Free of charge — I need the data.\"",
        greeting_hostile="\"I'll repair your ship. The sea doesn't hold grudges and neither does my yard. But I'm charging monsoon rates.\"",
        rumor="Devi and Elena Madeira in Silva Bay have been exchanging ship designs by letter for five years. Neither has met the other. When asked if she'd visit Silva Bay, Devi said, 'Someday. When I build a ship good enough to survive the voyage AND impress her.' She hasn't built it yet. She's still trying.",
        relationship_notes={
            "mr_harbor_ravi": "Partners. She builds; he launches. They coordinate on tide schedules.",
            "mr_brother_anand": "She builds ships to survive his worst forecasts. A sacred partnership of engineer and prophet.",
            "mr_spice_trader_priya": "Devi repairs the spice traders' ships. Priya pays promptly. Professional.",
            "mr_elder_council": "The council values the shipyard's revenue. Devi values her independence.",
            "mr_customs_sanjay": "No interaction. Ships aren't cargo.",
            "mr_broker_kamala": "Kamala brings repair commissions from the wider network. Good business.",
        },
    ),
    PortNPC(
        id="mr_spice_trader_priya",
        name="Priya Sundaram",
        title="Spice Factor",
        port_id="monsoon_reach",
        institution="exchange",
        personality="pragmatic",
        description=(
            "Sharp eyes, quick hands on the abacus, and the impatience of a woman "
            "who knows that spice prices change with the wind — literally. Priya "
            "runs Monsoon Reach's spice exchange: grading, pricing, and routing "
            "the spice that funnels through this crossroads port. She's the practical "
            "counterweight to the Temple's spirituality."
        ),
        agenda=(
            "Efficient trade. Priya wants spice to move — bought, priced, shipped — "
            "without the ceremonial delays that Jade Port imposes. Monsoon Reach is "
            "a Free Port, and Priya exploits that: she'll trade with the Silk Circle, "
            "the Exchange Alliance, the Gold Coast, and the Shadow Ports without "
            "discrimination. Quality and price are her only metrics."
        ),
        greeting_neutral="\"Spice or silk? I have both. Prices change with the afternoon forecast, so decide quickly. The wind doesn't wait for negotiations.\"",
        greeting_friendly="\"Captain! The morning lot is excellent — post-monsoon harvest, Anand predicts clear sailing for a week. Buy now, ship fast, sell high. I'll hold the best lots for you.\"",
        greeting_hostile="\"Prices are posted. Standard lots only. The premium reserves are for merchants who trade regularly and reliably. Perhaps next time.\"",
        rumor="Priya once sold spice to a Crimson Tide captain and an Alliance merchant in the same hour, from the same lot, at the same price. Both complained about the other's presence. Priya said, 'Spice doesn't choose its buyer. Neither do I.' Neither argued.",
        relationship_notes={
            "mr_harbor_ravi": "She consults his departure schedules. Timing is everything in the spice trade.",
            "mr_brother_anand": "His forecasts shape her pricing. A calm week means ship; a storm means hold.",
            "mr_shipwright_devi": "Priya's traders need seaworthy ships. Devi provides them.",
            "mr_elder_council": "She's the council's revenue engine. They depend on her trade volume.",
            "mr_customs_sanjay": "He checks her lots. She keeps them clean. No friction.",
            "mr_broker_kamala": "Kamala handles the contracts Priya generates. A fluid partnership.",
        },
    ),
    PortNPC(
        id="mr_elder_council",
        name="The Harbor Council",
        title="Governing Council",
        port_id="monsoon_reach",
        institution="governor",
        personality="deliberate",
        description=(
            "A council of five — two monks, two merchants, and one shipwright — who "
            "govern Monsoon Reach by consensus. They meet in the Wind Temple's "
            "lower hall, where the sound of the pagoda bells accompanies every "
            "decision. The council moves slowly because the monks insist on waiting "
            "for signs, which the merchants find maddening and the shipwright ignores."
        ),
        agenda=(
            "Neutrality and prosperity. The council wants Monsoon Reach to remain "
            "a Free Port — trading with all, allied with none. They rejected the "
            "Silk Circle's offer of membership because the monks said the wind "
            "doesn't recognize borders. The merchants agreed because neutrality "
            "brings more trade."
        ),
        greeting_neutral="\"Monsoon Reach welcomes all vessels. The council's only requirement: respect the Temple's forecasts and depart when the wind permits.\"",
        greeting_friendly="\"Captain — the council acknowledges your contributions to Monsoon Reach's prosperity. Your voice is welcome at our table.\"",
        greeting_hostile="\"The council notes your recent conduct. You may trade, but the Temple's forecasts are not optional. Depart only when cleared.\"",
        rumor="The council once voted to close the harbor for a week because Brother Anand dreamed of a great wave. No wave came. The monks said the dream was a warning they heeded. The merchants lost a week's revenue. The debate about whether prophecy counts as policy has never been settled.",
        relationship_notes={
            "mr_harbor_ravi": "He attends when the wind permits. The council has learned not to schedule around his availability.",
            "mr_brother_anand": "The council defers to him on weather. His forecasts shape every departure policy.",
            "mr_shipwright_devi": "The shipyard is represented on the council. Devi's independence is protected.",
            "mr_spice_trader_priya": "The revenue engine. The council depends on trade volume she generates.",
            "mr_customs_sanjay": "Reports to the council. Light-touch customs is deliberate policy.",
            "mr_broker_kamala": "Contract revenue funds council operations. Kamala's success is the council's success.",
        },
    ),
    PortNPC(
        id="mr_customs_sanjay",
        name="Customs Officer Sanjay",
        title="Customs Officer",
        port_id="monsoon_reach",
        institution="customs",
        personality="easygoing",
        description=(
            "A man who treats customs the way the monks treat weather: observe, "
            "record, and don't interfere unless absolutely necessary. Sanjay checks "
            "manifests, stamps paperwork, and makes sure nothing obviously illegal "
            "passes through. He's not lazy — he's philosophically aligned with "
            "Monsoon Reach's Free Port ethos."
        ),
        agenda="Sufficient compliance. Sanjay does enough to satisfy the Alliance's reporting requirements without slowing trade. The monks taught him that the river flows best when you stop throwing rocks in it.",
        greeting_neutral="\"Manifest? Let me stamp it. Monsoon Reach doesn't complicate trade. The wind does enough of that.\"",
        greeting_friendly="\"Captain — already stamped. I saw your sails and did the paperwork. Go see Priya before the good lots are gone.\"",
        greeting_hostile="\"Standard inspection today. Nothing personal — just... reports I need to file. I'll be quick.\"",
        rumor="Sanjay spent a year at the Wind Temple before becoming a customs officer. He left because he couldn't sit still long enough for meditation. The monks said his restlessness was also a form of prayer. He stamps manifests with the same equanimity.",
        relationship_notes={
            "mr_harbor_ravi": "They share dock space without friction. Non-overlapping concerns.",
            "mr_brother_anand": "Sanjay still meditates occasionally — badly. Anand doesn't judge.",
            "mr_shipwright_devi": "No interaction. Ships aren't cargo.",
            "mr_spice_trader_priya": "He checks her lots. She keeps them clean.",
            "mr_elder_council": "Reports to them. Light customs is deliberate council policy.",
            "mr_broker_kamala": "Stamps her contracts. No complications.",
        },
    ),
    PortNPC(
        id="mr_broker_kamala",
        name="Kamala Nair",
        title="Broker",
        port_id="monsoon_reach",
        institution="broker",
        personality="fluid",
        description=(
            "A woman who moves between cultures the way water moves between rocks — "
            "naturally, without friction. Kamala brokers contracts at Monsoon Reach "
            "by understanding what every party needs and finding the overlap. She "
            "speaks four languages, trades with every bloc, and has a reputation for "
            "finding deals that make everyone feel like they won."
        ),
        agenda=(
            "Connection. Kamala sees Monsoon Reach as a connector port — the place "
            "where Eastern quality meets Western demand meets Gold Coast resources. "
            "Her contracts are bridges. She incorporates Anand's weather forecasts "
            "into shipping schedules, which gives her clients a timing advantage "
            "no other broker can match."
        ),
        greeting_neutral="\"Captain — what are you carrying, and where does it need to go? I know someone who needs exactly that. I always do.\"",
        greeting_friendly="\"Captain! I've been holding a contract — spice to the Mediterranean, timed to Anand's forecast of clear sailing next week. Perfect margin. Shall I?\"",
        greeting_hostile="\"I... don't have anything that matches your current profile. But Monsoon Reach is a forgiving port. Come back when your reputation recovers.\"",
        rumor="Kamala once brokered a three-way deal: Iron Point ore to Jade Port, Jade Port porcelain to Porto Novo, Porto Novo grain to Iron Point. Three contracts, three routes, three satisfied parties. She calls it 'the Triangle.' Everyone else calls it genius.",
        relationship_notes={
            "mr_harbor_ravi": "She matches contracts; he matches tides. Both serve the flow.",
            "mr_brother_anand": "She incorporates his forecasts into timing. Smart — he approves.",
            "mr_shipwright_devi": "Brings repair commissions. Good business for both.",
            "mr_spice_trader_priya": "Fluid partnership. Priya generates trade; Kamala structures contracts.",
            "mr_elder_council": "Contract revenue funds council operations.",
            "mr_customs_sanjay": "Stamps her contracts. No complications.",
        },
    ),
]

_MONSOON_REACH_INSTITUTIONS = [
    PortInstitution(id="mr_harbor", name="The Headland Harbor", port_id="monsoon_reach", institution_type="harbor_master",
        description="A curved harbor around a headland crowned by the Wind Temple pagoda. Deeper keels, stronger moorings. The wind chimes on the pagoda are the harbor's clock.",
        function="Weather-coordinated berthing. Departures cleared by monk forecast only. Ravi manages the intersection of tide and prophecy.",
        political_leaning="Free Port. All flags welcome. The wind doesn't discriminate.", npc_id="mr_harbor_ravi"),
    PortInstitution(id="mr_temple", name="The Wind Temple", port_id="monsoon_reach", institution_type="apothecary",
        description="A pagoda on the headland where monks track the monsoon with instruments passed down for generations. Wind vanes, pressure bells, and archives of a thousand seasons.",
        function="Weather forecasting, spiritual guidance, departure clearance. Anand's predictions guide every ship that leaves.",
        political_leaning="Above politics. The wind belongs to everyone.", npc_id="mr_brother_anand"),
    PortInstitution(id="mr_shipyard", name="The Monsoon Yard", port_id="monsoon_reach", institution_type="shipyard",
        description="A yard built to produce monsoon-proof vessels. Deeper keels, reinforced masts, hulls designed from studying wrecks. Devi's workshop is full of failure analysis sketches.",
        function="Ship building and repair specialized for monsoon conditions. Devi studies destruction to build survival.",
        political_leaning="Independent. The yard serves the sea, not any bloc.", npc_id="mr_shipwright_devi"),
    PortInstitution(id="mr_spice_exchange", name="The Spice Crossroads", port_id="monsoon_reach", institution_type="exchange",
        description="An open-air market where spice from a dozen origins is graded and priced. Prices change with the afternoon forecast — literally.",
        function="Spice grading, pricing, and routing. Priya trades with all blocs without discrimination. Quality and price are the only metrics.",
        political_leaning="Free Port pragmatism. Commerce doesn't need borders.", npc_id="mr_spice_trader_priya"),
    PortInstitution(id="mr_council_hall", name="The Temple Hall", port_id="monsoon_reach", institution_type="governor",
        description="The Wind Temple's lower hall where pagoda bells accompany every decision. Five council members — two monks, two merchants, one shipwright.",
        function="Consensus governance. The monks wait for signs. The merchants find this maddening. The shipwright ignores both.",
        political_leaning="Free Port by conviction. The wind doesn't recognize borders.", npc_id="mr_elder_council"),
    PortInstitution(id="mr_customs", name="The Flow Desk", port_id="monsoon_reach", institution_type="customs",
        description="A desk near the harbor that Sanjay occupies with the same equanimity he brought from his year at the Temple. Stamp, smile, flow.",
        function="Minimal customs. Philosophical alignment with Free Port ethos: observe, record, don't interfere.",
        political_leaning="Free Port. The river flows best when you stop throwing rocks in it.", npc_id="mr_customs_sanjay"),
    PortInstitution(id="mr_broker", name="The Bridge Desk", port_id="monsoon_reach", institution_type="broker",
        description="A desk overlooking the spice market where Kamala matches contracts by understanding what every culture needs. Four languages. Zero borders.",
        function="Cross-cultural contract matching with weather-timed shipping. Kamala finds the overlap between what everyone wants.",
        political_leaning="Free Port connector. Kamala builds bridges, not walls.", npc_id="mr_broker_kamala"),
]

MONSOON_REACH_PROFILE = PortInstitutionalProfile(
    port_id="monsoon_reach",
    governor_title="Harbor Council",
    power_structure=(
        "Monsoon Reach is governed by a five-person council (2 monks, 2 merchants, "
        "1 shipwright) that meets in the Wind Temple. Brother Anand's forecasts are "
        "de facto law — no ship departs without his clearance. Ravi runs the harbor "
        "as an extension of the Temple's teachings. Devi builds ships to survive what "
        "Anand predicts. Priya moves the spice. Kamala connects the world. The power "
        "structure is unusually harmonious because everyone agrees on the port's "
        "purpose: trade in harmony with the monsoon."
    ),
    internal_tension=(
        "The tension is between faith and commerce. The monks believe the wind "
        "speaks truth and should be obeyed. The merchants believe the wind is data "
        "to be exploited. When Anand closes the harbor for a dream, the merchants "
        "lose money. When Anand's dreams prove accurate, the merchants are grateful. "
        "This cycle — frustration, then vindication — keeps the balance intact but "
        "never fully resolved. The deeper thread: Devi's correspondence with Elena "
        "in Silva Bay is building a cross-hemisphere shipwright relationship that "
        "could transform both yards. If they ever meet, the collaboration could "
        "produce ships neither culture imagined alone."
    ),
    institutions=_MONSOON_REACH_INSTITUTIONS,
    npcs=_MONSOON_REACH_NPCS,
)



# =========================================================================
# Remaining East Indies + South Seas ports are in port_institutions_east.py
# =========================================================================


# ---------------------------------------------------------------------------
# Master registry
# ---------------------------------------------------------------------------

PORT_INSTITUTIONAL_PROFILES: dict[str, PortInstitutionalProfile] = {
    "porto_novo": PORTO_NOVO_PROFILE,
    "al_manar": AL_MANAR_PROFILE,
    "silva_bay": SILVA_BAY_PROFILE,
    "corsairs_rest": CORSAIRS_REST_PROFILE,
    "ironhaven": IRONHAVEN_PROFILE,
    "stormwall": STORMWALL_PROFILE,
    "thornport": THORNPORT_PROFILE,
    "sun_harbor": SUN_HARBOR_PROFILE,
    "palm_cove": PALM_COVE_PROFILE,
    "iron_point": IRON_POINT_PROFILE,
    "pearl_shallows": PEARL_SHALLOWS_PROFILE,
    "jade_port": JADE_PORT_PROFILE,
    "monsoon_reach": MONSOON_REACH_PROFILE,
}

# Merge in East Indies + South Seas profiles from continuation file
from portlight.content.port_institutions_east import EAST_PROFILES  # noqa: E402
PORT_INSTITUTIONAL_PROFILES.update(EAST_PROFILES)

ALL_NPCS: dict[str, PortNPC] = {npc.id: npc for profile in PORT_INSTITUTIONAL_PROFILES.values() for npc in profile.npcs}

ALL_INSTITUTIONS: dict[str, PortInstitution] = {inst.id: inst for profile in PORT_INSTITUTIONAL_PROFILES.values() for inst in profile.institutions}
