#!/bin/bash

# Development and testing tools
pip install pytest black flake8
pip install selenium selenium-wire undetected-chromedriver
pip install requests-html aiofiles

# Enhanced browser support
playwright install firefox webkit

echo "✅ Development environment ready"