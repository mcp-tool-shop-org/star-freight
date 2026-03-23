"""Tests for the interactive captain selection screen.

Covers: view rendering, difficulty tags, data completeness, width adaptation,
and the interactive selection flow.
"""

from __future__ import annotations


from rich.console import Console

from portlight.app import formatting as fmt
from portlight.app import views
from portlight.engine.captain_identity import (
    CAPTAIN_COLORS,
    CAPTAIN_ORDER,
    CAPTAIN_QUOTES,
    CAPTAIN_TEMPLATES,
    CaptainType,
)


class TestCaptainSelectData:
    """Captain selection metadata is complete for all archetypes."""

    def test_all_captains_have_quotes(self):
        for ct in CAPTAIN_ORDER:
            assert ct in CAPTAIN_QUOTES, f"{ct.value} missing quote"
            assert len(CAPTAIN_QUOTES[ct]) > 5, f"{ct.value} quote too short"

    def test_all_captains_have_colors(self):
        for ct in CAPTAIN_ORDER:
            assert ct in CAPTAIN_COLORS, f"{ct.value} missing color"

    def test_order_covers_all_playable_types(self):
        playable = {ct for ct in CaptainType if ct in CAPTAIN_TEMPLATES}
        ordered = set(CAPTAIN_ORDER)
        assert ordered == playable, f"Missing from order: {playable - ordered}"

    def test_order_has_nine_entries(self):
        assert len(CAPTAIN_ORDER) == 9


class TestDifficultyTag:
    """Difficulty tag thresholds produce correct labels."""

    def test_easy(self):
        tag = fmt.difficulty_tag(700)
        assert "Easy" in tag

    def test_standard(self):
        tag = fmt.difficulty_tag(550)
        assert "Standard" in tag

    def test_moderate(self):
        for silver in (500, 475, 450, 425, 400, 350):
            tag = fmt.difficulty_tag(silver)
            assert "Moderate" in tag, f"Expected Moderate for {silver}s, got {tag}"

    def test_hard(self):
        tag = fmt.difficulty_tag(300)
        assert "Hard" in tag

    def test_boundary_349(self):
        tag = fmt.difficulty_tag(349)
        assert "Hard" in tag

    def test_boundary_350(self):
        tag = fmt.difficulty_tag(350)
        assert "Moderate" in tag


class TestRosterView:
    """Roster view renders without errors for all captains."""

    def test_renders_at_wide_width(self):
        result = views.captain_roster_view(
            CAPTAIN_TEMPLATES, CAPTAIN_ORDER, CAPTAIN_QUOTES, CAPTAIN_COLORS,
            console_width=100,
        )
        # Should be renderable without error
        c = Console(width=100, force_terminal=True, file=None, no_color=True)
        with c.capture() as cap:
            c.print(result)
        output = cap.get()
        assert "Choose Your Captain" in output
        # All 9 captain names should appear
        for ct in CAPTAIN_ORDER:
            tmpl = CAPTAIN_TEMPLATES[ct]
            assert tmpl.name in output, f"{tmpl.name} not in roster"

    def test_renders_at_narrow_width(self):
        result = views.captain_roster_view(
            CAPTAIN_TEMPLATES, CAPTAIN_ORDER, CAPTAIN_QUOTES, CAPTAIN_COLORS,
            console_width=50,
        )
        c = Console(width=50, force_terminal=True, file=None, no_color=True)
        with c.capture() as cap:
            c.print(result)
        output = cap.get()
        assert "Choose Your Captain" in output

    def test_renders_at_medium_width(self):
        result = views.captain_roster_view(
            CAPTAIN_TEMPLATES, CAPTAIN_ORDER, CAPTAIN_QUOTES, CAPTAIN_COLORS,
            console_width=65,
        )
        c = Console(width=65, force_terminal=True, file=None, no_color=True)
        with c.capture() as cap:
            c.print(result)
        output = cap.get()
        assert "Choose Your Captain" in output


class TestSpotlightView:
    """Spotlight view renders correctly for every captain type."""

    def test_all_captains_render(self):
        c = Console(width=90, force_terminal=True, file=None, no_color=True)
        for idx, ct in enumerate(CAPTAIN_ORDER):
            tmpl = CAPTAIN_TEMPLATES[ct]
            color = CAPTAIN_COLORS.get(ct, "blue")
            result = views.captain_spotlight_view(tmpl, idx + 1, 9, color=color)
            with c.capture() as cap:
                c.print(result)
            output = cap.get()
            assert tmpl.name in output, f"{tmpl.name} not in spotlight"
            assert tmpl.title in output
            assert "Starting Position" in output
            assert "Trade Profile" in output
            assert "Strengths" in output
            assert "Weaknesses" in output

    def test_corsair_shows_factions(self):
        tmpl = CAPTAIN_TEMPLATES[CaptainType.CORSAIR]
        result = views.captain_spotlight_view(tmpl, 5, 9, color="red")
        c = Console(width=90, force_terminal=True, file=None, no_color=True)
        with c.capture() as cap:
            c.print(result)
        output = cap.get()
        assert "Crimson Tide" in output
        assert "Deep Reef" in output

    def test_privateer_shows_cutter(self):
        tmpl = CAPTAIN_TEMPLATES[CaptainType.PRIVATEER]
        result = views.captain_spotlight_view(tmpl, 4, 9, color="blue")
        c = Console(width=90, force_terminal=True, file=None, no_color=True)
        with c.capture() as cap:
            c.print(result)
        output = cap.get()
        assert "Swift Cutter" in output


class TestConfirmView:
    """Confirmation view renders with captain name and details."""

    def test_confirm_shows_name_and_type(self):
        tmpl = CAPTAIN_TEMPLATES[CaptainType.SMUGGLER]
        result = views.captain_confirm_view("Blackbeard", tmpl, color="magenta")
        c = Console(width=60, force_terminal=True, file=None, no_color=True)
        with c.capture() as cap:
            c.print(result)
        output = cap.get()
        assert "Blackbeard" in output
        assert "The Smuggler" in output
        assert "Set Sail?" in output
        assert "Palm Cove" in output


class TestInteractiveSelect:
    """Integration test for the interactive selection flow."""

    def test_direct_type_flag_still_works(self):
        """Using --type directly should bypass interactive selection."""
        import tempfile
        from pathlib import Path
        from portlight.app.session import GameSession

        with tempfile.TemporaryDirectory() as tmp:
            s = GameSession(Path(tmp))
            s.new("Tester", captain_type="merchant")
            assert s.world is not None
            assert s.world.captain.captain_type == "merchant"

    def test_all_captains_creatable(self):
        """Every captain type from CAPTAIN_ORDER can start a game."""
        import tempfile
        from pathlib import Path
        from portlight.app.session import GameSession

        for ct in CAPTAIN_ORDER:
            with tempfile.TemporaryDirectory() as tmp:
                s = GameSession(Path(tmp))
                s.new("Tester", captain_type=ct.value)
                assert s.world is not None, f"{ct.value} failed to create game"
                assert s.world.captain.captain_type == ct.value
