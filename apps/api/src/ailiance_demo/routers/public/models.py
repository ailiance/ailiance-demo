"""Public models listing + detail."""
from fastapi import APIRouter, Depends, HTTPException, Query

from ailiance_demo.deps import get_hf_cache
from ailiance_demo.models import ModelCard
from ailiance_demo.models.model_card import ChatBackend, ModelKind, ModelStatus
from ailiance_demo.services.chat_proxy import ALIAS_TO_GATEWAY_MODEL
from ailiance_demo.services.hf_cache import HFCache

router = APIRouter(prefix="/api/public", tags=["public"])


# Synthetic cards for the live ailiance gateway models. They are not on HF, so
# the HF cache never produces them — but the chat proxy can route to them.
# Adding/removing entries in chat_proxy.ALIAS_TO_GATEWAY_MODEL is the single
# source of truth for chat eligibility, including this listing.
# Per-alias live model details. Centralised here so /models, /models/{id} and
# any future widget read the same source of truth. base_model = base
# architecture; domain = primary use case; description includes hardware host
# + memory footprint so users can pick the right model.
# 1 GiB constant for size annotations
_GIB = 1024**3

_LIVE_DETAILS: dict[str, dict] = {
    "ailiance/mistral-medium-3.5-128b": {
        "display_name": "Mistral Medium 3.5 128B",
        "base_model": "Mistral Medium 3.5 128B",
        "domain": "general",
        "description": (
            "Mistral AI flagship 128B — reasoning, code, vision, agents in a "
            "single model (absorbs Devstral 2 + Magistral + Pixtral). "
            "Released April 29 2026 under Modified MIT — free commercial use "
            "for individuals, startups, mid-market, and universities; "
            "high-revenue enterprises require Mistral's paid API. "
            "262 k context window. Runs on Mac Studio M3 Ultra."
        ),
        "headline": "128B params · MLX Q8 · 262k context · omlx (Mac Studio M3 Ultra)",
        "parameters": 128_000_000_000,
        "disk_size_bytes": 124 * _GIB,
        "memory_gb": 130.0,
        "quantization": "MLX Q8",
        "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
        "architecture": "mlx",
        "license": "modified-mit",
        "kind": ModelKind.QUANTIZED,
        # mistralai/Mistral-Medium-3.5* is gated (401 unauth). Point to the
        # public org page so visitors land somewhere meaningful.
        "hf_url": "https://huggingface.co/mistralai",
        "top_eval_score": 0.87,
        "top_eval_benchmark": "MT-Bench",
    },
    "ailiance/gemma4-e4b-curriculum": {
        "display_name": "Gemma 4 E4B + ailiance curriculum LoRA",
        "base_model": "google/gemma-4-E4B-it",
        "domain": "general",
        "description": (
            "Google Gemma 4 E4B Instruction-Tuned avec adapter LoRA fine-tuné "
            "en curriculum 4 phases (seq 512 → 1024 → 2048 → 3072) sur le "
            "dataset ailiance (~82k conversations, electronics + code). "
            "Test loss 2.094 (perplexity 8.12). Sert aussi de fallback vision "
            "léger. Servi par le serveur omlx sur Mac Studio (:8500)."
        ),
        "headline": "E4B · MLX 4-bit + LoRA · omlx (Mac Studio)",
        "parameters": 4_000_000_000,
        "disk_size_bytes": 4 * _GIB,
        "memory_gb": 12.0,
        "quantization": "MLX 4-bit + LoRA",
        "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
        "architecture": "mlx",
        "license": "gemma-terms",
        "kind": ModelKind.FINE_TUNED,
        "hf_url": "https://huggingface.co/Ailiance-fr/gemma-4-E4B-eukiki-lora",
        "top_eval_score": 0.61,
        "top_eval_benchmark": "MT-Bench-FR (LoRA tuned)",
    },
    "ailiance/qwen3-coder-next-80b": {
        "display_name": "Qwen3-Coder-Next 80B (qwen36 multi-LoRA)",
        "base_model": "Qwen/Qwen3-Coder-Next-80B-A3B",
        "domain": "code",
        "description": (
            "Qwen3-Coder-Next 80B sparse MoE (3B active per token) — 8-bit "
            "MLX served by the omlx server on Mac Studio. Also the base for "
            "the qwen36-35B multi-LoRA hardware/code specialists (30 adapters "
            "hot-swapped on the :9360 / :9361 instances)."
        ),
        "headline": "80B MoE / 3B active · MLX 8-bit · omlx (Mac Studio)",
        "parameters": 80_000_000_000,
        "disk_size_bytes": 48_410_988_384,
        "memory_gb": 50.0,
        "quantization": "MLX 8-bit",
        "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
        "architecture": "mlx",
        "license": "apache-2.0",
        "kind": ModelKind.QUANTIZED,
        "hf_url": "https://huggingface.co/Qwen",
        "top_eval_score": 0.91,
        "top_eval_benchmark": "MMLU / GSM8K",
    },
    "ailiance/eurollm-22b": {
        "display_name": "EuroLLM 22B Instruct",
        "base_model": "utter-project/EuroLLM-22B-Instruct",
        "domain": "multilingual",
        "description": (
            "EU-sovereign multilingual instruction model covering all 24 EU "
            "official languages. MLX-served by the omlx server on Mac Studio "
            "(:8500)."
        ),
        "headline": "22B · multilingual EU · omlx (Mac Studio)",
        "parameters": 22_000_000_000,
        "disk_size_bytes": 45 * _GIB,
        "memory_gb": 45.0,
        "quantization": "MLX",
        "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
        "architecture": "mlx",
        "license": "apache-2.0",
        "kind": ModelKind.QUANTIZED,
        "hf_url": "https://huggingface.co/utter-project",
        "top_eval_score": 0.74,
        "top_eval_benchmark": "MT-Bench (multilingual)",
    },
    "ailiance/apertus-70b": {
        "display_name": "Apertus 70B Instruct",
        "base_model": "swiss-ai/Apertus-70B-Instruct-2509",
        "domain": "general",
        "description": (
            "Swiss-sovereign Apertus 70B instruction model. The BF16 source "
            "was deleted in the storage cleanup; the 4-bit MLX build is "
            "retained and served on demand by the omlx server on Mac Studio."
        ),
        "headline": "70B · MLX 4-bit · omlx (Mac Studio)",
        "parameters": 70_000_000_000,
        "disk_size_bytes": 37 * _GIB,
        "memory_gb": 40.0,
        "quantization": "MLX 4-bit",
        "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
        "architecture": "mlx",
        "license": "apache-2.0",
        "kind": ModelKind.QUANTIZED,
        "hf_url": "https://huggingface.co/swiss-ai",
        "top_eval_score": 0.80,
        "top_eval_benchmark": "MMLU",
    },
    "ailiance/auto": {
        "display_name": "Auto-router",
        "base_model": "all-MiniLM-L6-v2 384d + 2-layer MLP (hidden 256)",
        "domain": "router",
        "description": (
            "Domain router classifies your prompt over 47 domains and forwards "
            "to the best specialist. Trained on the AI-Act-traceable clean "
            "corpus (router v9, 2026-05-30). Hardware/EDA domains (kicad / "
            "spice / stm32 / emc / embedded / power) route to the qwen36 "
            "multi-LoRA specialists with a sandboxed Docker validator. "
            "Generalist domains (math, code, multilingual, raisonnement) route "
            "directly. The decision is shown above each reply in the playground."
        ),
        "headline": "all-MiniLM-L6-v2 384d · 47 domains · macro-F1 0.889 · router v9",
        "parameters": 22_700_000,  # MiniLM L6 v2 ≈ 22.7M
        "disk_size_bytes": 90_500_000,
        "memory_gb": 0.2,
        "quantization": "FP32",
        "host": "electron-server (gateway-side, CPU)",
        "architecture": "safetensors",
        "license": "apache-2.0",
        "kind": ModelKind.FINE_TUNED,
        "hf_url": "https://huggingface.co/Ailiance-fr",
        "top_eval_score": 0.889,
        "top_eval_benchmark": "iact-bench 47 domains macro-F1",
    },
    "ailiance/granite-30b": {
        "display_name": "Granite 4.1 30B Instruct",
        "base_model": "ibm-granite/granite-4.1-30B-instruct",
        "domain": "code",
        "description": (
            "IBM Granite 4.1 30B Instruct — code-first instruction-tuned "
            "open model with strong enterprise SQL / RAG / tool-use scores. "
            "MLX-served by the omlx server on Mac Studio (:8500)."
        ),
        "headline": "30B · MLX · omlx (Mac Studio)",
        "parameters": 30_000_000_000,
        "disk_size_bytes": 18 * _GIB,
        "memory_gb": 20.0,
        "quantization": "MLX",
        "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
        "architecture": "mlx",
        "license": "apache-2.0",
        "kind": ModelKind.QUANTIZED,
        # ibm-granite/granite-4.1-30B-instruct is gated. Point to the org.
        "hf_url": "https://huggingface.co/ibm-granite",
        "top_eval_score": 0.83,
        "top_eval_benchmark": "HumanEval+ / BigBench-Hard code",
    },
    "ailiance/devstral-base": {
        "display_name": "Devstral Small 2 24B",
        "base_model": "mistralai/Devstral-Small-2-24B",
        "domain": "code",
        "description": (
            "Mistral Devstral Small 2 24B — agentic coding base. Now served "
            "by the omlx server on Mac Studio (:8500); the old macm1 :9302 "
            "Devstral worker is decommissioned."
        ),
        "headline": "24B · MLX · omlx (Mac Studio)",
        "parameters": 24_000_000_000,
        "disk_size_bytes": 14 * _GIB,
        "memory_gb": 15.0,
        "quantization": "MLX",
        "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
        "architecture": "mlx",
        "license": "apache-2.0",
        "kind": ModelKind.QUANTIZED,
        "hf_url": "https://huggingface.co/mistralai",
        "top_eval_score": 0.84,
        "top_eval_benchmark": "SWE-bench Verified",
    },
    "ailiance/mixtral-8x22b": {
        "display_name": "Mixtral 8x22B",
        "base_model": "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "domain": "general",
        "description": (
            "Mistral Mixtral 8x22B sparse MoE generalist. MLX-served by the "
            "omlx server on Mac Studio (:8500)."
        ),
        "headline": "8x22B MoE · MLX · omlx (Mac Studio)",
        "parameters": 141_000_000_000,
        "disk_size_bytes": 80 * _GIB,
        "memory_gb": 85.0,
        "quantization": "MLX",
        "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
        "architecture": "mlx",
        "license": "apache-2.0",
        "kind": ModelKind.QUANTIZED,
        "hf_url": "https://huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1",
        "top_eval_score": 0.79,
        "top_eval_benchmark": "MMLU",
    },
}


