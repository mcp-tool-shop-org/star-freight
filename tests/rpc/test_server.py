"""Tests for the JSON-RPC server — contract tests for Phase 7A."""

import io
import json
import pytest

from portlight.rpc.server import RpcServer
from portlight.rpc.protocol import NO_ACTIVE_GAME


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_server(with_game: bool = True) -> RpcServer:
    """Create an RpcServer, optionally with a loaded game session."""
    if with_game:
        from portlight.app.session import GameSession
        session = GameSession()
        session.new("TestCaptain", captain_type="merchant")
        return RpcServer(session=session)
    return RpcServer(session=None)


def _call(server: RpcServer, method: str, params: dict | None = None,
          req_id: int = 1) -> dict:
    """Send a JSON-RPC request and parse the response."""
    req = {"jsonrpc": "2.0", "method": method, "id": req_id}
    if params:
        req["params"] = params
    raw_response = server.dispatch(json.dumps(req))
    return json.loads(raw_response)


# ---------------------------------------------------------------------------
# ping
# ---------------------------------------------------------------------------

class TestPing:
    def test_ping_returns_ok(self):
        server = _make_server(with_game=False)
        resp = _call(server, "ping")
        assert resp["result"]["status"] == "ok"
        assert "version" in resp["result"]

    def test_ping_works_without_game(self):
        server = _make_server(with_game=False)
        resp = _call(server, "ping")
        assert resp["result"]["status"] == "ok"


# ---------------------------------------------------------------------------
# get_roster
# ---------------------------------------------------------------------------

class TestGetRoster:
    def test_returns_crew_list(self):
        server = _make_server()
        resp = _call(server, "get_roster")
        assert "error" not in resp
        roster = resp["result"]
        assert isinstance(roster["crew"], list)
        assert roster["count"] >= 2  # thal + varek from sf_campaign default

    def test_crew_shape(self):
        server = _make_server()
        resp = _call(server, "get_roster")
        member = resp["result"]["crew"][0]
        required_keys = {"id", "name", "civilization", "role", "hp", "hp_max",
                         "speed", "morale", "loyalty_tier", "status"}
        assert required_keys.issubset(member.keys())

    def test_no_game_returns_error(self):
        server = _make_server(with_game=False)
        resp = _call(server, "get_roster")
        assert "error" in resp
        assert resp["error"]["code"] == NO_ACTIVE_GAME


# ---------------------------------------------------------------------------
# get_crew_member
# ---------------------------------------------------------------------------

class TestGetCrewMember:
    def test_get_thal(self):
        server = _make_server()
        resp = _call(server, "get_crew_member", {"id": "thal_communion"})
        assert "error" not in resp
        assert resp["result"]["id"] == "thal_communion"
        assert resp["result"]["civilization"] == "keth"

    def test_unknown_id(self):
        server = _make_server()
        resp = _call(server, "get_crew_member", {"id": "nobody"})
        assert "error" in resp

    def test_missing_id_param(self):
        server = _make_server()
        resp = _call(server, "get_crew_member", {})
        assert "error" in resp


# ---------------------------------------------------------------------------
# get_campaign
# ---------------------------------------------------------------------------

class TestGetCampaign:
    def test_returns_summary(self):
        server = _make_server()
        resp = _call(server, "get_campaign")
        result = resp["result"]
        assert "credits" in result
        assert "day" in result
        assert "current_station" in result
        assert "crew_count" in result

    def test_no_game_returns_error(self):
        server = _make_server(with_game=False)
        resp = _call(server, "get_campaign")
        assert "error" in resp


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_unknown_method(self):
        server = _make_server()
        resp = _call(server, "nonexistent_method")
        assert resp["error"]["code"] == -32601

    def test_parse_error(self):
        server = _make_server()
        raw = server.dispatch("not json at all")
        resp = json.loads(raw)
        assert resp["error"]["code"] == -32700

    def test_malformed_request(self):
        server = _make_server()
        raw = server.dispatch('{"jsonrpc":"2.0"}')  # missing method
        resp = json.loads(raw)
        assert resp["error"]["code"] == -32700


# ---------------------------------------------------------------------------
# Stdio loop
# ---------------------------------------------------------------------------

class TestStdioLoop:
    def test_run_processes_lines(self):
        server = _make_server(with_game=False)
        requests = [
            json.dumps({"jsonrpc": "2.0", "method": "ping", "id": 1}),
            json.dumps({"jsonrpc": "2.0", "method": "shutdown", "id": 2}),
        ]
        input_stream = io.StringIO("\n".join(requests) + "\n")
        output_stream = io.StringIO()

        server.run(input_stream=input_stream, output_stream=output_stream)

        output_stream.seek(0)
        lines = [l.strip() for l in output_stream.readlines() if l.strip()]
        assert len(lines) == 2

        ping_resp = json.loads(lines[0])
        assert ping_resp["result"]["status"] == "ok"

        shutdown_resp = json.loads(lines[1])
        assert shutdown_resp["result"]["status"] == "shutting_down"

    def test_run_handles_eof(self):
        server = _make_server(with_game=False)
        input_stream = io.StringIO("")  # empty = immediate EOF
        output_stream = io.StringIO()
        server.run(input_stream=input_stream, output_stream=output_stream)
        # Should exit cleanly, no crash

    def test_run_skips_blank_lines(self):
        server = _make_server(with_game=False)
        requests = [
            "",
            json.dumps({"jsonrpc": "2.0", "method": "ping", "id": 1}),
            "",
            json.dumps({"jsonrpc": "2.0", "method": "shutdown", "id": 2}),
        ]
        input_stream = io.StringIO("\n".join(requests) + "\n")
        output_stream = io.StringIO()
        server.run(input_stream=input_stream, output_stream=output_stream)

        output_stream.seek(0)
        lines = [l.strip() for l in output_stream.readlines() if l.strip()]
        assert len(lines) == 2
