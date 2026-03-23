"""Tests for Pass A — onboarding and decision clarity views.

Proves: welcome view, hint system, market flood explanation,
obligation deadline context, status view upkeep, guide command.
"""

from io import StringIO
from pathlib import Path

from rich.console import Console

from portlight.app import views
from portlight.app.session import GameSession
from portlight.engine.contracts import ContractBoard
from portlight.engine.models import (
    Captain,
    CargoItem,
    Port,
    Route,
    Ship,
    VoyageState,
    VoyageStatus,
    WorldState,
)


def _render(renderable) -> str:
    """Render a Rich renderable to plain text for assertions."""
    buf = StringIO()
    console = Console(file=buf, width=120, no_color=True)
    console.print(renderable)
    return buf.getvalue()


def _fresh_session(tmp_path: Path, captain_type: str = "merchant") -> GameSession:
    s = GameSession(tmp_path)
    s.new("TestCaptain", captain_type=captain_type)
    return s


# ---------------------------------------------------------------------------
# A1 — Welcome view
# ---------------------------------------------------------------------------

class TestWelcomeView:
    def test_welcome_view_contains_commands(self, tmp_path: Path):
        s = _fresh_session(tmp_path)
        panel = views.welcome_view(s.captain, s.captain_template, s.world, s.infra)
        text = _render(panel)
        assert "market" in text
        assert "buy" in text
        assert "routes" in text
        assert "contracts" in text

    def test_welcome_view_shows_captain_type(self, tmp_path: Path):
        s = _fresh_session(tmp_path, "smuggler")
        panel = views.welcome_view(s.captain, s.captain_template, s.world, s.infra)
        text = _render(panel)
        assert "TestCaptain" in text

    def test_welcome_view_shows_port_highlights(self, tmp_path: Path):
        s = _fresh_session(tmp_path)
        # Boost grain stock to trigger "cheap" threshold (ratio > 1.3)
        port = s.current_port
        grain_slot = next(sl for sl in port.market if sl.good_id == "grain")
        grain_slot.stock_current = 50  # 50/35 = 1.43 > 1.3
        panel = views.welcome_view(s.captain, s.captain_template, s.world, s.infra)
        text = _render(panel)
        assert "Porto Novo" in text
        assert "Grain" in text


# ---------------------------------------------------------------------------
# A1 — Hint line
# ---------------------------------------------------------------------------

class TestHintLine:
    def test_hint_low_provisions(self, tmp_path: Path):
        s = _fresh_session(tmp_path)
        s.captain.provisions = 3
        s._save()
        hint = views.hint_line(s.world, s.infra, s.board)
        assert hint is not None
        assert "provision" in hint.lower()

    def test_hint_ship_upgrade_close(self, tmp_path: Path):
        s = _fresh_session(tmp_path)
        # Cutter costs 450, put captain at 350 silver (100 away)
        s.captain.silver = 350
        s._save()
        hint = views.hint_line(s.world, s.infra, s.board)
        assert hint is not None
        assert "upgrade" in hint.lower() or "Cutter" in hint

    def test_hint_no_warehouse(self, tmp_path: Path):
        s = _fresh_session(tmp_path)
        # Fill cargo past 50%
        s.captain.cargo = [CargoItem(good_id="grain", quantity=20, cost_basis=100)]
        s._save()
        hint = views.hint_line(s.world, s.infra, s.board)
        assert hint is not None
        assert "warehouse" in hint.lower()

    def test_hint_returns_none_when_healthy(self, tmp_path: Path):
        s = _fresh_session(tmp_path)
        # Default state: 30 provisions, 550 silver (far from 800), empty cargo, no offers
        s.board.offers = []
        hint = views.hint_line(s.world, s.infra, s.board)
        # With no offers, no low provisions, no full cargo, no close upgrade => None
        assert hint is None


# ---------------------------------------------------------------------------
# A2 — Market flood explanation
# ---------------------------------------------------------------------------

class TestMarketFloodExplanation:
    def test_market_view_flood_hint(self, tmp_path: Path):
        s = _fresh_session(tmp_path)
        port = s.current_port
        # Simulate a flood penalty on grain
        grain_slot = next(sl for sl in port.market if sl.good_id == "grain")
        grain_slot.flood_penalty = 0.25
        panel = views.market_view(port, s.captain)
        text = _render(panel)
        assert "flooded" in text.lower()
        assert "-25%" in text
        assert "Trade elsewhere" in text or "recovery" in text

    def test_market_view_no_flood_no_hint(self, tmp_path: Path):
        s = _fresh_session(tmp_path)
        port = s.current_port
        # Ensure no flood
        for slot in port.market:
            slot.flood_penalty = 0.0
        panel = views.market_view(port, s.captain)
        text = _render(panel)
        assert "flooded" not in text.lower()


