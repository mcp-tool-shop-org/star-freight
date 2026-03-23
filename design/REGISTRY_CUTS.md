# Cuts Registry — Star Freight

> **THE FULL GAME IS THE TARGET. BUILD THE FULL GAME.**
>
> This registry exists ONLY as an emergency reference if the lead developer explicitly decides to reduce scope due to time pressure. No cut tier is a build target. No feature listed as "deferrable" should be deferred unless the developer says so. A future contributor reading this document should build toward the Full scope described in the spine docs, not toward any reduced tier.
>
> **Rule: Nothing in this registry authorizes cutting a feature. Only the lead developer can authorize a cut, and only in response to concrete production pressure — not as a planning convenience.**

---

## Sacred (never cut — the game IS these)

These are the thesis. Cutting any of them produces a different (worse) game.

| Feature | What It Proves | If Cut |
|---------|---------------|--------|
| **Trade economy (buy/sell/margins across civilizations)** | Trade is layer 1 of the loop. Economic pressure creates decisions. | No game. No captain fantasy. |
| **Turn-based grid combat (one system, two theaters)** | Tactics is layer 2. Combat is a campaign event. Ships are characters. | No tactical depth. The captain is a merchant spreadsheet. |
| **Reputation (per-faction, gated access)** | The binding variable between all three layers. | Civilizations are decoration. Choices have no systemic weight. |
| **Crew as binding constraint (multi-layer contribution)** | The central design insight. One crew member changes trade, tactics, and plot simultaneously. | Three parallel minigames in a trenchcoat. |
| **Consequence engine** | The world remembers. Actions echo. The captain's history matters. | The world is static. Repeat routes feel identical. |
| **Cultural knowledge (per-civ levels)** | Civilizations are gameplay-distinct, not just flavor. | All civilizations feel the same. Trading is purely economic. |
| **Investigation (narrative spine)** | The story gives the merchant/pirate spectrum an endgame. | No reason to keep playing past economic comfort. |
| **Captain's View (persistent bar)** | The interface thesis — shared campaign state visible at all times. | The player feels like they're switching between apps. |
| **Anti-soft-lock systems** | The player can always recover. Failure is consequential but not terminal. | Game-ending states exist. Players quit after bad luck. |
| **5 civilizations (minimum 3 at Tier 3)** | The world has cultural texture. Different civilizations play differently. | Generic space. One set of rules, one kind of trade. |

---

## Powerful but Deferrable (ship without, add in post-launch or v1.1)

Each of these makes the game meaningfully better. None of them are required for the thesis to hold.

| Feature | What It Adds | What Happens if Deferred | Ship Condition |
|---------|-------------|-------------------------|----------------|
| **Veshan Debt Ledger** | The deepest, most personal cultural mechanic. Debts as callable currency. Obligations that compete with plans. | Veshan use standard reputation only. Still gameplay-distinct (honor culture, house rivalries, best weapons) but less mechanically unique. | The game works. Veshan are thinner. |
| **Orryn Telling mechanic** | Unique negotiation ritual. Radical honesty as a game mechanic. | Orryn use standard negotiation. Still distinct (information brokers, mobile drifts, middlemen) but less culturally deep. | The game works. Orryn are thinner. |
| **Orryn mobile drifts** | Moving stations create a dynamic map. Trade routes shift over time. | Fixed Orryn stations. The system is less alive but fully functional. | Simpler. Loses dynamism. |
| **Keth 4-season cycle** | Full seasonal variety. Each season changes trade, customs, and access. | 2-season model (harvest/dormancy). 80% of the gameplay value, 50% of the content. | Good enough. The seasonal concept lands. |
| **6th crew member (wildcard)** | Late-game recruit tied to the conspiracy. | 5 crew members. One less roster choice. Investigation connects through other crew. | The loop works with 5. |
| **Crew loyalty missions (multi-stage)** | Deep personal arcs with gameplay consequences. | Simplified single-encounter loyalty events. Less emotional, still functional for loyalty tier advancement. | Crew still binds the layers. Less narrative depth. |
| **New ship purchase (late game)** | Major milestone. Changes the play experience. | One upgradeable ship throughout. Still feels like scrappy survival. | Upgrades carry the progression. |
| **Proxy war contracts** | Veshan house politics as playable faction warfare. | Veshan contracts limited to standard trade/bounty. | Less political depth. |

---

## Luxury (first to go under any pressure)

Nice to have. The game doesn't notice their absence.

