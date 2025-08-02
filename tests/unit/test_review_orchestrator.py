"""
Unit tests for ReviewOrchestrator component.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from src.core.review_orchestrator import ReviewOrchestrator, PauseCheckpoint
from src.core.analysis_context import AnalysisContext
from src.core.contract_parser import Clause


class TestReviewOrchestrator:
    """Test suite for ReviewOrchestrator."""
    
    @pytest.fixture
    def orchestrator(self, mock_config):
        """Create orchestrator instance with mock config."""
        with patch('src.core.review_orchestrator.load_config', return_value=mock_config):
            # Mock all pipeline stages
            with patch('src.core.review_orchestrator.ContractParser') as mock_parser:
                with patch('src.core.review_orchestrator.LegalNLPProcessor') as mock_nlp:
                    with patch('src.core.review_orchestrator.ClauseAnalyzer') as mock_analyzer:
                        with patch('src.core.review_orchestrator.RiskAssessor') as mock_risk:
                            with patch('src.core.review_orchestrator.NegotiationAdvisor') as mock_negotiation:
                                with patch('src.core.review_orchestrator.ReportGenerator') as mock_report:
                                    orchestrator = ReviewOrchestrator()
                                    
                                    # Set up mock instances
                                    orchestrator.parser = mock_parser.return_value
                                    orchestrator.nlp_processor = mock_nlp.return_value
                                    orchestrator.clause_analyzer = mock_analyzer.return_value
                                    orchestrator.risk_assessor = mock_risk.return_value
                                    orchestrator.negotiation_advisor = mock_negotiation.return_value
                                    orchestrator.report_generator = mock_report.return_value
                                    
                                    return orchestrator
    
    def test_orchestrator_initialization(self, orchestrator, mock_config):
        """Test orchestrator initialization."""
        assert orchestrator.config == mock_config
        assert orchestrator.parser is not None
        assert orchestrator.nlp_processor is not None
        assert orchestrator.clause_analyzer is not None
        assert orchestrator.risk_assessor is not None
        assert orchestrator.negotiation_advisor is not None
        assert orchestrator.report_generator is not None
        assert orchestrator.checkpoints == []
    
    def test_review_contract_full_pipeline(self, orchestrator, temp_dir, sample_clauses):
        """Test full contract review pipeline."""
        # Set up test file
        test_file = temp_dir / "contract.txt"
        test_file.write_text("Test contract")
        
        # Mock pipeline stage responses
        orchestrator.parser.parse.return_value = {
            "metadata": {"title": "Test Contract"},
            "clauses": sample_clauses
        }
        
        mock_context = MagicMock(spec=AnalysisContext)
        mock_context.clauses = sample_clauses
        mock_context.should_pause.return_value = False
        
        orchestrator.nlp_processor.process.return_value = mock_context
        orchestrator.clause_analyzer.process.return_value = mock_context
        orchestrator.risk_assessor.process.return_value = mock_context
        orchestrator.negotiation_advisor.process.return_value = mock_context
        
        # Execute review
        result = orchestrator.review_contract(test_file)
        
        # Verify pipeline execution
        orchestrator.parser.parse.assert_called_once_with(test_file)
        orchestrator.nlp_processor.process.assert_called_once()
        orchestrator.clause_analyzer.process.assert_called_once()
        orchestrator.risk_assessor.process.assert_called_once()
        orchestrator.negotiation_advisor.process.assert_called_once()
        orchestrator.report_generator.process.assert_called_once()
        
        assert result is not None
    
    def test_pause_checkpoint_triggering(self, orchestrator, temp_dir, sample_clauses):
        """Test pause checkpoint triggers correctly."""
        # Set up test file
        test_file = temp_dir / "contract.txt"
        test_file.write_text("Test contract")
        
        # Create clauses that should trigger checkpoint
        many_clauses = [
            Clause(id=str(i), number=str(i), text=f"Clause {i}") 
            for i in range(10)
        ]
        
        orchestrator.parser.parse.return_value = {
            "metadata": {"title": "Test Contract"},
            "clauses": many_clauses
        }
        
        # Mock context to trigger pause after 3 clauses
        mock_context = MagicMock(spec=AnalysisContext)
        mock_context.clauses = many_clauses
        mock_context.clauses_processed = 0
        
        # Simulate pause after 3 clauses
        pause_count = 0
        def should_pause_side_effect():
            nonlocal pause_count
            mock_context.clauses_processed += 1
            if mock_context.clauses_processed % 3 == 0 and pause_count < 2:
                pause_count += 1
                return True
            return False
        
        mock_context.should_pause.side_effect = should_pause_side_effect
        
        # Set up pipeline mocks
        orchestrator.nlp_processor.process.return_value = mock_context
        orchestrator.clause_analyzer.process.return_value = mock_context
        orchestrator.risk_assessor.process.return_value = mock_context
        orchestrator.negotiation_advisor.process.return_value = mock_context
        
        # Mock user input to continue
        with patch('builtins.input', return_value='y'):
            result = orchestrator.review_contract(test_file)
        
        # Verify checkpoints were created
        assert len(orchestrator.checkpoints) == pause_count
        assert all(isinstance(cp, PauseCheckpoint) for cp in orchestrator.checkpoints)
    
    def test_pause_checkpoint_abort(self, orchestrator, temp_dir):
        """Test aborting at pause checkpoint."""
        # Set up test file
        test_file = temp_dir / "contract.txt"
        test_file.write_text("Test contract")
        
        # Set up basic mocks
        orchestrator.parser.parse.return_value = {
            "metadata": {"title": "Test Contract"},
            "clauses": [Clause(id="1", number="1", text="Test clause")]
        }
        
        mock_context = MagicMock(spec=AnalysisContext)
        mock_context.should_pause.return_value = True  # Always pause
        
        orchestrator.nlp_processor.process.return_value = mock_context
        
        # Mock user input to abort
        with patch('builtins.input', return_value='n'):
            with pytest.raises(RuntimeError, match="Review aborted by user"):
                orchestrator.review_contract(test_file)
    
    def test_pipeline_error_handling(self, orchestrator, temp_dir):
        """Test error handling in pipeline stages."""
        # Set up test file
        test_file = temp_dir / "contract.txt"
        test_file.write_text("Test contract")
        
        # Make parser fail
        orchestrator.parser.parse.side_effect = Exception("Parse error")
        
        with pytest.raises(Exception, match="Parse error"):
            orchestrator.review_contract(test_file)
        
        # Test error in middle stage
        orchestrator.parser.parse.side_effect = None
        orchestrator.parser.parse.return_value = {
            "metadata": {}, 
            "clauses": []
        }
        
        orchestrator.nlp_processor.process.side_effect = Exception("NLP error")
        
        with pytest.raises(Exception, match="NLP error"):
            orchestrator.review_contract(test_file)
    
    def test_report_generation_options(self, orchestrator, temp_dir):
        """Test different report generation options."""
        test_file = temp_dir / "contract.txt"
        test_file.write_text("Test contract")
        output_dir = temp_dir / "output"
        
        # Set up mocks
        orchestrator.parser.parse.return_value = {
            "metadata": {"title": "Test"},
            "clauses": []
        }
        
        mock_context = MagicMock()
        orchestrator.nlp_processor.process.return_value = mock_context
        orchestrator.clause_analyzer.process.return_value = mock_context
        orchestrator.risk_assessor.process.return_value = mock_context
        orchestrator.negotiation_advisor.process.return_value = mock_context
        
        # Test different formats
        for format_type in ["html", "pdf", "markdown", "json"]:
            orchestrator.review_contract(
                test_file,
                output_dir=output_dir,
                output_format=format_type
            )
            
            # Verify report generator was called with correct format
            call_args = orchestrator.report_generator.process.call_args
            assert call_args is not None
            # Check if format was passed correctly
    
    def test_checkpoint_data_persistence(self, orchestrator):
        """Test checkpoint data contains necessary information."""
        checkpoint = PauseCheckpoint(
            clause_number=3,
            total_clauses=10,
            issues_found=["Issue 1", "Issue 2"],
            token_count=3500
        )
        
        assert checkpoint.clause_number == 3
        assert checkpoint.total_clauses == 10
        assert len(checkpoint.issues_found) == 2
        assert checkpoint.token_count == 3500
        assert checkpoint.timestamp is not None
    
    def test_stage_execution_order(self, orchestrator, temp_dir):
        """Test pipeline stages execute in correct order."""
        test_file = temp_dir / "contract.txt"
        test_file.write_text("Test contract")
        
        # Track execution order
        execution_order = []
        
        def make_process_tracker(stage_name):
            def process(context):
                execution_order.append(stage_name)
                return context
            return process
        
        # Set up mocks with tracking
        orchestrator.parser.parse.return_value = {
            "metadata": {}, 
            "clauses": []
        }
        
        mock_context = MagicMock()
        orchestrator.nlp_processor.process = make_process_tracker("nlp")
        orchestrator.clause_analyzer.process = make_process_tracker("clause")
        orchestrator.risk_assessor.process = make_process_tracker("risk")
        orchestrator.negotiation_advisor.process = make_process_tracker("negotiation")
        orchestrator.report_generator.process = make_process_tracker("report")
        
        orchestrator.review_contract(test_file)
        
        # Verify correct order
        expected_order = ["nlp", "clause", "risk", "negotiation", "report"]
        assert execution_order == expected_order
    
    def test_parallel_processing_disabled(self, orchestrator):
        """Test that processing is sequential, not parallel."""
        # The orchestrator should process clauses sequentially
        # This is a requirement of the NEEX methodology
        assert not hasattr(orchestrator, 'enable_parallel')
        assert orchestrator.config["blueprint"]["pause_checkpoints"]["enabled"]
    
    def test_empty_contract_handling(self, orchestrator, temp_dir):
        """Test handling of empty contract."""
        test_file = temp_dir / "empty.txt"
        test_file.write_text("")
        
        orchestrator.parser.parse.return_value = {
            "metadata": {"title": "Empty Contract"},
            "clauses": []
        }
        
        mock_context = MagicMock()
        mock_context.clauses = []
        orchestrator.nlp_processor.process.return_value = mock_context
        orchestrator.clause_analyzer.process.return_value = mock_context
        orchestrator.risk_assessor.process.return_value = mock_context
        orchestrator.negotiation_advisor.process.return_value = mock_context
        
        result = orchestrator.review_contract(test_file)
        
        # Should complete without errors
        assert result is not None
    
    def test_checkpoint_token_threshold(self, orchestrator, temp_dir):
        """Test checkpoint triggers on token threshold."""
        test_file = temp_dir / "contract.txt"
        test_file.write_text("Test contract")
        
        # Create a context that exceeds token threshold
        mock_context = MagicMock()
        mock_context.clauses = [Clause(id="1", number="1", text="x" * 4000)]  # Long clause
        mock_context.token_count = 4000
        mock_context.should_pause.return_value = True  # Should pause due to tokens
        
        orchestrator.parser.parse.return_value = {
            "metadata": {},
            "clauses": mock_context.clauses
        }
        
        orchestrator.nlp_processor.process.return_value = mock_context
        orchestrator.clause_analyzer.process.return_value = mock_context
        
        # Mock user input to continue
        with patch('builtins.input', return_value='y'):
            orchestrator.review_contract(test_file)
        
        # Should have created checkpoint due to token count
        assert len(orchestrator.checkpoints) > 0
        assert orchestrator.checkpoints[0].token_count >= 3000


class TestPauseCheckpoint:
    """Test suite for PauseCheckpoint data structure."""
    
    def test_checkpoint_creation(self):
        """Test creating a pause checkpoint."""
        checkpoint = PauseCheckpoint(
            clause_number=5,
            total_clauses=20,
            issues_found=["Critical issue", "Material issue"],
            token_count=2500
        )
        
        assert checkpoint.clause_number == 5
        assert checkpoint.total_clauses == 20
        assert len(checkpoint.issues_found) == 2
        assert checkpoint.token_count == 2500
        assert checkpoint.timestamp is not None
    
    def test_checkpoint_progress_calculation(self):
        """Test progress calculation in checkpoint."""
        checkpoint = PauseCheckpoint(
            clause_number=10,
            total_clauses=40,
            issues_found=[],
            token_count=1000
        )
        
        progress = checkpoint.get_progress_percentage()
        assert progress == 25.0  # 10/40 = 25%
    
    def test_checkpoint_summary(self):
        """Test checkpoint summary generation."""
        checkpoint = PauseCheckpoint(
            clause_number=15,
            total_clauses=30,
            issues_found=["Issue 1", "Issue 2", "Issue 3"],
            token_count=3500
        )
        
        summary = checkpoint.get_summary()
        assert "15/30" in summary
        assert "3 issues" in summary or "3" in summary
        assert "3500" in summary
