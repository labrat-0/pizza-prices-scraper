"""Actor entrypoint with Apify lifecycle management."""

import logging
import os
from typing import Any

import httpx
from apify import Actor
from playwright.async_api import async_playwright

from .models import ScraperInput
from .scraper import PizzaPriceScraper

logger = logging.getLogger(__name__)

_BATCH_SIZE = 25
_FREE_TIER_LIMIT = 25


async def main() -> None:
    """Main actor function with Apify SDK."""
    async with Actor:
        # Get and parse input
        actor_input = await Actor.get_input() or {}
        config = ScraperInput.from_actor_input(actor_input)

        # Validate input
        validation_error = config.validate_input()
        if validation_error:
            logger.error("Input validation failed: %s", validation_error)
            await Actor.set_status_message(f"Error: {validation_error}")
            await Actor.fail(status_message=validation_error)
            return

        # Enforce free tier limit
        is_at_home = os.getenv("APIFY_IS_AT_HOME", "").lower() in ("1", "true")
        is_paying = os.getenv("APIFY_USER_IS_PAYING", "").lower() in ("1", "true")
        max_results = config.max_results
        if is_at_home and not is_paying:
            max_results = min(max_results, _FREE_TIER_LIMIT)
            logger.info("Free tier: limiting to %d results", max_results)

        # Set initial status
        franchise_list = ", ".join(f.capitalize() for f in config.franchises)
        await Actor.set_status_message(
            f"Scraping {franchise_list} pizza prices for zip {config.zip_code} (max {max_results})..."
        )

        # Open dataset and state
        dataset = await Actor.open_dataset()
        state = await Actor.use_state(default_value={"total_pushed": 0})
        total_pushed: int = state.get("total_pushed", 0)

        batch: list[dict[str, Any]] = []

        # Launch browser and create scraper
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)

            async with httpx.AsyncClient(
                follow_redirects=True,
                limits=httpx.Limits(max_connections=5, max_keepalive_connections=2),
            ) as http_client:
                scraper = PizzaPriceScraper(config, http_client, browser)

                try:
                    async for record in scraper.scrape():
                        if total_pushed >= max_results:
                            logger.info("Reached max results (%d), stopping", max_results)
                            break

                        batch.append(record)

                        if len(batch) >= _BATCH_SIZE:
                            # Guard: don't exceed max_results
                            remaining = max_results - total_pushed
                            flush = batch[:remaining]
                            await dataset.push_data(flush)
                            total_pushed += len(flush)
                            state["total_pushed"] = total_pushed

                            await Actor.set_status_message(
                                f"Scraped {total_pushed} pizza(s) from {franchise_list}..."
                            )
                            logger.info("Pushed batch of %d (total: %d)", len(flush), total_pushed)
                            batch = []

                            if total_pushed >= max_results:
                                break
                finally:
                    await browser.close()

        # Flush remaining
        if batch and total_pushed < max_results:
            remaining = max_results - total_pushed
            flush = batch[:remaining]
            await dataset.push_data(flush)
            total_pushed += len(flush)
            state["total_pushed"] = total_pushed
            logger.info("Flushed final batch of %d", len(flush))

        # Final status
        logger.info("Scraping complete. Total pizzas: %d", total_pushed)
        await Actor.set_status_message(
            f"Done! Scraped {total_pushed} pizza prices from {franchise_list}."
        )
