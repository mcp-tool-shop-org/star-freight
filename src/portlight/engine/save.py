"""Save/load system — serialize WorldState to/from JSON.

Contract:
  - save_game(world, path) -> writes JSON file
  - load_game(path) -> WorldState | None
  - WorldState round-trips without data loss
"""

# ruff: noqa: N818  — SaveVersionError inherits ValueError for back-compat

from __future__ import annotations

import json
from pathlib import Path

from portlight.engine.models import (
    ActiveFestival,
    ActiveInjury,
    Captain,
    CargoItem,
    CombatGear,
    CrewRoster,
    CulturalState,
    InstalledUpgrade,
    MarketSlot,
    OwnedShip,
    PendingDuel,
    PirateEncounterRecord,
    PirateState,
    Port,
    PortFeature,
    ReputationIncident,
    ReputationState,
    Route,
    Ship,
    VoyageState,
    VoyageStatus,
    WorldState,
)
from portlight.engine.contracts import (
    ActiveContract,
    ContractBoard,
    ContractFamily,
    ContractOffer,
    ContractOutcome,
    ContractStatus,
)
from portlight.engine.infrastructure import (
    ActivePolicy,
    BrokerOffice,
    BrokerTier,
    CreditState,
    CreditTier,
    InfrastructureState,
    InsuranceClaim,
    OwnedLicense,
    PolicyFamily,
    PolicyScope,
    StoredLot,
    WarehouseLease,
    WarehouseTier,
)
from portlight.engine.campaign import CampaignState, MilestoneCompletion
from portlight.engine.narrative import JournalEntry, NarrativeState
from portlight.receipts.models import ReceiptLedger, TradeAction, TradeReceipt

SAVE_DIR = "saves"
SAVE_FILE = "portlight_save.json"  # legacy filename, kept for migration
DEFAULT_SLOT = "default"
CURRENT_SAVE_VERSION = 12


class SaveVersionError(ValueError):
    """Save file version is incompatible (newer than code or migration chain broken)."""


def save_filename(slot: str = DEFAULT_SLOT) -> str:
    """Return the JSON filename for a named save slot."""
    # Sanitize: only allow alphanumeric, dash, underscore
    safe = "".join(c for c in slot if c.isalnum() or c in "-_")
    if not safe:
        safe = DEFAULT_SLOT
    return f"{safe}.json"


# ---------------------------------------------------------------------------
# Save migration chain
# ---------------------------------------------------------------------------

def _migrate_v1_to_v2(data: dict) -> dict:
    """v1 -> v2: Add save_version tracking, ensure all subsections have defaults."""
    # Ensure campaign section exists
    if "campaign" not in data:
        data["campaign"] = {"completed": [], "completed_paths": []}
    # Ensure infrastructure section exists
    if "infrastructure" not in data:
        data["infrastructure"] = {
            "warehouses": [], "brokers": [], "licenses": [],
            "policies": [], "claims": [],
        }
    # Ensure contract_board section exists
    if "contract_board" not in data:
        data["contract_board"] = {
            "offers": [], "active": [], "completed": [],
            "last_refresh_day": 0, "max_offers": 5,
        }
    # Ensure ledger section exists
    if "ledger" not in data:
        data["ledger"] = {
            "run_id": "", "receipts": [],
            "total_buys": 0, "total_sells": 0, "net_profit": 0,
        }
    data["version"] = 2
    return data


def _migrate_v2_to_v3(data: dict) -> dict:
    """v2 -> v3: Add North Atlantic and South Seas regions to reputation state."""
    captain = data.get("captain", {})
    standing = captain.get("standing", {})

    # Add new regions to regional_standing
    rs = standing.get("regional_standing", {})
    rs.setdefault("North Atlantic", 0)
    rs.setdefault("South Seas", 0)
    standing["regional_standing"] = rs

    # Add new regions to customs_heat
    ch = standing.get("customs_heat", {})
    ch.setdefault("North Atlantic", 0)
    ch.setdefault("South Seas", 0)
    standing["customs_heat"] = ch

    captain["standing"] = standing
    data["captain"] = captain
    data["version"] = 3
    return data


def _migrate_v3_to_v4(data: dict) -> dict:
    """v3 -> v4: Add cultural state tracking."""
    if "cultural_state" not in data:
        data["cultural_state"] = {
            "active_festivals": [],
            "regions_entered": [],
            "cultural_encounters": 0,
            "port_visits": {},
        }
    data["version"] = 4
    return data


# Ordered migration functions: (from_version, to_version, migrator)
def _migrate_v4_to_v5(data: dict) -> dict:
    """v4 -> v5: Add underworld standing and pirate state."""
    captain = data.get("captain", {})
    standing = captain.get("standing", {})
    standing.setdefault("underworld_standing", {})
    standing.setdefault("underworld_heat", 0)
    captain["standing"] = standing
    data["captain"] = captain
    data.setdefault("pirate_state", {"encounters": [], "nemesis_id": None, "duels_won": 0, "duels_lost": 0})
    data["version"] = 5
    return data


def _migrate_v5_to_v6(data: dict) -> dict:
    """v5 -> v6: Add armor, melee weapons, weapon upgrades to combat gear. Add ship upgrades."""
    captain = data.get("captain", {})
    gear = captain.get("combat_gear", {})
    gear.setdefault("armor", None)
    gear.setdefault("melee_weapon", None)
    gear.setdefault("weapon_upgrades", {})
    captain["combat_gear"] = gear
    ship = captain.get("ship")
    if ship:
        ship.setdefault("upgrades", [])
    data["version"] = 6
    return data


def _migrate_v6_to_v7(data: dict) -> dict:
    """v6 -> v7: Evolve ship upgrades from list[str] to list[dict] with upgrade_slots."""
    captain = data.get("captain", {})
    ship = captain.get("ship")
    if ship:
        old_upgrades = ship.get("upgrades", [])
        if old_upgrades and isinstance(old_upgrades[0], str):
            ship["upgrades"] = [
                {"upgrade_id": uid, "installed_day": 0} for uid in old_upgrades
            ]
        ship.setdefault("upgrade_slots", 2)
    data["version"] = 7
    return data


def _migrate_v7_to_v8(data: dict) -> dict:
    """v7 -> v8: Add fleet to captain."""
    captain = data.get("captain", {})
    captain.setdefault("fleet", [])
    data["version"] = 8
    return data


