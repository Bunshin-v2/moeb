"""
Unit tests for ReportGenerator component.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
from jinja2 import Template

from src.core.report_generator import ReportGenerator, ReportFormat
from src.core.analysis_context import AnalysisContext
from src.core.clause_analyzer import ClauseAnalysis
from src.ai.negotiation_advisor import NegotiationRecommendation


class TestReportGenerator:
    """Test suite for ReportGenerator."""
    
    @pytest.fixture
    def generator(self, mock_config):
        """Create report generator instance."""
        with patch('src.core.report_generator.load_config', return_value=mock_config):
            return ReportGenerator()
    
    @pytest.fixture
    def complete_context(self, analysis_context):
        """Create a complete analysis context with all data."""
        # Add clause analyses
        analysis_context.clause_analyses = {
            "1": ClauseAnalysis(
                clause_id="1",
                clause_text="Unlimited liability clause",
                interpretation="Broad liability exposure",
                exposure="Significant financial risk",
                opportunity="Negotiate liability cap",
                tags=["LEG"],
                risk_level="Critical",
                risk_score=9.0,
                risk_factors=["unlimited liability"]
            ),
            "2": ClauseAnalysis(
                clause_id="2",
                clause_text="Payment terms",
                interpretation="Standard payment terms",
                exposure="Minimal risk",
                opportunity="Could extend payment period",
                tags=["FIN"],
                risk_level="Procedural",
                risk_score=2.0,
                risk_factors=[]
            )
        }
        
        # Add risk assessment
        analysis_context.risk_assessment = {
            "overall_score": 7.5,
            "category_scores": {
                "Financial": 6.0,
                "Legal": 9.0,
                "Operational": 5.0,
                "Compliance": 3.0,
                "Reputational": 2.0,
                "Strategic": 4.0
            },
            "critical_risks": ["Unlimited liability", "No insurance requirements"],
            "risk_summary": "High legal risk due to unlimited liability"
        }
        
        # Add negotiation recommendations
        analysis_context.negotiation_recommendations = [
            NegotiationRecommendation(
                clause_id="1",
                rule_name="Unlimited Liability",
                type="redline",
                priority="Critical",
                suggested_change="Add liability cap at 12 months fees",
                rationale="Reduces catastrophic loss exposure"
            ),
            NegotiationRecommendation(
                clause_id="2",
                rule_name="Payment Terms",
                type="negotiation_point",
                priority="Low",
                suggested_change="Request 45-day payment terms",
                rationale="Improve cash flow"
            )
        ]
        
        # Add summary
        analysis_context.negotiation_summary = {
            "total_recommendations": 2,
            "critical_count": 1,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 1
        }
        
        return analysis_context
    
    def test_generator_initialization(self, generator):
        """Test report generator initialization."""
        assert generator.config is not None
        assert generator.template_loader is not None
        assert generator.templates is not None
    
    def test_generate_html_report(self, generator, complete_context, temp_dir):
        """Test HTML report generation."""
        output_path = temp_dir / "report.html"
        
        result = generator.generate_report(
            complete_context,
            format=ReportFormat.HTML,
            output_path=output_path
        )
        
        assert output_path.exists()
        content = output_path.read_text()
        
        # Check key content
        assert "<html" in content
        assert "Unlimited liability" in content
        assert "Critical" in content
        assert "Risk Assessment" in content
        assert "Negotiation Recommendations" in content
    
    def test_generate_pdf_report(self, generator, complete_context, temp_dir):
        """Test PDF report generation."""
        output_path = temp_dir / "report.pdf"
        
        # Mock PDF generation since it requires external dependencies
        with patch('src.core.report_generator.HTML') as mock_html:
            mock_html.return_value.write_pdf = Mock()
            
            result = generator.generate_report(
                complete_context,
                format=ReportFormat.PDF,
                output_path=output_path
            )
            
            mock_html.return_value.write_pdf.assert_called_once()
    
    def test_generate_markdown_report(self, generator, complete_context, temp_dir):
        """Test Markdown report generation."""
        output_path = temp_dir / "report.md"
        
        result = generator.generate_report(
            complete_context,
            format=ReportFormat.MARKDOWN,
            output_path=output_path
        )
        
        assert output_path.exists()
        content = output_path.read_text()
        
        # Check Markdown formatting
        assert "# " in content  # Headers
        assert "## " in content
        assert "**Critical**" in content or "**critical**" in content
        assert "- " in content  # Lists
    
    def test_generate_json_report(self, generator, complete_context, temp_dir):
        """Test JSON report generation."""
        output_path = temp_dir / "report.json"
        
        result = generator.generate_report(
            complete_context,
            format=ReportFormat.JSON,
            output_path=output_path
        )
        
        assert output_path.exists()
        
        # Verify valid JSON
        with open(output_path) as f:
            data = json.load(f)
        
        assert "metadata" in data
        assert "clause_analyses" in data
        assert "risk_assessment" in data
        assert "negotiation_recommendations" in data
    
    def test_generate_text_report(self, generator, complete_context, temp_dir):
        """Test plain text report generation."""
        output_path = temp_dir / "report.txt"
        
        result = generator.generate_report(
            complete_context,
            format=ReportFormat.TEXT,
            output_path=output_path
        )
        
        assert output_path.exists()
        content = output_path.read_text()
        
        # Check plain text formatting
        assert "CONTRACT REVIEW REPORT" in content
        assert "Unlimited liability" in content
        assert "Critical" in content
        assert "=" in content  # Section separators
    
    def test_process_method(self, generator, complete_context, temp_dir):
        """Test process method integration."""
        generator.output_dir = temp_dir
        generator.output_format = "html"
        
        result = generator.process(complete_context)
        
        # Should generate report files
        html_files = list(temp_dir.glob("*.html"))
        assert len(html_files) > 0
        
        # Should return context with report paths
        assert hasattr(result, 'report_paths')
        assert len(result.report_paths) > 0
    
    def test_template_rendering(self, generator, complete_context):
        """Test Jinja2 template rendering."""
        # Create simple template
        template_str = """
        Contract: {{ metadata.title }}
        Critical Issues: {{ risk_assessment.critical_risks | length }}
        Recommendations: {{ negotiation_recommendations | length }}
        """
        
        template = Template(template_str)
        rendered = template.render(
            metadata=complete_context.contract_metadata,
            risk_assessment=complete_context.risk_assessment,
            negotiation_recommendations=complete_context.negotiation_recommendations
        )
        
        assert "Contract:" in rendered
        assert "Critical Issues: 2" in rendered
        assert "Recommendations: 2" in rendered
    
    def test_missing_template_fallback(self, generator, complete_context, temp_dir):
        """Test fallback when template is missing."""
        # Remove templates to force fallback
        generator.templates = {}
        
        output_path = temp_dir / "report.html"
        result = generator.generate_report(
            complete_context,
            format=ReportFormat.HTML,
            output_path=output_path
        )
        
        # Should still generate report using fallback
        assert output_path.exists()
        content = output_path.read_text()
        assert len(content) > 100  # Non-empty report
    
    def test_empty_context_handling(self, generator, temp_dir):
        """Test handling of empty/minimal context."""
        empty_context = AnalysisContext()
        output_path = temp_dir / "empty_report.html"
        
        result = generator.generate_report(
            empty_context,
            format=ReportFormat.HTML,
            output_path=output_path
        )
        
        assert output_path.exists()
        content = output_path.read_text()
        assert "No clauses analyzed" in content or len(content) > 0
    
    def test_output_directory_creation(self, generator, complete_context, temp_dir):
        """Test automatic output directory creation."""
        nested_dir = temp_dir / "nested" / "output"
        output_path = nested_dir / "report.html"
        
        result = generator.generate_report(
            complete_context,
            format=ReportFormat.HTML,
            output_path=output_path
        )
        
        assert nested_dir.exists()
        assert output_path.exists()
    
    def test_multiple_format_generation(self, generator, complete_context, temp_dir):
        """Test generating reports in multiple formats."""
        formats = [
            (ReportFormat.HTML, "report.html"),
            (ReportFormat.MARKDOWN, "report.md"),
            (ReportFormat.JSON, "report.json"),
            (ReportFormat.TEXT, "report.txt")
        ]
        
        for format_type, filename in formats:
            output_path = temp_dir / filename
            
            # Skip PDF as it requires external dependencies
            if format_type == ReportFormat.PDF:
                continue
                
            result = generator.generate_report(
                complete_context,
                format=format_type,
                output_path=output_path
            )
            
            assert output_path.exists()
            assert output_path.stat().st_size > 0
    
    def test_risk_visualization(self, generator, complete_context):
        """Test risk score visualization in reports."""
        # Generate HTML report and check for risk visualization
        html_content = generator._generate_html_content(complete_context)
        
        # Should include risk scores
        assert "9.0" in html_content  # Legal risk score
        assert "6.0" in html_content  # Financial risk score
        
        # Should include risk categories
        assert "Legal" in html_content
        assert "Financial" in html_content
        assert "Operational" in html_content
    
    def test_clause_grouping_by_tag(self, generator, complete_context):
        """Test grouping of clauses by tag in reports."""
        # Add more clauses with different tags
        complete_context.clause_analyses["3"] = ClauseAnalysis(
            clause_id="3",
            clause_text="IP ownership clause",
            interpretation="IP rights allocation",
            exposure="IP loss risk",
            opportunity="Clarify ownership",
            tags=["IPX"],
            risk_level="Material",
            risk_score=7.0,
            risk_factors=["unclear ownership"]
        )
        
        html_content = generator._generate_html_content(complete_context)
        
        # Should group by tags
        assert "LEG" in html_content
        assert "FIN" in html_content
        assert "IPX" in html_content
    
    def test_executive_summary_generation(self, generator, complete_context):
        """Test executive summary generation."""
        html_content = generator._generate_html_content(complete_context)
        
        # Should include executive summary
        assert "executive summary" in html_content.lower() or "summary" in html_content.lower()
        assert "critical" in html_content.lower()
        assert "recommendations" in html_content.lower()
    
    def test_report_metadata(self, generator, complete_context, temp_dir):
        """Test report metadata inclusion."""
        output_path = temp_dir / "report.json"
        
        generator.generate_report(
            complete_context,
            format=ReportFormat.JSON,
            output_path=output_path
        )
        
        with open(output_path) as f:
            data = json.load(f)
        
        # Should include metadata
        assert "metadata" in data
        assert "generated_at" in data["metadata"] or "timestamp" in data
        assert "contract_title" in data["metadata"] or "title" in data["metadata"]
    
    def test_error_handling(self, generator, complete_context):
        """Test error handling in report generation."""
        # Test with invalid output path
        with pytest.raises(Exception):
            generator.generate_report(
                complete_context,
                format=ReportFormat.HTML,
                output_path="/invalid/path/report.html"
            )
        
        # Test with invalid format
        with pytest.raises(Exception):
            generator.generate_report(
                complete_context,
                format="invalid_format",
                output_path="report.xyz"
            )


class TestReportFormat:
    """Test suite for ReportFormat enum."""
    
    def test_format_values(self):
        """Test report format enum values."""
        assert ReportFormat.HTML.value == "html"
        assert ReportFormat.PDF.value == "pdf"
        assert ReportFormat.MARKDOWN.value == "markdown"
        assert ReportFormat.JSON.value == "json"
        assert ReportFormat.TEXT.value == "text"
    
    def test_format_file_extensions(self):
        """Test getting file extensions for formats."""
        assert ReportFormat.HTML.get_extension() == ".html"
        assert ReportFormat.PDF.get_extension() == ".pdf"
        assert ReportFormat.MARKDOWN.get_extension() == ".md"
        assert ReportFormat.JSON.get_extension() == ".json"
        assert ReportFormat.TEXT.get_extension() == ".txt"
