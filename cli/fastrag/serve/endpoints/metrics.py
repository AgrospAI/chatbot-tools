import os

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

router = APIRouter()
security = HTTPBearer()
METRICS_TOKEN = os.environ.get("METRICS_BEARER_TOKEN", "")


def verify_metrics_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    if not METRICS_TOKEN:
        return True
    if credentials.credentials != METRICS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return True


@router.get("/metrics")
async def metrics(authorized: bool = Depends(verify_metrics_token)) -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
