import aiohttp
from typing import Optional


async def fetch_html(url: str, *, timeout: int = 10) -> Optional[str]:
    """Fetch HTML content from a URL using aiohttp."""
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
        except aiohttp.ClientError:
            return None
    return None
