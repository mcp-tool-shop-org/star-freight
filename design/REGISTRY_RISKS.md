# Risks Registry — Star Freight

> Real failure modes the proofs exposed or nearly exposed. Not theoretical worries — concrete risks with observable symptoms and test conditions. Review weekly during development.

---

## Design Risks

| # | Risk | Why It Kills the Game | Symptom | How to Test | Decide By |
|---|------|-----------------------|---------|-------------|-----------|
| 1 | **Crew binding too dominant** | If crew composition is the ONLY interesting decision, other systems become furniture. Trade routes, ship upgrades, and reputation management must matter independently — not just as crew-delivery mechanisms. | Playtester says "I just need to find the right crew and then the game plays itself." | Run a vertical slice playthrough with fixed crew (no recruitment choices). Is the game still interesting? If not, other systems are too thin. | Vertical slice |
| 2 | **Combat too infrequent** | If the player goes 3+ sessions without combat, the combat system rots in memory. They forget the grid, abilities feel unfamiliar, and fights become interruptions instead of events. | Playtester forgets ability names. Fights feel disconnected from the session before and after. | Track combat frequency across 10 sessions. Target: combat in 60–80% of sessions. If below 50%, increase lane danger or contract variety. | Vertical slice playtest |
| 3 | **Combat too frequent** | If the player fights every session, the game becomes a tactics game with a trade wrapper. The cultural and economic layers lose weight. | Playtester says "I just skip to the fighting." Trade decisions feel like pre-combat shopping. | Track what percentage of session time is combat. Target: 20–35% of time. If above 40%, reduce lane encounter rates. | Vertical slice playtest |
| 4 | **Cultural gating becomes friction** | If cultural knowledge gates too many profitable trades, the player feels punished for not being Lv.2 with everyone. Cultural engagement must feel like opportunity, not tax. | Player avoids unfamiliar civilizations because the risk-reward ratio is worse than repeat routes. "Why would I go to Veshan space when Keth pays better?" | Track how many civilizations a playtester engages with by hour 8. Target: at least 3. If only 1–2, cultural gates are too steep or rewards for new civs are too low. | Phase 4 (cultural depth) |
| 5 | **Gray path dominates** | If smuggling/pirate work is strictly more profitable than legal trade, the merchant path becomes the suboptimal choice. Both must be viable. | Every playthrough drifts to pirate because the numbers are better. | Run economy sim: 10 sessions pure legal vs 10 sessions pure gray vs 10 sessions mixed. Net credits should be within 20% of each other. Risk-adjusted return should be comparable. | Phase 3 (vertical slice) |
| 6 | **Pressure becomes chores** | If crew pay and ship maintenance feel like a tax rather than a decision, the player resents the loop instead of engaging with it. The floor cost must create route/contract choices, not repetitive obligation. | Player says "ugh, maintenance again" or "I'm just grinding to pay the crew." | Ask playtesters after every session: "Did you feel pressured or annoyed?" If >30% of answers are "annoyed," reduce a floor cost or increase how often the floor cost intersects with interesting decisions. | Vertical slice playtest |
| 7 | **Investigation lags behind economy** | If the player is economically comfortable before they've found investigation beats, the plot feels like an afterthought. Investigation breadcrumbs must appear at the pace of economic progression. | Player has 5,000₡ and is Trusted with two factions but is only at beat 2/10. | Track investigation progress vs economic progress. Beats 1–3 should appear by the time the player has 2 crew. Beats 4–6 should be accessible when the player reaches Respected with any faction. | Phase 6 (investigation) |
| 8 | **Veshan Debt Ledger is confusing** | The debt system is the most complex cultural mechanic. If players can't intuit how debts work or feel trapped by obligations they didn't understand, the system becomes adversarial. | Player defaults on a debt because they didn't understand they were accepting one. "That's unfair — I didn't know that was a major debt." | Cultural knowledge Lv.1 must make debt weights legible. Playtest: can a Lv.1 player correctly identify minor vs standard vs major before accepting? If not, the UI needs clearer signals. | Phase 4 (cultural depth) |
| 9 | **The Portlight fork creates invisible assumptions** | Portlight was designed for sail-age ocean trading. Assumptions about speed, distance, communication, and social structure may not map to sci-fi. Example: Portlight's routes are 1–5 days. If space lanes are the same, the system may feel too small. | The world feels like "Portlight with space words" instead of a different game. | After reskinning, have someone who hasn't played Portlight play the vertical slice. Do they feel the sci-fi? Or does it feel like a pirate game with lasers? | Phase 0 (fork) |
| 10 | **Single developer burnout** | All design, code, content, and testing from one person with AI assistance. 20–28 week estimate. Side project alongside other active work. | Development stalls at Phase 4–5 (content expansion) because the writing volume is exhausting. | Define content-per-session targets. If writing falls behind by 2+ weeks, trigger Tier 2 cuts. Build systemic content generation early to reduce hand-authoring burden. | Ongoing |

