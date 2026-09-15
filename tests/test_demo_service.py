"""Unit tests for the stateless demo web service (demo_service)."""

from __future__ import annotations

import base64
import json
from datetime import date, datetime, timezone

import pytest

from flight_plan_ledger import demo_service
from flight_plan_ledger.demo_service import (
    DemoError,
    _ListStore,
    action_hash,
    action_recover,
    action_sign,
    action_verify,
    action_verify_chain,
    handle_action,
)
from flight_plan_ledger.models.canonical import FlightPlanCanonicalV1, normalize_flight_plan
from flight_plan_ledger.models.ledger_entry import LedgerEntry


def _plan_dict(**overrides):
    base = {
        "callsign": "QTR23",
        "aircraft_id": "A7-BAA",
        "dof": "2026-09-09",
        "origin": "OTHH",
        "destination": "EGLL",
        "departure_time_utc": "2026-09-09T07:30:00Z",
        "route": "OTHH DCT EGLL",
    }
    base.update(overrides)
    return base


def _signed(status="ACCEPTED", sequence=1, previous_entry_hash=None):
    return action_sign(
        {
            "plan": _plan_dict(),
            "status": status,
            "sequence": sequence,
            "previous_entry_hash": previous_entry_hash,
        }
    )


def _chain_payload(n=3):
    out, keys, prev = [], {}, None
    for i in range(1, n + 1):
        signed = _signed(sequence=i, previous_entry_hash=prev)
        out.append(signed["entry"])
        keys[signed["key_id"]] = signed["public_key_pem"]
        prev = signed["entry_hash"]
    return {"entries": out, "public_keys": keys}


# --- dispatcher ---


def test_handle_action_info_variants():
    for status, body in (
        handle_action(None, {}),
        handle_action("info", {}),
        handle_action(None, {"action": "hash", "plan": _plan_dict()}),
    ):
        assert status == 200
    assert handle_action(None, {})[1]["demo_only"] is True
    assert set(handle_action(None, {})[1]["actions"]) == {
        "info",
        "hash",
        "sign",
        "verify",
        "verify_chain",
        "recover",
    }


def test_handle_action_rejects_bad_envelope():
    with pytest.raises(DemoError):
        handle_action("hash", ["not", "a", "dict"])
    with pytest.raises(DemoError) as e:
        handle_action("nope", {})
    assert e.value.status == 404


# --- hash ---


def test_hash_matches_model(sample_plan_dict):
    body = action_hash({"plan": sample_plan_dict})
    plan = normalize_flight_plan(sample_plan_dict)
    assert body["plan_hash"] == plan.content_hash()
    assert body["canonical_json"] == plan.canonical_bytes().decode("utf-8")
    assert body["canonical"]["callsign"] == "QTR23"


def test_hash_rejects_bad_plans():
    with pytest.raises(DemoError):
        action_hash({"plan": ["not", "a", "dict"]})
    with pytest.raises(DemoError):
        action_hash({"plan": {"callsign": "QTR23"}})  # missing required fields
    with pytest.raises(DemoError):
        action_hash({"plan": _plan_dict(route="X" * (demo_service.MAX_PLAN_BYTES + 1))})
    with pytest.raises(DemoError):
        action_hash({"plan": _plan_dict(route={"not": "serializable-as-str-but-fine"})})
    with pytest.raises(DemoError):
        action_hash({"plan": _plan_dict(extra={"a", "set", "is", "not", "json"})})


# --- sign ---


def test_sign_genesis_forces_demo_markers():
    body = _signed()
    entry = body["entry"]
    assert body["demo"] is True
    assert entry["submitter_id"] == "org:demo"
    assert entry["metadata"]["demo"] is True
    assert entry["sequence"] == 1
    assert entry["previous_entry_hash"] is None
    assert entry["status"] == "ACCEPTED"
    assert body["key_id"].startswith("demo-ephemeral-")
    assert "warning" in body and "private key was discarded" in body["warning"]
    # The returned public key really verifies the entry signature.
    parsed = LedgerEntry.model_validate(entry)
    keys = demo_service._load_public_keys({body["key_id"]: body["public_key_pem"]})
    from flight_plan_ledger.crypto.keys import verify as raw_verify

    assert raw_verify(
        keys[body["key_id"]], parsed.content_for_signing(), parsed.signature.value
    )
    assert parsed.entry_hash() == body["entry_hash"]


def test_sign_ephemeral_keys_differ_per_request():
    assert _signed()["key_id"] != _signed()["key_id"]


