"""Async client for the ailiance gateway's medium35 training campaign endpoints.

The gateway exposes four admin endpoints (all gated by ``X-Admin-Token``):

- ``GET    /admin/training/status``
- ``POST   /admin/training/start``
- ``POST   /admin/training/abort``
- ``GET    /admin/training/log/{domain}?tail=N``

The cockpit-api proxies them so the browser never sees the token.
"""
from __future__ import annotations

import os

import httpx
import structlog
from fastapi import HTTPException

log = structlog.get_logger()

# Resolve at module load (env). The actual token is required at first call
# rather than at import so the module can be imported in tests without it.
_GATEWAY_URL = os.environ.get("COCKPIT_AILIANCE_GATEWAY_URL") or os.environ.get(
    "AILIANCE_GATEWAY_URL", "http://localhost:9300"
)
_ADMIN_TOKEN = os.environ.get("COCKPIT_AILIANCE_ADMIN_TOKEN") or os.environ.get(
    "AILIANCE_ADMIN_TOKEN"
)


# Shared async client. Reused across calls to keep connection pooling.
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(base_url=_GATEWAY_URL.rstrip("/"))
    return _client


def _auth_headers() -> dict[str, str]:
    if not _ADMIN_TOKEN:
        raise HTTPException(
            status_code=503,
            detail=(
                "COCKPIT_AILIANCE_ADMIN_TOKEN is not configured — the cockpit-api "
                "cannot proxy admin training campaign requests without it."
            ),
        )
    return {"X-Admin-Token": _ADMIN_TOKEN}


def _raise_from_upstream(exc: httpx.HTTPStatusError) -> None:
    status = exc.response.status_code
    try:
        body = exc.response.json()
        detail = body.get("detail", body) if isinstance(body, dict) else body
    except Exception:  # noqa: BLE001
        detail = exc.response.text or str(exc)
    log.warning("gateway_admin.upstream_error", status=status, detail=detail)
    raise HTTPException(status_code=status, detail=detail) from exc


async def get_status() -> dict:
    """GET /admin/training/status."""
    client = _get_client()
    try:
        r = await client.get(
            "/admin/training/status", headers=_auth_headers(), timeout=10.0
        )
        r.raise_for_status()
    except httpx.HTTPStatusError as exc:
        _raise_from_upstream(exc)
    except httpx.HTTPError as exc:
        log.warning("gateway_admin.status_failed", error=str(exc))
        raise HTTPException(status_code=502, detail=f"Gateway unreachable: {exc}") from exc
    return r.json()


async def start_campaign(domains: list[str] | None) -> dict:
    """POST /admin/training/start."""
    client = _get_client()
    body: dict = {}
    if domains is not None:
        body["domains"] = domains
    try:
        r = await client.post(
            "/admin/training/start", json=body, headers=_auth_headers(), timeout=5.0
        )
        r.raise_for_status()
    except httpx.HTTPStatusError as exc:
        _raise_from_upstream(exc)
    except httpx.HTTPError as exc:
        log.warning("gateway_admin.start_failed", error=str(exc))
        raise HTTPException(status_code=502, detail=f"Gateway unreachable: {exc}") from exc
    return r.json()


async def abort_campaign() -> dict:
    """POST /admin/training/abort."""
    client = _get_client()
    try:
        r = await client.post(
            "/admin/training/abort", headers=_auth_headers(), timeout=5.0
        )
        r.raise_for_status()
    except httpx.HTTPStatusError as exc:
        _raise_from_upstream(exc)
    except httpx.HTTPError as exc:
        log.warning("gateway_admin.abort_failed", error=str(exc))
        raise HTTPException(status_code=502, detail=f"Gateway unreachable: {exc}") from exc
    return r.json()


async def get_domain_log(domain: str, tail: int) -> str:
    """GET /admin/training/log/{domain}?tail=N."""
    client = _get_client()
    try:
        r = await client.get(
            f"/admin/training/log/{domain}",
            params={"tail": tail},
            headers=_auth_headers(),
            timeout=10.0,
        )
        r.raise_for_status()
    except httpx.HTTPStatusError as exc:
        _raise_from_upstream(exc)
    except httpx.HTTPError as exc:
        log.warning("gateway_admin.log_failed", domain=domain, error=str(exc))
        raise HTTPException(status_code=502, detail=f"Gateway unreachable: {exc}") from exc
    return r.text
