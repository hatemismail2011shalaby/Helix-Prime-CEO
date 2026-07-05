from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bridge import app  # noqa: E402


def test_chat_endpoint_returns_reply() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/chat",
        json={"message": "hello", "agent": "sami"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "reply" in payload
    assert payload["agent"] == "sami"
