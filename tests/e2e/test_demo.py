"""Smoke tests for the end-to-end demo (cli/demo.py)."""

from __future__ import annotations

from click.testing import CliRunner

from flight_plan_ledger.cli.demo import run_demo
from flight_plan_ledger.cli.main import cli
from flight_plan_ledger.ledger.store import LedgerStore
from flight_plan_ledger.ledger.verifier import Verifier


def test_run_demo_records_three_plans_and_valid_chain(tmp_path, capsys):
    keys_dir = tmp_path / "keys"
    ledger_path = tmp_path / "ledger.jsonl"

    run_demo(keys_dir, ledger_path)

    out = capsys.readouterr().out
    assert "Demo complete" in out

    store = LedgerStore(ledger_path)
    assert store.count() == 3
    ok, msg = Verifier(store, public_keys={}).verify_chain()
    assert ok, msg


def test_run_demo_reuses_existing_keys(tmp_path, capsys):
    keys_dir = tmp_path / "keys"
    ledger_path = tmp_path / "ledger.jsonl"

    run_demo(keys_dir, ledger_path)
    first_pub = (keys_dir / "nats-writer-01.public.pem").read_bytes()
    capsys.readouterr()

    # Second run loads keys instead of generating (fresh ledger, same key)
    run_demo(keys_dir, ledger_path)
    out = capsys.readouterr().out
    assert "Loading existing writer key pair" in out
    assert (keys_dir / "nats-writer-01.public.pem").read_bytes() == first_pub
    assert LedgerStore(ledger_path).count() == 3


def test_demo_cli_passthrough(tmp_path):
    runner = CliRunner()
    keys_dir = tmp_path / "keys"
    ledger = tmp_path / "ledger.jsonl"
    r = runner.invoke(cli, ["demo", "--keys-dir", str(keys_dir), "--ledger", str(ledger)])
    assert r.exit_code == 0, r.output
    assert LedgerStore(ledger).count() == 3
