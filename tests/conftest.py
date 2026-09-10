"""Shared pytest fixtures for flight-plan-ledger tests."""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

# Ensure `src/` is importable when running pytest from repo root
# (also covered by pyproject `pythonpath`, this is a belt-and-braces fallback).
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from flight_plan_ledger.crypto.keys import generate_keypair  # noqa: E402
from flight_plan_ledger.ledger.store import LedgerStore  # noqa: E402
from flight_plan_ledger.ledger.verifier import Verifier  # noqa: E402
from flight_plan_ledger.ledger.writer import LedgerWriter  # noqa: E402
from flight_plan_ledger.models.canonical import FlightPlanCanonicalV1  # noqa: E402


@pytest.fixture
def sample_plan() -> FlightPlanCanonicalV1:
    return FlightPlanCanonicalV1(
        callsign="QTR23",
        aircraft_id="A7-BAA",
        dof=date(2026, 9, 9),
        origin="OTHH",
        destination="EGLL",
        departure_time_utc=datetime(2026, 9, 9, 7, 30, tzinfo=timezone.utc),
        route="OTHH DCT EGLL",
    )


@pytest.fixture
def sample_plan_dict() -> dict:
    return {
        "callsign": "QTR23",
        "aircraft_id": "A7-BAA",
        "dof": "2026-09-09",
        "origin": "OTHH",
        "destination": "EGLL",
        "departure_time_utc": "2026-09-09T07:30:00Z",
        "route": "OTHH DCT EGLL",
    }


@pytest.fixture
def keypair():
    return generate_keypair()


@pytest.fixture
def key_id() -> str:
    return "test-writer-01"


@pytest.fixture
def submitter_id() -> str:
    return "org:test"


@pytest.fixture
def store(tmp_path: Path) -> LedgerStore:
    return LedgerStore(tmp_path / "ledger.jsonl")


@pytest.fixture
def writer(store: LedgerStore, keypair, key_id: str, submitter_id: str) -> LedgerWriter:
    private_key, _ = keypair
    return LedgerWriter(store, private_key, key_id=key_id, submitter_id=submitter_id)


@pytest.fixture
def verifier(store: LedgerStore, keypair, key_id: str) -> Verifier:
    _, public_key = keypair
    return Verifier(store, public_keys={key_id: public_key})


def make_plan(callsign: str = "BAW12", origin: str = "EGLL", destination: str = "KJFK") -> FlightPlanCanonicalV1:
    """Helper to build distinct plans quickly."""
    return FlightPlanCanonicalV1(
        callsign=callsign,
        aircraft_id="G-TEST",
        dof=date(2026, 9, 9),
        origin=origin,
        destination=destination,
        departure_time_utc=datetime(2026, 9, 9, 10, 15, tzinfo=timezone.utc),
        route=f"{origin} DCT {destination}",
    )
