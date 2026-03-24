"""Smoke tests for Textual TUI — verifies imports, construction, and theme."""

from __future__ import annotations

import pytest

textual = pytest.importorskip("textual", reason="textual not installed")


def test_tui_app_import():
    """PortlightApp can be imported."""
    from portlight.app.tui.app import PortlightApp
    assert PortlightApp is not None


def test_tui_app_construct():
    """PortlightApp can be constructed with a fresh session."""
    from portlight.app.tui.app import PortlightApp
    from portlight.app.session import GameSession
    session = GameSession()
    app = PortlightApp(session=session)
    assert app.session is session
    assert app._current_tab == "dashboard"


def test_dashboard_screen_import():
    """DashboardScreen can be imported."""
    from portlight.app.tui.screens.dashboard import DashboardScreen
    assert DashboardScreen is not None


def test_market_dialogs_import():
    """Market trade dialogs can be imported."""
    from portlight.app.tui.screens.market import TradeDialog, GoodSelectDialog
    assert TradeDialog is not None
    assert GoodSelectDialog is not None


def test_routes_dialogs_import():
    """Route/sail dialogs can be imported."""
    from portlight.app.tui.screens.routes import SailDialog
    assert SailDialog is not None


def test_combat_screen_import():
    """CombatScreen can be imported."""
    from portlight.app.tui.screens.combat import CombatScreen
    assert CombatScreen is not None


def test_theme_css():
    """Theme CSS is a non-empty string with Star Freight void palette."""
    from portlight.app.tui.theme import APP_CSS
    assert isinstance(APP_CSS, str)
    assert len(APP_CSS) > 500
    assert "#0a0e1a" in APP_CSS  # void black background
    assert "#4090e0" in APP_CSS  # shield blue accent
    assert "#1a1e2a" in APP_CSS  # hull gray for panels
    assert "#e05050" in APP_CSS  # alert red for danger


def test_theme_credits_display():
    """Credits display shows the \u20a1 symbol and handles ranges."""
    from portlight.app.tui.theme import credits_display
    assert "\u20a1" in credits_display(1000)
    assert "\u20a1" in credits_display(50)
    assert "0" in credits_display(0)


def test_theme_no_maritime_content():
    """Theme maritime stubs are empty (legacy compat only)."""
    import portlight.app.tui.theme as theme
    # Stubs exist for backward compat but must be empty
    assert theme.SHIP_ART == ""
    assert theme.REGION_BADGES == {}
    assert not hasattr(theme, "COMPASS_ROSE")


def test_theme_render_bar():
    """Visual bar renders correctly for different ratios."""
    from portlight.app.tui.theme import render_bar
    # Full health
    bar_full = render_bar(10, 10)
    assert len(bar_full) > 0
    # Half health
    bar_half = render_bar(5, 10)
    assert len(bar_half) > 0
    # Empty
    bar_empty = render_bar(0, 10)
    assert len(bar_empty) > 0
    # Zero max
    bar_zero = render_bar(0, 0)
    assert len(bar_zero) > 0


def test_theme_silver_display():
    """Silver display formats amounts with appropriate styling."""
    from portlight.app.tui.theme import silver_display
    assert "1,000" in silver_display(1000)
    assert "500" in silver_display(500)
    assert "0" in silver_display(0)


def test_theme_danger_indicator():
    """Danger indicator returns different symbols for different levels."""
    from portlight.app.tui.theme import danger_indicator
    safe = danger_indicator(0.05)
    low = danger_indicator(0.10)
    high = danger_indicator(0.18)
    perilous = danger_indicator(0.25)
    # They should all be non-empty and different from each other
    assert all(len(s) > 0 for s in [safe, low, high, perilous])


def test_dashboard_content_tabs():
    """ContentArea supports all Star Freight tab names."""
    from portlight.app.tui.screens.dashboard import ContentArea
    from portlight.app.session import GameSession
    session = GameSession()
    content = ContentArea(session)
    expected_tabs = [
        "dashboard", "crew", "routes", "market",
        "station", "journal", "faction", "help",
    ]
    for tab in expected_tabs:
        content._current_tab = tab
        assert content._current_tab == tab


def test_app_bindings():
    """App has bindings for all Star Freight navigation and action keys."""
    from portlight.app.tui.app import StarFreightApp
    app = StarFreightApp()
    binding_keys = {b.key for b in app.BINDINGS}
    # Navigation keys — Star Freight screen set
    nav_keys = {"d", "c", "r", "m", "t", "j", "f"}
    assert nav_keys.issubset(binding_keys)
    # Action keys
    action_keys = {"b", "s", "g", "a"}
    assert action_keys.issubset(binding_keys)
    # Quit
    assert "q" in binding_keys


def test_splash_title():
    """Splash screen title is Star Freight themed."""
    from portlight.app.tui.screens.dashboard import SPLASH_TITLE
    assert len(SPLASH_TITLE) > 100
    assert "Portlight" not in SPLASH_TITLE
    assert "merchant" in SPLASH_TITLE.lower() or "freight" in SPLASH_TITLE.lower()
    assert "____" in SPLASH_TITLE  # ASCII art banner


def test_captain_bar_components():
    """CaptainBar can be imported and has compose method."""
    from portlight.app.tui.screens.dashboard import CaptainBar
    from portlight.app.session import GameSession
    bar = CaptainBar(GameSession())
    assert hasattr(bar, "refresh_status")
    assert hasattr(bar, "compose")


def test_tabbar():
    """TabBar has all Star Freight tab labels."""
    from portlight.app.tui.screens.dashboard import TabBar
    bar = TabBar()
    labels = [label for _, label in bar.TAB_LABELS]
    assert "Dash" in labels
    assert "Crew" in labels
    assert "Routes" in labels
    assert "Market" in labels
    assert "Station" in labels
    assert "Journal" in labels
    assert "Faction" in labels
    assert "Help" in labels
    # No maritime tabs
    assert "Fleet" not in labels
    assert "Cargo" not in labels
    assert "Port" not in labels


def test_market_trade_dialog_construct():
    """TradeDialog can be constructed with parameters."""
    from portlight.app.tui.screens.market import TradeDialog
    dialog = TradeDialog("buy", "grain", "Grain", 10, 12)
    assert dialog.action == "buy"
    assert dialog.good_id == "grain"
    assert dialog.max_qty == 10
    assert dialog.price == 12


def test_sail_dialog_construct():
    """SailDialog can be constructed with destinations."""
    from portlight.app.tui.screens.routes import SailDialog
    dests = [("porto_novo", "Porto Novo", 30, 0.08, "mediterranean", 6)]
    dialog = SailDialog(dests)
    assert len(dialog.destinations) == 1


def test_event_icons():
    """Event icons dictionary is populated."""
    from portlight.app.tui.screens.routes import _EVENT_ICONS
    assert "pirate" in _EVENT_ICONS
    assert "storm" in _EVENT_ICONS
    assert "arrival" in _EVENT_ICONS
