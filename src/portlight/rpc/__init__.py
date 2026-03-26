"""JSON-RPC 2.0 server for Star Freight graphical clients.

The Python engine is the source of truth. Graphical clients (Godot, etc.)
connect via stdio JSON-RPC and receive game state as JSON.
"""

from portlight.rpc.protocol import Request, Response, ErrorResponse
from portlight.rpc.server import RpcServer

__all__ = ["Request", "Response", "ErrorResponse", "RpcServer"]
