from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from fastrag.serve.geolocalization import get_country_from_ip


class GeoIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.client:
            return await call_next(request)

        ip = request.client.host
        request.state.ip = ip
        request.state.country = get_country_from_ip(ip)
        return await call_next(request)
