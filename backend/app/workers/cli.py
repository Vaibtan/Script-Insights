from __future__ import annotations

import argparse
import logging
from time import sleep

from app.core.container import build_container
from app.core.logging import configure_logging
from app.core.settings import get_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Process queued script analysis runs.")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Drain currently queued runs once and exit.",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=1.0,
        help="Seconds to sleep between polls when not running with --once.",
    )
    args = parser.parse_args()

    configure_logging()
    logger = logging.getLogger("app.workers")
    settings = get_settings()
    container = build_container(settings=settings)

    while True:
        processed = container.run_queue_processor.drain()
        logger.info("worker_drain_completed", extra={"processed": processed})
        if args.once:
            return
        sleep(max(args.poll_interval, 0.1))


if __name__ == "__main__":
    main()