def _migrate_v8_to_v9(data: dict) -> dict:
    """v8 -> v9: Add crew roster to ships."""
    captain = data.get("captain", {})
    ship = captain.get("ship")
    if ship:
        crew_count = ship.get("crew", 0)
        ship.setdefault("roster", {
            "sailors": crew_count, "gunners": 0, "navigators": 0,
            "surgeons": 0, "marines": 0, "quartermasters": 0,
        })
    # Also add roster to fleet ships
    for owned in captain.get("fleet", []):
        fleet_ship = owned.get("ship", {})
        if fleet_ship:
            fc = fleet_ship.get("crew", 0)
            fleet_ship.setdefault("roster", {
                "sailors": fc, "gunners": 0, "navigators": 0,
                "surgeons": 0, "marines": 0, "quartermasters": 0,
            })
    data["version"] = 9
    return data


_MIGRATIONS = [
    (1, 2, _migrate_v1_to_v2),
    (2, 3, _migrate_v2_to_v3),
    (3, 4, _migrate_v3_to_v4),
    (4, 5, _migrate_v4_to_v5),
    (5, 6, _migrate_v5_to_v6),
    (6, 7, _migrate_v6_to_v7),
    (7, 8, _migrate_v7_to_v8),
    (8, 9, _migrate_v8_to_v9),
]


def _migrate_v9_to_v10(data: dict) -> dict:
    """v9 -> v10: Add morale to ships."""
    captain = data.get("captain", {})
    ship = captain.get("ship")
    if ship:
        ship.setdefault("morale", 50)
    for owned in captain.get("fleet", []):
        fleet_ship = owned.get("ship", {})
        if fleet_ship:
            fleet_ship.setdefault("morale", 50)
    data["version"] = 10
    return data


# Add v9->v10 and v10->v11 to migration chain
_MIGRATIONS.append((9, 10, _migrate_v9_to_v10))


def _migrate_v10_to_v11(data: dict) -> dict:
    """v10 -> v11: Add officers to ships."""
    captain = data.get("captain", {})
    ship = captain.get("ship")
    if ship:
        ship.setdefault("officers", [])
    for owned in captain.get("fleet", []):
        fleet_ship = owned.get("ship", {})
        if fleet_ship:
            fleet_ship.setdefault("officers", [])
    data["version"] = 11
    return data


_MIGRATIONS.append((10, 11, _migrate_v10_to_v11))


def _migrate_v11_to_v12(data: dict) -> dict:
    """v11 -> v12: Add recent_events to voyage, breach tracking, bounty fields."""
    voyage = data.get("voyage")
    if voyage and isinstance(voyage, dict):
        voyage.setdefault("recent_events", [])
    # Future phases will add more fields here with safe defaults
    captain = data.get("captain", {})
    captain.setdefault("breach_records", [])
    captain.setdefault("wanted_level", 0)
    captain.setdefault("deferred_fees", [])
    captain.setdefault("active_bounties", [])
    pirates = data.get("pirates", {})
    pirates.setdefault("bounty_board", [])
    data["version"] = 12
    return data


_MIGRATIONS.append((11, 12, _migrate_v11_to_v12))


def migrate_save(data: dict) -> dict:
    """Apply all necessary migrations to bring save data to current version.

    Returns migrated data dict. Raises ValueError if version is unsupported.
    """
    version = data.get("version", 1)
    if version == CURRENT_SAVE_VERSION:
        return data
    if version > CURRENT_SAVE_VERSION:
        raise SaveVersionError(
            f"Save file version {version} is newer than supported "
            f"version {CURRENT_SAVE_VERSION}. Update Portlight to load this save."
        )

    for from_v, to_v, fn in _MIGRATIONS:
        if version == from_v:
            data = fn(data)
            version = to_v

    if version != CURRENT_SAVE_VERSION:
        raise SaveVersionError(
            f"Migration chain broken: reached version {version}, "
            f"expected {CURRENT_SAVE_VERSION}"
        )
    return data


def _ship_to_dict(ship: Ship) -> dict:
    return {
        "template_id": ship.template_id,
        "name": ship.name,
        "hull": ship.hull,
        "hull_max": ship.hull_max,
        "cargo_capacity": ship.cargo_capacity,
        "speed": ship.speed,
        "crew": ship.crew,
        "crew_max": ship.crew_max,
        "cannons": getattr(ship, "cannons", 0),
        "maneuver": getattr(ship, "maneuver", 0.5),
        "upgrades": [
            {"upgrade_id": u.upgrade_id, "installed_day": u.installed_day}
            for u in (ship.upgrades or [])
        ],
        "upgrade_slots": getattr(ship, "upgrade_slots", 2),
        "roster": {
            "sailors": ship.roster.sailors,
            "gunners": ship.roster.gunners,
            "navigators": ship.roster.navigators,
            "surgeons": ship.roster.surgeons,
            "marines": ship.roster.marines,
            "quartermasters": ship.roster.quartermasters,
        } if hasattr(ship, "roster") else None,
        "morale": getattr(ship, "morale", 50),
        "officers": [
            {"name": o.name, "role": o.role.value if hasattr(o.role, 'value') else o.role,
             "experience": o.experience, "origin_port": o.origin_port, "trait": o.trait}
            for o in (ship.officers if hasattr(ship, "officers") else [])
        ],
    }


def _ship_from_dict(d: dict) -> Ship:
    # Derive cannons/maneuver from template if not in save data (migration)
    if "cannons" not in d or "maneuver" not in d:
        from portlight.content.ships import SHIPS
        template = SHIPS.get(d.get("template_id", ""))
        d.setdefault("cannons", template.cannons if template else 0)
        d.setdefault("maneuver", template.maneuver if template else 0.5)
    # Deserialize upgrades from dicts to InstalledUpgrade objects
    raw_upgrades = d.pop("upgrades", [])
    upgrades = []
    for item in raw_upgrades:
        if isinstance(item, dict):
            upgrades.append(InstalledUpgrade(**item))
        elif isinstance(item, str):
            upgrades.append(InstalledUpgrade(upgrade_id=item, installed_day=0))
    d["upgrades"] = upgrades
    d.setdefault("upgrade_slots", 2)
    # Deserialize roster
    raw_roster = d.pop("roster", None)
    if raw_roster and isinstance(raw_roster, dict):
        roster = CrewRoster(**raw_roster)
    else:
        # Legacy: create roster with all current crew as sailors
        roster = CrewRoster(sailors=d.get("crew", 0))
    d["roster"] = roster
    d.setdefault("morale", 50)
    # Deserialize officers
    from portlight.engine.models import CrewRole, Officer
    raw_officers = d.pop("officers", [])
    officers = []
    for o in raw_officers:
        try:
            role = CrewRole(o.get("role", "sailor"))
        except ValueError:
            role = CrewRole.SAILOR
        officers.append(Officer(
            name=o.get("name", "Unknown"),
            role=role,
            experience=o.get("experience", 0),
            origin_port=o.get("origin_port", ""),
            trait=o.get("trait", ""),
        ))
    d["officers"] = officers
    return Ship(**d)


