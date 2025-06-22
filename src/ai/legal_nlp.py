"""
NEEX Legal Contract Review System
Legal NLP Processor Module

Provides natural language processing capabilities specialized for legal text analysis.
Handles key term extraction, clause function analysis, and legal pattern recognition.
"""

import re
import logging
from typing import List, Dict, Set, Tuple, Optional
from collections import Counter
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LegalEntity:
    """Represents a legal entity or concept extracted from text."""
    text: str
    category: str
    confidence: float
    start_pos: int
    end_pos: int


@dataclass
class ClauseFunction:
    """Represents the identified function/purpose of a clause."""
    primary_function: str
    secondary_functions: List[str]
    confidence: float
    indicators: List[str]


class LegalNLPProcessor:
    """
    Natural Language Processing engine for legal contract analysis.
    Specialized for legal terminology and contract structure.
    """
    
    def __init__(self):
        """Initialize the legal NLP processor with patterns and vocabularies."""
        self.legal_vocabulary = self._build_legal_vocabulary()
        self.action_patterns = self._build_action_patterns()
        self.obligation_patterns = self._build_obligation_patterns()
        self.conditional_patterns = self._build_conditional_patterns()
        self.temporal_patterns = self._build_temporal_patterns()
        
        logger.info("LegalNLPProcessor initialized")
    
    def extract_key_terms(self, text: str, context_tags: List[str] = None) -> List[str]:
        """
        Extract key legal and technical terms from clause text.
        
        Args:
            text: Clause content to analyze
            context_tags: Context tags (TEC, LEG, FIN, etc.) to guide extraction
            
        Returns:
            List of important terms, ranked by relevance
        """
        # Normalize text
        text_clean = self._clean_text(text)
        
        # Extract different types of terms
        legal_terms = self._extract_legal_terms(text_clean)
        technical_terms = self._extract_technical_terms(text_clean, context_tags)
        financial_terms = self._extract_financial_terms(text_clean)
        temporal_terms = self._extract_temporal_terms(text_clean)
        
        # Combine and rank terms
        all_terms = legal_terms + technical_terms + financial_terms + temporal_terms
        
        # Remove duplicates and rank by importance
        term_scores = self._score_terms(all_terms, text_clean, context_tags)
        
        # Return top terms
        ranked_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)
        return [term for term, score in ranked_terms[:10]]
    
    def analyze_clause_function(self, text: str) -> str:
        """
        Analyze and describe the primary function of a clause.
        
        Args:
            text: Clause content
            
        Returns:
            Description of clause function and purpose
        """
        function = self._identify_clause_function(text)
        
        if function.confidence > 0.7:
            return f"Primary function: {function.primary_function}. {self._generate_function_description(function)}"
        else:
            return f"Appears to {function.primary_function}. Additional analysis may be needed for clarity."
    
    def extract_obligations(self, text: str) -> List[Dict[str, str]]:
        """
        Extract obligations and responsibilities from clause text.
        
        Args:
            text: Clause content
            
        Returns:
            List of obligations with party assignments
        """
        obligations = []
        
        for pattern_name, pattern in self.obligation_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                obligation = {
                    'type': pattern_name,
                    'text': match.group(0),
                    'party': self._identify_obligated_party(match.group(0)),
                    'action': self._extract_action(match.group(0))
                }
                obligations.append(obligation)
        
        return obligations
    
    def extract_conditions(self, text: str) -> List[Dict[str, str]]:
        """
        Extract conditional statements and trigger conditions.
        
        Args:
            text: Clause content
            
        Returns:
            List of conditions with triggers and consequences
        """
        conditions = []
        
        for pattern in self.conditional_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                condition = {
                    'trigger': match.group(1) if match.groups() else match.group(0),
                    'consequence': self._extract_consequence(match.group(0), text),
                    'type': self._classify_condition_type(match.group(0))
                }
                conditions.append(condition)
        
        return conditions
    
    def extract_temporal_elements(self, text: str) -> List[Dict[str, str]]:
        """
        Extract time-related elements (deadlines, durations, schedules).
        
        Args:
            text: Clause content
            
        Returns:
            List of temporal elements
        """
        temporal_elements = []
        
        for pattern_name, pattern in self.temporal_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                element = {
                    'type': pattern_name,
                    'text': match.group(0),
                    'value': self._normalize_temporal_value(match.group(0)),
                    'context': self._extract_temporal_context(match.group(0), text)
                }
                temporal_elements.append(element)
        
        return temporal_elements
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for processing."""
        # Remove extra whitespace
        text = re.sub(r'\\s+', ' ', text)
        # Remove line breaks
        text = text.replace('\\n', ' ').replace('\\r', ' ')
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        return text.strip()
    
    def _extract_legal_terms(self, text: str) -> List[str]:
        """Extract legal terminology from text."""
        legal_terms = []
        
        # Multi-word legal phrases
        for phrase in self.legal_vocabulary['phrases']:
            if phrase.lower() in text.lower():
                legal_terms.append(phrase)
        
        # Single legal words
        words = text.lower().split()
        for word in words:
            if word in self.legal_vocabulary['words']:
                legal_terms.append(word)
        
        return legal_terms
    
    def _extract_technical_terms(self, text: str, context_tags: List[str] = None) -> List[str]:
        """Extract technical terms based on context."""
        technical_terms = []
        
        # Technical patterns based on context
        if context_tags and 'TEC' in context_tags:
            tech_patterns = [
                r'\\b\\d+%\\b',  # Percentages (SLAs)
                r'\\b\\d+\\s*hours?\\b',  # Time specifications
                r'\\b\\d+\\s*days?\\b',
                r'\\buptime\\b',
                r'\\bperformance\\b',
                r'\\bdeliverable\\b'
            ]
            
            for pattern in tech_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                technical_terms.extend(matches)
        
        return technical_terms
    
    def _extract_financial_terms(self, text: str) -> List[str]:
        """Extract financial and monetary terms."""
        financial_patterns = [
            r'\\$[\\d,]+(?:\\.\\d{2})?',  # Dollar amounts
            r'\\b\\d+(?:\\.\\d{2})?%\\b',  # Interest rates/percentages
            r'\\b(?:payment|fee|cost|penalty|refund)\\b',  # Financial keywords
            r'\\b\\d+\\s*days?\\s*(?:after|before|from)\\b'  # Payment terms
        ]
        
        financial_terms = []
        for pattern in financial_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            financial_terms.extend(matches)
        
        return financial_terms
    
    def _extract_temporal_terms(self, text: str) -> List[str]:
        """Extract time-related terms and expressions."""
        temporal_terms = []
        
        # Common temporal expressions in contracts
        temporal_expressions = [
            r'\\b\\d+\\s*(?:day|week|month|year)s?\\b',
            r'\\bimmediately\\b',
            r'\\bpromptly\\b',
            r'\\bupon\\s+\\w+\\b',
            r'\\bwithin\\s+\\d+\\s*\\w+\\b',
            r'\\bno\\s+later\\s+than\\b'
        ]
        
        for pattern in temporal_expressions:
            matches = re.findall(pattern, text, re.IGNORECASE)
            temporal_terms.extend(matches)
        
        return temporal_terms
    
    def _score_terms(self, terms: List[str], text: str, context_tags: List[str] = None) -> Dict[str, float]:
        """Score terms by importance and relevance."""
        term_scores = {}
        text_lower = text.lower()
        
        for term in terms:
            score = 1.0  # Base score
            
            # Frequency scoring
            frequency = text_lower.count(term.lower())
            score += frequency * 0.5
            
            # Length scoring (longer terms often more specific)
            if len(term) > 5:
                score += 0.3
            
            # Legal vocabulary bonus
            if term.lower() in self.legal_vocabulary['high_value']:
                score += 1.0
            
            # Context relevance
            if context_tags:
                for tag in context_tags:
                    if tag in ['FIN'] and any(fin_word in term.lower() 
                                            for fin_word in ['payment', 'fee', 'cost']):
                        score += 0.5
                    elif tag == 'LEG' and any(leg_word in term.lower() 
                                            for leg_word in ['liability', 'breach', 'law']):
                        score += 0.5
            
            term_scores[term] = score
        
        return term_scores
    
    def _identify_clause_function(self, text: str) -> ClauseFunction:
        """Identify the primary function of a clause."""
        function_indicators = {
            'define_obligations': ['shall', 'must', 'agrees to', 'undertakes to'],
            'establish_rights': ['entitled to', 'right to', 'may', 'permitted to'],
            'set_conditions': ['if', 'unless', 'provided that', 'subject to'],
            'specify_procedures': ['procedure', 'process', 'method', 'manner'],
            'allocate_risks': ['liable', 'responsible', 'assumes', 'bears'],
            'define_terms': ['means', 'defined as', 'refers to', 'includes'],
            'establish_timelines': ['within', 'by', 'deadline', 'schedule'],
            'govern_payments': ['payment', 'invoice', 'fee', 'cost', 'penalty']
        }
        
        scores = {}
        indicators_found = []
        
        text_lower = text.lower()
        for function, indicators in function_indicators.items():
            score = 0
            for indicator in indicators:
                if indicator in text_lower:
                    score += 1
                    indicators_found.append(indicator)
            scores[function] = score
        
        if not scores or max(scores.values()) == 0:
            return ClauseFunction(
                primary_function="establish contractual terms",
                secondary_functions=[],
                confidence=0.3,
                indicators=[]
            )
        
        primary_function = max(scores, key=scores.get)
        confidence = min(scores[primary_function] / 3.0, 1.0)  # Normalize confidence
        
        # Get secondary functions
        secondary_functions = [func for func, score in scores.items() 
                             if func != primary_function and score > 0]
        
        return ClauseFunction(
            primary_function=primary_function.replace('_', ' '),
            secondary_functions=[func.replace('_', ' ') for func in secondary_functions],
            confidence=confidence,
            indicators=indicators_found
        )
    
    def _generate_function_description(self, function: ClauseFunction) -> str:
        """Generate a natural language description of clause function."""
        descriptions = {
            'define obligations': "This clause creates binding duties and responsibilities for the parties.",
            'establish rights': "This clause grants specific rights and permissions to the parties.",
            'set conditions': "This clause establishes conditional requirements that must be met.",
            'specify procedures': "This clause outlines the specific processes and methods to be followed.",
            'allocate risks': "This clause determines how risks and liabilities are distributed.",
            'define terms': "This clause provides definitions and interpretations of key terms.",
            'establish timelines': "This clause sets important deadlines and scheduling requirements.",
            'govern payments': "This clause controls financial obligations and payment procedures."
        }
        
        return descriptions.get(function.primary_function, "This clause establishes contractual provisions.")
    
    def _identify_obligated_party(self, obligation_text: str) -> str:
        """Identify which party has the obligation."""
        party_indicators = {
            'Provider': ['provider', 'contractor', 'vendor', 'supplier'],
            'Client': ['client', 'customer', 'buyer', 'purchaser'],
            'Both': ['parties', 'each party', 'both']
        }
        
        text_lower = obligation_text.lower()
        for party, indicators in party_indicators.items():
            if any(indicator in text_lower for indicator in indicators):
                return party
        
        return "Unspecified"
    
    def _extract_action(self, obligation_text: str) -> str:
        """Extract the action/verb from an obligation."""
        action_verbs = re.findall(r'\\b(?:shall|must|will|agrees? to|undertakes? to)\\s+(\\w+)', 
                                 obligation_text, re.IGNORECASE)
        return action_verbs[0] if action_verbs else "perform"
    
    def _extract_consequence(self, condition_text: str, full_text: str) -> str:
        """Extract the consequence of a conditional statement."""
        # Look for consequence indicators after the condition
        consequence_patterns = [
            r'then\\s+(.+?)(?:\\.|;|,)',
            r',\\s*(.+?)(?:\\.|;)',
            r'\\s+(.+?)(?:\\.|;)'
        ]
        
        for pattern in consequence_patterns:
            match = re.search(pattern, condition_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "consequence not clearly specified"
    
    def _classify_condition_type(self, condition_text: str) -> str:
        """Classify the type of condition."""
        if 'if' in condition_text.lower():
            return 'conditional'
        elif 'unless' in condition_text.lower():
            return 'negative_conditional'
        elif 'provided that' in condition_text.lower():
            return 'proviso'
        else:
            return 'general_condition'
    
    def _normalize_temporal_value(self, temporal_text: str) -> str:
        """Normalize temporal expressions to standard format."""
        # Extract number and unit
        match = re.search(r'(\\d+)\\s*(\\w+)', temporal_text)
        if match:
            number, unit = match.groups()
            # Normalize unit
            unit_map = {
                'day': 'days', 'days': 'days',
                'week': 'weeks', 'weeks': 'weeks', 
                'month': 'months', 'months': 'months',
                'year': 'years', 'years': 'years'
            }
            normalized_unit = unit_map.get(unit.lower(), unit)
            return f"{number} {normalized_unit}"
        
        return temporal_text
    
    def _extract_temporal_context(self, temporal_text: str, full_text: str) -> str:
        """Extract context around temporal expressions."""
        # Find the sentence containing the temporal expression
        sentences = full_text.split('.')
        for sentence in sentences:
            if temporal_text in sentence:
                return sentence.strip()
        return "context not found"
    
    def _build_legal_vocabulary(self) -> Dict[str, List[str]]:
        """Build legal vocabulary for term extraction."""
        return {
            'words': [
                'liability', 'indemnification', 'breach', 'default', 'termination',
                'jurisdiction', 'governing', 'arbitration', 'mediation', 'damages',
                'warranty', 'representation', 'covenant', 'obligation', 'remedy'
            ],
            'phrases': [
                'governing law', 'dispute resolution', 'force majeure', 'intellectual property',
                'confidential information', 'trade secrets', 'limitation of liability',
                'liquidated damages', 'specific performance', 'injunctive relief'
            ],
            'high_value': [
                'indemnification', 'limitation of liability', 'intellectual property',
                'termination', 'breach', 'governing law', 'dispute resolution'
            ]
        }
    
    def _build_action_patterns(self) -> Dict[str, str]:
        """Build patterns for action detection."""
        return {
            'obligation': r'\\b(?:shall|must|agrees? to|undertakes? to|is required to)\\b',
            'permission': r'\\b(?:may|is permitted to|is entitled to|has the right to)\\b',
            'prohibition': r'\\b(?:shall not|must not|may not|is prohibited from)\\b'
        }
    
    def _build_obligation_patterns(self) -> Dict[str, str]:
        """Build patterns for obligation detection."""
        return {
            'payment_obligation': r'\\b(?:shall pay|must pay|payment.{0,20}due)\\b',
            'delivery_obligation': r'\\b(?:shall deliver|must provide|delivery.{0,20}required)\\b',
            'performance_obligation': r'\\b(?:shall perform|must complete|performance.{0,20}required)\\b',
            'notice_obligation': r'\\b(?:shall notify|must inform|notice.{0,20}required)\\b'
        }
    
    def _build_conditional_patterns(self) -> List[str]:
        """Build patterns for conditional statement detection."""
        return [
            r'\\bif\\b(.+?)\\bthen\\b',
            r'\\bunless\\b(.+?)(?:,|\\.|;)',
            r'\\bprovided that\\b(.+?)(?:,|\\.|;)',
            r'\\bsubject to\\b(.+?)(?:,|\\.|;)'
        ]
    
    def _build_temporal_patterns(self) -> Dict[str, str]:
        """Build patterns for temporal element detection."""
        return {
            'deadline': r'\\b(?:by|before|no later than)\\s+[^,\\.]+',
            'duration': r'\\b\\d+\\s*(?:day|week|month|year)s?\\b',
            'frequency': r'\\b(?:daily|weekly|monthly|annually|quarterly)\\b',
            'immediacy': r'\\b(?:immediately|promptly|forthwith|without delay)\\b'
        }


def main():
    """Example usage of LegalNLPProcessor."""
    processor = LegalNLPProcessor()
    
    sample_text = """
    The Provider shall deliver all deliverables within 30 days of contract execution.
    If the Provider fails to meet the deadline, a penalty of 2% per month shall apply.
    The Client must pay all invoices within 15 days of receipt.
    """
    
    print("Key Terms:", processor.extract_key_terms(sample_text, ['TEC', 'FIN']))
    print("Function:", processor.analyze_clause_function(sample_text))
    print("Obligations:", processor.extract_obligations(sample_text))
    print("Conditions:", processor.extract_conditions(sample_text))
    print("Temporal Elements:", processor.extract_temporal_elements(sample_text))


if __name__ == "__main__":
    main()
