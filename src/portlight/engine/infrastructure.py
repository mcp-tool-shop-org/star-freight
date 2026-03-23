"""Infrastructure engine — commercial assets that change how trade is executed.

Warehouses, broker offices, licenses, insurance, credit all live here.
3D-1 ships warehouses. Later sub-packets add the rest.

Design law:
  - Every asset must change trade timing, scale, or access — not just buff a number.
  - Provenance is preserved through all storage operations.
  - Upkeep is real. Assets that aren't maintained decay or close.
  - Physical presence required: deposit/withdraw only when docked at the port.

Warehouse lifecycle:
  - lease_warehouse(state, port_id, tier) -> opens a lease
  - deposit_cargo(state, port_id, captain, good_id, qty) -> ship -> warehouse
  - withdraw_cargo(state, port_id, captain, good_id, qty) -> warehouse -> ship
  - tick_infrastructure(state, day) -> deducts upkeep, closes defaulted leases
  - warehouse_inventory(state, port_id) -> read-only view of stored lots
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from portlight.engine.models import Captain, ReputationState


# ---------------------------------------------------------------------------
# Warehouse tier
# ---------------------------------------------------------------------------

class WarehouseTier(str, Enum):
    DEPOT = "depot"                    # small, cheap, starter
    REGIONAL = "regional"              # mid-tier, real staging
    COMMERCIAL = "commercial"          # large, expensive, full power


@dataclass
class WarehouseTierSpec:
    """Static definition of a warehouse tier."""
    tier: WarehouseTier
    name: str
    capacity: int                      # max cargo weight units
    lease_cost: int                    # one-time silver to open
    upkeep_per_day: int                # daily silver cost
    description: str


# ---------------------------------------------------------------------------
# Stored lot (cargo in warehouse, provenance preserved)
# ---------------------------------------------------------------------------

@dataclass
class StoredLot:
    """A single lot of goods in warehouse storage."""
    good_id: str
    quantity: int
    acquired_port: str
    acquired_region: str
    acquired_day: int
    deposited_day: int = 0


# ---------------------------------------------------------------------------
# Warehouse lease (live state)
# ---------------------------------------------------------------------------

@dataclass
class WarehouseLease:
    """An active warehouse at a specific port."""
    id: str
    port_id: str
    tier: WarehouseTier
    capacity: int
    lease_cost: int
    upkeep_per_day: int
    inventory: list[StoredLot] = field(default_factory=list)
    opened_day: int = 0
    upkeep_paid_through: int = 0       # last day upkeep was covered
    active: bool = True

    @property
    def used_capacity(self) -> int:
        return sum(lot.quantity for lot in self.inventory)

    @property
    def free_capacity(self) -> int:
        return max(0, self.capacity - self.used_capacity)


# ---------------------------------------------------------------------------
# Broker office
# ---------------------------------------------------------------------------

class BrokerTier(str, Enum):
    NONE = "none"
    LOCAL = "local"                    # broker contact — foothold
    ESTABLISHED = "established"        # broker house — serious presence


@dataclass
class BrokerOfficeSpec:
    """Static definition of a broker office tier."""
    tier: BrokerTier
    name: str
    purchase_cost: int
    upkeep_per_day: int
    board_quality_bonus: float         # multiplier on premium offer weight (1.5 = 50% more)
    market_signal_bonus: float         # improves shortage/opportunity visibility
    trade_term_modifier: float         # mild spread improvement (0.95 = 5% tighter)
    description: str


@dataclass
class BrokerOffice:
    """A regional broker office — intelligence and commercial quality."""
    region: str
    tier: BrokerTier = BrokerTier.NONE
    opened_day: int = 0
    upkeep_paid_through: int = 0
    active: bool = True


# ---------------------------------------------------------------------------
# License / charter
# ---------------------------------------------------------------------------

@dataclass
class LicenseSpec:
    """Static definition of a purchasable license."""
    id: str
    name: str
    description: str
    region_scope: str | None           # None = global
    purchase_cost: int
    upkeep_per_day: int
    required_trust_tier: str           # min trust to purchase
    required_standing: int             # min regional standing (in scope region)
    required_heat_max: int | None      # max heat allowed (None = no ceiling)
    required_broker_tier: BrokerTier | None  # must have this broker tier in scope region
    effects: dict[str, float] = field(default_factory=dict)
    # Effect keys: "contract_family_unlock", "customs_mult", "premium_offer_mult",
    #              "lawful_board_mult", "luxury_access"


@dataclass
class OwnedLicense:
    """A license the player has purchased."""
    license_id: str
    purchased_day: int
    upkeep_paid_through: int = 0
    active: bool = True


# ---------------------------------------------------------------------------
# Infrastructure state (session-level)
# ---------------------------------------------------------------------------

@dataclass
class InfrastructureState:
    """All commercial infrastructure owned by the player."""
    warehouses: list[WarehouseLease] = field(default_factory=list)
    brokers: list[BrokerOffice] = field(default_factory=list)
    licenses: list[OwnedLicense] = field(default_factory=list)
    policies: list["ActivePolicy"] = field(default_factory=list)
    claims: list["InsuranceClaim"] = field(default_factory=list)
    credit: CreditState | None = None


# ---------------------------------------------------------------------------
# Warehouse ID
# ---------------------------------------------------------------------------

def _warehouse_id(port_id: str, tier: str, day: int) -> str:
    raw = f"wh:{port_id}:{tier}:{day}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Lease
# ---------------------------------------------------------------------------

def lease_warehouse(
    state: InfrastructureState,
    captain: "Captain",
    port_id: str,
    tier_spec: WarehouseTierSpec,
    day: int,
) -> WarehouseLease | str:
    """Open a warehouse lease at a port. Returns lease or error string."""
    # Check for existing active warehouse at this port
    existing = next(
        (w for w in state.warehouses if w.port_id == port_id and w.active),
        None,
    )
    if existing:
        if existing.tier == tier_spec.tier:
            return f"Already have a {tier_spec.name} at this port"
        # Upgrading: close old, open new (keep inventory if it fits)
        old_inventory = list(existing.inventory)
        existing.active = False
    else:
        old_inventory = []

    # Cost check
    if tier_spec.lease_cost > captain.silver:
        return f"Need {tier_spec.lease_cost} silver to lease {tier_spec.name}, have {captain.silver}"

    captain.silver -= tier_spec.lease_cost

    lease = WarehouseLease(
        id=_warehouse_id(port_id, tier_spec.tier.value, day),
        port_id=port_id,
        tier=tier_spec.tier,
        capacity=tier_spec.capacity,
        lease_cost=tier_spec.lease_cost,
        upkeep_per_day=tier_spec.upkeep_per_day,
        opened_day=day,
        upkeep_paid_through=day,
        active=True,
    )

    # Transfer old inventory — refuse if downgrade would lose goods
    old_total = sum(lot.quantity for lot in old_inventory)
    if old_total > lease.capacity:
        # Undo: reactivate old warehouse, refund
        if existing:
            existing.active = True
        captain.silver += tier_spec.lease_cost
        return (
            f"Cannot downgrade: {old_total} units in storage exceeds "
            f"{tier_spec.name} capacity ({lease.capacity}). "
            f"Withdraw goods first."
        )
    for lot in old_inventory:
        lease.inventory.append(lot)

    state.warehouses.append(lease)
    return lease


# ---------------------------------------------------------------------------
# Deposit
# ---------------------------------------------------------------------------

def deposit_cargo(
    state: InfrastructureState,
    port_id: str,
    captain: "Captain",
    good_id: str,
    quantity: int,
    day: int,
) -> int | str:
    """Move cargo from ship to warehouse. Returns quantity deposited or error."""
    warehouse = next(
        (w for w in state.warehouses if w.port_id == port_id and w.active),
        None,
    )
    if warehouse is None:
        return "No warehouse at this port"
    if quantity <= 0:
        return "Quantity must be positive"

    # Find cargo in ship hold
    cargo_item = next(
        (c for c in captain.cargo if c.good_id == good_id),
        None,
    )
    if cargo_item is None or cargo_item.quantity < quantity:
        have = cargo_item.quantity if cargo_item else 0
        return f"Only have {have} units of {good_id} in hold"

    # Check warehouse capacity
    if quantity > warehouse.free_capacity:
        return f"Warehouse only has {warehouse.free_capacity} units of space"

    # Execute transfer: ship -> warehouse (preserve provenance)
    deposit_qty = quantity
    cargo_item.quantity -= deposit_qty
    if cargo_item.quantity == 0:
        captain.cargo.remove(cargo_item)

    # Merge into existing lot with same provenance, or create new
    merged = False
    for lot in warehouse.inventory:
        if (lot.good_id == good_id and
            lot.acquired_port == cargo_item.acquired_port and
            lot.acquired_region == cargo_item.acquired_region):
            lot.quantity += deposit_qty
            merged = True
            break

    if not merged:
        warehouse.inventory.append(StoredLot(
            good_id=good_id,
            quantity=deposit_qty,
            acquired_port=cargo_item.acquired_port,
            acquired_region=cargo_item.acquired_region,
            acquired_day=cargo_item.acquired_day,
            deposited_day=day,
        ))

    return deposit_qty


# ---------------------------------------------------------------------------
# Withdraw
# ---------------------------------------------------------------------------

def withdraw_cargo(
    state: InfrastructureState,
    port_id: str,
    captain: "Captain",
    good_id: str,
    quantity: int,
    source_port: str | None = None,
) -> int | str:
    """Move cargo from warehouse to ship. Returns quantity withdrawn or error.

    If source_port is specified, only withdraw from lots with that provenance.
    """
    from portlight.engine.models import CargoItem

    warehouse = next(
        (w for w in state.warehouses if w.port_id == port_id and w.active),
        None,
    )
    if warehouse is None:
        return "No warehouse at this port"
    if quantity <= 0:
        return "Quantity must be positive"

    # Check ship capacity
    ship = captain.ship
    if ship is None:
        return "No ship"
    cargo_weight = sum(c.quantity for c in captain.cargo)
    free_space = ship.cargo_capacity - cargo_weight
    if quantity > free_space:
        return f"Ship only has {free_space} units of cargo space"

    # Find matching lots in warehouse
    matching = [
        lot for lot in warehouse.inventory
        if lot.good_id == good_id and (source_port is None or lot.acquired_port == source_port)
    ]
    available = sum(lot.quantity for lot in matching)
    if available < quantity:
        return f"Only {available} units of {good_id} in warehouse" + (
            f" from {source_port}" if source_port else ""
        )

    # Execute transfer: warehouse -> ship (preserve provenance per lot)
    remaining = quantity
    for lot in matching:
        if remaining <= 0:
            break
        take = min(lot.quantity, remaining)
        lot.quantity -= take
        remaining -= take

        # Add to ship cargo with original provenance
        existing = next(
            (c for c in captain.cargo
             if c.good_id == good_id and c.acquired_port == lot.acquired_port),
            None,
        )
        if existing:
            existing.quantity += take
        else:
            captain.cargo.append(CargoItem(
                good_id=good_id,
                quantity=take,
                cost_basis=0,  # cost basis lost on warehouse transfer (trade P&L tracked separately)
                acquired_port=lot.acquired_port,
                acquired_region=lot.acquired_region,
                acquired_day=lot.acquired_day,
            ))

    # Clean up empty lots
    warehouse.inventory = [lot for lot in warehouse.inventory if lot.quantity > 0]

    return quantity


# ---------------------------------------------------------------------------
# Upkeep tick
# ---------------------------------------------------------------------------

def tick_infrastructure(
    state: InfrastructureState,
    captain: "Captain",
    day: int,
) -> list[str]:
    """Daily infrastructure upkeep. Deducts costs, closes defaulted assets.

    Returns list of status messages.
    """
    messages: list[str] = []

    # --- Warehouse upkeep ---
    for warehouse in state.warehouses:
        if not warehouse.active:
            continue

        days_owed = day - warehouse.upkeep_paid_through
        if days_owed <= 0:
            continue

        cost = days_owed * warehouse.upkeep_per_day
        if captain.silver >= cost:
            captain.silver -= cost
            warehouse.upkeep_paid_through = day
        else:
            affordable_days = captain.silver // warehouse.upkeep_per_day if warehouse.upkeep_per_day > 0 else 0
            if affordable_days > 0:
                captain.silver -= affordable_days * warehouse.upkeep_per_day
                warehouse.upkeep_paid_through += affordable_days

            unpaid_days = day - warehouse.upkeep_paid_through
            if unpaid_days >= 3:
                warehouse.active = False
                lost_goods = [(lot.good_id, lot.quantity) for lot in warehouse.inventory]
                warehouse.inventory.clear()
                if lost_goods:
                    goods_str = ", ".join(f"{q}x {g}" for g, q in lost_goods)
                    messages.append(
                        f"Warehouse at {warehouse.port_id} closed for non-payment. "
                        f"Goods seized: {goods_str}"
                    )
                else:
                    messages.append(
                        f"Warehouse at {warehouse.port_id} closed for non-payment."
                    )

    # --- Broker office upkeep ---
    from portlight.content.infrastructure import get_broker_spec
    for broker in state.brokers:
        if not broker.active or broker.tier == BrokerTier.NONE:
            continue

        spec = get_broker_spec(broker.region, broker.tier)
        if not spec:
            continue
        upkeep = spec.upkeep_per_day

        days_owed = day - broker.upkeep_paid_through
        if days_owed <= 0:
            continue

        cost = days_owed * upkeep
        if captain.silver >= cost:
            captain.silver -= cost
            broker.upkeep_paid_through = day
        else:
            affordable_days = captain.silver // upkeep if upkeep > 0 else 0
            if affordable_days > 0:
                captain.silver -= affordable_days * upkeep
                broker.upkeep_paid_through += affordable_days

            unpaid_days = day - broker.upkeep_paid_through
            if unpaid_days >= 5:  # brokers are more forgiving than warehouses
                broker.active = False
                messages.append(
                    f"Broker office in {broker.region} closed for non-payment."
                )

    # --- License upkeep ---
    from portlight.content.infrastructure import get_license_spec
    for lic in state.licenses:
        if not lic.active:
            continue

        spec = get_license_spec(lic.license_id)
        if not spec:
            continue
        upkeep = spec.upkeep_per_day

        days_owed = day - lic.upkeep_paid_through
        if days_owed <= 0:
            continue

        cost = days_owed * upkeep
        if captain.silver >= cost:
            captain.silver -= cost
            lic.upkeep_paid_through = day
        else:
            affordable_days = captain.silver // upkeep if upkeep > 0 else 0
            if affordable_days > 0:
                captain.silver -= affordable_days * upkeep
                lic.upkeep_paid_through += affordable_days

            unpaid_days = day - lic.upkeep_paid_through
            if unpaid_days >= 5:  # licenses revoked after 5 days unpaid
                lic.active = False
                messages.append(
                    f"License '{lic.license_id}' revoked for non-payment."
                )

    return messages


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def get_warehouse(state: InfrastructureState, port_id: str) -> WarehouseLease | None:
    """Get the active warehouse at a port, if any."""
    return next(
        (w for w in state.warehouses if w.port_id == port_id and w.active),
        None,
    )


def warehouse_summary(state: InfrastructureState) -> list[WarehouseLease]:
    """Get all active warehouses."""
    return [w for w in state.warehouses if w.active]


# ---------------------------------------------------------------------------
# Broker office operations
# ---------------------------------------------------------------------------

def get_broker(state: InfrastructureState, region: str) -> BrokerOffice | None:
    """Get the active broker office in a region, if any."""
    return next(
        (b for b in state.brokers if b.region == region and b.active and b.tier != BrokerTier.NONE),
        None,
    )


def get_broker_tier(state: InfrastructureState, region: str) -> BrokerTier:
    """Get the broker tier in a region (NONE if no office)."""
    b = get_broker(state, region)
    return b.tier if b else BrokerTier.NONE


def open_broker_office(
    state: InfrastructureState,
    captain: "Captain",
    region: str,
    spec: BrokerOfficeSpec,
    day: int,
) -> BrokerOffice | str:
    """Open or upgrade a broker office in a region."""
    existing = get_broker(state, region)

    if existing:
        if existing.tier == spec.tier:
            return f"Already have a {spec.name} in {region}"
        if existing.tier == BrokerTier.ESTABLISHED and spec.tier == BrokerTier.LOCAL:
            return "Cannot downgrade a broker office"

    if spec.purchase_cost > captain.silver:
        return f"Need {spec.purchase_cost} silver to open {spec.name}, have {captain.silver}"

    captain.silver -= spec.purchase_cost

    if existing:
        # Upgrade in place
        existing.tier = spec.tier
        existing.opened_day = day
        existing.upkeep_paid_through = day
        return existing
    else:
        office = BrokerOffice(
            region=region,
            tier=spec.tier,
            opened_day=day,
            upkeep_paid_through=day,
            active=True,
        )
        state.brokers.append(office)
        return office


# ---------------------------------------------------------------------------
# License operations
# ---------------------------------------------------------------------------

def get_license(state: InfrastructureState, license_id: str) -> OwnedLicense | None:
    """Get an active owned license by ID."""
    return next(
        (lic for lic in state.licenses if lic.license_id == license_id and lic.active),
        None,
    )


def has_license(state: InfrastructureState, license_id: str) -> bool:
    """Check if the player has an active license."""
    return get_license(state, license_id) is not None


def check_license_eligibility(
    state: InfrastructureState,
    spec: LicenseSpec,
    rep: "ReputationState",
) -> str | None:
    """Check if the player meets requirements. Returns error string or None."""
    from portlight.engine.reputation import get_trust_tier

    # Already owned?
    if has_license(state, spec.id):
        return "Already own this license"

    # Trust check
    trust_tier = get_trust_tier(rep)
    trust_rank = {"unproven": 0, "new": 1, "credible": 2, "reliable": 3, "trusted": 4}
    player_trust = trust_rank.get(trust_tier, 0)
    required_trust = trust_rank.get(spec.required_trust_tier, 0)
    if player_trust < required_trust:
        return f"Requires {spec.required_trust_tier} trust (currently {trust_tier})"

    # Standing check (region-scoped)
    if spec.region_scope and spec.required_standing > 0:
        standing = rep.regional_standing.get(spec.region_scope, 0)
        if standing < spec.required_standing:
            return f"Requires {spec.required_standing} standing in {spec.region_scope} (currently {standing})"

    # Heat check
    if spec.required_heat_max is not None and spec.region_scope:
        heat = rep.customs_heat.get(spec.region_scope, 0)
        if heat > spec.required_heat_max:
            return f"Heat too high in {spec.region_scope}: {heat} (max {spec.required_heat_max})"

    # Broker prerequisite
    if spec.required_broker_tier is not None:
        tier_rank = {BrokerTier.NONE: 0, BrokerTier.LOCAL: 1, BrokerTier.ESTABLISHED: 2}
        required_rank = tier_rank.get(spec.required_broker_tier, 0)
        if spec.region_scope:
            # Region-scoped: check specific region
            broker_tier = get_broker_tier(state, spec.region_scope)
            if tier_rank.get(broker_tier, 0) < required_rank:
                return f"Requires {spec.required_broker_tier.value} broker office in {spec.region_scope}"
        else:
            # Global: require the tier in at least one region
            has_any = any(
                tier_rank.get(b.tier, 0) >= required_rank
                for b in state.brokers if b.active
            )
            if not has_any:
                return f"Requires {spec.required_broker_tier.value} broker office in at least one region"

    return None


def purchase_license(
    state: InfrastructureState,
    captain: "Captain",
    spec: LicenseSpec,
    rep: "ReputationState",
    day: int,
) -> OwnedLicense | str:
    """Purchase a license. Returns OwnedLicense or error string."""
    # Eligibility
    err = check_license_eligibility(state, spec, rep)
    if err:
        return err

    # Cost
    if spec.purchase_cost > captain.silver:
        return f"Need {spec.purchase_cost} silver, have {captain.silver}"

    captain.silver -= spec.purchase_cost

    owned = OwnedLicense(
        license_id=spec.id,
        purchased_day=day,
        upkeep_paid_through=day,
        active=True,
    )
    state.licenses.append(owned)
    return owned


# ---------------------------------------------------------------------------
# Board effect computation
# ---------------------------------------------------------------------------

def compute_board_effects(
    state: InfrastructureState,
    region: str,
    license_specs: dict[str, LicenseSpec] | None = None,
) -> dict[str, float]:
    """Compute aggregate board generation effects for a region.

    Returns dict with keys:
      - board_quality_bonus: multiplier on premium offer weight
      - premium_offer_mult: from licenses
      - customs_mult: from licenses
      - lawful_board_mult: from licenses
      - luxury_access: from licenses (0 or 1)
    """
    effects: dict[str, float] = {
        "board_quality_bonus": 1.0,
        "market_signal_bonus": 0.0,
        "trade_term_modifier": 1.0,
        "premium_offer_mult": 1.0,
        "customs_mult": 1.0,
        "lawful_board_mult": 1.0,
        "luxury_access": 0.0,
    }

    # Broker effects
    broker = get_broker(state, region)
    if broker:
        from portlight.content.infrastructure import get_broker_spec
        spec = get_broker_spec(region, broker.tier)
        if spec:
            effects["board_quality_bonus"] = spec.board_quality_bonus
            effects["market_signal_bonus"] = spec.market_signal_bonus
            effects["trade_term_modifier"] = spec.trade_term_modifier

    # License effects (aggregate all active licenses that apply to this region)
    if license_specs:
        for owned in state.licenses:
            if not owned.active:
                continue
            spec = license_specs.get(owned.license_id)
            if spec is None:
                continue
            # Check scope
            if spec.region_scope is not None and spec.region_scope != region:
                continue
            # Apply effects
            for key, value in spec.effects.items():
                if key in effects:
                    if key in ("customs_mult",):
                        effects[key] *= value  # multiplicative
                    elif key in ("luxury_access",):
                        effects[key] = max(effects[key], value)  # flag
                    else:
                        effects[key] *= value  # multiplicative

    return effects


# ---------------------------------------------------------------------------
# Insurance — risk pricing for calculated operators
# ---------------------------------------------------------------------------

class PolicyFamily(str, Enum):
    HULL = "hull"                      # covers ship damage
    PREMIUM_CARGO = "premium_cargo"    # covers cargo loss on luxury/high-value
    CONTRACT_GUARANTEE = "contract_guarantee"  # covers contract failure downside


class PolicyScope(str, Enum):
    NEXT_VOYAGE = "next_voyage"        # expires on arrival
    ACTIVE_CARGO = "active_cargo"      # while specific cargo is held
    NAMED_CONTRACT = "named_contract"  # tied to a specific contract


@dataclass
class PolicySpec:
    """Static definition of an insurance policy."""
    id: str
    family: PolicyFamily
    name: str
    description: str
    premium: int                       # one-time silver cost
    coverage_pct: float                # 0.0-1.0 portion of loss covered
    coverage_cap: int                  # max silver payout per claim
    scope: PolicyScope
    covered_risks: list[str]           # event types or risk classes covered
    exclusions: list[str]              # e.g. ["contraband", "high_heat"]
    heat_max: int | None               # max heat to purchase (None = no limit)
    heat_premium_mult: float           # premium multiplier per heat point above 0


@dataclass
class ActivePolicy:
    """A purchased insurance policy in effect."""
    id: str
    spec_id: str
    family: PolicyFamily
    scope: PolicyScope
    purchased_day: int
    coverage_pct: float
    coverage_cap: int
    premium_paid: int
    target_id: str = ""                # contract_id for guarantee, voyage destination, etc.
    claims_made: int = 0
    total_paid_out: int = 0
    active: bool = True
    voyage_origin: str = ""            # for next_voyage scope: origin port
    voyage_destination: str = ""       # for next_voyage scope: destination port


@dataclass
class InsuranceClaim:
    """Record of a resolved insurance claim."""
    policy_id: str
    day: int
    incident_type: str                 # storm, pirates, inspection, contract_failure
    loss_value: int                    # total loss in silver
    payout: int                        # what insurance actually paid
    denied: bool = False
    denial_reason: str = ""


# ---------------------------------------------------------------------------
# Insurance state extension
# ---------------------------------------------------------------------------
# ActivePolicy and InsuranceClaim lists live on InfrastructureState
# (added via dataclass field extension below — done in the state class above)


def _policy_id(spec_id: str, day: int, seq: int) -> str:
    raw = f"pol:{spec_id}:{day}:{seq}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def purchase_policy(
    state: InfrastructureState,
    captain: "Captain",
    spec: PolicySpec,
    day: int,
    heat: int = 0,
    target_id: str = "",
    voyage_origin: str = "",
    voyage_destination: str = "",
) -> ActivePolicy | str:
    """Purchase an insurance policy. Returns ActivePolicy or error string."""
    # Heat gate
    if spec.heat_max is not None and heat > spec.heat_max:
        return f"Heat too high ({heat}) for {spec.name} — max {spec.heat_max}"

    # Heat-adjusted premium
    heat_surcharge = max(0, heat) * spec.heat_premium_mult
    adjusted_premium = int(spec.premium * (1.0 + heat_surcharge))

    if adjusted_premium > captain.silver:
        return f"Need {adjusted_premium} silver for {spec.name}, have {captain.silver}"

    # Check for duplicate active policy of same type and scope
    for existing in state.policies:
        if (existing.active and existing.spec_id == spec.id and
                existing.target_id == target_id):
            return f"Already have active {spec.name}"

    captain.silver -= adjusted_premium

    seq = len(state.policies)
    policy = ActivePolicy(
        id=_policy_id(spec.id, day, seq),
        spec_id=spec.id,
        family=spec.family,
        scope=spec.scope,
        purchased_day=day,
        coverage_pct=spec.coverage_pct,
        coverage_cap=spec.coverage_cap,
        premium_paid=adjusted_premium,
        target_id=target_id,
        voyage_origin=voyage_origin,
        voyage_destination=voyage_destination,
        active=True,
    )
    state.policies.append(policy)
    return policy


def resolve_claim(
    state: InfrastructureState,
    captain: "Captain",
    incident_type: str,
    loss_value: int,
    day: int,
    cargo_category: str = "",
    contract_id: str = "",
    voyage_destination: str = "",
) -> list[InsuranceClaim]:
    """Check all active policies against an incident. Returns list of claims resolved.

    Called from session after voyage events or contract failures.
    """
    claims: list[InsuranceClaim] = []

    for policy in state.policies:
        if not policy.active:
            continue

        # Match incident to policy family
        if policy.family == PolicyFamily.HULL and incident_type not in ("storm", "pirates"):
            continue
        if policy.family == PolicyFamily.PREMIUM_CARGO and incident_type not in ("pirates", "storm", "inspection"):
            continue
        if policy.family == PolicyFamily.CONTRACT_GUARANTEE and incident_type != "contract_failure":
            continue

        # Scope check
        if policy.scope == PolicyScope.NAMED_CONTRACT:
            if not contract_id or policy.target_id != contract_id:
                continue
        if policy.scope == PolicyScope.NEXT_VOYAGE:
            if voyage_destination and policy.voyage_destination and policy.voyage_destination != voyage_destination:
                continue

        # Check covered risks
        from portlight.content.infrastructure import get_policy_spec
        spec = get_policy_spec(policy.spec_id)
        if spec is None:
            continue

        if incident_type not in spec.covered_risks:
            continue

        # Check exclusions
        denied = False
        denial_reason = ""
        if "contraband" in spec.exclusions and cargo_category == "contraband":
            denied = True
            denial_reason = "Contraband cargo excluded from coverage"

        if denied:
            claim = InsuranceClaim(
                policy_id=policy.id,
                day=day,
                incident_type=incident_type,
                loss_value=loss_value,
                payout=0,
                denied=True,
                denial_reason=denial_reason,
            )
            claims.append(claim)
            state.claims.append(claim)
            continue

        # Calculate payout
        raw_payout = int(loss_value * policy.coverage_pct)
        remaining_cap = policy.coverage_cap - policy.total_paid_out
        payout = min(raw_payout, remaining_cap)
        payout = max(0, payout)

        if payout > 0:
            captain.silver += payout
            policy.claims_made += 1
            policy.total_paid_out += payout

        claim = InsuranceClaim(
            policy_id=policy.id,
            day=day,
            incident_type=incident_type,
            loss_value=loss_value,
            payout=payout,
        )
        claims.append(claim)
        state.claims.append(claim)

    return claims


def expire_voyage_policies(state: InfrastructureState) -> list[str]:
    """Expire next_voyage policies on arrival. Returns messages."""
    messages = []
    for policy in state.policies:
        if policy.active and policy.scope == PolicyScope.NEXT_VOYAGE:
            policy.active = False
            messages.append(f"Voyage policy expired: {policy.spec_id}")
    return messages


def get_active_policies(state: InfrastructureState) -> list[ActivePolicy]:
    """Get all active insurance policies."""
    return [p for p in state.policies if p.active]


# ---------------------------------------------------------------------------
# Credit — borrowed commercial momentum
# ---------------------------------------------------------------------------

class CreditTier(str, Enum):
    NONE = "none"
    MERCHANT_LINE = "merchant_line"          # entry leverage
    HOUSE_CREDIT = "house_credit"            # serious working capital
    PREMIER_COMMERCIAL = "premier_commercial"  # top-tier leverage


@dataclass
class CreditTierSpec:
    """Static definition of a credit tier."""
    tier: CreditTier
    name: str
    credit_limit: int                  # max outstanding debt
    interest_rate: float               # per-period rate (per 10 days)
    interest_period: int               # days between interest accrual
    required_trust_tier: str
    required_standing: int             # min standing in any region
    required_heat_max: int | None      # max heat allowed
    required_license: str | None       # must own this license (or None)
    description: str


@dataclass
class CreditState:
    """Player's credit account state."""
    tier: CreditTier = CreditTier.NONE
    credit_limit: int = 0
    outstanding: int = 0              # current debt
    interest_accrued: int = 0         # interest owed
    last_interest_day: int = 0        # last day interest was calculated
    next_due_day: int = 0             # next payment deadline
    defaults: int = 0                 # number of past defaults
    total_borrowed: int = 0           # lifetime draw total
    total_repaid: int = 0             # lifetime repayment total
    active: bool = False


