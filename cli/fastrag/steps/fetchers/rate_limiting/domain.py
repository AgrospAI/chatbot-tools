import asyncio
import time
from dataclasses import dataclass, field
from typing import ClassVar
from urllib.parse import urlparse

from fastrag.steps.fetchers.rate_limiting.rate_limiter import IRateLimiter


@dataclass(frozen=True)
class DomainRateLimiter(IRateLimiter):
    supported: ClassVar[str] = "domain"

    locks: dict[str, asyncio.Lock] = field(default_factory=dict)
    timestamps: dict[str, float] = field(default_factory=dict)

    async def wait(self, url: str):
        domain = urlparse(url).netloc
        if domain not in self.locks:
            self.locks[domain] = asyncio.Lock()
            self.timestamps[domain] = 0.0

        async with self.locks[domain]:
            now = time.monotonic()
            elapsed = now - self.timestamps[domain]
            wait_time = self.delay - elapsed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            self.timestamps[domain] = time.monotonic()