# 12 mascarade LoRA specialists — one card, twelve adapters. Each entry lists
# its domain, blurb, sandboxed validator(s), and approximate training steps.
# The cockpit surfaces them collectively in /models/ailiance/mascarade.
MASCARADE_LORAS: list[dict] = [
    {"name": "kicad", "domain": "kicad", "steps": 522,
     "blurb": "KiCad schematic & PCB DSL — s-expression .kicad_sch and .kicad_pcb generation",
     "validator": "kicad-cli ERC + DRC sandboxed (--network=none)"},
    {"name": "spice", "domain": "spice", "steps": 412,
     "blurb": "SPICE netlist + simulation — ngspice / Xyce / LTspice idiomatic input",
     "validator": "ngspice batch --no-spiceinit"},
    {"name": "stm32", "domain": "stm32", "steps": 350,
     "blurb": "STM32 / ARM Cortex-M embedded — HAL/LL, FreeRTOS, peripheral init",
     "validator": "arm-none-eabi-gcc + cppcheck"},
    {"name": "emc", "domain": "emc", "steps": 280,
     "blurb": "EMC / EMI compliance — CISPR / FCC limits, filter & decoupling design",
     "validator": "rule-based EMC checker (compatibility report)"},
    {"name": "embedded", "domain": "embedded", "steps": 100,
     "blurb": "Generic embedded C/C++ — bare-metal drivers, MMIO, ISR, DMA",
     "validator": "g++ + compile + cppcheck"},
    {"name": "platformio", "domain": "platformio", "steps": 2,
     "blurb": "PlatformIO / Arduino — board configs, library targets, build pipeline",
     "validator": "pio run --target lint"},
    {"name": "freecad", "domain": "freecad", "steps": 2,
     "blurb": "FreeCAD scripting — Python macros for parametric modelling & 3D MCAD",
     "validator": "freecadcmd headless script run"},
    {"name": "dsp", "domain": "dsp", "steps": 2,
     "blurb": "DSP / signal processing — IIR/FIR, FFT, audio + RF analyse",
     "validator": "numpy + scipy validator"},
    {"name": "iot", "domain": "iot", "steps": 2,
     "blurb": "IoT / connectivity — MQTT, BLE, LoRa, ESP-IDF, Zephyr",
     "validator": "ESP-IDF idf.py build"},
    {"name": "power", "domain": "power", "steps": 2,
     "blurb": "Power electronics — DC/DC, converters, motor drives, battery management",
     "validator": "ngspice transient + steady-state"},
    {"name": "components-review", "domain": "components-review", "steps": 200,
     "blurb": "BOM / parts review — recommends alternatives, flags obsolescence, sourcing",
     "validator": "OctoPart / Digi-Key API cross-check"},
    {"name": "coder", "domain": "code", "steps": 300,
     "blurb": "Polyglot coder — Python, Rust, TypeScript, Go with iact-bench code validators",
     "validator": "tsc, ruff, rustc, go vet"},
]