def test_sign_accepts_all_statuses_and_chain_linking():
    prev = None
    for i, status in enumerate(["ACCEPTED", "REJECTED", "AMENDED", "CANCELLED"], start=1):
        body = _signed(status=status, sequence=i, previous_entry_hash=prev)
        assert body["entry"]["status"] == status
        prev = body["entry_hash"]
    with pytest.raises(DemoError):
        action_sign({"plan": _plan_dict(), "status": "MAYBE"})


def test_sign_rejects_bad_sequence_and_links():
    good_prev = _signed()["entry_hash"]
    for bad in (0, 65, "2", True, 1.5, None):
        with pytest.raises(DemoError):
            action_sign({"plan": _plan_dict(), "sequence": bad})
    with pytest.raises(DemoError):  # genesis must not carry a link
        action_sign({"plan": _plan_dict(), "sequence": 1, "previous_entry_hash": good_prev})
    with pytest.raises(DemoError):  # non-genesis needs a well-formed link
        action_sign({"plan": _plan_dict(), "sequence": 2})
    with pytest.raises(DemoError):
        action_sign({"plan": _plan_dict(), "sequence": 2, "previous_entry_hash": "bogus"})


# --- verify ---


def test_verify_roundtrip_and_tamper(sample_plan_dict):
    signed = _signed()
    keys = {signed["key_id"]: signed["public_key_pem"]}
    ok = action_verify({"plan": sample_plan_dict, "entry": signed["entry"], "public_keys": keys})
    assert ok["valid"] is True and ok["plan_hash_match"] is True
    assert ok["signature_valid"] is True

    tampered = _plan_dict(callsign="QTR24")
    bad = action_verify({"plan": tampered, "entry": signed["entry"], "public_keys": keys})
    assert bad["valid"] is False and bad["plan_hash_match"] is False
    assert "does not match" in bad["message"]


def test_verify_detects_bad_signature_and_unknown_key():
    signed = _signed()
    entry = dict(signed["entry"])
    sig = dict(entry["signature"])
    raw = base64.b64decode(sig["value"])
    sig["value"] = base64.b64encode(bytes([raw[0] ^ 1]) + raw[1:]).decode("ascii")
    entry["signature"] = sig
    keys = {signed["key_id"]: signed["public_key_pem"]}
    bad = action_verify({"plan": _plan_dict(), "entry": entry, "public_keys": keys})
    assert bad["valid"] is False and bad["signature_valid"] is False
    assert "Signature check failed" in bad["message"]

    unknown = action_verify({"plan": _plan_dict(), "entry": signed["entry"], "public_keys": {}})
    assert unknown["valid"] is False and unknown["signature_valid"] is False


def test_verify_unsigned_entry_reports_clearly():
    signed = _signed()
    entry = dict(signed["entry"])
    entry["signature"] = None
    keys = {signed["key_id"]: signed["public_key_pem"]}
    res = action_verify({"plan": _plan_dict(), "entry": entry, "public_keys": keys})
    assert res["valid"] is False and res["signature_valid"] is None
    assert res["message"] == "Entry carries no signature"

    res2 = action_verify(
        {"plan": _plan_dict(callsign="OTHER"), "entry": entry, "public_keys": keys}
    )
    assert res2["valid"] is False
    assert res2["message"] == "Plan hash does not match entry"


def test_verify_rejects_bad_inputs():
    signed = _signed()
    with pytest.raises(DemoError):
        action_verify({"plan": _plan_dict(), "entry": ["nope"], "public_keys": {}})
    with pytest.raises(DemoError):
        action_verify({"plan": _plan_dict(), "entry": signed["entry"], "public_keys": ["nope"]})
    with pytest.raises(DemoError):
        action_verify(
            {"plan": _plan_dict(), "entry": signed["entry"], "public_keys": {"k": 42}}
        )
    with pytest.raises(DemoError):
        action_verify(
            {
                "plan": _plan_dict(),
                "entry": signed["entry"],
                "public_keys": {"k": "not-a-pem"},
            }
        )


# --- verify_chain ---


def test_verify_chain_valid_with_and_without_keys():
    payload = _chain_payload(3)
    res = action_verify_chain(payload)
    assert res["valid"] is True and res["entries_checked"] == 3
    assert all(e["signature_valid"] is True for e in res["chain"])
    assert res["chain"][0]["previous_entry_hash"] is None

    res2 = action_verify_chain({"entries": payload["entries"]})
    assert res2["valid"] is True
    assert all(e["signature_valid"] is None for e in res2["chain"])


