"""Public models listing + detail."""
from fastapi import APIRouter, Depends, HTTPException, Query

from kiki_cockpit.deps import get_hf_cache
from kiki_cockpit.models import ModelCard
from kiki_cockpit.models.model_card import ChatBackend, ModelStatus
from kiki_cockpit.services.chat_proxy import ALIAS_TO_GATEWAY_MODEL
from kiki_cockpit.services.hf_cache import HFCache

router = APIRouter(prefix="/api/public", tags=["public"])


# Synthetic cards for the live eu-kiki gateway models. They are not on HF, so
# the HF cache never produces them — but the chat proxy can route to them.
# Adding/removing entries in chat_proxy.ALIAS_TO_GATEWAY_MODEL is the single
# source of truth for chat eligibility, including this listing.
# Per-alias live model details. Centralised here so /models, /models/{id} and
# any future widget read the same source of truth. base_model = base
# architecture; domain = primary use case; description includes hardware host
# + memory footprint so users can pick the right model.
_LIVE_DETAILS: dict[str, dict] = {
    "eu-kiki/apertus-70b": {
        "display_name": "Apertus 70B",
        "base_model": "Apertus 70B",
        "domain": "general",
        "description": (
            "Swiss-stack 70B foundation model — fluent FR/DE/IT/EN. "
            "MLX 8-bit · ~70 GB · runs on Mac Studio M3 Ultra (studio:9301)."
        ),
        "headline": "70B params · 8-bit · Mac Studio M3 Ultra",
    },
    "eu-kiki/devstral-24b": {
        "display_name": "Devstral 24B",
        "base_model": "Mistral Small 3.1",
        "domain": "code",
        "description": (
            "Mistral-AI Devstral 24B — code-focused. MLX 4-bit · ~13 GB · "
            "runs on Mac mini M1 (macm1:9302)."
        ),
        "headline": "24B params · MLX 4-bit · Mac mini M1",
    },
    "eu-kiki/eurollm-22b": {
        "display_name": "EuroLLM 22B",
        "base_model": "EuroLLM 22B",
        "domain": "multilingual",
        "description": (
            "EuroLLM 22B — multilingual EU coverage (24 official languages). "
            "MLX 8-bit · ~22 GB · runs on Mac Studio M3 Ultra (studio:9303)."
        ),
        "headline": "22B params · 8-bit · Mac Studio M3 Ultra",
    },
    "eu-kiki/qwen-35b-a3b": {
        "display_name": "Qwen3.5 35B A3B",
        "base_model": "Qwen3.5 35B (MoE 256 experts, 3B active)",
        "domain": "reasoning",
        "description": (
            "Qwen3.5 35B Active-3B MoE Q3_K_XL — reasoning-tuned with explicit "
            "<think> traces. ~17 GB · llama.cpp on KXKM-AI server (RTX 4090 "
            "via SSH tunnel)."
        ),
        "headline": "35B MoE / 3B active · Q3_K_XL · KXKM-AI",
    },
    "eu-kiki/auto": {
        "display_name": "Auto-router",
        "base_model": "MiniLM L6 v2 + 2-layer MLP",
        "domain": "router",
        "description": (
            "Domain router classifies your prompt over 34 domains and forwards "
            "to the best worker (Apertus 70B / Devstral 24B / EuroLLM 22B / "
            "Qwen 35B / Gemma 3 4B). Decision shown above each reply."
        ),
        "headline": "MiniLM 384d · 34 domains · top1=65 % top3=86 %",
    },
}


def _live_cards() -> list[ModelCard]:
    cards: list[ModelCard] = []
    for alias in ALIAS_TO_GATEWAY_MODEL:
        owner, name = alias.split("/", 1)
        details = _LIVE_DETAILS.get(alias, {})
        cards.append(
            ModelCard(
                id=alias,
                owner=owner,
                name=name,
                display_name=details.get("display_name", name),
                description=details.get("description"),
                base_model=details.get("base_model"),
                domain=details.get("domain"),
                status=ModelStatus.PRODUCTION,
                chat_backend=ChatBackend.EU_KIKI_LIVE,
                chat_eligible=True,
                featured_rank=0,  # surfaces them at the top of the listing
                featured_headline=details.get("headline"),
                hf_url=f"https://huggingface.co/{alias}",
            )
        )
    return cards


@router.get("/models", response_model=list[ModelCard])
def list_models(
    cache: HFCache = Depends(get_hf_cache),
    domain: str | None = Query(default=None),
    base_model: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> list[ModelCard]:
    # Live cards first so the SPA surfaces chat-eligible models prominently.
    cards = _live_cards() + cache.list_cards()
    if domain:
        cards = [c for c in cards if c.domain == domain]
    if base_model:
        cards = [c for c in cards if c.base_model == base_model]
    if status:
        cards = [c for c in cards if c.status.value == status]
    return cards


@router.get("/models/{owner}/{name}", response_model=ModelCard)
def get_model(owner: str, name: str, cache: HFCache = Depends(get_hf_cache)) -> ModelCard:
    model_id = f"{owner}/{name}"
    if model_id in ALIAS_TO_GATEWAY_MODEL:
        return next(c for c in _live_cards() if c.id == model_id)
    card = cache.get_card(model_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    return card