# Additional gateway aliases exposed by the router but without a dedicated
# detail entry above. Light auto-generated cards so /models reflects the
# real /v1/models surface of the gateway.
_LIVE_DETAILS["ailiance/pixtral-12b"] = {
    "display_name": "Pixtral 12B (vision)",
    "base_model": "mistralai/Pixtral-12B",
    "domain": "vision",
    "description": (
        "Mistral Pixtral 12B multimodal — texte + image. Worker vision "
        "canonique, servi par le serveur omlx sur Mac Studio (:8500). "
        "Gemma 4 E4B sert de fallback vision léger."
    ),
    "headline": "vision · 12B · omlx (Mac Studio)",
    "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
    "architecture": "mlx",
    "license": "apache-2.0",
    "kind": ModelKind.QUANTIZED,
    "hf_url": "https://huggingface.co/mistralai/Pixtral-12B-2409",
    "top_eval_score": 0.72,
    "top_eval_benchmark": "MMMU vision",
}
_LIVE_DETAILS["ailiance/reasoning-r1"] = {
    "display_name": "Reasoning R1",
    "base_model": "DeepSeek-R1-Distill-Qwen-32B",
    "domain": "reasoning",
    "description": (
        "Modèle de raisonnement chain-of-thought (DeepSeek-R1 distill 32B). "
        "Servi par le serveur omlx sur Mac Studio (:8500)."
    ),
    "headline": "chain-of-thought · reasoning · omlx (Mac Studio)",
    "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
    "architecture": "mlx",
    "license": "apache-2.0",
    "kind": ModelKind.DISTILLED,
    "hf_url": "https://huggingface.co/deepseek-ai",
    "top_eval_score": 0.89,
    "top_eval_benchmark": "AIME / MATH",
}
_LIVE_DETAILS["ailiance/coder-pro"] = {
    "display_name": "Coder Pro",
    "base_model": "Qwen3-Coder-30B-A3B-Instruct",
    "domain": "code",
    "description": (
        "Spécialiste code généraliste avec validators iact-bench (tsc, ruff, "
        "rustc, go vet). Servi par le serveur omlx sur Mac Studio (:8500)."
    ),
    "headline": "code · validators · omlx (Mac Studio)",
    "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
    "architecture": "mlx",
    "license": "apache-2.0",
    "kind": ModelKind.QUANTIZED,
    "hf_url": "https://huggingface.co/Qwen",
    "top_eval_score": 0.86,
    "top_eval_benchmark": "HumanEval+ / MultiPL-E",
}
_LIVE_DETAILS["ailiance/mistral-small-3.5"] = {
    "display_name": "Mistral Small 3.5",
    "base_model": "mistralai/Mistral-Small-3.5-24B-Instruct",
    "domain": "general",
    "description": (
        "Mistral Small 3.5 24B — généraliste rapide, alternative légère au "
        "Medium. Servi par le serveur omlx sur Mac Studio (:8500)."
    ),
    "headline": "24B · général · fast · omlx (Mac Studio)",
    "host": "studio (omlx :8500, Mac Studio M3 Ultra)",
    "architecture": "mlx",
    "license": "apache-2.0",
    "kind": ModelKind.QUANTIZED,
    "hf_url": "https://huggingface.co/mistralai",
    "top_eval_score": 0.79,
    "top_eval_benchmark": "MT-Bench",
}

