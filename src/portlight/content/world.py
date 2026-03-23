"""World factory — assembles a fresh WorldState from content data."""

from __future__ import annotations

import copy
import time

from portlight.content.goods import GOODS
from portlight.content.ports import PORTS
from portlight.content.routes import ROUTES
from portlight.content.ships import SHIPS, create_ship_from_template
from portlight.engine.captain_identity import CAPTAIN_TEMPLATES, CaptainType
from portlight.engine.economy import recalculate_prices
from portlight.engine.models import Captain, ReputationState, VoyageState, VoyageStatus, WorldState


def new_game(
    captain_name: str = "Captain",
    starting_port: str | None = None,
    captain_type: CaptainType = CaptainType.MERCHANT,
    seed: int | None = None,
) -> WorldState:
    """Create a fresh game world with initial market prices computed.

    If starting_port is None, uses the captain template's home port.
    If seed is None, uses current time.
    """
    template = CAPTAIN_TEMPLATES[captain_type]

    ports = copy.deepcopy(PORTS)
    routes = list(ROUTES)

    # Starting ship from template
    ship_template = SHIPS[template.starting_ship_id]
    ship = create_ship_from_template(ship_template)

    # Build reputation from template's reputation seed
    # (renamed to rep_seed to avoid shadowing the seed parameter)
    rep_seed = template.reputation_seed
    standing = ReputationState(
        regional_standing={
            "Mediterranean": rep_seed.mediterranean,
            "North Atlantic": rep_seed.north_atlantic,
            "West Africa": rep_seed.west_africa,
            "East Indies": rep_seed.east_indies,
            "South Seas": rep_seed.south_seas,
        },
        port_standing={},
        customs_heat={
            "Mediterranean": rep_seed.customs_heat,
            "North Atlantic": rep_seed.customs_heat,
            "West Africa": rep_seed.customs_heat,
            "East Indies": rep_seed.customs_heat,
            "South Seas": rep_seed.customs_heat,
        },
        commercial_trust=rep_seed.commercial_trust,
        underworld_standing=dict(rep_seed.underworld) if rep_seed.underworld else {},
    )

    port_id = starting_port or template.home_port_id

    captain = Captain(
        name=captain_name,
        captain_type=captain_type.value,
        silver=template.starting_silver,
        ship=ship,
        provisions=template.starting_provisions,
        standing=standing,
    )

    world = WorldState(
        captain=captain,
        ports=ports,
        routes=routes,
        voyage=VoyageState(
            origin_id=port_id,
            destination_id=port_id,
            distance=0,
            status=VoyageStatus.IN_PORT,
        ),
        day=1,
        seed=seed if seed is not None else int(time.time()),
    )

    # Compute initial prices
    for port in world.ports.values():
        recalculate_prices(port, GOODS)

    return world
