import asyncio
from dataclasses import InitVar, dataclass, field
from typing import AsyncGenerator, ClassVar, override
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup
from httpx import AsyncClient

from fastrag.events import Event
from fastrag.helpers.url_field import URLField
from fastrag.helpers.utils import normalize_url
from fastrag.plugins import PluginRegistry, plugin
from fastrag.steps.fetchers.events import FetchingEvent
from fastrag.steps.fetchers.rate_limiting.rate_limiter import RateLimiter
from fastrag.steps.task import Task
from fastrag.systems import System


def is_same_domain(url_a: str, url_b: str) -> bool:
    return urlparse(url_a).netloc == urlparse(url_b).netloc


@dataclass(frozen=True)
@plugin(system=System.FETCHING, supported="Crawling")
class CrawlerFetcher(Task):
    url: URLField = URLField()
    depth: int = field(default=5)
    workers: int = field(default=5)
    delay: InitVar[float] = field(default=0.1)

    _visited: set[str] = field(init=False, compare=False, default_factory=set)
    _cached: int = field(init=False, compare=False, default=0)
    _rate_limiter: RateLimiter | None = field(compare=False, default=None)

    UserAgent: ClassVar[str] = "CrawlerFetcher/1.0"

    def __post_init__(self, delay: float) -> None:
        object.__setattr__(
            self,
            "_rate_limiter",
            PluginRegistry.get_instance(System.RATE_LIMITING, "domain", delay=delay),
        )

    @override
    async def callback(self) -> AsyncGenerator[Event, None]:
        self._visited.clear()

        queue: asyncio.Queue[tuple[str, int]] = asyncio.Queue()
        event_queue: asyncio.Queue[Event] = asyncio.Queue()
        await queue.put((normalize_url(self.url), 0))

        async with AsyncClient(
            timeout=5,
            follow_redirects=True,
            headers={"User-Agent": CrawlerFetcher.UserAgent},
            cookies={},
        ) as client:

            async def get_robot_parser():
                rp = RobotFileParser()
                robots_url = urljoin(self.url, "/robots.txt")
                try:
                    res = await client.get(robots_url)
                    if res.status_code == 200:
                        rp.parse(res.text.splitlines())
                    else:
                        rp.parse([])
                except Exception:
                    rp.parse([])
                rp.user_agent = CrawlerFetcher.UserAgent
                return rp

            rp = await get_robot_parser()

            async def parse_and_enqueue(
                *,
                html: str,
                base_url: str,
                depth: int,
            ):
                soup = BeautifulSoup(html, "html.parser")

                for a in soup.find_all("a", href=True):
                    next_url = urljoin(base_url, a["href"])
                    parsed = urlparse(next_url)

                    if parsed.scheme not in ("http", "https"):
                        continue

                    next_url = normalize_url(next_url)
                    if is_same_domain(base_url, next_url):
                        await queue.put((next_url, depth + 1))

            async def worker():
                while True:
                    try:
                        url, depth = await queue.get()
                    except asyncio.CancelledError:
                        return

                    try:  # Safety measure
                        if depth > self.depth or url in self._visited:
                            continue

                        self._visited.add(url)
                        if not rp.can_fetch(CrawlerFetcher.UserAgent, url):
                            await event_queue.put(
                                FetchingEvent.Type.EXCEPTION,
                                f"Blocked by robots.txt: {url}",
                            )
                            continue

                        if self.cache.is_present(url):
                            object.__setattr__(self, "_cached", self._cached + 1)

                            cached = await self.cache.get(url)
                            html = cached.content.decode()

                            await event_queue.put(
                                FetchingEvent(
                                    FetchingEvent.Type.PROGRESS,
                                    f"Parsing cached {url}",
                                )
                            )
                        else:
                            await event_queue.put(
                                FetchingEvent(
                                    FetchingEvent.Type.PROGRESS,
                                    f"Fetching {url}",
                                )
                            )

                            await self._rate_limiter.wait(url)
                            res = await client.get(url)
                            res.raise_for_status()

                            content_type = res.headers.get("Content-Type", "")
                            if "text/html" not in content_type:
                                await event_queue.put(
                                    FetchingEvent(
                                        FetchingEvent.Type.EXCEPTION,
                                        f"Unsupported content type: ({url}) {content_type}",
                                    )
                                )
                                return

                            html = res.text

                            await self.cache.create(
                                url,
                                html.encode(),
                                "fetching",
                                {
                                    "format": "html",
                                    "strategy": CrawlerFetcher.supported,
                                    "depth": depth,
                                },
                            )
                        await parse_and_enqueue(html=html, base_url=url, depth=depth)
                    except Exception as e:
                        await event_queue.put(
                            FetchingEvent(FetchingEvent.Type.EXCEPTION, f"{url}: {e}")
                        )
                    finally:
                        queue.task_done()

            workers = [asyncio.create_task(worker()) for _ in range(self.workers)]

            # Task that completes when crawling is finished
            crawl_done = asyncio.create_task(queue.join())

            # Drain events until crawl is done
            while not crawl_done.done() or not event_queue.empty():
                try:
                    event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                    yield event
                    event_queue.task_done()
                except asyncio.TimeoutError:
                    continue

            for w in workers:
                w.cancel()

    @override
    def completed_callback(self) -> Event:
        return FetchingEvent(
            FetchingEvent.Type.COMPLETED,
            (
                f"From {self.url}, crawled {len(self._visited)} sites "
                f"({self._cached} cached) with CrawlerFetcher"
            ),
        )
