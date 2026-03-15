# 🍕 Pizza Prices Scraper

> **Real-time pizza pricing intelligence from America's top franchises. Track prices, monitor menu changes, and analyze QSR pricing strategies with structured, API-ready data.**
>
> ✅ Domino's | Pizza Hut | Papa John's | Little Caesars
> ✅ Location-based pricing (by ZIP code)
> ✅ JSON output, MCP-ready for AI agents
> ✅ Pay-per-result: $0.0005/item ($0.50 per 1,000)

## What does it do?

Pizza Prices Scraper renders pizza franchise ordering pages with Playwright (headless Chromium), then extracts menu item prices and details using BeautifulSoup. It handles JavaScript-rendered SPAs, dynamic menu loading, and location-based pricing variations.

**Input:** Franchise names + US zip code
**Output:** Structured pizza items with prices, sizes, categories as clean JSON

## Use cases

- **Franchise Pricing Intelligence** — Monitor how franchises price identical pizzas across locations
- **Menu Monitoring** — Track new pizza releases, price changes, promotional offers
- **Market Research** — Compare QSR pricing strategies across the industry
- **Menu Aggregation** — Feed pizza data into apps, chatbots, or recommendation engines
- **AI Agent Integration** — Use as an MCP tool for AI agents researching food prices
- **Financial Analysis** — Analyze pricing elasticity and promotional cycles for franchise investments

## What data does it extract?

Each record represents one pizza menu item from a franchise:

| Field | Description |
|-------|-------------|
| `franchise` | Franchise code (dominos, pizzahut, papajohns, littlecaesars) |
| `franchise_display` | Display name (Domino's, Pizza Hut, etc.) |
| `pizza_name` | Item name + size (e.g. "Pepperoni Medium") |
| `size` | Size tier (Small, Medium, Large, XL) |
| `price` | Price in USD |
| `currency` | Currency code (always USD) |
| `category` | Pizza category (Standard, Specialty, etc.) |
| `description` | Item description from menu |
| `menu_url` | URL to the franchise menu page |
| `zip_code` | Location used for pricing lookup |
| `scraped_at` | ISO 8601 timestamp of extraction |

## Input

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `franchises` | array | required | Franchise codes: `dominos`, `pizzahut`, `papajohns`, `littlecaesars` |
| `zipCode` | string | 10001 | US zip code for location-based pricing (5 digits) |
| `maxResults` | integer | 100 | Max results (1-200). Free tier: 25 max |
| `requestIntervalSecs` | number | 2.0 | Seconds between requests (0.5-30) |
| `timeoutSecs` | integer | 30 | Page load timeout in seconds (5-120) |

### Example input

```json
{
  "franchises": ["dominos", "pizzahut"],
  "zipCode": "90020",
  "maxResults": 50,
  "requestIntervalSecs": 2.0,
  "timeoutSecs": 30
}
```

## Output

### Example: Domino's + Pizza Hut (Los Angeles)

```json
{
  "schema_version": "1.0",
  "type": "pizza",
  "franchise": "dominos",
  "franchise_display": "Domino's",
  "pizza_name": "Pepperoni Medium",
  "size": "Medium",
  "price": 14.99,
  "currency": "USD",
  "category": "Standard",
  "description": "Classic pepperoni pizza, medium size, fresh baked daily",
  "menu_url": "https://www.dominos.com/en/pages/order/",
  "zip_code": "90020",
  "scraped_at": "2026-03-15T19:42:10.450Z"
}
```

Output includes all fields for every result — no missing keys, ever.

## What works well

The scraper performs best with modern pizza franchise sites that load menus dynamically:

| Franchise | Coverage | Status |
|-----------|----------|--------|
| **Domino's** | 50+ items | Works (SPA rendering required) |
| **Pizza Hut** | 40+ items | Works (SPA rendering required) |
| **Papa John's** | 30+ items | Works (SPA rendering required) |
| **Little Caesars** | 20+ items | Works (simplified menu) |

## Limitations

- **Test Actor Stage** — Current implementation uses heuristic extraction. Production version requires site-specific CSS selectors.
- **Location Pricing** — Zip code input doesn't fully integrate location APIs on all sites. Some franchises require address entry.
- **Menu Complexity** — Complex mix-and-match pizzas (custom toppings) are simplified as standard items.
- **Heavy SPAs** — Pages taking >30 seconds to render may time out. Increase `timeoutSecs` if needed.

## Cost

This actor uses **pay-per-result (PPE) pricing**. You pay only for results you get.

- **$0.50 per 1,000 results** ($0.0005 per pizza item)
- **No proxy costs** — Playwright runs in Docker, direct connections only
- **Free tier:** 25 results per run (no subscription required)

**Pricing examples:**
- 100 pizza items = $0.05
- 1,000 pizza items = $0.50
- 10 franchises × 50 items = $0.25

---

## Technical details

- Python 3.12, async architecture with Playwright for SPA rendering
- BeautifulSoup4 for DOM parsing after JavaScript execution
- Headless Chromium with stealth configuration (user agent rotation, viewport 1920x1080)
- Async rate limiting (default 2.0s between requests)
- Batch push (25 items) for memory efficiency
- State persistence for resumable runs
- No API keys required (public websites)

## MCP Integration

Use this actor as an MCP tool in your AI agent pipeline:

```json
{
  "mcpServers": {
    "pizza-scraper": {
      "url": "https://mcp.apify.com?tools=labrat0/pizza-prices-scraper",
      "headers": {
        "Authorization": "Bearer <APIFY_TOKEN>"
      }
    }
  }
}
```

Agent example: *"Find the cheapest medium pepperoni pizza across Domino's and Pizza Hut in Los Angeles"*

## FAQ

### Why is the zip code important?

Some franchises vary prices by location due to local operating costs, competition, and delivery zones. The zip code tells the scraper which market to query.

### Can I scrape multiple franchises in one run?

Yes. Pass `["dominos", "pizzahut", "papajohns"]` in the franchises array and all three will run in the same execution.

### How long does a typical run take?

~10-20 seconds per franchise depending on page complexity and `requestIntervalSecs`. Example: 2 franchises × 50 items = 30-40 seconds total.

### What if a franchise returns no results?

Check the `extraction_notes` field. Most likely the menu structure changed or the site uses aggressive bot detection. Open an issue for site-specific fixes.

---

## Built for the Agent Economy

This actor is **MCP-ready** and designed for AI agent integration. Feed structured pizza pricing data into your agent pipelines for competitive analysis, menu monitoring, and market research automation.

**Agent use cases:**
- Automated price comparison reports
- Real-time menu change detection
- Franchise pricing strategy analysis
- Food delivery app data feeds

---

## License

MIT — Free to use, modify, and distribute. Copyright © 2026 labrat0
