"""Application settings (from env + defaults)."""
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COCKPIT_", env_file=".env", extra="ignore")

    # Service
    host: str = "127.0.0.1"
    port: int = 9100
    log_level: str = "INFO"

    # Paths to sibling repos (read-only sources)
    kiki_mac_tunner_root: Path = Path.home() / "Documents" / "Projets" / "ailiance-mac-tuner"
    ailiance_root: Path = Path.home() / "Documents" / "Projets" / "ailiance"

    # ailiance gateway
    ailiance_gateway_url: str = "http://localhost:9200"

    # HF
    hf_api_base: str = "https://huggingface.co/api"
    hf_token: str | None = None
    hf_owners: list[str] = Field(default_factory=lambda: ["Ailiance-fr"])
    hf_sync_interval_seconds: int = 600  # 10 min

    # Featured config
    featured_path: Path = Path("featured.yaml")

    # Benchmarks config
    benchmarks_yaml_path: Path = Path(__file__).parent.parent.parent / "benchmarks.yaml"

    # Cache
    cache_dir: Path = Path.home() / ".cache" / "ailiance-demo"

    # Training runs
    training_log_roots: list[Path] = Field(
        default_factory=lambda: [
            Path.home() / "Documents" / "Projets" / "ailiance-mac-tuner" / "logs",
            Path.home() / "Documents" / "Projets" / "ailiance" / "logs",
        ],
    )
    datasets_root: list[Path] = Field(
        default_factory=lambda: [
            Path("/datasets"),
            Path.home() / "Documents" / "Projets" / "ailiance" / "data" / "hf-traced",
        ],
    )
    dataset_flags_dir: Path = Path("/dataset-flags")
    machine_label: str = "studio"
    # Serving is consolidated onto the omlx multi-model server (:8500) plus
    # the two qwen36 multi-LoRA instances (:9360 / :9361), all on Mac Studio.
    # The old per-port workers (9301/9303/9304, macm1:9302, kxkm-ai:8002) are
    # decommissioned and no longer probed.
    workers_to_check: list[dict] = Field(
        default_factory=lambda: [
            {"name": "gateway", "url": "http://host.docker.internal:9300/health"},
            {"name": "omlx", "url": "http://100.116.92.12:8500/health"},
            {"name": "qwen36-hardware", "url": "http://100.116.92.12:9360/health"},
            {"name": "qwen36-code", "url": "http://100.116.92.12:9361/health"},
        ],
    )


settings = Settings()
