"""Expanded ship catalog — 5 classes, each changes the game shape.

Sloop: fast, fragile, small hold. Mediterranean-safe. Gets punished on long hauls.
Cutter: nimble scout with moderate hold. Opens early cross-region runs.
  Fast enough to outrun pirates. Good crew-to-speed ratio.
Brigantine: balanced workhorse. Opens West Africa reliably and East Indies hub.
  More cargo = bulk routes viable. Higher crew = real wage pressure.
Galleon: slow fortress. Makes long-haul luxury profitable.
  Huge hold but expensive crew, slow speed means more provisions burned.
  Storm-resistant — the only ship that can reliably survive perilous routes.
Man-of-War: endgame capital ship. Massive hold, maximum storm resistance.
  Eye-watering crew costs but opens every route in the game.
  For the captain who has truly built an empire.
"""

from portlight.engine.models import ShipClass, ShipTemplate, UPGRADE_SLOTS

SHIPS: dict[str, ShipTemplate] = {s.id: s for s in [
    ShipTemplate(
        id="coastal_sloop",
        name="Coastal Sloop",
        ship_class=ShipClass.SLOOP,
        cargo_capacity=30,
        speed=8,
        hull_max=60,
        crew_min=3,
        crew_max=8,
        price=0,  # starting ship
        daily_wage=1,
        storm_resist=0.0,
        cannons=0,          # no guns — must board to fight
        maneuver=0.9,       # extremely nimble
    ),
    ShipTemplate(
        id="swift_cutter",
        name="Swift Cutter",
        ship_class=ShipClass.CUTTER,
        cargo_capacity=50,
        speed=9,            # fastest ship in the game
        hull_max=70,
        crew_min=5,
        crew_max=12,
        price=450,
        daily_wage=1,
        storm_resist=0.15,  # modest storm protection
        cannons=2,          # light armament
        maneuver=0.8,       # fast and agile
    ),
    ShipTemplate(
        id="trade_brigantine",
        name="Trade Brigantine",
        ship_class=ShipClass.BRIGANTINE,
        cargo_capacity=80,
        speed=6,
        hull_max=100,
        crew_min=8,
        crew_max=20,
        price=800,
        daily_wage=2,
        storm_resist=0.3,  # absorbs 30% storm damage
        cannons=6,          # broadside capable
        maneuver=0.5,       # balanced
    ),
    ShipTemplate(
        id="merchant_galleon",
        name="Merchant Galleon",
        ship_class=ShipClass.GALLEON,
        cargo_capacity=150,
        speed=4,
        hull_max=160,
        crew_min=15,
        crew_max=40,
        price=2200,
        daily_wage=3,
        storm_resist=0.6,  # absorbs 60% storm damage
        cannons=12,         # heavy broadside
        maneuver=0.3,       # sluggish
    ),
    ShipTemplate(
        id="royal_man_of_war",
        name="Royal Man-of-War",
        ship_class=ShipClass.MAN_OF_WAR,
        cargo_capacity=200,
        speed=3,
        hull_max=220,
        crew_min=25,
        crew_max=60,
        price=5000,
        daily_wage=4,
        storm_resist=0.8,  # near-invulnerable to storms
        cannons=20,         # devastating firepower
        maneuver=0.2,       # nearly immobile
    ),
]}


def create_ship_from_template(template: ShipTemplate, name: str | None = None) -> "Ship":  # noqa: F821
    """Instantiate a Ship from a template."""
    from portlight.engine.models import CrewRoster, Ship
    return Ship(
        template_id=template.id,
        name=name or template.name,
        hull=template.hull_max,
        hull_max=template.hull_max,
        cargo_capacity=template.cargo_capacity,
        speed=template.speed,
        crew=template.crew_min,
        crew_max=template.crew_max,
        cannons=template.cannons,
        maneuver=template.maneuver,
        upgrade_slots=UPGRADE_SLOTS.get(template.ship_class, 2),
        roster=CrewRoster(sailors=template.crew_min),
    )
