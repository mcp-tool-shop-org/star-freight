"""Version alignment tests."""

import re
from pathlib import Path

import portlight
from typer.testing import CliRunner
from portlight.app.cli import app


def _pyproject_version() -> str:
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    for line in pyproject.read_text().splitlines():
        if line.startswith("version"):
            return line.split('"')[1]
    raise RuntimeError("version not found in pyproject.toml")


def test_init_version_matches_pyproject():
    assert portlight.__version__ == _pyproject_version()


def test_version_is_valid_semver():
    assert re.match(r"^\d+\.\d+\.\d+$", portlight.__version__)


def test_version_command():
    runner = CliRunner()
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert portlight.__version__ in result.output
