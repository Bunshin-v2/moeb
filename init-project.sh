#!/bin/bash

# Create project structure
mkdir -p src/{scrapers,analyzers,utils}
mkdir -p config data/{raw,processed} tests logs

# Create essential files
touch src/__init__.py tests/__init__.py .env .gitignore

# Create configuration templates
echo "OPENAI_API_KEY=your-key-here" > .env.template
echo "# Add your API keys here" >> .env.template

echo "✅ Project structure created"
