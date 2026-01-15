from slowapi import Limiter
from slowapi.util import get_remote_address

# Create the limiter instance
limiter = Limiter(key_func=get_remote_address)


# Custom rate limit handler (can be imported and used in main.py)
async def custom_rate_limit_handler(request, exc):
    from fastrag.serve.monitoring.metrics import rejected_requests_total

    if request.url.path.startswith("/ask"):
        rejected_requests_total.labels(reason="rate_limit_ask").inc()
    else:
        rejected_requests_total.labels(reason="rate_limit_other").inc()
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded."},
    )
