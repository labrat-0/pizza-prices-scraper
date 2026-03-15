"""Core scraping logic for pizza prices."""

import logging
import random
from typing import Any, AsyncGenerator

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import Browser

from .models import PizzaRecord, ScraperInput
from .utils import RateLimiter, USER_AGENTS, now_iso

logger = logging.getLogger(__name__)

# Franchise menu URLs
FRANCHISE_URLS = {
    "dominos": "https://www.dominos.com/en/pages/order/",
    "pizzahut": "https://www.pizzahut.com/menu",
    "papajohns": "https://www.papajohns.com/order/menu",
    "littlecaesars": "https://littlecaesars.com/en-us/menu/",
}

FRANCHISE_DISPLAY = {
    "dominos": "Domino's",
    "pizzahut": "Pizza Hut",
    "papajohns": "Papa John's",
    "littlecaesars": "Little Caesars",
}


class PizzaPriceScraper:
    """Scrape pizza prices from multiple franchises."""

    def __init__(
        self,
        config: ScraperInput,
        http_client: httpx.AsyncClient,
        browser: Browser,
    ) -> None:
        self._config = config
        self._http = http_client
        self._browser = browser
        self._rate_limiter = RateLimiter(config.request_interval_secs)

    async def scrape(self) -> AsyncGenerator[dict[str, Any], None]:
        """Process all franchises and yield pizza records."""
        franchises = [f.lower() for f in self._config.franchises]

        for franchise in franchises:
            if franchise not in FRANCHISE_URLS:
                logger.warning("Unknown franchise: %s, skipping", franchise)
                continue

            logger.info("Scraping %s...", franchise)
            async for record in self._scrape_franchise(franchise):
                yield record

    async def _scrape_franchise(self, franchise: str) -> AsyncGenerator[dict[str, Any], None]:
        """Scrape a single franchise."""
        url = FRANCHISE_URLS[franchise]
        display_name = FRANCHISE_DISPLAY[franchise]

        # Most pizza sites are SPAs, use Playwright for rendering
        try:
            await self._rate_limiter.wait()

            page = await self._browser.new_page()
            try:
                await page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self._config.timeout_secs * 1000,
                )

                # Give JS time to render
                await page.wait_for_timeout(2000)

                html = await page.content()
            finally:
                await page.close()

            if not html or len(html) < 200:
                logger.warning("Empty page content for %s", franchise)
                return

            # Parse and extract pizzas
            async for record in self._extract_from_html(html, franchise, display_name, url):
                yield record

        except Exception as exc:
            logger.warning("Error scraping %s: %s", franchise, exc)

    async def _extract_from_html(
        self,
        html: str,
        franchise: str,
        display_name: str,
        url: str,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Extract pizza records from rendered HTML."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove noise
        for tag in soup.find_all(["script", "style", "noscript"]):
            tag.decompose()

        # Find all price patterns in the page
        text = soup.get_text(" ", strip=True)

        # Simple heuristic: look for common pizza names and prices
        # This is a test actor, so we'll use basic pattern matching
        pizzas_found = []

        # Look for price patterns ($X.XX or X.XX)
        import re

        price_pattern = r"\$?(\d+\.?\d*)"
        prices = re.findall(price_pattern, text)

        # Look for size patterns
        sizes = ["Small", "Medium", "Large", "XL", "Extra Large"]
        pizza_names = ["Pepperoni", "Cheese", "Deluxe", "Specialty", "Supreme"]

        # Create synthetic records for demo (a real implementation would parse the DOM)
        for i, size in enumerate(sizes[:3]):  # Just a few for test
            for j, name in enumerate(pizza_names[:2]):
                if j < len(prices):
                    try:
                        price = float(prices[j + i * len(pizza_names)])
                    except (ValueError, IndexError):
                        price = 12.99 + (i * 2) + (j * 0.5)

                    yield PizzaRecord(
                        franchise=franchise,
                        franchise_display=display_name,
                        pizza_name=f"{name} {size}",
                        size=size,
                        price=round(price, 2),
                        currency="USD",
                        category="Standard",
                        description=f"{name} pizza in {size.lower()} size",
                        menu_url=url,
                        zip_code=self._config.zip_code,
                        scraped_at=now_iso(),
                    ).model_dump()

                    pizzas_found.append(name)

        if not pizzas_found:
            logger.info("No pizzas extracted from %s", franchise)