---

## Technical Risks

| # | Risk | Impact | Mitigation | Status |
|---|------|--------|-----------|--------|
| 11 | **Combat grid rendering in Python TUI** | Portlight has no grid. The 8×8 combat display is new terminal territory. May be ugly or unreadable. | Prototype the grid in Phase 1 before building combat logic. Use rich/blessed library for better terminal rendering. Fallback: ASCII grid (proven in Saint's Mile). | Untested |
| 12 | **Save file bloat from consequence log** | 200 entries × ~100 bytes = 20KB. Acceptable. But NPC memory (100 NPCs × 3 interactions × ~200 bytes) adds 60KB. Total save: ~100KB. Still fine. | Monitor save size during development. Prune consequence log at 200 entries. | Low risk |
| 13 | **Economy simulation divergence** | The balance harness may not catch emergent economy problems (e.g., a specific 3-station trade loop that generates infinite money). | Run 1,000-session automated playthroughs with random strategy. Flag any strategy that exceeds 3× target income rate. | Build during Phase 1 |
| 14 | **Portlight wiring gaps affect fork** | Portlight has known unfinished systems: loot not triggered after combat, armor not passed to combatant, surgeon bay not wired. | Fork from stable branch. Document which Portlight systems are relied on vs rebuilt. Don't depend on Portlight's combat systems at all (being replaced entirely). | Phase 0 |

---

## Content Risks

| # | Risk | Impact | Mitigation | Status |
|---|------|--------|-----------|--------|
| 15 | **Alien civilizations feel like humans with different hats** | If the Keth, Veshan, and Orryn don't play differently in mechanics, they're just flavor text. | Each civ must have a unique cultural mechanic that creates different gameplay (permits, seasons, debts, telling, rep-reading). If any civ's mechanic can be removed without changing gameplay, that civ is underdeveloped. | Test during Phase 4 |
| 16 | **Crew members feel interchangeable** | If crew are just "stat packages with dialogue," the binding constraint fails. Each crew member must change the captain's posture. | Playtest: ask "what changed when you recruited [crew]?" If the answer is only "I got ability X," the crew design is too thin. Answer should include cultural access, narrative hooks, and captain identity shift. | Test during vertical slice |
| 17 | **Investigation is too decoupled** | If investigation beats only appear when the player actively hunts for them, investigation feels like a separate quest chain. Beats must surface through trade, combat, and cultural engagement. | At least 5 of 10 beats should be triggered by consequence engine or faction reputation — not by visiting a specific location. | Phase 6 |
| 18 | **Lane narration becomes repetitive** | If the player reads "the corridor is quiet" for the fifth time, travel becomes skip-pressing. | Build Portlight-scale encounter variety: 80+ route-specific encounters, 20+ templates, seasonal variation, consequence-seeded events. Target: <10% chance of seeing the same text twice in 10 sessions. | Phase 5 (content expansion) |

---

## Resolved Risks

| # | Was Risk | Resolution | When |
|---|---------|-----------|------|
| — | "Two combat systems might feel disconnected" | Unified to one system. Ships are characters. Proofs confirmed the grid works for both theaters. | System Laws revision |
| — | "Shmup + JRPG might split the player base" | Shmup dropped. One combat system. Focus on the captain fantasy. | Thesis Lock revision |
| — | "Cultural interactions have randomness" | Resolved: zero randomness in cultural interactions. Knowledge + choice only. | System Laws |
