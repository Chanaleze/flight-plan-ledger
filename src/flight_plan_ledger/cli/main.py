"""Simple CLI for the Flight Plan Integrity Ledger prototype."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import click
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from flight_plan_ledger.crypto.keys import (
    generate_keypair,
    load_keypair,
    load_public_key,
    save_keypair,
)
from flight_plan_ledger.ledger.store import LedgerStore
from flight_plan_ledger.ledger.verifier import Verifier
from flight_plan_ledger.ledger.writer import LedgerWriter
from flight_plan_ledger.models.canonical import FlightPlanCanonicalV1, normalize_flight_plan
from flight_plan_ledger.models.ledger_entry import EntryStatus


DEFAULT_DATA_DIR = Path("data")
DEFAULT_LEDGER = DEFAULT_DATA_DIR / "ledger.jsonl"
DEFAULT_KEYS_DIR = DEFAULT_DATA_DIR / "keys"


@click.group()
def cli():
    """Flight Plan Integrity Ledger – prototype CLI"""
    pass


@cli.command("init-keys")
@click.option("--key-id", default="nats-writer-01", show_default=True)
@click.option("--keys-dir", type=click.Path(), default=str(DEFAULT_KEYS_DIR))
def init_keys(key_id: str, keys_dir: str):
    """Generate a new Ed25519 key pair for a writer."""
    keys_path = Path(keys_dir)
    private_path = keys_path / f"{key_id}.private.pem"
    public_path = keys_path / f"{key_id}.public.pem"

    if private_path.exists():
        click.echo(f"Key already exists: {private_path}", err=True)
        sys.exit(1)

    private_key, public_key = generate_keypair()
    save_keypair(private_key, public_key, private_path, public_path)
    click.echo(f"Generated key pair:")
    click.echo(f"  private: {private_path}")
    click.echo(f"  public : {public_path}")
    click.echo(f"  key_id : {key_id}")


@cli.command("record")
@click.option("--plan", "plan_file", type=click.Path(exists=True), required=True)
@click.option("--status", type=click.Choice([s.value for s in EntryStatus]), default="ACCEPTED")
@click.option("--submitter", default="org:nats", show_default=True)
@click.option("--key-id", default="nats-writer-01", show_default=True)
@click.option("--keys-dir", type=click.Path(), default=str(DEFAULT_KEYS_DIR))
@click.option("--ledger", type=click.Path(), default=str(DEFAULT_LEDGER))
def record(plan_file: str, status: str, submitter: str, key_id: str, keys_dir: str, ledger: str):
    """Record a flight plan decision onto the ledger."""
    keys_path = Path(keys_dir)
    private_path = keys_path / f"{key_id}.private.pem"
    public_path = keys_path / f"{key_id}.public.pem"

    if not private_path.exists():
        click.echo("Keys not found. Run: fpl init-keys", err=True)
        sys.exit(1)

    private_key, _ = load_keypair(private_path, public_path)
    store = LedgerStore(Path(ledger))
    writer = LedgerWriter(store, private_key, key_id=key_id, submitter_id=submitter)

    raw = json.loads(Path(plan_file).read_text(encoding="utf-8"))
    plan = normalize_flight_plan(raw)

    entry = writer.record(plan, status=EntryStatus(status))
    click.echo("Recorded entry:")
    click.echo(f"  entry_id     : {entry.entry_id}")
    click.echo(f"  sequence     : {entry.sequence}")
    click.echo(f"  plan_hash    : {entry.plan_hash}")
    click.echo(f"  status       : {entry.status.value}")
    click.echo(f"  submitter    : {entry.submitter_id}")
    click.echo(f"  previous_hash: {entry.previous_entry_hash}")


@cli.command("verify")
@click.option("--plan", "plan_file", type=click.Path(exists=True), required=True)
@click.option("--key-id", default="nats-writer-01", show_default=True)
@click.option("--keys-dir", type=click.Path(), default=str(DEFAULT_KEYS_DIR))
@click.option("--ledger", type=click.Path(), default=str(DEFAULT_LEDGER))
def verify_cmd(plan_file: str, key_id: str, keys_dir: str, ledger: str):
    """Verify that a flight plan appears on the ledger with a valid signature."""
    keys_path = Path(keys_dir)
    public_path = keys_path / f"{key_id}.public.pem"
    if not public_path.exists():
        click.echo("Public key not found.", err=True)
        sys.exit(1)

    public_key = load_public_key(public_path.read_bytes())
    store = LedgerStore(Path(ledger))
    verifier = Verifier(store, public_keys={key_id: public_key})

    raw = json.loads(Path(plan_file).read_text(encoding="utf-8"))
    plan = normalize_flight_plan(raw)

    result = verifier.verify_plan(plan)
    click.echo(result)
    if result.found and result.signature_valid:
        click.echo("✓ Plan is present and signature is valid")
        for e in result.entries:
            click.echo(f"  - seq={e.sequence} status={e.status.value} at {e.timestamp.isoformat()}")
    else:
        click.echo("✗ Verification failed or plan not found")
        sys.exit(1)


@cli.command("verify-chain")
@click.option("--ledger", type=click.Path(), default=str(DEFAULT_LEDGER))
@click.option("--key-id", default="nats-writer-01", show_default=True)
@click.option("--keys-dir", type=click.Path(), default=str(DEFAULT_KEYS_DIR))
def verify_chain_cmd(ledger: str, key_id: str, keys_dir: str):
    """Check integrity of the entire hash chain."""
    keys_path = Path(keys_dir)
    public_path = keys_path / f"{key_id}.public.pem"
    public_keys = {}
    if public_path.exists():
        public_keys[key_id] = load_public_key(public_path.read_bytes())

    store = LedgerStore(Path(ledger))
    verifier = Verifier(store, public_keys=public_keys)
    ok, message = verifier.verify_chain()
    click.echo(message)
    if not ok:
        sys.exit(1)


@cli.command("list")
@click.option("--ledger", type=click.Path(), default=str(DEFAULT_LEDGER))
def list_cmd(ledger: str):
    """List all entries in the ledger."""
    store = LedgerStore(Path(ledger))
    entries = store.get_all()
    if not entries:
        click.echo("Ledger is empty")
        return
    for e in entries:
        click.echo(
            f"[{e.sequence:04d}] {e.status.value:10s}  {e.metadata.get('callsign', '?'):8s}  "
            f"{e.metadata.get('origin', '?')}→{e.metadata.get('destination', '?')}  "
            f"hash={e.plan_hash[7:19]}…  id={e.entry_id[:8]}…"
        )


@cli.command("recover")
@click.option("--ledger", type=click.Path(), default=str(DEFAULT_LEDGER))
@click.option("--output", type=click.Path(), default=None, help="Optional JSON export path")
@click.option("--summary/--no-summary", default=True, help="Print human-readable summary")
def recover_cmd(ledger: str, output: str | None, summary: bool):
    """Reconstruct last known good accepted plans from the ledger (post-outage recovery)."""
    from flight_plan_ledger.ledger.recovery import RecoveryService

    store = LedgerStore(Path(ledger))
    recovery = RecoveryService(store)
    entries = recovery.last_known_good(only_accepted=True)

    if summary:
        click.echo(recovery.export_summary(entries))

    if output:
        out_path = Path(output)
        recovery.export_json(entries, out_path)
        click.echo(f"\nJSON export written to: {out_path.resolve()}")

    if not entries:
        click.echo("No accepted plans found in ledger.")


@cli.command("demo")
@click.option("--keys-dir", type=click.Path(), default=str(DEFAULT_KEYS_DIR))
@click.option("--ledger", type=click.Path(), default=str(DEFAULT_LEDGER))
def demo(keys_dir: str, ledger: str):
    """Run a full end-to-end demonstration."""
    from flight_plan_ledger.cli.demo import run_demo
    run_demo(Path(keys_dir), Path(ledger))


if __name__ == "__main__":
    cli()
