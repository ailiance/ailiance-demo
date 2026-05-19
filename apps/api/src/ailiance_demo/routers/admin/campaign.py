"""Cockpit proxy for the gateway's medium35 training campaign endpoints.

The browser hits these via ``/api/admin/training/campaign/*``; this router
forwards each call to ``http://gateway/admin/training/*`` with the
``X-Admin-Token`` header injected server-side so the secret never leaves
the cockpit-api container.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from ailiance_demo.auth.tailscale import require_tailscale_user
from ailiance_demo.services import gateway_admin

router = APIRouter(
    prefix="/api/admin/training/campaign",
    tags=["campaign"],
    dependencies=[Depends(require_tailscale_user)],
)


class StartCampaignBody(BaseModel):
    domains: list[str] | None = None


@router.get("/status")
async def get_status() -> dict:
    return await gateway_admin.get_status()


@router.post("/start", status_code=202)
async def start_campaign(body: StartCampaignBody | None = None) -> dict:
    domains = body.domains if body else None
    return await gateway_admin.start_campaign(domains)


@router.post("/abort")
async def abort_campaign() -> dict:
    return await gateway_admin.abort_campaign()


@router.get("/log/{domain}", response_class=PlainTextResponse)
async def get_domain_log(domain: str, tail: int = 100) -> str:
    tail = max(1, min(tail, 1000))
    return await gateway_admin.get_domain_log(domain, tail)
