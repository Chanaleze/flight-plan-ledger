"""End-to-end demonstration of the integrity ledger."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

from flight_plan_ledger.crypto.keys import generate_keypair, load_keypair, save_keypair
from flight_plan_ledger.ledger.store import LedgerStore
from flight_plan_ledger.ledger.verifier import Verifier
from flight_plan_ledger.ledger.writer import LedgerWriter
from flight_plan_ledger.models.canonical import FlightPlanCanonicalV1
from flight_plan_ledger.models.ledger_entry import EntryStatus


def run_demo(keys_dir: Path, ledger_path: Path) -> None:
    print("=" * 60)
    print("Flight Plan Integrity Ledger – Live Demo")
    print("=" * 60)
    print()

    # 1. Keys
    key_id = "nats-writer-01"
    private_path = keys_dir / f"{key_id}.private.pem"
    public_path = keys_dir / f"{key_id}.public.pem"

    if not private_path.exists():
        print("-> Generating writer key pair...")
        private_key, public_key = generate_keypair()
        save_keypair(private_key, public_key, private_path, public_path)
    else:
        print("-> Loading existing writer key pair...")
        private_key, public_key = load_keypair(private_path, public_path)

    # Fresh ledger for the demo
    if ledger_path.exists():
        ledger_path.unlink()
    store = LedgerStore(ledger_path)
    writer = LedgerWriter(
        store,
        private_key,
        key_id=key_id,
        submitter_id="org:nats",
    )
    verifier = Verifier(store, public_keys={key_id: public_key})

    # 2. Sample flight plans (inspired by real Qatar Airways / UK routes)
    plans = [
        FlightPlanCanonicalV1(
            callsign="QTR23",
            aircraft_id="A7-BAA",
            dof=date(2026, 9, 9),
            origin="OTHH",
            destination="EGLL",
            departure_time_utc=datetime(2026, 9, 9, 7, 30, tzinfo=timezone.utc),
            route="OTHH DCT EGLL",
        ),
        FlightPlanCanonicalV1(
            callsign="BAW12",
            aircraft_id="G-ZBJH",
            dof=date(2026, 9, 9),
            origin="EGLL",
            destination="KJFK",
            departure_time_utc=datetime(2026, 9, 9, 10, 15, tzinfo=timezone.utc),
            route="EGLL DCT KJFK",
        ),
        FlightPlanCanonicalV1(
            callsign="EZY8567",
            aircraft_id="G-EZBR",
            dof=date(2026, 9, 9),
            origin="EGKK",
            destination="LEPA",
            departure_time_utc=datetime(2026, 9, 9, 6, 45, tzinfo=timezone.utc),
            route="EGKK DCT LEPA",
        ),
    ]

    print("-> Recording three flight plans as ACCEPTED...")
    entries = []
    for plan in plans:
        entry = writer.record(plan, status=EntryStatus.ACCEPTED)
        entries.append(entry)
        print(f"   - {plan.callsign:8s}  {plan.origin}->{plan.destination}  "
              f"seq={entry.sequence}  hash={entry.plan_hash[7:19]}...")

    print()
    print("-> Verifying each plan independently...")
    for plan in plans:
        result = verifier.verify_plan(plan)
        status = "[OK] VALID" if (result.found and result.signature_valid) else "[FAIL] FAIL"
        print(f"   {status}  {plan.callsign}")

    print()
    print("-> Checking full hash-chain integrity...")
    ok, msg = verifier.verify_chain()
    print(f"   {'[OK]' if ok else '[FAIL]'} {msg}")

    print()
    print("-> Simulating primary system outage + recovery view...")
    from flight_plan_ledger.ledger.recovery import RecoveryService
    recovery = RecoveryService(store)
    print(recovery.export_summary(recovery.last_known_good()))

    print()
    print("=" * 60)
    print("Demo complete. The ledger file is at:")
    print(f"  {ledger_path.resolve()}")
    print()
    print("You can now run:")
    print("  PYTHONPATH=src python -m flight_plan_ledger.cli.main list")
    print("  PYTHONPATH=src python -m flight_plan_ledger.cli.main verify-chain")
    print("  PYTHONPATH=src python -m flight_plan_ledger.cli.main recover")
    print("  PYTHONPATH=src python -m flight_plan_ledger.cli.main recover --output data/recovery.json")
    print("=" * 60)
