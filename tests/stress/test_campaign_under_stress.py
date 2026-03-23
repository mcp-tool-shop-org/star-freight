"""Campaign/victory tests under stress — prove milestones and paths stay consistent.

These tests inject campaign progress then apply economic pressure, verifying
that milestones are never duplicated, victory paths are never double-completed,
and the is_first flag stays stable under compound mutations.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from portlight.app.session import GameSession
from portlight.content.campaign import MILESTONE_SPECS
from portlight.engine.campaign import (
    MilestoneCompletion,
    SessionSnapshot,
    VictoryCompletion,
    evaluate_milestones,
)
from portlight.engine.infrastructure import CreditState, CreditTier
from portlight.stress.invariants import check_all_invariants


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_session(tmp_path: Path, captain_type: str = "merchant") -> GameSession:
    s = GameSession(base_path=tmp_path)
    s.new("CampaignBot", captain_type=captain_type)
    return s


def _build_snapshot(session: GameSession) -> SessionSnapshot:
    """Build a SessionSnapshot from the current session state."""
    return SessionSnapshot(
        captain=session.captain,
        world=session.world,
        ledger=session.ledger,
        board=session.board,
        infra=session.infra,
        campaign=session.campaign,
    )


# ---------------------------------------------------------------------------
# Milestone deduplication under repeated evaluation
# ---------------------------------------------------------------------------

class TestMilestoneDeduplication:
    def test_evaluate_twice_no_dupes(self, tmp_path):
        """Evaluating milestones twice should not create duplicates."""
        s = _fresh_session(tmp_path)
        # Advance a few days to create some state
        for _ in range(5):
            s.advance()

        snap = _build_snapshot(s)
        new1 = evaluate_milestones(MILESTONE_SPECS, snap)
        # Record them
        for m in new1:
            s.campaign.completed.append(
                MilestoneCompletion(milestone_id=m.id, completed_day=s.world.day)
            )

        # Evaluate again — same state, should return nothing new
        snap2 = _build_snapshot(s)
        new2 = evaluate_milestones(MILESTONE_SPECS, snap2)

        # Already-completed milestones should not appear again
        completed_ids = {m.milestone_id for m in s.campaign.completed}
        for m in new2:
            assert m.id not in completed_ids, (
                f"Milestone {m.id} was already completed but evaluate returned it again"
            )

        failures = check_all_invariants(s)
        assert failures == []

    def test_milestones_stable_under_silver_pressure(self, tmp_path):
        """Dropping silver to near-zero shouldn't corrupt milestone state."""
        s = _fresh_session(tmp_path)
        # Record a milestone
        s.campaign.completed.append(
            MilestoneCompletion(milestone_id="test_m1", completed_day=5)
        )

        # Apply economic pressure
        s.captain.silver = 1
        s.captain.provisions = 2

        # Advance a few days under duress
        for _ in range(3):
            s.advance()

        # Milestone should still be there, no dupes
        ids = [m.milestone_id for m in s.campaign.completed]
        assert ids.count("test_m1") == 1

        failures = check_all_invariants(s)
        assert failures == []


# ---------------------------------------------------------------------------
# Victory path consistency
# ---------------------------------------------------------------------------

class TestVictoryPathConsistency:
    def test_is_first_stays_stable(self, tmp_path):
        """Once a path is marked is_first, no other path should also be first."""
        s = _fresh_session(tmp_path)
        s.campaign.completed_paths = [
            VictoryCompletion(
                path_id="shadow_network", completion_day=50,
                summary="built it", is_first=True,
            ),
        ]

        # Add a second path — is_first should be False
        s.campaign.completed_paths.append(
            VictoryCompletion(
                path_id="oceanic_reach", completion_day=70,
                summary="explored it", is_first=False,
            ),
        )

        failures = check_all_invariants(s)
        assert failures == []
        firsts = [p for p in s.campaign.completed_paths if p.is_first]
        assert len(firsts) == 1

    def test_victory_path_survives_credit_default(self, tmp_path):
        """Victory completion should persist even if credit defaults afterward."""
        s = _fresh_session(tmp_path)
        s.campaign.completed_paths = [
            VictoryCompletion(
                path_id="lawful_trade_house", completion_day=60,
                summary="established house", is_first=True,
            ),
        ]
        # Now default on credit
        s.infra.credit = CreditState(
            tier=CreditTier.MERCHANT_LINE,
            credit_limit=500,
            outstanding=400,
            defaults=2,
            active=True,
        )
        # Advance to trigger credit pressure
        for _ in range(5):
            s.advance()

        # Victory should still be recorded
        assert len(s.campaign.completed_paths) == 1
        assert s.campaign.completed_paths[0].path_id == "lawful_trade_house"

        failures = check_all_invariants(s)
        assert failures == []


# ---------------------------------------------------------------------------
# Campaign under compound system pressure
# ---------------------------------------------------------------------------

class TestCampaignUnderCompoundPressure:
    def test_campaign_stable_through_bankruptcy_edge(self, tmp_path):
        """Campaign state stays clean when player is at bankruptcy edge."""
        s = _fresh_session(tmp_path)
        s.campaign.completed = [
            MilestoneCompletion(milestone_id="m1", completed_day=10),
            MilestoneCompletion(milestone_id="m2", completed_day=15),
        ]
        s.captain.silver = 5
        s.captain.provisions = 2

        # Run until provisions run out
        for _ in range(5):
            s.advance()

        # No duplicate milestones
        ids = [m.milestone_id for m in s.campaign.completed]
        assert len(ids) == len(set(ids))

        failures = check_all_invariants(s)
        assert failures == []

    def test_stress_scenario_preserves_campaign(self, tmp_path):
        """The victory_then_stress scenario should keep campaign lawful."""
        from portlight.stress.runner import run_stress_scenario
        from portlight.stress.scenarios import STRESS_SCENARIOS

        scenario = STRESS_SCENARIOS["victory_then_stress"]
        report = run_stress_scenario(scenario)
        assert report.passed, (
            f"victory_then_stress had violations: "
            f"{[inv.name for inv in report.invariant_results]}"
        )

    def test_legitimization_pivot_campaign_clean(self, tmp_path):
        """Smuggler pivot scenario should not corrupt milestones."""
        from portlight.stress.runner import run_stress_scenario
        from portlight.stress.scenarios import STRESS_SCENARIOS

        scenario = STRESS_SCENARIOS["legitimization_pivot"]
        report = run_stress_scenario(scenario)
        assert report.passed, (
            f"legitimization_pivot had violations: "
            f"{[inv.name for inv in report.invariant_results]}"
        )

    @pytest.mark.parametrize("captain_type", ["merchant", "smuggler", "navigator"])
    def test_all_captains_campaign_clean_under_pressure(self, tmp_path, captain_type):
        """Each captain type keeps campaign clean under low-silver pressure."""
        s = _fresh_session(tmp_path, captain_type=captain_type)
        s.captain.silver = 10
        s.captain.provisions = 5

        for _ in range(10):
            s.advance()

        failures = check_all_invariants(s)
        assert failures == [], (
            f"{captain_type} had invariant failures under pressure: "
            f"{[(f.name, f.message) for f in failures]}"
        )
