---
title: Getting Started
description: Install Star Freight and start your first run.
sidebar:
  order: 1
---

## Requirements

- Python 3.11 or later
- Terminal with Unicode support (most modern terminals)

## Install

```bash
git clone https://github.com/mcp-tool-shop-org/star-freight.git
cd star-freight
pip install -e ".[tui]"
```

## Start a game

```bash
starfreight tui
```

## Controls

| Key | Action |
|-----|--------|
| `D` | Dashboard — pressure overview |
| `C` | Crew — abilities, culture, morale |
| `R` | Routes — lanes, fuel, inspection risk |
| `M` | Market — goods, prices, cultural gates |
| `T` | Station — where you are, what's available |
| `J` | Journal — investigation fragments |
| `F` | Faction — standing with power structures |
| `B` | Buy goods |
| `S` | Sell goods |
| `G` | Travel to destination |
| `A` | Advance day |

## First run advice

- Sell before buying. A captain who arrives with cargo and leaves with cargo is wasting hold space.
- Watch crew morale. Pay day is every 30 days. Miss it and people leave.
- Cultural knowledge matters. The Keth don't sell to strangers. The Veshan challenge before they trade.
- Fuel constrains routing. Running dry means expensive emergency refueling.
- Read the station screen before trading. Prices depend on whether a station produces or demands a good.
