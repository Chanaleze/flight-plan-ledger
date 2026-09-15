"""Stateless demo-only web service logic.

This module powers the public interactive demo (static frontend + one
serverless function, see ``demo/`` and ``api/``). It reuses the real
prototype logic (canonicalization, Ed25519, chain checks, recovery) but is
deliberately **not** the product API (that remains a sketch, see
``contracts/openapi-sketch.yaml``).

Security model (see ADR 0004 — must stay true if this is ever touched):

- Ephemeral Ed25519 keypair generated per ``sign`` request. The private key
  never leaves process memory and is never logged or returned.
- The demo can only mint entries with ``submitter_id="org:demo"`` and
  ``metadata["demo"]=True``, so demo entries can never be mistaken for real
  operational entries.
- No persistence: chain state lives in the visitor's browser; every call is
  a pure function of its JSON input.
- Strict size/count limits bound abuse of the free hosting tier.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Tuple

from pydantic import ValidationError

from flight_plan_ledger.crypto.keys import (
    generate_keypair,
    load_public_key,
    serialize_public_key,
    sign,
    verify,
)
from flight_plan_ledger.ledger.recovery import RecoveryService
from flight_plan_ledger.models.canonical import normalize_flight_plan
from flight_plan_ledger.models.ledger_entry import EntryStatus, LedgerEntry, Signature

DEMO_SUBMITTER_ID = "org:demo"
DEMO_KEY_ID_PREFIX = "demo-ephemeral-"

MAX_PLAN_BYTES = 8 * 1024  # largest accepted plan JSON (re-serialized)
MAX_ENTRY_BYTES = 16 * 1024  # largest accepted single entry JSON
MAX_ENTRIES = 64  # largest accepted chain / recovery input
MAX_BODY_BYTES = 256 * 1024  # largest accepted HTTP body (enforced by adapter)

_PREV_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

ACTIONS = ("info", "hash", "sign", "verify", "verify_chain", "recover")

INFO: Dict[str, Any] = {
    "service": "flight-plan-ledger-demo",
    "version": "0.1.0",
    "demo_only": True,
    "actions": list(ACTIONS),
    "limits": {
        "max_plan_bytes": MAX_PLAN_BYTES,
        "max_entry_bytes": MAX_ENTRY_BYTES,
        "max_entries": MAX_ENTRIES,
    },
    "note": (
        "Public demonstration only. Ephemeral demo keys, sample data, nothing "
        "persists. Entries are always marked org:demo and can never be mistaken "
        "for operational records. Not connected to any ATC system."
    ),
}


class DemoError(Exception):
    """A demo request the service refuses, with an HTTP-style status code."""

    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.message = message
        self.status = status


def _payload_size_ok(obj: Any, limit: int, what: str) -> None:
    try:
        size = len(json.dumps(obj))
    except (TypeError, ValueError):
        raise DemoError(f"{what} is not JSON-serializable")
    if size > limit:
        raise DemoError(f"{what} too large ({size} > {limit} bytes)")


def _load_plan(raw: Any) -> Any:
    if not isinstance(raw, dict):
        raise DemoError("plan must be a JSON object")
    _payload_size_ok(raw, MAX_PLAN_BYTES, "plan")
    try:
        return normalize_flight_plan(raw)
    except ValidationError as e:
        raise DemoError(f"plan failed validation: {e.errors()[0]['msg']}")


def _load_entry(raw: Any) -> LedgerEntry:
    if not isinstance(raw, dict):
        raise DemoError("entry must be a JSON object")
    _payload_size_ok(raw, MAX_ENTRY_BYTES, "entry")
    try:
        return LedgerEntry.model_validate(raw)
    except ValidationError as e:
        raise DemoError(f"entry failed validation: {e.errors()[0]['msg']}")


def _check_sequence(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DemoError("sequence must be an integer")
    if not 1 <= value <= MAX_ENTRIES:
        raise DemoError(f"sequence must be between 1 and {MAX_ENTRIES}")
    return value


def _check_previous_entry_hash(value: Any, sequence: int) -> Optional[str]:
    if sequence == 1:
        if value is not None:
            raise DemoError("genesis entry (sequence=1) must not carry previous_entry_hash")
        return None
    if not isinstance(value, str) or not _PREV_HASH_RE.match(value):
        raise DemoError("previous_entry_hash must look like 'sha256:<64 hex chars>'")
    return value


def action_hash(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return the canonical form and content hash of a plan (no keys involved)."""
    plan = _load_plan(payload.get("plan"))
    canonical_json = plan.canonical_bytes().decode("utf-8")
    return {
        "canonical": json.loads(canonical_json),
        "canonical_json": canonical_json,
        "plan_hash": plan.content_hash(),
    }


