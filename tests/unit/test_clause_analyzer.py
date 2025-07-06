"""
Unit tests for ClauseAnalyzer component.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.core.clause_analyzer import ClauseAnalyzer, ClauseAnalysis
from src.core.contract_parser import Clause
from src.core.analysis_context import AnalysisContext


class TestClauseAnalyzer:
    """Test suite for ClauseAnalyzer."""
    
    @pytest.fixture
    def analyzer(self, mock_config):
        """Create analyzer instance with mock config."""
        with patch('src.core.clause_analyzer.load_config', return_value=mock_config):
            return ClauseAnalyzer()
    
    def test_analyzer_initialization(self, analyzer, mock_config):
        """Test analyzer initialization."""
        assert analyzer.config == mock_config
        assert analyzer.clause_definitions is not None
        assert analyzer.nlp_processor is not None
    
    def test_analyze_single_clause(self, analyzer, sample_clauses):
        """Test analyzing a single clause."""
        clause = sample_clauses[0]  # SCOPE OF SERVICES
        analysis = analyzer.analyze_clause(clause)
        
        assert isinstance(analysis, ClauseAnalysis)
        assert analysis.clause_id == clause.id
        assert analysis.interpretation is not None
        assert analysis.exposure is not None
        assert analysis.opportunity is not None
        assert len(analysis.tags) > 0
        assert analysis.risk_level in ["Critical", "Material", "Procedural"]
    
    def test_tag_classification(self, analyzer):
        """Test clause tag classification."""
        # Test technical clause
        tech_clause = Clause(id="1", number="1", text="Software shall be developed using Python 3.10+")
        tags = analyzer._classify_tags(tech_clause)
        assert "TEC" in tags
        
        # Test financial clause
        fin_clause = Clause(id="2", number="2", text="Payment of $10,000 due within 30 days")
        tags = analyzer._classify_tags(fin_clause)
        assert "FIN" in tags
        
        # Test legal clause
        legal_clause = Clause(id="3", number="3", text="Indemnification against all claims")
        tags = analyzer._classify_tags(legal_clause)
        assert "LEG" in tags
        
        # Test IP clause
        ip_clause = Clause(id="4", number="4", text="All intellectual property rights shall belong to Client")
        tags = analyzer._classify_tags(ip_clause)
        assert "IPX" in tags
        
        # Test termination clause
        term_clause = Clause(id="5", number="5", text="Either party may terminate with 30 days notice")
        tags = analyzer._classify_tags(term_clause)
        assert "TRM" in tags
    
    def test_risk_assessment(self, analyzer):
        """Test risk level assessment."""
        # High risk clause
        high_risk = Clause(id="1", number="1", text="Unlimited liability for all damages")
        analysis = analyzer.analyze_clause(high_risk)
        assert analysis.risk_level == "Critical"
        assert analysis.risk_score >= 8
        
        # Medium risk clause
        medium_risk = Clause(id="2", number="2", text="Payment terms net 30 days")
        analysis = analyzer.analyze_clause(medium_risk)
        assert analysis.risk_level in ["Material", "Procedural"]
        
        # Low risk clause
        low_risk = Clause(id="3", number="3", text="Notices shall be sent via email")
        analysis = analyzer.analyze_clause(low_risk)
        assert analysis.risk_level == "Procedural"
        assert analysis.risk_score < 5
    
    def test_three_layer_analysis(self, analyzer):
        """Test three-layer analysis methodology."""
        clause = Clause(
            id="1",
            number="1",
            text="Service Provider shall indemnify Client against all claims with unlimited liability"
        )
        
        analysis = analyzer.analyze_clause(clause)
        
        # Check interpretation layer
        assert "indemnify" in analysis.interpretation.lower()
        assert len(analysis.interpretation) > 20
        
        # Check exposure layer
        assert "unlimited" in analysis.exposure.lower() or "liability" in analysis.exposure.lower()
        assert len(analysis.exposure) > 20
        
        # Check opportunity layer
        assert any(word in analysis.opportunity.lower() for word in ["negotiate", "cap", "limit", "revise"])
        assert len(analysis.opportunity) > 20
    
    def test_process_method(self, analyzer, analysis_context):
        """Test process method that analyzes all clauses."""
        # Mock NLP processor
        analyzer.nlp_processor.process = Mock(return_value=analysis_context)
        
        # Process the context
        result = analyzer.process(analysis_context)
        
        # Verify all clauses were analyzed
        assert len(result.clause_analyses) == len(analysis_context.clauses)
        
        # Verify each analysis
        for clause_id, analysis in result.clause_analyses.items():
            assert isinstance(analysis, ClauseAnalysis)
            assert analysis.clause_id == clause_id
    
    def test_complex_clause_analysis(self, analyzer):
        """Test analysis of complex multi-part clauses."""
        complex_clause = Clause(
            id="1",
            number="1",
            title="PAYMENT AND PENALTIES",
            text="Payment due in 30 days with 1.5% monthly penalty",
            children=[
                Clause(id="1.1", number="1.1", text="Base payment $10,000"),
                Clause(id="1.2", number="1.2", text="Late penalty 1.5% compounded monthly")
            ]
        )
        
        analysis = analyzer.analyze_clause(complex_clause)
        
        # Should identify multiple tags
        assert "FIN" in analysis.tags
        assert len(analysis.tags) >= 1
        
        # Should identify financial risk
        assert analysis.risk_score > 5
    
    def test_keyword_matching(self, analyzer):
        """Test keyword-based risk identification."""
        # Test various risk keywords
        test_cases = [
            ("unlimited liability", "Critical"),
            ("consequential damages", "Material"),
            ("gross negligence", "Material"),
            ("best efforts", "Procedural"),
            ("email notice", "Procedural")
        ]
        
        for text, expected_level in test_cases:
            clause = Clause(id="1", number="1", text=text)
            analysis = analyzer.analyze_clause(clause)
            # Risk level should be at least as high as expected
            if expected_level == "Critical":
                assert analysis.risk_level == "Critical"
            elif expected_level == "Material":
                assert analysis.risk_level in ["Critical", "Material"]
    
    def test_empty_clause_handling(self, analyzer):
        """Test handling of empty or minimal clauses."""
        empty_clause = Clause(id="1", number="1", text="")
        analysis = analyzer.analyze_clause(empty_clause)
        
        assert analysis.risk_level == "Procedural"
        assert analysis.risk_score == 0
        assert len(analysis.tags) == 0
    
    def test_clause_with_subclauses(self, analyzer):
        """Test analysis includes subclause content."""
        parent = Clause(
            id="1",
            number="1",
            title="LIMITATION OF LIABILITY",
            text="Liability limitations apply as follows:",
            children=[
                Clause(id="1.1", number="1.1", text="Direct damages capped at contract value"),
                Clause(id="1.2", number="1.2", text="No liability for consequential damages"),
                Clause(id="1.3", number="1.3", text="Exclusions do not apply to gross negligence")
            ]
        )
        
        analysis = analyzer.analyze_clause(parent)
        
        # Should consider all subclause content
        assert "LEG" in analysis.tags
        assert analysis.risk_level in ["Material", "Critical"]
        # Analysis should reference subclause content
        assert any(term in analysis.interpretation.lower() 
                  for term in ["damages", "liability", "cap"])
    
    def test_nlp_integration(self, analyzer, mock_nlp_results):
        """Test integration with NLP results."""
        clause = Clause(id="1", number="1", text="Payment of $10,000 due in 30 days")
        
        # Mock NLP results in context
        with patch.object(analyzer, '_get_nlp_insights', return_value=mock_nlp_results):
            analysis = analyzer.analyze_clause(clause)
            
            # Analysis should incorporate NLP insights
            assert "$10,000" in analysis.interpretation or "payment" in analysis.interpretation.lower()
    
    def test_risk_factor_accumulation(self, analyzer):
        """Test accumulation of multiple risk factors."""
        risky_clause = Clause(
            id="1",
            number="1",
            text="Unlimited liability with immediate termination rights and no cure period"
        )
        
        analysis = analyzer.analyze_clause(risky_clause)
        
        # Multiple risk factors should increase score
        assert analysis.risk_score >= 8
        assert analysis.risk_level == "Critical"
        assert len(analysis.risk_factors) >= 3


class TestClauseAnalysis:
    """Test suite for ClauseAnalysis data structure."""
    
    def test_analysis_creation(self):
        """Test creating a clause analysis."""
        analysis = ClauseAnalysis(
            clause_id="1",
            clause_text="Test clause",
            interpretation="This clause means X",
            exposure="Risk is Y",
            opportunity="Can negotiate Z",
            tags=["TEC", "LEG"],
            risk_level="Material",
            risk_score=6.5,
            risk_factors=["Factor 1", "Factor 2"],
            recommendations=["Recommendation 1"]
        )
        
        assert analysis.clause_id == "1"
        assert analysis.interpretation == "This clause means X"
        assert analysis.exposure == "Risk is Y"
        assert analysis.opportunity == "Can negotiate Z"
        assert "TEC" in analysis.tags
        assert analysis.risk_level == "Material"
        assert analysis.risk_score == 6.5
    
    def test_analysis_to_dict(self):
        """Test serialization of analysis to dictionary."""
        analysis = ClauseAnalysis(
            clause_id="1",
            clause_text="Test",
            interpretation="Interp",
            exposure="Exp",
            opportunity="Opp",
            tags=["TEC"],
            risk_level="Critical",
            risk_score=9.0
        )
        
        result_dict = analysis.to_dict()
        
        assert result_dict["clause_id"] == "1"
        assert result_dict["interpretation"] == "Interp"
        assert result_dict["tags"] == ["TEC"]
        assert result_dict["risk_level"] == "Critical"
        assert result_dict["risk_score"] == 9.0
    
    def test_analysis_validation(self):
        """Test validation of analysis data."""
        # Valid risk levels
        for level in ["Critical", "Material", "Procedural"]:
            analysis = ClauseAnalysis(
                clause_id="1",
                clause_text="Test",
                interpretation="I",
                exposure="E",
                opportunity="O",
                tags=[],
                risk_level=level,
                risk_score=5.0
            )
            assert analysis.risk_level == level
        
        # Risk score boundaries
        analysis = ClauseAnalysis(
            clause_id="1",
            clause_text="Test",
            interpretation="I",
            exposure="E", 
            opportunity="O",
            tags=[],
            risk_level="Critical",
            risk_score=10.0  # Maximum score
        )
        assert analysis.risk_score == 10.0