_LIVE_DETAILS["ailiance/mascarade"] = {
    "display_name": "Mascarade · LoRAs spécialistes qwen36",
    "base_model": "Qwen3.6-35B-A3B + LoRA",
    "domain": "hardware-specialists",
    "description": (
        "Famille d'adaptateurs LoRA fine-tunés (curriculum) sur le modèle de "
        "base Qwen3.6-35B-A3B. Servis par deux instances multi-LoRA sur Mac "
        "Studio (:9360 hardware/EDA/math, :9361 code/web/lang) avec hot-swap "
        "des 30 adaptateurs. L'auto-router classifie le domaine du prompt et "
        "délègue au spécialiste correspondant, puis fait passer la sortie "
        "dans un validator Docker sandboxé. La fiche détaillée liste les "
        "spécialistes avec leur domaine et leur validator dédié."
    ),
    "headline": "Qwen3.6-35B + LoRAs · multi-LoRA :9360/:9361 (Mac Studio) · validator sandbox",
    "parameters": 35_000_000_000,
    "disk_size_bytes": 70 * _GIB,
    "memory_gb": 70.0,
    "quantization": "MLX bf16 + LoRA",
    "host": "studio (multi-LoRA :9360/:9361, Mac Studio M3 Ultra)",
    "architecture": "mlx",
    "license": "apache-2.0",
    "kind": ModelKind.LORA,
}


