"""Campaign engine — milestones, career profile, and victory truth.

This is the interpretive layer: it reads session truth and derives what kind
of trade house the player actually built. No fiction, no flavor toggles.
Everything here is mechanically grounded in ledger, contracts, reputation,
infrastructure, and ship history.

Core functions:
  - evaluate_milestones(session_snapshot) -> newly completed milestones
  - compute_career_profile(session_snapshot) -> ranked profile tags
  - compute_victory_progress(session_snapshot) -> per-path progress

Design law:
  - Milestones derive from actual business history, not flags or counters.
  - Profile tags are weighted evidence, not arbitrary labels.
  - Victory paths represent commercial identities, not checklists.
  - Two runs that end rich in different ways must be distinguishable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from portlight.engine.contracts import ContractBoard
    from portlight.engine.infrastructure import InfrastructureState
    from portlight.engine.models import Captain, WorldState
    from portlight.receipts.models import ReceiptLedger


# ---------------------------------------------------------------------------
# Milestone families
# ---------------------------------------------------------------------------

class MilestoneFamily(str, Enum):
    REGIONAL_FOOTHOLD = "regional_foothold"
    LAWFUL_HOUSE = "lawful_house"
    SHADOW_NETWORK = "shadow_network"
    OCEANIC_REACH = "oceanic_reach"
    COMMERCIAL_FINANCE = "commercial_finance"
    INTEGRATED_HOUSE = "integrated_house"


# ---------------------------------------------------------------------------
# Milestone spec (content-driven definition)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MilestoneSpec:
    """Static definition of a milestone. Content data, not runtime state."""
    id: str
    name: str
    family: MilestoneFamily
    description: str
    evaluator: str               # function name in _EVALUATORS registry


# ---------------------------------------------------------------------------
# Milestone completion (runtime state)
# ---------------------------------------------------------------------------

@dataclass
class MilestoneCompletion:
    """Record of a completed milestone."""
    milestone_id: str
    completed_day: int
    evidence: str = ""           # human-readable summary of what triggered it


# ---------------------------------------------------------------------------
# Campaign state (persisted)
# ---------------------------------------------------------------------------

@dataclass
class VictoryCompletion:
    """Record of a completed victory path."""
    path_id: str
    completion_day: int
    summary: str
    is_first: bool = False  # first path completed in this run


@dataclass
class CampaignState:
    """All campaign progress. Persisted in save file."""
    completed: list[MilestoneCompletion] = field(default_factory=list)
    completed_paths: list[VictoryCompletion] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Session snapshot — read-only view for evaluation
# ---------------------------------------------------------------------------

@dataclass
class SessionSnapshot:
    """Immutable snapshot of session state for milestone evaluation.

    This decouples the campaign engine from the session's mutable internals.
    Built by session.py before evaluation.
    """
    captain: "Captain"
    world: "WorldState"
    board: "ContractBoard"
    infra: "InfrastructureState"
    ledger: "ReceiptLedger"
    campaign: CampaignState


# ---------------------------------------------------------------------------
# Career profile
# ---------------------------------------------------------------------------

class ProfileConfidence(str, Enum):
    FORMING = "Forming"         # early signal, not yet established
    MODERATE = "Moderate"       # meaningful evidence, not dominant
    STRONG = "Strong"           # clear pattern with solid evidence
    DEFINING = "Defining"       # dominant identity of the run


@dataclass
class ProfileScore:
    """Legacy profile score — kept for backward compat in tests."""
    tag: str
    score: float
    evidence: list[str] = field(default_factory=list)


@dataclass
class CareerProfileTag:
    """A richer profile tag with lifetime, recent, and confidence scoring."""
    tag: str
    lifetime_score: float       # accumulated business history
    recent_score: float         # what player is doing now (last ~20 days)
    combined_score: float       # weighted blend for ranking
    confidence: ProfileConfidence
    evidence: list[str] = field(default_factory=list)


@dataclass
class CareerProfile:
    """Interpreted career profile — not just a ranked list."""
    primary: CareerProfileTag | None = None
    secondaries: list[CareerProfileTag] = field(default_factory=list)
    emerging: CareerProfileTag | None = None
    all_tags: list[CareerProfileTag] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Victory path
# ---------------------------------------------------------------------------

class RequirementStatus(str, Enum):
    MET = "met"
    MISSING = "missing"
    BLOCKED = "blocked"


@dataclass
class VictoryRequirement:
    """One requirement within a victory path."""
    description: str
    status: RequirementStatus
    detail: str = ""
    action: str = ""      # human-readable next step when missing

    @property
    def met(self) -> bool:
        return self.status == RequirementStatus.MET


@dataclass
class VictoryPathStatus:
    """Full diagnostic for one victory path."""
    path_id: str
    name: str
    requirements: list[VictoryRequirement] = field(default_factory=list)
    candidate_strength: float = 0.0
    completion_day: int = 0            # 0 = not yet completed
    completion_summary: str = ""

    @property
    def met_count(self) -> int:
        return sum(1 for r in self.requirements if r.met)

    @property
    def total_count(self) -> int:
        return len(self.requirements)

    @property
    def is_complete(self) -> bool:
        return all(r.met for r in self.requirements)

    @property
    def requirements_met(self) -> list[VictoryRequirement]:
        return [r for r in self.requirements if r.status == RequirementStatus.MET]

    @property
    def requirements_missing(self) -> list[VictoryRequirement]:
        return [r for r in self.requirements if r.status == RequirementStatus.MISSING]

    @property
    def requirements_blocked(self) -> list[VictoryRequirement]:
        return [r for r in self.requirements if r.status == RequirementStatus.BLOCKED]

    @property
    def is_active_candidate(self) -> bool:
        """At least half the requirements are met — this path is live."""
        return self.total_count > 0 and self.met_count >= self.total_count // 2


# Keep legacy alias for backward compat in existing test imports
VictoryPathProgress = VictoryPathStatus


# ---------------------------------------------------------------------------
# Evaluator helpers — read session truth
# ---------------------------------------------------------------------------

def _completed_ids(snap: SessionSnapshot) -> set[str]:
    return {c.milestone_id for c in snap.campaign.completed}


def _active_warehouses(snap: SessionSnapshot) -> list:
    return [w for w in snap.infra.warehouses if w.active]


def _active_brokers(snap: SessionSnapshot) -> list:
    from portlight.engine.infrastructure import BrokerTier
    return [b for b in snap.infra.brokers if b.active and b.tier != BrokerTier.NONE]


def _active_licenses(snap: SessionSnapshot) -> list:
    return [lic for lic in snap.infra.licenses if lic.active]


def _has_license(snap: SessionSnapshot, license_id: str) -> bool:
    return any(lic.license_id == license_id and lic.active for lic in snap.infra.licenses)


def _trust_tier(snap: SessionSnapshot) -> str:
    from portlight.engine.reputation import get_trust_tier
    return get_trust_tier(snap.captain.standing)


def _trust_rank(tier: str) -> int:
    return {"unproven": 0, "new": 1, "credible": 2, "reliable": 3, "trusted": 4}.get(tier, 0)


def _regions_with_standing(snap: SessionSnapshot, min_standing: int) -> list[str]:
    return [r for r, s in snap.captain.standing.regional_standing.items() if s >= min_standing]


def _max_heat(snap: SessionSnapshot) -> int:
    return max(snap.captain.standing.customs_heat.values()) if snap.captain.standing.customs_heat else 0


def _min_heat(snap: SessionSnapshot) -> int:
    return min(snap.captain.standing.customs_heat.values()) if snap.captain.standing.customs_heat else 0


def _completed_contracts(snap: SessionSnapshot) -> list:
    return [o for o in snap.board.completed if o.outcome_type in ("completed", "completed_bonus")]


def _completed_contract_families(snap: SessionSnapshot) -> dict[str, int]:
    """Count completed contracts by contract family."""
    counts: dict[str, int] = {}
    for c in snap.board.completed:
        if c.outcome_type in ("completed", "completed_bonus") and c.family is not None:
            key = c.family.value
            counts[key] = counts.get(key, 0) + 1
    return counts


def _total_completed_contracts(snap: SessionSnapshot) -> int:
    return len(_completed_contracts(snap))


def _total_trades(snap: SessionSnapshot) -> int:
    return len(snap.ledger.receipts)


def _ship_class(snap: SessionSnapshot) -> str:
    if not snap.captain.ship:
        return "sloop"
    from portlight.content.ships import SHIPS
    template = SHIPS.get(snap.captain.ship.template_id)
    return template.ship_class.value if template else "sloop"


def _regions_with_broker(snap: SessionSnapshot) -> set[str]:
    from portlight.engine.infrastructure import BrokerTier
    return {b.region for b in snap.infra.brokers if b.active and b.tier != BrokerTier.NONE}


def _regions_with_warehouse(snap: SessionSnapshot) -> set[str]:
    """Regions that have an active warehouse (need port->region mapping)."""
    regions = set()
    for w in snap.infra.warehouses:
        if not w.active:
            continue
        port = snap.world.ports.get(w.port_id)
        if port:
            regions.add(port.region)
    return regions


def _credit_active_no_defaults(snap: SessionSnapshot) -> bool:
    credit = snap.infra.credit
    if credit is None:
        return False
    return credit.active and credit.defaults == 0


def _insurance_claims_paid(snap: SessionSnapshot) -> int:
    return sum(1 for c in snap.infra.claims if not c.denied and c.payout > 0)


def _policies_purchased(snap: SessionSnapshot) -> int:
    return len(snap.infra.policies)


# ---------------------------------------------------------------------------
# Milestone evaluators — each returns (met, evidence_string)
# ---------------------------------------------------------------------------

def _eval_first_warehouse(snap: SessionSnapshot) -> tuple[bool, str]:
    wh = _active_warehouses(snap)
    if wh:
        return True, f"Warehouse at {wh[0].port_id}"
    return False, ""


def _eval_first_broker(snap: SessionSnapshot) -> tuple[bool, str]:
    brokers = _active_brokers(snap)
    if brokers:
        return True, f"Broker in {brokers[0].region}"
    return False, ""


def _eval_standing_one_region(snap: SessionSnapshot) -> tuple[bool, str]:
    regions = _regions_with_standing(snap, 10)
    if regions:
        return True, f"Standing 10+ in {regions[0]}"
    return False, ""


def _eval_strong_standing_one_region(snap: SessionSnapshot) -> tuple[bool, str]:
    regions = _regions_with_standing(snap, 25)
    if regions:
        return True, f"Standing 25+ in {regions[0]}"
    return False, ""


def _eval_presence_two_regions(snap: SessionSnapshot) -> tuple[bool, str]:
    regions = _regions_with_standing(snap, 5)
    if len(regions) >= 2:
        return True, f"Established in {', '.join(regions[:2])}"
    return False, ""


def _eval_sustained_three_regions(snap: SessionSnapshot) -> tuple[bool, str]:
    """Registered evaluator with no milestone spec yet — reserved for future use."""
    regions = _regions_with_standing(snap, 10)
    if len(regions) >= 3:
        return True, "Standing 10+ in all three regions"
    return False, ""


# --- Lawful house ---

def _eval_credible_trust(snap: SessionSnapshot) -> tuple[bool, str]:
    tier = _trust_tier(snap)
    if _trust_rank(tier) >= 2:
        return True, f"Trust tier: {tier}"
    return False, ""


def _eval_reliable_trust(snap: SessionSnapshot) -> tuple[bool, str]:
    tier = _trust_tier(snap)
    if _trust_rank(tier) >= 3:
        return True, f"Trust tier: {tier}"
    return False, ""


def _eval_regional_charter(snap: SessionSnapshot) -> tuple[bool, str]:
    for lic_id in ("med_trade_charter", "wa_commerce_permit", "ei_access_charter"):
        if _has_license(snap, lic_id):
            return True, f"License: {lic_id}"
    return False, ""


def _eval_high_rep_charter(snap: SessionSnapshot) -> tuple[bool, str]:
    if _has_license(snap, "high_rep_charter"):
        return True, "High Reputation Commercial Charter acquired"
    return False, ""


def _eval_lawful_contracts_completed(snap: SessionSnapshot) -> tuple[bool, str]:
    count = _total_completed_contracts(snap)
    if count >= 5:
        return True, f"{count} contracts completed successfully"
    return False, ""


def _eval_low_heat_scaling(snap: SessionSnapshot) -> tuple[bool, str]:
    """Achieved reliable trust while keeping max heat <= 5."""
    tier = _trust_tier(snap)
    max_h = _max_heat(snap)
    if _trust_rank(tier) >= 3 and max_h <= 5:
        return True, f"Reliable trust with max heat {max_h}"
    return False, ""


# --- Shadow network ---

def _eval_first_discreet_success(snap: SessionSnapshot) -> tuple[bool, str]:
    from portlight.engine.contracts import ContractFamily
    for o in snap.board.completed:
        if o.outcome_type in ("completed", "completed_bonus"):
            # Use canonical family field when available, fall back to summary heuristic
            if o.family == ContractFamily.LUXURY_DISCREET:
                return True, "First discreet luxury delivery"
            if o.family is None and ("luxury" in o.summary.lower() or "discreet" in o.summary.lower()):
                return True, "First discreet luxury delivery"
    return False, ""


def _eval_elevated_heat_sustained(snap: SessionSnapshot) -> tuple[bool, str]:
    """Sustained heat >= 15 in any region while staying profitable."""
    max_h = _max_heat(snap)
    if max_h >= 15 and snap.captain.silver >= 500:
        return True, f"Operating at heat {max_h} with {snap.captain.silver} silver"
    return False, ""


def _eval_shadow_profitability(snap: SessionSnapshot) -> tuple[bool, str]:
    """Net profit >= 2000 while having sustained heat."""
    profit = snap.ledger.net_profit
    max_h = _max_heat(snap)
    if profit >= 2000 and max_h >= 10:
        return True, f"Profit {profit} with heat {max_h}"
    return False, ""


def _eval_seizure_recovery(snap: SessionSnapshot) -> tuple[bool, str]:
    """Survived a cargo seizure and still operating profitably."""
    had_seizure = any(
        i.incident_type == "inspection" and "seized" in i.description.lower()
        for i in snap.captain.standing.recent_incidents
    )
    if had_seizure and snap.captain.silver >= 300:
        return True, "Recovered from cargo seizure"
    return False, ""


# --- Oceanic reach ---

def _eval_ei_access(snap: SessionSnapshot) -> tuple[bool, str]:
    if _has_license(snap, "ei_access_charter"):
        return True, "East Indies Access Charter acquired"
    return False, ""


def _eval_ei_broker(snap: SessionSnapshot) -> tuple[bool, str]:
    if "East Indies" in _regions_with_broker(snap):
        return True, "Broker office in East Indies"
    return False, ""


def _eval_galleon_deployed(snap: SessionSnapshot) -> tuple[bool, str]:
    sc = _ship_class(snap)
    if sc in ("galleon", "man_of_war"):
        return True, f"Operating a {sc}"
    return False, ""


def _eval_ei_standing(snap: SessionSnapshot) -> tuple[bool, str]:
    standing = snap.captain.standing.regional_standing.get("East Indies", 0)
    if standing >= 15:
        return True, f"East Indies standing: {standing}"
    return False, ""


# --- Commercial finance ---

def _eval_first_insurance_success(snap: SessionSnapshot) -> tuple[bool, str]:
    paid = _insurance_claims_paid(snap)
    if paid >= 1:
        return True, f"{paid} insurance claims paid"
    return False, ""


def _eval_credit_opened(snap: SessionSnapshot) -> tuple[bool, str]:
    credit = snap.infra.credit
    if credit and credit.total_borrowed > 0:
        return True, f"Credit used, {credit.total_borrowed} total borrowed"
    return False, ""


def _eval_credit_clean(snap: SessionSnapshot) -> tuple[bool, str]:
    if _credit_active_no_defaults(snap) and snap.infra.credit.total_borrowed >= 200:
        return True, f"Borrowed {snap.infra.credit.total_borrowed} with no defaults"
    return False, ""


def _eval_leveraged_expansion(snap: SessionSnapshot) -> tuple[bool, str]:
    """Used credit + has multiple infrastructure assets."""
    credit = snap.infra.credit
    wh = len(_active_warehouses(snap))
    brokers = len(_active_brokers(snap))
    if credit and credit.total_borrowed >= 300 and credit.defaults == 0 and (wh + brokers) >= 3:
        return True, f"Borrowed {credit.total_borrowed}, {wh} warehouses + {brokers} brokers"
    return False, ""


# --- Integrated house ---

def _eval_multi_region_infra(snap: SessionSnapshot) -> tuple[bool, str]:
    wh_regions = _regions_with_warehouse(snap)
    bk_regions = _regions_with_broker(snap)
    infra_regions = wh_regions | bk_regions
    if len(infra_regions) >= 2:
        return True, f"Infrastructure in {', '.join(sorted(infra_regions))}"
    return False, ""


def _eval_full_spectrum(snap: SessionSnapshot) -> tuple[bool, str]:
    """Has warehouse + broker + license + insurance used + credit used."""
    wh = len(_active_warehouses(snap)) >= 1
    brokers = len(_active_brokers(snap)) >= 1
    licenses = len(_active_licenses(snap)) >= 1
    insured = _policies_purchased(snap) >= 1
    credit = snap.infra.credit is not None and snap.infra.credit.total_borrowed > 0
    met = sum([wh, brokers, licenses, insured, credit])
    if met >= 4:
        parts = []
        if wh:
            parts.append("warehouse")
        if brokers:
            parts.append("broker")
        if licenses:
            parts.append("license")
        if insured:
            parts.append("insurance")
        if credit:
            parts.append("credit")
        return True, f"Using {', '.join(parts)}"
    return False, ""


def _eval_major_contracts_multi_region(snap: SessionSnapshot) -> tuple[bool, str]:
    """5+ completed contracts and standing 10+ in 2+ regions."""
    contracts = _total_completed_contracts(snap)
    regions = _regions_with_standing(snap, 10)
    if contracts >= 5 and len(regions) >= 2:
        return True, f"{contracts} contracts, standing in {', '.join(regions)}"
    return False, ""


def _eval_brigantine_acquired(snap: SessionSnapshot) -> tuple[bool, str]:
    sc = _ship_class(snap)
    if sc in ("cutter", "brigantine", "galleon", "man_of_war"):
        return True, f"Operating a {sc}"
    return False, ""


# ---------------------------------------------------------------------------
# Evaluator registry
# ---------------------------------------------------------------------------

_EVALUATORS: dict[str, callable] = {
    "first_warehouse": _eval_first_warehouse,
    "first_broker": _eval_first_broker,
    "standing_one_region": _eval_standing_one_region,
    "strong_standing_one_region": _eval_strong_standing_one_region,
    "presence_two_regions": _eval_presence_two_regions,
    "sustained_three_regions": _eval_sustained_three_regions,
    "credible_trust": _eval_credible_trust,
    "reliable_trust": _eval_reliable_trust,
    "regional_charter": _eval_regional_charter,
    "high_rep_charter": _eval_high_rep_charter,
    "lawful_contracts_completed": _eval_lawful_contracts_completed,
    "low_heat_scaling": _eval_low_heat_scaling,
    "first_discreet_success": _eval_first_discreet_success,
    "elevated_heat_sustained": _eval_elevated_heat_sustained,
    "shadow_profitability": _eval_shadow_profitability,
    "seizure_recovery": _eval_seizure_recovery,
    "ei_access": _eval_ei_access,
    "ei_broker": _eval_ei_broker,
    "galleon_deployed": _eval_galleon_deployed,
    "ei_standing": _eval_ei_standing,
    "first_insurance_success": _eval_first_insurance_success,
    "credit_opened": _eval_credit_opened,
    "credit_clean": _eval_credit_clean,
    "leveraged_expansion": _eval_leveraged_expansion,
    "multi_region_infra": _eval_multi_region_infra,
    "full_spectrum": _eval_full_spectrum,
    "major_contracts_multi_region": _eval_major_contracts_multi_region,
    "brigantine_acquired": _eval_brigantine_acquired,
}


# ---------------------------------------------------------------------------
# Evaluate milestones
# ---------------------------------------------------------------------------

def evaluate_milestones(
    specs: list[MilestoneSpec],
    snap: SessionSnapshot,
) -> list[MilestoneCompletion]:
    """Check all milestones against current session state.

    Returns only newly completed milestones (not already in snap.campaign.completed).
    """
    already = _completed_ids(snap)
    newly: list[MilestoneCompletion] = []

    for spec in specs:
        if spec.id in already:
            continue
        evaluator = _EVALUATORS.get(spec.evaluator)
        if evaluator is None:
            continue
        met, evidence = evaluator(snap)
        if met:
            completion = MilestoneCompletion(
                milestone_id=spec.id,
                completed_day=snap.world.day,
                evidence=evidence,
            )
            newly.append(completion)
            already.add(spec.id)  # prevent double-fire in same pass

    return newly


# ---------------------------------------------------------------------------
# Career profile scoring
# ---------------------------------------------------------------------------

def _compute_base_scores(snap: SessionSnapshot) -> dict[str, tuple[float, list[str]]]:
    """Compute raw session-truth scores per tag. Returns {tag: (score, evidence)}."""
    rep = snap.captain.standing
    results: dict[str, tuple[float, list[str]]] = {}

    # --- Lawful House ---
    lawful = 0.0
    lawful_ev: list[str] = []
    tier = _trust_tier(snap)
    rank = _trust_rank(tier)
    lawful += rank * 10
    if rank >= 3:
        lawful_ev.append(f"trust: {tier}")
    if _min_heat(snap) <= 3:
        lawful += 15
        lawful_ev.append("low heat")
    for lic_id in ("med_trade_charter", "wa_commerce_permit", "ei_access_charter", "high_rep_charter"):
        if _has_license(snap, lic_id):
            lawful += 10
            lawful_ev.append(lic_id)
    completed = _total_completed_contracts(snap)
    lawful += min(completed * 3, 30)
    if completed >= 3:
        lawful_ev.append(f"{completed} contracts completed")
    results["Lawful House"] = (lawful, lawful_ev)

    # --- Shadow Operator ---
    shadow = 0.0
    shadow_ev: list[str] = []
    max_h = _max_heat(snap)
    if max_h >= 10:
        shadow += min(max_h * 2, 40)
        shadow_ev.append(f"max heat: {max_h}")
    if snap.captain.captain_type == "smuggler":
        shadow += 15
        shadow_ev.append("smuggler captain")
    seizures = sum(
        1 for i in rep.recent_incidents
        if "seized" in i.description.lower()
    )
    if seizures > 0 and snap.captain.silver >= 200:
        shadow += seizures * 10
        shadow_ev.append(f"survived {seizures} seizures")
    if snap.ledger.net_profit > 1500 and max_h >= 10:
        shadow += 20
        shadow_ev.append("profitable under heat")
    results["Shadow Operator"] = (shadow, shadow_ev)

    # --- Oceanic Carrier ---
    oceanic = 0.0
    oceanic_ev: list[str] = []
    ei_standing = rep.regional_standing.get("East Indies", 0)
    if ei_standing >= 5:
        oceanic += ei_standing * 2
        oceanic_ev.append(f"East Indies standing: {ei_standing}")
    if _has_license(snap, "ei_access_charter"):
        oceanic += 20
        oceanic_ev.append("EI access charter")
    if "East Indies" in _regions_with_broker(snap):
        oceanic += 15
        oceanic_ev.append("EI broker")
    if _ship_class(snap) == "galleon":
        oceanic += 25
        oceanic_ev.append("galleon operator")
    elif _ship_class(snap) == "brigantine":
        oceanic += 10
        oceanic_ev.append("brigantine capable")
    results["Oceanic Carrier"] = (oceanic, oceanic_ev)

    # --- Contract Specialist ---
    contract = 0.0
    contract_ev: list[str] = []
    contract += min(completed * 5, 50)
    if completed >= 3:
        contract_ev.append(f"{completed} contracts delivered")
    bonus_count = sum(1 for o in snap.board.completed if o.outcome_type == "completed_bonus")
    if bonus_count > 0:
        contract += bonus_count * 8
        contract_ev.append(f"{bonus_count} early bonuses")
    results["Contract Specialist"] = (contract, contract_ev)

    # --- Infrastructure Builder ---
    infra = 0.0
    infra_ev: list[str] = []
    wh = len(_active_warehouses(snap))
    bk = len(_active_brokers(snap))
    lics = len(_active_licenses(snap))
    infra += wh * 10 + bk * 12 + lics * 15
    if wh >= 2:
        infra_ev.append(f"{wh} warehouses")
    if bk >= 2:
        infra_ev.append(f"{bk} broker offices")
    if lics >= 2:
        infra_ev.append(f"{lics} licenses")
    regions = _regions_with_warehouse(snap) | _regions_with_broker(snap)
    if len(regions) >= 2:
        infra += 15
        infra_ev.append(f"presence in {len(regions)} regions")
    results["Infrastructure Builder"] = (infra, infra_ev)

    # --- Leveraged Trader ---
    leverage = 0.0
    leverage_ev: list[str] = []
    credit = snap.infra.credit
    if credit and credit.total_borrowed > 0:
        leverage += min(credit.total_borrowed // 10, 30)
        leverage_ev.append(f"borrowed {credit.total_borrowed}")
        if credit.defaults == 0:
            leverage += 20
            leverage_ev.append("no defaults")
        if credit.total_repaid > credit.total_borrowed * 0.5:
            leverage += 15
            leverage_ev.append("repaying responsibly")
    results["Leveraged Trader"] = (leverage, leverage_ev)

    # --- Risk-Managed Merchant ---
    risk = 0.0
    risk_ev: list[str] = []
    policies = _policies_purchased(snap)
    claims_paid = _insurance_claims_paid(snap)
    if policies > 0:
        risk += policies * 8
        risk_ev.append(f"{policies} policies purchased")
    if claims_paid > 0:
        risk += claims_paid * 12
        risk_ev.append(f"{claims_paid} claims paid")
    if policies >= 3 and _trust_rank(_trust_tier(snap)) >= 2:
        risk += 15
        risk_ev.append("systematic insurance user")
    results["Risk-Managed Merchant"] = (risk, risk_ev)

    return results


def _milestone_scores(snap: SessionSnapshot) -> dict[str, tuple[float, float]]:
    """Compute per-tag milestone contributions split into lifetime and recent.

    Returns {tag: (lifetime_bonus, recent_bonus)}.
    """
    from portlight.content.campaign import (
        MILESTONE_WEIGHT,
        PROFILE_MILESTONE_FAMILIES,
        RECENT_MILESTONE_BONUS,
        RECENT_WINDOW_DAYS,
    )

    current_day = snap.world.day
    lifetime: dict[str, float] = {}
    recent: dict[str, float] = {}

    # Build family->tag reverse map
    family_to_tags: dict[str, list[str]] = {}
    for tag, families in PROFILE_MILESTONE_FAMILIES.items():
        for fam in families:
            family_to_tags.setdefault(fam, []).append(tag)

    for comp in snap.campaign.completed:
        # Look up which family this milestone belongs to
        from portlight.content.campaign import MILESTONE_BY_ID
        spec = MILESTONE_BY_ID.get(comp.milestone_id)
        if not spec:
            continue
        tags = family_to_tags.get(spec.family.value, [])
        for tag in tags:
            lifetime[tag] = lifetime.get(tag, 0.0) + MILESTONE_WEIGHT
            if (current_day - comp.completed_day) <= RECENT_WINDOW_DAYS:
                recent[tag] = recent.get(tag, 0.0) + RECENT_MILESTONE_BONUS

    return {
        tag: (lifetime.get(tag, 0.0), recent.get(tag, 0.0))
        for tag in PROFILE_MILESTONE_FAMILIES
    }


def compute_career_profile(snap: SessionSnapshot) -> CareerProfile:
    """Derive a weighted, interpreted career profile from session truth.

    For each tag, computes:
      - lifetime_score: accumulated business history + milestone history
      - recent_score: session-truth base + recent milestone bonus
      - combined_score: weighted blend (tunable from content)
      - confidence: how strongly earned the tag is

    Returns a CareerProfile with primary, secondaries, and emerging tags.
    """
    from portlight.content.campaign import (
        CONFIDENCE_THRESHOLDS,
        EMERGING_MIN_RECENT,
        LIFETIME_WEIGHT,
        RECENT_WEIGHT,
        SECONDARY_THRESHOLD,
    )

    base_scores = _compute_base_scores(snap)
    ms_scores = _milestone_scores(snap)
    all_tags: list[CareerProfileTag] = []

    for tag, (base, evidence) in base_scores.items():
        ms_lifetime, ms_recent = ms_scores.get(tag, (0.0, 0.0))

        lifetime = base + ms_lifetime
        recent = base * 0.5 + ms_recent   # recent uses half-base + recent milestones
        combined = lifetime * LIFETIME_WEIGHT + recent * RECENT_WEIGHT

        # Determine confidence band
        confidence = ProfileConfidence.FORMING
        for level, threshold in CONFIDENCE_THRESHOLDS.items():
            if combined >= threshold:
                confidence = ProfileConfidence(level)
                break

        all_tags.append(CareerProfileTag(
            tag=tag,
            lifetime_score=round(lifetime, 1),
            recent_score=round(recent, 1),
            combined_score=round(combined, 1),
            confidence=confidence,
            evidence=evidence,
        ))

    # Sort by combined_score descending
    all_tags.sort(key=lambda t: t.combined_score, reverse=True)

    # Interpret into primary / secondaries / emerging
    primary = all_tags[0] if all_tags and all_tags[0].combined_score > 0 else None
    secondaries = [
        t for t in all_tags[1:3]
        if t.combined_score >= SECONDARY_THRESHOLD
    ]
    # Emerging: highest recent_score tag that isn't already primary,
    # if it has meaningful recent activity
    emerging = None
    for t in all_tags:
        if t is primary:
            continue
        if t in secondaries:
            continue
        if t.recent_score >= EMERGING_MIN_RECENT:
            emerging = t
            break

    return CareerProfile(
        primary=primary,
        secondaries=secondaries,
        emerging=emerging,
        all_tags=all_tags,
    )


def compute_career_profile_legacy(snap: SessionSnapshot) -> list[ProfileScore]:
    """Legacy profile scoring — flat ranked list for backward compat."""
    base = _compute_base_scores(snap)
    scores = [ProfileScore(tag, score, ev) for tag, (score, ev) in base.items()]
    scores.sort(key=lambda s: s.score, reverse=True)
    return scores


# ---------------------------------------------------------------------------
# Victory path evaluation — per-path evaluators
# ---------------------------------------------------------------------------

def _req(
    description: str,
    met: bool,
    detail: str = "",
    action: str = "",
    blocker: bool = False,
) -> VictoryRequirement:
    """Helper to build a requirement with met/missing/blocked status."""
    if met:
        status = RequirementStatus.MET
    elif blocker:
        status = RequirementStatus.BLOCKED
    else:
        status = RequirementStatus.MISSING
    return VictoryRequirement(description=description, status=status, detail=detail, action=action)


def _discreet_completions(snap: SessionSnapshot) -> int:
    """Count completed contracts in the luxury_discreet family."""
    from portlight.engine.contracts import ContractFamily
    count = 0
    for o in snap.board.completed:
        if o.outcome_type in ("completed", "completed_bonus"):
            # Use canonical family field when available, fall back to summary heuristic
            if o.family == ContractFamily.LUXURY_DISCREET:
                count += 1
            elif o.family is None and ("luxury" in o.summary.lower() or "discreet" in o.summary.lower()):
                count += 1
    return count


def _seizure_count(snap: SessionSnapshot) -> int:
    return sum(
        1 for i in snap.captain.standing.recent_incidents
        if "seized" in i.description.lower()
    )


def _evaluate_lawful_trade_house(snap: SessionSnapshot) -> VictoryPathStatus:
    from portlight.content.campaign import LAWFUL_THRESHOLDS as T, CANDIDATE_BOOSTS

    tier = _trust_tier(snap)
    rank = _trust_rank(tier)
    max_h = _max_heat(snap)
    contracts = _total_completed_contracts(snap)
    regions_15 = _regions_with_standing(snap, 15)
    lic_count = len(_active_licenses(snap))

    reqs = [
        _req(
            "Trusted commercial standing",
            rank >= T["trust_rank"],
            f"Currently: {tier}",
            f"Reach trusted trust tier (currently {tier})",
        ),
        _req(
            "High Reputation Commercial Charter",
            _has_license(snap, "high_rep_charter"),
            action="Acquire the High Reputation Commercial Charter",
        ),
        _req(
            "Regional breadth (2+ licenses or standing 15+ in 2 regions)",
            lic_count >= T["regional_licenses_or_standing"] or len(regions_15) >= T["regional_licenses_or_standing"],
            f"Licenses: {lic_count}, regions at 15+: {', '.join(regions_15) or 'none'}",
            f"Acquire {T['regional_licenses_or_standing'] - lic_count} more license(s) or build standing in another region"
            if lic_count < T["regional_licenses_or_standing"] and len(regions_15) < T["regional_licenses_or_standing"]
            else "",
        ),
        _req(
            f"{T['contracts_completed']}+ contracts completed",
            contracts >= T["contracts_completed"],
            f"Completed: {contracts}",
            f"Complete {T['contracts_completed'] - contracts} more contracts" if contracts < T["contracts_completed"] else "",
        ),
        _req(
            f"Max heat <= {T['max_heat_cap']}",
            max_h <= T["max_heat_cap"],
            f"Max heat: {max_h}",
            f"Reduce customs heat from {max_h} to {T['max_heat_cap']} or below",
            blocker=max_h > T["max_heat_cap"],
        ),
        _req(
            f"{T['silver_min']}+ silver",
            snap.captain.silver >= T["silver_min"],
            f"Silver: {snap.captain.silver}",
            f"Earn {T['silver_min'] - snap.captain.silver} more silver" if snap.captain.silver < T["silver_min"] else "",
        ),
    ]

    # Candidate strength
    boosts = CANDIDATE_BOOSTS["lawful_house"]
    base_ratio = sum(1 for r in reqs if r.met) / len(reqs) * 100
    strength = base_ratio
    strength += max(0, rank - 2) * boosts["trust_rank_bonus_per"]
    if len(_regions_with_standing(snap, 10)) >= 2:
        strength += boosts["standing_breadth_bonus"]
    if max_h <= 3:
        strength += boosts["low_heat_bonus"]
    strength += _seizure_count(snap) * boosts["seizure_penalty"]
    if max_h > T["max_heat_cap"]:
        strength += (max_h - T["max_heat_cap"]) * boosts["high_heat_penalty_per"]
    credit = snap.infra.credit
    if credit and credit.defaults > 0:
        strength += boosts["default_penalty"]

    return VictoryPathStatus(
        path_id="lawful_house",
        name="Lawful Trade House",
        requirements=reqs,
        candidate_strength=max(0.0, round(strength, 1)),
    )


def _evaluate_shadow_network(snap: SessionSnapshot) -> VictoryPathStatus:
    from portlight.content.campaign import SHADOW_THRESHOLDS as T, CANDIDATE_BOOSTS

    max_h = _max_heat(snap)
    profit = snap.ledger.net_profit
    trades = _total_trades(snap)
    discreet = _discreet_completions(snap)
    seizures = _seizure_count(snap)

    reqs = [
        _req(
            f"{T['discreet_completions']}+ discreet luxury completions",
            discreet >= T["discreet_completions"],
            f"Discreet completions: {discreet}",
            f"Complete {T['discreet_completions'] - discreet} more discreet luxury deliveries" if discreet < T["discreet_completions"] else "",
        ),
        _req(
            f"Operated under meaningful heat (>= {T['heat_floor']})",
            max_h >= T["heat_floor"],
            f"Max heat: {max_h}",
            f"Shadow commerce requires operating under customs pressure (heat {max_h}, need {T['heat_floor']}+)",
            blocker=max_h < T["heat_floor"] and profit > 1000,  # blocker if profitable but clean
        ),
        _req(
            f"Heat manageable (<= {T['heat_ceiling']})",
            max_h <= T["heat_ceiling"],
            f"Max heat: {max_h}",
            f"Reduce heat from {max_h} — network collapses above {T['heat_ceiling']}",
            blocker=max_h > T["heat_ceiling"],
        ),
        _req(
            f"Profitable under pressure (profit >= {T['profit_under_heat']})",
            profit >= T["profit_under_heat"] and max_h >= T["heat_floor"],
            f"Profit: {profit}, heat: {max_h}",
            "Build profitability while maintaining shadow operations",
        ),
        _req(
            f"{T['silver_min']}+ silver on hand",
            snap.captain.silver >= T["silver_min"],
            f"Silver: {snap.captain.silver}",
            f"Accumulate {T['silver_min'] - snap.captain.silver} more silver" if snap.captain.silver < T["silver_min"] else "",
        ),
        _req(
            f"Trade volume under heat ({T['trades_under_heat']}+ trades)",
            trades >= T["trades_under_heat"] and max_h >= T["heat_floor"],
            f"Trades: {trades}, max heat: {max_h}",
            "Complete more trades while operating under customs pressure",
        ),
    ]

    boosts = CANDIDATE_BOOSTS["shadow_network"]
    base_ratio = sum(1 for r in reqs if r.met) / len(reqs) * 100
    strength = base_ratio
    strength += discreet * boosts["discreet_bonus_per"]
    if profit >= T["profit_under_heat"] and max_h >= T["heat_floor"]:
        strength += boosts["heat_resilience_bonus"]
    if seizures > 0 and snap.captain.silver >= 200:
        strength += boosts["seizure_survival_bonus"]
    if max_h < 3:
        strength += boosts["zero_heat_penalty"]
    if snap.captain.silver < 100:
        strength += boosts["collapse_penalty"]

    return VictoryPathStatus(
        path_id="shadow_network",
        name="Shadow Network",
        requirements=reqs,
        candidate_strength=max(0.0, round(strength, 1)),
    )


def _evaluate_oceanic_reach(snap: SessionSnapshot) -> VictoryPathStatus:
    from portlight.content.campaign import OCEANIC_THRESHOLDS as T, CANDIDATE_BOOSTS

    ei_standing = snap.captain.standing.regional_standing.get("East Indies", 0)
    contracts = _total_completed_contracts(snap)
    ship = _ship_class(snap)
    has_ei_charter = _has_license(snap, "ei_access_charter")
    ei_broker = "East Indies" in _regions_with_broker(snap)
    ei_warehouse = "East Indies" in _regions_with_warehouse(snap)
    has_ei_foothold = ei_broker or ei_warehouse

    min_rank = {"sloop": 0, "cutter": 1, "brigantine": 2, "galleon": 3, "man_of_war": 4}
    ship_rank = min_rank.get(ship, 0)
    required_rank = min_rank.get(T["ship_class_min"], 2)
    ship_ok = ship_rank >= required_rank

    reqs = [
        _req(
            "East Indies Access Charter",
            has_ei_charter,
            action="Acquire the East Indies Access Charter",
        ),
        _req(
            "East Indies commercial foothold (broker or warehouse)",
            has_ei_foothold,
            f"EI broker: {'yes' if ei_broker else 'no'}, EI warehouse: {'yes' if ei_warehouse else 'no'}",
            "Open a broker office or warehouse in the East Indies",
        ),
        _req(
            f"East Indies standing >= {T['ei_standing']}",
            ei_standing >= T["ei_standing"],
            f"EI standing: {ei_standing}",
            f"Build East Indies standing from {ei_standing} to {T['ei_standing']}",
        ),
        _req(
            "Long-haul ship capability (Brigantine or Galleon)",
            ship_ok,
            f"Ship: {ship}",
            "Upgrade to a Brigantine or Galleon for long-haul routes",
        ),
        _req(
            f"{T['contracts_completed']}+ contracts completed",
            contracts >= T["contracts_completed"],
            f"Completed: {contracts}",
            f"Complete {T['contracts_completed'] - contracts} more contracts" if contracts < T["contracts_completed"] else "",
        ),
        _req(
            f"{T['silver_min']}+ silver",
            snap.captain.silver >= T["silver_min"],
            f"Silver: {snap.captain.silver}",
            f"Earn {T['silver_min'] - snap.captain.silver} more silver" if snap.captain.silver < T["silver_min"] else "",
        ),
    ]

    boosts = CANDIDATE_BOOSTS["oceanic_reach"]
    base_ratio = sum(1 for r in reqs if r.met) / len(reqs) * 100
    strength = base_ratio
    strength += ei_standing * boosts["ei_standing_bonus_per"]
    if ship == "galleon":
        strength += boosts["galleon_bonus"]
    if ei_broker and ei_warehouse:
        strength += boosts["ei_infra_bonus"]
    if ei_standing == 0 and not has_ei_charter:
        strength += boosts["local_only_penalty"]

    return VictoryPathStatus(
        path_id="oceanic_reach",
        name="Oceanic Reach",
        requirements=reqs,
        candidate_strength=max(0.0, round(strength, 1)),
    )


def _evaluate_commercial_empire(snap: SessionSnapshot) -> VictoryPathStatus:
    from portlight.content.campaign import EMPIRE_THRESHOLDS as T, CANDIDATE_BOOSTS

    tier = _trust_tier(snap)
    rank = _trust_rank(tier)
    infra_regions = _regions_with_warehouse(snap) | _regions_with_broker(snap)
    contracts = _total_completed_contracts(snap)
    lic_count = len(_active_licenses(snap))
    policies = _policies_purchased(snap)
    credit = snap.infra.credit
    credit_used = credit is not None and credit.total_borrowed > 0
    insurance_used = policies >= 1
    finance_ok = credit_used and insurance_used

    reqs = [
        _req(
            f"Infrastructure in {T['infra_regions']} regions",
            len(infra_regions) >= T["infra_regions"],
            f"Regions: {', '.join(sorted(infra_regions)) or 'none'}",
            f"Expand infrastructure to {T['infra_regions'] - len(infra_regions)} more region(s)"
            if len(infra_regions) < T["infra_regions"] else "",
        ),
        _req(
            "Reliable+ trust",
            rank >= T["trust_rank"],
            f"Trust: {tier}",
            f"Build trust to reliable tier (currently {tier})",
        ),
        _req(
            "Insurance and credit both used successfully",
            finance_ok,
            f"Insurance: {'yes' if insurance_used else 'no'}, Credit: {'yes' if credit_used else 'no'}",
            ("Use insurance" if not insurance_used else "") +
            (" and " if not insurance_used and not credit_used else "") +
            ("Draw on credit" if not credit_used else ""),
        ),
        _req(
            f"{T['contracts_completed']}+ contracts completed",
            contracts >= T["contracts_completed"],
            f"Completed: {contracts}",
            f"Complete {T['contracts_completed'] - contracts} more contracts" if contracts < T["contracts_completed"] else "",
        ),
        _req(
            f"{T['silver_min']}+ silver",
            snap.captain.silver >= T["silver_min"],
            f"Silver: {snap.captain.silver}",
            f"Earn {T['silver_min'] - snap.captain.silver} more silver" if snap.captain.silver < T["silver_min"] else "",
        ),
        _req(
            f"{T['licenses_min']}+ active licenses",
            lic_count >= T["licenses_min"],
            f"Active: {lic_count}",
            f"Acquire {T['licenses_min'] - lic_count} more license(s)" if lic_count < T["licenses_min"] else "",
        ),
    ]

    boosts = CANDIDATE_BOOSTS["commercial_empire"]
    base_ratio = sum(1 for r in reqs if r.met) / len(reqs) * 100
    strength = base_ratio
    strength += len(infra_regions) * boosts["infra_breadth_bonus_per"]
    if finance_ok:
        strength += boosts["finance_maturity_bonus"]
    if contracts >= 10:
        strength += boosts["contract_breadth_bonus"]
    if len(infra_regions) <= 1:
        strength += boosts["narrow_penalty"]
    if credit and credit.defaults > 0:
        strength += boosts["default_penalty"]

    return VictoryPathStatus(
        path_id="commercial_empire",
        name="Commercial Empire",
        requirements=reqs,
        candidate_strength=max(0.0, round(strength, 1)),
    )


def compute_victory_progress(snap: SessionSnapshot) -> list[VictoryPathStatus]:
    """Evaluate all victory paths with diagnostics: met/missing/blocked,
    candidate strength, and actionable missing-requirement text.

    If a path was previously completed (in campaign state), its completion_day
    and completion_summary are restored from the record.

    Returns paths sorted by candidate_strength descending.
    """
    from portlight.content.campaign import COMPLETION_SUMMARIES

    paths = [
        _evaluate_lawful_trade_house(snap),
        _evaluate_shadow_network(snap),
        _evaluate_oceanic_reach(snap),
        _evaluate_commercial_empire(snap),
    ]

    # Attach completion records from campaign state
    completed_map = {vc.path_id: vc for vc in snap.campaign.completed_paths}
    for path in paths:
        vc = completed_map.get(path.path_id)
        if vc:
            path.completion_day = vc.completion_day
            path.completion_summary = vc.summary

        # For newly-complete paths not yet recorded, attach summary from content
        if path.is_complete and not path.completion_summary:
            path.completion_summary = COMPLETION_SUMMARIES.get(path.path_id, "")

    paths.sort(key=lambda p: p.candidate_strength, reverse=True)
    return paths


def evaluate_victory_closure(snap: SessionSnapshot) -> list[VictoryCompletion]:
    """Check if any victory path just completed. Returns newly completed paths.

    Only returns paths not already in snap.campaign.completed_paths.
    """
    from portlight.content.campaign import COMPLETION_SUMMARIES

    already = {vc.path_id for vc in snap.campaign.completed_paths}
    is_first = len(already) == 0
    newly: list[VictoryCompletion] = []

    paths = [
        _evaluate_lawful_trade_house(snap),
        _evaluate_shadow_network(snap),
        _evaluate_oceanic_reach(snap),
        _evaluate_commercial_empire(snap),
    ]

    for path in paths:
        if path.path_id in already:
            continue
        if path.is_complete:
            summary = COMPLETION_SUMMARIES.get(path.path_id, "")
            vc = VictoryCompletion(
                path_id=path.path_id,
                completion_day=snap.world.day,
                summary=summary,
                is_first=is_first and len(newly) == 0,
            )
            newly.append(vc)

    return newly
