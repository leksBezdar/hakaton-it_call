from dataclasses import dataclass

from fastapi import APIRouter, status


healthcheck_router = APIRouter()


@dataclass(frozen=True)
class OKStatus:
    status: str = "OK"


OK_STATUS = OKStatus()


@healthcheck_router.get("/", status_code=status.HTTP_200_OK)
async def get_status() -> OKStatus:
    return OK_STATUS
