from bs4 import BeautifulSoup
from typing import Optional


def extract_footer_text(html: str) -> Optional[str]:
    """Extract text from the <footer> tag."""
    soup = BeautifulSoup(html, "html.parser")
    footer = soup.find("footer")
    if footer:
        return footer.get_text(separator=" ", strip=True)
    return None
