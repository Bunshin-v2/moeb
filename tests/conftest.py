"""
Pytest configuration and shared fixtures for NEEX Legal Contract Review tests.
"""
import pytest
from pathlib import Path
from typing import Dict, Any, List
import tempfile
import json
from unittest.mock import Mock, MagicMock

from src.core.analysis_context import AnalysisContext
from src.core.contract_parser import ContractParser, Clause


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_text_contract():
    """Sample contract text for testing."""
    return """
SERVICE AGREEMENT

This Service Agreement (the "Agreement") is entered into as of January 1, 2025 
(the "Effective Date") by and between ABC Corporation ("Client") and 
XYZ Services Ltd. ("Service Provider").

1. SCOPE OF SERVICES
   1.1 The Service Provider shall provide software development services.
   1.2 All deliverables shall be completed within the agreed timeline.

2. PAYMENT TERMS
   2.1 Client shall pay $10,000 per month for services rendered.
   2.2 Payment is due within 30 days of invoice.
   2.3 Late payments shall incur a penalty of 1.5% per month.

3. INTELLECTUAL PROPERTY
   3.1 All work product shall be owned by the Client.
   3.2 Service Provider retains no rights to deliverables.

4. INDEMNIFICATION
   4.1 Service Provider shall indemnify Client against all claims.
   4.2 This indemnification includes unlimited liability.

5. TERMINATION
   5.1 Either party may terminate with 30 days written notice.
   5.2 Early termination requires payment of all outstanding fees.
"""


@pytest.fixture
def sample_clauses():
    """Sample parsed clauses for testing."""
    return [
        Clause(
            id="1",
            number="1",
            title="SCOPE OF SERVICES",
            text="The Service Provider shall provide software development services.",
            children=[
                Clause(id="1.1", number="1.1", text="The Service Provider shall provide software development services."),
                Clause(id="1.2", number="1.2", text="All deliverables shall be completed within the agreed timeline.")
            ]
        ),
        Clause(
            id="2",
            number="2",
            title="PAYMENT TERMS",
            text="Client shall pay $10,000 per month for services rendered.",
            children=[
                Clause(id="2.1", number="2.1", text="Client shall pay $10,000 per month for services rendered."),
                Clause(id="2.2", number="2.2", text="Payment is due within 30 days of invoice."),
                Clause(id="2.3", number="2.3", text="Late payments shall incur a penalty of 1.5% per month.")
            ]
        ),
        Clause(
            id="3",
            number="3",
            title="INTELLECTUAL PROPERTY",
            text="All work product shall be owned by the Client.",
            children=[
                Clause(id="3.1", number="3.1", text="All work product shall be owned by the Client."),
                Clause(id="3.2", number="3.2", text="Service Provider retains no rights to deliverables.")
            ]
        ),
        Clause(
            id="4",
            number="4",
            title="INDEMNIFICATION",
            text="Service Provider shall indemnify Client against all claims.",
            children=[
                Clause(id="4.1", number="4.1", text="Service Provider shall indemnify Client against all claims."),
                Clause(id="4.2", number="4.2", text="This indemnification includes unlimited liability.")
            ]
        ),
        Clause(
            id="5",
            number="5",
            title="TERMINATION",
            text="Either party may terminate with 30 days written notice.",
            children=[
                Clause(id="5.1", number="5.1", text="Either party may terminate with 30 days written notice."),
                Clause(id="5.2", number="5.2", text="Early termination requires payment of all outstanding fees.")
            ]
        )
    ]


