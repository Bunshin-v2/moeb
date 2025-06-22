"""
NEEX Legal Contract Review System
Review Orchestrator Module

Central pipeline coordinator that manages the end-to-end contract analysis workflow.
Implements the NEEX blueprint methodology with pause checkpoints and error handling.
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from .analysis_context import AnalysisContext
from .processing_stage import ProcessingStage, ProcessingStageError, SkipStageError
from .contract_parser import ContractParser
from ..ai.legal_nlp import LegalNLPProcessor
from .clause_analyzer import ClauseAnalyzer
from ..ai.risk_assessor import RiskAssessor


logger = logging.getLogger(__name__)


class ReviewOrchestrator:
    """
    Central orchestrator for the NEEX legal contract review pipeline.
    
    Coordinates sequential processing through all analysis stages while
    implementing NEEX blueprint requirements for pause checkpoints and
    comprehensive error handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the review orchestrator with configuration.
        
        Args:
            config: Configuration dictionary loaded from YAML files
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize processing stages
        self.stages: List[ProcessingStage] = []
        self._setup_pipeline()
        
        # Pipeline metrics
        self.total_contracts_processed = 0
        self.total_processing_time = 0.0
    
    def _setup_pipeline(self) -> None:
        """Initialize and configure the processing pipeline stages."""
        try:
            # Stage 1: Contract parsing
            parser_stage = ContractParsingStage()
            self.stages.append(parser_stage)
            
            # Stage 2: NLP processing  
            nlp_stage = NLPProcessingStage()
            self.stages.append(nlp_stage)
            
            # Stage 3: Clause analysis
            analysis_stage = ClauseAnalysisStage()
            self.stages.append(analysis_stage)
            
            # Stage 4: Risk assessment
            risk_stage = RiskAssessmentStage()
            self.stages.append(risk_stage)
            
            # Stage 5: Negotiation advice (placeholder - to be implemented)
            # negotiation_stage = NegotiationAdviceStage()
            # self.stages.append(negotiation_stage)
            
            # Stage 6: Report generation (placeholder - to be implemented)
            # report_stage = ReportGenerationStage()
            # self.stages.append(report_stage)
            
            self.logger.info(f"Pipeline initialized with {len(self.stages)} stages")
            
        except Exception as e:
            self.logger.error(f"Failed to setup pipeline: {e}")
            raise ProcessingStageError("Pipeline Setup", str(e), e)
    
    def conduct_review(
        self, 
        contract_file: Path,
        pause_checkpoints: bool = True,
        clause_limit: Optional[int] = None,
        filter_tags: Optional[List[str]] = None
    ) -> AnalysisContext:
        """
        Conduct a complete contract review following NEEX methodology.
        
        Args:
            contract_file: Path to the contract file to analyze
            pause_checkpoints: Whether to enable pause checkpoints
            clause_limit: Optional limit on number of clauses to analyze
            filter_tags: Optional list of clause tags to filter analysis
            
        Returns:
            AnalysisContext with complete analysis results
            
        Raises:
            ProcessingStageError: If critical stage processing fails
        """
        start_time = time.time()
        
        # Initialize analysis context
        context = AnalysisContext(
            source_file=contract_file,
            config=self.config
        )
        
        self.logger.info(f"Starting contract review: {contract_file}")
        
        try:
            # Process through each stage
            for i, stage in enumerate(self.stages):
                self._process_stage(stage, context, pause_checkpoints)
                
                # Check pause conditions (NEEX blueprint requirement)
                if pause_checkpoints and self._should_pause(context, i):
                    self._handle_pause_checkpoint(context, i)
                
                # Stop if critical errors occurred
                if not context.should_continue_processing():
                    self.logger.warning("Stopping processing due to critical errors")
                    break
            
            # Calculate final metrics
            context.processing_time = time.time() - start_time
            self.total_contracts_processed += 1
            self.total_processing_time += context.processing_time
            
            self.logger.info(f"Contract review completed in {context.processing_time:.2f}s")
            return context
            
        except Exception as e:
            context.add_error(f"Pipeline execution failed: {str(e)}")
            self.logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            raise ProcessingStageError("Pipeline Execution", str(e), e)
    
    def _process_stage(self, stage: ProcessingStage, context: AnalysisContext, pause_checkpoints: bool) -> None:
        """Process a single pipeline stage with error handling."""
        stage.log_stage_entry(context)
        
        try:
            # Validate stage can process
            if not stage.can_process(context):
                raise SkipStageError(stage.stage_name, "Stage prerequisites not met")
            
            # Validate input data
            validation_error = stage.validate_input(context)
            if validation_error:
                raise ProcessingStageError(stage.stage_name, validation_error)
            
            # Process the stage
            stage.process(context)
            stage.log_stage_exit(context, success=True)
            
        except SkipStageError as e:
            self.logger.warning(f"Skipping {stage.stage_name}: {e}")
            stage.log_stage_exit(context, success=False)
            
        except ProcessingStageError as e:
            # Let stage handle its own error
            should_continue = stage.handle_error(context, e)
            stage.log_stage_exit(context, success=False)
            
            if not should_continue:
                raise e
                
        except Exception as e:
            # Unexpected error - let stage handle it
            should_continue = stage.handle_error(context, e)
            stage.log_stage_exit(context, success=False)
            
            if not should_continue:
                raise ProcessingStageError(stage.stage_name, str(e), e)
    
    def _should_pause(self, context: AnalysisContext, stage_index: int) -> bool:
        """Check if pipeline should pause for checkpoint."""
        if not context.clause_analyses:
            return False
            
        processed_clauses = len(context.clause_analyses)
        return context.is_ready_for_pause_checkpoint(processed_clauses, context.total_tokens)
    
    def _handle_pause_checkpoint(self, context: AnalysisContext, stage_index: int) -> None:
        """Handle pause checkpoint according to NEEX blueprint."""
        checkpoint_data = {
            "stage": stage_index,
            "processed_clauses": len(context.clause_analyses),
            "total_tokens": context.total_tokens,
            "timestamp": time.time(),
            "summary": context.get_summary()
        }
        
        context.pause_checkpoints.append(checkpoint_data)
        self.logger.info(f"Pause checkpoint reached: {len(context.clause_analyses)} clauses processed")
    
    def generate_reports(
        self, 
        context: AnalysisContext, 
        output_dir: Path, 
        format: str = "html"
    ) -> List[Path]:
        """
        Generate analysis reports from the context.
        
        Args:
            context: Completed analysis context
            output_dir: Directory to write reports
            format: Output format (html, pdf, markdown, json)
            
        Returns:
            List of generated report file paths
        """
        # Placeholder implementation - ReportGenerator will handle this
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # For now, create a simple text summary
        summary_file = output_dir / f"summary.{format}"
        with open(summary_file, 'w') as f:
            summary = context.get_summary()
            f.write(f"NEEX Contract Analysis Summary\n")
            f.write(f"================================\n\n")
            f.write(f"Contract: {context.source_file.name}\n")
            f.write(f"Total Clauses: {summary['total_clauses']}\n")
            f.write(f"Critical Issues: {summary['critical_issues']}\n")
            f.write(f"Material Issues: {summary['material_issues']}\n")
            f.write(f"Processing Time: {summary['processing_time']:.2f}s\n")
        
        return [summary_file]


