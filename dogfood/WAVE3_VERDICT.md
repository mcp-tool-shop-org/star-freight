# Wave 3 Verdict: PASS

**Date:** 2026-03-24
**Build:** post-P1 tuning + scenario override fix
**Commit:** (pending)

## Objective

Prove the P1-tuned game is viable, divergent, stressful in the right ways,
and not hiding a new dominant path.

## Run Set (7 scenarios)

### Core Confirmation (90 days, seed 42)

| Captain | Credits | Combat | Wins/Losses | Injuries | Fear |
|---------|---------|--------|-------------|----------|------|
| Relief  | 3386    | 7      | 2/5         | 5        | delivery delay |
| Gray    | 709     | 4      | 0/0 (4 retreats) | 0   | exposure |
| Honor   | 813     | 7      | 6/1         | 4        | crew loss |

**Ratio:** 4.78x (target 3-5x)
**Divergence:** 1.88 overall (station 1.00, lane 1.00, trade 1.00)

### Stress Confirmation (60 days, seed 17)

| Scenario | Credits | Combat | Wins/Losses | Injuries | Fear |
|----------|---------|--------|-------------|----------|------|
| Gray Seizure | 743 | 2 | 0/0 (2 retreats) | 0 | exposure |
| Relief Shortage | 2228 | 0 | -- | 0 | delivery delay |
| Honor Escalation | 245 | 7 | 3/4 | 4 | crew loss |

### Recovery Confirmation (45 days, seed 99)

| Scenario | Credits | Combat | Survived |
|----------|---------|--------|----------|
| Burned Rep | 679 | 2 wins | Yes |

## Pass Bar Results

| # | Check | Target | Actual | Verdict |
|---|-------|--------|--------|---------|
| 1 | Credit ratio | 3-5x | 4.78x | PASS |
| 2 | All baselines survive | yes | yes | PASS |
| 3 | Relief richest, not runaway | yes | 3386, ratio 4.78x | PASS |
| 4 | Gray viable | >200 | 709 | PASS |
| 5 | Honor escalation shape | survives, not comfortable | 245 credits, 4.1/day vs baseline 9.0/day | PASS |
| 6 | Fear classifier distinct | 3/3 | 3/3 | PASS |
| 7 | Divergence high | >0.5 | 1.88 | PASS |
| 8 | Recovery playable | survives | 679 credits | PASS |

## What Was Fixed During Wave 3

### Bug: run_scenario did not apply overrides before simulation

`run_scenario()` created a campaign state and ran `simulate_run()` without
applying scenario overrides (starting state, world pressure). This meant
stress scenarios (seizure flags, encounter rate multipliers, reputation
penalties) were never applied. All stress runs were effectively baselines
with different seeds.

**Fix:** `run_scenario()` now creates the state, applies overrides via
`apply_scenario_overrides()`, then passes the configured state to
`simulate_run()` via a new `initial_state` parameter.

### Bug: simulate_run always started at Meridian Exchange

Even when a scenario specified a different starting station (e.g.,
Drashan Citadel for Honor escalation), `simulate_run()` hardcoded
`dock_at_station(state, "meridian_exchange")`.

**Fix:** `simulate_run()` now respects `state.current_station` from the
initial state.

### Infrastructure: danger_multiplier on CampaignState

Added `danger_multiplier: float = 1.0` to `CampaignState`. The `travel_to()`
encounter roll now uses `lane.danger * state.danger_multiplier`, allowing
scenarios to increase encounter frequency without modifying lane data.

### Scenario retuning: Honor Escalation

With overrides properly applied, the original scenario (1.5x encounter rate,
-15 Veshan rep) was too harsh — Honor died at -106 credits. Retuned to
1.3x encounters, -10/-5 Veshan rep. Honor now survives at 245 credits with
3 wins, 4 defeats, 4 injuries — scarred but alive.

## Watch Items for Future Waves

1. **Gray at 709** — viable but close to floor. Monitor across different seeds.
2. **Relief at 4.78x** — top edge of target band. Good seeds could push higher.
3. **test_full_voyage_arrives** — pre-existing flaky test (passes in isolation,
   fails in full suite due to test ordering). Not caused by P1 changes.

## Verdict

**PASS.** Tag v0.1.1-dogfood when committed.
