"""Tests for /api/public/models."""
from fastapi.testclient import TestClient


def test_list_models_returns_cards(client_with_cache: TestClient) -> None:
    response = client_with_cache.get("/api/public/models")

    assert response.status_code == 200
    cards = response.json()
    ids = {c["id"] for c in cards}
    # Live workers (omlx :8500 + qwen36 :9360/:9361) + auto-router +
    # consolidated mascarade card + mocked HF entry.
    assert {
        "ailiance/mistral-medium-3.5-128b",
        "ailiance/gemma4-e4b-curriculum",
        "ailiance/qwen3-coder-next-80b",
        "ailiance/granite-30b",
        "ailiance/eurollm-22b",
        "ailiance/mascarade",
        "ailiance/auto",
        "Ailiance-fr/micro-kiki-v3",
    }.issubset(ids)
    hf_card = next(c for c in cards if c["id"] == "Ailiance-fr/micro-kiki-v3")
    assert hf_card["chat_eligible"] is False


def test_get_model_returns_single_card(client_with_cache: TestClient) -> None:
    response = client_with_cache.get("/api/public/models/Ailiance-fr/micro-kiki-v3")

    assert response.status_code == 200
    card = response.json()
    assert card["display_name"] == "Micro-Ailiance v3"


def test_get_model_404_when_unknown(client_with_cache: TestClient) -> None:
    response = client_with_cache.get("/api/public/models/Ailiance-fr/does-not-exist")

    assert response.status_code == 404