def _incident_to_dict(inc: ReputationIncident) -> dict:
    return {
        "day": inc.day,
        "port_id": inc.port_id,
        "region": inc.region,
        "incident_type": inc.incident_type,
        "description": inc.description,
        "heat_delta": inc.heat_delta,
        "standing_delta": inc.standing_delta,
        "trust_delta": inc.trust_delta,
    }


def _incident_from_dict(d: dict) -> ReputationIncident:
    return ReputationIncident(**d)


def _reputation_to_dict(rep: ReputationState) -> dict:
    return {
        "regional_standing": rep.regional_standing,
        "port_standing": rep.port_standing,
        "customs_heat": rep.customs_heat,
        "commercial_trust": rep.commercial_trust,
        "recent_incidents": [_incident_to_dict(i) for i in rep.recent_incidents],
        "underworld_standing": rep.underworld_standing,
        "underworld_heat": rep.underworld_heat,
    }


def _reputation_from_dict(d: dict) -> ReputationState:
    incidents = [_incident_from_dict(i) for i in d.get("recent_incidents", [])]
    # Ensure all 5 regions exist (migration from 3-region saves)
    default_standing = {"Mediterranean": 0, "North Atlantic": 0, "West Africa": 0, "East Indies": 0, "South Seas": 0}
    default_heat = {"Mediterranean": 0, "North Atlantic": 0, "West Africa": 0, "East Indies": 0, "South Seas": 0}
    standing = {**default_standing, **d.get("regional_standing", {})}
    heat = {**default_heat, **d.get("customs_heat", {})}
    return ReputationState(
        regional_standing=standing,
        port_standing=d.get("port_standing", {}),
        customs_heat=heat,
        commercial_trust=d.get("commercial_trust", 0),
        recent_incidents=incidents,
        underworld_standing=d.get("underworld_standing", {}),
        underworld_heat=d.get("underworld_heat", 0),
    )


def _combat_gear_to_dict(gear: CombatGear) -> dict:
    return {
        "firearm": gear.firearm,
        "firearm_ammo": gear.firearm_ammo,
        "throwing_weapons": gear.throwing_weapons,
        "mechanical_weapon": gear.mechanical_weapon,
        "mechanical_ammo": gear.mechanical_ammo,
        "armor": gear.armor,
        "melee_weapon": gear.melee_weapon,
        "weapon_upgrades": gear.weapon_upgrades,
        "weapon_quality": gear.weapon_quality,
        "weapon_usage": gear.weapon_usage,
        "weapon_provenance": _provenance_dict_to_save(gear.weapon_provenance),
    }


def _provenance_dict_to_save(prov_dict: dict) -> dict:
    """Serialize weapon provenance dict for save."""
    from portlight.engine.weapon_provenance import WeaponProvenance
    result = {}
    for wid, prov in prov_dict.items():
        if isinstance(prov, WeaponProvenance):
            result[wid] = {
                "weapon_id": prov.weapon_id,
                "acquired_port": prov.acquired_port,
                "acquired_day": prov.acquired_day,
                "acquired_region": prov.acquired_region,
                "kills": prov.kills,
                "named_kills": prov.named_kills,
                "epithet": prov.epithet,
                "custom_name": prov.custom_name,
                "times_recognized": prov.times_recognized,
            }
        else:
            result[wid] = prov  # already a dict
    return result


def _provenance_dict_from_save(data: dict) -> dict:
    """Deserialize weapon provenance from save."""
    from portlight.engine.weapon_provenance import WeaponProvenance
    result = {}
    for wid, pd in data.items():
        result[wid] = WeaponProvenance(
            weapon_id=pd.get("weapon_id", wid),
            acquired_port=pd.get("acquired_port", ""),
            acquired_day=pd.get("acquired_day", 0),
            acquired_region=pd.get("acquired_region", ""),
            kills=pd.get("kills", 0),
            named_kills=pd.get("named_kills", []),
            epithet=pd.get("epithet"),
            custom_name=pd.get("custom_name"),
            times_recognized=pd.get("times_recognized", 0),
        )
    return result


def _combat_gear_from_dict(d: dict) -> CombatGear:
    return CombatGear(
        firearm=d.get("firearm"),
        firearm_ammo=d.get("firearm_ammo", 0),
        throwing_weapons=d.get("throwing_weapons", {}),
        mechanical_weapon=d.get("mechanical_weapon"),
        mechanical_ammo=d.get("mechanical_ammo", 0),
        armor=d.get("armor"),
        melee_weapon=d.get("melee_weapon"),
        weapon_upgrades=d.get("weapon_upgrades", {}),
        weapon_quality=d.get("weapon_quality", {}),
        weapon_usage=d.get("weapon_usage", {}),
        weapon_provenance=_provenance_dict_from_save(d.get("weapon_provenance", {})),
    )


def _injury_to_dict(inj: ActiveInjury) -> dict:
    return {
        "injury_id": inj.injury_id,
        "acquired_day": inj.acquired_day,
        "heal_remaining": inj.heal_remaining,
        "treated": inj.treated,
    }


def _injury_from_dict(d: dict) -> ActiveInjury:
    return ActiveInjury(**d)


