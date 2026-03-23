"""Goods catalog — 17 tradeable goods across 6 categories.

Phase 1: 8 goods (grain, timber, iron, cotton, spice, silk, rum, porcelain)
Phase 2: +6 goods (tea, tobacco, dyes, pearls, weapons, medicines)
Phase 3: +3 contraband (opium, black_powder, stolen_cargo)

Contraband goods are only tradeable at BLACK_MARKET ports.
They carry extreme inspection risk but massive margins.
"""

from portlight.engine.models import Good, GoodCategory

GOODS: dict[str, Good] = {g.id: g for g in [
    # === Commodities ===
    Good("grain",     "Grain",         GoodCategory.COMMODITY,  base_price=12),
    Good("timber",    "Timber",        GoodCategory.COMMODITY,  base_price=18),
    Good("iron",      "Iron Ore",      GoodCategory.COMMODITY,  base_price=25),
    Good("cotton",    "Cotton",        GoodCategory.COMMODITY,  base_price=15),
    Good("dyes",      "Dyes",          GoodCategory.COMMODITY,  base_price=22),

    # === Luxuries ===
    Good("spice",     "Spice",         GoodCategory.LUXURY,     base_price=55),
    Good("silk",      "Silk",          GoodCategory.LUXURY,     base_price=70),
    Good("porcelain", "Porcelain",     GoodCategory.LUXURY,     base_price=60),
    Good("tea",       "Tea",           GoodCategory.LUXURY,     base_price=40),
    Good("pearls",    "Pearls",        GoodCategory.LUXURY,     base_price=95),

    # === Provisions ===
    Good("rum",       "Rum",           GoodCategory.PROVISION,  base_price=20),
    Good("tobacco",   "Tobacco",       GoodCategory.PROVISION,  base_price=28),

    # === Military ===
    Good("weapons",   "Weapons",       GoodCategory.MILITARY,   base_price=45),

    # === Medicine ===
    Good("medicines", "Medicines",     GoodCategory.MEDICINE,   base_price=35),

    # === Contraband (BLACK_MARKET ports only) ===
    Good("opium",        "Opium",         GoodCategory.CONTRABAND, base_price=85, weight_per_unit=0.5),
    Good("black_powder", "Black Powder",  GoodCategory.CONTRABAND, base_price=65, weight_per_unit=1.5),
    Good("stolen_cargo", "Stolen Cargo",  GoodCategory.CONTRABAND, base_price=40, weight_per_unit=1.0),

    # === Hunted goods ===
    Good("pelts",  "Pelts",  GoodCategory.COMMODITY, base_price=8, weight_per_unit=0.5),
]}
