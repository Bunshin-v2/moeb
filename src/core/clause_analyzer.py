"""
NEEX Legal Contract Review System  
Clause Analyzer Module

Performs AI-powered analysis of contract clauses according to NEEX blueprint:
- 3-layered analysis: Interpretation → Exposure → Opportunity
- Risk assessment and scoring
- Negotiation opportunity detection
- AI investigatory question generation
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .contract_parser import Clause
from ..ai.legal_nlp import LegalNLPProcessor
from ..ai.risk_assessor import RiskAssessor

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk assessment levels based on NEEX blueprint."""
    CRITICAL = "Critical"
    MATERIAL = "Material" 
    PROCEDURAL = "Procedural"


@dataclass
class ClauseAnalysis:
    """
    Comprehensive analysis result for a single clause.
    Based on NEEX blueprint analysis structure.
    """
    clause: Clause
    tags: List[str] = field(default_factory=list)
    
    # 3-Layered Analysis Components
    interpretation: str = ""
    exposure: str = ""
    opportunity: str = ""
    
    # Risk Assessment
    risk_level: RiskLevel = RiskLevel.PROCEDURAL
    risk_score: float = 0.0
    risk_factors: List[str] = field(default_factory=list)
    
    # AI Analysis
    key_scope_terms: List[str] = field(default_factory=list)
    legal_business_risk: str = ""
    negotiation_opportunity: str = ""
    ai_investigatory_question: str = ""
    
    # Metadata
    token_count: int = 0
    processing_time: float = 0.0


@dataclass
class AnalysisSession:
    """Tracks analysis progress and manages pause checkpoints."""
    total_clauses: int = 0
    processed_clauses: int = 0
    total_tokens: int = 0
    session_tokens: int = 0
    pause_triggers: Dict[str, int] = field(default_factory=dict)
    findings_summary: Dict[str, int] = field(default_factory=lambda: {
        'critical': 0, 'material': 0, 'procedural': 0
    })


