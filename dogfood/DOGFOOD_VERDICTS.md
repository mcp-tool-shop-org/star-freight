# Dogfood Verdicts — Star Freight

> Rolling log of run results. Each entry records the verdict and any design actions taken.
> Newest entries at the top.

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
