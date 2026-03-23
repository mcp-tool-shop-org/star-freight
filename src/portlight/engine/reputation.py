"""Reputation engine — the world's memory of the player's commercial behavior.

All standing/heat/trust mutations flow through this module. No other code
should directly mutate ReputationState dictionaries.

Canonical mutation points:
  - record_trade_outcome: after a profitable sell (the primary reputation driver)
  - record_port_arrival: when docking at a port
  - record_inspection_outcome: after an inspection event at sea
  - record_seizure: after cargo is confiscated
  - tick_reputation: daily time decay (heat cools, standing stabilizes)

Access effects:
  - get_fee_modifier: regional standing affects port fees
  - get_service_modifier: port standing affects local service costs
  - get_inspection_modifier: heat affects inspection severity
  - get_trust_tier: commercial trust tier for contract eligibility
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from portlight.engine.models import GoodCategory, ReputationIncident

if TYPE_CHECKING:
    from portlight.engine.models import ReputationState

# Maximum values (prevent runaway)
MAX_STANDING = 100
MAX_HEAT = 100
MAX_TRUST = 100
MAX_INCIDENTS = 20


def _clamp(value: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, value))


def _add_incident(
    rep: "ReputationState",
    day: int,
    port_id: str,
    region: str,
    incident_type: str,
    description: str,
    heat_delta: int = 0,
    standing_delta: int = 0,
    trust_delta: int = 0,
) -> None:
    """Record an incident and cap the list."""
    rep.recent_incidents.insert(0, ReputationIncident(
        day=day, port_id=port_id, region=region,
        incident_type=incident_type, description=description,
        heat_delta=heat_delta, standing_delta=standing_delta,
        trust_delta=trust_delta,
    ))
    if len(rep.recent_incidents) > MAX_INCIDENTS:
        rep.recent_incidents = rep.recent_incidents[:MAX_INCIDENTS]


# ---------------------------------------------------------------------------
# Suspicious-dump law
# ---------------------------------------------------------------------------

def _compute_suspicion(
    good_category: GoodCategory,
    quantity: int,
    stock_target: int,
    margin_pct: float,
    flood_penalty: float,
    captain_type: str,
    region_heat: int,
) -> int:
    """Score how suspicious a sell action looks. Higher = more heat generated.

    Factors:
      - margin severity (high margins look like exploitation)
      - quantity vs market target (flooding a small market is suspicious)
      - luxury/sensitive goods flag
      - existing heat amplifies further suspicion
      - captain inspection profile
      - flood penalty (repeated dumps at same port)
    """
    score = 0

    # Margin severity (>100% margin starts generating heat)
    if margin_pct > 200:
        score += 4
    elif margin_pct > 150:
        score += 3
    elif margin_pct > 100:
        score += 2
    elif margin_pct > 50:
        score += 1

    # Quantity relative to market target (>50% of target is aggressive)
    if stock_target > 0:
        dump_ratio = quantity / stock_target
        if dump_ratio > 0.8:
            score += 3
        elif dump_ratio > 0.5:
            score += 2
        elif dump_ratio > 0.3:
            score += 1

    # Luxury goods draw more attention
    if good_category == GoodCategory.LUXURY:
        score += 2
    elif good_category == GoodCategory.CONTRABAND:
        score += 4

    # Existing flood penalty means repeated dumps (compound suspicion)
    if flood_penalty > 0.3:
        score += 2
    elif flood_penalty > 0.1:
        score += 1

    # Existing heat amplifies (watched traders attract more scrutiny)
    if region_heat >= 25:
        score += 2
    elif region_heat >= 10:
        score += 1

    # Captain profile
    if captain_type == "smuggler":
        score += 1  # smugglers inherently draw more suspicion

    return score


# ---------------------------------------------------------------------------
# Core mutation functions
# ---------------------------------------------------------------------------

def record_trade_outcome(
    rep: "ReputationState",
    captain_type: str,
    day: int,
    port_id: str,
    region: str,
    good_id: str,
    good_category: GoodCategory,
    quantity: int,
    margin_pct: float,
    stock_target: int,
    flood_penalty: float,
    is_sell: bool,
) -> int:
    """Record a trade and mutate reputation. Returns heat delta.

    Buy actions are mostly neutral. Sell actions are where reputation moves.
    """
    if not is_sell:
        # Buys are neutral — just a small familiarity bump
        rep.port_standing.setdefault(port_id, 0)
        return 0

    region_heat = rep.customs_heat.get(region, 0)

    # Compute suspicion
    suspicion = _compute_suspicion(
        good_category, quantity, stock_target,
        margin_pct, flood_penalty, captain_type, region_heat,
    )

    heat_delta = 0
    standing_delta = 0
    trust_delta = 0

    if suspicion >= 6:
        # Very suspicious — big heat spike, standing damage
        heat_delta = min(suspicion, 8)
        standing_delta = -2
        trust_delta = -1
        desc = f"Suspicious {good_id} dump ({int(margin_pct)}% margin, {quantity} units)"
    elif suspicion >= 3:
        # Moderately suspicious — heat rises, no standing change
        heat_delta = suspicion
        desc = f"Aggressive {good_id} sale drew attention ({int(margin_pct)}% margin)"
    elif margin_pct > 20:
        # Clean profitable trade — good for standing and trust
        standing_delta = 1
        trust_delta = 1
        desc = f"Profitable {good_id} trade (+{int(margin_pct)}% margin)"
    else:
        # Break-even or small margin — minor familiarity
        desc = f"Routine {good_id} sale"

    # Merchant bonus: clean trades build trust faster
    if captain_type == "merchant" and suspicion < 3 and margin_pct > 20:
        trust_delta += 1

    # Apply mutations
    rep.customs_heat[region] = _clamp(region_heat + heat_delta, 0, MAX_HEAT)
    rep.regional_standing[region] = _clamp(
        rep.regional_standing.get(region, 0) + standing_delta, 0, MAX_STANDING)
    rep.commercial_trust = _clamp(rep.commercial_trust + trust_delta, 0, MAX_TRUST)
    rep.port_standing.setdefault(port_id, 0)
    rep.port_standing[port_id] = _clamp(
        rep.port_standing[port_id] + max(standing_delta, 0) + (1 if suspicion < 3 else 0),
        0, MAX_STANDING)

    if heat_delta != 0 or standing_delta != 0 or trust_delta != 0:
        _add_incident(rep, day, port_id, region, "trade", desc,
                      heat_delta, standing_delta, trust_delta)

    return heat_delta


def record_port_arrival(
    rep: "ReputationState",
    day: int,
    port_id: str,
    region: str,
) -> None:
    """Record arrival at a port. Reinforces familiarity, slight heat decay."""
    # Port familiarity
    rep.port_standing.setdefault(port_id, 0)
    rep.port_standing[port_id] = _clamp(rep.port_standing[port_id] + 1, 0, MAX_STANDING)

    # Regional familiarity (slower)
    rep.regional_standing[region] = _clamp(
        rep.regional_standing.get(region, 0) + 1, 0, MAX_STANDING)

    # Arrival decays a bit of regional heat (lawful presence)
    heat = rep.customs_heat.get(region, 0)
    if heat > 0:
        decay = max(1, heat // 10)  # 10% decay on arrival
        rep.customs_heat[region] = _clamp(heat - decay, 0, MAX_HEAT)


def record_inspection_outcome(
    rep: "ReputationState",
    day: int,
    port_id: str,
    region: str,
    fine_amount: int,
    cargo_seized: bool,
) -> None:
    """Record an inspection event during a voyage."""
    heat_delta = 2  # all inspections raise some heat
    standing_delta = 0
    trust_delta = 0

    if cargo_seized:
        heat_delta = 5
        standing_delta = -3
        trust_delta = -2
        desc = f"Cargo seized during inspection (fined {fine_amount} silver)"
    elif fine_amount > 15:
        heat_delta = 3
        trust_delta = -1
        desc = f"Heavy inspection fine ({fine_amount} silver)"
    else:
        desc = f"Routine inspection ({fine_amount} silver fee)"

    rep.customs_heat[region] = _clamp(
        rep.customs_heat.get(region, 0) + heat_delta, 0, MAX_HEAT)
    rep.regional_standing[region] = _clamp(
        rep.regional_standing.get(region, 0) + standing_delta, 0, MAX_STANDING)
    rep.commercial_trust = _clamp(rep.commercial_trust + trust_delta, 0, MAX_TRUST)

    _add_incident(rep, day, port_id, region, "inspection", desc,
                  heat_delta, standing_delta, trust_delta)


def tick_reputation(rep: "ReputationState") -> None:
    """Daily time decay. Called once per game day.

    Heat decays fastest (hot situations cool).
    Standing and trust are stable (you don't lose reputation from inaction).
    """
    # Heat decays: -2/day above 20, -1/day from 5-19.
    # Below 5: no time-based decay (intentional baseline friction).
    # Low heat (1-4) only decays via port arrival (-10%, min 1).
    # This means a player who earned minor heat will carry a small residual
    # unless they visit ports to trigger arrival decay.
    for region in rep.customs_heat:
        heat = rep.customs_heat[region]
        if heat >= 20:
            rep.customs_heat[region] = heat - 2
        elif heat >= 5:
            rep.customs_heat[region] = heat - 1


# ---------------------------------------------------------------------------
# Access effects — computed from reputation state
# ---------------------------------------------------------------------------

def get_fee_modifier(rep: "ReputationState", region: str) -> float:
    """Port fee multiplier based on regional standing.

    Higher standing = cheaper fees (0.8 at 30+, 0.9 at 15+).
    High heat = more expensive (1.2 at 25+, 1.1 at 15+).
    """
    standing = rep.regional_standing.get(region, 0)
    heat = rep.customs_heat.get(region, 0)

    mod = 1.0
    if standing >= 30:
        mod -= 0.2
    elif standing >= 15:
        mod -= 0.1

    if heat >= 25:
        mod += 0.2
    elif heat >= 15:
        mod += 0.1

    return max(0.5, min(1.5, mod))


def get_service_modifier(rep: "ReputationState", port_id: str) -> float:
    """Service cost multiplier based on port standing.

    Higher standing = cheaper provisions/repairs/crew.
    """
    standing = rep.port_standing.get(port_id, 0)

    if standing >= 30:
        return 0.8
    elif standing >= 15:
        return 0.9
    elif standing >= 5:
        return 0.95
    return 1.0


def get_inspection_modifier(rep: "ReputationState", region: str) -> float:
    """Additional inspection chance multiplier from heat.

    Stacks with captain's inspection_chance_mult.
    """
    heat = rep.customs_heat.get(region, 0)

    if heat >= 40:
        return 1.8  # almost doubled
    elif heat >= 25:
        return 1.4
    elif heat >= 15:
        return 1.2
    return 1.0


def get_fine_modifier(rep: "ReputationState", region: str) -> float:
    """Fine severity multiplier from heat. Stacks with captain's fine_mult."""
    heat = rep.customs_heat.get(region, 0)

    if heat >= 30:
        return 1.5
    elif heat >= 15:
        return 1.2
    return 1.0


def get_trust_tier(rep: "ReputationState") -> str:
    """Commercial trust tier name for display and contract gating."""
    trust = rep.commercial_trust
    if trust >= 40:
        return "trusted"
    elif trust >= 25:
        return "reliable"
    elif trust >= 10:
        return "credible"
    elif trust >= 1:
        return "new"
    return "unproven"
