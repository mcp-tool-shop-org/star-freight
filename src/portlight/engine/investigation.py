"""Investigation system — Star Freight Phase 4.

Information is cargo with consequences. Leads emerge from captain life,
not from quest givers. Knowledge changes route choice, contract value,
encounter setup, faction risk, and what the player notices.

Design laws:
- Leads surface through normal play (trade, combat, culture, crew)
- Information has state (rumor → clue → corroborated → actionable → locked)
- Investigation feeds all three layers (trade, tactics, narrative)
- Multiple paths can progress the same thread
- Ignoring the plot is allowed but costly
- The journal preserves fragments, not chores

Pure functions. Callers decide mutations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Evidence quality
# ---------------------------------------------------------------------------

class EvidenceGrade(str, Enum):
    """How reliable a piece of information is."""
    RUMOR = "rumor"                # Heard something. Maybe true.
    CLUE = "clue"                  # Found something concrete but unexplained.
    CORROBORATED = "corroborated"  # Two independent sources agree.
    ACTIONABLE = "actionable"      # Enough to act on with confidence.
    LOCKED = "locked"              # Proven. Cannot be disputed.

    @property
    def weight(self) -> int:
        return {"rumor": 1, "clue": 2, "corroborated": 3, "actionable": 4, "locked": 5}[self.value]


# ---------------------------------------------------------------------------
# Fragments (journal entries)
# ---------------------------------------------------------------------------

@dataclass
class Fragment:
    """One piece of information the player has learned.

    Not a task. Not an objective. A record of something known,
    who said it, and what it might connect to.
    """
    id: str
    thread_id: str                   # which investigation thread
    content: str                     # what the player learned
    source_type: str                 # trade | combat | cultural | crew | station | transit
    source_detail: str               # specific: "cargo manifest at Keth relay" / "Varek mentioned..."
    grade: EvidenceGrade
    day_acquired: int
    connections: list[str] = field(default_factory=list)  # other fragment IDs this connects to
    crew_interpreter: str = ""       # crew_id who helped interpret this (if any)
    acted_on: bool = False           # whether player has used this info


# ---------------------------------------------------------------------------
# Source types (how leads enter the game)
# ---------------------------------------------------------------------------

class SourceType(str, Enum):
    """How a lead was discovered. Multiple sources can feed the same thread."""
    TRADE = "trade"              # cargo manifest, price anomaly, restricted goods
    COMBAT = "combat"            # salvage data, dying words, intercepted comms
    CULTURAL = "cultural"        # festival records, debt ledger entries, customs logs
    CREW = "crew"                # crew memory, loyalty mission, personal connection
    STATION = "station"          # overheard conversation, bounty board, news feed
    TRANSIT = "transit"          # distress signal, derelict scan, patrol chatter


@dataclass
class LeadSource:
    """A potential way to discover a fragment."""
    fragment_id: str                 # which fragment this can produce
    source_type: SourceType
    trigger: str                     # what must happen: "haul_medical_cargo_to_keth"
    crew_required: str = ""          # crew_id needed to interpret (empty = anyone)
    civ_knowledge_required: str = "" # civ_id if cultural knowledge needed
    knowledge_level_required: int = 0
    reputation_required: dict[str, int] = field(default_factory=dict)  # faction → min standing
    description: str = ""            # human-readable: "Hauling medical supplies to a Keth station"


# ---------------------------------------------------------------------------
# Investigation thread
# ---------------------------------------------------------------------------

class ThreadState(str, Enum):
    """Overall progress of an investigation thread."""
    DORMANT = "dormant"          # Not yet discovered
    ACTIVE = "active"            # Player has at least one fragment
    ADVANCED = "advanced"        # Multiple corroborated fragments
    CRITICAL = "critical"        # Enough to act — actionable evidence
    RESOLVED = "resolved"        # Thread concluded


@dataclass
class InvestigationThread:
    """A line of inquiry the player can pursue.

    Not a quest chain. A web of fragments that can be assembled
    from multiple directions. The thread resolves when enough
    evidence reaches sufficient grade.
    """
    id: str
    title: str                       # "The Medical Shipment" — player sees this
    premise: str                     # What the player suspects
    resolution_threshold: int        # total evidence weight needed to resolve
    fragments_required: int          # minimum distinct fragments
    max_delay_days: int              # days before delay consequences start
    delay_consequence_tag: str       # consequence engine tag when delayed

    # State
    state: ThreadState = ThreadState.DORMANT
    discovered_day: int = 0          # day first fragment was found
    last_progress_day: int = 0       # day of most recent fragment

    # Available sources (how this thread CAN be advanced)
    sources: list[LeadSource] = field(default_factory=list)

    # Found fragments
    fragments: list[Fragment] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Investigation state (persisted on campaign)
# ---------------------------------------------------------------------------

@dataclass
class InvestigationState:
    """Complete investigation state. Persisted in save files."""
    threads: dict[str, InvestigationThread] = field(default_factory=dict)
    all_fragments: list[Fragment] = field(default_factory=list)
    total_progress: int = 0          # 0-10 overall investigation score
    delay_warnings_issued: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Fragment discovery
# ---------------------------------------------------------------------------

def discover_fragment(
    state: InvestigationState,
    thread_id: str,
    fragment: Fragment,
) -> dict:
    """Add a newly discovered fragment to a thread.

    Returns {thread_id, fragment_id, thread_state_changed, new_state, summary}.
    """
    thread = state.threads.get(thread_id)
    if thread is None:
        return {"error": f"Unknown thread: {thread_id}"}

    # Don't duplicate
    if any(f.id == fragment.id for f in thread.fragments):
        return {"duplicate": True, "fragment_id": fragment.id}

    thread.fragments.append(fragment)
    state.all_fragments.append(fragment)
    thread.last_progress_day = fragment.day_acquired

    # First fragment activates the thread
    old_state = thread.state
    if thread.state == ThreadState.DORMANT:
        thread.state = ThreadState.ACTIVE
        thread.discovered_day = fragment.day_acquired

    # Check for state advancement
    _update_thread_state(thread)

    # Update overall progress
    state.total_progress = _calculate_total_progress(state)

    return {
        "thread_id": thread_id,
        "fragment_id": fragment.id,
        "duplicate": False,
        "thread_state_changed": old_state != thread.state,
        "old_state": old_state.value,
        "new_state": thread.state.value,
        "summary": f"Learned: {fragment.content}",
        "source": fragment.source_type,
        "grade": fragment.grade.value,
    }


def _update_thread_state(thread: InvestigationThread) -> None:
    """Advance thread state based on fragment quality and quantity."""
    total_weight = sum(f.grade.weight for f in thread.fragments)
    distinct_count = len(thread.fragments)
    has_corroborated = any(f.grade.weight >= EvidenceGrade.CORROBORATED.weight for f in thread.fragments)
    has_actionable = any(f.grade.weight >= EvidenceGrade.ACTIONABLE.weight for f in thread.fragments)

    if total_weight >= thread.resolution_threshold and distinct_count >= thread.fragments_required:
        thread.state = ThreadState.RESOLVED
    elif has_actionable or (has_corroborated and distinct_count >= thread.fragments_required - 1):
        thread.state = ThreadState.CRITICAL
    elif has_corroborated or distinct_count >= 2:
        thread.state = ThreadState.ADVANCED
    elif distinct_count >= 1:
        thread.state = ThreadState.ACTIVE


def _calculate_total_progress(state: InvestigationState) -> int:
    """Overall investigation progress (0-10)."""
    if not state.threads:
        return 0
    total = 0
    for thread in state.threads.values():
        if thread.state == ThreadState.RESOLVED:
            total += 3
        elif thread.state == ThreadState.CRITICAL:
            total += 2
        elif thread.state == ThreadState.ADVANCED:
            total += 1
    return min(10, total)


# ---------------------------------------------------------------------------
# Corroboration (two sources agree)
# ---------------------------------------------------------------------------

def check_corroboration(thread: InvestigationThread) -> list[tuple[str, str]]:
    """Check if any fragments corroborate each other.

    Two fragments corroborate if they are from different source types
    and share connections. Returns list of (fragment_a_id, fragment_b_id) pairs.
    """
    pairs = []
    frags = thread.fragments
    for i in range(len(frags)):
        for j in range(i + 1, len(frags)):
            a, b = frags[i], frags[j]
            if a.source_type == b.source_type:
                continue  # same source type doesn't corroborate
            shared = set(a.connections) & set(b.connections)
            if shared or a.id in b.connections or b.id in a.connections:
                pairs.append((a.id, b.id))
    return pairs


def upgrade_corroborated(thread: InvestigationThread) -> list[str]:
    """Upgrade fragments that are corroborated to CORROBORATED grade.

    Returns list of upgraded fragment IDs.
    """
    pairs = check_corroboration(thread)
    upgraded = []
    corroborated_ids = set()
    for a_id, b_id in pairs:
        corroborated_ids.add(a_id)
        corroborated_ids.add(b_id)

    for frag in thread.fragments:
        if frag.id in corroborated_ids and frag.grade.weight < EvidenceGrade.CORROBORATED.weight:
            frag.grade = EvidenceGrade.CORROBORATED
            upgraded.append(frag.id)

    if upgraded:
        _update_thread_state(thread)

    return upgraded


# ---------------------------------------------------------------------------
# Source matching (does this game event produce a lead?)
# ---------------------------------------------------------------------------

def check_lead_sources(
    thread: InvestigationThread,
    event_type: str,
    event_trigger: str,
    crew_ids: list[str],
    cultural_knowledge: dict[str, int],
    reputation: dict[str, int],
) -> list[LeadSource]:
    """Check if a game event matches any lead source for this thread.

    Returns list of matching sources (the caller creates the fragments).
    """
    matches = []
    for source in thread.sources:
        # Already found this fragment?
        if any(f.id == source.fragment_id for f in thread.fragments):
            continue

        # Check trigger match
        if source.trigger != event_trigger:
            continue

        # Check crew requirement
        if source.crew_required and source.crew_required not in crew_ids:
            continue

        # Check cultural knowledge
        if source.civ_knowledge_required:
            civ = source.civ_knowledge_required
            level = cultural_knowledge.get(civ, 0)
            if level < source.knowledge_level_required:
                continue

        # Check reputation
        rep_ok = True
        for faction, min_standing in source.reputation_required.items():
            if reputation.get(faction, 0) < min_standing:
                rep_ok = False
                break
        if not rep_ok:
            continue

        matches.append(source)

    return matches


# ---------------------------------------------------------------------------
# Delay consequences
# ---------------------------------------------------------------------------

def check_delay_consequences(
    state: InvestigationState,
    current_day: int,
) -> list[dict]:
    """Check if any active threads have been neglected too long.

    Returns list of {thread_id, days_stale, consequence_tag, warning}.
    Delay doesn't kill the thread — it makes the world move without you.
    """
    consequences = []
    for thread in state.threads.values():
        if thread.state in (ThreadState.DORMANT, ThreadState.RESOLVED):
            continue

        days_since_progress = current_day - thread.last_progress_day
        if days_since_progress <= thread.max_delay_days:
            continue

        # Already warned about this thread?
        warn_key = f"{thread.id}_day{current_day // 30}"  # warn once per ~month
        if warn_key in state.delay_warnings_issued:
            continue

        state.delay_warnings_issued.append(warn_key)

        staleness = days_since_progress - thread.max_delay_days
        severity = "mild" if staleness < 30 else "serious" if staleness < 60 else "critical"

        consequences.append({
            "thread_id": thread.id,
            "thread_title": thread.title,
            "days_stale": days_since_progress,
            "severity": severity,
            "consequence_tag": thread.delay_consequence_tag,
            "warning": _delay_warning(thread, severity),
        })

    return consequences


def _delay_warning(thread: InvestigationThread, severity: str) -> str:
    """Generate a contextual delay warning."""
    if severity == "mild":
        return f"The trail on \"{thread.title}\" is going cold. Someone else may be following it."
    elif severity == "serious":
        return f"\"{thread.title}\" — you've been quiet too long. The people involved are moving without you."
    else:
        return f"\"{thread.title}\" — critical delay. Evidence is being destroyed. Witnesses are disappearing."


# ---------------------------------------------------------------------------
# Campaign impact queries
# ---------------------------------------------------------------------------

def investigation_trade_impact(state: InvestigationState) -> dict:
    """What the investigation reveals about trade opportunities.

    Returns dict of unlock flags that the trade system reads.
    """
    impacts = {
        "restricted_goods_visible": [],     # goods that investigation reveals
        "price_anomalies_flagged": [],      # stations where prices are suspicious
        "smuggling_routes_known": [],       # routes revealed by investigation
        "faction_trade_warnings": [],       # factions with hidden agendas
    }

    for frag in state.all_fragments:
        if frag.grade.weight >= EvidenceGrade.CLUE.weight:
            # Fragments with trade-relevant tags
            if "cargo" in frag.source_type or "trade" in frag.source_type:
                impacts["price_anomalies_flagged"].append(frag.source_detail)
            if "smuggling" in frag.content.lower():
                impacts["smuggling_routes_known"].append(frag.source_detail)

    return impacts


def investigation_encounter_impact(state: InvestigationState) -> dict:
    """What the investigation changes about encounters.

    Returns dict of flags the encounter system reads.
    """
    impacts = {
        "ambush_awareness": False,       # player knows someone is hunting them
        "faction_motives_known": [],      # factions whose real agenda is understood
        "safe_passage_available": [],     # routes where investigation grants safe passage
        "threat_level_modifier": 0,       # +/- to encounter danger
    }

    for thread in state.threads.values():
        if thread.state in (ThreadState.CRITICAL, ThreadState.RESOLVED):
            impacts["ambush_awareness"] = True
        if thread.state == ThreadState.ADVANCED:
            impacts["threat_level_modifier"] += 1  # knowing more = more dangerous

    return impacts


def investigation_narrative_impact(state: InvestigationState) -> dict:
    """What the investigation opens in narrative/cultural space.

    Returns dict of flags for narrative, cultural, and crew systems.
    """
    impacts = {
        "crew_loyalty_threads": [],       # crew members whose loyalty missions unlock
        "cultural_readings": [],          # cultural events that mean something different now
        "faction_inner_circle": [],       # factions where investigation grants deeper access
        "endgame_paths_available": [],    # which endings are reachable
    }

    for thread in state.threads.values():
        if thread.state == ThreadState.RESOLVED:
            impacts["endgame_paths_available"].append(thread.id)
        for frag in thread.fragments:
            if frag.crew_interpreter:
                impacts["crew_loyalty_threads"].append(frag.crew_interpreter)

    return impacts


# ---------------------------------------------------------------------------
# Journal view (for UI)
# ---------------------------------------------------------------------------

def get_journal_view(state: InvestigationState) -> list[dict]:
    """Get the player-facing journal. Fragments organized by thread.

    Not a task list. A record of what is known and what it might mean.
    """
    entries = []
    for thread in state.threads.values():
        if thread.state == ThreadState.DORMANT:
            continue

        thread_entry = {
            "thread_id": thread.id,
            "title": thread.title,
            "premise": thread.premise,
            "state": thread.state.value,
            "fragments": [],
            "connections_found": 0,
            "total_evidence_weight": sum(f.grade.weight for f in thread.fragments),
        }

        for frag in thread.fragments:
            thread_entry["fragments"].append({
                "content": frag.content,
                "grade": frag.grade.value,
                "source": frag.source_detail,
                "day": frag.day_acquired,
                "interpreter": frag.crew_interpreter,
                "connections": len(frag.connections),
            })

        thread_entry["connections_found"] = len(check_corroboration(thread))
        entries.append(thread_entry)

    return entries


# ---------------------------------------------------------------------------
# Thread factory (for building specific investigation threads)
# ---------------------------------------------------------------------------

def create_medical_cargo_thread() -> InvestigationThread:
    """The Medical Shipment — a complete investigation thread.

    Suspicious medical cargo is being routed through Keth space.
    The shipments don't match Keth seasonal demand patterns.
    Someone is using medical supplies as cover for something else.

    Can be discovered through:
    - Trade: hauling medical cargo and noticing price anomalies
    - Combat: salvaging a destroyed freighter's manifest
    - Cultural: Keth crew member recognizes non-seasonal medical orders
    - Station: overhearing dockworkers mention unusual shipments
    - Crew: Keth crew member's medical debt connects to the supplier

    Thread proves the conspiracy touches the player's disgrace.
    """
    return InvestigationThread(
        id="medical_cargo",
        title="The Medical Shipment",
        premise="Medical cargo is being routed through Keth space in patterns "
                "that don't match seasonal demand. Someone is hiding something.",
        resolution_threshold=12,   # need solid evidence
        fragments_required=3,      # at least 3 distinct pieces
        max_delay_days=45,         # 45 days before trail goes cold
        delay_consequence_tag="medical_evidence_destroyed",
        sources=[
            # Trade source: haul medical cargo to Keth station
            LeadSource(
                fragment_id="med_price_anomaly",
                source_type=SourceType.TRADE,
                trigger="trade_medical_at_keth",
                description="Haul medical supplies to a Keth station during off-season",
            ),
            # Combat source: salvage a destroyed freighter
            LeadSource(
                fragment_id="med_manifest",
                source_type=SourceType.COMBAT,
                trigger="salvage_freighter_debris",
                description="Search the wreckage of a destroyed medical freighter",
            ),
            # Cultural source: Keth crew interprets the anomaly
            LeadSource(
                fragment_id="med_seasonal_mismatch",
                source_type=SourceType.CULTURAL,
                trigger="keth_medical_analysis",
                crew_required="thal_communion",
                civ_knowledge_required="keth",
                knowledge_level_required=1,
                description="A Keth crew member recognizes the orders don't match the season",
            ),
            # Station source: overhear dockworkers
            LeadSource(
                fragment_id="med_dock_rumor",
                source_type=SourceType.STATION,
                trigger="station_rumor_keth_medical",
                description="Overhear dockworkers at a Keth station discussing unusual shipments",
            ),
            # Crew source: Keth crew member's personal connection
            LeadSource(
                fragment_id="med_personal_connection",
                source_type=SourceType.CREW,
                trigger="thal_medical_debt_reveal",
                crew_required="thal_communion",
                description="Thal reveals their medical debt connects to the supplier",
            ),
            # Transit source: intercept a communication
            LeadSource(
                fragment_id="med_intercepted_comms",
                source_type=SourceType.TRANSIT,
                trigger="intercept_medical_comms",
                reputation_required={"compact": -10},  # need to be somewhat outside the law
                description="Intercept an encrypted communication about medical shipment routing",
            ),
        ],
    )


def get_medical_cargo_fragments() -> dict[str, Fragment]:
    """Pre-defined fragments for the medical cargo thread.

    Each fragment is a piece of truth. Together they reveal the pattern.
    """
    return {
        "med_price_anomaly": Fragment(
            id="med_price_anomaly",
            thread_id="medical_cargo",
            content="Medical supply prices at this Keth station are wrong. "
                    "Demand is high but it's not the right season for illness. "
                    "Someone is buying in bulk for reasons that aren't medical.",
            source_type="trade",
            source_detail="Price data at Keth relay station",
            grade=EvidenceGrade.CLUE,
            day_acquired=0,
            connections=["med_seasonal_mismatch", "med_manifest"],
        ),
        "med_manifest": Fragment(
            id="med_manifest",
            thread_id="medical_cargo",
            content="The freighter's manifest lists medical supplies but the "
                    "cargo weights don't match. The containers are too heavy "
                    "for medical equipment. Something else is inside.",
            source_type="combat",
            source_detail="Salvaged manifest from destroyed freighter",
            grade=EvidenceGrade.CLUE,
            day_acquired=0,
            connections=["med_price_anomaly", "med_intercepted_comms"],
        ),
        "med_seasonal_mismatch": Fragment(
            id="med_seasonal_mismatch",
            thread_id="medical_cargo",
            content="These medical orders were placed during emergence — the healthiest "
                    "season. No Communion facility would need this volume. "
                    "The buyer isn't Keth.",
            source_type="cultural",
            source_detail="Thal's analysis of Keth medical procurement patterns",
            grade=EvidenceGrade.CORROBORATED,
            day_acquired=0,
            connections=["med_price_anomaly", "med_personal_connection"],
            crew_interpreter="thal_communion",
        ),
        "med_dock_rumor": Fragment(
            id="med_dock_rumor",
            thread_id="medical_cargo",
            content="Dockworkers say the medical crates go into a warehouse "
                    "that never opens during daylight. The receiving signature "
                    "is always the same name — not a Keth name.",
            source_type="station",
            source_detail="Overheard at Keth relay station docks",
            grade=EvidenceGrade.RUMOR,
            day_acquired=0,
            connections=["med_price_anomaly"],
        ),
        "med_personal_connection": Fragment(
            id="med_personal_connection",
            thread_id="medical_cargo",
            content="Thal's medical debt was bought by the same supplier routing "
                    "these shipments. The supplier isn't a medical company — "
                    "they're a Compact military contractor. The one that processed "
                    "your discharge papers.",
            source_type="crew",
            source_detail="Thal's personal revelation about their medical debt",
            grade=EvidenceGrade.ACTIONABLE,
            day_acquired=0,
            connections=["med_seasonal_mismatch", "med_intercepted_comms"],
            crew_interpreter="thal_communion",
        ),
        "med_intercepted_comms": Fragment(
            id="med_intercepted_comms",
            thread_id="medical_cargo",
            content="Encrypted communication confirms: the medical supplies are "
                    "cover for Ancestor tech components being moved through Keth "
                    "space. The routing avoids all Compact patrol lanes. "
                    "Authorization code matches your old unit's designation.",
            source_type="transit",
            source_detail="Intercepted encrypted transmission, deep-system relay",
            grade=EvidenceGrade.ACTIONABLE,
            day_acquired=0,
            connections=["med_manifest", "med_personal_connection"],
        ),
    }


# ---------------------------------------------------------------------------
# 7A: Ghost Tonnage thread
# ---------------------------------------------------------------------------

def create_ghost_tonnage_thread() -> InvestigationThread:
    """Ghost Tonnage — aid and harvest shipments arriving underweight.

    Logistics fraud disguised as weather loss and lane hazards. Someone is
    skimming aid, harvest, and memorial shipments on paper-clean routes.
    Different from Medical Shipment (which is tech smuggling disguised as
    medical cargo). Ghost Tonnage is about systemic theft from vulnerable
    supply chains.

    Can be discovered through:
    - Trade: manifest weight mismatches when buying/selling at Keth stations
    - Combat: pirate cargo that doesn't match their stolen paperwork
    - Cultural: Keth crew recognizes shortage patterns as unnatural
    - Crew: Sera Vale reads the document trail
    - Station: dockworkers at Mourning Quay mention missing deliveries
    """
    return InvestigationThread(
        id="ghost_tonnage",
        title="Ghost Tonnage",
        premise="Aid, harvest, and memorial shipments keep arriving underweight. "
                "Losses are blamed on weather and lane hazards, but only on "
                "paper-clean routes. Someone is skimming.",
        resolution_threshold=10,
        fragments_required=3,
        max_delay_days=40,
        delay_consequence_tag="ghost_tonnage_covered_up",
        sources=[
            LeadSource(
                fragment_id="ghost_weight_mismatch",
                source_type=SourceType.TRADE,
                trigger="trade_at_mourning_quay",
                description="Notice manifest weight mismatches when trading at Mourning Quay",
            ),
            LeadSource(
                fragment_id="ghost_pirate_paperwork",
                source_type=SourceType.COMBAT,
                trigger="salvage_pirate_cargo",
                description="Salvaged pirate cargo doesn't match the paperwork they stole",
            ),
            LeadSource(
                fragment_id="ghost_shortage_pattern",
                source_type=SourceType.CULTURAL,
                trigger="keth_shortage_analysis",
                crew_required="thal_communion",
                civ_knowledge_required="keth",
                knowledge_level_required=1,
                description="Thal recognizes the shortage pattern as unnatural for this season",
            ),
            LeadSource(
                fragment_id="ghost_document_trail",
                source_type=SourceType.CREW,
                trigger="sera_manifest_analysis",
                crew_required="sera_vale",
                description="Sera reads the document trail and finds the same audit signature",
            ),
            LeadSource(
                fragment_id="ghost_dock_complaint",
                source_type=SourceType.STATION,
                trigger="station_rumor_keth_medical",
                description="Dockworkers at Mourning Quay complain about missing deliveries",
            ),
        ],
    )


def get_ghost_tonnage_fragments() -> dict[str, Fragment]:
    """Pre-defined fragments for the Ghost Tonnage thread."""
    return {
        "ghost_weight_mismatch": Fragment(
            id="ghost_weight_mismatch",
            thread_id="ghost_tonnage",
            content="The manifest says 40 tonnes of harvest compound. The scale says 31. "
                    "The difference is too consistent to be spillage.",
            source_type="trade",
            source_detail="Weight discrepancy at Mourning Quay loading dock",
            grade=EvidenceGrade.CLUE,
            day_acquired=0,
            connections=["ghost_shortage_pattern", "ghost_document_trail"],
        ),
        "ghost_pirate_paperwork": Fragment(
            id="ghost_pirate_paperwork",
            thread_id="ghost_tonnage",
            content="The raider was carrying harvest compounds — but their forged manifest "
                    "lists medical supplies. Someone gave them the wrong cover story. "
                    "Or the cargo was swapped before it reached the lane.",
            source_type="combat",
            source_detail="Salvaged manifest from defeated pirate vessel",
            grade=EvidenceGrade.CLUE,
            day_acquired=0,
            connections=["ghost_weight_mismatch"],
        ),
        "ghost_shortage_pattern": Fragment(
            id="ghost_shortage_pattern",
            thread_id="ghost_tonnage",
            content="Thal says the shortages follow a pattern that matches audit cycles, "
                    "not weather or lane loss. Someone is timing the skim to arrive "
                    "between inspections.",
            source_type="cultural",
            source_detail="Thal's analysis of Communion supply records",
            grade=EvidenceGrade.CORROBORATED,
            day_acquired=0,
            connections=["ghost_weight_mismatch", "ghost_document_trail"],
            crew_interpreter="thal_communion",
        ),
        "ghost_document_trail": Fragment(
            id="ghost_document_trail",
            thread_id="ghost_tonnage",
            content="The same audit signature appears on every clean manifest that later "
                    "shows a weight discrepancy. Sera says the signature belongs to a "
                    "Compact logistics officer who was reassigned after your discharge.",
            source_type="crew",
            source_detail="Sera Vale's document analysis",
            grade=EvidenceGrade.ACTIONABLE,
            day_acquired=0,
            connections=["ghost_shortage_pattern", "ghost_weight_mismatch"],
            crew_interpreter="sera_vale",
        ),
        "ghost_dock_complaint": Fragment(
            id="ghost_dock_complaint",
            thread_id="ghost_tonnage",
            content="The dock elder says three memorial shipments arrived light this season. "
                    "Families are angry. The Communion is investigating internally. "
                    "Nobody outside has asked about it — until you.",
            source_type="station",
            source_detail="Mourning Quay dock elder conversation",
            grade=EvidenceGrade.RUMOR,
            day_acquired=0,
            connections=["ghost_weight_mismatch"],
        ),
    }


# ---------------------------------------------------------------------------
# 7B: Paper Fleet thread
# ---------------------------------------------------------------------------

def create_paper_fleet_thread() -> InvestigationThread:
    """Paper Fleet — ships disappearing through layered legal claims.

    Different from Ghost Tonnage (logistics fraud) and Medical Shipment
    (tech smuggling). Paper Fleet is about institutional disappearance:
    ships and cargo vanishing through emergency reallocations, sealed
    transfers, and claims that look valid from any one angle.

    Deepens the conspiracy: someone is using Compact legal machinery
    to make assets disappear without anyone technically breaking a law.

    Can be discovered through:
    - Trade: bond plate irregularities at Registry Spindle
    - Combat: seized ship's registry doesn't match any active claim
    - Cultural: Compact crew interprets the claim chain
    - Crew: Nera recognizes the filing pattern from her registry days
    - Station: overheard at Registry Spindle about missing fleet entries
    """
    return InvestigationThread(
        id="paper_fleet",
        title="Paper Fleet",
        premise="Ships are disappearing through layered claims, emergency reallocations, "
                "and sealed transfers. Each step looks legal from one angle. "
                "Together, they add up to institutionalized theft.",
        resolution_threshold=12,
        fragments_required=3,
        max_delay_days=50,
        delay_consequence_tag="paper_fleet_records_sealed",
        sources=[
            LeadSource(
                fragment_id="paper_fleet_registry_flag",
                source_type=SourceType.STATION,
                trigger="station_registry_spindle_query",
                description="Query the registry at Registry Spindle and notice missing entries",
            ),
            LeadSource(
                fragment_id="paper_fleet_bond_irregularity",
                source_type=SourceType.TRADE,
                trigger="trade_bond_plate_registry",
                description="Bond plate serial numbers at Registry Spindle don't match the manifest chain",
            ),
            LeadSource(
                fragment_id="paper_fleet_seized_mismatch",
                source_type=SourceType.COMBAT,
                trigger="salvage_seized_ship",
                description="A seized ship's registry data doesn't match any active claim on file",
            ),
            LeadSource(
                fragment_id="paper_fleet_filing_pattern",
                source_type=SourceType.CREW,
                trigger="nera_filing_analysis",
                crew_required="nera_quill",
                description="Nera recognizes the claim filing pattern from her registry days",
            ),
            LeadSource(
                fragment_id="paper_fleet_compact_interpretation",
                source_type=SourceType.CULTURAL,
                trigger="compact_legal_analysis",
                crew_required="sera_vale",
                civ_knowledge_required="compact",
                knowledge_level_required=2,
                description="Sera interprets the legal chain and finds the authorization loop",
            ),
        ],
    )


def get_paper_fleet_fragments() -> dict[str, Fragment]:
    """Pre-defined fragments for the Paper Fleet thread."""
    return {
        "paper_fleet_registry_flag": Fragment(
            id="paper_fleet_registry_flag",
            thread_id="paper_fleet",
            content="Three ships registered to independent captains were transferred to a "
                    "Compact holding entity last quarter. The transfer orders are sealed. "
                    "The holding entity has no public trade record.",
            source_type="station",
            source_detail="Registry Spindle public records query",
            grade=EvidenceGrade.CLUE,
            day_acquired=0,
            connections=["paper_fleet_bond_irregularity", "paper_fleet_filing_pattern"],
        ),
        "paper_fleet_bond_irregularity": Fragment(
            id="paper_fleet_bond_irregularity",
            thread_id="paper_fleet",
            content="The bond plates on this cargo were issued six months ago but reference "
                    "a manifest that was filed yesterday. Someone backdated the legitimacy chain.",
            source_type="trade",
            source_detail="Bond plate audit at Registry Spindle",
            grade=EvidenceGrade.CLUE,
            day_acquired=0,
            connections=["paper_fleet_registry_flag", "paper_fleet_compact_interpretation"],
        ),
        "paper_fleet_seized_mismatch": Fragment(
            id="paper_fleet_seized_mismatch",
            thread_id="paper_fleet",
            content="This ship was supposedly seized under emergency reallocation. "
                    "But the reallocation order references a shortage that ended two weeks "
                    "before the seizure was filed. The timeline doesn't survive inspection.",
            source_type="combat",
            source_detail="Registry data from salvaged Compact-flagged vessel",
            grade=EvidenceGrade.CORROBORATED,
            day_acquired=0,
            connections=["paper_fleet_registry_flag", "paper_fleet_filing_pattern"],
        ),
        "paper_fleet_filing_pattern": Fragment(
            id="paper_fleet_filing_pattern",
            thread_id="paper_fleet",
            content="Nera says: 'I've seen this pattern. Emergency reallocation, sealed transfer, "
                    "holding entity, dormant registry. It's how the Compact makes things disappear "
                    "without anyone technically breaking a law. I signed three of these before I "
                    "understood what I was looking at.'",
            source_type="crew",
            source_detail="Nera Quill's institutional analysis",
            grade=EvidenceGrade.ACTIONABLE,
            day_acquired=0,
            connections=["paper_fleet_registry_flag", "paper_fleet_compact_interpretation"],
            crew_interpreter="nera_quill",
        ),
        "paper_fleet_compact_interpretation": Fragment(
            id="paper_fleet_compact_interpretation",
            thread_id="paper_fleet",
            content="Sera traced the authorization chain. Every transfer was approved by the "
                    "same three-person committee. Two of them sit on the corporate board. "
                    "The third is the officer who processed your discharge. "
                    "The Paper Fleet isn't a theft ring. It's a procurement channel.",
            source_type="cultural",
            source_detail="Sera Vale's legal chain analysis",
            grade=EvidenceGrade.ACTIONABLE,
            day_acquired=0,
            connections=["paper_fleet_bond_irregularity", "paper_fleet_filing_pattern"],
            crew_interpreter="sera_vale",
        ),
    }


# ---------------------------------------------------------------------------
# 7C: Dry Ledger thread
# ---------------------------------------------------------------------------

def create_dry_ledger_thread() -> InvestigationThread:
    """Dry Ledger — manufactured scarcity.

    Different from Ghost Tonnage (logistics fraud) and Paper Fleet
    (institutional disappearance). Dry Ledger is about shortages being
    amplified on paper and in scheduling, not just caused by weather
    or conflict. Someone is manufacturing desperation.

    This deepens the conspiracy: the same institutional machinery that
    makes ships disappear (Paper Fleet) and skims cargo (Ghost Tonnage)
    is also engineering the conditions that make those operations invisible.

    Can be discovered through:
    - Trade: ration prices at Queue of Flags don't match actual supply
    - Combat: convoy manifest shows rerouted cargo that never arrived
    - Cultural: Orryn crew interprets scheduling patterns as deliberate
    - Crew: Ilen recognizes the priority manipulation from inside
    - Station: queue delays at Queue of Flags follow political patterns
    """
    return InvestigationThread(
        id="dry_ledger",
        title="Dry Ledger",
        premise="Shortages are being amplified on paper and in convoy scheduling. "
                "Real supply exists but is being routed around the stations that need it. "
                "Someone is manufacturing desperation — and profiting from the emergency response.",
        resolution_threshold=10,
        fragments_required=3,
        max_delay_days=35,
        delay_consequence_tag="dry_ledger_shortage_worsens",
        sources=[
            LeadSource(
                fragment_id="dry_ledger_price_mismatch",
                source_type=SourceType.TRADE,
                trigger="trade_ration_queue",
                description="Ration prices at Queue of Flags don't match the supply ships in dock",
            ),
            LeadSource(
                fragment_id="dry_ledger_convoy_reroute",
                source_type=SourceType.COMBAT,
                trigger="salvage_convoy_manifest",
                description="A convoy manifest shows cargo rerouted to a station not on any shortage list",
            ),
            LeadSource(
                fragment_id="dry_ledger_schedule_pattern",
                source_type=SourceType.CULTURAL,
                trigger="orryn_schedule_analysis",
                crew_required="ilen_marr",
                civ_knowledge_required="orryn",
                knowledge_level_required=1,
                description="Ilen reads the convoy schedule and finds deliberate bottlenecking",
            ),
            LeadSource(
                fragment_id="dry_ledger_priority_manipulation",
                source_type=SourceType.CREW,
                trigger="ilen_priority_reveal",
                crew_required="ilen_marr",
                description="Ilen reveals they've seen this pattern before — priority slots sold, not earned",
            ),
            LeadSource(
                fragment_id="dry_ledger_queue_delay",
                source_type=SourceType.STATION,
                trigger="station_queue_of_flags_query",
                description="Queue delays at Queue of Flags follow political patterns, not supply ones",
            ),
        ],
    )


def get_dry_ledger_fragments() -> dict[str, Fragment]:
    """Pre-defined fragments for the Dry Ledger thread."""
    return {
        "dry_ledger_price_mismatch": Fragment(
            id="dry_ledger_price_mismatch",
            thread_id="dry_ledger",
            content="Ration grain is priced at shortage rates, but there are three full supply "
                    "ships in the docking queue. The supply exists. The price says it doesn't. "
                    "Someone is holding cargo until the emergency premium peaks.",
            source_type="trade",
            source_detail="Price observation at Queue of Flags",
            grade=EvidenceGrade.CLUE,
            day_acquired=0,
            connections=["dry_ledger_schedule_pattern", "dry_ledger_priority_manipulation"],
        ),
        "dry_ledger_convoy_reroute": Fragment(
            id="dry_ledger_convoy_reroute",
            thread_id="dry_ledger",
            content="This convoy was supposed to deliver coolant ampoules to Communion Relay. "
                    "The manifest shows it was rerouted to a Compact military depot that isn't "
                    "on any shortage list. The reroute was authorized by 'emergency priority.'",
            source_type="combat",
            source_detail="Manifest from salvaged convoy escort vessel",
            grade=EvidenceGrade.CLUE,
            day_acquired=0,
            connections=["dry_ledger_price_mismatch"],
        ),
        "dry_ledger_schedule_pattern": Fragment(
            id="dry_ledger_schedule_pattern",
            thread_id="dry_ledger",
            content="Ilen says: 'The bottleneck isn't capacity. It's scheduling. Someone is "
                    "inserting holds into the convoy queue that delay civilian relief while "
                    "priority cargo moves through the same lanes at full speed. "
                    "The holds are authorized. The authorization is circular.'",
            source_type="cultural",
            source_detail="Ilen Marr's convoy schedule analysis",
            grade=EvidenceGrade.CORROBORATED,
            day_acquired=0,
            connections=["dry_ledger_price_mismatch", "dry_ledger_priority_manipulation"],
            crew_interpreter="ilen_marr",
        ),
        "dry_ledger_priority_manipulation": Fragment(
            id="dry_ledger_priority_manipulation",
            thread_id="dry_ledger",
            content="Ilen reveals: 'Priority slots are being sold. Not openly — through "
                    "intermediary contracts that look like emergency allotments. The same "
                    "broker network that reroutes relief cargo sells priority access to "
                    "whoever pays. I know because I used to schedule for them.'",
            source_type="crew",
            source_detail="Ilen Marr's personal revelation",
            grade=EvidenceGrade.ACTIONABLE,
            day_acquired=0,
            connections=["dry_ledger_schedule_pattern", "dry_ledger_queue_delay"],
            crew_interpreter="ilen_marr",
        ),
        "dry_ledger_queue_delay": Fragment(
            id="dry_ledger_queue_delay",
            thread_id="dry_ledger",
            content="The queue delays follow a pattern. Ships carrying relief cargo for Keth "
                    "stations wait longest. Ships carrying Compact-flagged cargo move first. "
                    "The Orryn running the queue say it's 'protocol.' But the protocol "
                    "changed three months ago, and nobody voted on it.",
            source_type="station",
            source_detail="Queue pattern observation at Queue of Flags",
            grade=EvidenceGrade.RUMOR,
            day_acquired=0,
            connections=["dry_ledger_price_mismatch"],
        ),
    }