| Feature | What It Adds | Cut Cost |
|---------|-------------|----------|
| **Sound design / audio** | Atmosphere. Ambient station sounds, combat impacts. | Zero gameplay impact. |
| **Crew portraits (Tauri build only)** | Visual identity for crew members. | Text carries the identity. Portlight and Saint's Mile proved this. |
| **Tauri desktop build** | Richer UI, visual grid, potential for art. | The game is designed for TUI. Tauri is a future edition, not a requirement. |
| **NPC count above 100** | Denser world. More unique interactions. | 60–80 NPCs with standing-aware templates feels alive enough. Portlight proved 134 works, but 80 is the viable floor. |
| **Full 4 Keth seasons with unique cultural events per season** | Maximum seasonal depth. | 2 seasons with 1 event each captures the core mechanic. |
| **Ship-to-ship encounters without combat** | Merchant convoys, Orryn passing, Compact hails resolved socially. | Lane encounters default to event text + choice menu. No dedicated social-encounter system needed. |

---

## False Complexity (cut proactively — these feel important but don't serve the thesis)

| Feature | Why It Feels Important | Why It's False | Resolution |
|---------|----------------------|----------------|------------|
| **Crew-to-crew relationships** | "Crew is the game, so crew should interact with each other!" | Crew members react to the player's choices, not to each other. Adding crew-to-crew dynamics doubles the social simulation without improving the three-layer loop. | Cut. Crew opinions about the player are sufficient. |
| **Equipment / gear system for crew** | "RPGs have equipment!" | Crew stats are fixed by role. Growth comes from loyalty tiers (unlocking abilities) not from gear. Adding equipment creates an inventory management system that competes with cargo hold management and adds busywork. Anti-pillar 1. | Cut. Ship upgrades are the equipment system. |
| **Crafting** | "Keth bio-materials + Veshan metals = new items!" | Anti-pillar 1: no busywork systems. Crafting adds a gathering → combining → result loop that serves neither trade nor tactics. | Cut. Buy and sell, don't craft. |
| **NPC schedules / daily routines** | "A living world should have NPCs who move around!" | NPCs are at their stations. Their behavior changes based on reputation and consequence state, not time of day. Schedules add simulation complexity with no campaign state impact. | Cut. Standing-aware behavior is sufficient. |
| **Map fog / exploration** | "Discovering new stations is exciting!" | The player is from this system — they know where things are. Gating access through reputation and cultural knowledge is more interesting than through map exploration. Knowledge, not geography, is the frontier. | Cut. All stations visible from Day 1. Knowledge gates access. |
| **Survival mechanics (food, oxygen, life support)** | "Space is dangerous! Ships need supplies!" | Fuel already provides travel pressure. Adding food/oxygen creates a second consumable that doesn't generate decisions — only upkeep. | Cut. Fuel is the only travel consumable. |
| **Alignment / karma system** | "The merchant-pirate spectrum needs tracking!" | It IS tracked — derived from the reputation portfolio. A separate alignment variable would duplicate the reputation system and add moral judgment the game explicitly avoids (anti-pillar 2). | Cut. Reputation IS alignment. |
| **Procedural station generation** | "20 hand-authored stations is limiting!" | 20 hand-authored stations with deep culture, named NPCs, and standing-aware behavior are richer than 50 procedural stations with template descriptions. Quality > quantity. | Cut. Hand-author 20. Portlight proved this works. |

---

## Emergency Cuts (Tier 3 — 50% capacity, what ships)

If production time is halved, this is the game that ships. Every sacred feature survives. The world is smaller but the thesis holds.

| What Remains | Scope |
|-------------|-------|
| Civilizations | 3: Compact, Keth, Sable Reach |
| Stations | 9 (3 per civ) |
| Lanes | 15 |
| Trade goods | 10 |
| Crew members | 3 (1 Keth, 1 Reach, 1 Compact) |
| Contract types | 4 (trade run, bounty, smuggling, investigation) |
| Cultural knowledge | 2 levels (Ignorant/Aware) per civ |
| Cultural mechanics | Keth: 2-season cycle. Compact: basic permits. Reach: reputation as law. |
| Investigation | 5 beats |
| NPCs | 40 |
| Lane encounters | 30 (templates + a few per-route) |
| Combat enemy types | 8 ground + 5 ship |
| Consequence triggers | 20 |

**What dies at Tier 3:** Veshan civilization (all houses, Debt Ledger, honor challenges). Orryn civilization (Telling, mobile drifts, information brokerage). 3 crew members. 11 stations. 25 lanes. 10 trade goods. 5 investigation beats. Proxy wars. Salvage runs. Ancestor Cult faction. Half the NPC roster. Most lane encounter variety.

**What survives at Tier 3:** The three-layer loop. Crew as binding constraint (3 crew, each bridging trade + tactics + plot). One unified combat system. Trade economy with cultural gating. Reputation spectrum (merchant ↔ pirate). Consequence engine. Investigation (short but complete). Anti-soft-lock systems. Captain's View.

**This is the minimum viable game.** It's small — 10-12 hours instead of 15-25. But a player who finishes it will have made campaign decisions across trade, tactics, and plot, felt crew as multi-system assets, navigated 3 cultures, tracked a conspiracy, and ended as either a merchant or a pirate.
