# Fork Map — Star Freight ← Portlight

> What we inherited, what we keep, what we replace, what we build new.
> This is the single source of truth for fork decisions.

---

## Inherited Intact (use as-is, reskin content only)

These systems are architecturally sound and map directly to the sci-fi setting.

| Portlight Module | Star Freight Role | Notes |
|---|---|---|
| `engine/economy.py` | Trade engine | Scarcity-ratio pricing, stock mutation, buy/sell receipts — identical mechanic, different goods |
| `engine/voyage.py` | Travel engine | Depart/advance/arrive state machine — "sailing" becomes "transit between stations" |
| `engine/contracts.py` | Contract system | 7 contract families map cleanly (procurement, smuggling, reputation charter, etc.) |
| `engine/reputation.py` | Reputation engine | Regional standing + commercial trust + decay — per-civilization instead of per-region |
| `engine/infrastructure.py` | Station services | Warehouses, broker offices, credit lines, insurance — rename, keep mechanics |
| `engine/models.py` | Core state schema | Dataclass foundation — extend, don't replace |
| `engine/save.py` | Save/load | JSON serialization — extend for new state |
| `engine/port_arrival_engine.py` | Station arrival | Dock → pay fee → refresh prices → offers — same flow |
| `engine/captain_identity.py` | Captain background | 9 archetypes → rework for military pilot backstory variants |
| `engine/narrative.py` | Milestone engine | Campaign milestone evaluation — extend for investigation |
| `engine/campaign.py` | Campaign state | Arc tracking, unlocks, victory conditions — extend |
| `engine/underworld.py` | Pirate factions | Faction standing, hostility — rename factions to sci-fi |
| `engine/loot.py` | Salvage/loot | Post-encounter drops — reskin |
| `balance/` | Balance harness | Seed-deterministic simulation with policy bots — invaluable, keep whole |
| `stress/` | Stress harness | Invariant checking per tick — keep, extend invariants |
| `receipts/` | Trade ledger | Deterministic receipt hashing — keep intact |

## Must Be Replaced (same role, new implementation)

| Portlight Module | Why Replace | Star Freight Replacement |
|---|---|---|
| `engine/combat.py` | Stance-triangle melee doesn't fit sci-fi grid combat | New: grid-based tactical combat (shared for ground + ship) |
| `engine/duel.py` | Sword duel orchestrator — no equivalent in sci-fi | Remove entirely |
| `engine/naval.py` | Broadside/close/evade — ship combat is now grid combat with ships-as-characters | Replace with unified grid engine |
| `engine/encounter.py` | 4-phase naval escalation — replace with encounter → grid combat (ground or ship) | New encounter state machine |
| `engine/skill_engine.py` | Medieval skill tree — replace with crew ability system | New: crew binding spine |
| `engine/companion_engine.py` | Simple morale + role bonus — too thin for crew-as-binding-constraint | New: deep crew system (tactical + cultural + narrative) |
| `engine/culture_engine.py` | Sea culture flavor injection — replace with civilization knowledge system | New: cultural knowledge engine |
| `engine/sea_culture_engine.py` | Voyage-day flavor — replace with transit encounter system | New: transit event engine |
| `engine/injuries.py` | Personal injury tracking — extend to crew + ship damage model | New: unified damage/repair |
| `engine/hunting.py` | Forage/hunt at port — no direct equivalent | Remove or rethink as salvage ops |
| `engine/weapon_quality.py` | Melee weapon condition — no equivalent | Remove |
| `engine/weapon_provenance.py` | Weapon pedigree — no equivalent | Remove |
| `app/combat_views.py` | Duel rendering — replace with grid combat UI | New: grid combat renderer |
| `app/tui/screens/combat.py` | Stance selection screen — replace | New: tactical grid screen |
| `app/tui/screens/encounter.py` | Naval encounter flow — replace | New: encounter screen |

## Must Be Built New (no Portlight equivalent)

| System | Design Doc Source | Priority |
|---|---|---|
| **Crew Binding Spine** | System Laws §Crew | **P0 — thesis seam** |
| **Grid Combat Engine** | System Laws §Combat | P1 — shared ground/ship |
| **Cultural Knowledge System** | System Laws §Cultural Knowledge | P2 — civilization depth |
| **Investigation System** | System Laws §Investigation | P3 — conspiracy plot layer |
| **Civilization Content** | Content Architecture (5 civs) | P1 — parallel with systems |
| **Ship-as-Character Model** | System Laws §Combat | P1 — unified with grid |
| **Debt Ledger (Veshan)** | Progression Economy §Veshan | P2 — civ-specific pressure |
| **The Telling (Keth)** | Content Architecture §Keth | P2 — civ-specific ritual |
| **Transit Events** | Experience Contract §sub-loop | P2 — replaces sea culture |

## Remove (Portlight-specific, no Star Freight equivalent)

| Module | Reason |
|---|---|
| `printandplay/` | Board game generator — not applicable |
| `content/melee_weapons.py` | Medieval weapons |
| `content/ranged_weapons.py` | Medieval ranged |
| `content/armor.py` | Medieval armor |
| `content/fighting_styles.py` | Regional sword traditions |
| `content/sea_culture.py` | Maritime flavor text — replaced by civilization culture |
| `content/port_institutions.py` | Mediterranean institutions |
| `content/port_institutions_east.py` | East Indies institutions |
| `engine/fleet.py` | Multi-ship management (planned, never active) |
| All `world/ports/*.json` | Maritime port data — replaced by station data |

## Content Reskin (keep structure, replace data)

| Content Module | Reskin Target |
|---|---|
| `content/ports.py` | 20 ports → 20 stations (4 per civilization) |
| `content/routes.py` | 65 sea routes → space lanes between stations |
| `content/goods.py` | 35 maritime goods → 20 sci-fi trade goods |
| `content/ships.py` | 5 ship classes → sci-fi vessel classes |
| `content/seasons.py` | 4 seasons → Keth seasonal cycle or remove |
| `content/companions.py` | 15 companions → 7 crew members (deeper) |
| `content/merchants.py` | Merchant archetypes → station vendor types |
| `content/factions.py` | 8 pirate factions → sci-fi criminal/rival factions |
| `content/contracts.py` | Contract templates → sci-fi contract families |
| `content/skills.py` | 10 skills → crew abilities |
| `content/upgrades.py` | Ship upgrades → sci-fi ship modules |
| `content/crew_roles.py` | Crew roles → Star Freight crew roles |

---

## Fork Rules

1. **Inherit first.** Don't rewrite working systems that map cleanly.
2. **Portlight is not sacred.** Anything that fights the sci-fi captain fantasy is provisional.
3. **One combat engine.** Grid-based, shared between ground and ship. No mode split.
4. **Crew is the new seam.** The companion system must be rebuilt from scratch — it's the thesis.
5. **Content is the last step.** Systems first, then stations/goods/NPCs.