class ClauseAnalyzer:
    """
    Main clause analysis engine implementing NEEX blueprint methodology.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize analyzer with configuration.
        
        Args:
            config_path: Path to configuration files
        """
        self.config = self._load_config(config_path)
        
        # Initialize AI components
        self.nlp_processor = LegalNLPProcessor()
        self.risk_assessor = RiskAssessor()
        
        # Analysis session state
        self.session = AnalysisSession()
        
        # Load clause patterns and definitions
        self.clause_definitions = self._load_clause_definitions()
        self.tag_patterns = self._load_tag_patterns()
        
        logger.info("ClauseAnalyzer initialized successfully")
    
    def analyze_clause(self, clause: Clause) -> ClauseAnalysis:
        """
        Perform comprehensive analysis of a single clause.
        
        Args:
            clause: Clause object to analyze
            
        Returns:
            Complete ClauseAnalysis with all components
        """
        logger.debug(f"Analyzing clause {clause.number}: {clause.title}")
        
        analysis = ClauseAnalysis(clause=clause)
        
        # Step 1: Tag Classification
        analysis.tags = self._classify_clause_tags(clause)
        
        # Step 2: Extract Key Terms
        analysis.key_scope_terms = self._extract_key_terms(clause, analysis.tags)
        
        # Step 3: 3-Layered Analysis
        analysis.interpretation = self._analyze_interpretation(clause, analysis.tags)
        analysis.exposure = self._analyze_exposure(clause, analysis.tags)
        analysis.opportunity = self._analyze_opportunity(clause, analysis.tags)
        
        # Step 4: Risk Assessment
        analysis.risk_score, analysis.risk_factors = self.risk_assessor.assess_risk(
            clause, analysis.tags
        )
        analysis.risk_level = self._determine_risk_level(analysis.risk_score)
        
        # Step 5: Legal Business Risk Analysis  
        analysis.legal_business_risk = self._analyze_legal_business_risk(
            clause, analysis.risk_factors, analysis.risk_level
        )
        
        # Step 6: Negotiation Opportunities (placeholder - will be handled by pipeline)
        analysis.negotiation_opportunity = self._analyze_opportunity(clause, analysis.tags)
        
        # Step 7: AI Investigatory Question
        analysis.ai_investigatory_question = self._generate_investigatory_question(
            clause, analysis.tags, analysis.risk_factors
        )
        
        # Update session tracking
        analysis.token_count = self._estimate_tokens(clause.content)
        self.session.processed_clauses += 1
        self.session.session_tokens += analysis.token_count
        self.session.findings_summary[analysis.risk_level.value.lower()] += 1
        
        logger.debug(f"Clause analysis complete: {analysis.risk_level.value} risk")
        return analysis
    
    def _classify_clause_tags(self, clause: Clause) -> List[str]:
        """
        Classify clause into NEEX categories: TEC/LEG/FIN/COM/IPX/TRM/DIS/DOC/EXE/EXT
        
        Args:
            clause: Clause to classify
            
        Returns:
            List of applicable tags
        """
        tags = []
        content_lower = clause.content.lower()
        title_lower = clause.title.lower()
        combined_text = f"{title_lower} {content_lower}"
        
        # Check each tag category
        for tag, patterns in self.tag_patterns.items():
            score = 0
            for pattern in patterns:
                if isinstance(pattern, str):
                    # Simple keyword matching
                    if pattern.lower() in combined_text:
                        score += 1
                else:
                    # Regex pattern matching
                    if re.search(pattern, combined_text, re.IGNORECASE):
                        score += 2
            
            # Tag threshold - adjust based on pattern strength
            if score >= 1:
                tags.append(tag)
        
        # Ensure at least one tag is assigned
        if not tags:
            # Default classification based on content characteristics
            if any(word in combined_text for word in ['payment', 'fee', 'cost']):
                tags.append('FIN')
            elif any(word in combined_text for word in ['termination', 'breach']):
                tags.append('TRM')
            elif any(word in combined_text for word in ['legal', 'jurisdiction', 'law']):
                tags.append('LEG')
            else:
                tags.append('DOC')  # Default to document control
        
        return tags
    
    def _extract_key_terms(self, clause: Clause, tags: List[str]) -> List[str]:
        """
        Extract key technical and legal terms from clause content.
        
        Args:
            clause: Clause to analyze
            tags: Assigned clause tags
            
        Returns:
            List of important terms
        """
        return self.nlp_processor.extract_key_terms(clause.content, tags)
    
    def _analyze_interpretation(self, clause: Clause, tags: List[str]) -> str:
        """
        Generate interpretation analysis: "What does this clause technically enable or control?"
        
        Args:
            clause: Clause to interpret
            tags: Clause tags for context
            
        Returns:
            Interpretation analysis text
        """
        # Use NLP processor to understand clause function
        clause_function = self.nlp_processor.analyze_clause_function(clause.content)
        
        # Build interpretation based on tags and function
        interpretation_parts = []
        
        if 'TEC' in tags:
            interpretation_parts.append(f"establishes technical requirements and deliverable specifications")
        if 'LEG' in tags:
            interpretation_parts.append(f"defines legal obligations and protective mechanisms")
        if 'FIN' in tags:
            interpretation_parts.append(f"governs financial terms and payment obligations")
        if 'IPX' in tags:
            interpretation_parts.append(f"controls intellectual property rights and ownership")
        
        if not interpretation_parts:
            interpretation_parts.append("provides contractual terms and conditions")
        
        # Extract key mechanisms
        mechanisms = self._identify_mechanisms(clause.content)
        mechanism_text = f" through {', '.join(mechanisms)}" if mechanisms else ""
        
        return f"This clause {', '.join(interpretation_parts)}{mechanism_text}. {clause_function}"
    
    def _analyze_exposure(self, clause: Clause, tags: List[str]) -> str:
        """
        Generate exposure analysis: "Where might Neex be vulnerable?"
        
        Args:
            clause: Clause to analyze
            tags: Clause tags for context
            
        Returns:
            Exposure analysis text
        """
        # Get risk factors from risk assessor
        vulnerabilities = self.risk_assessor.identify_vulnerabilities(clause.content, tags)
        
        if not vulnerabilities:
            return "No significant vulnerabilities identified in this clause."
        
        exposure_text = "Potential vulnerabilities include: " + "; ".join(vulnerabilities)
        
        # Add tag-specific exposure concerns
        tag_exposures = {
            'FIN': "financial liability and payment disputes",
            'LEG': "legal liability and enforcement challenges", 
            'TEC': "scope creep and delivery failures",
            'IPX': "intellectual property loss or disputes",
            'TRM': "unfavorable termination conditions",
            'COM': "compliance violations and regulatory risks"
        }
        
        additional_concerns = [tag_exposures[tag] for tag in tags if tag in tag_exposures]
        if additional_concerns:
            exposure_text += f". Category-specific concerns: {'; '.join(additional_concerns)}."
        
        return exposure_text
    
    def _analyze_opportunity(self, clause: Clause, tags: List[str]) -> str:
        """
        Generate opportunity analysis: "What leverage, negotiation hook, or remedy exists?"
        
        Args:
            clause: Clause to analyze  
            tags: Clause tags for context
            
        Returns:
            Opportunity analysis text
        """
        # Basic opportunity analysis - detailed analysis handled by NegotiationAdvisor in pipeline
        content_lower = clause.content.lower()
        opportunities = []
        
        if 'FIN' in tags and 'penalty' in content_lower and 'cap' not in content_lower:
            opportunities.append("Consider negotiating penalty caps")
        if 'LEG' in tags and 'liability' in content_lower and 'limit' not in content_lower:
            opportunities.append("Negotiate liability limitations")
        if 'TEC' in tags and 'deliverable' in content_lower and 'acceptance' not in content_lower:
            opportunities.append("Define clear acceptance criteria")
        
        return "; ".join(opportunities) if opportunities else "Standard commercial review recommended"
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """
        Convert numeric risk score to NEEX risk level categories.
        
        Args:
            risk_score: Numeric risk score (0-10)
            
        Returns:
            Corresponding RiskLevel enum
        """
        if risk_score >= 8.0:
            return RiskLevel.CRITICAL
        elif risk_score >= 5.0:
            return RiskLevel.MATERIAL
        else:
            return RiskLevel.PROCEDURAL
    
    def _analyze_legal_business_risk(self, clause: Clause, risk_factors: List[str], 
                                   risk_level: RiskLevel) -> str:
        """
        Generate comprehensive legal and business risk analysis.
        
        Args:
            clause: Clause being analyzed
            risk_factors: Identified risk factors
            risk_level: Determined risk level
            
        Returns:
            Legal business risk analysis text
        """
        if not risk_factors:
            return f"{risk_level.value} risk level. No specific risk factors identified."
        
        risk_text = f"{risk_level.value} risk level. Key concerns: {'; '.join(risk_factors)}."
        
        # Add business impact assessment
        business_impact = self._assess_business_impact(clause, risk_level)
        if business_impact:
            risk_text += f" Business impact: {business_impact}."
        
        return risk_text
    
    def _generate_investigatory_question(self, clause: Clause, tags: List[str], 
                                       risk_factors: List[str]) -> str:
        """
        Generate AI investigatory question based on clause analysis.
        
        Args:
            clause: Clause being analyzed
            tags: Clause tags
            risk_factors: Identified risks
            
        Returns:
            Investigatory question text
        """
        # Generate questions based on primary tag
        if 'FIN' in tags:
            return "Are the payment terms clearly defined with adequate protection against non-payment?"
        elif 'LEG' in tags:
            return "Do the legal protections adequately safeguard Neex's interests and limit liability exposure?"
        elif 'TEC' in tags:
            return "Are the technical requirements and deliverables specific enough to prevent scope disputes?"
        elif 'IPX' in tags:
            return "Does Neex retain appropriate intellectual property rights and protections?"
        elif 'TRM' in tags:
            return "Are the termination conditions balanced and do they provide adequate exit protection?"
        elif 'COM' in tags:
            return "Do the compliance requirements align with applicable regulations and industry standards?"
        else:
            return "Does this clause adequately protect Neex's interests while maintaining commercial viability?"
    
    def _identify_mechanisms(self, content: str) -> List[str]:
        """Extract mechanisms/methods from clause content."""
        mechanisms = []
        
        mechanism_patterns = [
            r'by means of ([^,\\.]+)',
            r'through ([^,\\.]+)',
            r'via ([^,\\.]+)',
            r'using ([^,\\.]+)',
            r'pursuant to ([^,\\.]+)'
        ]
        
        for pattern in mechanism_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            mechanisms.extend([match.strip() for match in matches])
        
        return mechanisms[:3]  # Limit to most relevant
    
    def _assess_business_impact(self, clause: Clause, risk_level: RiskLevel) -> str:
        """Assess potential business impact of the clause."""
        if risk_level == RiskLevel.CRITICAL:
            return "potential for significant financial or operational disruption"
        elif risk_level == RiskLevel.MATERIAL:
            return "moderate business risk requiring attention"
        else:
            return "limited business impact"
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        return len(text.split()) + len(text) // 4  # Words + characters/4
    
    def check_pause_conditions(self) -> Dict[str, bool]:
        """
        Check if any pause conditions are met based on NEEX blueprint.
        
        Returns:
            Dict indicating which pause conditions are triggered
        """
        conditions = {
            'clause_count': self.session.processed_clauses % 3 == 0 and self.session.processed_clauses > 0,
            'token_count': self.session.session_tokens >= 3000,
            'section_boundary': False  # Would need section detection logic
        }
        
        return conditions
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML files."""
        # TODO: Implement YAML config loading
        return {}
    
    def _load_clause_definitions(self) -> Dict:
        """Load clause definitions from config."""
        # TODO: Load from clause_definitions.yaml
        return {}
    
    def _load_tag_patterns(self) -> Dict[str, List[str]]:
        """Load tag classification patterns."""
        # Based on clause_definitions.yaml patterns
        return {
            'TEC': ['deliverable', 'milestone', 'SLA', 'service level', 'uptime', 'performance'],
            'LEG': ['jurisdiction', 'governing law', 'indemnif', 'liability', 'breach', 'warranty'],
            'FIN': ['payment', 'invoice', 'fee', 'cost', 'penalty', 'refund', 'currency'],
            'COM': ['compliance', 'regulation', 'license', 'AML', 'GDPR', 'privacy'],
            'IPX': ['intellectual property', 'copyright', 'license', 'ownership', 'exclusive'],
            'TRM': ['termination', 'breach', 'default', 'cure period', 'notice'],
            'DIS': ['dispute', 'arbitration', 'mediation', 'jurisdiction', 'venue'],
            'DOC': ['document', 'annex', 'amendment', 'modification', 'version'],
            'EXE': ['signature', 'execution', 'authority', 'effective date'],
            'EXT': ['external', 'third party', 'vendor', 'dependency']
        }


def main():
    """Example usage of ClauseAnalyzer."""
    from .contract_parser import Clause
    
    analyzer = ClauseAnalyzer()
    
    # Example clause
    sample_clause = Clause(
        number=1,
        title="Payment Terms",
        content="Payment shall be made within 30 days of invoice receipt. Late payments incur 2% monthly penalty."
    )
    
    analysis = analyzer.analyze_clause(sample_clause)
    
    print(f"Clause: {analysis.clause.title}")
    print(f"Tags: {analysis.tags}")
    print(f"Risk Level: {analysis.risk_level.value}")
    print(f"Interpretation: {analysis.interpretation}")
    print(f"Opportunity: {analysis.negotiation_opportunity}")
    print(f"Question: {analysis.ai_investigatory_question}")


if __name__ == "__main__":
    main()
