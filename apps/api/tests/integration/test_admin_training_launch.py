from fastapi.testclient import TestClient

from ailiance_demo.deps import get_training_launcher
from ailiance_demo.main import app
from ailiance_demo.services.training_launcher import (
    DEFAULT_HOST_FOR_MODEL,
    LaunchInfo,
    TrainingLauncher,
)


def test_launch_endpoint_requires_auth() -> None:
    client = TestClient(app)
    r = client.post(
        "/api/admin/training/launch",
        json={"base_model": "ailiance/gemma4-e4b-curriculum", "dataset_domain": "x"},
    )
    assert r.status_code == 401


def test_launch_endpoint_returns_run_id_and_host() -> None:
    captured: list[tuple[str, str, str]] = []

    def fake_dispatch(host: str, run_id: str, yaml_text: str) -> None:
        captured.append((host, run_id, yaml_text))

    app.dependency_overrides[get_training_launcher] = lambda: TrainingLauncher(
        host_for_model=DEFAULT_HOST_FOR_MODEL,
        dispatcher=fake_dispatch,
    )
    try:
        client = TestClient(app)
        r = client.post(
            "/api/admin/training/launch",
            headers={"X-Tailscale-User": "test"},
            json={
                "base_model": "ailiance/gemma4-e4b-curriculum",
                "dataset_domain": "electronics-hw",
                "iters": 100,
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["host"] == "macm1"
        assert body["run_id"].startswith("electronics-hw-")
        assert len(captured) == 1
    finally:
        app.dependency_overrides.clear()


def test_launch_endpoint_unknown_model_returns_400() -> None:
    app.dependency_overrides[get_training_launcher] = lambda: TrainingLauncher(
        host_for_model={}, dispatcher=lambda *_: None
    )
    try:
        client = TestClient(app)
        r = client.post(
            "/api/admin/training/launch",
            headers={"X-Tailscale-User": "test"},
            json={"base_model": "x/y", "dataset_domain": "z"},
        )
        assert r.status_code == 400
        assert "x/y" in r.json()["detail"]
    finally:
        app.dependency_overrides.clear()