def _captain_to_dict(captain: Captain) -> dict:
    return {
        "name": captain.name,
        "captain_type": captain.captain_type,
        "silver": captain.silver,
        "reputation": captain.reputation,
        "ship": _ship_to_dict(captain.ship) if captain.ship else None,
        "cargo": [{
            "good_id": c.good_id, "quantity": c.quantity, "cost_basis": c.cost_basis,
            "acquired_port": c.acquired_port, "acquired_region": c.acquired_region,
            "acquired_day": c.acquired_day,
        } for c in captain.cargo],
        "provisions": captain.provisions,
        "day": captain.day,
        "standing": _reputation_to_dict(captain.standing),
        "learned_styles": captain.learned_styles,
        "active_style": captain.active_style,
        "combat_gear": _combat_gear_to_dict(captain.combat_gear),
        "injuries": [_injury_to_dict(i) for i in captain.injuries],
        "skills": captain.skills,
        "party": _party_to_dict(captain.party),
        "fleet": [_owned_ship_to_dict(o) for o in captain.fleet],
        "deferred_fees": captain.deferred_fees,
        "breach_records": captain.breach_records,
        "wanted_level": captain.wanted_level,
        "active_bounties": captain.active_bounties,
    }


def _party_to_dict(party_data) -> dict:
    """Serialize party state. Accepts either PartyState or raw dict."""
    from portlight.engine.companion_engine import PartyState
    if isinstance(party_data, PartyState):
        return {
            "companions": [
                {"companion_id": c.companion_id, "role_id": c.role_id,
                 "morale": c.morale, "joined_day": c.joined_day, "personality": c.personality}
                for c in party_data.companions
            ],
            "max_size": party_data.max_size,
            "departed": party_data.departed,
        }
    if isinstance(party_data, dict):
        return party_data  # already serialized
    return {"companions": [], "max_size": 2, "departed": []}


def _party_from_dict(d: dict):
    """Deserialize party state. Returns PartyState."""
    from portlight.engine.companion_engine import CompanionState, PartyState
    companions = [
        CompanionState(
            companion_id=c["companion_id"], role_id=c["role_id"],
            morale=c.get("morale", 70), joined_day=c.get("joined_day", 0),
            personality=c.get("personality", "pragmatic"),
        )
        for c in d.get("companions", [])
    ]
    return PartyState(
        companions=companions,
        max_size=d.get("max_size", 2),
        departed=d.get("departed", []),
    )


def _cargo_from_dict(c: dict) -> CargoItem:
    return CargoItem(
        good_id=c["good_id"], quantity=c["quantity"],
        cost_basis=c.get("cost_basis", 0),
        acquired_port=c.get("acquired_port", ""),
        acquired_region=c.get("acquired_region", ""),
        acquired_day=c.get("acquired_day", 0),
    )


def _captain_from_dict(d: dict) -> Captain:
    standing = _reputation_from_dict(d["standing"]) if "standing" in d else ReputationState()
    gear = _combat_gear_from_dict(d["combat_gear"]) if "combat_gear" in d else CombatGear()
    injuries = [_injury_from_dict(i) for i in d.get("injuries", [])]
    return Captain(
        name=d["name"],
        captain_type=d.get("captain_type", "merchant"),
        silver=d["silver"],
        reputation=d.get("reputation", 0),
        ship=_ship_from_dict(d["ship"]) if d.get("ship") else None,
        cargo=[_cargo_from_dict(c) for c in d.get("cargo", [])],
        provisions=d["provisions"],
        day=d["day"],
        standing=standing,
        learned_styles=d.get("learned_styles", []),
        active_style=d.get("active_style"),
        combat_gear=gear,
        injuries=injuries,
        skills=d.get("skills", {}),
        party=_party_to_dict(_party_from_dict(d.get("party", {}))) if "party" in d else {"companions": [], "max_size": 2, "departed": []},
        fleet=[_owned_ship_from_dict(o) for o in d.get("fleet", [])],
        deferred_fees=d.get("deferred_fees", []),
        breach_records=d.get("breach_records", []),
        wanted_level=d.get("wanted_level", 0),
        active_bounties=d.get("active_bounties", []),
    )


def _owned_ship_to_dict(owned: OwnedShip) -> dict:
    return {
        "ship": _ship_to_dict(owned.ship),
        "docked_port_id": owned.docked_port_id,
        "cargo": [{
            "good_id": c.good_id, "quantity": c.quantity, "cost_basis": c.cost_basis,
            "acquired_port": c.acquired_port, "acquired_region": c.acquired_region,
            "acquired_day": c.acquired_day,
        } for c in owned.cargo],
    }


def _owned_ship_from_dict(d: dict) -> OwnedShip:
    return OwnedShip(
        ship=_ship_from_dict(d["ship"]),
        docked_port_id=d["docked_port_id"],
        cargo=[_cargo_from_dict(c) for c in d.get("cargo", [])],
    )


def _slot_to_dict(slot: MarketSlot) -> dict:
    return {
        "good_id": slot.good_id,
        "stock_current": slot.stock_current,
        "stock_target": slot.stock_target,
        "restock_rate": slot.restock_rate,
        "local_affinity": slot.local_affinity,
        "spread": slot.spread,
        "buy_price": slot.buy_price,
        "sell_price": slot.sell_price,
        "flood_penalty": slot.flood_penalty,
    }


def _slot_from_dict(d: dict) -> MarketSlot:
    return MarketSlot(**d)


def _port_to_dict(port: Port) -> dict:
    return {
        "id": port.id,
        "name": port.name,
        "description": port.description,
        "region": port.region,
        "features": [f.value for f in port.features],
        "market": [_slot_to_dict(s) for s in port.market],
        "port_fee": port.port_fee,
        "provision_cost": port.provision_cost,
        "repair_cost": port.repair_cost,
        "crew_cost": port.crew_cost,
        "map_x": port.map_x,
        "map_y": port.map_y,
    }


def _port_from_dict(d: dict) -> Port:
    return Port(
        id=d["id"],
        name=d["name"],
        description=d["description"],
        region=d["region"],
        features=[PortFeature(f) for f in d.get("features", [])],
        market=[_slot_from_dict(s) for s in d.get("market", [])],
        port_fee=d.get("port_fee", 5),
        provision_cost=d.get("provision_cost", 2),
        repair_cost=d.get("repair_cost", 3),
        crew_cost=d.get("crew_cost", 5),
        map_x=d.get("map_x", 0),
        map_y=d.get("map_y", 0),
    )


def _voyage_to_dict(voyage: VoyageState) -> dict:
    return {
        "origin_id": voyage.origin_id,
        "destination_id": voyage.destination_id,
        "distance": voyage.distance,
        "progress": voyage.progress,
        "days_elapsed": voyage.days_elapsed,
        "status": voyage.status.value,
        "recent_events": voyage.recent_events,
    }