def _ensure_credit(state: InfrastructureState) -> CreditState:
    """Ensure credit state is initialized."""
    if state.credit is None:
        state.credit = CreditState()
    return state.credit


def check_credit_eligibility(
    state: InfrastructureState,
    spec: CreditTierSpec,
    rep: "ReputationState",
) -> str | None:
    """Check if the player qualifies for a credit tier. Returns error or None."""
    from portlight.engine.reputation import get_trust_tier

    # Trust check
    trust_tier = get_trust_tier(rep)
    trust_rank = {"unproven": 0, "new": 1, "credible": 2, "reliable": 3, "trusted": 4}
    player_trust = trust_rank.get(trust_tier, 0)
    required_trust = trust_rank.get(spec.required_trust_tier, 0)
    if player_trust < required_trust:
        return f"Requires {spec.required_trust_tier} trust (currently {trust_tier})"

    # Standing check (best region)
    if spec.required_standing > 0:
        best_standing = max(rep.regional_standing.values()) if rep.regional_standing else 0
        if best_standing < spec.required_standing:
            return f"Requires {spec.required_standing} standing in any region (best: {best_standing})"

    # Heat check (lowest heat)
    if spec.required_heat_max is not None:
        lowest_heat = min(rep.customs_heat.values()) if rep.customs_heat else 0
        if lowest_heat > spec.required_heat_max:
            return f"Heat too high (lowest: {lowest_heat}, max: {spec.required_heat_max})"

    # License check
    if spec.required_license is not None:
        if not has_license(state, spec.required_license):
            return f"Requires license: {spec.required_license}"

    # Default history penalty
    credit = _ensure_credit(state)
    if credit.defaults >= 3:
        return "Too many past defaults — credit locked"
    if credit.defaults >= 1 and spec.tier == CreditTier.PREMIER_COMMERCIAL:
        return "Premier credit unavailable with default history"

    return None


