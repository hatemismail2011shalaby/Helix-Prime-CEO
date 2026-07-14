from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bridge import app  # noqa: E402


def test_homepage_contains_workspace_ui() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    body = response.text
    assert "Helix Prime CEO" in body
    assert "workspace" in body.lower()
    assert "thinking" in body.lower()
