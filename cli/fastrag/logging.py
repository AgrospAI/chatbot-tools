import logging


def configure_logging(level: str | int = logging.INFO) -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=level,
    )


configure_logging()

logger = logging.getLogger(__name__)


logging.getLogger("httpx").setLevel("WARN")
