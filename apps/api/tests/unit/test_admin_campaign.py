"""Tests for the medium35 campaign proxy router.

Mocks ``ailiance_demo.services.gateway_admin`` so the upstream gateway is
never actually contacted; verifies the cockpit-api correctly forwards
status, start, abort, and log requests.
"""
from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from ailiance_demo.main import create_app
from ailiance_demo.services import gateway_admin

AUTH = {"X-Tailscale-User": "test"}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    # Token must be present for the proxy not to short-circuit with 503,
    # but we mock every call so its value doesn't matter.
    monkeypatch.setattr(gateway_admin, "_ADMIN_TOKEN", "test-token", raising=False)
    app = create_app()
    with TestClient(app) as c:
        yield c


def test_status_proxies_gateway_response(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = AsyncMock(return_value={"status": "TRAINING", "current_domain": "kicad-dsl"})
    monkeypatch.setattr(gateway_admin, "get_status", fake)

    r = client.get("/api/admin/training/campaign/status", headers=AUTH)

    assert r.status_code == 200
    assert r.json() == {"status": "TRAINING", "current_domain": "kicad-dsl"}
    fake.assert_awaited_once()


def test_start_forwards_domain_list(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = AsyncMock(return_value={"accepted": True})
    monkeypatch.setattr(gateway_admin, "start_campaign", fake)

    r = client.post(
        "/api/admin/training/campaign/start",
        headers=AUTH,
        json={"domains": ["a", "b"]},
    )

    assert r.status_code == 202
    assert r.json() == {"accepted": True}
    fake.assert_awaited_once_with(["a", "b"])


def test_start_with_no_body_forwards_none(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = AsyncMock(return_value={"accepted": True})
    monkeypatch.setattr(gateway_admin, "start_campaign", fake)

    r = client.post("/api/admin/training/campaign/start", headers=AUTH, json={})

    assert r.status_code == 202
    fake.assert_awaited_once_with(None)


def test_abort_proxies(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = AsyncMock(return_value={"aborted": True})
    monkeypatch.setattr(gateway_admin, "abort_campaign", fake)

    r = client.post("/api/admin/training/campaign/abort", headers=AUTH)

    assert r.status_code == 200
    assert r.json() == {"aborted": True}
    fake.assert_awaited_once()


def test_log_returns_plain_text_and_clamps_tail(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = AsyncMock(return_value="Iter 100: Train loss 0.5\nIter 200: Train loss 0.4\n")
    monkeypatch.setattr(gateway_admin, "get_domain_log", fake)

    r = client.get(
        "/api/admin/training/campaign/log/kicad-dsl",
        params={"tail": 5},
        headers=AUTH,
    )

    assert r.status_code == 200
    assert "Iter 100" in r.text
    assert r.headers["content-type"].startswith("text/plain")
    fake.assert_awaited_once_with("kicad-dsl", 5)


def test_log_clamps_tail_to_max(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = AsyncMock(return_value="x")
    monkeypatch.setattr(gateway_admin, "get_domain_log", fake)

    r = client.get(
        "/api/admin/training/campaign/log/kicad-dsl",
        params={"tail": 99999},
        headers=AUTH,
    )
    assert r.status_code == 200
    fake.assert_awaited_once_with("kicad-dsl", 1000)


def test_status_requires_auth(client: TestClient) -> None:
    r = client.get("/api/admin/training/campaign/status")
    assert r.status_code == 401
