"""
Unit tests for NegotiationAdvisor component.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.ai.negotiation_advisor import NegotiationAdvisor, NegotiationRecommendation
from src.core.analysis_context import AnalysisContext
from src.core.clause_analyzer import ClauseAnalysis


class TestNegotiationAdvisor:
    """Test suite for NegotiationAdvisor."""
    
    @pytest.fixture
    def advisor(self, mock_config):
        """Create advisor instance with mock config."""
        with patch('src.ai.negotiation_advisor.load_config', return_value=mock_config):
            return NegotiationAdvisor()
    
    def test_advisor_initialization(self, advisor, mock_config):
        """Test advisor initialization."""
        assert advisor.config == mock_config
        assert advisor.rules is not None
        assert len(advisor.rules) > 0
    
    def test_process_context(self, advisor, analysis_context):
        """Test processing analysis context."""
        # Add mock clause analyses
        analysis_context.clause_analyses = {
            "1": ClauseAnalysis(
                clause_id="1",
                clause_text="Unlimited liability for all damages",
                interpretation="Broad liability",
                exposure="Significant financial risk",
                opportunity="Negotiate liability cap",
                tags=["LEG"],
                risk_level="Critical",
                risk_score=9.0,
                risk_factors=["unlimited liability"]
            ),
            "2": ClauseAnalysis(
                clause_id="2",
                clause_text="Payment due in 30 days",
                interpretation="Standard payment terms",
                exposure="Minimal risk",
                opportunity="Could negotiate extended terms",
                tags=["FIN"],
                risk_level="Procedural",
                risk_score=2.0,
                risk_factors=[]
            )
        }
        
        # Process the context
        result = advisor.process(analysis_context)
        
        # Should have recommendations
        assert hasattr(result, 'negotiation_recommendations')
        assert len(result.negotiation_recommendations) > 0
        
        # Should have at least one critical recommendation for unlimited liability
        critical_recs = [r for r in result.negotiation_recommendations 
                        if r.priority == "Critical"]
        assert len(critical_recs) > 0
    
    def test_rule_matching(self, advisor):
        """Test rule matching logic."""
        # Create analysis with specific conditions
        analysis = ClauseAnalysis(
            clause_id="1",
            clause_text="Service Provider accepts unlimited liability for all claims",
            interpretation="Broad liability acceptance",
            exposure="Extreme financial exposure",
            opportunity="Must negotiate cap",
            tags=["LEG"],
            risk_level="Critical",
            risk_score=10.0,
            risk_factors=["unlimited liability"]
        )
        
        # Apply rules
        recommendations = advisor._apply_rules(analysis)
        
        # Should match unlimited liability rule
        assert len(recommendations) > 0
        unlimited_rec = next((r for r in recommendations 
                            if "unlimited liability" in r.rule_name.lower()), None)
        assert unlimited_rec is not None
        assert unlimited_rec.priority == "Critical"
        assert "cap" in unlimited_rec.suggested_change.lower()
    
    def test_recommendation_generation(self, advisor):
        """Test generation of different recommendation types."""
        # Test redline recommendation
        redline_analysis = ClauseAnalysis(
            clause_id="1",
            clause_text="One-sided indemnification favoring only Client",
            interpretation="Unbalanced risk allocation",
            exposure="Service provider bears all risk",
            opportunity="Negotiate mutual indemnification",
            tags=["LEG"],
            risk_level="Material",
            risk_score=7.0,
            risk_factors=["one-sided indemnification"]
        )
        
        recommendations = advisor._apply_rules(redline_analysis)
        redline_recs = [r for r in recommendations if r.type == "redline"]
        assert len(redline_recs) > 0
        
        # Test clarification recommendation
        unclear_analysis = ClauseAnalysis(
            clause_id="2",
            clause_text="Deliverables shall be completed in reasonable time",
            interpretation="Vague timeline",
            exposure="Disputes over timing",
            opportunity="Define specific deadlines",
            tags=["COM"],
            risk_level="Material",
            risk_score=6.0,
            risk_factors=["vague terms"]
        )
        
        recommendations = advisor._apply_rules(unclear_analysis)
        assert any(r.type == "clarification" for r in recommendations)
    
    def test_priority_levels(self, advisor):
        """Test different priority levels of recommendations."""
        # Critical priority
        critical_analysis = ClauseAnalysis(
            clause_id="1",
            clause_text="No limitation on consequential damages",
            interpretation="Broad damages",
            exposure="Catastrophic losses possible",
            opportunity="Must limit damages",
            tags=["LEG"],
            risk_level="Critical",
            risk_score=9.5,
            risk_factors=["consequential damages", "no limit"]
        )
        
        recs = advisor._apply_rules(critical_analysis)
        assert any(r.priority == "Critical" for r in recs)
        
        # High priority
        high_analysis = ClauseAnalysis(
            clause_id="2",
            clause_text="Termination only for cause with no cure period",
            interpretation="Harsh termination",
            exposure="Immediate termination risk",
            opportunity="Add cure period",
            tags=["TRM"],
            risk_level="Material",
            risk_score=7.0,
            risk_factors=["no cure period"]
        )
        
        recs = advisor._apply_rules(high_analysis)
        assert any(r.priority in ["High", "Critical"] for r in recs)
    
    def test_multiple_rule_matches(self, advisor):
        """Test when multiple rules match a single clause."""
        complex_analysis = ClauseAnalysis(
            clause_id="1",
            clause_text="Unlimited liability with one-sided indemnification and no insurance",
            interpretation="Multiple risk factors",
            exposure="Extreme exposure on multiple fronts",
            opportunity="Comprehensive renegotiation needed",
            tags=["LEG", "FIN"],
            risk_level="Critical",
            risk_score=10.0,
            risk_factors=["unlimited liability", "one-sided indemnification", "no insurance"]
        )
        
        recommendations = advisor._apply_rules(complex_analysis)
        
        # Should have multiple recommendations
        assert len(recommendations) >= 2
        
        # Should cover different aspects
        rule_names = [r.rule_name.lower() for r in recommendations]
        assert any("liability" in name for name in rule_names)
        assert any("indemnif" in name for name in rule_names)
    
    def test_negotiation_strategy(self, advisor, analysis_context):
        """Test overall negotiation strategy generation."""
        # Add varied clause analyses
        analysis_context.clause_analyses = {
            "1": ClauseAnalysis(
                clause_id="1",
                clause_text="Critical issue clause",
                interpretation="I",
                exposure="E",
                opportunity="O",
                tags=["LEG"],
                risk_level="Critical",
                risk_score=9.0,
                risk_factors=["critical factor"]
            ),
            "2": ClauseAnalysis(
                clause_id="2",
                clause_text="Material issue clause",
                interpretation="I",
                exposure="E",
                opportunity="O",
                tags=["FIN"],
                risk_level="Material",
                risk_score=6.0,
                risk_factors=["material factor"]
            ),
            "3": ClauseAnalysis(
                clause_id="3",
                clause_text="Procedural issue clause",
                interpretation="I",
                exposure="E",
                opportunity="O",
                tags=["DOC"],
                risk_level="Procedural",
                risk_score=2.0,
                risk_factors=[]
            )
        }
        
        result = advisor.process(analysis_context)
        
        # Should prioritize critical issues
        critical_recs = [r for r in result.negotiation_recommendations 
                        if r.priority == "Critical"]
        high_recs = [r for r in result.negotiation_recommendations 
                    if r.priority == "High"]
        
        # Critical should come before high priority
        if critical_recs and high_recs:
            first_critical_idx = result.negotiation_recommendations.index(critical_recs[0])
            first_high_idx = result.negotiation_recommendations.index(high_recs[0])
            assert first_critical_idx < first_high_idx
    
    def test_empty_context_handling(self, advisor):
        """Test handling empty analysis context."""
        empty_context = AnalysisContext()
        empty_context.clause_analyses = {}
        
        result = advisor.process(empty_context)
        
        assert hasattr(result, 'negotiation_recommendations')
        assert result.negotiation_recommendations == []
    
    def test_custom_rule_application(self, advisor):
        """Test custom negotiation rules."""
        # Add a custom rule
        custom_rule = {
            "name": "Custom Test Rule",
            "conditions": {
                "tags": ["IPX"],
                "content_contains": ["intellectual property"],
                "content_lacks": ["ownership"]
            },
            "recommendation": {
                "type": "addition",
                "priority": "High",
                "suggested_change": "Add clear IP ownership clause"
            }
        }
        
        advisor.rules.append(custom_rule)
        
        # Test with matching clause
        ip_analysis = ClauseAnalysis(
            clause_id="1",
            clause_text="All intellectual property created during engagement",
            interpretation="IP mentioned but ownership unclear",
            exposure="Ownership disputes possible",
            opportunity="Clarify IP ownership",
            tags=["IPX"],
            risk_level="Material",
            risk_score=7.0,
            risk_factors=["unclear ownership"]
        )
        
        recommendations = advisor._apply_rules(ip_analysis)
        custom_rec = next((r for r in recommendations 
                          if r.rule_name == "Custom Test Rule"), None)
        
        assert custom_rec is not None
        assert custom_rec.type == "addition"
        assert custom_rec.priority == "High"
    
    def test_recommendation_deduplication(self, advisor):
        """Test that duplicate recommendations are avoided."""
        # Create analysis that might trigger same rule multiple times
        analysis = ClauseAnalysis(
            clause_id="1",
            clause_text="Unlimited liability and no liability cap with unlimited exposure",
            interpretation="Multiple unlimited references",
            exposure="Extreme exposure",
            opportunity="Cap needed",
            tags=["LEG"],
            risk_level="Critical",
            risk_score=10.0,
            risk_factors=["unlimited liability", "no cap", "unlimited exposure"]
        )
        
        recommendations = advisor._apply_rules(analysis)
        
        # Check for duplicates
        rule_names = [r.rule_name for r in recommendations]
        assert len(rule_names) == len(set(rule_names))  # No duplicates
    
    def test_negotiation_summary_generation(self, advisor, analysis_context):
        """Test generation of negotiation summary."""
        # Add comprehensive analyses
        analysis_context.clause_analyses = {
            str(i): ClauseAnalysis(
                clause_id=str(i),
                clause_text=f"Clause {i}",
                interpretation="I",
                exposure="E",
                opportunity="O",
                tags=["LEG"],
                risk_level="Critical" if i == 1 else "Material",
                risk_score=9.0 if i == 1 else 6.0,
                risk_factors=[f"factor_{i}"]
            ) for i in range(1, 6)
        }
        
        result = advisor.process(analysis_context)
        
        # Should generate summary
        assert hasattr(result, 'negotiation_summary')
        summary = result.negotiation_summary
        
        assert 'total_recommendations' in summary
        assert 'critical_count' in summary
        assert 'high_count' in summary
        assert 'medium_count' in summary
        assert summary['total_recommendations'] == len(result.negotiation_recommendations)


class TestNegotiationRecommendation:
    """Test suite for NegotiationRecommendation data structure."""
    
    def test_recommendation_creation(self):
        """Test creating a negotiation recommendation."""
        rec = NegotiationRecommendation(
            clause_id="1",
            rule_name="Test Rule",
            type="redline",
            priority="Critical",
            suggested_change="Change X to Y",
            rationale="Because of risk Z",
            alternative_approaches=["Option A", "Option B"]
        )
        
        assert rec.clause_id == "1"
        assert rec.rule_name == "Test Rule"
        assert rec.type == "redline"
        assert rec.priority == "Critical"
        assert rec.suggested_change == "Change X to Y"
        assert rec.rationale == "Because of risk Z"
        assert len(rec.alternative_approaches) == 2
    
    def test_recommendation_types(self):
        """Test different recommendation types."""
        types = ["redline", "clarification", "addition", "deletion", "negotiation_point"]
        
        for rec_type in types:
            rec = NegotiationRecommendation(
                clause_id="1",
                rule_name="Test",
                type=rec_type,
                priority="High",
                suggested_change="Change"
            )
            assert rec.type == rec_type
    
    def test_recommendation_priorities(self):
        """Test recommendation priority levels."""
        priorities = ["Critical", "High", "Medium", "Low"]
        
        for priority in priorities:
            rec = NegotiationRecommendation(
                clause_id="1",
                rule_name="Test",
                type="redline",
                priority=priority,
                suggested_change="Change"
            )
            assert rec.priority == priority
    
    def test_recommendation_to_dict(self):
        """Test recommendation serialization."""
        rec = NegotiationRecommendation(
            clause_id="1",
            rule_name="Test Rule",
            type="redline",
            priority="Critical",
            suggested_change="Change this",
            rationale="Risk mitigation",
            alternative_approaches=["Alt 1"]
        )
        
        rec_dict = rec.to_dict()
        
        assert rec_dict["clause_id"] == "1"
        assert rec_dict["rule_name"] == "Test Rule"
        assert rec_dict["type"] == "redline"
        assert rec_dict["priority"] == "Critical"
        assert rec_dict["suggested_change"] == "Change this"
        assert rec_dict["rationale"] == "Risk mitigation"
        assert rec_dict["alternative_approaches"] == ["Alt 1"]
