# State Model — Star Freight (Code-Facing)

> Canonical translation of the State Dictionary into implementation schema.
> Every variable in this document has a 1:1 match in `REGISTRY_STATE_DICTIONARY.md`.
> If a variable is not in the State Dictionary, it does not exist.

---

## Campaign State (top-level game object)

```python
@dataclass
class CampaignState:
    # --- Primary ---
    credits: int                          # 0–uncapped. Start: 500
    day: int                              # 1–uncapped. Start: 1
    crew_roster: list[CrewMember]         # Max 6
    ship: Ship
    cargo_hold: list[CargoSlot]           # Limited by ship.cargo_capacity
    reputation: dict[str, int]            # faction_id → -100..+100
    cultural_knowledge: dict[str, int]    # civ_id → 0..3
    veshan_debts: list[VeshanDebt]
    investigation_progress: int           # 0–10
    investigation_beats_found: list[str]  # beat IDs
    consequence_log: list[ConsequenceEntry]  # Rolling 200

    # --- Station context (set on arrival, cleared on departure) ---
    current_station: str | None           # station_id or None if in transit
    transit_state: TransitState | None    # None if docked
```

## Crew Member

```python
@dataclass
class CrewMember:
    name: str
    civilization: str                     # compact, keth, veshan, orryn, reach
    role: str                             # gunner, engineer, pilot, medic, broker, face, tech
    hp: int
    hp_max: int
    speed: int                            # grid tiles per turn
    abilities: list[str]                  # 3 ability IDs. 3rd locked until trusted.
    ship_skill: str                       # Ability contributed to ship combat
    morale: int                           # 0–100. Start: 40–50
    loyalty_tier: str                     # stranger | trusted | bonded
    loyalty_points: int                   # 0–100. Thresholds: 31=trusted, 66=bonded
    injured: bool
    pay_rate: int                         # credits per 30 days
    narrative_hooks: list[str]            # active story hooks
    opinions: dict[str, int]             # faction_id → -10..+10 (crew values)
```

## Ship

```python
@dataclass
class Ship:
    hull_hp: int                          # Start: 1800
    hull_max: int                         # Start: 2000
    shield_hp: int                        # Start: 200
    shield_max: int                       # Start: 250
    weapon_power: int                     # Base value, modified by crew
    engine_speed: int                     # Grid tiles per turn. Start: 2
    cargo_capacity: int                   # Max cargo slots. Start: 6
    quarters_tier: int                    # 1–3. Affects crew morale
    systems_condition: int                # 0–100%. Start: 70. Degrades ~1.5–2%/day
    ability_slots: list[str]              # 3 slots, filled by crew ship_skill
    upgrades: dict[str, str]              # slot_id → upgrade_id
    fuel: int                             # Days of travel remaining. Start: 4
```

## Cargo

```python
@dataclass
class CargoSlot:
    good: str                             # good_id
    quantity: int
    contraband: bool                      # True if illegal in some jurisdictions
    origin_civ: str                       # civilization of origin
```

## Veshan Debt

```python
@dataclass
class VeshanDebt:
    house: str                            # Veshan house ID (drashan, vekhari, solketh)
    weight: str                           # minor | standard | major
    direction: str                        # owed | held (owed = you owe them)
    description: str
    day_created: int
```

## Consequence Entry

```python
@dataclass
class ConsequenceEntry:
    action_tag: str                       # e.g., "trade_smuggle", "combat_retreat", "custom_violate"
    faction_tags: list[str]               # factions affected
    severity: str                         # minor | standard | major
    day: int
    description: str
```

## Transit State

```python
@dataclass
class TransitState:
    origin: str                           # station_id
    destination: str                      # station_id
    lane_id: str
    days_remaining: int
    days_total: int
    events_pending: list[str]             # pre-rolled encounter IDs for this trip
```

---

## Derived States (computed, never stored)

```python
# These are functions, not fields.

def merchant_pirate_spectrum(state: CampaignState) -> float:
    """Weighted average of lawful vs criminal reputation. -1.0 (pirate) to +1.0 (merchant)."""

def crew_fitness(state: CampaignState) -> int:
    """Count of crew where injured == False."""

def ship_combat_ready(state: CampaignState) -> bool:
    """hull_hp > 0 AND systems_condition > 25 AND fuel > 0."""

def monthly_floor_cost(state: CampaignState) -> int:
    """fuel_rate + maintenance_rate + sum(crew.pay_rate)."""

def station_access_tier(state: CampaignState, station_id: str) -> str:
    """Map reputation to breakpoint: hostile/unwelcome/cold/neutral/respected/trusted/allied."""

def trade_price_modifier(state: CampaignState, station_id: str) -> float:
    """Map reputation to discount/surcharge multiplier."""

def breakdown_risk(state: CampaignState) -> float:
    """0% if systems > 50, 5%/day if 25–50, 100% if <25."""

def keth_season(state: CampaignState) -> str:
    """Derived from day % 360: emergence (0–89), harvest (90–179), dormancy (180–269), spawning (270–359)."""
```

---

## State That Does NOT Exist

These are explicitly excluded. Do not add them.

| Rejected | Reason |
|----------|--------|
| Player XP / level | Growth from crew + reputation + knowledge, not XP |
| Skill points / skill tree | Crew abilities are fixed per role |
| Alignment / morality score | Derived from reputation spectrum |
| Hunger / thirst / survival | Fuel is the only consumable travel pressure |
| Crew-to-crew relationships | Crew have opinions about player, not each other |
| Weather state | Sector conditions are placed events |
| NPC schedules | NPCs don't move |
| Equipment / stat items | No "+5 damage" items. Ship upgrades only. |
| Map fog / exploration | All stations known. Knowledge gates access, not visibility. |

---

## Mutation Rules

1. **Credits cannot go below 0.** If an action would reduce credits below 0, it must be rejected or trigger anti-soft-lock (emergency loan, distress work, docking charity).
2. **Reputation is clamped -100 to +100.** Excess points are lost.
3. **Cultural knowledge is clamped 0 to 3.** No regression.
4. **Crew roster max 6.** Recruitment blocked if full.
5. **Consequence log rolls at 200.** Oldest entries pruned first.
6. **Morale clamped 0–100.** Departure check fires at <25 for 3+ consecutive days.
7. **Loyalty tier transitions are one-way.** Once trusted, cannot revert to stranger. (Departure removes the crew member entirely.)
8. **Ship systems degrade every travel day.** This is automatic and cannot be avoided.
9. **Fuel decrements every travel day.** Reaching 0 mid-transit triggers drift emergency.
10. **Veshan debts age.** Debts >30 days old trigger pressure events via consequence engine.
