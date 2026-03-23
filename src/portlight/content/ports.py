"""Expanded port network — 20 ports across 5 regions.

Phase 1: 10 ports, 3 regions (Mediterranean, West Africa, East Indies)
Phase 2: +10 ports, +2 regions (North Atlantic, South Seas)

Each port has:
  - Clear export/import identity (affinity-driven)
  - Variable provisioning cost (cheap at farming ports, expensive at luxury hubs)
  - Variable repair cost (cheap at shipyard ports, expensive elsewhere)
  - Variable crew cost (cheap at large ports, expensive at remote ones)

Market design goals:
  - Every port trades 7-10 goods so players rarely hear "doesn't trade X"
  - Pelts tradeable at most ports (hunting should always yield sellable goods)
  - Export affinity 1.3-1.7 (cheap to buy), import affinity 0.5-0.65 (expensive = good sell target)
  - 1-2 "desperate" goods per port at 0.4-0.45 affinity for high-margin opportunities
  - Clear buy-here / sell-there routes between adjacent ports

Port identity should be readable in one glance from the market screen.
"""

from portlight.engine.models import MarketSlot, Port, PortFeature


def _slot(good_id: str, stock: int, target: int, restock: float, affinity: float = 1.0, spread: float = 0.15) -> MarketSlot:
    return MarketSlot(good_id=good_id, stock_current=stock, stock_target=target, restock_rate=restock, local_affinity=affinity, spread=spread)