def _voyage_from_dict(d: dict) -> VoyageState:
    return VoyageState(
        origin_id=d["origin_id"],
        destination_id=d["destination_id"],
        distance=d["distance"],
        progress=d.get("progress", 0),
        days_elapsed=d.get("days_elapsed", 0),
        status=VoyageStatus(d["status"]),
        recent_events=d.get("recent_events", []),
    )


def _receipt_to_dict(r: TradeReceipt) -> dict:
    return {
        "receipt_id": r.receipt_id,
        "captain_name": r.captain_name,
        "port_id": r.port_id,
        "good_id": r.good_id,
        "action": r.action.value,
        "quantity": r.quantity,
        "unit_price": r.unit_price,
        "total_price": r.total_price,
        "day": r.day,
        "timestamp": r.timestamp,
        "stock_before": r.stock_before,
        "stock_after": r.stock_after,
    }


def _receipt_from_dict(d: dict) -> TradeReceipt:
    return TradeReceipt(
        receipt_id=d["receipt_id"],
        captain_name=d["captain_name"],
        port_id=d["port_id"],
        good_id=d["good_id"],
        action=TradeAction(d["action"]),
        quantity=d["quantity"],
        unit_price=d["unit_price"],
        total_price=d["total_price"],
        day=d["day"],
        timestamp=d.get("timestamp", ""),
        stock_before=d.get("stock_before", 0),
        stock_after=d.get("stock_after", 0),
    )


def _offer_to_dict(o: ContractOffer) -> dict:
    return {
        "id": o.id,
        "template_id": o.template_id,
        "family": o.family.value,
        "title": o.title,
        "description": o.description,
        "issuer_port_id": o.issuer_port_id,
        "destination_port_id": o.destination_port_id,
        "good_id": o.good_id,
        "quantity": o.quantity,
        "created_day": o.created_day,
        "deadline_day": o.deadline_day,
        "reward_silver": o.reward_silver,
        "bonus_reward": o.bonus_reward,
        "required_trust_tier": o.required_trust_tier,
        "required_standing": o.required_standing,
        "heat_ceiling": o.heat_ceiling,
        "inspection_modifier": o.inspection_modifier,
        "source_region": o.source_region,
        "source_port": o.source_port,
        "offer_reason": o.offer_reason,
        "tags": o.tags,
        "acceptance_window": o.acceptance_window,
    }


def _offer_from_dict(d: dict) -> ContractOffer:
    return ContractOffer(
        id=d["id"],
        template_id=d["template_id"],
        family=ContractFamily(d["family"]),
        title=d["title"],
        description=d["description"],
        issuer_port_id=d["issuer_port_id"],
        destination_port_id=d["destination_port_id"],
        good_id=d["good_id"],
        quantity=d["quantity"],
        created_day=d["created_day"],
        deadline_day=d["deadline_day"],
        reward_silver=d["reward_silver"],
        bonus_reward=d.get("bonus_reward", 0),
        required_trust_tier=d.get("required_trust_tier", "unproven"),
        required_standing=d.get("required_standing", 0),
        heat_ceiling=d.get("heat_ceiling"),
        inspection_modifier=d.get("inspection_modifier", 0.0),
        source_region=d.get("source_region"),
        source_port=d.get("source_port"),
        offer_reason=d.get("offer_reason", ""),
        tags=d.get("tags", []),
        acceptance_window=d.get("acceptance_window", 10),
    )


def _active_contract_to_dict(c: ActiveContract) -> dict:
    return {
        "offer_id": c.offer_id,
        "template_id": c.template_id,
        "family": c.family.value,
        "title": c.title,
        "accepted_day": c.accepted_day,
        "deadline_day": c.deadline_day,
        "destination_port_id": c.destination_port_id,
        "good_id": c.good_id,
        "required_quantity": c.required_quantity,
        "delivered_quantity": c.delivered_quantity,
        "reward_silver": c.reward_silver,
        "bonus_reward": c.bonus_reward,
        "source_region": c.source_region,
        "source_port": c.source_port,
        "inspection_modifier": c.inspection_modifier,
        "status": c.status.value,
    }


def _active_contract_from_dict(d: dict) -> ActiveContract:
    return ActiveContract(
        offer_id=d["offer_id"],
        template_id=d["template_id"],
        family=ContractFamily(d["family"]),
        title=d["title"],
        accepted_day=d["accepted_day"],
        deadline_day=d["deadline_day"],
        destination_port_id=d["destination_port_id"],
        good_id=d["good_id"],
        required_quantity=d["required_quantity"],
        delivered_quantity=d.get("delivered_quantity", 0),
        reward_silver=d.get("reward_silver", 0),
        bonus_reward=d.get("bonus_reward", 0),
        source_region=d.get("source_region"),
        source_port=d.get("source_port"),
        inspection_modifier=d.get("inspection_modifier", 0.0),
        status=ContractStatus(d.get("status", "accepted")),
    )


def _outcome_to_dict(o: ContractOutcome) -> dict:
    result = {
        "contract_id": o.contract_id,
        "outcome_type": o.outcome_type,
        "silver_delta": o.silver_delta,
        "trust_delta": o.trust_delta,
        "standing_delta": o.standing_delta,
        "heat_delta": o.heat_delta,
        "completion_day": o.completion_day,
        "summary": o.summary,
    }
    if o.family is not None:
        result["family"] = o.family.value
    return result


def _outcome_from_dict(d: dict) -> ContractOutcome:
    d = dict(d)  # don't mutate caller's dict
    raw_family = d.pop("family", None)
    family = ContractFamily(raw_family) if raw_family else None
    return ContractOutcome(**d, family=family)


def _board_to_dict(board: ContractBoard) -> dict:
    return {
        "offers": [_offer_to_dict(o) for o in board.offers],
        "active": [_active_contract_to_dict(c) for c in board.active],
        "completed": [_outcome_to_dict(o) for o in board.completed],
        "last_refresh_day": board.last_refresh_day,
        "max_offers": board.max_offers,
    }


def _board_from_dict(d: dict) -> ContractBoard:
    return ContractBoard(
        offers=[_offer_from_dict(o) for o in d.get("offers", [])],
        active=[_active_contract_from_dict(c) for c in d.get("active", [])],
        completed=[_outcome_from_dict(o) for o in d.get("completed", [])],
        last_refresh_day=d.get("last_refresh_day", 0),
        max_offers=d.get("max_offers", 5),
    )


