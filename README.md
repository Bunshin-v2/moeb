# NEEX Legal Contract Review System

🏛️ **AI-powered legal contract analysis implementing the comprehensive NEEX blueprint methodology**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🎯 Overview

NEEX Legal Contract Review is a sophisticated AI-powered system that performs **clause-by-clause contract analysis** following a structured 3-layered methodology:

- **Interpretation** → What does this clause technically enable or control?
- **Exposure** → Where might your organization be vulnerable?  
- **Opportunity** → What leverage, negotiation hooks, or remedies exist?

The system implements the official **NEEX Legal Contract Review Blueprint** for Service & Deliverables Contracts, providing comprehensive risk assessment, negotiation recommendations, and compliance verification.

## ✨ Key Features

### 📋 Comprehensive Analysis
- **10-Tag Clause Classification**: TEC/LEG/FIN/COM/IPX/TRM/DIS/DOC/EXE/EXT
- **3-Tier Risk Scoring**: Critical/Material/Procedural with quantitative scoring
- **6-Category Risk Assessment**: Financial, Legal, Operational, Compliance, Reputational, Strategic
- **Negotiation Recommendations**: Rule-based system with actionable advice

### 📄 Multi-Format Support
- **Document Input**: PDF, DOCX, TXT with robust parsing
- **Report Output**: HTML, PDF, Markdown, JSON with professional templates
- **CLI Interface**: Rich console with progress indicators and formatted output

### 🔄 NEEX Blueprint Compliance
- **Pause Checkpoints**: Every 3 clauses OR 3000 tokens for human oversight
- **Sequential Analysis**: No clause skipping permitted per methodology
- **Comprehensive Logging**: Detailed audit trail of analysis decisions

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd neex-legal-review
```

2. **Install the system**
```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"

# Download required spaCy language model
python -m spacy download en_core_web_sm
```

3. **Set up environment (optional)**
```bash
# Copy environment template
cp .env.sample .env

# Edit .env with your API keys (optional for basic functionality)
# OPENAI_API_KEY=your-key-here
# GOOGLE_API_KEY=your-key-here
```

### Basic Usage

```bash
# Analyze a contract
neex-review analyze contract.pdf --output ./reports --format html

# Extract contract structure only
neex-review extract contract.pdf --clauses-only

# Show available clause tags and risk levels
neex-review info --clause-tags --risk-levels

# Validate configuration
neex-review validate-config src/config/blueprint.yaml
```

## 📊 Example Output

```
NEEX Legal Review System v1.0.0
================================

✓ Document parsed: 45 clauses identified
✓ Analysis Complete!

Analysis Summary:
• Critical Issues: 3
• Material Issues: 8  
• Procedural Issues: 12
• Negotiation Opportunities: 15
• Clauses Analyzed: 45

Reports generated:
📄 reports/detailed_analysis.html
📄 reports/negotiation_checklist.md
📄 reports/risk_summary.json
```

## 🏗️ Architecture

The system implements a **pipeline pattern** with sequential processing stages:

```
Contract File → Parser → NLP Processor → Clause Analyzer → Risk Assessor → Negotiation Advisor → Report Generator
```

### Core Components

- **ReviewOrchestrator** - Central pipeline coordinator with pause checkpoints
- **ContractParser** - Multi-format document processing (PDF/DOCX/TXT)
- **LegalNLPProcessor** - AI-powered text analysis and entity extraction
- **ClauseAnalyzer** - 3-layered analysis engine with tag classification
- **RiskAssessor** - Quantitative risk scoring across 6 categories
- **NegotiationAdvisor** - Rule-based recommendation engine
- **ReportGenerator** - Template-driven multi-format output

## ⚙️ Configuration

The system is driven by YAML configuration files in `src/config/`:

- **blueprint.yaml** - Core NEEX methodology configuration
- **clause_definitions.yaml** - Clause patterns and risk factors  
- **review_templates.yaml** - Report formatting templates

### Customization

```yaml
# Example: Custom negotiation rule
negotiation_rules:
  - name: "High Penalty Risk"
    conditions:
      tags: ["FIN"]
      content_contains: ["penalty"]
      content_lacks: ["cap", "limit"]
    recommendation:
      type: "redline"
      priority: "High"
      suggested_change: "Add penalty caps to limit financial exposure"
```

## 🧪 Development

### Code Quality
```bash
# Format code
black .

# Type checking
mypy --strict src/

# Linting  
flake8 src/ tests/

# Run all quality checks
pre-commit run --all-files
```

### Testing
```bash
# Run all tests
pytest --cov=src --cov-report=term-missing

# Run specific test
pytest tests/test_contract_parser.py -v

# Run without slow tests
pytest -m "not slow"
```

### Docker Development
```bash
# Build image
docker build -t neex/legal-review .

# Run analysis
docker run --rm -v $(pwd)/contracts:/data neex/legal-review analyze /data/contract.pdf
```

## 📁 Project Structure

```
neex-legal-review/
├── src/
│   ├── cli/                    # Command-line interface
│   ├── config/                 # YAML configuration files
│   ├── core/                   # Core analysis components
│   └── ai/                     # AI/ML processing modules
├── tests/                      # Test suite (to be implemented)
├── docs/                       # Documentation
├── templates/                  # Report templates
├── .github/workflows/          # CI/CD pipeline
├── Dockerfile                  # Container configuration
├── pyproject.toml             # Project configuration
├── CLAUDE.md                  # Developer guidance
└── PROJECT_STATUS.md          # Implementation status
```

## 🔒 Security & Privacy

- **Local Processing**: All analysis performed locally, no data sent to external services
- **API Keys Optional**: Basic functionality works without external API keys
- **Secure Defaults**: Docker runs as non-root user, minimal attack surface
- **Vulnerability Scanning**: Automated security scanning in CI/CD pipeline

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Developer guidance for Claude Code
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Detailed implementation status
- **[Blueprint Document](NEEX%20LEGAL%20CONTRACT%20REVIEW%20EXECUTION%20BLUEPRINT%20(Service%20&%20Deliverables%20Contract)%20(1).docx)** - Original NEEX methodology

## 🤝 Contributing

This project follows the NEEX Legal Contract Review Blueprint methodology. Key principles:

- **Sequential Analysis**: All clauses must be processed in order
- **No Skipping**: Every clause receives full 3-layered analysis
- **Pause Compliance**: Mandatory checkpoints every 3 clauses/3000 tokens
- **Comprehensive Coverage**: All 10 clause tags must be supported

## ⚖️ Legal Notice

This software is designed to assist in contract review but does not constitute legal advice. Always consult qualified legal counsel for important contract decisions.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Comprehensive guides in `/docs` directory  
- **Development**: See `CLAUDE.md` for development guidance

---

**Built with ❤️ for legal professionals by the NEEX Legal AI Team**