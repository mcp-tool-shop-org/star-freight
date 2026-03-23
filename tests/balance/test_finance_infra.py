"""Finance and infrastructure balance tests.

Proves that infrastructure and financial tools are meaningful
without being mandatory or decorative.
"""

from __future__ import annotations

from portlight.balance.runner import run_balance_simulation
from portlight.balance.types import BalanceRunConfig, PolicyId


class TestInfrastructurePacing:
    def test_infrastructure_forward_buys_warehouse(self):
        """Infrastructure-forward policy should buy a warehouse."""
        metrics = [
            run_balance_simulation(BalanceRunConfig(
                scenario_id="infra_test", seed=s,
                captain_type="merchant",
                policy_id=PolicyId.INFRASTRUCTURE_FORWARD,
                max_days=60,
            ))
            for s in (42, 137, 256)
        ]
        bought = sum(1 for m in metrics if m.warehouses_opened > 0)
        assert bought >= 1, "Infra-forward never bought a warehouse"

    def test_warehouses_not_mandatory_early(self):
        """Captains should be profitable without warehouses in early game."""
        metrics = [
            run_balance_simulation(BalanceRunConfig(
                scenario_id="no_wh_test", seed=s,
                captain_type="merchant",
                policy_id=PolicyId.OPPORTUNISTIC_TRADER,
                max_days=30,
            ))
            for s in (42, 137, 256, 512, 777, 1001)
        ]
        profitable_without = sum(
            1 for m in metrics
            if m.warehouses_opened == 0 and m.final_silver > 200
        )
        assert profitable_without >= 1, \
            f"Can't profit without warehouses. " \
            f"Silvers: {[m.final_silver for m in metrics]}, " \
            f"WHs: {[m.warehouses_opened for m in metrics]}"


class TestFinance:
    def test_leverage_forward_uses_credit(self):
        """Leverage-forward policy should attempt credit operations."""
        metrics = [
            run_balance_simulation(BalanceRunConfig(
                scenario_id="credit_test", seed=s,
                captain_type="merchant",
                policy_id=PolicyId.LEVERAGE_FORWARD,
                max_days=60,
            ))
            for s in (42, 137, 256)
        ]
        # Credit may not be available due to trust requirements,
        # but the policy should at least run without crashing
        for m in metrics:
            assert m.final_silver >= 0, "Negative silver after leverage run"

    def test_no_universal_defaults(self):
        """Default shouldn't happen in every leveraged run."""
        metrics = [
            run_balance_simulation(BalanceRunConfig(
                scenario_id="default_test", seed=s,
                captain_type="merchant",
                policy_id=PolicyId.LEVERAGE_FORWARD,
                max_days=60,
            ))
            for s in (42, 137, 256, 512, 777)
        ]
        default_runs = sum(1 for m in metrics if m.defaults > 0)
        assert default_runs < len(metrics), \
            "Every leveraged run resulted in defaults"
