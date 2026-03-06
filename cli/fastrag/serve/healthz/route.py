from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/healthz")
async def healthz() -> Response:
    return Response(content="ok", media_type="text/plain")
