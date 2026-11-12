"""Player-facing surfaces must tell people to run starfreight, not portlight.

The Python package is still named portlight until the fork rename.
That is an import-path fact. It must not leak into command copy.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from portlight.app.cli import app
from portlight.app.tui.app import StarFreightApp

ROOT = Path(__file__).resolve().parent.parent

# Command copy and install hints — not Python imports.
FORBIDDEN_PLAYER_COPY = [
    "portlight new",
    "portlight tui",
    "portlight contracts",
    "portlight obligations",
    "portlight advance",
    "Usage: portlight",
    "[cyan]portlight",
    "[bold]portlight",
    "pip install portlight",
    "portlight-print-and-play.pdf",
]

PLAYER_FACING_FILES = [
    ROOT / "src" / "portlight" / "app" / "cli.py",
    ROOT / "src" / "portlight" / "app" / "views.py",
    ROOT / "src" / "portlight" / "app" / "combat_views.py",
    ROOT / "src" / "portlight" / "app" / "tui" / "app.py",
    ROOT / "src" / "portlight" / "printandplay" / "rules.py",
    ROOT / "src" / "portlight" / "printandplay" / "generator.py",
]


def test_missing_save_points_at_starfreight_new():
    runner = CliRunner()
    result = runner.invoke(app, ["captain"])
    assert result.exit_code == 1
    assert "starfreight new" in result.output
    assert "portlight new" not in result.output


def test_tui_title_is_star_freight():
    assert StarFreightApp.TITLE == "Star Freight"


def test_player_facing_files_do_not_recommend_portlight_commands():
    for path in PLAYER_FACING_FILES:
        text = path.read_text(encoding="utf-8")
        for needle in FORBIDDEN_PLAYER_COPY:
            assert needle not in text, f"{path.name} still tells the player to use '{needle}'"
