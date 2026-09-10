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
