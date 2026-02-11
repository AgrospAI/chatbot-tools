from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from fastrag.serve.telemetry.metrics import rejected_requests_total

limiter = Limiter(key_func=get_remote_address)


async def custom_rate_limit_handler(request, exc):
    if request.url.path.startswith("/ask"):
        rejected_requests_total.add(1, {"reason": "rate_limit_ask"})
    else:
        rejected_requests_total.add(1, {"reason": "rate_limit_other"})

    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded."},
    )
