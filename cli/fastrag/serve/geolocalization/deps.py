from fastapi.requests import Request
from pydantic import BaseModel


class ClientInfo(BaseModel):
    ip: str
    country: str | None


def get_client_info(request: Request) -> ClientInfo:
    return ClientInfo(
        ip=request.state.ip,
        country=request.state.country,
    )
