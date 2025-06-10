from src.utils.html import extract_footer_text


def test_extract_footer_text():
    html = """
    <html><body><footer>Example Footer Text</footer></body></html>
    """
    assert extract_footer_text(html) == "Example Footer Text"