def test_verify_chain_detects_break_bad_genesis_and_bad_signature():
    payload = _chain_payload(3)
    broken = json.loads(json.dumps(payload))
    broken["entries"][2]["previous_entry_hash"] = "sha256:" + "0" * 64
    res = action_verify_chain(broken)
    assert res["valid"] is False and "Chain break at sequence=3" in res["message"]

    orphan = {"entries": [payload["entries"][1]], "public_keys": payload["public_keys"]}
    res2 = action_verify_chain(orphan)
    assert res2["valid"] is False and "Genesis" in res2["message"]

    forged_sig = json.loads(json.dumps(payload))
    # Tamper the *last* entry's signature: links still hold, so this must
    # surface as a signature failure (tampering any earlier signature would
    # change that entry's hash and surface as a downstream chain break).
    sig = forged_sig["entries"][2]["signature"]["value"]
    raw = base64.b64decode(sig)
    forged_sig["entries"][2]["signature"]["value"] = base64.b64encode(
        bytes([raw[0] ^ 1]) + raw[1:]
    ).decode("ascii")
    res3 = action_verify_chain(forged_sig)
    assert res3["valid"] is False and "Bad signature at sequence=3" in res3["message"]

    # An unsigned trailing entry passes the link check; its signature slot
    # is reported as unchecked (None) rather than failing the chain.
    unsigned = json.loads(json.dumps(payload))
    unsigned["entries"][2]["signature"] = None
    res5 = action_verify_chain(unsigned)
    assert res5["valid"] is True
    assert res5["chain"][2]["signature_valid"] is None

    # Forging signed content (not the link) breaks the *downstream* link:
    # that is the hash chain doing its job.
    forged_meta = json.loads(json.dumps(payload))
    forged_meta["entries"][1]["metadata"]["callsign"] = "FORGED"
    res4 = action_verify_chain(forged_meta)
    assert res4["valid"] is False and "Chain break at sequence=3" in res4["message"]


def test_verify_chain_rejects_bad_inputs():
    with pytest.raises(DemoError):
        action_verify_chain({"entries": {"not": "a list"}})
    with pytest.raises(DemoError):
        action_verify_chain({"entries": []})
    with pytest.raises(DemoError):
        action_verify_chain({"entries": [{"sequence": 1}] * (demo_service.MAX_ENTRIES + 1)})
    with pytest.raises(DemoError):
        action_verify_chain({"entries": ["nope"]})
    with pytest.raises(DemoError) as e:
        action_verify_chain({"entries": [{"sequence": "one"}]})
    assert "failed validation" in e.value.message


# --- recover ---


def test_recover_returns_accepted_only():
    payload = _chain_payload(1)
    # Append a REJECTED plan: only the ACCEPTED genesis plan should be recovered.
    seq2 = action_sign(
        {
            "plan": _plan_dict(callsign="BAW12", aircraft_id="G-ZBJH", origin="EGLL",
                              destination="KJFK", route="EGLL DCT KJFK",
                              departure_time_utc="2026-09-09T10:15:00Z"),
            "status": "REJECTED",
            "sequence": 2,
            "previous_entry_hash": _chain_tip(payload),
        }
    )
    entries = payload["entries"] + [seq2["entry"]]
    report = action_recover({"entries": entries})
    assert report["demo"] is True
    assert report["accepted_plan_count"] == 1
    assert report["plans"][0]["callsign"] == "QTR23"
    assert _ListStore(entries).get_all() == entries


def _chain_tip(payload):
    from flight_plan_ledger.models.ledger_entry import LedgerEntry as LE

    entries = [LE.model_validate(e) for e in payload["entries"]]
    return entries[-1].entry_hash()


def test_recover_rejects_bad_inputs():
    with pytest.raises(DemoError):
        action_recover({"entries": []})


# --- misc ---


def test_public_key_loader_edges():
    assert demo_service._load_public_keys(None) == {}
    assert demo_service._payload_size_ok({"a": 1}, 100, "x") is None


def test_flight_plan_model_smoke():
    plan = FlightPlanCanonicalV1(
        callsign="t1",
        aircraft_id="g-1",
        dof=date(2026, 9, 9),
        origin="egll",
        destination="kjfk",
        departure_time_utc=datetime(2026, 9, 9, 10, 15, tzinfo=timezone.utc),
    )
    assert plan.callsign == "T1"