PORTS: dict[str, Port] = {p.id: p for p in [
    # =========================================================================
    # MEDITERRANEAN (4 ports)
    # =========================================================================
    Port(
        id="porto_novo", name="Porto Novo", region="Mediterranean",
        description="A bustling harbor city, gateway to inland trade. Grain ships fill the docks.",
        features=[PortFeature.SHIPYARD],
        market=[
            _slot("grain",  40, 35, 3.0, affinity=1.4),   # EXPORTS grain
            _slot("timber", 20, 25, 2.0, affinity=0.8),
            _slot("iron",   15, 15, 1.5, affinity=1.0),
            _slot("cotton", 10, 12, 1.0, affinity=0.6),   # WANTS cotton
            _slot("rum",    18, 20, 1.5, affinity=1.1),
            _slot("dyes",   8,  10, 1.0, affinity=0.6),   # WANTS dyes for textiles
            _slot("pelts",  8,  10, 1.0, affinity=0.8),   # buys pelts (leather trade)
            _slot("porcelain", 4, 6, 0.5, affinity=0.55), # WANTS porcelain
        ],
        port_fee=5,
        provision_cost=1,
        repair_cost=2,
        crew_cost=4,
        map_x=18, map_y=8,
    ),
    Port(
        id="al_manar", name="Al-Manar", region="Mediterranean",
        description="Ancient port famed for its spice markets. Merchants bid fiercely for grain and iron.",
        market=[
            _slot("spice",  30, 25, 2.5, affinity=1.5),   # EXPORTS spice
            _slot("silk",   8,  10, 1.0, affinity=0.9),
            _slot("grain",  10, 15, 1.5, affinity=0.5),   # WANTS grain badly
            _slot("porcelain", 5, 8, 0.8, affinity=0.55), # WANTS porcelain
            _slot("rum",    12, 15, 1.0, affinity=0.7),
            _slot("tea",    6,  8,  0.8, affinity=0.6),
            _slot("medicines", 10, 12, 1.0, affinity=1.1),
            _slot("iron",   5,  8,  0.8, affinity=0.55),  # WANTS iron
            _slot("pelts",  5,  8,  0.8, affinity=0.7),   # buys pelts
        ],
        port_fee=8,
        provision_cost=3,
        repair_cost=4,
        crew_cost=6,
        map_x=24, map_y=6,
    ),
    Port(
        id="silva_bay", name="Silva Bay", region="Mediterranean",
        description="Timber-rich bay surrounded by dense forests. The shipwrights here are the best in the region.",
        features=[PortFeature.SHIPYARD],
        market=[
            _slot("timber", 45, 40, 3.5, affinity=1.6),   # EXPORTS timber (best source)
            _slot("iron",   20, 18, 2.0, affinity=1.3),   # EXPORTS iron
            _slot("grain",  15, 18, 1.5, affinity=0.9),
            _slot("cotton", 8,  10, 1.0, affinity=0.6),   # WANTS cotton
            _slot("weapons", 5, 8,  0.8, affinity=0.55),  # WANTS weapons
            _slot("pelts",  12, 10, 1.5, affinity=1.3),   # EXPORTS pelts (forest trapping)
            _slot("rum",    8,  10, 1.0, affinity=0.7),
            _slot("silk",   3,  5,  0.5, affinity=0.5),   # WANTS silk
        ],
        port_fee=4,
        provision_cost=2,
        repair_cost=1,
        crew_cost=5,
        map_x=14, map_y=10,
    ),
    Port(
        id="corsairs_rest", name="Corsair's Rest", region="Mediterranean",
        description="A lawless harbor tucked between cliffs. Smugglers, pirates, and those who trade with them.",
        features=[PortFeature.BLACK_MARKET],
        market=[
            _slot("weapons", 25, 20, 2.5, affinity=1.5),  # EXPORTS weapons
            _slot("rum",     30, 25, 3.0, affinity=1.5),   # EXPORTS rum
            _slot("tobacco", 20, 18, 2.0, affinity=1.3),   # EXPORTS tobacco
            _slot("silk",    3,  5,  0.5, affinity=0.5),   # WANTS silk
            _slot("medicines", 4, 6, 0.5, affinity=0.5),   # WANTS medicines
            _slot("pelts",   10, 8,  1.0, affinity=1.1),   # trades pelts
            _slot("grain",   8,  10, 1.0, affinity=0.7),
            # === Contraband ===
            _slot("black_powder", 8, 6, 0.5, affinity=1.3),
            _slot("stolen_cargo", 12, 10, 1.0, affinity=1.2),
            _slot("opium",        3, 4, 0.3, affinity=0.7),
        ],
        port_fee=3,
        provision_cost=2,
        repair_cost=3,
        crew_cost=2,
        map_x=21, map_y=13,
    ),

    # =========================================================================
    # NORTH ATLANTIC (3 ports)
    # =========================================================================
    Port(
        id="ironhaven", name="Ironhaven", region="North Atlantic",
        description="Industrial port city wreathed in forge smoke. Weapons and iron flow out, everything else flows in.",
        features=[PortFeature.SHIPYARD],
        market=[
            _slot("iron",    50, 45, 4.0, affinity=1.7),   # EXPORTS iron (best)
            _slot("weapons", 35, 30, 3.0, affinity=1.6),   # EXPORTS weapons
            _slot("timber",  15, 18, 1.5, affinity=0.8),
            _slot("grain",   10, 15, 1.0, affinity=0.55),  # WANTS grain
            _slot("cotton",  8,  12, 1.0, affinity=0.5),   # WANTS cotton
            _slot("tobacco", 12, 15, 1.0, affinity=0.9),
            _slot("pelts",   10, 12, 1.5, affinity=1.2),   # EXPORTS pelts (northern fur)
            _slot("silk",    3,  5,  0.5, affinity=0.45),   # WANTS silk badly
            _slot("rum",     5,  8,  0.8, affinity=0.6),
        ],
        port_fee=6,
        provision_cost=2,
        repair_cost=1,
        crew_cost=4,
        map_x=8, map_y=4,
    ),
    Port(
        id="stormwall", name="Stormwall", region="North Atlantic",
        description="Fortress port guarding the northern straits. Military outpost with strict inspections.",
        market=[
            _slot("weapons", 15, 18, 1.5, affinity=1.1),
            _slot("grain",   20, 22, 2.0, affinity=1.1),
            _slot("timber",  18, 20, 1.5, affinity=1.0),
            _slot("medicines", 15, 12, 1.5, affinity=1.4), # EXPORTS medicines
            _slot("rum",     10, 12, 1.0, affinity=0.5),   # WANTS rum badly
            _slot("tobacco", 8,  10, 0.8, affinity=0.55),  # WANTS tobacco
            _slot("pelts",   8,  10, 1.0, affinity=0.8),   # buys pelts
            _slot("silk",    3,  5,  0.5, affinity=0.5),
        ],
        port_fee=10,
        provision_cost=2,
        repair_cost=2,
        crew_cost=3,
        map_x=4, map_y=8,
    ),
    Port(
        id="thornport", name="Thornport", region="North Atlantic",
        description="Whaling town turned trading post. Tea and tobacco are the local currency. Medicines fetch gold.",
        market=[
            _slot("tea",      25, 22, 2.5, affinity=1.5),  # EXPORTS tea
            _slot("tobacco",  30, 25, 3.0, affinity=1.6),  # EXPORTS tobacco
            _slot("timber",   20, 18, 2.0, affinity=1.2),
            _slot("pelts",    18, 15, 2.0, affinity=1.5),  # EXPORTS pelts (whaling)
            _slot("medicines", 5, 8,  0.8, affinity=0.45), # WANTS medicines badly
            _slot("silk",     3,  5,  0.5, affinity=0.5),
            _slot("spice",    4,  6,  0.6, affinity=0.5),
            _slot("porcelain", 2, 4,  0.3, affinity=0.5),
        ],
        port_fee=5,
        provision_cost=1,
        repair_cost=3,
        crew_cost=3,
        map_x=11, map_y=10,
    ),

    # =========================================================================
    # WEST AFRICA (4 ports)
    # =========================================================================
    Port(
        id="sun_harbor", name="Sun Harbor", region="West Africa",
        description="Golden coast port where cotton bales stack higher than the warehouses.",
        market=[
            _slot("cotton", 35, 30, 3.0, affinity=1.5),   # EXPORTS cotton (best)
            _slot("iron",   25, 22, 2.0, affinity=1.3),   # EXPORTS iron
            _slot("dyes",   20, 18, 2.0, affinity=1.4),   # EXPORTS dyes
            _slot("pelts",  15, 12, 2.0, affinity=1.4),   # EXPORTS pelts (savanna)
            _slot("silk",   3,  5,  0.5, affinity=0.5),   # WANTS silk
            _slot("spice",  5,  8,  0.8, affinity=0.5),   # WANTS spice
            _slot("rum",    10, 12, 1.0, affinity=0.8),
            _slot("porcelain", 3, 5, 0.5, affinity=0.55),
        ],
        port_fee=5,
        provision_cost=2,
        repair_cost=4,
        crew_cost=3,
        map_x=14, map_y=22,
    ),
    Port(
        id="palm_cove", name="Palm Cove", region="West Africa",
        description="A sheltered cove where rum barrels outnumber the inhabitants. Cheapest provisions on the coast.",
        market=[
            _slot("rum",     40, 35, 3.0, affinity=1.7),  # EXPORTS rum (best)
            _slot("grain",   12, 15, 1.5, affinity=0.7),
            _slot("timber",  8,  10, 1.0, affinity=0.6),  # WANTS timber
            _slot("cotton",  15, 18, 1.5, affinity=1.1),
            _slot("tobacco", 18, 15, 2.0, affinity=1.3),  # EXPORTS tobacco
            _slot("pelts",   8,  10, 1.0, affinity=0.9),  # buys pelts
            _slot("silk",    3,  5,  0.5, affinity=0.5),
            _slot("iron",    5,  8,  0.8, affinity=0.6),
        ],
        port_fee=3,
        provision_cost=1,
        repair_cost=5,
        crew_cost=3,
        map_x=10, map_y=26,
    ),
    Port(
        id="iron_point", name="Iron Point", region="West Africa",
        description="Mining settlement at the river mouth. Iron flows out, everything else flows in at a premium.",
        market=[
            _slot("iron",   50, 45, 4.0, affinity=1.7),   # EXPORTS iron
            _slot("grain",  8,  12, 1.0, affinity=0.5),   # WANTS grain
            _slot("timber", 12, 15, 1.5, affinity=0.8),
            _slot("porcelain", 2, 4, 0.5, affinity=0.55),
            _slot("weapons", 8, 10, 1.0, affinity=0.6),
            _slot("rum",    5,  8,  0.8, affinity=0.6),
            _slot("medicines", 3, 5, 0.5, affinity=0.5),
            _slot("pelts",  6,  8,  1.0, affinity=0.9),
        ],
        port_fee=4,
        provision_cost=3,
        repair_cost=3,
        crew_cost=4,
        map_x=18, map_y=24,
    ),
    Port(
        id="pearl_shallows", name="Pearl Shallows", region="West Africa",
        description="Divers bring up pearls from the warm shallows. A quiet port where fortunes are made by the patient.",
        market=[
            _slot("pearls",  15, 12, 1.5, affinity=1.7),  # EXPORTS pearls
            _slot("cotton",  20, 18, 2.0, affinity=1.2),
            _slot("dyes",    15, 12, 1.5, affinity=1.4),   # EXPORTS dyes
            _slot("medicines", 3, 5, 0.5, affinity=0.45),  # WANTS medicines badly
            _slot("grain",   10, 12, 1.0, affinity=0.7),
            _slot("silk",    3,  5,  0.5, affinity=0.5),
            _slot("pelts",   8, 10, 1.0, affinity=1.0),
            _slot("rum",     6,  8, 0.8, affinity=0.7),
        ],
        port_fee=4,
        provision_cost=2,
        repair_cost=4,
        crew_cost=4,
        map_x=12, map_y=30,
    ),

    # =========================================================================
    # EAST INDIES (6 ports)
    # =========================================================================
    Port(
        id="jade_port", name="Jade Port", region="East Indies",
        description="Porcelain workshops line the waterfront. Iron and grain are worth their weight in gold here.",
        market=[
            _slot("porcelain", 35, 30, 3.0, affinity=1.6),  # EXPORTS porcelain
            _slot("silk",   25, 22, 2.5, affinity=1.3),     # EXPORTS silk
            _slot("tea",    20, 18, 2.0, affinity=1.3),     # EXPORTS tea
            _slot("spice",  15, 18, 1.5, affinity=1.1),
            _slot("grain",  5,  8,  0.8, affinity=0.5),     # WANTS grain
            _slot("iron",   3,  5,  0.5, affinity=0.5),     # WANTS iron
            _slot("rum",    6,  8,  0.8, affinity=0.6),     # WANTS rum
            _slot("pelts",  4,  6,  0.8, affinity=0.7),     # buys pelts
            _slot("cotton", 5,  8,  0.8, affinity=0.6),     # WANTS cotton
        ],
        port_fee=10,
        provision_cost=3,
        repair_cost=3,
        crew_cost=7,
        map_x=34, map_y=10,
    ),
    Port(
        id="monsoon_reach", name="Monsoon Reach", region="East Indies",
        description="Seasonal winds funnel the spice trade through this crossroads. The shipyard builds for endurance.",
        features=[PortFeature.SHIPYARD],
        market=[
            _slot("spice",  25, 22, 2.5, affinity=1.4),   # EXPORTS spice
            _slot("silk",   20, 18, 2.0, affinity=1.2),   # EXPORTS silk
            _slot("cotton", 5,  8,  0.8, affinity=0.5),   # WANTS cotton
            _slot("timber", 5,  8,  0.8, affinity=0.45),   # WANTS timber badly
            _slot("rum",    8,  10, 1.0, affinity=0.6),
            _slot("medicines", 8, 10, 1.0, affinity=0.9),
            _slot("grain",  6,  10, 1.0, affinity=0.6),
            _slot("porcelain", 8, 10, 1.0, affinity=0.8),
            _slot("pelts",  5,  8,  0.8, affinity=0.8),
        ],
        port_fee=8,
        provision_cost=2,
        repair_cost=2,
        crew_cost=6,
        map_x=38, map_y=14,
    ),
    Port(
        id="silk_haven", name="Silk Haven", region="East Indies",
        description="Premier silk market of the eastern waters. Rum and iron are scarce luxuries here.",
        market=[
            _slot("silk",   40, 35, 3.5, affinity=1.7),   # EXPORTS silk (best)
            _slot("porcelain", 15, 12, 1.5, affinity=1.2),
            _slot("spice",  10, 12, 1.0, affinity=0.9),
            _slot("rum",    5,  8,  0.8, affinity=0.45),   # WANTS rum badly
            _slot("dyes",   3,  5,  0.5, affinity=0.5),
            _slot("iron",   3,  5,  0.5, affinity=0.5),
            _slot("cotton", 5,  8,  0.8, affinity=0.55),
            _slot("grain",  4,  6,  0.5, affinity=0.55),
            _slot("pelts",  3,  5,  0.5, affinity=0.6),
        ],
        port_fee=7,
        provision_cost=3,
        repair_cost=5,
        crew_cost=8,
        map_x=42, map_y=8,
    ),
    Port(
        id="crosswind_isle", name="Crosswind Isle", region="East Indies",
        description="Free port at the junction of all trade winds. Everything passes through, nothing stays cheap.",
        features=[PortFeature.SAFE_HARBOR],
        market=[
            _slot("grain",  15, 15, 1.5, affinity=1.0),
            _slot("timber", 12, 12, 1.2, affinity=1.0),
            _slot("iron",   10, 10, 1.0, affinity=1.0),
            _slot("cotton", 10, 10, 1.0, affinity=1.0),
            _slot("spice",  10, 10, 1.0, affinity=1.0),
            _slot("silk",   8,  8,  0.8, affinity=1.0),
            _slot("rum",    10, 10, 1.0, affinity=1.0),
            _slot("porcelain", 6, 6, 0.6, affinity=1.0),
            _slot("tea",    8,  8,  0.8, affinity=1.0),
            _slot("pelts",  6,  8,  1.0, affinity=0.9),
            _slot("tobacco", 8, 8,  0.8, affinity=1.0),
        ],
        port_fee=6,
        provision_cost=2,
        repair_cost=3,
        crew_cost=5,
        map_x=32, map_y=16,
    ),
    Port(
        id="dragons_gate", name="Dragon's Gate", region="East Indies",
        description="Fortress harbor controlling the eastern straits. Weapons are contraband here, but medicines are gold.",
        market=[
            _slot("tea",       30, 25, 3.0, affinity=1.5),  # EXPORTS tea
            _slot("porcelain", 20, 18, 2.0, affinity=1.3),
            _slot("medicines", 3,  5,  0.5, affinity=0.4),  # WANTS medicines desperately
            _slot("iron",      5,  8,  0.8, affinity=0.5),
            _slot("tobacco",   4,  6,  0.5, affinity=0.5),
            _slot("rum",       6,  8,  0.8, affinity=0.6),
            _slot("cotton",    5,  8,  0.8, affinity=0.65),
            _slot("pelts",     4,  6,  0.5, affinity=0.7),
        ],
        port_fee=9,
        provision_cost=2,
        repair_cost=3,
        crew_cost=7,
        map_x=44, map_y=12,
    ),
    Port(
        id="spice_narrows", name="Spice Narrows", region="East Indies",
        description="Hidden anchorage in the spice archipelago. The most concentrated spice market in the world.",
        features=[PortFeature.BLACK_MARKET],
        market=[
            _slot("spice",    45, 40, 4.0, affinity=1.8),  # EXPORTS spice (best)
            _slot("pearls",   8,  6,  1.0, affinity=1.3),
            _slot("silk",     10, 12, 1.0, affinity=0.9),
            _slot("weapons",  3,  5,  0.5, affinity=0.5),
            _slot("grain",    5,  8,  0.5, affinity=0.5),
            _slot("rum",      6,  8,  0.8, affinity=0.6),
            _slot("pelts",    5,  6,  0.8, affinity=0.8),
            # === Contraband ===
            _slot("opium",        10, 8, 0.5, affinity=1.4),
            _slot("stolen_cargo", 8, 6, 0.8, affinity=1.0),
            _slot("black_powder", 3, 4, 0.3, affinity=0.6),
        ],
        port_fee=5,
        provision_cost=3,
        repair_cost=5,
        crew_cost=6,
        map_x=38, map_y=20,
    ),

    # =========================================================================
    # SOUTH SEAS (3 ports)
    # =========================================================================
    Port(
        id="ember_isle", name="Ember Isle", region="South Seas",
        description="Volcanic island with obsidian beaches. Rich in rare minerals and medicinal plants.",
        market=[
            _slot("medicines", 25, 20, 2.5, affinity=1.6),  # EXPORTS medicines
            _slot("dyes",      20, 18, 2.0, affinity=1.5),  # EXPORTS dyes
            _slot("iron",      15, 12, 1.5, affinity=1.2),
            _slot("grain",     5,  8,  0.5, affinity=0.5),
            _slot("timber",    5,  8,  0.5, affinity=0.5),
            _slot("weapons",   3,  5,  0.5, affinity=0.5),
            _slot("rum",       5,  8,  0.8, affinity=0.6),
            _slot("pelts",     5,  8,  0.8, affinity=0.7),
            _slot("cotton",    4,  6,  0.5, affinity=0.55),
        ],
        port_fee=6,
        provision_cost=2,
        repair_cost=4,
        crew_cost=5,
        map_x=34, map_y=28,
    ),
    Port(
        id="typhoon_anchorage", name="Typhoon Anchorage", region="South Seas",
        description="Storm-battered harbor that only the boldest captains visit. Pearls and rare goods reward the brave.",
        features=[PortFeature.SHIPYARD],
        market=[
            _slot("pearls",    20, 15, 2.0, affinity=1.7),  # EXPORTS pearls (best)
            _slot("timber",    25, 22, 2.5, affinity=1.4),   # EXPORTS timber
            _slot("spice",     12, 10, 1.5, affinity=1.2),
            _slot("silk",      3,  5,  0.5, affinity=0.45),  # WANTS silk badly
            _slot("porcelain", 2,  4,  0.5, affinity=0.45),  # WANTS porcelain badly
            _slot("medicines", 8,  10, 1.0, affinity=0.8),
            _slot("rum",       5,  8,  0.8, affinity=0.6),
            _slot("pelts",     6,  8,  1.0, affinity=0.9),
            _slot("grain",     4,  6,  0.5, affinity=0.55),
        ],
        port_fee=4,
        provision_cost=1,
        repair_cost=2,
        crew_cost=4,
        map_x=40, map_y=30,
    ),
    Port(
        id="coral_throne", name="Coral Throne", region="South Seas",
        description="Island kingdom built on coral reefs. The king trades pearls for weapons and demands tribute in silk.",
        market=[
            _slot("pearls",    12, 10, 1.5, affinity=1.5),  # EXPORTS pearls
            _slot("tobacco",   20, 18, 2.0, affinity=1.4),  # EXPORTS tobacco
            _slot("rum",       18, 15, 2.0, affinity=1.3),
            _slot("weapons",   2,  4,  0.3, affinity=0.4),  # WANTS weapons desperately
            _slot("silk",      2,  4,  0.3, affinity=0.4),  # WANTS silk desperately
            _slot("tea",       3,  5,  0.5, affinity=0.5),
            _slot("grain",     4,  6,  0.5, affinity=0.55),
            _slot("pelts",     5,  8,  0.8, affinity=0.7),
            _slot("porcelain", 2,  4,  0.3, affinity=0.45),
        ],
        port_fee=7,
        provision_cost=1,
        repair_cost=4,
        crew_cost=5,
        map_x=44, map_y=26,
    ),
]}
