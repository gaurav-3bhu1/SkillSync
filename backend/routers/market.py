from fastapi import APIRouter, Query

from backend.schemas.market import MarketSummary
from backend.services.data_service import (
    get_market_summary,
)


router = APIRouter(
    prefix="/api/market",
    tags=["Market Intelligence"],
)


@router.get(
    "/summary",
    response_model=MarketSummary,
)
def market_summary(
    district: str | None = Query(
        default=None
    ),
    sector: str | None = Query(
        default=None
    ),
):
    return get_market_summary(
        district=district,
        sector=sector,
    )