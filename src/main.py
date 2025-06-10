# src/main.py
import asyncio
import os
from typing import List

import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ← list your brokers here
BROKER_URLS: List[str] = [
    "https://www.atfx.com",
    "https://www.cfiglobal.com",
    "https://www.startrader.com",
    "https://www.exness.com",
    "https://www.pepperstone.com",
    "https://www.fpmarkets.com",
    "https://www.eightcap.com",
    "https://www.equiti.com",
    "https://www.xs.com",
    "https://www.axiory.com",
    "https://www.blackbullmarkets.com",
    "https://www.fxpesa.com",
    "https://www.cmtrading.com",
    "https://www.fxprimus.com",
    "https://www.tickmill.com",
    "https://www.hantecmarkets.com",
    "https://www.vtmarkets.com",
    "https://www.acysecurities.com",
    "https://www.gomarkets.com",
    "https://www.legacyfx.com",
]


async def fetch_footer(session: aiohttp.ClientSession, url: str):
    try:
        async with session.get(url, timeout=10) as resp:
            text = await resp.text()
            soup = BeautifulSoup(text, "html.parser")
            footer = soup.find("footer")
            return url, footer.get_text(" ", strip=True) if footer else None
    except Exception:
        return url, None

async def main():
    load_dotenv()  # pulls your SCRAPERAPI_KEY, etc.
    headers = {}
    # If you need to route through ScraperAPI/SerpAPI/BrightData proxy,
    # you'd build your URL or headers here using os.getenv("SCRAPERAPI_KEY"), etc.

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [fetch_footer(session, url) for url in BROKER_URLS]
        for url, footer in await asyncio.gather(*tasks):
            if footer:
                print(f"{url} → {footer}")
            else:
                print(f"footer not found or could not be fetched: {url}")

if __name__ == "__main__":
    asyncio.run(main())
