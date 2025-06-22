"""
NEEX Legal Contract Review System
Processing Stage Interface

Defines the abstract interface for pipeline stages in the ReviewOrchestrator.
Each analysis component implements this interface for consistent integration.
"""

from abc import ABC, abstractmethod
from typing import Optional
import logging

from .analysis_context import AnalysisContext


logger = logging.getLogger(__name__)


class ProcessingStage(ABC):
    """
    Abstract base class for all processing stages in the analysis pipeline.
    
    Each stage receives an AnalysisContext, performs its analysis,
    and updates the context with results before returning.
    """
    
    def __init__(self, stage_name: str):
        """
        Initialize the processing stage.
        
        Args:
            stage_name: Human-readable name for this stage (for logging)
        """
        self.stage_name = stage_name
        self.logger = logging.getLogger(f"{__name__}.{stage_name}")
    
    @abstractmethod
    def process(self, context: AnalysisContext) -> None:
        """
        Process the analysis context and update it with stage results.
        
        Args:
            context: The analysis context containing accumulated results
            
        Raises:
            ProcessingStageError: If stage processing fails critically
        """
        pass
    
    def can_process(self, context: AnalysisContext) -> bool:
        """
        Check if this stage can process the given context.
        Override in subclasses for dependency checking.
        
        Args:
            context: The analysis context to check
            
        Returns:
            True if stage can process, False otherwise
        """
        return True
    
    def get_dependencies(self) -> list[str]:
        """
        Get list of stage names this stage depends on.
        Override in subclasses that have prerequisites.
        
        Returns:
            List of stage names that must run before this stage
        """
        return []
    
    def validate_input(self, context: AnalysisContext) -> Optional[str]:
        """
        Validate that the context has required data for this stage.
        
        Args:
            context: The analysis context to validate
            
        Returns:
            Error message if validation fails, None if valid
        """
        return None
    
    def handle_error(self, context: AnalysisContext, error: Exception) -> bool:
        """
        Handle errors that occur during processing.
        
        Args:
            context: The analysis context
            error: The exception that occurred
            
        Returns:
            True if error was handled and processing should continue,
            False if error is critical and processing should stop
        """
        error_msg = f"{self.stage_name} stage failed: {str(error)}"
        self.logger.error(error_msg, exc_info=True)
        context.add_error(error_msg)
        
        # By default, most errors are non-critical
        # Override in subclasses for stage-specific error handling
        return True
    
    def log_stage_entry(self, context: AnalysisContext) -> None:
        """Log entry into this processing stage."""
        self.logger.info(f"Starting {self.stage_name} stage")
        if context.contract_document:
            self.logger.debug(f"Processing contract: {context.contract_document.title}")
    
    def log_stage_exit(self, context: AnalysisContext, success: bool = True) -> None:
        """Log exit from this processing stage."""
        status = "completed" if success else "failed"
        self.logger.info(f"{self.stage_name} stage {status}")


class ProcessingStageError(Exception):
    """Exception raised when a processing stage encounters a critical error."""
    
    def __init__(self, stage_name: str, message: str, cause: Optional[Exception] = None):
        self.stage_name = stage_name
        self.cause = cause
        super().__init__(f"Processing stage '{stage_name}' failed: {message}")


class SkipStageError(ProcessingStageError):
    """Exception to indicate a stage should be skipped (non-critical)."""
    pass