"""
NEEX Legal Contract Review System
Risk Assessor Module

Evaluates legal and business risks in contract clauses.
Provides risk scoring, vulnerability identification, and risk factor analysis.
"""

import logging
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RiskCategory(Enum):
    """Categories of contract risks."""
    FINANCIAL = "Financial"
    LEGAL = "Legal"
    OPERATIONAL = "Operational"
    COMPLIANCE = "Compliance"
    REPUTATIONAL = "Reputational"
    STRATEGIC = "Strategic"


@dataclass
class RiskFactor:
    """Individual risk factor with metadata."""
    category: RiskCategory
    description: str
    severity: float  # 0-10 scale
    likelihood: float  # 0-1 probability
    impact: str
    mitigation: Optional[str] = None


@dataclass
class RiskAssessment:
    """Complete risk assessment for a clause."""
    overall_score: float
    primary_risks: List[RiskFactor]
    vulnerabilities: List[str]
    risk_distribution: Dict[RiskCategory, float]
    recommendations: List[str]


class RiskAssessor:
    """
    AI-powered risk assessment engine for legal contract clauses.
    Analyzes various risk dimensions and provides quantitative scoring.
    """
    
    def __init__(self):
        """Initialize risk assessor with risk patterns and scoring matrices."""
        self.risk_patterns = self._build_risk_patterns()
        self.vulnerability_indicators = self._build_vulnerability_indicators()
        self.risk_weights = self._build_risk_weights()
        self.mitigation_strategies = self._build_mitigation_strategies()
        
        logger.info("RiskAssessor initialized")
    
    def assess_risk(self, clause, tags: List[str]) -> Tuple[float, List[str]]:
        """
        Perform comprehensive risk assessment of a clause.
        
        Args:
            clause: Clause object to assess
            tags: Clause classification tags
            
        Returns:
            Tuple of (risk_score, risk_factors_list)
        """
        assessment = self._perform_full_assessment(clause.content, tags)
        
        # Extract risk factors as strings for backward compatibility
        risk_factors = [f"{rf.category.value}: {rf.description}" for rf in assessment.primary_risks]
        
        logger.debug(f"Risk assessment complete: {assessment.overall_score:.2f}")
        return assessment.overall_score, risk_factors
    
    def identify_vulnerabilities(self, content: str, tags: List[str]) -> List[str]:
        """
        Identify specific vulnerabilities in clause content.
        
        Args:
            content: Clause text content
            tags: Clause classification tags
            
        Returns:
            List of identified vulnerabilities
        """
        vulnerabilities = []
        content_lower = content.lower()
        
        # Check each vulnerability category
        for category, indicators in self.vulnerability_indicators.items():
            for indicator in indicators:
                if isinstance(indicator, str):
                    if indicator.lower() in content_lower:
                        vulnerabilities.append(f"{category}: {indicator}")
                else:  # regex pattern
                    if re.search(indicator, content, re.IGNORECASE):
                        vulnerabilities.append(f"{category}: pattern match")
        
        # Tag-specific vulnerability checks
        tag_specific = self._check_tag_specific_vulnerabilities(content, tags)
        vulnerabilities.extend(tag_specific)
        
        return list(set(vulnerabilities))  # Remove duplicates
    
    def _perform_full_assessment(self, content: str, tags: List[str]) -> RiskAssessment:
        """Perform comprehensive risk assessment."""
        risk_factors = []
        content_lower = content.lower()
        
        # Analyze each risk category
        for category in RiskCategory:
            category_risks = self._assess_category_risk(content, category, tags)
            risk_factors.extend(category_risks)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(risk_factors)
        
        # Get primary risks (top severity)
        primary_risks = sorted(risk_factors, key=lambda x: x.severity, reverse=True)[:5]
        
        # Calculate risk distribution
        risk_distribution = self._calculate_risk_distribution(risk_factors)
        
        # Generate vulnerabilities
        vulnerabilities = self.identify_vulnerabilities(content, tags)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(primary_risks, tags)
        
        return RiskAssessment(
            overall_score=overall_score,
            primary_risks=primary_risks,
            vulnerabilities=vulnerabilities,
            risk_distribution=risk_distribution,
            recommendations=recommendations
        )
    
    def _assess_category_risk(self, content: str, category: RiskCategory, tags: List[str]) -> List[RiskFactor]:
        """Assess risks for a specific category."""
        risks = []
        
        if category == RiskCategory.FINANCIAL:
            risks.extend(self._assess_financial_risks(content, tags))
        elif category == RiskCategory.LEGAL:
            risks.extend(self._assess_legal_risks(content, tags))
        elif category == RiskCategory.OPERATIONAL:
            risks.extend(self._assess_operational_risks(content, tags))
        elif category == RiskCategory.COMPLIANCE:
            risks.extend(self._assess_compliance_risks(content, tags))
        elif category == RiskCategory.REPUTATIONAL:
            risks.extend(self._assess_reputational_risks(content, tags))
        elif category == RiskCategory.STRATEGIC:
            risks.extend(self._assess_strategic_risks(content, tags))
        
        return risks
    
    def _assess_financial_risks(self, content: str, tags: List[str]) -> List[RiskFactor]:
        """Assess financial risks in clause content."""
        risks = []
        content_lower = content.lower()
        
        # Payment delay risks
        if 'payment' in content_lower and ('penalty' not in content_lower or 'interest' not in content_lower):
            risks.append(RiskFactor(
                category=RiskCategory.FINANCIAL,
                description="Payment terms lack penalty provisions for late payment",
                severity=6.0,
                likelihood=0.3,
                impact="Potential cash flow issues and collection difficulties"
            ))
        
        # Unlimited liability exposure
        if 'liable' in content_lower and 'limit' not in content_lower:
            risks.append(RiskFactor(
                category=RiskCategory.FINANCIAL,
                description="Unlimited liability exposure without caps",
                severity=8.0,
                likelihood=0.2,
                impact="Potentially catastrophic financial exposure"
            ))
        
        # Currency risk
        if any(curr in content_lower for curr in ['currency', 'exchange', 'usd', 'eur']):
            if 'hedg' not in content_lower and 'fix' not in content_lower:
                risks.append(RiskFactor(
                    category=RiskCategory.FINANCIAL,
                    description="Currency exchange rate risk without hedging",
                    severity=5.0,
                    likelihood=0.4,
                    impact="Potential financial losses from rate fluctuations"
                ))
        
        # Penalty assessment
        penalty_match = re.search(r'(\\d+)%.*penalty', content_lower)
        if penalty_match:
            penalty_rate = float(penalty_match.group(1))
            if penalty_rate > 5:
                risks.append(RiskFactor(
                    category=RiskCategory.FINANCIAL,
                    description=f"High penalty rate of {penalty_rate}% may be excessive",
                    severity=7.0,
                    likelihood=0.3,
                    impact="Disproportionate financial penalties"
                ))
        
        return risks
    
    def _assess_legal_risks(self, content: str, tags: List[str]) -> List[RiskFactor]:
        """Assess legal risks in clause content."""
        risks = []
        content_lower = content.lower()
        
        # Jurisdiction issues
        if 'jurisdiction' in content_lower:
            unfavorable_jurisdictions = ['foreign', 'offshore', 'international arbitration']
            if any(unfav in content_lower for unfav in unfavorable_jurisdictions):
                risks.append(RiskFactor(
                    category=RiskCategory.LEGAL,
                    description="Potentially unfavorable jurisdiction for dispute resolution",
                    severity=7.0,
                    likelihood=0.2,
                    impact="Increased legal costs and procedural disadvantages"
                ))
        
        # Indemnification gaps
        if 'indemnif' in content_lower:
            if 'mutual' not in content_lower and 'reciprocal' not in content_lower:
                risks.append(RiskFactor(
                    category=RiskCategory.LEGAL,
                    description="One-sided indemnification obligations",
                    severity=6.5,
                    likelihood=0.3,
                    impact="Asymmetric legal protection and liability exposure"
                ))
        
        # Broad warranty language
        if any(term in content_lower for term in ['warrant', 'guarantee']) and 'disclaim' not in content_lower:
            risks.append(RiskFactor(
                category=RiskCategory.LEGAL,
                description="Broad warranty obligations without disclaimers",
                severity=5.5,
                likelihood=0.4,
                impact="Potential warranty claims and associated costs"
            ))
        
        # Termination imbalance
        if 'terminat' in content_lower:
            if 'convenience' in content_lower and 'cure' not in content_lower:
                risks.append(RiskFactor(
                    category=RiskCategory.LEGAL,
                    description="Termination for convenience without cure period",
                    severity=6.0,
                    likelihood=0.25,
                    impact="Risk of abrupt contract termination"
                ))
        
        return risks
    
    def _assess_operational_risks(self, content: str, tags: List[str]) -> List[RiskFactor]:
        """Assess operational risks in clause content."""
        risks = []
        content_lower = content.lower()
        
        # Unrealistic timelines
        timeline_patterns = [
            (r'(\\d+)\\s*days?', 'days'),
            (r'(\\d+)\\s*hours?', 'hours'),
            (r'(\\d+)\\s*weeks?', 'weeks')
        ]
        
        for pattern, unit in timeline_patterns:
            matches = re.findall(pattern, content_lower)
            for match in matches:
                days = int(match)
                if unit == 'hours':
                    days = days / 24
                elif unit == 'weeks':
                    days = days * 7
                
                if days < 3:  # Very tight timeline
                    risks.append(RiskFactor(
                        category=RiskCategory.OPERATIONAL,
                        description=f"Tight timeline of {match} {unit} may be unrealistic",
                        severity=5.0,
                        likelihood=0.5,
                        impact="Risk of delivery delays and penalty exposure"
                    ))
        
        # Scope definition issues
        if 'deliverable' in content_lower and 'specific' not in content_lower:
            risks.append(RiskFactor(
                category=RiskCategory.OPERATIONAL,
                description="Vague deliverable specifications may lead to scope disputes",
                severity=6.0,
                likelihood=0.4,
                impact="Scope creep and delivery disagreements"
            ))
        
        # Dependency risks
        if 'depend' in content_lower or 'third party' in content_lower:
            risks.append(RiskFactor(
                category=RiskCategory.OPERATIONAL,
                description="Third-party dependencies create operational risks",
                severity=4.5,
                likelihood=0.3,
                impact="Potential delays due to external factors"
            ))
        
        return risks
    
    def _assess_compliance_risks(self, content: str, tags: List[str]) -> List[RiskFactor]:
        """Assess compliance risks in clause content."""
        risks = []
        content_lower = content.lower()
        
        # Regulatory compliance gaps
        if any(reg in content_lower for reg in ['regulation', 'compliance', 'law']) and 'current' not in content_lower:
            risks.append(RiskFactor(
                category=RiskCategory.COMPLIANCE,
                description="Compliance obligations may not reflect current regulations",
                severity=6.5,
                likelihood=0.3,
                impact="Regulatory violations and associated penalties"
            ))
        
        # Data protection issues
        if 'data' in content_lower and 'gdpr' not in content_lower and 'privacy' not in content_lower:
            risks.append(RiskFactor(
                category=RiskCategory.COMPLIANCE,
                description="Data handling without explicit privacy protections",
                severity=7.0,
                likelihood=0.4,
                impact="Privacy violations and regulatory fines"
            ))
        
        # AML/CTF compliance
        if any(fin in content_lower for fin in ['payment', 'financial', 'money']) and 'aml' not in content_lower:
            risks.append(RiskFactor(
                category=RiskCategory.COMPLIANCE,
                description="Financial operations without AML/CTF compliance measures",
                severity=5.5,
                likelihood=0.2,
                impact="Anti-money laundering compliance issues"
            ))
        
        return risks
    
    def _assess_reputational_risks(self, content: str, tags: List[str]) -> List[RiskFactor]:
        """Assess reputational risks in clause content."""
        risks = []
        content_lower = content.lower()
        
        # Public disclosure risks
        if 'public' in content_lower or 'disclosure' in content_lower:
            if 'confidential' not in content_lower:
                risks.append(RiskFactor(
                    category=RiskCategory.REPUTATIONAL,
                    description="Public disclosure without confidentiality protections",
                    severity=5.0,
                    likelihood=0.3,
                    impact="Potential reputation damage from public exposure"
                ))
        
        # Quality standards
        if 'quality' in content_lower and 'standard' not in content_lower:
            risks.append(RiskFactor(
                category=RiskCategory.REPUTATIONAL,
                description="Quality expectations without defined standards",
                severity=4.0,
                likelihood=0.4,
                impact="Risk of quality disputes affecting reputation"
            ))
        
        return risks
    
    def _assess_strategic_risks(self, content: str, tags: List[str]) -> List[RiskFactor]:
        """Assess strategic risks in clause content."""
        risks = []
        content_lower = content.lower()
        
        # IP strategy risks
        if 'intellectual property' in content_lower or 'copyright' in content_lower:
            if 'license back' not in content_lower and 'retain' not in content_lower:
                risks.append(RiskFactor(
                    category=RiskCategory.STRATEGIC,
                    description="IP transfer without license-back rights",
                    severity=7.5,
                    likelihood=0.2,
                    impact="Loss of strategic IP assets and future licensing opportunities"
                ))
        
        # Exclusivity concerns
        if 'exclusive' in content_lower and 'term' not in content_lower:
            risks.append(RiskFactor(
                category=RiskCategory.STRATEGIC,
                description="Indefinite exclusivity arrangements",
                severity=6.0,
                likelihood=0.25,
                impact="Strategic flexibility limitations"
            ))
        
        return risks
    
    def _check_tag_specific_vulnerabilities(self, content: str, tags: List[str]) -> List[str]:
        """Check for vulnerabilities specific to clause tags."""
        vulnerabilities = []
        content_lower = content.lower()
        
        if 'FIN' in tags:
            if 'payment' in content_lower and 'escrow' not in content_lower:
                vulnerabilities.append("Financial: No escrow protection for payments")
            if 'penalty' in content_lower and 'cap' not in content_lower:
                vulnerabilities.append("Financial: Uncapped penalty exposure")
        
        if 'TEC' in tags:
            if 'sla' in content_lower and 'remedy' not in content_lower:
                vulnerabilities.append("Technical: SLA without enforcement remedies")
            if 'deliverable' in content_lower and 'acceptance' not in content_lower:
                vulnerabilities.append("Technical: No formal acceptance criteria")
        
        if 'LEG' in tags:
            if 'liability' in content_lower and 'insurance' not in content_lower:
                vulnerabilities.append("Legal: Liability exposure without insurance requirements")
        
        return vulnerabilities
    
    def _calculate_overall_score(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate overall risk score from individual factors."""
        if not risk_factors:
            return 1.0  # Minimal risk baseline
        
        # Weight by severity and likelihood
        weighted_scores = []
        for factor in risk_factors:
            weighted_score = factor.severity * factor.likelihood
            category_weight = self.risk_weights.get(factor.category, 1.0)
            weighted_scores.append(weighted_score * category_weight)
        
        # Aggregate using root mean square to avoid overweighting
        total_score = (sum(score ** 2 for score in weighted_scores) / len(weighted_scores)) ** 0.5
        return min(total_score, 10.0)  # Cap at 10
    
    def _calculate_risk_distribution(self, risk_factors: List[RiskFactor]) -> Dict[RiskCategory, float]:
        """Calculate risk distribution across categories."""
        distribution = {category: 0.0 for category in RiskCategory}
        
        if not risk_factors:
            return distribution
        
        category_scores = {}
        for factor in risk_factors:
            if factor.category not in category_scores:
                category_scores[factor.category] = []
            category_scores[factor.category].append(factor.severity * factor.likelihood)
        
        for category, scores in category_scores.items():
            distribution[category] = sum(scores) / len(scores)
        
        return distribution
    
    def _generate_recommendations(self, primary_risks: List[RiskFactor], tags: List[str]) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        for risk in primary_risks[:3]:  # Top 3 risks
            if risk.category in self.mitigation_strategies:
                strategy = self.mitigation_strategies[risk.category].get(
                    risk.description, "Review and address this risk factor"
                )
                recommendations.append(f"{risk.category.value}: {strategy}")
        
        # Tag-specific recommendations
        if 'FIN' in tags:
            recommendations.append("Financial: Consider adding payment security mechanisms")
        if 'LEG' in tags:
            recommendations.append("Legal: Review indemnification and liability provisions")
        
        return recommendations
    
    def _build_risk_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for risk detection."""
        return {
            'high_risk_terms': [
                'unlimited liability', 'personal guarantee', 'joint and several',
                'in perpetuity', 'irrevocable', 'unconditional'
            ],
            'financial_risks': [
                'penalty', 'liquidated damages', 'late fee', 'interest',
                'collection costs', 'attorney fees'
            ],
            'legal_risks': [
                'indemnification', 'hold harmless', 'breach', 'default',
                'termination', 'injunctive relief'
            ]
        }
    
    def _build_vulnerability_indicators(self) -> Dict[str, List[str]]:
        """Build indicators for vulnerability detection."""
        return {
            'asymmetric_terms': [
                'solely responsible', 'exclusively liable', 'bears all costs',
                'at own expense', 'without recourse'
            ],
            'vague_language': [
                'reasonable efforts', 'best efforts', 'commercially reasonable',
                'appropriate measures', 'satisfactory performance'
            ],
            'missing_protections': [
                'without warranty', 'as is', 'no guarantee',
                'disclaim all liability', 'exclude all warranties'
            ]
        }
    
    def _build_risk_weights(self) -> Dict[RiskCategory, float]:
        """Build weighting factors for different risk categories."""
        return {
            RiskCategory.FINANCIAL: 1.2,
            RiskCategory.LEGAL: 1.1,
            RiskCategory.OPERATIONAL: 0.9,
            RiskCategory.COMPLIANCE: 1.0,
            RiskCategory.REPUTATIONAL: 0.8,
            RiskCategory.STRATEGIC: 1.0
        }
    
    def _build_mitigation_strategies(self) -> Dict[RiskCategory, Dict[str, str]]:
        """Build mitigation strategies for common risks."""
        return {
            RiskCategory.FINANCIAL: {
                "Payment terms lack penalty provisions": "Add late payment penalties and interest charges",
                "Unlimited liability exposure": "Insert liability caps and limitations",
                "Currency exchange rate risk": "Include currency hedging or fixed rate provisions"
            },
            RiskCategory.LEGAL: {
                "One-sided indemnification": "Negotiate mutual indemnification provisions",
                "Unfavorable jurisdiction": "Seek neutral jurisdiction or alternative dispute resolution",
                "Broad warranty obligations": "Add warranty disclaimers and limitations"
            },
            RiskCategory.OPERATIONAL: {
                "Tight timeline": "Request realistic deadlines with force majeure protection",
                "Vague deliverable specifications": "Demand detailed specifications and acceptance criteria"
            }
        }


def main():
    """Example usage of RiskAssessor."""
    from ..core.contract_parser import Clause
    
    assessor = RiskAssessor()
    
    # Example high-risk clause
    sample_clause = Clause(
        number=5,
        title="Liability and Indemnification",
        content="Provider shall indemnify and hold harmless Client from all claims and shall be solely responsible for unlimited damages arising from any breach."
    )
    
    risk_score, risk_factors = assessor.assess_risk(sample_clause, ['LEG', 'FIN'])
    vulnerabilities = assessor.identify_vulnerabilities(sample_clause.content, ['LEG', 'FIN'])
    
    print(f"Risk Score: {risk_score:.2f}/10")
    print(f"Risk Factors: {risk_factors}")
    print(f"Vulnerabilities: {vulnerabilities}")


if __name__ == "__main__":
    main()
