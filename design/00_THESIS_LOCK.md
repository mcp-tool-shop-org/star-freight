# Thesis Lock — Star Freight

> One-page truth of the game. Everything flows from here. If this is unclear, nothing downstream matters.

## Fantasy Promise

You were the best pilot in the fleet — until they needed a scapegoat. Stripped of rank, blacklisted, and dumped on the fringe with a rusted ship and nothing to your name. Now you trade between worlds, run contracts, and scrape together a crew of misfits who don't care about your past. The star system is alive — five civilizations (human and alien) with their own economies, customs, politics, and opinions about outsiders. Space is dangerous: pirates raid the lanes, factions wage cold wars through proxies, and rivals don't forget. Every port is a culture to navigate. Every route is a risk. Every contract is a choice: play it clean and claw back your name, or go pirate and build something they can't take from you. The reputation you earn follows you everywhere.

## Genre Blend

Gritty sci-fi space RPG. Trade, travel, combat, and cultural navigation in a living star system. Turn-based tactical combat (grid, ships-as-characters) is a natural part of life — pirates attack lanes, bounties end in fights, faction rivalries turn violent, and sometimes you pick the fight. Five civilizations (human + alien species) with deep culture. Reputation-driven narrative on a sliding scale from merchant to pirate.

## Player Fantasy (one sentence)

You are a disgraced military pilot who starts over on the fringe, navigating alien cultures, dangerous space lanes, and criminal economies, choosing whether to rebuild your name or become the pirate they already think you are.

## Design Pillars (exactly 3)

1. **The world is alive** — Five civilizations with their own trade goods, customs, festivals, politics, and grudges. Pirates prowl the lanes. Factions push agendas. NPCs remember you. The star system feels inhabited and dangerous.
2. **Reputation is currency** — Every trade, every fight, every choice shifts where you sit — with each civilization, with the underworld, with the law. Doors open and close. Prices change. Enemies appear. Your crew has opinions.
3. **Scrappy survival** — Money is tight, the ship is held together with duct tape, and every upgrade is earned. You're a small operator in a big system. The grounded tone lives in the budget.

## Anti-Pillars (exactly 3)

1. **No busywork systems** — No crafting, no gathering, no filler fetch quests. If a system doesn't create a meaningful decision, it doesn't exist.
2. **No morality lectures** — The game presents choices and consequences, not good/evil scores with judgment. Going pirate is a valid, complete path.
3. **No empty calories** — Every fight, every trade, every conversation exists because the world demands it. No random encounters for XP, no padding. But the world demands plenty.

## Platform

TBD — likely Rust TUI (proven stack) or desktop (Tauri). Not browser. Not mobile.

## Session Shape

30–60 minute sessions. A typical session: dock at a station, read the market, talk to contacts, pick up a contract or speculative cargo, travel the lane (encounters en route — pirates, patrols, distress calls, debris), arrive, navigate the local culture, sell or deliver, deal with complications. Some sessions are mostly trade. Some sessions are mostly combat. Most are a mix. One full run per sitting.

## Target Scope

Medium. One star system. 5 civilizations (human + 3–4 alien species). ~20 stations/ports across 5 cultural sectors. 15–25 hour main path. Crew of 4–6 recruitable characters. Deep culture per civilization, high replayability through reputation divergence and path variety.

## Comps (for feel, not imitation)

- **Cowboy Bebop** — tone, crew dynamics, the feeling of being broke in space. Trade and violence coexist. NOT the episodic structure.
- **Portlight** — the direct ancestor. Trade routes, port cultures, NPC memory, sea encounters, pirate factions, combat, reputation, crew morale, consequence engine. We ARE this, but in space with aliens.
- **FTL** — scrappy ship management, making do with what you have, danger on every route. NOT the roguelike permadeath.
- **Mass Effect** — alien civilizations with real politics and history between them. Crew loyalty. The ship as home. NOT the cover shooter or the savior plot.
- **Sunless Seas** — small trader in a vast, strange, culturally rich, dangerous world. Travel that tells stories. NOT the permadeath or the Lovecraft.

