"""
Integration tests for the full NEEX Legal Contract Review pipeline.
"""
import pytest
from pathlib import Path
import json
import time
from unittest.mock import patch, MagicMock

from src.core.review_orchestrator import ReviewOrchestrator
from src.core.analysis_context import AnalysisContext
from src.core.contract_parser import ContractParser, Clause
from src.core.clause_analyzer import ClauseAnalyzer
from src.ai.risk_assessor import RiskAssessor
from src.ai.negotiation_advisor import NegotiationAdvisor
from src.core.report_generator import ReportGenerator, ReportFormat


class TestFullPipeline:
    """Integration tests for the complete analysis pipeline."""
    
    @pytest.fixture
    def sample_contract_path(self, tmp_path):
        """Create a realistic sample contract for testing."""
        contract_text = """
SERVICE AGREEMENT

This Service Agreement (the "Agreement") is entered into as of January 1, 2025 
(the "Effective Date") by and between ABC Corporation, a Delaware corporation 
("Client"), and XYZ Services Ltd., a UK limited company ("Service Provider").

RECITALS
WHEREAS, Client desires to engage Service Provider to perform certain software 
development services; and
WHEREAS, Service Provider has the expertise and resources to provide such services;

NOW, THEREFORE, in consideration of the mutual covenants and agreements contained 
herein, the parties agree as follows:

1. SCOPE OF SERVICES
   1.1 Services. Service Provider shall provide software development services as 
       detailed in Exhibit A ("Services").
   1.2 Deliverables. All deliverables shall meet the specifications in Exhibit A.
   1.3 Timeline. Services shall be completed according to the timeline in Exhibit B.

2. PAYMENT TERMS
   2.1 Fees. Client shall pay Service Provider $50,000 per month.
   2.2 Payment Schedule. Payment is due within 30 days of invoice receipt.
   2.3 Late Payments. Late payments shall incur interest at 1.5% per month.
   2.4 Expenses. Client shall reimburse pre-approved expenses.

3. INTELLECTUAL PROPERTY
   3.1 Ownership. All work product created under this Agreement shall be owned by Client.
   3.2 License. Service Provider grants Client a perpetual license to all deliverables.
   3.3 Background IP. Each party retains ownership of its pre-existing IP.

4. CONFIDENTIALITY
   4.1 Definition. "Confidential Information" means non-public proprietary information.
   4.2 Obligations. Each party shall protect the other's Confidential Information.
   4.3 Duration. Confidentiality obligations survive termination for 5 years.

5. WARRANTIES AND REPRESENTATIONS
   5.1 Service Provider warrants that Services will be performed professionally.
   5.2 Service Provider represents it has the right to enter this Agreement.
   5.3 NO OTHER WARRANTIES. EXCEPT AS EXPRESSLY SET FORTH HEREIN, SERVICE PROVIDER 
       DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED.

6. INDEMNIFICATION
   6.1 Service Provider Indemnity. Service Provider shall indemnify Client against 
       all third-party claims arising from Service Provider's negligence or breach.
   6.2 Client Indemnity. Client shall indemnify Service Provider against claims 
       arising from Client's use of deliverables.
   6.3 Procedure. The indemnified party shall promptly notify the indemnifying party.

7. LIMITATION OF LIABILITY
   7.1 Cap. Each party's liability is limited to fees paid in the 12 months preceding 
       the claim.
   7.2 Exclusions. The limitation does not apply to breaches of confidentiality, 
       indemnification obligations, or gross negligence.
   7.3 NO CONSEQUENTIAL DAMAGES. Neither party is liable for consequential damages.

8. TERM AND TERMINATION
   8.1 Term. This Agreement continues until Services are complete.
   8.2 Termination for Convenience. Either party may terminate with 30 days notice.
   8.3 Termination for Cause. Either party may terminate immediately for material breach 
       that remains uncured after 15 days written notice.
   8.4 Effect. Upon termination, Client shall pay for Services performed.

9. DISPUTE RESOLUTION
   9.1 Negotiation. Parties shall first attempt to resolve disputes through negotiation.
   9.2 Arbitration. Unresolved disputes shall be settled by binding arbitration under 
       ICC rules in London, UK.
   9.3 Injunctive Relief. Either party may seek injunctive relief in court.

10. GENERAL PROVISIONS
    10.1 Governing Law. This Agreement is governed by English law.
    10.2 Entire Agreement. This Agreement constitutes the entire agreement.
    10.3 Amendment. Amendments must be in writing and signed by both parties.
    10.4 Assignment. Neither party may assign without the other's consent.
    10.5 Severability. Invalid provisions shall be severed.
    10.6 Force Majeure. Neither party is liable for delays due to force majeure.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first 
written above.

CLIENT:                           SERVICE PROVIDER:
ABC Corporation                   XYZ Services Ltd.

By: _________________________    By: _________________________
Name: John Smith                  Name: Jane Doe
Title: CEO                        Title: Managing Director
"""
        
        contract_file = tmp_path / "service_agreement.txt"
        contract_file.write_text(contract_text)
        return contract_file
    
    def test_complete_pipeline_execution(self, sample_contract_path, tmp_path):
        """Test the complete pipeline from parsing to report generation."""
        output_dir = tmp_path / "output"
        
        # Create orchestrator
        orchestrator = ReviewOrchestrator()
        
        # Mock pause checkpoints to avoid user input
        with patch('builtins.input', return_value='y'):
            # Execute full pipeline
            result = orchestrator.review_contract(
                sample_contract_path,
                output_dir=output_dir,
                output_format="html"
            )
        
        # Verify all stages completed
        assert result is not None
        
        # Check output files exist
        assert output_dir.exists()
        html_files = list(output_dir.glob("*.html"))
        assert len(html_files) > 0
        
        # Verify report content
        report_content = html_files[0].read_text()
        assert "SERVICE AGREEMENT" in report_content
        assert "Risk Assessment" in report_content
        assert "Negotiation Recommendations" in report_content
    
    def test_pipeline_data_flow(self, sample_contract_path):
        """Test data flows correctly through all pipeline stages."""
        # Create individual components
        parser = ContractParser()
        nlp_processor = MagicMock()
        clause_analyzer = ClauseAnalyzer()
        risk_assessor = RiskAssessor()
        negotiation_advisor = NegotiationAdvisor()
        report_generator = ReportGenerator()
        
        # Stage 1: Parse contract
        parse_result = parser.parse(sample_contract_path)
        assert "clauses" in parse_result
        assert len(parse_result["clauses"]) > 0
        
        # Stage 2: Create context
        context = AnalysisContext()
        context.contract_metadata = parse_result["metadata"]
        context.clauses = parse_result["clauses"]
        
        # Stage 3: NLP Processing (mocked)
        nlp_processor.process.return_value = context
        context = nlp_processor.process(context)
        
        # Stage 4: Clause Analysis
        context = clause_analyzer.process(context)
        assert hasattr(context, 'clause_analyses')
        assert len(context.clause_analyses) > 0
        
        # Stage 5: Risk Assessment
        context = risk_assessor.process(context)
        assert hasattr(context, 'risk_assessment')
        assert 'overall_score' in context.risk_assessment
        
        # Stage 6: Negotiation Advice
        context = negotiation_advisor.process(context)
        assert hasattr(context, 'negotiation_recommendations')
        assert len(context.negotiation_recommendations) > 0
        
        # Stage 7: Report Generation
        report_path = sample_contract_path.parent / "report.json"
        report_generator.generate_report(
            context,
            format=ReportFormat.JSON,
            output_path=report_path
        )
        
        # Verify final output
        assert report_path.exists()
        with open(report_path) as f:
            report_data = json.load(f)
        
        assert "clause_analyses" in report_data
        assert "risk_assessment" in report_data
        assert "negotiation_recommendations" in report_data
    
    def test_pause_checkpoint_integration(self, sample_contract_path):
        """Test pause checkpoint functionality in full pipeline."""
        orchestrator = ReviewOrchestrator()
        
        # Track checkpoint calls
        checkpoint_count = 0
        
        def mock_input(prompt):
            nonlocal checkpoint_count
            checkpoint_count += 1
            return 'y'  # Always continue
        
        with patch('builtins.input', side_effect=mock_input):
            result = orchestrator.review_contract(sample_contract_path)
        
        # Should have triggered checkpoints (contract has >3 clauses)
        assert checkpoint_count > 0
        assert len(orchestrator.checkpoints) == checkpoint_count
    
    def test_error_propagation(self, tmp_path):
        """Test error handling across pipeline stages."""
        # Create invalid contract file
        invalid_file = tmp_path / "invalid.pdf"
        invalid_file.write_bytes(b"Not a valid PDF")
        
        orchestrator = ReviewOrchestrator()
        
        # Should raise parse error
        with pytest.raises(Exception) as exc_info:
            orchestrator.review_contract(invalid_file)
        
        assert "parse" in str(exc_info.value).lower() or "pdf" in str(exc_info.value).lower()
    
    def test_multiple_format_outputs(self, sample_contract_path, tmp_path):
        """Test generating reports in multiple formats."""
        orchestrator = ReviewOrchestrator()
        
        formats = ["html", "markdown", "json", "text"]
        
        for format_type in formats:
            output_dir = tmp_path / format_type
            
            with patch('builtins.input', return_value='y'):
                result = orchestrator.review_contract(
                    sample_contract_path,
                    output_dir=output_dir,
                    output_format=format_type
                )
            
            # Check appropriate file was created
            if format_type == "html":
                assert len(list(output_dir.glob("*.html"))) > 0
            elif format_type == "markdown":
                assert len(list(output_dir.glob("*.md"))) > 0
            elif format_type == "json":
                assert len(list(output_dir.glob("*.json"))) > 0
            elif format_type == "text":
                assert len(list(output_dir.glob("*.txt"))) > 0
    
    def test_high_risk_contract_analysis(self, tmp_path):
        """Test analysis of a high-risk contract."""
        high_risk_contract = """
DANGEROUS SERVICE AGREEMENT

1. UNLIMITED LIABILITY
   Service Provider accepts unlimited liability for any and all damages.

2. ONE-SIDED INDEMNIFICATION  
   Service Provider shall indemnify Client for any reason whatsoever.

3. NO PAYMENT TERMS
   Payment terms to be determined solely by Client.

4. IMMEDIATE TERMINATION
   Client may terminate immediately without cause or notice.

5. NO DISPUTE RESOLUTION
   All disputes decided solely by Client.
"""
        
        contract_file = tmp_path / "high_risk.txt"
        contract_file.write_text(high_risk_contract)
        
        orchestrator = ReviewOrchestrator()
        
        with patch('builtins.input', return_value='y'):
            result = orchestrator.review_contract(
                contract_file,
                output_dir=tmp_path,
                output_format="json"
            )
        
        # Load and verify results
        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) > 0
        
        with open(json_files[0]) as f:
            report = json.load(f)
        
        # Should identify critical risks
        risk_assessment = report.get("risk_assessment", {})
        assert risk_assessment.get("overall_score", 0) > 8.0  # Critical level
        
        # Should have multiple critical recommendations
        recommendations = report.get("negotiation_recommendations", [])
        critical_recs = [r for r in recommendations if r.get("priority") == "Critical"]
        assert len(critical_recs) >= 3
    
    def test_performance_large_contract(self, tmp_path):
        """Test performance with a large contract."""
        # Generate large contract with many clauses
        large_contract = "LARGE CONTRACT\n\n"
        for i in range(1, 101):  # 100 clauses
            large_contract += f"{i}. CLAUSE {i}\n"
            large_contract += f"   This is the content of clause {i} with various terms.\n\n"
        
        contract_file = tmp_path / "large_contract.txt"
        contract_file.write_text(large_contract)
        
        orchestrator = ReviewOrchestrator()
        
        start_time = time.time()
        
        # Disable checkpoints for performance test
        orchestrator.config["blueprint"]["pause_checkpoints"]["enabled"] = False
        
        result = orchestrator.review_contract(
            contract_file,
            output_dir=tmp_path,
            output_format="json"
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete in reasonable time (adjust based on system)
        assert execution_time < 60  # 60 seconds for 100 clauses
        
        # Verify all clauses were analyzed
        json_files = list(tmp_path.glob("*.json"))
        with open(json_files[0]) as f:
            report = json.load(f)
        
        clause_analyses = report.get("clause_analyses", {})
        assert len(clause_analyses) >= 50  # At least half should be analyzed
    
    def test_clause_tag_classification_accuracy(self, sample_contract_path):
        """Test accuracy of clause tag classification."""
        parser = ContractParser()
        analyzer = ClauseAnalyzer()
        
        parse_result = parser.parse(sample_contract_path)
        
        context = AnalysisContext()
        context.clauses = parse_result["clauses"]
        
        context = analyzer.process(context)
        
        # Verify tag assignments
        tag_expectations = {
            "SCOPE OF SERVICES": ["COM", "TEC"],
            "PAYMENT TERMS": ["FIN"],
            "INTELLECTUAL PROPERTY": ["IPX"],
            "CONFIDENTIALITY": ["LEG"],
            "INDEMNIFICATION": ["LEG"],
            "LIMITATION OF LIABILITY": ["LEG"],
            "TERMINATION": ["TRM"],
            "DISPUTE RESOLUTION": ["DIS"]
        }
        
        for clause_id, analysis in context.clause_analyses.items():
            clause = next((c for c in context.clauses if c.id == clause_id), None)
            if clause and clause.title in tag_expectations:
                expected_tags = tag_expectations[clause.title]
                assert any(tag in analysis.tags for tag in expected_tags), \
                    f"Expected tags {expected_tags} for {clause.title}, got {analysis.tags}"
    
    def test_risk_score_calculation_accuracy(self, sample_contract_path):
        """Test accuracy of risk score calculations."""
        orchestrator = ReviewOrchestrator()
        
        with patch('builtins.input', return_value='y'):
            orchestrator.review_contract(
                sample_contract_path,
                output_dir=sample_contract_path.parent,
                output_format="json"
            )
        
        # Load results
        json_files = list(sample_contract_path.parent.glob("*.json"))
        with open(json_files[0]) as f:
            report = json.load(f)
        
        risk_assessment = report["risk_assessment"]
        
        # Verify risk scores are reasonable
        assert 0 <= risk_assessment["overall_score"] <= 10
        
        # Check category scores
        for category, score in risk_assessment["category_scores"].items():
            assert 0 <= score <= 10, f"{category} score out of range: {score}"
        
        # Legal risk should be moderate to high (indemnification, liability clauses)
        assert risk_assessment["category_scores"]["Legal"] >= 5.0
        
        # Financial risk should be moderate (clear payment terms)
        assert 3.0 <= risk_assessment["category_scores"]["Financial"] <= 7.0
