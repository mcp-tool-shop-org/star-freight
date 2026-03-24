"""Maritime term guard — ensures no Portlight vocabulary reaches the player.

This test renders all Star Freight TUI screens and asserts that none
of them contain forbidden maritime terms. If this test fails, someone
has leaked sea-trade language into the space-trade surface.

This is a CI guardrail, not a one-time audit.
"""

from __future__ import annotations

import re

import pytest

from rich.console import Console

from portlight.engine.sf_campaign import CampaignState, dock_at_station
from portlight.engine.crew import recruit
from portlight.content.star_freight import create_thal, create_varek
from portlight.app.sf_views import (
    captains_view,
    crew_screen,
    dashboard,
    station_screen,
    routes_screen,
    market_screen,
    faction_screen,
    journal_screen,
)


# ---------------------------------------------------------------------------
# Forbidden terms — if any of these appear in rendered output, the test fails
# ---------------------------------------------------------------------------

FORBIDDEN_TERMS = [
    "portlight",
    r"\bsail\b",       # "sail" as word, not "assail" or "detail"
    r"\bsailing\b",
    "voyage",
    r"\bsilver\b",      # currency, not color
    "provisions",
    "safe harbor",
    "broadside",
    r"\brake\b",        # naval maneuver, not "brake" — \brake\b matches "rake"
    r"\bharbor\b",
    "harbour",
    "dock master",
    r"\banchor\b",
    r"\bat sea\b",
    r"\bin port\b",
    "shipyard",
    r"\bnaval\b",
    "compass rose",
    r"\bfelucca\b",
    r"\bbarge\b",
    "maritime",
    "nautical",
]


def _render_to_text(renderable) -> str:
    """Render a Rich renderable to plain text."""
    console = Console(width=120, force_terminal=True, no_color=True)
    with console.capture() as capture:
        console.print(renderable)
    return capture.get()


def _make_state() -> CampaignState:
    """Create a campaign state with crew for rendering."""
    state = CampaignState()
    recruit(state.crew, create_thal())
    recruit(state.crew, create_varek())
    dock_at_station(state, "meridian_exchange")
    return state


class TestMaritimeGuard:
    """Ensure no maritime vocabulary in Star Freight TUI screens."""

    @pytest.fixture
    def state(self):
        return _make_state()

    def _check_forbidden(self, text: str, screen_name: str):
        """Assert no forbidden terms in rendered text."""
        text_lower = text.lower()
        for term in FORBIDDEN_TERMS:
            if term.startswith(r"\b"):
                # Regex word-boundary match
                pattern = term
                matches = re.findall(pattern, text_lower)
                assert not matches, (
                    f"Forbidden maritime term '{term}' found in {screen_name}: "
                    f"matches={matches}"
                )
            else:
                assert term not in text_lower, (
                    f"Forbidden maritime term '{term}' found in {screen_name}"
                )

    def test_captains_view_clean(self, state):
        text = _render_to_text(captains_view(state))
        self._check_forbidden(text, "captains_view")

    def test_crew_screen_clean(self, state):
        text = _render_to_text(crew_screen(state))
        self._check_forbidden(text, "crew_screen")

    def test_dashboard_clean(self, state):
        text = _render_to_text(dashboard(state))
        self._check_forbidden(text, "dashboard")

    def test_station_screen_clean(self, state):
        text = _render_to_text(station_screen(state))
        self._check_forbidden(text, "station_screen")

    def test_routes_screen_clean(self, state):
        text = _render_to_text(routes_screen(state))
        self._check_forbidden(text, "routes_screen")

    def test_market_screen_clean(self, state):
        text = _render_to_text(market_screen(state))
        self._check_forbidden(text, "market_screen")

    def test_faction_screen_clean(self, state):
        text = _render_to_text(faction_screen(state))
        self._check_forbidden(text, "faction_screen")

    def test_journal_screen_clean(self, state):
        text = _render_to_text(journal_screen(state))
        self._check_forbidden(text, "journal_screen")

    def test_help_view_clean(self, state):
        """Help view rendered inside ContentArea must be maritime-free."""
        from portlight.app.tui.screens.dashboard import ContentArea
        from portlight.app.session import GameSession
        session = GameSession()
        content = ContentArea(session)
        help_renderable = content._help_view()
        text = _render_to_text(help_renderable)
        self._check_forbidden(text, "help_view")

    def test_theme_css_clean(self):
        """Theme CSS should not contain maritime references."""
        from portlight.app.tui.theme import APP_CSS
        css_lower = APP_CSS.lower()
        for term in ["ocean", "sea foam", "maritime", "voyage", "sail", "ship-art", "wave"]:
            assert term not in css_lower, f"Maritime term '{term}' in APP_CSS"

    def test_app_title_clean(self):
        """App title should say Star Freight, not Portlight."""
        from portlight.app.tui.app import StarFreightApp
        assert StarFreightApp.TITLE == "Star Freight"
        assert "Portlight" not in StarFreightApp.TITLE

    def test_splash_clean(self):
        """Splash screen should not contain Portlight branding."""
        from portlight.app.tui.screens.dashboard import SPLASH_TITLE
        assert "Portlight" not in SPLASH_TITLE
        assert "portlight" not in SPLASH_TITLE.lower()
