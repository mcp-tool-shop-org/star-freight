"""Tests for JSON-RPC 2.0 protocol types."""

import json
import pytest

from portlight.rpc.protocol import (
    Request,
    Response,
    ErrorResponse,
    crew_member_to_dict,
    campaign_summary,
)


class TestRequest:
    def test_from_json_minimal(self):
        raw = '{"jsonrpc":"2.0","method":"ping","id":1}'
        req = Request.from_json(raw)
        assert req.method == "ping"
        assert req.id == 1
        assert req.params == {}

    def test_from_json_with_params(self):
        raw = '{"jsonrpc":"2.0","method":"get_crew_member","id":2,"params":{"id":"thal"}}'
        req = Request.from_json(raw)
        assert req.method == "get_crew_member"
        assert req.params == {"id": "thal"}

    def test_roundtrip(self):
        req = Request(method="ping", id=1)
        raw = req.to_json()
        parsed = json.loads(raw)
        assert parsed["method"] == "ping"
        assert parsed["jsonrpc"] == "2.0"


class TestResponse:
    def test_success_json(self):
        resp = Response(id=1, result={"status": "ok"})
        parsed = json.loads(resp.to_json())
        assert parsed["id"] == 1
        assert parsed["result"]["status"] == "ok"
        assert "error" not in parsed

    def test_null_result(self):
        resp = Response(id=1, result=None)
        parsed = json.loads(resp.to_json())
        assert parsed["result"] is None


class TestErrorResponse:
    def test_error_json(self):
        resp = ErrorResponse(id=1, code=-32601, message="Method not found")
        parsed = json.loads(resp.to_json())
        assert parsed["error"]["code"] == -32601
        assert parsed["error"]["message"] == "Method not found"
        assert "result" not in parsed

    def test_error_with_data(self):
        resp = ErrorResponse(id=1, code=-32602, message="Bad param", data={"field": "id"})
        parsed = json.loads(resp.to_json())
        assert parsed["error"]["data"] == {"field": "id"}


class TestCrewMemberSerialization:
    def test_crew_member_to_dict(self):
        from portlight.content.star_freight import create_thal
        thal = create_thal()
        d = crew_member_to_dict(thal)
        assert d["id"] == "thal_communion"
        assert d["name"] == "Thal"
        assert d["civilization"] == "keth"
        assert d["role"] == "engineer"
        assert isinstance(d["hp"], int)
        assert isinstance(d["abilities"], list)
        # Must be JSON-serializable
        json.dumps(d)


class TestCampaignSummary:
    def test_summary_shape(self):
        from portlight.engine.sf_campaign import CampaignState
        from portlight.engine.crew import recruit
        from portlight.content.star_freight import create_thal

        state = CampaignState()
        recruit(state.crew, create_thal())
        summary = campaign_summary(state)

        assert summary["credits"] == 500
        assert summary["day"] == 1
        assert summary["current_station"] == "meridian_exchange"
        assert summary["crew_count"] == 1
        json.dumps(summary)  # must be serializable