def open_credit_line(
    state: InfrastructureState,
    spec: CreditTierSpec,
    rep: "ReputationState",
    day: int,
) -> str | None:
    """Open or upgrade a credit line. Returns error or None."""
    err = check_credit_eligibility(state, spec, rep)
    if err:
        return err

    credit = _ensure_credit(state)

    # Can't downgrade
    tier_rank = {CreditTier.NONE: 0, CreditTier.MERCHANT_LINE: 1,
                 CreditTier.HOUSE_CREDIT: 2, CreditTier.PREMIER_COMMERCIAL: 3}
    if tier_rank.get(credit.tier, 0) >= tier_rank.get(spec.tier, 0) and credit.active:
        return f"Already have {credit.tier.value} or better"

    credit.tier = spec.tier
    credit.credit_limit = spec.credit_limit
    credit.active = True
    if credit.last_interest_day == 0:
        credit.last_interest_day = day
    if credit.next_due_day == 0:
        credit.next_due_day = day + spec.interest_period

    return None


def draw_credit(
    state: InfrastructureState,
    captain: "Captain",
    amount: int,
) -> str | None:
    """Borrow from credit line. Returns error or None."""
    credit = _ensure_credit(state)
    if not credit.active:
        return "No credit line established"
    if amount <= 0:
        return "Amount must be positive"

    available = credit.credit_limit - credit.outstanding
    if amount > available:
        return f"Only {available} silver available on credit line (limit {credit.credit_limit}, outstanding {credit.outstanding})"

    credit.outstanding += amount
    credit.total_borrowed += amount
    captain.silver += amount
    return None


