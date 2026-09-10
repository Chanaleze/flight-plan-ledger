"""Docs guardrails: research note exists and is linked."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "docs" / "research" / "nats-system-background.md"
PROFILE = ROOT / "docs" / "PROJECT-PROFILE-AND-WAY-FORWARD.md"
README = ROOT / "README.md"
OVERVIEW = ROOT / "docs" / "architecture" / "overview.md"


def test_nats_background_exists_with_expected_sections():
    assert RESEARCH.exists(), "docs/research/nats-system-background.md missing"
    text = RESEARCH.read_text(encoding="utf-8")
    for heading in (
        "What NATS Currently Uses",
        "Where the Fault Is",
        "How We Bring Value",
    ):
        assert heading in text


def test_readme_links_nats_background():
    text = README.read_text(encoding="utf-8")
    assert "docs/research/nats-system-background.md" in text


def test_overview_links_nats_background():
    text = OVERVIEW.read_text(encoding="utf-8")
    assert "nats-system-background" in text.lower()


def test_project_profile_exists_with_expected_sections():
    assert PROFILE.exists(), "docs/PROJECT-PROFILE-AND-WAY-FORWARD.md missing"
    text = PROFILE.read_text(encoding="utf-8")
    for heading in (
        "One-Sentence Summary",
        "Business Model",
        "Way Forward",
        "Explicit Non-Goals",
    ):
        assert heading in text
    # Must be clean markdown: no literal escape backslashes
    assert "\\#" not in text and "\\*" not in text


def test_readme_links_project_profile():
    text = README.read_text(encoding="utf-8")
    assert "docs/PROJECT-PROFILE-AND-WAY-FORWARD.md" in text


def test_adrs_exist_with_decision_format():
    for n in ("0001-permissioned-ledger", "0002-sidecar-architecture", "0003-minimal-on-ledger-data"):
        p = ROOT / "docs" / "adr" / f"{n}.md"
        assert p.exists(), f"docs/adr/{n}.md missing"
        text = p.read_text(encoding="utf-8")
        for heading in ("## Status", "## Context", "## Decision", "## Consequences"):
            assert heading in text, f"{n}.md missing {heading}"


def test_contributing_states_sidecar_rules():
    p = ROOT / "CONTRIBUTING.md"
    assert p.exists(), "CONTRIBUTING.md missing"
    text = p.read_text(encoding="utf-8").lower()
    assert "sidecar" in text
    assert "pytest" in text


def test_future_surface_is_marked_sketch_not_product():    # Interface sketches and the OpenAPI draft must never look implemented
    for p in (
        ROOT / "services" / "README.md",
        ROOT / "services" / "ledger-writer" / "INTERFACE.md",
        ROOT / "services" / "verifier" / "INTERFACE.md",
        ROOT / "contracts" / "openapi-sketch.yaml",
    ):
        assert p.exists(), f"{p.relative_to(ROOT)} missing"
        text = p.read_text(encoding="utf-8").lower()
        assert "sketch" in text or "future" in text, f"{p.name} not marked as sketch/future"


def test_ops_runbook_and_limitations_exist():
    for name, markers in (
        ("ops/RECOVERY-RUNBOOK.md", ("verify-chain", "last known good", "TASK-LOG")),
        ("ops/KEY-ROTATION-DRILL.md", ("rotation", "verify-chain", "TASK-LOG")),
        ("ops/LIMITATIONS.md", ("does NOT do", "revocation", "permissioned")),
    ):
        p = ROOT / name
        assert p.exists(), f"{name} missing"
        text = p.read_text(encoding="utf-8")
        lowered = text.lower()
        for m in markers:
            assert m.lower() in lowered, f"{name} missing {m!r}"
