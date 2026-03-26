"""JSON-RPC 2.0 stdio server for Star Freight.

Reads newline-delimited JSON from stdin, writes responses to stdout.
Designed to be spawned as a subprocess by graphical clients (Godot, etc.).

The RPC surface is intentionally tiny for Phase 7A:
  - ping          → liveness check
  - get_roster    → crew list for roster scene
  - get_campaign  → minimal campaign summary
  - shutdown      → clean exit
"""

from __future__ import annotations

import json
import sys

from portlight.rpc.protocol import (
    Request,
    Response,
    ErrorResponse,
    PARSE_ERROR,
    METHOD_NOT_FOUND,
    NO_ACTIVE_GAME,
    crew_member_to_dict,
    campaign_summary,
)


class RpcServer:
    """Stdio JSON-RPC server wrapping a Star Freight GameSession."""

    def __init__(self, session=None):
        self._session = session
        self._running = False
        self._methods = {
            "ping": self._ping,
            "get_roster": self._get_roster,
            "get_crew_member": self._get_crew_member,
            "get_campaign": self._get_campaign,
            "shutdown": self._shutdown,
        }

    @property
    def session(self):
        return self._session

    def _ensure_campaign(self):
        """Return campaign state or None if no game is active."""
        if self._session is None or not self._session.active:
            return None
        return self._session.sf_campaign

    # -------------------------------------------------------------------
    # RPC methods
    # -------------------------------------------------------------------

    def _ping(self, _params: dict) -> dict:
        from portlight import __version__
        return {"status": "ok", "version": __version__}

    def _get_roster(self, _params: dict) -> dict | ErrorResponse:
        campaign = self._ensure_campaign()
        if campaign is None:
            return ErrorResponse(id=None, code=NO_ACTIVE_GAME,
                                 message="No active game")
        members = [
            crew_member_to_dict(m)
            for m in campaign.crew.members
            if m.status.value != "departed"
        ]
        return {"crew": members, "count": len(members)}

    def _get_crew_member(self, params: dict) -> dict | ErrorResponse:
        campaign = self._ensure_campaign()
        if campaign is None:
            return ErrorResponse(id=None, code=NO_ACTIVE_GAME,
                                 message="No active game")
        crew_id = params.get("id")
        if not crew_id:
            return ErrorResponse(id=None, code=-32602,
                                 message="Missing required param: id")
        for m in campaign.crew.members:
            if m.id == crew_id:
                return crew_member_to_dict(m)
        return ErrorResponse(id=None, code=-32602,
                             message=f"Unknown crew member: {crew_id}")

    def _get_campaign(self, _params: dict) -> dict | ErrorResponse:
        campaign = self._ensure_campaign()
        if campaign is None:
            return ErrorResponse(id=None, code=NO_ACTIVE_GAME,
                                 message="No active game")
        return campaign_summary(campaign)

    def _shutdown(self, _params: dict) -> dict:
        self._running = False
        return {"status": "shutting_down"}

    # -------------------------------------------------------------------
    # Dispatch
    # -------------------------------------------------------------------

    def dispatch(self, raw: str) -> str:
        """Parse a JSON-RPC request and return a JSON response string."""
        try:
            req = Request.from_json(raw)
        except (json.JSONDecodeError, KeyError, TypeError):
            return ErrorResponse(
                id=None, code=PARSE_ERROR, message="Parse error"
            ).to_json()

        handler = self._methods.get(req.method)
        if handler is None:
            return ErrorResponse(
                id=req.id, code=METHOD_NOT_FOUND,
                message=f"Method not found: {req.method}",
            ).to_json()

        result = handler(req.params)

        # Handler returned an error directly
        if isinstance(result, ErrorResponse):
            result.id = req.id
            return result.to_json()

        return Response(id=req.id, result=result).to_json()

    # -------------------------------------------------------------------
    # Stdio loop
    # -------------------------------------------------------------------

    def run(self, input_stream=None, output_stream=None):
        """Read JSON-RPC requests from stdin, write responses to stdout.

        Streams can be overridden for testing.
        """
        inp = input_stream or sys.stdin
        out = output_stream or sys.stdout
        self._running = True

        while self._running:
            try:
                line = inp.readline()
            except (EOFError, KeyboardInterrupt):
                break
            if not line:
                break  # EOF

            line = line.strip()
            if not line:
                continue  # skip blank lines

            response = self.dispatch(line)
            out.write(response + "\n")
            out.flush()
