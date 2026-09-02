"""Live session boots Star Freight overlay, not Portlight's ocean world."""

from pathlib import Path

from typer.testing import CliRunner

from portlight.app.cli import app
from portlight.app.session import GameSession
from portlight.engine.sf_campaign import execute_trade, hire_crew, travel_to, run_combat, resolve_transit


def test_new_docks_at_meridian_exchange(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    s = GameSession(tmp_path)
    s.new("Kael", seed=7)
    assert s.world is None
    assert s.sf_campaign is not None
    state = s.sf_campaign
    assert state.captain_name == "Kael"
    assert state.current_station == "meridian_exchange"
    assert state.crew.members == []
    assert state.credits == 490  # 500 minus Meridian docking fee
    assert state.reputation["compact"] == -25
    save = tmp_path / "saves"
    sf_files = list(save.glob("*.sf.json"))
    assert sf_files, "Star Freight save should be written as .sf.json"


def test_save_and_load_roundtrip(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    s = GameSession(tmp_path, slot="roundtrip")
    s.new("Kael", seed=11)
    s.sf_campaign.credits = 321
    hire_crew(s.sf_campaign, "sera_vale")
    s._save()

    s2 = GameSession(tmp_path, slot="roundtrip")
    assert s2.load()
    assert s2.world is None
    assert s2.sf_campaign.captain_name == "Kael"
    assert s2.sf_campaign.credits == 321 - 40  # Sera pay_rate
    assert [m.id for m in s2.sf_campaign.crew.members] == ["sera_vale"]


def test_buy_and_hire_on_live_session(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    s = GameSession(tmp_path)
    s.new("Kael", seed=3)
    state = s.sf_campaign
    bought = execute_trade(state, "medical_supplies", "buy", 1)
    assert "error" not in bought, bought
    assert "medical_supplies" in state.ship_cargo
    hired = hire_crew(state, "sera_vale")
    assert "error" not in hired, hired
    assert hired["hired"] == "Sera"


def test_travel_reaches_communion_or_resolves_encounter(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    s = GameSession(tmp_path)
    s.new("Kael", seed=1)
    state = s.sf_campaign
    result = travel_to(state, "communion_relay")
    assert "error" not in result, result
    if result.get("encounter"):
        combat = run_combat(state, result["encounter"], strategy="aggressive")
        arrive = resolve_transit(state)
        assert "error" not in arrive, arrive
        assert combat.outcome is not None
    assert state.current_station == "communion_relay"
    assert state.in_transit is False


def test_cli_new_prints_meridian(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["new", "Kael", "--seed", "9"])
    assert result.exit_code == 0, result.output
    assert "Meridian Exchange" in result.output
    assert "porto_novo" not in result.output.lower()


def test_cli_status_after_new(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    assert runner.invoke(app, ["new", "Kael", "--seed", "9"]).exit_code == 0
    status = runner.invoke(app, ["status"])
    assert status.exit_code == 0, status.output
    assert "Dashboard" in status.output or "Credits" in status.output
    station = runner.invoke(app, ["station"])
    assert station.exit_code == 0, station.output
    assert "Meridian Exchange" in station.output


def test_cli_ancestor_hunt_is_blocked(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    assert runner.invoke(app, ["new", "Kael", "--seed", "9"]).exit_code == 0
    result = runner.invoke(app, ["hunt"])
    assert result.exit_code == 1
    assert "ocean ancestor" in result.output
