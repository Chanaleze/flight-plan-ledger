"""E2E tests for the click CLI (init-keys / record / verify / list / recover)."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from flight_plan_ledger.cli.main import cli


def _write_plan(path: Path, callsign: str = "QTR23") -> Path:
    plan = {
        "callsign": callsign,
        "aircraft_id": "A7-BAA",
        "dof": "2026-09-09",
        "origin": "OTHH",
        "destination": "EGLL",
        "departure_time_utc": "2026-09-09T07:30:00Z",
        "route": "OTHH DCT EGLL",
    }
    path.write_text(json.dumps(plan), encoding="utf-8")
    return path


def _base_args(tmp_path: Path, key_id: str = "nats-writer-01"):
    keys_dir = tmp_path / "keys"
    ledger = tmp_path / "ledger.jsonl"
    return keys_dir, ledger, key_id


def test_init_keys_then_record_verify_chain_list_recover(tmp_path: Path):
    runner = CliRunner()
    keys_dir, ledger, key_id = _base_args(tmp_path)
    plan_file = _write_plan(tmp_path / "plan.json")

    r = runner.invoke(cli, ["init-keys", "--key-id", key_id, "--keys-dir", str(keys_dir)])
    assert r.exit_code == 0, r.output
    assert (keys_dir / f"{key_id}.private.pem").exists()

    r = runner.invoke(cli, [
        "record", "--plan", str(plan_file),
        "--keys-dir", str(keys_dir), "--ledger", str(ledger),
    ])
    assert r.exit_code == 0, r.output
    assert "sequence" in r.output.lower() or "Recorded" in r.output

    r = runner.invoke(cli, [
        "verify", "--plan", str(plan_file),
        "--key-id", key_id, "--keys-dir", str(keys_dir), "--ledger", str(ledger),
    ])
    assert r.exit_code == 0, r.output
    assert "VALID" in r.output or "valid" in r.output.lower()

    r = runner.invoke(cli, ["verify-chain", "--ledger", str(ledger)])
    assert r.exit_code == 0, r.output
    assert "valid" in r.output.lower()

    r = runner.invoke(cli, ["list", "--ledger", str(ledger)])
    assert r.exit_code == 0, r.output
    assert "QTR23" in r.output

    r = runner.invoke(cli, ["recover", "--ledger", str(ledger)])
    assert r.exit_code == 0, r.output
    assert "QTR23" in r.output

    out_json = tmp_path / "recovery.json"
    r = runner.invoke(cli, [
        "recover", "--ledger", str(ledger), "--output", str(out_json), "--summary",
    ])
    assert r.exit_code == 0, r.output
    assert out_json.exists()
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["entry_count"] == 1


def test_init_keys_refuses_overwrite(tmp_path: Path):
    runner = CliRunner()
    keys_dir, _, key_id = _base_args(tmp_path)
    assert runner.invoke(cli, ["init-keys", "--key-id", key_id, "--keys-dir", str(keys_dir)]).exit_code == 0
    second = runner.invoke(cli, ["init-keys", "--key-id", key_id, "--keys-dir", str(keys_dir)])
    assert second.exit_code == 1
    assert "already exists" in second.output.lower()


def test_record_without_keys_fails(tmp_path: Path):
    runner = CliRunner()
    keys_dir, ledger, _ = _base_args(tmp_path)
    plan_file = _write_plan(tmp_path / "plan.json")
    r = runner.invoke(cli, [
        "record", "--plan", str(plan_file),
        "--keys-dir", str(keys_dir), "--ledger", str(ledger),
    ])
    assert r.exit_code == 1
    assert "init-keys" in r.output.lower() or "not found" in r.output.lower()


def test_verify_unknown_plan_fails(tmp_path: Path):
    runner = CliRunner()
    keys_dir, ledger, key_id = _base_args(tmp_path)
    assert runner.invoke(cli, ["init-keys", "--key-id", key_id, "--keys-dir", str(keys_dir)]).exit_code == 0
    recorded = _write_plan(tmp_path / "recorded.json", callsign="QTR23")
    other = _write_plan(tmp_path / "other.json", callsign="BAW99")
    assert runner.invoke(cli, [
        "record", "--plan", str(recorded),
        "--keys-dir", str(keys_dir), "--ledger", str(ledger),
    ]).exit_code == 0
    r = runner.invoke(cli, [
        "verify", "--plan", str(other),
        "--key-id", key_id, "--keys-dir", str(keys_dir), "--ledger", str(ledger),
    ])
    assert r.exit_code == 1


def test_verify_chain_empty_ok(tmp_path: Path):
    runner = CliRunner()
    _, ledger, _ = _base_args(tmp_path)
    r = runner.invoke(cli, ["verify-chain", "--ledger", str(ledger)])
    assert r.exit_code == 0
    assert "empty" in r.output.lower() or "valid" in r.output.lower()


def test_recover_empty_ledger(tmp_path: Path):
    runner = CliRunner()
    _, ledger, _ = _base_args(tmp_path)
    r = runner.invoke(cli, ["recover", "--ledger", str(ledger)])
    assert r.exit_code == 0
    assert "No accepted plans" in r.output or "0 accepted" in r.output
