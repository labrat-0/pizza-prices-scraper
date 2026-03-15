"""Entry point for pizza prices scraper actor."""

import asyncio
import logging
import sys

from apify.log import ActorLogFormatter

from .main import main

# Configure logging with Apify formatter
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(ActorLogFormatter())

root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

# Run the actor
asyncio.run(main())
