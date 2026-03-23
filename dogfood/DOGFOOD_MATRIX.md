# Dogfood Matrix — Star Freight Wave 1

> 12 canonical runs. Seeded, named, scoped, comparable, evidence-backed.
> The point is not to prove the game has content. It is to prove that under
> repeated pressure, the game stays legible, the runs stay different, failure
> stays interesting, and the captain's life still feels coherent.

---

## Run Classes

### A. Baseline Runs (3)
Prove the normal game is good. Three captain postures, same seed, 90 days each. Divergence should be visible by day 20-30.

### B. Stress Runs (3)
Inject a specific pressure and see whether the game bends or breaks. 60 days each. Start from a normal state but with one world pressure amplified.

### C. Recovery Runs (3)
Start from a wounded state and prove the campaign can still produce interesting decisions. 45 days each. Start with damage already done.

### D. TUI Runs (3)
Prove the interface is readable under real use. Focus on specific surface challenges.

---

## The 12 Runs

### Baseline Divergence

| # | ID | Path | Crew | Seed | Days | Focus |
|---|---|---|---|---|---|---|
| 1 | `relief_baseline_90d_s42` | Relief / Legitimacy | Thal + Ilen | 42 | 90 | Convoy discipline, trust access, Keth/Orryn cultural doors |
| 2 | `gray_baseline_90d_s42` | Gray / Document | Sera + Nera | 42 | 90 | Paper leverage, institutional navigation, Compact depth |
| 3 | `honor_baseline_90d_s42` | Honor / Frontier | Varek + Thal | 42 | 90 | Direct confrontation, house politics, Veshan/Keth doors |

**Pass condition:** By day 30, the three runs use different dominant stations, different lane preferences, different goods traded, and different encounter profiles. No path dominates profit, safety, and access simultaneously.

### Stress

| # | ID | Path | Pressure Injected | Seed | Days | Focus |
|---|---|---|---|---|---|---|
| 4 | `gray_seizure_60d_s17` | Gray | Compact seizure flag active from day 1 | 17 | 60 | Does paper leverage survive institutional scrutiny? |
| 5 | `relief_shortage_60d_s17` | Relief | Shortage prices active, convoy delays doubled | 17 | 60 | Does relief work stay viable when the system squeezes hardest? |
| 6 | `honor_escalation_60d_s17` | Honor | Veshan standing starts at -15 (Cold), encounter rate +50% | 17 | 60 | Does confrontation tolerance survive when the world pushes back? |

**Pass condition:** Every stress run produces pressure without turning into chores. The captain adapts or fails interestingly — never grinds.

### Recovery

| # | ID | Starting Wound | Seed | Days | Focus |
|---|---|---|---|---|---|
| 7 | `recovery_injured_crew_45d_s99` | Thal injured (5d), Varek morale 20 | 99 | 45 | Can you rebuild capability with one crew member down? |
| 8 | `recovery_broke_hull_45d_s99` | Credits 50, hull 800/2000, pay missed once | 99 | 45 | Can you climb out of poverty without dead time? |
| 9 | `recovery_burned_rep_45d_s99` | Compact -50, Keth -25, investigation delayed 30 days | 99 | 45 | Can you operate when doors are closing and evidence is going cold? |

**Pass condition:** Every recovery run finds a viable but painful path forward. Recovery is ugly, slow, and interesting — never painless, never impossible.

### TUI

| # | ID | Focus | Duration | What to watch |
|---|---|---|---|---|
| 10 | `tui_first_hour_s01` | First-time player experience | 45 min | Does the player know what to do, where to go, what matters? |
| 11 | `tui_combat_heavy_s01` | Combat legibility under pressure | 30 min | Can you read grid, abilities, retreat, aftermath clearly? |
| 12 | `tui_investigation_s01` | Journal and consequence clarity | 30 min | Do fragments surface clearly? Do consequences show? |

**Pass condition:** 80%+ of TUI runs complete without "what am I looking at?" confusion. The player can describe what changed after every major decision.

---

## Wave 1 Pass Criteria

Wave 1 passes if ALL of these are true:

1. The 3 baseline paths clearly diverge by day 20-30
2. No captain path dominates profit, safety, and access all at once
3. Every stress run produces pressure without turning into chores
4. Every recovery run finds a viable but painful path forward
5. At least 80% of TUI runs complete without interface confusion
6. Testers can describe their run as a life, not just a build

---

## Seven Scoring Dimensions

Each run is scored on these dimensions:

| Dimension | What it measures |
|---|---|
| **Loop clarity** | Does the core loop (dock → trade → travel → encounter → dock) feel cohesive? |
| **Captain divergence** | Does this run feel different from other runs? |
| **Pressure fairness** | Does pressure create decisions, not punishment? |
| **Recovery viability** | Can bad states be recovered from interestingly? |
| **TUI legibility** | Can the player read state and consequence clearly? |
| **Content freshness** | Does content still feel distinct after repeated exposure? |
| **Consequence credibility** | Do outcomes feel earned, not arbitrary? |

Verdict per run: **PASS** / **WARN** / **FAIL**
