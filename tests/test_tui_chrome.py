"""TUI chrome (Item 4c) — live-key Footer on every tab, survives 100x30."""

from __future__ import annotations

from pathlib import Path

import pytest

textual = pytest.importorskip("textual", reason="textual not installed")

from textual.widgets import Footer  # noqa: E402

from portlight.app.session import GameSession  # noqa: E402
from portlight.app.tui.app import StarFreightApp  # noqa: E402


def _session(tmp_path: Path) -> GameSession:
    s = GameSession(tmp_path, slot="tui_chrome")
    s.new("Kael", seed=1)
    return s


@pytest.mark.asyncio
async def test_footer_present_with_live_keys(tmp_path: Path):
    s = _session(tmp_path)
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        footer = app.screen.query(Footer)
        assert footer, "no Footer on the dashboard"
        # The Services key we registered should be a live binding.
        keys = {b.key for b in app.BINDINGS if hasattr(b, "key")}
        assert "p" in keys and "g" in keys and "b" in keys


@pytest.mark.asyncio
async def test_all_tabs_survive_min_size(tmp_path: Path):
    s = _session(tmp_path)
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        for key in ("d", "c", "r", "m", "t", "j", "f", "question_mark", "d"):
            await pilot.press(key)
            await pilot.pause()
        # The app is still alive and on its main screen after touring every tab.
        assert app.is_running
