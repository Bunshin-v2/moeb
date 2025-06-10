from typing import Optional
import whois


def get_whois(domain: str) -> Optional[dict]:
    """Run a WHOIS lookup and return the result as a dictionary."""
    try:
        result = whois.whois(domain)
    except Exception:
        return None
    if isinstance(result, dict):
        return result
    if hasattr(result, "__dict__"):
        return result.__dict__
    return None