def action_sign(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create one demo entry with a fresh ephemeral key (private key never leaves)."""
    plan = _load_plan(payload.get("plan"))
    sequence = _check_sequence(payload.get("sequence", 1))
    previous_entry_hash = _check_previous_entry_hash(
        payload.get("previous_entry_hash"), sequence
    )
    raw_status = payload.get("status", EntryStatus.ACCEPTED.value)
    try:
        status = EntryStatus(raw_status)
    except ValueError:
        allowed = ", ".join(s.value for s in EntryStatus)
        raise DemoError(f"unknown status {raw_status!r} (allowed: {allowed})")

    private_key, public_key = generate_keypair()
    fingerprint = hashlib.sha256(public_key.public_bytes_raw()).hexdigest()[:16]
    key_id = f"{DEMO_KEY_ID_PREFIX}{fingerprint}"

    meta = {
        "origin": plan.origin,
        "destination": plan.destination,
        "aircraft_id": plan.aircraft_id,
        "callsign": plan.callsign,
        "dof": plan.dof.isoformat(),
        "demo": True,
    }
    entry = LedgerEntry(
        sequence=sequence,
        submitter_id=DEMO_SUBMITTER_ID,
        plan_hash=plan.content_hash(),
        status=status,
        previous_entry_hash=previous_entry_hash,
        metadata=meta,
    )
    entry.signature = Signature(
        alg="Ed25519",
        key_id=key_id,
        value=sign(private_key, entry.content_for_signing()),
    )
    return {
        "demo": True,
        "entry": entry.model_dump(mode="json"),
        "entry_hash": entry.entry_hash(),
        "plan_hash": plan.content_hash(),
        "key_id": key_id,
        "public_key_pem": serialize_public_key(public_key).decode("ascii"),
        "warning": (
            "Demo entry only: ephemeral key, submitter org:demo. "
            "The private key was discarded and cannot be recovered."
        ),
    }


def _load_public_keys(raw: Any) -> Dict[str, Any]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise DemoError("public_keys must be an object mapping key_id to PEM")
    keys: Dict[str, Any] = {}
    for key_id, pem in raw.items():
        if not isinstance(pem, str):
            raise DemoError(f"public key for {key_id!r} must be a PEM string")
        try:
            keys[key_id] = load_public_key(pem.encode("ascii"))
        except Exception:
            raise DemoError(f"public key for {key_id!r} is not a valid Ed25519 PEM")
    return keys


def action_verify(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Check one plan against one entry and its public key (read-only)."""
    plan = _load_plan(payload.get("plan"))
    entry = _load_entry(payload.get("entry"))
    keys = _load_public_keys(payload.get("public_keys"))

    plan_hash = plan.content_hash()
    plan_hash_match = entry.plan_hash == plan_hash
    signature_valid: Optional[bool] = None
    if entry.signature is not None:
        pub = keys.get(entry.signature.key_id)
        signature_valid = (
            verify(pub, entry.content_for_signing(), entry.signature.value)
            if pub is not None
            else False
        )
    ok = plan_hash_match and signature_valid is not False and signature_valid is not None
    if signature_valid is None:
        message = "Entry carries no signature" if plan_hash_match else "Plan hash does not match entry"
        ok = False
    elif not plan_hash_match:
        message = "Plan hash does not match entry (plan was changed or is a different plan)"
        ok = False
    elif not signature_valid:
        message = "Signature check failed (unknown key or tampered entry)"
        ok = False
    else:
        message = "Plan matches entry and the demo signature is valid"
    return {
        "valid": ok,
        "message": message,
        "plan_hash": plan_hash,
        "plan_hash_match": plan_hash_match,
        "signature_valid": signature_valid,
        "entry_id": entry.entry_id,
        "sequence": entry.sequence,
        "status": entry.status.value,
    }


class _ListStore:
    """Minimal in-memory stand-in exposing the read surface RecoveryService needs."""

    def __init__(self, entries: List[LedgerEntry]):
        self._entries = entries

    def get_all(self) -> List[LedgerEntry]:
        return list(self._entries)


def _load_entries(raw: Any) -> List[LedgerEntry]:
    if not isinstance(raw, list):
        raise DemoError("entries must be a JSON array")
    if not 1 <= len(raw) <= MAX_ENTRIES:
        raise DemoError(f"entries must contain between 1 and {MAX_ENTRIES} items")
    return [_load_entry(item) for item in raw]


def action_verify_chain(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Walk the provided entries in sequence order and check hash links (+ signatures)."""
    entries = sorted(_load_entries(payload.get("entries")), key=lambda e: e.sequence)
    keys = _load_public_keys(payload.get("public_keys"))

    chain: List[Dict[str, Any]] = []
    valid = True
    message = f"Chain valid - {len(entries)} entries"
    # Pass 1: hash links (mirrors Verifier.verify_chain on the real store).
    for i, entry in enumerate(entries):
        if i == 0:
            if entry.previous_entry_hash is not None:
                valid = False
                message = "Genesis entry must have previous_entry_hash=None"
        else:
            expected = entries[i - 1].entry_hash()
            if entry.previous_entry_hash != expected:
                valid = False
                message = (
                    f"Chain break at sequence={entry.sequence}: expected previous "
                    f"{expected}, got {entry.previous_entry_hash}"
                )
    # Pass 2: signatures, only for keys the caller supplied.
    signatures: List[Optional[bool]] = [None] * len(entries)
    if valid:
        for i, entry in enumerate(entries):
            if entry.signature is None:
                continue
            pub = keys.get(entry.signature.key_id)
            if pub is None:
                continue
            sig_valid = verify(pub, entry.content_for_signing(), entry.signature.value)
            signatures[i] = sig_valid
            if not sig_valid:
                valid = False
                message = f"Bad signature at sequence={entry.sequence}"
    for entry, sig_valid in zip(entries, signatures):
        chain.append(
            {
                "sequence": entry.sequence,
                "entry_id": entry.entry_id,
                "entry_hash": entry.entry_hash(),
                "previous_entry_hash": entry.previous_entry_hash,
                "plan_hash": entry.plan_hash,
                "status": entry.status.value,
                "submitter_id": entry.submitter_id,
                "key_id": entry.signature.key_id if entry.signature else None,
                "signature_valid": sig_valid,
            }
        )
    return {
        "valid": valid,
        "message": message,
        "entries_checked": len(entries),
        "chain": chain,
    }


def action_recover(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Reconstruct the last-known-good accepted set from the provided entries."""
    entries = sorted(_load_entries(payload.get("entries")), key=lambda e: e.sequence)
    report = RecoveryService(_ListStore(entries)).recovery_report()
    return {"demo": True, **report}


def handle_action(action: Any, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Dispatch one demo request. Returns (http_status, json_body)."""
    if not isinstance(payload, dict):
        raise DemoError("request body must be a JSON object")
    if action is None:
        action = payload.get("action")
    if action is None or action == "info":
        return 200, dict(INFO)
    handlers = {
        "hash": action_hash,
        "sign": action_sign,
        "verify": action_verify,
        "verify_chain": action_verify_chain,
        "recover": action_recover,
    }
    handler = handlers.get(action)
    if handler is None:
        raise DemoError(f"unknown action {action!r} (allowed: {', '.join(ACTIONS)})", status=404)
    return 200, handler(payload)
