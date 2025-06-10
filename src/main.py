import sys
from pathlib import Path
from urllib.parse import urlparse
import argparse
import asyncio
from typing import List, Optional

# Ensure project root is on the path when executed as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from config.loader import load_env
from src.scrapers.fetcher import fetch_html
from src.utils.html import extract_footer_text

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

def _domain_to_filename(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.replace(".", "_") + ".txt"


def write_footer(domain: str, footer: Optional[str], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / _domain_to_filename(domain)
    content = footer if footer else "Footer not found."
    file_path.write_text(content)
    print(f"Saved footer for {domain} to {file_path}")


async def process_domain(domain: str, output_dir: Path) -> None:
    html = await fetch_html(domain)
    footer = extract_footer_text(html) if html else None
    write_footer(domain, footer, output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch footers from broker sites")
    parser.add_argument(
        "--urls",
        nargs="*",
        help="Optional list of URLs to scrape. Defaults to built-in list.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "data" / "footers"),
        help="Directory to store footer text files.",
    )
    return parser.parse_args()


async def main() -> None:
    load_env()
    args = parse_args()
    urls = args.urls if args.urls else BROKER_URLS
    output_dir = Path(args.output_dir)
    await asyncio.gather(*(process_domain(url, output_dir) for url in urls))


if __name__ == "__main__":
    asyncio.run(main())