@pytest.fixture
def analysis_context(sample_clauses):
    """Create a sample AnalysisContext for testing."""
    context = AnalysisContext()
    context.contract_metadata = {
        "title": "Service Agreement",
        "parties": ["ABC Corporation", "XYZ Services Ltd."],
        "effective_date": "January 1, 2025"
    }
    context.clauses = sample_clauses
    return context


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        "blueprint": {
            "pause_checkpoints": {
                "enabled": True,
                "clause_interval": 3,
                "token_threshold": 3000
            },
            "clause_tags": {
                "TEC": {"name": "Technical", "description": "Technical specifications"},
                "LEG": {"name": "Legal", "description": "Legal and regulatory"},
                "FIN": {"name": "Financial", "description": "Financial terms"},
                "COM": {"name": "Commercial", "description": "Commercial terms"},
                "IPX": {"name": "Intellectual Property", "description": "IP rights"},
                "TRM": {"name": "Termination", "description": "Termination conditions"},
                "DIS": {"name": "Dispute", "description": "Dispute resolution"},
                "DOC": {"name": "Documentation", "description": "Documentation requirements"},
                "EXE": {"name": "Execution", "description": "Execution and delivery"},
                "EXT": {"name": "External", "description": "External dependencies"}
            },
            "risk_levels": {
                "Critical": {"score_range": [8, 10], "description": "Immediate attention required"},
                "Material": {"score_range": [5, 7], "description": "Significant impact possible"},
                "Procedural": {"score_range": [0, 4], "description": "Minor administrative issues"}
            }
        },
        "negotiation_rules": [
            {
                "name": "Unlimited Liability",
                "conditions": {
                    "tags": ["LEG"],
                    "content_contains": ["unlimited liability"],
                    "content_lacks": ["cap", "limit", "maximum"]
                },
                "recommendation": {
                    "type": "redline",
                    "priority": "Critical",
                    "suggested_change": "Add liability cap at reasonable multiple of contract value"
                }
            }
        ]
    }


@pytest.fixture
def mock_nlp_results():
    """Mock NLP analysis results."""
    return {
        "key_terms": ["software development", "payment", "indemnification", "termination"],
        "obligations": [
            {"party": "Service Provider", "obligation": "provide software development services"},
            {"party": "Client", "obligation": "pay $10,000 per month"}
        ],
        "temporal_elements": [
            {"text": "30 days", "context": "payment terms"},
            {"text": "1.5% per month", "context": "late payment penalty"}
        ],
        "entities": {
            "parties": ["ABC Corporation", "XYZ Services Ltd."],
            "amounts": ["$10,000"],
            "dates": ["January 1, 2025"]
        }
    }


@pytest.fixture
def mock_risk_scores():
    """Mock risk assessment scores."""
    return {
        "Financial": {
            "score": 7.5,
            "factors": ["High monthly payment", "Penalty clause", "No payment caps"]
        },
        "Legal": {
            "score": 9.0,
            "factors": ["Unlimited liability", "One-sided indemnification", "No dispute resolution"]
        },
        "Operational": {
            "score": 5.0,
            "factors": ["Unclear deliverables", "No milestones defined"]
        },
        "Compliance": {
            "score": 3.0,
            "factors": ["Standard terms", "No regulatory concerns"]
        },
        "Reputational": {
            "score": 2.0,
            "factors": ["Low public visibility"]
        },
        "Strategic": {
            "score": 6.0,
            "factors": ["IP ownership clear", "No exclusivity concerns"]
        }
    }


@pytest.fixture
def sample_pdf_path(temp_dir):
    """Create a sample PDF file for testing."""
    # For testing purposes, we'll create a simple text file
    # In real tests, you'd use a proper PDF library
    pdf_path = temp_dir / "sample_contract.pdf"
    pdf_path.write_text("Sample PDF content")
    return pdf_path


@pytest.fixture
def sample_docx_path(temp_dir):
    """Create a sample DOCX file for testing."""
    # For testing purposes, we'll create a simple text file
    # In real tests, you'd use python-docx to create a proper DOCX
    docx_path = temp_dir / "sample_contract.docx"
    docx_path.write_text("Sample DOCX content")
    return docx_path


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = MagicMock()
    client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Mock AI response"))]
    )
    return client