# Concrete stage implementations for existing components

class ContractParsingStage(ProcessingStage):
    """Stage wrapper for ContractParser."""
    
    def __init__(self):
        super().__init__("Contract Parsing")
        self.parser = ContractParser()
    
    def process(self, context: AnalysisContext) -> None:
        context.contract_document = self.parser.parse_document(context.source_file)
    
    def validate_input(self, context: AnalysisContext) -> Optional[str]:
        if not context.source_file.exists():
            return f"Contract file not found: {context.source_file}"
        return None


class NLPProcessingStage(ProcessingStage):
    """Stage wrapper for LegalNLPProcessor."""
    
    def __init__(self):
        super().__init__("NLP Processing")
        self.processor = LegalNLPProcessor()
    
    def process(self, context: AnalysisContext) -> None:
        if not context.contract_document:
            return
            
        # Process each clause with NLP
        for clause in context.contract_document.clauses:
            key_terms = self.processor.extract_key_terms(clause.content)
            context.key_terms.extend(key_terms)
            
            obligations = self.processor.extract_obligations(clause.content)
            context.obligations.extend(obligations)
            
            conditions = self.processor.extract_conditions(clause.content)
            context.conditions.extend(conditions)
    
    def get_dependencies(self) -> list[str]:
        return ["Contract Parsing"]


class ClauseAnalysisStage(ProcessingStage):
    """Stage wrapper for ClauseAnalyzer."""
    
    def __init__(self):
        super().__init__("Clause Analysis")
        self.analyzer = ClauseAnalyzer()
    
    def process(self, context: AnalysisContext) -> None:
        if not context.contract_document:
            return
            
        # Analyze each clause
        for clause in context.contract_document.clauses:
            analysis = self.analyzer.analyze_clause(clause)
            context.clause_analyses.append(analysis)
            context.total_tokens += analysis.token_count
    
    def get_dependencies(self) -> list[str]:
        return ["Contract Parsing", "NLP Processing"]


class RiskAssessmentStage(ProcessingStage):
    """Stage wrapper for RiskAssessor."""
    
    def __init__(self):
        super().__init__("Risk Assessment")
        self.assessor = RiskAssessor()
    
    def process(self, context: AnalysisContext) -> None:
        if not context.clause_analyses:
            return
            
        # Calculate overall risk metrics
        total_risk = 0.0
        risk_counts = {}
        
        for analysis in context.clause_analyses:
            total_risk += analysis.risk_score
            risk_level = analysis.risk_level.value
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
            
            if analysis.risk_score >= 7.0:
                context.high_risk_clauses.append(analysis.clause.number)
        
        context.overall_risk_score = total_risk / len(context.clause_analyses)
        context.risk_distribution = risk_counts
    
    def get_dependencies(self) -> list[str]:
        return ["Clause Analysis"]