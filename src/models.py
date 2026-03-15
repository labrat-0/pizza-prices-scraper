"""Pydantic models for pizza prices scraper input and output."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class ScraperInput(BaseModel):
    """Validated scraper configuration from actor input."""

    franchises: list[str] = Field(default_factory=list, description="List of franchises to scrape")
    zip_code: str = Field(default="10001", description="US zip code for location-based pricing")
    max_results: int = Field(default=100, ge=1, le=200, description="Max results per run")
    request_interval_secs: float = Field(default=2.0, ge=0.5, le=30.0, description="Seconds between requests")
    timeout_secs: int = Field(default=30, ge=5, le=120, description="Playwright timeout in seconds")

    @classmethod
    def from_actor_input(cls, raw: dict[str, Any]) -> "ScraperInput":
        """Map camelCase actor input keys to snake_case model fields."""
        return cls(
            franchises=raw.get("franchises", []),
            zip_code=raw.get("zipCode", "10001"),
            max_results=raw.get("maxResults", 100),
            request_interval_secs=raw.get("requestIntervalSecs", 2.0),
            timeout_secs=raw.get("timeoutSecs", 30),
        )

    def validate_input(self) -> Optional[str]:
        """Return error string if invalid, else None."""
        if not self.franchises:
            return "Provide at least one franchise name in 'franchises' field."

        valid_franchises = {"dominos", "pizzahut", "papajohns", "littlecaesars"}
        invalid = set(f.lower() for f in self.franchises) - valid_franchises
        if invalid:
            return f"Invalid franchises: {', '.join(sorted(invalid))}. Valid: {', '.join(sorted(valid_franchises))}"

        # Validate zip code (5 digits)
        if not self.zip_code.isdigit() or len(self.zip_code) != 5:
            return "Zip code must be exactly 5 digits."

        return None


class PizzaRecord(BaseModel):
    """One pizza item from a franchise menu."""

    schema_version: str = "1.0"
    type: str = "pizza"

    # Franchise and location info
    franchise: str = ""
    franchise_display: str = ""
    menu_url: str = ""
    zip_code: str = ""

    # Pizza details
    pizza_name: str = ""
    size: str = ""
    price: float = 0.0
    currency: str = "USD"
    category: str = ""
    description: str = ""

    # Metadata
    scraped_at: str = ""
