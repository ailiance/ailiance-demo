"""Admin datasets gallery endpoints."""
from fastapi import APIRouter, Depends, HTTPException

from ailiance_demo.auth.tailscale import require_tailscale_user
from ailiance_demo.deps import get_datasets_service
from ailiance_demo.models import DatasetDetail, DatasetSummary
from ailiance_demo.services.datasets import DatasetsService

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
    dependencies=[Depends(require_tailscale_user)],
)


@router.get("/datasets", response_model=list[DatasetSummary])
def list_datasets(
    svc: DatasetsService = Depends(get_datasets_service),
) -> list[DatasetSummary]:
    return svc.list()


@router.get("/datasets/{domain}", response_model=DatasetDetail)
def get_dataset(
    domain: str,
    svc: DatasetsService = Depends(get_datasets_service),
) -> DatasetDetail:
    detail = svc.get(domain)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Dataset {domain} not found")
    return detail
