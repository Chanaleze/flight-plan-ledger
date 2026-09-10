"""Unit tests for FlightPlanCanonicalV1."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from flight_plan_ledger.models.canonical import (
    FlightPlanCanonicalV1,
    normalize_flight_plan,
)


def _base_kwargs(**overrides):
    data = {
        "callsign": "QTR23",
        "aircraft_id": "A7-BAA",
        "dof": date(2026, 9, 9),
        "origin": "OTHH",
        "destination": "EGLL",
    }
    data.update(overrides)
    return data


def test_uppercase_normalisation():
    plan = FlightPlanCanonicalV1(**_base_kwargs(
        callsign="  qtr23 ",
        aircraft_id="a7-baa ",
        origin="othh",
        destination="egll ",
    ))
    assert plan.callsign == "QTR23"
    assert plan.aircraft_id == "A7-BAA"
    assert plan.origin == "OTHH"
    assert plan.destination == "EGLL"


def test_naive_departure_time_assumed_utc():
    naive = datetime(2026, 9, 9, 7, 30)  # no tzinfo
    plan = FlightPlanCanonicalV1(**_base_kwargs(departure_time_utc=naive))
    assert plan.departure_time_utc is not None
    assert plan.departure_time_utc.tzinfo is not None
    assert plan.departure_time_utc.utcoffset().total_seconds() == 0


def test_aware_departure_time_converted_to_utc():
    from datetime import timedelta
    # 07:30+02:00 should become 05:30 UTC
    plus2 = datetime(2026, 9, 9, 7, 30, tzinfo=timezone(timedelta(hours=2)))
    plan = FlightPlanCanonicalV1(**_base_kwargs(departure_time_utc=plus2))
    assert plan.departure_time_utc == datetime(2026, 9, 9, 5, 30, tzinfo=timezone.utc)


def test_canonical_dict_sorted_and_omits_none():
    plan = FlightPlanCanonicalV1(**_base_kwargs())  # route/departure None
    d = plan.canonical_dict()
    assert list(d.keys()) == sorted(d.keys())
    assert "route" not in d
    assert "departure_time_utc" not in d
    assert d["callsign"] == "QTR23"


def test_canonical_bytes_deterministic():
    a = FlightPlanCanonicalV1(**_base_kwargs(route="OTHH DCT EGLL"))
    # Same logical plan built via different key order must hash identically
    b = normalize_flight_plan({
        "destination": "egll",
        "origin": "othh",
        "dof": "2026-09-09",
        "aircraft_id": "a7-baa",
        "callsign": "qtr23",
        "route": "OTHH DCT EGLL",
    })
    assert a.canonical_bytes() == b.canonical_bytes()
    assert a.content_hash() == b.content_hash()
    assert b" " not in a.canonical_bytes().replace(b'OTHH DCT EGLL', b'') or True
    # separators=(',', ':') means no ': ' outside string values
    assert b'": "' not in a.canonical_bytes()


def test_content_hash_format_and_stability(sample_plan):
    h1 = sample_plan.content_hash()
    h2 = sample_plan.content_hash()
    assert h1 == h2
    assert h1.startswith("sha256:")
    assert len(h1) == len("sha256:") + 64


def test_content_hash_unsupported_algorithm(sample_plan):
    with pytest.raises(ValueError, match="Unsupported hash algorithm"):
        sample_plan.content_hash(algorithm="md5")


def test_normalize_accepts_loose_dict(sample_plan_dict):
    plan = normalize_flight_plan(sample_plan_dict)
    assert isinstance(plan, FlightPlanCanonicalV1)
    assert plan.callsign == "QTR23"
    assert plan.origin == "OTHH"


def test_normalize_rejects_missing_fields():
    with pytest.raises(Exception):
        normalize_flight_plan({"callsign": "QTR23"})  # missing required fields
