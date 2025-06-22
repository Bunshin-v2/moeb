# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NEEX Legal Contract Review is an AI-powered contract analysis system implementing a comprehensive legal blueprint for clause-by-clause review. The system follows a structured 3-layered analysis approach: Interpretation → Exposure → Opportunity, with automatic risk scoring and negotiation recommendations.

## Key Commands

### Development Setup
```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"

# Download required spaCy model
python -m spacy download en_core_web_sm

# Set up pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run all tests with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_contract_parser.py -v

# Run tests with specific markers
pytest -m "not slow" -v

# Run single test method
pytest tests/test_clause_analyzer.py::TestClauseAnalyzer::test_risk_assessment -v
```

### Code Quality
```bash
# Format code
black .

# Type checking (strict mode)
mypy --strict src/

# Lint code
flake8 src/ tests/

# Run all pre-commit hooks
pre-commit run --all-files
```

### CLI Usage
```bash
# Analyze a contract (main command)
neex-review analyze contract.pdf --output ./reports --format html

# Extract contract structure without analysis
neex-review extract contract.pdf --clauses-only

# Validate configuration files
neex-review validate-config src/config/blueprint.yaml

# Show system information
neex-review info --clause-tags --risk-levels
```

## Architecture Overview

### Core Analysis Pipeline
The system implements a pipeline pattern where each contract flows through sequential analysis stages:

1. **ContractParser** (`src/core/contract_parser.py`) - Extracts structured clauses from PDF/DOCX/TXT
2. **LegalNLPProcessor** (`src/ai/legal_nlp.py`) - Performs NLP analysis and key term extraction  
3. **ClauseAnalyzer** (`src/core/clause_analyzer.py`) - 3-layered analysis with NEEX methodology
4. **RiskAssessor** (`src/ai/risk_assessor.py`) - Scores risks across 6 categories (Financial, Legal, Operational, etc.)
5. **ReviewOrchestrator** (`src/core/review_orchestrator.py`) - **[MISSING]** Main pipeline coordinator
6. **NegotiationAdvisor** (`src/ai/negotiation_advisor.py`) - **[MISSING]** Rule-based recommendation engine
7. **ReportGenerator** (`src/core/report_generator.py`) - **[MISSING]** Template-driven output generation

### Configuration System
The system is driven by YAML configuration files in `src/config/`:

- **blueprint.yaml** - Main NEEX methodology configuration with 10-tag clause system (TEC/LEG/FIN/COM/IPX/TRM/DIS/DOC/EXE/EXT)
- **clause_definitions.yaml** - Detailed patterns and risk factors for each clause type
- **review_templates.yaml** - Output templates for reports and analysis formats

### Data Flow
```
Contract File → Parser → Clause Objects → NLP Analysis → Risk Assessment → Negotiation Advice → Reports
```

Each stage uses an `AnalysisContext` object to pass accumulated analysis data through the pipeline.

### Pause Checkpoint System
Critical NEEX requirement: Analysis must pause every 3 clauses OR 3000 tokens to allow human review and continuation decisions. This is implemented in the ReviewOrchestrator's pipeline management.

## Missing Critical Components

The following components are referenced in the codebase but not yet implemented:

1. **ReviewOrchestrator** - Core pipeline manager imported by CLI but missing
2. **NegotiationAdvisor** - Referenced in clause_analyzer.py but not implemented
3. **ReportGenerator** - Expected by CLI for output generation
4. **Test Suite** - Pytest configuration exists but no actual test files

## Development Notes

### NLP Model Management
- Heavy ML dependencies (transformers, torch, spacy) require careful memory management
- Models should be loaded once and cached, not reloaded per contract
- Consider model optimization for production deployment

### Risk Assessment Categories
The system scores risks across 6 categories with specific weighting:
- Financial (1.2x weight) - Payment, liability, currency risks
- Legal (1.1x weight) - Jurisdiction, indemnification, breach
- Operational (0.9x weight) - Timelines, deliverables, dependencies
- Compliance (1.0x weight) - Regulatory, data protection, AML
- Reputational (0.8x weight) - Public disclosure, quality standards  
- Strategic (1.0x weight) - IP transfer, exclusivity arrangements

### Environment Variables
Use `.env.sample` as template for local development. Required keys:
- `OPENAI_API_KEY` / `GOOGLE_API_KEY` / `ANTHROPIC_API_KEY` for AI services
- `NEEX_DEBUG`, `NEEX_LOG_LEVEL`, `NEEX_OUTPUT_DIR` for configuration

### Docker Deployment
Multi-stage Dockerfile optimized for production with non-root user and health checks. Build with:
```bash
docker build -t neex/legal-review .
docker run --rm -v $(pwd)/contracts:/data neex/legal-review analyze /data/contract.pdf
```

## Blueprint Compliance
The system implements the official NEEX Legal Contract Review Blueprint for Service & Deliverables Contracts. All analysis must follow the structured methodology:
- Clause-by-clause sequential analysis (no skipping permitted)
- 3-layered analysis per clause: interpretation, exposure, opportunity
- Mandatory pause checkpoints for human oversight
- Risk scoring with Critical/Material/Procedural classification
- Negotiation recommendations based on rule engine