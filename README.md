# Pizza Prices Scraper

Scrape real-time pizza menu prices from major US franchises: Domino's, Pizza Hut, Papa John's, and Little Caesars.

## Features
- **Multi-franchise support** — Scrape multiple franchises in one run
- **Location-based pricing** — Input any US zip code
- **Configurable output** — Control batch size and result limits
- **Free tier compatible** — Limited to 25 results for free users
- **Async processing** — Fast, concurrent page rendering with Playwright

## Input
```json
{
  "franchises": ["dominos", "pizzahut"],
  "zipCode": "10001",
  "maxResults": 100,
  "requestIntervalSecs": 2.0,
  "timeoutSecs": 30
}
```

### Parameters
- **franchises** (required): List of franchise codes
  - Valid: `dominos`, `pizzahut`, `papajohns`, `littlecaesars`
- **zipCode**: US postal code (5 digits, default: 10001)
- **maxResults**: Max items to return, 1-200 (default: 100)
- **requestIntervalSecs**: Seconds between requests (default: 2.0)
- **timeoutSecs**: Page load timeout in seconds (default: 30)

## Output
```json
{
  "franchise": "dominos",
  "franchise_display": "Domino's",
  "pizza_name": "Pepperoni Medium",
  "size": "Medium",
  "price": 12.99,
  "currency": "USD",
  "category": "Standard",
  "description": "Pepperoni pizza in medium size",
  "menu_url": "https://www.dominos.com/en/pages/order/",
  "zip_code": "10001",
  "scraped_at": "2026-03-15T10:30:45.123456Z"
}
```

## Usage

### On Apify Platform
1. Open this actor on Apify
2. Set input parameters (see above)
3. Run the actor
4. Download results from dataset

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set fake Apify token
export APIFY_TOKEN="fake-token"

# Create input file
mkdir -p storage/datasets
cat > storage/actor_input.json << 'EOF'
{
  "franchises": ["dominos"],
  "zipCode": "10001",
  "maxResults": 50
}
EOF

# Run locally
python -m src

# Check output
cat storage/datasets/default/*.jsonl
```

## Technical Details
- **Language:** Python 3.12
- **Browser:** Playwright (Chromium headless)
- **HTML Parsing:** BeautifulSoup4
- **Framework:** Apify SDK v2
- **Models:** Pydantic v2

## Limits
- **Free tier:** Maximum 25 results per run
- **Paid tier:** Up to 200 results per run
- **Request interval:** 0.5s minimum, 30s maximum
- **Timeout:** 5-120 seconds per page

## Known Limitations
This is a **test actor** demonstrating Apify patterns. Current implementation:
- Uses simplified extraction heuristics
- May not capture all menu items
- Requires franchise URL hardcoding
- Location-based pricing may be limited

For production use, implement site-specific CSS selectors and interaction flows.

## Support
For issues or questions, check the `.arc/` directory (local documentation):
- `.arc/purpose.md` — What this does
- `.arc/architecture.md` — How it's built
- `.arc/instructions.md` — Development guide
- `.arc/memory.md` — Learned patterns
- `.arc/errors.md` — Known issues
- `.arc/security.md` — Security policy

## License
MIT
