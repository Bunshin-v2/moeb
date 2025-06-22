"""
NEEX Legal Contract Review System
Analysis Context Module

Defines the central data structure that flows through the analysis pipeline.
Accumulates results from each processing stage.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

from .contract_parser import ContractDocument, Clause
from .clause_analyzer import ClauseAnalysis


@dataclass
class AnalysisContext:
    """
    Central context object that flows through the ReviewOrchestrator pipeline.
    Accumulates analysis results from each processing stage.
    """
    
    # Input data
    source_file: Path
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Stage 1: Contract parsing results
    contract_document: Optional[ContractDocument] = None
    
    # Stage 2: NLP processing results
    extracted_entities: List[Dict[str, Any]] = field(default_factory=list)
    key_terms: List[str] = field(default_factory=list)
    obligations: List[Dict[str, str]] = field(default_factory=list)
    conditions: List[Dict[str, str]] = field(default_factory=list)
    
    # Stage 3: Clause analysis results
    clause_analyses: List[ClauseAnalysis] = field(default_factory=list)
    
    # Stage 4: Risk assessment results
    overall_risk_score: float = 0.0
    risk_distribution: Dict[str, float] = field(default_factory=dict)
    high_risk_clauses: List[int] = field(default_factory=list)
    
    # Stage 5: Negotiation advice results
    negotiation_recommendations: List[Dict[str, str]] = field(default_factory=list)
    priority_items: List[Dict[str, str]] = field(default_factory=list)
    
    # Stage 6: Report generation metadata
    report_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processing metadata
    processing_time: float = 0.0
    total_tokens: int = 0
    pause_checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str) -> None:
        """Add an error message to the context."""
        self.errors.append(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message to the context."""
        self.warnings.append(warning)
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate a summary of the analysis results."""
        if not self.contract_document:
            return {"status": "error", "message": "No contract document parsed"}
        
        critical_issues = sum(1 for analysis in self.clause_analyses 
                            if analysis.risk_level.value == "Critical")
        material_issues = sum(1 for analysis in self.clause_analyses 
                            if analysis.risk_level.value == "Material")
        procedural_issues = sum(1 for analysis in self.clause_analyses 
                              if analysis.risk_level.value == "Procedural")
        
        return {
            "status": "completed",
            "total_clauses": len(self.clause_analyses),
            "critical_issues": critical_issues,
            "material_issues": material_issues,
            "procedural_issues": procedural_issues,
            "negotiation_items": len(self.negotiation_recommendations),
            "overall_risk_score": self.overall_risk_score,
            "processing_time": self.processing_time,
            "has_errors": len(self.errors) > 0,
            "has_warnings": len(self.warnings) > 0
        }
    
    def is_ready_for_pause_checkpoint(self, processed_clauses: int, tokens_processed: int) -> bool:
        """Check if pause checkpoint conditions are met (NEEX blueprint requirement)."""
        return (
            processed_clauses % 3 == 0 and processed_clauses > 0
        ) or tokens_processed >= 3000
    
    def should_continue_processing(self) -> bool:
        """Check if processing should continue despite errors."""
        # Stop if we have critical parsing errors
        critical_errors = [e for e in self.errors if 'parse' in e.lower() or 'file' in e.lower()]
        return len(critical_errors) == 0