# The 12 mascarade-* gateway aliases stay in ALIAS_TO_GATEWAY_MODEL so the
# gateway router can still address each specialist directly, but the public
# /models catalog folds them into a single "ailiance/mascarade" card.
# The family alias itself is also hidden from the loop since the explicit
# append below emits it once with the right metadata.
_MASCARADE_HIDDEN = {f"ailiance/mascarade-{lo['name']}" for lo in MASCARADE_LORAS} | {"ailiance/mascarade"}


def _live_cards() -> list[ModelCard]:
    cards: list[ModelCard] = []
    for alias in ALIAS_TO_GATEWAY_MODEL:
        if alias in _MASCARADE_HIDDEN:
            continue  # collapsed into the single ailiance/mascarade card below
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
                chat_backend=ChatBackend.AILIANCE_LIVE,
                chat_eligible=True,
                featured_rank=0,
                featured_headline=details.get("headline"),
                # Per-entry hf_url when known (upstream base or Ailiance-fr
                # adapter); fall back to the org page since the bare
                # huggingface.co/ailiance/... namespace is squatted (401).
                hf_url=details.get("hf_url", "https://huggingface.co/Ailiance-fr"),
                parameters=details.get("parameters"),
                disk_size_bytes=details.get("disk_size_bytes"),
                memory_gb=details.get("memory_gb"),
                quantization=details.get("quantization"),
                host=details.get("host"),
                architecture=details.get("architecture"),
                license=details.get("license"),
                kind=details.get("kind", ModelKind.UNKNOWN),
                top_eval_score=details.get("top_eval_score"),
                top_eval_benchmark=details.get("top_eval_benchmark"),
            )
        )

    # Append the consolidated mascarade card (not in ALIAS_TO_GATEWAY_MODEL —
    # it represents the LoRA family, individual specialists are routed
    # transparently by the auto-router).
    md = _LIVE_DETAILS["ailiance/mascarade"]
    cards.append(
        ModelCard(
            id="ailiance/mascarade",
            owner="ailiance",
            name="mascarade",
            display_name=md["display_name"],
            description=md["description"],
            base_model=md["base_model"],
            domain=md["domain"],
            status=ModelStatus.PRODUCTION,
            chat_backend=ChatBackend.AILIANCE_LIVE,
            chat_eligible=True,
            featured_rank=0,
            featured_headline=md["headline"],
            hf_url="https://huggingface.co/Ailiance-fr",
            parameters=md["parameters"],
            disk_size_bytes=md["disk_size_bytes"],
            memory_gb=md["memory_gb"],
            quantization=md["quantization"],
            host=md["host"],
            architecture=md["architecture"],
            license=md["license"],
            kind=md["kind"],
            top_eval_score=0.62,
            top_eval_benchmark="iact-bench hardware avg",
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
    if model_id == "ailiance/mascarade" or model_id in ALIAS_TO_GATEWAY_MODEL:
        return next(c for c in _live_cards() if c.id == model_id)
    card = cache.get_card(model_id)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    return card


@router.get("/models/ailiance/mascarade/loras")
def mascarade_loras() -> list[dict]:
    """List the 12 LoRA specialists under the mascarade family."""
    return MASCARADE_LORAS
