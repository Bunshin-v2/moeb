import os
from tempfile import NamedTemporaryFile
from config.loader import load_env


def test_load_env():
    with NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.write("TEST_KEY=value\n")
        temp_path = tmp.name
    try:
        variables = load_env(temp_path)
        assert variables["TEST_KEY"] == "value"
        assert os.environ.get("TEST_KEY") == "value"
    finally:
        os.remove(temp_path)
        os.environ.pop("TEST_KEY", None)
