"""JSON-RPC 2.0 message types for the Star Freight engine bridge.

Frozen for 7A — only expand when the client needs new methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any
import json


# ---------------------------------------------------------------------------
# JSON-RPC 2.0 wire types
# ---------------------------------------------------------------------------

@dataclass
class Request:
    """Inbound JSON-RPC 2.0 request."""
    method: str
    id: int | str | None = None
    params: dict[str, Any] = field(default_factory=dict)
    jsonrpc: str = "2.0"

    @classmethod
    def from_json(cls, raw: str) -> Request:
        data = json.loads(raw)
        return cls(
            method=data["method"],
            id=data.get("id"),
            params=data.get("params", {}),
            jsonrpc=data.get("jsonrpc", "2.0"),
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))


@dataclass
class Response:
    """Outbound JSON-RPC 2.0 success response."""
    id: int | str | None
    result: Any
    jsonrpc: str = "2.0"

    def to_json(self) -> str:
        return json.dumps(
            {"jsonrpc": self.jsonrpc, "id": self.id, "result": self.result},
            separators=(",", ":"),
        )


@dataclass
class ErrorResponse:
    """Outbound JSON-RPC 2.0 error response."""
    id: int | str | None
    code: int
    message: str
    data: Any = None
    jsonrpc: str = "2.0"

    def to_json(self) -> str:
        err = {"code": self.code, "message": self.message}
        if self.data is not None:
            err["data"] = self.data
        return json.dumps(
            {"jsonrpc": self.jsonrpc, "id": self.id, "error": err},
            separators=(",", ":"),
        )


# ---------------------------------------------------------------------------
# Error codes (JSON-RPC 2.0 standard + app codes)
# ---------------------------------------------------------------------------

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

# App-specific
NO_ACTIVE_GAME = 1001


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def crew_member_to_dict(member) -> dict:
    """Serialize a CrewMember to a JSON-safe dict."""
    return {
        "id": member.id,
        "name": member.name,
        "civilization": member.civilization.value,
        "role": member.role.value,
        "hp": member.hp,
        "hp_max": member.hp_max,
        "speed": member.speed,
        "abilities": list(member.abilities),
        "ship_skill": member.ship_skill,
        "morale": member.morale,
        "loyalty_tier": member.loyalty_tier.value,
        "loyalty_points": member.loyalty_points,
        "status": member.status.value,
        "pay_rate": member.pay_rate,
    }


def campaign_summary(state) -> dict:
    """Serialize campaign state to a minimal summary."""
    return {
        "credits": state.credits,
        "day": state.day,
        "current_station": state.current_station,
        "in_transit": state.in_transit,
        "ship_hull": state.ship_hull,
        "ship_hull_max": state.ship_hull_max,
        "ship_fuel": state.ship_fuel,
        "ship_cargo": list(state.ship_cargo),
        "ship_cargo_capacity": state.ship_cargo_capacity,
        "crew_count": len([m for m in state.crew.members
                           if m.status.value != "departed"]),
    }
