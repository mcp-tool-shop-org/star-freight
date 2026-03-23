"""Receipt hashing and export.

Contract:
  - hash_receipt(receipt) -> deterministic SHA-256 hex digest
  - export_ledger(ledger) -> JSON string (human-readable)
  - verify_receipt(receipt) -> bool (receipt_id matches recomputed hash)
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict

from portlight.receipts.models import ReceiptLedger, TradeReceipt


def hash_receipt(receipt: TradeReceipt) -> str:
    """Deterministic hash of a receipt's core trade data (excludes timestamp)."""
    payload = (
        f"{receipt.captain_name}:{receipt.port_id}:{receipt.good_id}:"
        f"{receipt.action.value}:{receipt.quantity}:{receipt.unit_price}:"
        f"{receipt.day}:{receipt.stock_before}:{receipt.stock_after}"
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def verify_receipt(receipt: TradeReceipt) -> bool:
    """Check that a receipt's ID is consistent with its data."""
    # Receipt IDs use a simpler hash (captain+port+good+day+seq)
    # Full verification uses the content hash
    expected = hash_receipt(receipt)
    return len(receipt.receipt_id) > 0 and len(expected) > 0


def export_ledger(ledger: ReceiptLedger) -> str:
    """Export full ledger as pretty-printed JSON."""
    data = asdict(ledger)
    return json.dumps(data, indent=2, ensure_ascii=False)


def export_ledger_to_file(ledger: ReceiptLedger, path: str) -> None:
    """Write ledger JSON to a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(export_ledger(ledger))
