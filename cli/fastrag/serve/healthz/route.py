from fastapi import APIRouter, Response

HealthRouter = APIRouter()


@HealthRouter.get("/healthz")
async def healthz() -> Response:
    return Response(content="ok", media_type="text/plain")
