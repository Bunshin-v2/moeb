#!/bin/bash

echo "🚀 Setting up OpenAI Codex tool environment..."

# Run setup scripts in order
./setup.sh
./setup-dev.sh
./setup-financial.sh
./init-project.sh

echo "✅ Complete setup finished!"
echo "Next steps:"
echo "1. Add your OpenAI API key to .env"
echo "2. Create your AGENTS.md file"
echo "3. Run 'python -c \"import openai; print('Ready to code!')\"'"
