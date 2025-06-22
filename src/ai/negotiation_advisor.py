"""
NEEX Legal Contract Review System
Negotiation Advisor Module

Rule-based system for generating negotiation recommendations based on clause analysis.
Provides actionable advice for contract improvements and risk mitigation.
"""

import logging
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..core.clause_analyzer import ClauseAnalysis, RiskLevel


logger = logging.getLogger(__name__)


@dataclass
class NegotiationRecommendation:
    """Represents a specific negotiation recommendation."""
    clause_number: int
    clause_title: str
    priority: str  # "Critical", "High", "Medium", "Low"
    recommendation_type: str  # "redline", "addition", "deletion", "clarification"
    current_text: str
    suggested_change: str
    rationale: str
    negotiation_strategy: str


@dataclass
class NegotiationRule:
    """Represents a rule for generating negotiation advice."""
    name: str
    conditions: Dict[str, Any]
    recommendation_template: Dict[str, str]
    priority: str


class NegotiationAdvisor:
    """
    AI-powered negotiation advisor that analyzes contract clauses and
    provides specific, actionable recommendations for contract improvements.
    """
    
    def __init__(self, rules_path: Optional[Path] = None):
        """
        Initialize the negotiation advisor with rule sets.
        
        Args:
            rules_path: Optional path to custom rules file
        """
        self.logger = logging.getLogger(__name__)
        self.rules: List[NegotiationRule] = []
        
        # Load negotiation rules
        if rules_path and rules_path.exists():
            self._load_rules_from_file(rules_path)
        else:
            self._load_default_rules()
        
        self.logger.info(f"NegotiationAdvisor initialized with {len(self.rules)} rules")
    
    def identify_opportunities(
        self, 
        clause, 
        tags: List[str], 
        risk_level: RiskLevel
    ) -> str:
        """
        Identify negotiation opportunities for a specific clause.
        
        Args:
            clause: Clause object being analyzed
            tags: List of clause tags (TEC, LEG, FIN, etc.)
            risk_level: Assessed risk level
            
        Returns:
            Negotiation opportunity description
        """
        opportunities = []
        
        # Apply rules to identify opportunities
        for rule in self.rules:
            if self._rule_applies(rule, clause, tags, risk_level):
                opportunity = self._generate_opportunity_text(rule, clause, tags, risk_level)
                opportunities.append(opportunity)
        
        if not opportunities:
            return "No specific negotiation opportunities identified for this clause."
        
        return " ".join(opportunities)
    
    def analyze_opportunities(self, content: str, tags: List[str]) -> str:
        """
        Analyze general negotiation opportunities in clause content.
        
        Args:
            content: Clause text content
            tags: Clause classification tags
            
        Returns:
            Negotiation opportunity analysis
        """
        content_lower = content.lower()
        opportunities = []
        
        # Financial opportunities
        if 'FIN' in tags:
            if 'penalty' in content_lower and 'cap' not in content_lower:
                opportunities.append("Consider negotiating penalty caps to limit financial exposure")
            if 'payment' in content_lower and 'escrow' not in content_lower:
                opportunities.append("Explore escrow arrangements for payment security")
            if 'late' in content_lower and 'cure' not in content_lower:
                opportunities.append("Request cure period before late payment penalties apply")
        
        # Legal opportunities
        if 'LEG' in tags:
            if 'indemnif' in content_lower and 'mutual' not in content_lower:
                opportunities.append("Push for mutual indemnification to balance liability")
            if 'liability' in content_lower and 'limit' not in content_lower:
                opportunities.append("Negotiate liability limitations and caps")
            if 'jurisdiction' in content_lower:
                opportunities.append("Evaluate jurisdiction for favorability and convenience")
        
        # Technical opportunities
        if 'TEC' in tags:
            if 'deliverable' in content_lower and 'acceptance' not in content_lower:
                opportunities.append("Define clear acceptance criteria for deliverables")
            if 'sla' in content_lower and 'remedy' not in content_lower:
                opportunities.append("Include specific remedies for SLA breaches")
        
        # Termination opportunities
        if 'TRM' in tags:
            if 'terminat' in content_lower and 'cure' not in content_lower:
                opportunities.append("Negotiate cure periods before termination rights activate")
            if 'convenience' in content_lower:
                opportunities.append("Seek reciprocal termination rights or notice periods")
        
        if not opportunities:
            return "Consider standard commercial protections and balanced risk allocation."
        
        return "; ".join(opportunities) + "."
    
    def generate_recommendations(
        self, 
        clause_analyses: List[ClauseAnalysis]
    ) -> List[NegotiationRecommendation]:
        """
        Generate comprehensive negotiation recommendations for all analyzed clauses.
        
        Args:
            clause_analyses: List of completed clause analyses
            
        Returns:
            List of prioritized negotiation recommendations
        """
        recommendations = []
        
        for analysis in clause_analyses:
            clause_recommendations = self._generate_clause_recommendations(analysis)
            recommendations.extend(clause_recommendations)
        
        # Sort by priority (Critical -> High -> Medium -> Low)
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 4))
        
        return recommendations
    
    def _generate_clause_recommendations(
        self, 
        analysis: ClauseAnalysis
    ) -> List[NegotiationRecommendation]:
        """Generate recommendations for a single clause analysis."""
        recommendations = []
        
        # Apply each rule to the clause
        for rule in self.rules:
            if self._rule_applies_to_analysis(rule, analysis):
                rec = self._create_recommendation_from_rule(rule, analysis)
                if rec:
                    recommendations.append(rec)
        
        return recommendations
    
    def _rule_applies(
        self, 
        rule: NegotiationRule, 
        clause, 
        tags: List[str], 
        risk_level: RiskLevel
    ) -> bool:
        """Check if a rule applies to the given clause context."""
        conditions = rule.conditions
        
        # Check risk level condition
        if 'risk_level' in conditions:
            required_risk = conditions['risk_level']
            if risk_level.value != required_risk:
                return False
        
        # Check tag conditions
        if 'tags' in conditions:
            required_tags = conditions['tags']
            if isinstance(required_tags, str):
                required_tags = [required_tags]
            if not any(tag in tags for tag in required_tags):
                return False
        
        # Check content conditions
        if 'content_contains' in conditions:
            content_checks = conditions['content_contains']
            if isinstance(content_checks, str):
                content_checks = [content_checks]
            content_lower = clause.content.lower()
            if not any(check.lower() in content_lower for check in content_checks):
                return False
        
        # Check content absence conditions
        if 'content_lacks' in conditions:
            content_lacks = conditions['content_lacks']
            if isinstance(content_lacks, str):
                content_lacks = [content_lacks]
            content_lower = clause.content.lower()
            if any(lack.lower() in content_lower for lack in content_lacks):
                return False
        
        return True
    
    def _rule_applies_to_analysis(self, rule: NegotiationRule, analysis: ClauseAnalysis) -> bool:
        """Check if a rule applies to a clause analysis."""
        return self._rule_applies(rule, analysis.clause, analysis.tags, analysis.risk_level)
    
    def _generate_opportunity_text(
        self, 
        rule: NegotiationRule, 
        clause, 
        tags: List[str], 
        risk_level: RiskLevel
    ) -> str:
        """Generate opportunity text from a rule template."""
        template = rule.recommendation_template.get('opportunity', '')
        
        # Simple template substitution
        return template.format(
            clause_title=clause.title,
            risk_level=risk_level.value,
            tags=', '.join(tags)
        )
    
    def _create_recommendation_from_rule(
        self, 
        rule: NegotiationRule, 
        analysis: ClauseAnalysis
    ) -> Optional[NegotiationRecommendation]:
        """Create a negotiation recommendation from a rule and analysis."""
        template = rule.recommendation_template
        
        return NegotiationRecommendation(
            clause_number=analysis.clause.number,
            clause_title=analysis.clause.title,
            priority=rule.priority,
            recommendation_type=template.get('type', 'clarification'),
            current_text=analysis.clause.content[:200] + "..." if len(analysis.clause.content) > 200 else analysis.clause.content,
            suggested_change=template.get('suggested_change', 'Review and clarify this clause'),
            rationale=template.get('rationale', f"Address {analysis.risk_level.value.lower()} risk factors"),
            negotiation_strategy=template.get('strategy', 'Discuss with legal counsel')
        )
    
    def _load_rules_from_file(self, rules_path: Path) -> None:
        """Load negotiation rules from YAML file."""
        try:
            with open(rules_path, 'r') as f:
                rules_data = yaml.safe_load(f)
            
            for rule_data in rules_data.get('negotiation_rules', []):
                rule = NegotiationRule(
                    name=rule_data['name'],
                    conditions=rule_data['conditions'],
                    recommendation_template=rule_data['recommendation'],
                    priority=rule_data.get('priority', 'Medium')
                )
                self.rules.append(rule)
                
        except Exception as e:
            self.logger.error(f"Failed to load rules from {rules_path}: {e}")
            self._load_default_rules()
    
    def _load_default_rules(self) -> None:
        """Load default negotiation rules."""
        default_rules = [
            NegotiationRule(
                name="High Financial Risk",
                conditions={
                    'risk_level': 'Critical',
                    'tags': ['FIN']
                },
                recommendation_template={
                    'type': 'redline',
                    'opportunity': 'Critical financial risk requires immediate attention and likely redlining',
                    'suggested_change': 'Add liability caps, penalty limitations, and payment protections',
                    'rationale': 'Excessive financial exposure poses significant business risk',
                    'strategy': 'Demand material revisions or consider contract rejection'
                },
                priority='Critical'
            ),
            NegotiationRule(
                name="Unlimited Liability",
                conditions={
                    'content_contains': ['liable', 'liability'],
                    'content_lacks': ['limit', 'cap']
                },
                recommendation_template={
                    'type': 'addition',
                    'opportunity': 'Unlimited liability exposure should be capped',
                    'suggested_change': 'Add liability limitations clause capping damages',
                    'rationale': 'Unlimited liability creates unacceptable business risk',
                    'strategy': 'Negotiate specific dollar amount caps or limit to contract value'
                },
                priority='High'
            ),
            NegotiationRule(
                name="One-sided Indemnification",
                conditions={
                    'content_contains': ['indemnif'],
                    'content_lacks': ['mutual', 'reciprocal']
                },
                recommendation_template={
                    'type': 'redline',
                    'opportunity': 'One-sided indemnification should be made mutual',
                    'suggested_change': 'Revise to mutual indemnification provisions',
                    'rationale': 'Asymmetric indemnification creates unfair risk allocation',
                    'strategy': 'Push for balanced mutual protections'
                },
                priority='High'
            ),
            NegotiationRule(
                name="Vague Deliverables",
                conditions={
                    'tags': ['TEC'],
                    'content_contains': ['deliverable'],
                    'content_lacks': ['specific', 'criteria']
                },
                recommendation_template={
                    'type': 'clarification',
                    'opportunity': 'Deliverable specifications need clarification to prevent disputes',
                    'suggested_change': 'Add detailed acceptance criteria and specifications',
                    'rationale': 'Vague deliverables lead to scope disputes and project delays',
                    'strategy': 'Define clear, measurable deliverable requirements'
                },
                priority='Medium'
            ),
            NegotiationRule(
                name="Missing Cure Period",
                conditions={
                    'tags': ['TRM'],
                    'content_contains': ['breach', 'default', 'terminat'],
                    'content_lacks': ['cure', 'remedy']
                },
                recommendation_template={
                    'type': 'addition',
                    'opportunity': 'Add cure period before termination or penalty application',
                    'suggested_change': 'Include reasonable cure period (e.g., 30 days written notice)',
                    'rationale': 'Cure periods provide opportunity to address issues before severe consequences',
                    'strategy': 'Negotiate fair notice and cure provisions'
                },
                priority='Medium'
            )
        ]
        
        self.rules.extend(default_rules)
        self.logger.info(f"Loaded {len(default_rules)} default negotiation rules")