def _stored_lot_to_dict(lot: StoredLot) -> dict:
    return {
        "good_id": lot.good_id,
        "quantity": lot.quantity,
        "acquired_port": lot.acquired_port,
        "acquired_region": lot.acquired_region,
        "acquired_day": lot.acquired_day,
        "deposited_day": lot.deposited_day,
    }


def _stored_lot_from_dict(d: dict) -> StoredLot:
    return StoredLot(**d)


def _warehouse_to_dict(w: WarehouseLease) -> dict:
    return {
        "id": w.id,
        "port_id": w.port_id,
        "tier": w.tier.value,
        "capacity": w.capacity,
        "lease_cost": w.lease_cost,
        "upkeep_per_day": w.upkeep_per_day,
        "inventory": [_stored_lot_to_dict(lot) for lot in w.inventory],
        "opened_day": w.opened_day,
        "upkeep_paid_through": w.upkeep_paid_through,
        "active": w.active,
    }


def _warehouse_from_dict(d: dict) -> WarehouseLease:
    return WarehouseLease(
        id=d["id"],
        port_id=d["port_id"],
        tier=WarehouseTier(d["tier"]),
        capacity=d["capacity"],
        lease_cost=d.get("lease_cost", 0),
        upkeep_per_day=d.get("upkeep_per_day", 1),
        inventory=[_stored_lot_from_dict(lot) for lot in d.get("inventory", [])],
        opened_day=d.get("opened_day", 0),
        upkeep_paid_through=d.get("upkeep_paid_through", 0),
        active=d.get("active", True),
    )


def _broker_to_dict(b: BrokerOffice) -> dict:
    return {
        "region": b.region,
        "tier": b.tier.value,
        "opened_day": b.opened_day,
        "upkeep_paid_through": b.upkeep_paid_through,
        "active": b.active,
    }


def _broker_from_dict(d: dict) -> BrokerOffice:
    return BrokerOffice(
        region=d["region"],
        tier=BrokerTier(d.get("tier", "none")),
        opened_day=d.get("opened_day", 0),
        upkeep_paid_through=d.get("upkeep_paid_through", 0),
        active=d.get("active", True),
    )


def _license_to_dict(lic: OwnedLicense) -> dict:
    return {
        "license_id": lic.license_id,
        "purchased_day": lic.purchased_day,
        "upkeep_paid_through": lic.upkeep_paid_through,
        "active": lic.active,
    }


def _license_from_dict(d: dict) -> OwnedLicense:
    return OwnedLicense(
        license_id=d["license_id"],
        purchased_day=d.get("purchased_day", 0),
        upkeep_paid_through=d.get("upkeep_paid_through", 0),
        active=d.get("active", True),
    )


def _policy_to_dict(p: ActivePolicy) -> dict:
    return {
        "id": p.id,
        "spec_id": p.spec_id,
        "family": p.family.value,
        "scope": p.scope.value,
        "purchased_day": p.purchased_day,
        "coverage_pct": p.coverage_pct,
        "coverage_cap": p.coverage_cap,
        "premium_paid": p.premium_paid,
        "target_id": p.target_id,
        "claims_made": p.claims_made,
        "total_paid_out": p.total_paid_out,
        "active": p.active,
        "voyage_origin": p.voyage_origin,
        "voyage_destination": p.voyage_destination,
    }


def _policy_from_dict(d: dict) -> ActivePolicy:
    return ActivePolicy(
        id=d["id"],
        spec_id=d["spec_id"],
        family=PolicyFamily(d["family"]),
        scope=PolicyScope(d["scope"]),
        purchased_day=d.get("purchased_day", 0),
        coverage_pct=d.get("coverage_pct", 0.5),
        coverage_cap=d.get("coverage_cap", 100),
        premium_paid=d.get("premium_paid", 0),
        target_id=d.get("target_id", ""),
        claims_made=d.get("claims_made", 0),
        total_paid_out=d.get("total_paid_out", 0),
        active=d.get("active", True),
        voyage_origin=d.get("voyage_origin", ""),
        voyage_destination=d.get("voyage_destination", ""),
    )


def _claim_to_dict(c: InsuranceClaim) -> dict:
    return {
        "policy_id": c.policy_id,
        "day": c.day,
        "incident_type": c.incident_type,
        "loss_value": c.loss_value,
        "payout": c.payout,
        "denied": c.denied,
        "denial_reason": c.denial_reason,
    }


def _claim_from_dict(d: dict) -> InsuranceClaim:
    return InsuranceClaim(**d)


def _credit_to_dict(c: CreditState) -> dict:
    return {
        "tier": c.tier.value,
        "credit_limit": c.credit_limit,
        "outstanding": c.outstanding,
        "interest_accrued": c.interest_accrued,
        "last_interest_day": c.last_interest_day,
        "next_due_day": c.next_due_day,
        "defaults": c.defaults,
        "total_borrowed": c.total_borrowed,
        "total_repaid": c.total_repaid,
        "active": c.active,
    }


def _credit_from_dict(d: dict) -> CreditState:
    return CreditState(
        tier=CreditTier(d.get("tier", "none")),
        credit_limit=d.get("credit_limit", 0),
        outstanding=d.get("outstanding", 0),
        interest_accrued=d.get("interest_accrued", 0),
        last_interest_day=d.get("last_interest_day", 0),
        next_due_day=d.get("next_due_day", 0),
        defaults=d.get("defaults", 0),
        total_borrowed=d.get("total_borrowed", 0),
        total_repaid=d.get("total_repaid", 0),
        active=d.get("active", False),
    )


def _infra_to_dict(state: InfrastructureState) -> dict:
    d = {
        "warehouses": [_warehouse_to_dict(w) for w in state.warehouses],
        "brokers": [_broker_to_dict(b) for b in state.brokers],
        "licenses": [_license_to_dict(lic) for lic in state.licenses],
        "policies": [_policy_to_dict(p) for p in state.policies],
        "claims": [_claim_to_dict(c) for c in state.claims],
    }
    if state.credit is not None:
        d["credit"] = _credit_to_dict(state.credit)
    return d


def _infra_from_dict(d: dict) -> InfrastructureState:
    credit = _credit_from_dict(d["credit"]) if d.get("credit") else None
    return InfrastructureState(
        warehouses=[_warehouse_from_dict(w) for w in d.get("warehouses", [])],
        brokers=[_broker_from_dict(b) for b in d.get("brokers", [])],
        licenses=[_license_from_dict(lic) for lic in d.get("licenses", [])],
        policies=[_policy_from_dict(p) for p in d.get("policies", [])],
        claims=[_claim_from_dict(c) for c in d.get("claims", [])],
        credit=credit,
    )


