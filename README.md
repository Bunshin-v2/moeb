# Moeb Project

This project contains tools for scraping broker websites and analyzing regulatory disclosures.

## Setup

1. Install dependencies (Python 3.10+ recommended):
   ```bash
   pip install -r requirements.txt
   ```
   Or run the setup scripts if available.

2. Create a `.env` file in the project root and add any API keys you wish to use:
   ```env
   SCRAPERAPI_KEY=your-key
   SERPAPI_KEY=your-key
   BRIGHTDATA_KEY=your-key
   ```

3. Load environment variables in your code using `config.load_env()`.

## Running Tests

Execute all tests with:

```bash
python -m pytest tests/
```

The tests verify basic HTML parsing and environment variable loading.

## Fetching Footers

Run the scraper to store each broker's footer text in `data/footers/`:

```bash
python src/main.py
```

You can specify custom URLs and output directory:

```bash
python src/main.py --urls https://example.com --output-dir /tmp/footers
```
