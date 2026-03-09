from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from fastrag.serve.telemetry.metrics import (
    http_request_errors_total,
    http_requests_in_flight,
    http_requests_total,
    requests_per_ip_total,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.scope["path"]

        http_requests_in_flight.add(
            1,
            {
                "path": path,
            },
        )
        requests_per_ip_total.add(
            1,
            {
                "ip": request.state.ip,
            },
        )  # set by GeoIPMiddleware

        try:
            response = await call_next(request)
            http_requests_total.add(
                1,
                {
                    "method": request.method,
                    "path": path,
                    "status": response.status_code,
                },
            )
            return response
        except Exception as e:
            http_request_errors_total.add(
                1,
                {
                    "path": path,
                    "type": type(e).__name__,
                },
            )
            raise
        finally:
            http_requests_in_flight.add(-1, {"path": path})