def _milestone_to_dict(m: MilestoneCompletion) -> dict:
    return {
        "milestone_id": m.milestone_id,
        "completed_day": m.completed_day,
        "evidence": m.evidence,
    }


def _milestone_from_dict(d: dict) -> MilestoneCompletion:
    return MilestoneCompletion(
        milestone_id=d["milestone_id"],
        completed_day=d.get("completed_day", 0),
        evidence=d.get("evidence", ""),
    )


def _victory_completion_to_dict(vc: "VictoryCompletion") -> dict:  # noqa: F821
    return {
        "path_id": vc.path_id,
        "completion_day": vc.completion_day,
        "summary": vc.summary,
        "is_first": vc.is_first,
    }


def _victory_completion_from_dict(d: dict) -> "VictoryCompletion":  # noqa: F821
    from portlight.engine.campaign import VictoryCompletion
    return VictoryCompletion(
        path_id=d["path_id"],
        completion_day=d.get("completion_day", 0),
        summary=d.get("summary", ""),
        is_first=d.get("is_first", False),
    )


def _campaign_to_dict(state: CampaignState) -> dict:
    return {
        "completed": [_milestone_to_dict(m) for m in state.completed],
        "completed_paths": [_victory_completion_to_dict(vc) for vc in state.completed_paths],
    }


def _campaign_from_dict(d: dict) -> CampaignState:
    return CampaignState(
        completed=[_milestone_from_dict(m) for m in d.get("completed", [])],
        completed_paths=[_victory_completion_from_dict(vc) for vc in d.get("completed_paths", [])],
    )


def _narrative_to_dict(state: NarrativeState) -> dict:
    return {
        "fired": list(state.fired),
        "journal": [
            {"beat_id": j.beat_id, "day": j.day, "port_id": j.port_id, "region": j.region}
            for j in state.journal
        ],
    }


def _narrative_from_dict(d: dict) -> NarrativeState:
    return NarrativeState(
        fired=d.get("fired", []),
        journal=[
            JournalEntry(
                beat_id=j["beat_id"], day=j.get("day", 0),
                port_id=j.get("port_id", ""), region=j.get("region", ""),
            )
            for j in d.get("journal", [])
        ],
    )


def _pirate_state_to_dict(state: PirateState) -> dict:
    result = {
        "encounters": [
            {"captain_id": e.captain_id, "faction_id": e.faction_id,
             "day": e.day, "outcome": e.outcome, "region": e.region}
            for e in state.encounters
        ],
        "nemesis_id": state.nemesis_id,
        "duels_won": state.duels_won,
        "duels_lost": state.duels_lost,
        "naval_victories": state.naval_victories,
        "naval_defeats": state.naval_defeats,
        "encounter_phase": state.encounter_phase,
        "encounter_state": state.encounter_state,
    }
    if state.pending_duel is not None:
        pd = state.pending_duel
        result["pending_duel"] = {
            "captain_id": pd.captain_id, "captain_name": pd.captain_name,
            "faction_id": pd.faction_id, "personality": pd.personality,
            "strength": pd.strength, "region": pd.region,
        }
    # Captain memories — serialize the CaptainMemory objects
    if state.captain_memories:
        from portlight.engine.captain_memory import CaptainMemory
        memories_dict = {}
        for cid, mem in state.captain_memories.items():
            if isinstance(mem, CaptainMemory):
                memories_dict[cid] = {
                    "captain_id": mem.captain_id,
                    "relationship": {
                        "respect": mem.relationship.respect,
                        "fear": mem.relationship.fear,
                        "grudge": mem.relationship.grudge,
                        "familiarity": mem.relationship.familiarity,
                    },
                    "encounters": [{
                        "day": e.day, "region": e.region, "outcome": e.outcome,
                        "player_spared": e.player_spared, "player_used_firearm": e.player_used_firearm,
                        "crew_killed": e.crew_killed, "respect_delta": e.respect_delta,
                        "fear_delta": e.fear_delta, "grudge_delta": e.grudge_delta,
                        "familiarity_delta": e.familiarity_delta,
                    } for e in mem.encounters],
                    "last_seen_day": mem.last_seen_day,
                    "last_seen_region": mem.last_seen_region,
                    "times_spared": mem.times_spared,
                    "times_defeated_by_player": mem.times_defeated_by_player,
                    "times_defeated_player": mem.times_defeated_player,
                    "player_sank_their_ship": mem.player_sank_their_ship,
                }
            else:
                memories_dict[cid] = mem  # already dict (raw load)
        result["captain_memories"] = memories_dict
    return result


def _pirate_state_from_dict(d: dict) -> PirateState:
    pd_data = d.get("pending_duel")
    pending = PendingDuel(**pd_data) if pd_data else None
    # Deserialize captain memories
    from portlight.engine.captain_memory import CaptainMemory, CaptainRelationship, EncounterMemory
    raw_memories = d.get("captain_memories", {})
    captain_memories = {}
    for cid, md in raw_memories.items():
        rel_d = md.get("relationship", {})
        captain_memories[cid] = CaptainMemory(
            captain_id=md.get("captain_id", cid),
            relationship=CaptainRelationship(
                respect=rel_d.get("respect", 0), fear=rel_d.get("fear", 0),
                grudge=rel_d.get("grudge", 0), familiarity=rel_d.get("familiarity", 0),
            ),
            encounters=[EncounterMemory(**e) for e in md.get("encounters", [])],
            last_seen_day=md.get("last_seen_day", 0),
            last_seen_region=md.get("last_seen_region", ""),
            times_spared=md.get("times_spared", 0),
            times_defeated_by_player=md.get("times_defeated_by_player", 0),
            times_defeated_player=md.get("times_defeated_player", 0),
            player_sank_their_ship=md.get("player_sank_their_ship", False),
        )
    return PirateState(
        encounters=[
            PirateEncounterRecord(
                captain_id=e["captain_id"], faction_id=e["faction_id"],
                day=e["day"], outcome=e["outcome"], region=e.get("region", ""),
            )
            for e in d.get("encounters", [])
        ],
        nemesis_id=d.get("nemesis_id"),
        duels_won=d.get("duels_won", 0),
        duels_lost=d.get("duels_lost", 0),
        naval_victories=d.get("naval_victories", 0),
        naval_defeats=d.get("naval_defeats", 0),
        pending_duel=pending,
        captain_memories=captain_memories,
        encounter_phase=d.get("encounter_phase", ""),
        encounter_state=d.get("encounter_state", {}),
    )


