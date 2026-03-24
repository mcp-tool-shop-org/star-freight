# Dogfood Verdicts — Star Freight

> Rolling log of run results. Each entry records the verdict and any design actions taken.
> Newest entries at the top.

---

## Wave 3 — P1 Tuning Confirmation

**Overall: PASS**

All 8 checks passed. Credit ratio 4.78x (target 3-5x). All baselines survive.
Fear classifier 3/3 distinct. Divergence 1.88. Honor escalation survives at
245 credits with 4 injuries — scarred but alive, not comfortable.

Two infrastructure bugs fixed during wave:
1. `run_scenario` was not applying overrides before simulation (all stress runs were baselines)
2. `simulate_run` always started at Meridian Exchange, ignoring scenario starting station

| # | Scenario | Class | Credits | Fear | Verdict |
|---|----------|-------|---------|------|---------|
| 1 | Relief baseline | core | 3386 | delivery delay | PASS |
| 2 | Gray baseline | core | 709 | exposure | PASS |
| 3 | Honor baseline | core | 813 | crew loss | PASS |
| 4 | Gray seizure | stress | 743 | exposure | PASS |
| 5 | Relief shortage | stress | 2228 | delivery delay | PASS |
| 6 | Honor escalation | stress | 245 | crew loss | PASS |
| 7 | Burned rep recovery | recovery | 679 | combat attrition | PASS |

---

## Wave 2 — Post-P0 Economy Fix

**Overall: PASS with P1 items**

Economy viable. All captains survive. Divergence preserved (1.00 across all dimensions).

Three findings:
1. Relief dominates (11x credit ratio — target 3-5x)
2. Honor escalation is comfortable, not stressful (combat = income)
3. Fear classifier still coarse (2/3 unique fears)
4. Investigation sources still station-only (harness issue, not game issue)

| Pass | Result | Key Finding |
|---|---|---|
| A: Baselines | PASS/WARN | All survive. Relief 4585, Gray 407, Honor 1034. 11x ratio too wide. |
| B: Investigation | FAIL | Station sources only. Harness doesn't emit trade/combat events. |
| C: Stress | PASS | All survive stress. Honor thrives under escalation (too comfortable). |

---

## Wave 1 — v0.1.0-dogfood

**Overall: WARN (economy blocks PASS)**

Architecture holds. Divergence is real (1.00 station, 1.00 lane). 3/3 unique identities. Combat postures differ. But every captain goes negative on credits. Economy is non-functional.

| # | Scenario | Class | Verdict | Key Finding |
|---|---|---|---|---|
| 1 | `relief_baseline_90d_s42` | baseline | WARN | Route divergence excellent. Economy -1144. |
| 2 | `gray_baseline_90d_s42` | baseline | WARN | Best goods variety. All retreats. Economy -1205. |
| 3 | `honor_baseline_90d_s42` | baseline | WARN | Clear combat identity. Economy -1143. |
| 4 | `gray_seizure_60d_s17` | stress | WARN | 18 delays. Economy obscures seizure pressure. |
| 5 | `relief_shortage_60d_s17` | stress | WARN | Shortage present. Economy dominates. |
| 6 | `honor_escalation_60d_s17` | stress | WARN | 3 injuries. Economy still dominant signal. |
| 7 | `recovery_injured_crew_45d_s99` | recovery | WARN | Crew recovered. Economy bleeds. |
| 8 | `recovery_broke_hull_45d_s99` | recovery | WARN | Starting broke stays broke. |
| 9 | `recovery_burned_rep_45d_s99` | recovery | WARN | Rep damage persists. Economy compounds. |
| 10 | `tui_first_hour_s01` | tui | PASS | Clean run. |
| 11 | `tui_combat_heavy_s01` | tui | PASS | No confusion. |
| 12 | `tui_investigation_s01` | tui | PASS | Fragments surfaced. |

---

## Design Actions Log

| Date | Source | Finding | Action | Status |
|---|---|---|---|---|
| 2026-03-23 | Wave 1 | Economy non-viable (all captains negative) | P0: Recalibrate income/expense ratio | PENDING |
| 2026-03-23 | Wave 1 | Fear classifier too coarse (2/3 unique) | P1: Add fear dimensions | PENDING |
| 2026-03-23 | Wave 1 | Investigation only from station sources | P2: Broaden trigger matching | PENDING |
| 2026-03-23 | Wave 1 | Reputation barely moves | P3: Increase rep velocity | PENDING |
| 2026-03-23 | Wave 2 | Relief dominates (11x ratio) | P1: Narrow margin gap to 3-5x | DONE (Wave 3 confirmed 4.78x) |
| 2026-03-23 | Wave 2 | Honor escalation too comfortable | P1: Make escalation stress real | DONE (Wave 3: 245 credits, 4 injuries) |
| 2026-03-23 | Wave 2 | Investigation only station sources | P2: Fix harness event emission | PENDING |
| 2026-03-24 | Wave 3 | run_scenario not applying overrides | Fix: apply before simulation | DONE |
| 2026-03-24 | Wave 3 | simulate_run ignoring starting station | Fix: respect initial_state | DONE |
| 2026-03-24 | Wave 3 | Gray at 709 — close to floor | Watch: monitor across seeds | WATCH |
| 2026-03-24 | Wave 3 | test_full_voyage_arrives flaky | Pre-existing test ordering issue | WATCH |
