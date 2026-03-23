"""Stress runner — execute scenarios with invariant enforcement after every tick.

Unlike the balance runner (which measures outcomes), the stress runner
measures truth: does the game ever enter an illegal state?
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from portlight.balance.policies import ActionPlan, choose_actions
from portlight.balance.types import PolicyId
from portlight.stress.invariants import check_all_invariants
from portlight.stress.types import (
    StressRunReport,
    StressScenario,
    TraceEvent,
)


def run_stress_scenario(
    scenario: StressScenario,
    policy_id: PolicyId = PolicyId.OPPORTUNISTIC_TRADER,
) -> StressRunReport:
    """Run one stress scenario and return a report with invariant results."""
    from portlight.app.session import GameSession

    with tempfile.TemporaryDirectory() as tmp:
        session = GameSession(Path(tmp))
        session.new("StressBot", captain_type=scenario.captain_type)

        # Override seed
        import random
        session._rng = random.Random(scenario.seed)
        session.world.seed = scenario.seed

        # Inject preconditions
        _inject_preconditions(session, scenario)

        report = StressRunReport(scenario_id=scenario.id)
        trace: list[TraceEvent] = []

        # Check invariants after injection
        failures = check_all_invariants(session)
        if failures:
            report.invariant_results.extend(failures)
            report.invariant_failures += len(failures)

        for day_num in range(scenario.max_days):
            if not session.active:
                break

            current_day = session.world.day

            # Get and execute policy actions
            try:
                actions = choose_actions(session, policy_id)
                _execute_actions(session, actions)
            except Exception as e:
                trace.append(TraceEvent(
                    day=current_day,
                    action="error",
                    detail=str(e),
                    silver_after=session.captain.silver if session.captain else 0,
                ))

            # Advance day
            try:
                if not session.at_sea and session.current_port:
                    session.advance()
                elif session.at_sea:
                    session.advance()
            except Exception as e:
                trace.append(TraceEvent(
                    day=current_day,
                    action="advance_error",
                    detail=str(e),
                    silver_after=session.captain.silver if session.captain else 0,
                ))

            # Record trace
            silver = session.captain.silver if session.captain else 0
            trace.append(TraceEvent(
                day=session.world.day,
                action="tick",
                silver_after=silver,
            ))

            # CHECK INVARIANTS AFTER EVERY TICK
            failures = check_all_invariants(session)
            if failures:
                report.invariant_results.extend(failures)
                report.invariant_failures += len(failures)
                for f in failures:
                    trace.append(TraceEvent(
                        day=session.world.day,
                        action=f"invariant_violation:{f.name}",
                        detail=f.message,
                        silver_after=silver,
                    ))

            # Stop on bankruptcy
            if session.captain.silver <= 0 and session.captain.provisions <= 0:
                trace.append(TraceEvent(
                    day=session.world.day,
                    action="bankruptcy",
                    silver_after=session.captain.silver,
                ))
                break

        # Finalize report
        report.trace = trace
        report.days_survived = session.world.day
        report.final_silver = session.captain.silver if session.captain else 0
        if session.captain and session.captain.ship:
            report.final_ship_class = session.captain.ship.template_id
        return report


def _inject_preconditions(session, scenario: StressScenario) -> None:
    """Apply scenario preconditions to the session."""
    if scenario.inject_silver is not None:
        session.captain.silver = scenario.inject_silver

    if scenario.inject_provisions is not None:
        session.captain.provisions = scenario.inject_provisions

    if scenario.inject_heat is not None:
        for region, heat in scenario.inject_heat.items():
            session.captain.standing.customs_heat[region] = heat

    if scenario.inject_trust is not None:
        session.captain.standing.commercial_trust = scenario.inject_trust

    if scenario.inject_standing is not None:
        for region, standing in scenario.inject_standing.items():
            session.captain.standing.regional_standing[region] = standing


def _execute_actions(session, actions: list[ActionPlan]) -> None:
    """Execute policy actions (reuses balance runner dispatch)."""
    from portlight.balance.runner import _execute_one
    dummy_tracker: dict = {}
    for action in actions:
        try:
            _execute_one(session, action, dummy_tracker)
        except Exception:
            continue


def run_stress_batch(
    scenarios: list[StressScenario],
    policy_id: PolicyId = PolicyId.OPPORTUNISTIC_TRADER,
) -> list[StressRunReport]:
    """Run a batch of stress scenarios."""
    return [run_stress_scenario(s, policy_id) for s in scenarios]
