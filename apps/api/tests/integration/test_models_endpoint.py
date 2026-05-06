"""Tests for /api/public/models."""
from fastapi.testclient import TestClient


def test_list_models_returns_cards(client_with_cache: TestClient) -> None:
    response = client_with_cache.get("/api/public/models")

    assert response.status_code == 200
    cards = response.json()
    ids = {c["id"] for c in cards}
    # 5 live eu-kiki workers + auto-router + the mocked HF entry.
    assert {
        "eu-kiki/apertus-70b",
        "eu-kiki/devstral-24b",
        "eu-kiki/eurollm-22b",
        "eu-kiki/gemma3-4b",
        "eu-kiki/qwen3-next-80b-a3b-instruct",
        "eu-kiki/auto",
        "clemsail/micro-kiki-v3",
    }.issubset(ids)
    hf_card = next(c for c in cards if c["id"] == "clemsail/micro-kiki-v3")
    assert hf_card["chat_eligible"] is False


def test_get_model_returns_single_card(client_with_cache: TestClient) -> None:
    response = client_with_cache.get("/api/public/models/clemsail/micro-kiki-v3")

    assert response.status_code == 200
    card = response.json()
    assert card["display_name"] == "Micro-KIKI v3"


def test_get_model_404_when_unknown(client_with_cache: TestClient) -> None:
    response = client_with_cache.get("/api/public/models/clemsail/does-not-exist")

    assert response.status_code == 404
