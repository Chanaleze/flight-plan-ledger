"""
Canonical flight-plan representation and hashing rules.

Design goal: two independent parties must produce the exact same hash
for the same logical flight plan.
"""

from __future__ import annotations

import hashlib
from datetime import date, datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class FlightPlanCanonicalV1(BaseModel):
    """
    Strict, versioned canonical form of a flight plan.
    Only the fields needed for integrity are included in v0.1.
    """

    schema_version: str = Field(default="FlightPlanCanonicalV1", frozen=True)

    # Core identification
    callsign: str
    aircraft_id: str  # registration, e.g. A7-BAA
    dof: date  # date of flight

    origin: str  # ICAO
    destination: str  # ICAO

    # Optional but useful for queries / recovery
    departure_time_utc: Optional[datetime] = None
    route: Optional[str] = None  # simplified route string for prototype

    @field_validator("callsign", "aircraft_id", "origin", "destination")
    @classmethod
    def uppercase_ids(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("departure_time_utc")
    @classmethod
    def ensure_utc(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return None
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    def canonical_dict(self) -> dict[str, Any]:
        """
        Produce a deterministic dictionary ready for hashing.
        - Keys sorted
        - None values omitted
        - Dates/datetimes in strict ISO format
        """
        data = self.model_dump(exclude_none=True, mode="json")
        # Ensure deterministic ordering
        return dict(sorted(data.items()))

    def canonical_bytes(self) -> bytes:
        """
        Canonical byte representation used for hashing.
        Uses the standard library for zero extra dependencies.
        """
        import json
        # separators=(',', ':') removes whitespace; sort_keys for determinism
        return json.dumps(
            self.canonical_dict(),
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=False,
        ).encode('utf-8')

    def content_hash(self, algorithm: str = "sha256") -> str:
        """Return hash in the form 'sha256:<hex>'."""
        if algorithm != "sha256":
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
        digest = hashlib.sha256(self.canonical_bytes()).hexdigest()
        return f"sha256:{digest}"


def normalize_flight_plan(raw: dict[str, Any]) -> FlightPlanCanonicalV1:
    """
    Accept a loose dict (from airline systems, FIXM subset, etc.)
    and produce a validated canonical object.
    """
    # Very small adapter for the prototype. Real system would have
    # richer mapping from ICAO / FIXM / FF-ICE.
    return FlightPlanCanonicalV1.model_validate(raw)