## Architecture Decision: Portlight Fork

This game is built by forking Portlight's world simulation layer and reskinning ocean → space. The mapping:

| Portlight | Space JRPG |
|---|---|
| Ports (20) | Stations / planets (~20) |
| Regions (5) | Cultural sectors (5 civilizations) |
| Regional cultures (5) | Alien + human civilizations with customs, taboos, trade preferences |
| Routes (43) | Space lanes |
| Sea encounters / weather | Lane encounters / sector hazards |
| Pirate factions (4) + 8 named captains | Space pirate factions + named captains |
| Naval combat (broadside/evade/board) | Ship combat (volley/maneuver/board) — turn-based grid, ships-as-characters |
| Personal combat (stance triangle + styles) | Ground combat — turn-based grid, crew as party |
| Seasonal system | Sector conditions (solar storms, blockades, trade cycles, festivals) |
| NPCs (134) with standing-aware behavior | Station NPCs who remember you |
| Port cultures + festivals | Civilization customs, holidays, market effects |
| Captain classes (9) | Pilot backgrounds / origin classes |
| Companions (5 roles, morale) | Crew with roles, opinions, and cultural backgrounds |
| Consequence engine | Reputation-generated encounters |
| Cross-port politics (merchant/broker/inspector networks) | Cross-station faction and civilization politics |
| Trade economy (17 goods, merchants, markup) | Interstellar trade economy, civilization-specific goods |
| Sea culture (route encounters, sightings, superstitions, crew moods, weather) | Space culture (lane encounters, ship sightings, spacer superstitions, crew moods, sector hazards) |

**Combat approach:** Portlight's naval + personal combat maps to a unified turn-based tactical grid. Ships-as-characters: crew fills ship roles (gunner/pilot/engineer/captain) during space encounters, ground roles during station/surface encounters. Boarding transitions from ship to ground theater mid-fight. Combat frequency matches Portlight — pirate lanes are dangerous, bounties fight back, faction conflicts escalate.

**What Portlight already solves:** Travel, world structure, NPC memory, reputation mechanics, crew morale, economy, encounter generation, consequence tracking, faction politics, cultural depth per region, cross-port relationship networks, pirate ecosystem.

**What must be built new:** Alien civilizations (biology, customs, trade preferences, taboos), turn-based grid combat engine (replacing Portlight's stance/broadside systems), the cultural navigation mechanics, the disgrace/redemption narrative spine, sci-fi content.

---

## Unresolved Questions

- What are the 5 civilizations? (1 human diaspora + 3–4 alien species? Or a different mix?)
- What makes each alien species culturally distinct in gameplay terms? (Trade preferences, customs, taboos, combat styles?)
- How does crew recruitment work? Cultural background of crew members = access to their civilization's inner circle?
- How does cultural knowledge work mechanically? (Learn customs over time? Crew members teach you? Skill-based?)
- Does the player ever lose the ship? Fail state or narrative beat?
- How many trade goods? Portlight has 17 — does space need more, fewer, or civilization-specific exclusives?
- Is there a time pressure mechanic or is it open-ended?
- How does the pirate path differ mechanically from the merchant path beyond reputation? (Different jobs? Different ports? Different economy?)
- Working title needed.

## Contradictions Discovered

- "5 deep civilizations" vs "medium scope" — Portlight proved 5 regions with 134 NPCs is achievable, but adding alien biology/customs/taboos on top multiplies content. Must define what "deep" means per civilization and hold the line.
- "Lean content" vs "high replayability" — divergence should be tonal (same ports, different treatment) more than structural (different maps). The civilization reaction to your reputation is the replay value, not branching content.

## What Must Be Proven Next

- Civilization sketches: what are the 5 cultures and what makes each one gameplay-distinct?
- The reputation spectrum: what concretely changes at different points, per civilization?
- Economy proof: one trade run showing buy/sell/margin across two civilizations.
- Combat proof: one ship encounter and one ground encounter on the grid.
