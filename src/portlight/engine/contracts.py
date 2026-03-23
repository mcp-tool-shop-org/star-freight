"""Contract engine — multi-voyage business arcs on top of the living economy.

Contracts never replace the economy. They send the player back into market
reading, cargo allocation, route choice, timing, and risk management.

Lifecycle:
  - generate_offers: creates offers from world state at port arrival
  - accept_offer: commits player to an obligation
  - check_delivery: observes real cargo sales and credits progress
  - abandon_contract: player gives up (reputation cost)
  - tick_contracts: daily deadline checks, expiry resolution
  - complete_contract: pays out, mutates reputation

All reputation mutations flow through engine/reputation.py canonical seam.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from portlight.engine.models import Captain, Port, ReputationState, WorldState


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ContractFamily(str, Enum):
    PROCUREMENT = "procurement"
    SHORTAGE = "shortage"
    LUXURY_DISCREET = "luxury_discreet"
    RETURN_FREIGHT = "return_freight"
    CIRCUIT = "circuit"
    REPUTATION_CHARTER = "reputation_charter"
    SMUGGLING = "smuggling"


class ContractStatus(str, Enum):
    AVAILABLE = "available"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    ABANDONED = "abandoned"


# ---------------------------------------------------------------------------
# Contract template (reusable pattern)
# ---------------------------------------------------------------------------

@dataclass
class ContractTemplate:
    """Reusable contract pattern. Content data, not runtime state."""
    id: str
    family: ContractFamily
    title_pattern: str                     # e.g. "Grain for {destination}"
    description: str
    goods_pool: list[str]                  # eligible good_ids
    quantity_min: int
    quantity_max: int
    reward_per_unit: int                   # silver per unit delivered
    bonus_reward: int = 0                  # extra for early/full delivery
    deadline_days: int = 30                # base deadline
    trust_requirement: str = "unproven"    # min trust tier
    standing_requirement: int = 0          # min regional standing
    heat_ceiling: int | None = None        # max heat to see this offer
    inspection_modifier: float = 0.0       # added inspection risk during this contract
    source_region: str | None = None       # cargo must come from this region
    source_port: str | None = None         # cargo must come from this port
    destination_regions: list[str] = field(default_factory=list)  # valid dest regions
    captain_bias: list[str] = field(default_factory=list)  # captain types that see this more
    tags: list[str] = field(default_factory=list)
    cultural_flavor: str = ""              # atmospheric text about cultural significance


# ---------------------------------------------------------------------------
# Contract offer (generated, live in the world)
# ---------------------------------------------------------------------------

@dataclass
class ContractOffer:
    """A live offer on the board at a port."""
    id: str
    template_id: str
    family: ContractFamily
    title: str
    description: str
    issuer_port_id: str
    destination_port_id: str
    good_id: str
    quantity: int
    created_day: int
    deadline_day: int
    reward_silver: int
    bonus_reward: int
    required_trust_tier: str
    required_standing: int
    heat_ceiling: int | None
    inspection_modifier: float
    source_region: str | None
    source_port: str | None
    offer_reason: str                      # why this offer exists
    tags: list[str] = field(default_factory=list)
    acceptance_window: int = 10            # days until offer expires if not accepted


# ---------------------------------------------------------------------------
# Active contract (accepted obligation)
# ---------------------------------------------------------------------------

@dataclass
class ActiveContract:
    """An accepted contract obligation."""
    offer_id: str
    template_id: str
    family: ContractFamily
    title: str
    accepted_day: int
    deadline_day: int
    destination_port_id: str
    good_id: str
    required_quantity: int
    delivered_quantity: int = 0
    reward_silver: int = 0
    bonus_reward: int = 0
    source_region: str | None = None
    source_port: str | None = None
    inspection_modifier: float = 0.0
    status: ContractStatus = ContractStatus.ACCEPTED


# ---------------------------------------------------------------------------
# Contract outcome (resolution truth)
# ---------------------------------------------------------------------------

@dataclass
class ContractOutcome:
    """Resolution of a completed/failed contract."""
    contract_id: str
    outcome_type: str              # completed, completed_bonus, expired, abandoned
    silver_delta: int
    trust_delta: int
    standing_delta: int
    heat_delta: int
    completion_day: int
    summary: str
    family: ContractFamily | None = None  # canonical contract family for victory path evaluation


# ---------------------------------------------------------------------------
# Contract board (session state)
# ---------------------------------------------------------------------------

@dataclass
class ContractBoard:
    """All contract state for a game session."""
    offers: list[ContractOffer] = field(default_factory=list)
    active: list[ActiveContract] = field(default_factory=list)
    completed: list[ContractOutcome] = field(default_factory=list)
    last_refresh_day: int = 0
    max_offers: int = 5                    # board slots


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def _offer_id(template_id: str, port_id: str, day: int, seq: int) -> str:
    raw = f"{template_id}:{port_id}:{day}:{seq}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


_SHIP_CLASS_RANK = {"sloop": 0, "cutter": 1, "brigantine": 2, "galleon": 3, "man_of_war": 4}


def _pick_destination(
    template: ContractTemplate,
    issuer_port: "Port",
    ports: dict[str, "Port"],
    routes: list,
    good_id: str | None = None,
    rng: random.Random | None = None,
    player_ship_rank: int | None = None,
) -> "Port | None":
    """Pick a valid destination port for a contract.

    If *good_id* is provided, only ports whose market includes that good are
    considered.  This prevents generating contracts to deliver goods a port
    doesn't trade.

    If *player_ship_rank* is provided, only destinations reachable by routes
    whose min_ship_class the player can handle are considered.
    """
    _rng = rng or random.Random()
    candidates = []
    for pid, port in ports.items():
        if pid == issuer_port.id:
            continue
        if template.destination_regions and port.region not in template.destination_regions:
            continue
        # Destination must trade the contract good
        if good_id and not any(slot.good_id == good_id for slot in port.market):
            continue
        # Check route exists (and player can sail it)
        def _route_accessible(r) -> bool:
            if player_ship_rank is not None:
                route_rank = _SHIP_CLASS_RANK.get(getattr(r, "min_ship_class", "sloop"), 0)
                if player_ship_rank < route_rank:
                    return False
            return True

        has_route = any(
            ((r.port_a == issuer_port.id and r.port_b == pid) or
             (r.port_a == pid and r.port_b == issuer_port.id))
            and _route_accessible(r)
            for r in routes
        )
        # Also accept multi-hop (destination reachable from somewhere connected)
        # Skip multi-hop when ship filtering is active — a destination may have
        # sloop routes locally but be unreachable from the player's region.
        if not has_route and player_ship_rank is None:
            has_route = any(
                (r.port_a == pid or r.port_b == pid) and _route_accessible(r)
                for r in routes
            )
        if has_route:
            candidates.append(port)
    return _rng.choice(candidates) if candidates else None


def _compute_offer_reason(
    template: ContractTemplate,
    issuer_port: "Port",
    dest_port: "Port",
    good_id: str,
) -> str:
    """Generate a human-readable reason for this offer."""
    match template.family:
        case ContractFamily.PROCUREMENT:
            return f"{dest_port.name} needs {good_id} delivered"
        case ContractFamily.SHORTAGE:
            return f"Shortage at {dest_port.name} — urgent demand for {good_id}"
        case ContractFamily.LUXURY_DISCREET:
            return f"Discreet buyer at {dest_port.name} wants {good_id}"
        case ContractFamily.RETURN_FREIGHT:
            return f"{issuer_port.name} has {good_id} that needs to reach {dest_port.name}"
        case ContractFamily.CIRCUIT:
            return f"Trade circuit opportunity: {good_id} to {dest_port.name}"
        case ContractFamily.REPUTATION_CHARTER:
            return f"Premium charter: deliver {good_id} to {dest_port.name}"
        case _:
            return f"Deliver {good_id} to {dest_port.name}"


def generate_offers(
    templates: list[ContractTemplate],
    world: "WorldState",
    port: "Port",
    rep: "ReputationState",
    captain_type: str,
    rng: random.Random,
    player_ship_rank: int | None = None,
    max_offers: int = 5,
    board_effects: dict[str, float] | None = None,
) -> list[ContractOffer]:
    """Generate contract offers from world state at a port.

    Reads scarcity, trust, heat, standing, captain type to shape the board.
    board_effects from compute_board_effects() modifies weights:
      - board_quality_bonus: multiplier on all premium template weights
      - premium_offer_mult: extra multiplier on high-reward templates
      - lawful_board_mult: multiplier on lawful family weights (procurement, charter)
      - luxury_access: if > 0, luxury_discreet templates get weight boost
    """
    from portlight.engine.reputation import get_trust_tier

    trust_tier = get_trust_tier(rep)
    trust_rank = {"unproven": 0, "new": 1, "credible": 2, "reliable": 3, "trusted": 4}
    player_trust = trust_rank.get(trust_tier, 0)
    region_standing = rep.regional_standing.get(port.region, 0)
    region_heat = rep.customs_heat.get(port.region, 0)

    # Board effects defaults
    bq = board_effects or {}
    quality_mult = bq.get("board_quality_bonus", 1.0)
    premium_mult = bq.get("premium_offer_mult", 1.0)
    lawful_mult = bq.get("lawful_board_mult", 1.0)
    luxury_access = bq.get("luxury_access", 0.0)

    eligible = []
    for t in templates:
        # Trust gate
        required_trust = trust_rank.get(t.trust_requirement, 0)
        if player_trust < required_trust:
            continue
        # Standing gate (requirement=0 means no gate — allows negative standing)
        if t.standing_requirement > 0 and region_standing < t.standing_requirement:
            continue
        # Heat ceiling
        if t.heat_ceiling is not None and region_heat > t.heat_ceiling:
            continue
        # Captain bias (weighted, not gated)
        weight = 2.0 if captain_type in t.captain_bias else 1.0
        # Shortage templates need actual scarcity somewhere
        if t.family == ContractFamily.SHORTAGE:
            has_scarcity = False
            for p in world.ports.values():
                for slot in p.market:
                    if slot.good_id in t.goods_pool:
                        if slot.stock_current < slot.stock_target * 0.5:
                            has_scarcity = True
                            break
                if has_scarcity:
                    break
            if not has_scarcity:
                weight *= 0.2  # still possible but much less likely

        # --- Infrastructure board effects ---
        # Lawful families benefit from broker presence and charters
        if t.family in (ContractFamily.PROCUREMENT, ContractFamily.REPUTATION_CHARTER):
            weight *= lawful_mult
        # Premium templates (high trust/standing req) benefit from board quality
        if required_trust >= 2 or t.standing_requirement >= 10:
            weight *= quality_mult * premium_mult
        # Luxury discreet benefits from luxury access license
        if t.family == ContractFamily.LUXURY_DISCREET and luxury_access > 0:
            weight *= 1.5  # license makes luxury contracts notably more common

        eligible.append((t, weight))

    if not eligible:
        return []

    # Weighted selection without replacement
    offers = []
    used_templates = set()
    attempts = 0
    while len(offers) < max_offers and attempts < max_offers * 3:
        attempts += 1
        weights = [w for t, w in eligible if t.id not in used_templates]
        choices = [t for t, w in eligible if t.id not in used_templates]
        if not choices:
            break

        template = rng.choices(choices, weights=weights, k=1)[0]

        # Pick good
        good_id = rng.choice(template.goods_pool)

        # Pick destination (must trade the contract good)
        dest = _pick_destination(template, port, world.ports, world.routes, good_id=good_id, rng=rng, player_ship_rank=player_ship_rank)
        if dest is None:
            # Try another good from the pool before giving up on this template
            alt_goods = [g for g in template.goods_pool if g != good_id]
            rng.shuffle(alt_goods)
            for alt in alt_goods:
                dest = _pick_destination(template, port, world.ports, world.routes, good_id=alt, rng=rng, player_ship_rank=player_ship_rank)
                if dest is not None:
                    good_id = alt
                    break
            if dest is None:
                used_templates.add(template.id)
                continue

        used_templates.add(template.id)

        # Compute quantity
        qty = rng.randint(template.quantity_min, template.quantity_max)

        # Compute deadline (base + distance buffer)
        deadline = world.day + template.deadline_days

        # Compute reward
        reward = qty * template.reward_per_unit

        reason = _compute_offer_reason(template, port, dest, good_id)

        offer = ContractOffer(
            id=_offer_id(template.id, port.id, world.day, len(offers)),
            template_id=template.id,
            family=template.family,
            title=template.title_pattern.format(
                good=good_id, destination=dest.name, source=port.name,
            ),
            description=template.description,
            issuer_port_id=port.id,
            destination_port_id=dest.id,
            good_id=good_id,
            quantity=qty,
            created_day=world.day,
            deadline_day=deadline,
            reward_silver=reward,
            bonus_reward=template.bonus_reward,
            required_trust_tier=template.trust_requirement,
            required_standing=template.standing_requirement,
            heat_ceiling=template.heat_ceiling,
            inspection_modifier=template.inspection_modifier,
            source_region=template.source_region,
            source_port=template.source_port,
            offer_reason=reason,
            tags=list(template.tags),
        )
        offers.append(offer)

    # Fallback: if no offers were generated despite eligible templates, retry
    # with relaxed destination regions (drop region constraint for one offer)
    if not offers and eligible:
        for t, _w in eligible:
            if t.id in used_templates:
                continue
            for g in t.goods_pool:
                dest = _pick_destination(
                    t, port, world.ports, world.routes, good_id=g, rng=rng,
                    player_ship_rank=player_ship_rank,
                )
                if dest is None:
                    # Try without good filter — any reachable port
                    dest = _pick_destination(
                        t, port, world.ports, world.routes, good_id=None, rng=rng,
                        player_ship_rank=player_ship_rank,
                    )
                if dest is not None:
                    qty = rng.randint(t.quantity_min, t.quantity_max)
                    reward = qty * t.reward_per_unit
                    reason = _compute_offer_reason(t, port, dest, g)
                    offers.append(ContractOffer(
                        id=_offer_id(t.id, port.id, world.day, 0),
                        template_id=t.id,
                        family=t.family,
                        title=t.title_pattern.format(
                            good=g, destination=dest.name, source=port.name,
                        ),
                        description=t.description,
                        issuer_port_id=port.id,
                        destination_port_id=dest.id,
                        good_id=g,
                        quantity=qty,
                        created_day=world.day,
                        deadline_day=world.day + t.deadline_days,
                        reward_silver=reward,
                        bonus_reward=t.bonus_reward,
                        required_trust_tier=t.trust_requirement,
                        required_standing=t.standing_requirement,
                        heat_ceiling=t.heat_ceiling,
                        inspection_modifier=t.inspection_modifier,
                        source_region=t.source_region,
                        source_port=t.source_port,
                        offer_reason=reason,
                        tags=list(t.tags),
                    ))
                    break
            if offers:
                break

    return offers


# ---------------------------------------------------------------------------
# Acceptance
# ---------------------------------------------------------------------------

def accept_offer(
    board: ContractBoard,
    offer_id: str,
    day: int,
) -> ActiveContract | str:
    """Accept an offer. Returns ActiveContract on success, error string on failure."""
    offer = next((o for o in board.offers if o.id == offer_id), None)
    if offer is None:
        return "Offer not found"
    if len(board.active) >= 3:
        return "Too many active contracts (max 3)"

    contract = ActiveContract(
        offer_id=offer.id,
        template_id=offer.template_id,
        family=offer.family,
        title=offer.title,
        accepted_day=day,
        deadline_day=offer.deadline_day,
        destination_port_id=offer.destination_port_id,
        good_id=offer.good_id,
        required_quantity=offer.quantity,
        reward_silver=offer.reward_silver,
        bonus_reward=offer.bonus_reward,
        source_region=offer.source_region,
        source_port=offer.source_port,
        inspection_modifier=offer.inspection_modifier,
    )
    board.active.append(contract)
    board.offers = [o for o in board.offers if o.id != offer_id]
    return contract


# ---------------------------------------------------------------------------
# Delivery (checks real cargo sales)
# ---------------------------------------------------------------------------

def check_delivery(
    board: ContractBoard,
    port_id: str,
    good_id: str,
    quantity: int,
    source_port: str,
    source_region: str,
) -> list[tuple[ActiveContract, int]]:
    """Check if a sale at port fulfills any active contracts.

    Returns list of (contract, credited_qty) pairs.
    Only credits cargo that matches provenance requirements.
    """
    credited = []
    for contract in board.active:
        if contract.status != ContractStatus.ACCEPTED:
            continue
        if contract.destination_port_id != port_id:
            continue
        if contract.good_id != good_id:
            continue
        remaining = contract.required_quantity - contract.delivered_quantity
        if remaining <= 0:
            continue

        # Source validation
        if contract.source_region and source_region != contract.source_region:
            continue
        if contract.source_port and source_port != contract.source_port:
            continue

        credit = min(quantity, remaining)
        contract.delivered_quantity += credit
        quantity -= credit
        credited.append((contract, credit))

        if quantity <= 0:
            break

    return credited


# ---------------------------------------------------------------------------
# Completion / failure
# ---------------------------------------------------------------------------

def resolve_completed(
    board: ContractBoard,
    day: int,
) -> list[ContractOutcome]:
    """Check for completed contracts and resolve them."""
    outcomes = []
    still_active = []

    for contract in board.active:
        if contract.status != ContractStatus.ACCEPTED:
            still_active.append(contract)
            continue

        if contract.delivered_quantity >= contract.required_quantity:
            # Completed!
            is_early = day < contract.deadline_day - 3
            bonus = contract.bonus_reward if is_early and contract.bonus_reward > 0 else 0
            total_reward = contract.reward_silver + bonus

            outcome_type = "completed_bonus" if bonus > 0 else "completed"
            outcome = ContractOutcome(
                contract_id=contract.offer_id,
                outcome_type=outcome_type,
                silver_delta=total_reward,
                trust_delta=2 if bonus > 0 else 1,
                standing_delta=1,
                heat_delta=-1,  # clean delivery reduces heat
                completion_day=day,
                summary=f"Delivered {contract.delivered_quantity} {contract.good_id} to {contract.destination_port_id}"
                + (f" (early bonus: +{bonus} silver)" if bonus > 0 else ""),
                family=contract.family,
            )
            contract.status = ContractStatus.COMPLETED
            outcomes.append(outcome)
            board.completed.append(outcome)
        else:
            still_active.append(contract)

    board.active = still_active
    return outcomes


def tick_contracts(
    board: ContractBoard,
    day: int,
    captain: "Captain | None" = None,
) -> list[ContractOutcome]:
    """Daily tick: expire overdue contracts, remove stale offers."""
    outcomes = []
    still_active = []

    for contract in board.active:
        if contract.status != ContractStatus.ACCEPTED:
            still_active.append(contract)
            continue

        if day > contract.deadline_day:
            # Expired
            partial = contract.delivered_quantity > 0
            if partial:
                # Partial payout
                partial_pct = contract.delivered_quantity / contract.required_quantity
                payout = round(contract.reward_silver * partial_pct * 0.5)  # 50% of pro-rata
                outcome = ContractOutcome(
                    contract_id=contract.offer_id,
                    outcome_type="expired",
                    silver_delta=payout,
                    trust_delta=-2,
                    standing_delta=-1,
                    heat_delta=1,
                    completion_day=day,
                    summary=f"Contract expired: delivered {contract.delivered_quantity}/{contract.required_quantity} {contract.good_id} (partial payout: {payout} silver)",
                    family=contract.family,
                )
            else:
                outcome = ContractOutcome(
                    contract_id=contract.offer_id,
                    outcome_type="expired",
                    silver_delta=0,
                    trust_delta=-3,
                    standing_delta=-2,
                    heat_delta=2,
                    completion_day=day,
                    summary=f"Contract defaulted: failed to deliver {contract.good_id} to {contract.destination_port_id}",
                    family=contract.family,
                )
            contract.status = ContractStatus.EXPIRED
            outcomes.append(outcome)
            board.completed.append(outcome)
            # Record breach on captain
            if captain is not None:
                _record_breach(captain, contract.offer_id, day, contract.destination_port_id, contract.family)
        else:
            still_active.append(contract)

    board.active = still_active

    # Remove expired offers
    board.offers = [o for o in board.offers if day <= o.created_day + o.acceptance_window]

    return outcomes


def abandon_contract(
    board: ContractBoard,
    offer_id: str,
    day: int,
    captain: "Captain | None" = None,
) -> ContractOutcome | str:
    """Player abandons a contract. Reputation cost + breach record."""
    contract = next((c for c in board.active if c.offer_id == offer_id), None)
    if contract is None:
        return "No active contract with that ID"

    outcome = ContractOutcome(
        contract_id=contract.offer_id,
        outcome_type="abandoned",
        silver_delta=0,
        trust_delta=-2,
        standing_delta=-1,
        heat_delta=1,
        completion_day=day,
        summary=f"Abandoned contract: {contract.title}",
        family=contract.family,
    )
    contract.status = ContractStatus.ABANDONED
    board.active = [c for c in board.active if c.offer_id != offer_id]
    board.completed.append(outcome)
    # Record breach on captain
    if captain is not None:
        _record_breach(captain, contract.offer_id, day, contract.destination_port_id, contract.family)
    return outcome


# ---------------------------------------------------------------------------
# Breach tracking
# ---------------------------------------------------------------------------

def _record_breach(
    captain: "Captain",
    contract_id: str,
    day: int,
    port_id: str,
    family: str,
) -> None:
    """Record a contract breach and escalate wanted level."""
    captain.breach_records.append({
        "contract_id": contract_id,
        "day": day,
        "port_id": port_id,
        "family": family,
    })
    # Escalate wanted level based on breach count
    count = len(captain.breach_records)
    if count >= 5:
        captain.wanted_level = max(captain.wanted_level, 3)  # hunted
    elif count >= 3:
        captain.wanted_level = max(captain.wanted_level, 2)  # wanted
    elif count >= 2:
        captain.wanted_level = max(captain.wanted_level, 1)  # watched


def get_breach_count_for_family(captain: "Captain", family: str) -> int:
    """Count breaches for a specific contract family."""
    return sum(1 for b in captain.breach_records if b.get("family") == family)