# ---------------------------------------------------------------------------
# A3 — Obligation deadline context
# ---------------------------------------------------------------------------

class TestObligationsDeadlineContext:
    def test_obligations_deadline_shows_days_left(self):
        from portlight.engine.contracts import ActiveContract, ContractFamily
        board = ContractBoard()
        board.active.append(ActiveContract(
            offer_id="test12345678", template_id="t1",
            family=ContractFamily.PROCUREMENT,
            title="Deliver Grain", accepted_day=1, deadline_day=20,
            destination_port_id="al_manar", good_id="grain",
            required_quantity=10, reward_silver=100,
        ))
        panel = views.obligations_view(board, 5)
        text = _render(panel)
        assert "15d left" in text

    def test_obligations_sail_time_context(self):
        """When destination port has a direct route, show estimated sail days."""
        # Build minimal world with route
        captain = Captain(
            name="Test", silver=500, provisions=30,
            ship=Ship(
                template_id="coastal_sloop", name="Test Sloop",
                hull=60, hull_max=60, cargo_capacity=30, speed=8,
                crew=3, crew_max=8,
            ),
        )
        world = WorldState(
            captain=captain,
            ports={
                "porto_novo": Port(id="porto_novo", name="Porto Novo", description="", region="Med"),
                "al_manar": Port(id="al_manar", name="Al-Manar", description="", region="Med"),
            },
            routes=[Route(port_a="porto_novo", port_b="al_manar", distance=24, danger=0.08)],
            voyage=VoyageState(
                origin_id="porto_novo", destination_id="porto_novo",
                distance=0, progress=0, status=VoyageStatus.IN_PORT,
            ),
            day=1,
        )

        # Create a board with an active contract to al_manar
        from portlight.engine.contracts import ActiveContract, ContractFamily
        board = ContractBoard()
        board.active.append(ActiveContract(
            offer_id="test12345678", template_id="t1",
            family=ContractFamily.PROCUREMENT,
            title="Deliver Grain", accepted_day=1, deadline_day=15,
            destination_port_id="al_manar", good_id="grain",
            required_quantity=10, delivered_quantity=0,
            reward_silver=100,
        ))

        panel = views.obligations_view(board, 1, world)
        text = _render(panel)
        # Distance 24, speed 8 => 3 days sail
        assert "3d sail" in text
        assert "Al-Manar" in text


# ---------------------------------------------------------------------------
# A4 — Status view enrichment
# ---------------------------------------------------------------------------

class TestStatusViewEnrichment:
    def test_status_daily_costs_with_infra(self, tmp_path: Path):
        s = _fresh_session(tmp_path)
        # Lease a warehouse to create upkeep
        from portlight.content.infrastructure import WAREHOUSE_TIERS
        from portlight.engine.infrastructure import WarehouseTier, lease_warehouse
        spec = WAREHOUSE_TIERS[WarehouseTier.DEPOT]
        lease_warehouse(s.infra, s.captain, "porto_novo", spec, s.world.day)
        s._save()
        panel = views.status_view(s.world, s.ledger, s.infra)
        text = _render(panel)
        assert "upkeep" in text.lower()
        assert "warehouse" in text.lower()

    def test_status_no_infra_clean(self, tmp_path: Path):
        s = _fresh_session(tmp_path)
        panel = views.status_view(s.world, s.ledger, s.infra)
        text = _render(panel)
        # No infrastructure, should not show upkeep or "Active:" line
        assert "upkeep" not in text.lower()


# ---------------------------------------------------------------------------
# A1 — Guide command output
# ---------------------------------------------------------------------------

class TestGuideCommand:
    def test_guide_command_output(self, tmp_path: Path, capsys):
        """Guide command prints grouped categories."""
        from typer.testing import CliRunner
        from portlight.app.cli import app
        runner = CliRunner()
        result = runner.invoke(app, ["guide"])
        assert result.exit_code == 0
        output = result.output
        assert "Trading" in output
        assert "Navigation" in output
        assert "Contracts" in output
        assert "Infrastructure" in output
        assert "Finance" in output
        assert "Career" in output
