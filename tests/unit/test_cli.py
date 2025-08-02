"""
Unit tests for CLI interface.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from src.cli.main import cli, analyze, extract, validate_config, info


class TestCLI:
    """Test suite for CLI interface."""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock ReviewOrchestrator."""
        with patch('src.cli.main.ReviewOrchestrator') as mock:
            orchestrator = mock.return_value
            orchestrator.review_contract.return_value = MagicMock()
            yield orchestrator
    
    @pytest.fixture
    def sample_contract_file(self, tmp_path):
        """Create a sample contract file."""
        contract = tmp_path / "contract.txt"
        contract.write_text("Sample contract content")
        return contract
    
    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "NEEX Legal Contract Review System" in result.output
        assert "Commands:" in result.output
        assert "analyze" in result.output
        assert "extract" in result.output
    
    def test_analyze_command_basic(self, runner, mock_orchestrator, sample_contract_file):
        """Test basic analyze command."""
        result = runner.invoke(analyze, [str(sample_contract_file)])
        
        assert result.exit_code == 0
        assert "Analyzing contract" in result.output
        assert "✓ Analysis Complete!" in result.output
        
        # Verify orchestrator was called
        mock_orchestrator.review_contract.assert_called_once()
        call_args = mock_orchestrator.review_contract.call_args
        assert str(sample_contract_file) in str(call_args)
    
    def test_analyze_command_with_output(self, runner, mock_orchestrator, sample_contract_file, tmp_path):
        """Test analyze command with output directory."""
        output_dir = tmp_path / "output"
        
        result = runner.invoke(analyze, [
            str(sample_contract_file),
            "--output", str(output_dir)
        ])
        
        assert result.exit_code == 0
        
        # Verify output directory was passed
        call_args = mock_orchestrator.review_contract.call_args
        assert "output_dir" in call_args.kwargs
        assert str(output_dir) in str(call_args.kwargs["output_dir"])
    
    def test_analyze_command_with_format(self, runner, mock_orchestrator, sample_contract_file):
        """Test analyze command with different output formats."""
        formats = ["html", "pdf", "markdown", "json", "text"]
        
        for format_type in formats:
            result = runner.invoke(analyze, [
                str(sample_contract_file),
                "--format", format_type
            ])
            
            assert result.exit_code == 0
            
            # Verify format was passed
            call_args = mock_orchestrator.review_contract.call_args
            assert "output_format" in call_args.kwargs
            assert call_args.kwargs["output_format"] == format_type
    
    def test_analyze_command_verbose(self, runner, mock_orchestrator, sample_contract_file):
        """Test analyze command with verbose flag."""
        result = runner.invoke(analyze, [
            str(sample_contract_file),
            "--verbose"
        ])
        
        assert result.exit_code == 0
        assert "Configuration loaded" in result.output or "verbose" in result.output.lower()
    
    def test_analyze_command_missing_file(self, runner, mock_orchestrator):
        """Test analyze command with missing file."""
        result = runner.invoke(analyze, ["nonexistent.pdf"])
        
        assert result.exit_code != 0
        assert "does not exist" in result.output or "not found" in result.output.lower()
    
    def test_analyze_command_error_handling(self, runner, mock_orchestrator, sample_contract_file):
        """Test analyze command error handling."""
        # Make orchestrator raise an exception
        mock_orchestrator.review_contract.side_effect = Exception("Analysis failed")
        
        result = runner.invoke(analyze, [str(sample_contract_file)])
        
        assert result.exit_code != 0
        assert "Error" in result.output
        assert "Analysis failed" in result.output
    
    def test_extract_command_basic(self, runner, sample_contract_file):
        """Test basic extract command."""
        with patch('src.cli.main.ContractParser') as mock_parser:
            mock_parser.return_value.parse.return_value = {
                "metadata": {"title": "Test Contract"},
                "clauses": []
            }
            
            result = runner.invoke(extract, [str(sample_contract_file)])
            
            assert result.exit_code == 0
            assert "Extracting structure" in result.output
            assert "✓ Extraction Complete!" in result.output
            
            mock_parser.return_value.parse.assert_called_once()
    
    def test_extract_command_clauses_only(self, runner, sample_contract_file):
        """Test extract command with clauses-only flag."""
        with patch('src.cli.main.ContractParser') as mock_parser:
            mock_parser.return_value.parse.return_value = {
                "metadata": {"title": "Test"},
                "clauses": [
                    {"id": "1", "text": "Clause 1"},
                    {"id": "2", "text": "Clause 2"}
                ]
            }
            
            result = runner.invoke(extract, [
                str(sample_contract_file),
                "--clauses-only"
            ])
            
            assert result.exit_code == 0
            assert "Clause 1" in result.output
            assert "Clause 2" in result.output
            assert "Metadata" not in result.output
    
    def test_extract_command_output_file(self, runner, sample_contract_file, tmp_path):
        """Test extract command with output file."""
        output_file = tmp_path / "structure.json"
        
        with patch('src.cli.main.ContractParser') as mock_parser:
            mock_parser.return_value.parse.return_value = {
                "metadata": {"title": "Test"},
                "clauses": []
            }
            
            result = runner.invoke(extract, [
                str(sample_contract_file),
                "--output", str(output_file)
            ])
            
            assert result.exit_code == 0
            assert output_file.exists()
            assert f"saved to {output_file}" in result.output
    
    def test_validate_config_command(self, runner, tmp_path):
        """Test validate-config command."""
        # Create test config file
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
        blueprint:
          clause_tags:
            TEC: {name: Technical, description: Tech specs}
            LEG: {name: Legal, description: Legal terms}
          risk_levels:
            Critical: {score_range: [8, 10], description: High risk}
        """)
        
        result = runner.invoke(validate_config, [str(config_file)])
        
        assert result.exit_code == 0
        assert "✓ Configuration is valid" in result.output
    
    def test_validate_config_invalid(self, runner, tmp_path):
        """Test validate-config with invalid config."""
        invalid_config = tmp_path / "invalid.yaml"
        invalid_config.write_text("invalid: yaml: content:")
        
        result = runner.invoke(validate_config, [str(invalid_config)])
        
        assert result.exit_code != 0
        assert "Invalid configuration" in result.output
    
    def test_info_command_basic(self, runner):
        """Test basic info command."""
        result = runner.invoke(info)
        
        assert result.exit_code == 0
        assert "NEEX Legal Review System" in result.output
        assert "Version:" in result.output
    
    def test_info_command_clause_tags(self, runner):
        """Test info command with clause-tags flag."""
        with patch('src.cli.main.load_config') as mock_config:
            mock_config.return_value = {
                "blueprint": {
                    "clause_tags": {
                        "TEC": {"name": "Technical", "description": "Technical specifications"},
                        "LEG": {"name": "Legal", "description": "Legal terms"}
                    }
                }
            }
            
            result = runner.invoke(info, ["--clause-tags"])
            
            assert result.exit_code == 0
            assert "Clause Tags:" in result.output
            assert "TEC" in result.output
            assert "Technical" in result.output
            assert "LEG" in result.output
            assert "Legal" in result.output
    
    def test_info_command_risk_levels(self, runner):
        """Test info command with risk-levels flag."""
        with patch('src.cli.main.load_config') as mock_config:
            mock_config.return_value = {
                "blueprint": {
                    "risk_levels": {
                        "Critical": {"score_range": [8, 10], "description": "Immediate attention"},
                        "Material": {"score_range": [5, 7], "description": "Significant impact"}
                    }
                }
            }
            
            result = runner.invoke(info, ["--risk-levels"])
            
            assert result.exit_code == 0
            assert "Risk Levels:" in result.output
            assert "Critical" in result.output
            assert "8-10" in result.output
            assert "Material" in result.output
            assert "5-7" in result.output
    
    def test_info_command_negotiation_rules(self, runner):
        """Test info command with negotiation-rules flag."""
        with patch('src.cli.main.load_config') as mock_config:
            mock_config.return_value = {
                "negotiation_rules": [
                    {
                        "name": "Unlimited Liability",
                        "conditions": {"tags": ["LEG"]},
                        "recommendation": {"priority": "Critical"}
                    }
                ]
            }
            
            result = runner.invoke(info, ["--negotiation-rules"])
            
            assert result.exit_code == 0
            assert "Negotiation Rules:" in result.output
            assert "Unlimited Liability" in result.output
            assert "Critical" in result.output
    
    def test_main_cli_group(self, runner):
        """Test main CLI group commands."""
        result = runner.invoke(cli)
        
        assert result.exit_code == 0
        assert "Commands:" in result.output
        
        # Test listing commands
        for command in ["analyze", "extract", "validate-config", "info"]:
            assert command in result.output
    
    def test_cli_error_formatting(self, runner, mock_orchestrator):
        """Test CLI error formatting with Rich."""
        # Test that errors are properly formatted
        mock_orchestrator.review_contract.side_effect = ValueError("Invalid input")
        
        result = runner.invoke(analyze, ["fake.pdf"])
        
        assert result.exit_code != 0
        # Should show formatted error (exact format depends on Rich)
        assert "Error" in result.output or "error" in result.output
    
    def test_analyze_progress_display(self, runner, mock_orchestrator, sample_contract_file):
        """Test progress display during analysis."""
        # Mock a longer-running analysis
        def slow_review(*args, **kwargs):
            import time
            time.sleep(0.1)
            return MagicMock()
        
        mock_orchestrator.review_contract.side_effect = slow_review
        
        result = runner.invoke(analyze, [str(sample_contract_file)])
        
        assert result.exit_code == 0
        # Should show some progress indication
        assert "Analyzing" in result.output
    
    def test_config_file_option(self, runner, mock_orchestrator, sample_contract_file, tmp_path):
        """Test using custom config file."""
        custom_config = tmp_path / "custom.yaml"
        custom_config.write_text("custom: config")
        
        with patch('src.cli.main.load_config') as mock_load:
            mock_load.return_value = {"custom": "config"}
            
            result = runner.invoke(analyze, [
                str(sample_contract_file),
                "--config", str(custom_config)
            ])
            
            assert result.exit_code == 0
            mock_load.assert_called_with(str(custom_config))