def _cultural_state_to_dict(state: CulturalState) -> dict:
    return {
        "active_festivals": [
            {"festival_id": af.festival_id, "port_id": af.port_id,
             "start_day": af.start_day, "end_day": af.end_day}
            for af in state.active_festivals
        ],
        "regions_entered": list(state.regions_entered),
        "cultural_encounters": state.cultural_encounters,
        "port_visits": dict(state.port_visits),
        "festivals_visited": state.festivals_visited,
    }


def _cultural_state_from_dict(d: dict) -> CulturalState:
    return CulturalState(
        active_festivals=[
            ActiveFestival(
                festival_id=af["festival_id"], port_id=af["port_id"],
                start_day=af["start_day"], end_day=af["end_day"],
            )
            for af in d.get("active_festivals", [])
        ],
        regions_entered=d.get("regions_entered", []),
        cultural_encounters=d.get("cultural_encounters", 0),
        port_visits=d.get("port_visits", {}),
        festivals_visited=d.get("festivals_visited", 0),
    )


def _ledger_to_dict(ledger: ReceiptLedger) -> dict:
    return {
        "run_id": ledger.run_id,
        "receipts": [_receipt_to_dict(r) for r in ledger.receipts],
        "total_buys": ledger.total_buys,
        "total_sells": ledger.total_sells,
        "net_profit": ledger.net_profit,
    }


def _ledger_from_dict(d: dict) -> ReceiptLedger:
    ledger = ReceiptLedger(
        run_id=d.get("run_id", ""),
        total_buys=d.get("total_buys", 0),
        total_sells=d.get("total_sells", 0),
        net_profit=d.get("net_profit", 0),
    )
    ledger.receipts = [_receipt_from_dict(r) for r in d.get("receipts", [])]
    return ledger


def world_to_dict(
    world: WorldState,
    ledger: ReceiptLedger | None = None,
    board: ContractBoard | None = None,
    infra: InfrastructureState | None = None,
    campaign: CampaignState | None = None,
    narrative: NarrativeState | None = None,
) -> dict:
    """Serialize full game state to a JSON-safe dict."""
    d = {
        "version": CURRENT_SAVE_VERSION,
        "captain": _captain_to_dict(world.captain),
        "ports": {pid: _port_to_dict(p) for pid, p in world.ports.items()},
        "routes": [{"port_a": r.port_a, "port_b": r.port_b, "distance": r.distance, "danger": r.danger, "min_ship_class": r.min_ship_class} for r in world.routes],
        "voyage": _voyage_to_dict(world.voyage) if world.voyage else None,
        "day": world.day,
        "seed": world.seed,
        "cultural_state": _cultural_state_to_dict(world.culture),
        "pirate_state": _pirate_state_to_dict(world.pirates),
        "ledger": _ledger_to_dict(ledger) if ledger else None,
        "contract_board": _board_to_dict(board) if board else None,
        "infrastructure": _infra_to_dict(infra) if infra else None,
    }
    if campaign is not None:
        d["campaign"] = _campaign_to_dict(campaign)
    if narrative is not None:
        d["narrative"] = _narrative_to_dict(narrative)
    return d


def world_from_dict(d: dict) -> tuple[WorldState, ReceiptLedger, ContractBoard, InfrastructureState, CampaignState, NarrativeState]:
    """Deserialize game state from dict. Returns (world, ledger, board, infra, campaign, narrative)."""
    culture = _cultural_state_from_dict(d["cultural_state"]) if d.get("cultural_state") else CulturalState()
    pirates = _pirate_state_from_dict(d["pirate_state"]) if d.get("pirate_state") else PirateState()
    world = WorldState(
        captain=_captain_from_dict(d["captain"]),
        ports={pid: _port_from_dict(p) for pid, p in d["ports"].items()},
        routes=[Route(**r) for r in d["routes"]],
        voyage=_voyage_from_dict(d["voyage"]) if d.get("voyage") else None,
        day=d["day"],
        seed=d.get("seed", 0),
        culture=culture,
        pirates=pirates,
    )
    ledger = _ledger_from_dict(d["ledger"]) if d.get("ledger") else ReceiptLedger()
    board = _board_from_dict(d["contract_board"]) if d.get("contract_board") else ContractBoard()
    infra = _infra_from_dict(d["infrastructure"]) if d.get("infrastructure") else InfrastructureState()
    campaign = _campaign_from_dict(d["campaign"]) if d.get("campaign") else CampaignState()
    narrative = _narrative_from_dict(d["narrative"]) if d.get("narrative") else NarrativeState()
    return world, ledger, board, infra, campaign, narrative


def save_game(
    world: WorldState,
    ledger: ReceiptLedger | None = None,
    board: ContractBoard | None = None,
    infra: InfrastructureState | None = None,
    campaign: CampaignState | None = None,
    narrative: NarrativeState | None = None,
    base_path: Path | None = None,
    slot: str = DEFAULT_SLOT,
) -> Path:
    """Save game state to JSON file. Returns path written."""
    base = base_path or Path(".")
    save_dir = base / SAVE_DIR
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / save_filename(slot)
    data = world_to_dict(world, ledger, board, infra, campaign, narrative)
    save_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return save_path


def load_game(
    base_path: Path | None = None,
    slot: str = DEFAULT_SLOT,
) -> tuple[WorldState, ReceiptLedger, ContractBoard, InfrastructureState, CampaignState, NarrativeState] | None:
    """Load game state from JSON file. Returns None if no save exists or data is corrupt."""
    base = base_path or Path(".")
    save_dir = base / SAVE_DIR
    save_path = save_dir / save_filename(slot)

    # Auto-migrate legacy single-file save to default slot
    if not save_path.exists() and slot == DEFAULT_SLOT:
        legacy_path = save_dir / SAVE_FILE
        if legacy_path.exists():
            legacy_path.rename(save_path)

    if not save_path.exists():
        return None
    try:
        data = json.loads(save_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    try:
        data = migrate_save(data)
        return world_from_dict(data)
    except SaveVersionError:
        raise  # let version errors surface with their descriptive message
    except (KeyError, TypeError, ValueError):
        return None