def repay_credit(
    state: InfrastructureState,
    captain: "Captain",
    amount: int,
) -> str | None:
    """Repay credit debt. Returns error or None."""
    credit = _ensure_credit(state)
    if not credit.active:
        return "No credit line"
    if amount <= 0:
        return "Amount must be positive"

    # Pay interest first, then principal
    total_owed = credit.outstanding + credit.interest_accrued
    if total_owed == 0:
        return "No outstanding debt"
    amount = min(amount, total_owed)
    if amount > captain.silver:
        return f"Need {amount} silver to repay, have {captain.silver}"

    captain.silver -= amount
    credit.total_repaid += amount

    # Apply to interest first
    if credit.interest_accrued > 0:
        interest_payment = min(amount, credit.interest_accrued)
        credit.interest_accrued -= interest_payment
        amount -= interest_payment

    # Then to principal
    if amount > 0:
        credit.outstanding -= amount

    return None


def tick_credit(
    state: InfrastructureState,
    captain: "Captain",
    day: int,
) -> list[str]:
    """Daily credit tick — accrue interest, check due dates, enforce defaults.

    Returns status messages.
    """
    credit = _ensure_credit(state)
    messages: list[str] = []

    if not credit.active or credit.outstanding == 0:
        return messages

    # Interest accrual
    from portlight.content.infrastructure import get_credit_spec
    spec = get_credit_spec(credit.tier)
    if spec is None:
        return messages

    days_since = day - credit.last_interest_day
    if days_since >= spec.interest_period:
        periods = days_since // spec.interest_period
        interest = int(credit.outstanding * spec.interest_rate * periods)
        credit.interest_accrued += interest
        credit.last_interest_day = day
        if interest > 0:
            messages.append(f"Interest accrued: {interest} silver on {credit.outstanding} debt")

    # Due date enforcement — check against the due day set at open/last payment
    total_owed = credit.outstanding + credit.interest_accrued
    if day >= credit.next_due_day and credit.next_due_day > 0 and total_owed > 0:
        # Minimum payment = interest + 10% of principal
        min_payment = credit.interest_accrued + max(1, credit.outstanding // 10)

        if captain.silver >= min_payment:
            # Auto-pay minimum
            captain.silver -= min_payment
            credit.total_repaid += min_payment
            # Apply to interest first
            interest_part = min(min_payment, credit.interest_accrued)
            credit.interest_accrued -= interest_part
            remaining = min_payment - interest_part
            credit.outstanding -= remaining
            credit.next_due_day = day + spec.interest_period
            messages.append(f"Credit payment due: {min_payment} silver auto-deducted")
        else:
            # Default!
            credit.defaults += 1
            messages.append(
                f"CREDIT DEFAULT! Cannot pay {min_payment} silver. "
                f"Default #{credit.defaults} recorded — trust damage applied."
            )
            # Deduct whatever is available
            if captain.silver > 0:
                partial = captain.silver
                captain.silver = 0
                credit.total_repaid += partial
                if credit.interest_accrued > 0:
                    interest_part = min(partial, credit.interest_accrued)
                    credit.interest_accrued -= interest_part
                    partial -= interest_part
                credit.outstanding -= partial

            credit.next_due_day = day + spec.interest_period

            # After 3 defaults, line is frozen
            if credit.defaults >= 3:
                credit.active = False
                messages.append("Credit line frozen after 3 defaults.")

    return messages


# ---------------------------------------------------------------------------
# Emergency loan (anti-soft-lock — no trust required)
# ---------------------------------------------------------------------------

def emergency_loan(
    captain: "Captain",
    amount: int,
) -> str | int:
    """Take an emergency loan at terrible terms (15% immediate interest).

    No trust required. Available to anyone. The interest is applied
    immediately — you borrow 100, you owe 115, but get 100 in hand.

    Returns silver received on success, or error string.
    """
    if amount <= 0:
        return "Amount must be positive"
    if amount > 200:
        return "Emergency loans capped at 200 silver"

    interest = max(1, int(amount * 0.15))
    total_debt = amount + interest
    captain.silver += amount

    # Track as a deferred fee (simple debt that must be repaid)
    captain.deferred_fees.append({
        "type": "emergency_loan",
        "amount": total_debt,
        "day": captain.day,
    })
    return amount
