"""Station services numbered picker (Item 4a / Harbor analogue)."""

from __future__ import annotations

from pathlib import Path

import pytest

textual = pytest.importorskip("textual", reason="textual not installed")

from portlight.app.session import GameSession  # noqa: E402
from portlight.app.tui.app import StarFreightApp  # noqa: E402
from portlight.app.tui.screens.services import (  # noqa: E402
    ServicesDialog,
    _build_options,
    _run_service,
)


class _App:
    """Minimal app stub for unit-testing the service runners."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify(self, msg: str, **kw) -> None:
        self.messages.append(msg)

    def refresh_views(self) -> None:
        pass


def _session(tmp_path: Path) -> GameSession:
    s = GameSession(tmp_path, slot="tui_services")
    s.new("Kael", seed=1)
    return s


def test_build_options_lists_repair_refuel_hire(tmp_path: Path):
    s = _session(tmp_path)
    st = s.sf_campaign
    st.ship_hull = 1000  # needs repair
    st.ship_fuel = 3  # needs fuel
    ids = [sid for sid, _ in _build_options(st)]
    assert "repair" in ids
    assert "refuel" in ids
    assert any(sid.startswith("hire:") for sid in ids)  # Meridian hires Sera


def test_repair_service_repairs_affordable(tmp_path: Path):
    s = _session(tmp_path)
    st = s.sf_campaign
    st.ship_hull = 1000
    st.credits = 300  # Meridian repair 3/pt -> 100 pts
    _run_service(_App(), s, "repair")
    assert st.ship_hull == 1100
    assert st.credits == 0


def test_refuel_service_fills_affordable(tmp_path: Path):
    s = _session(tmp_path)
    st = s.sf_campaign
    st.ship_fuel = 3
    st.credits = 500
    _run_service(_App(), s, "refuel")
    assert st.ship_fuel == st.ship_fuel_max  # 5 days needed, easily afforded


def test_hire_service_recruits_crew(tmp_path: Path):
    s = _session(tmp_path)
    st = s.sf_campaign
    before = len(st.crew.members)
    _run_service(_App(), s, "hire:sera_vale")
    assert len(st.crew.members) == before + 1


@pytest.mark.asyncio
async def test_p_key_opens_services_when_docked(tmp_path: Path):
    s = _session(tmp_path)
    s.sf_campaign.ship_hull = 1000  # ensure at least one option exists
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.press("p")
        await pilot.pause()
        assert isinstance(app.screen, ServicesDialog)


@pytest.mark.asyncio
async def test_services_blocked_in_transit(tmp_path: Path):
    s = _session(tmp_path)
    s.sf_campaign.in_transit = True
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.press("p")
        await pilot.pause()
        assert not isinstance(app.screen, ServicesDialog)
