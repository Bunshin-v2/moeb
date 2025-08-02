"""
Unit tests for ContractParser component.
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import PyPDF2

from src.core.contract_parser import ContractParser, Clause, ParseError


class TestContractParser:
    """Test suite for ContractParser."""
    
    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = ContractParser()
        assert parser.supported_formats == ['.pdf', '.docx', '.txt']
        assert parser.clause_patterns is not None
    
    def test_parse_text_file(self, temp_dir, sample_text_contract):
        """Test parsing a text file."""
        # Create test file
        test_file = temp_dir / "contract.txt"
        test_file.write_text(sample_text_contract)
        
        # Parse the file
        parser = ContractParser()
        result = parser.parse(test_file)
        
        # Verify metadata
        assert result["metadata"]["title"] == "SERVICE AGREEMENT"
        assert "ABC Corporation" in result["metadata"]["parties"]
        assert "XYZ Services Ltd." in result["metadata"]["parties"]
        
        # Verify clauses
        assert len(result["clauses"]) > 0
        assert any(clause.title == "SCOPE OF SERVICES" for clause in result["clauses"])
        assert any(clause.title == "PAYMENT TERMS" for clause in result["clauses"])
    
    def test_parse_pdf_file(self, sample_pdf_path):
        """Test parsing a PDF file."""
        parser = ContractParser()
        
        # Mock PyPDF2 reader
        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_pdf = MagicMock()
            mock_pdf.pages = [MagicMock(extract_text=lambda: "CONTRACT\n\n1. Terms\nSample terms")]
            mock_reader.return_value = mock_pdf
            
            result = parser.parse(sample_pdf_path)
            assert result["metadata"]["format"] == "pdf"
            assert result["clauses"] is not None
    
    def test_parse_docx_file(self, sample_docx_path):
        """Test parsing a DOCX file."""
        parser = ContractParser()
        
        # Mock python-docx
        with patch('docx.Document') as mock_doc:
            mock_document = MagicMock()
            mock_document.paragraphs = [
                MagicMock(text="CONTRACT"),
                MagicMock(text=""),
                MagicMock(text="1. Terms"),
                MagicMock(text="Sample terms")
            ]
            mock_doc.return_value = mock_document
            
            result = parser.parse(sample_docx_path)
            assert result["metadata"]["format"] == "docx"
            assert result["clauses"] is not None
    
    def test_parse_unsupported_format(self, temp_dir):
        """Test parsing unsupported file format."""
        parser = ContractParser()
        unsupported_file = temp_dir / "contract.xyz"
        unsupported_file.write_text("content")
        
        with pytest.raises(ParseError, match="Unsupported file format"):
            parser.parse(unsupported_file)
    
    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file."""
        parser = ContractParser()
        
        with pytest.raises(ParseError, match="File not found"):
            parser.parse(Path("nonexistent.pdf"))
    
    def test_extract_clauses(self, sample_text_contract):
        """Test clause extraction from text."""
        parser = ContractParser()
        clauses = parser._extract_clauses(sample_text_contract)
        
        # Check clause count
        assert len(clauses) == 5  # 5 main clauses
        
        # Check clause structure
        scope_clause = next((c for c in clauses if c.title == "SCOPE OF SERVICES"), None)
        assert scope_clause is not None
        assert len(scope_clause.children) == 2  # 1.1 and 1.2
        
        # Check clause numbering
        assert scope_clause.number == "1"
        assert scope_clause.children[0].number == "1.1"
    
    def test_extract_metadata(self, sample_text_contract):
        """Test metadata extraction."""
        parser = ContractParser()
        metadata = parser._extract_metadata(sample_text_contract)
        
        assert metadata["title"] == "SERVICE AGREEMENT"
        assert "ABC Corporation" in metadata["parties"]
        assert "XYZ Services Ltd." in metadata["parties"]
        assert metadata.get("effective_date") == "January 1, 2025"
    
    def test_clause_hierarchy(self):
        """Test clause hierarchy construction."""
        parser = ContractParser()
        text = """
        1. Main Clause
           1.1 Sub clause one
           1.2 Sub clause two
               1.2.1 Sub sub clause
        2. Another Main Clause
        """
        
        clauses = parser._extract_clauses(text)
        
        # Check main clauses
        assert len(clauses) == 2
        assert clauses[0].number == "1"
        assert clauses[1].number == "2"
        
        # Check sub-clauses
        assert len(clauses[0].children) == 2
        assert clauses[0].children[0].number == "1.1"
        assert clauses[0].children[1].number == "1.2"
        
        # Check sub-sub-clauses
        assert len(clauses[0].children[1].children) == 1
        assert clauses[0].children[1].children[0].number == "1.2.1"
    
    def test_clause_pattern_matching(self):
        """Test different clause pattern matching."""
        parser = ContractParser()
        
        # Test numbered pattern
        text1 = "1. First Clause\n2. Second Clause"
        clauses1 = parser._extract_clauses(text1)
        assert len(clauses1) == 2
        
        # Test lettered pattern
        text2 = "A. First Clause\nB. Second Clause"
        clauses2 = parser._extract_clauses(text2)
        assert len(clauses2) == 2
        
        # Test section pattern
        text3 = "Section 1: First\nSection 2: Second"
        clauses3 = parser._extract_clauses(text3)
        assert len(clauses3) == 2
        
        # Test article pattern
        text4 = "Article I - First\nArticle II - Second"
        clauses4 = parser._extract_clauses(text4)
        assert len(clauses4) == 2
    
    def test_empty_document(self):
        """Test parsing empty document."""
        parser = ContractParser()
        
        result = parser._extract_clauses("")
        assert result == []
        
        metadata = parser._extract_metadata("")
        assert metadata["title"] == "Untitled Contract"
        assert metadata["parties"] == []
    
    def test_malformed_pdf(self, temp_dir):
        """Test handling of malformed PDF."""
        parser = ContractParser()
        
        # Create a file that's not a valid PDF
        bad_pdf = temp_dir / "bad.pdf"
        bad_pdf.write_text("Not a PDF")
        
        with patch('PyPDF2.PdfReader', side_effect=Exception("Invalid PDF")):
            with pytest.raises(ParseError, match="Failed to parse PDF"):
                parser.parse(bad_pdf)
    
    def test_large_document_handling(self):
        """Test handling of large documents."""
        parser = ContractParser()
        
        # Create a large document
        large_text = "\n".join([f"{i}. Clause {i}" for i in range(1, 101)])
        clauses = parser._extract_clauses(large_text)
        
        assert len(clauses) == 100
        assert clauses[0].number == "1"
        assert clauses[-1].number == "100"
    
    def test_special_characters_in_clauses(self):
        """Test handling special characters in clause text."""
        parser = ContractParser()
        
        text = """
        1. Payment Terms ($10,000/month)
        2. Liability & Indemnification
        3. IP Rights © 2025
        """
        
        clauses = parser._extract_clauses(text)
        assert len(clauses) == 3
        assert "$10,000/month" in clauses[0].text
        assert "&" in clauses[1].text
        assert "©" in clauses[2].text


class TestClause:
    """Test suite for Clause data structure."""
    
    def test_clause_creation(self):
        """Test basic clause creation."""
        clause = Clause(
            id="1",
            number="1",
            title="Test Clause",
            text="This is test clause content"
        )
        
        assert clause.id == "1"
        assert clause.number == "1"
        assert clause.title == "Test Clause"
        assert clause.text == "This is test clause content"
        assert clause.children == []
    
    def test_clause_with_children(self):
        """Test clause with sub-clauses."""
        child1 = Clause(id="1.1", number="1.1", text="Sub clause 1")
        child2 = Clause(id="1.2", number="1.2", text="Sub clause 2")
        
        parent = Clause(
            id="1",
            number="1",
            title="Parent Clause",
            text="Parent content",
            children=[child1, child2]
        )
        
        assert len(parent.children) == 2
        assert parent.children[0].number == "1.1"
        assert parent.children[1].number == "1.2"
    
    def test_clause_string_representation(self):
        """Test clause string representation."""
        clause = Clause(
            id="1",
            number="1",
            title="Test",
            text="Content"
        )
        
        str_repr = str(clause)
        assert "1" in str_repr
        assert "Test" in str_repr
    
    def test_clause_to_dict(self):
        """Test clause serialization to dictionary."""
        clause = Clause(
            id="1",
            number="1",
            title="Test",
            text="Content",
            children=[
                Clause(id="1.1", number="1.1", text="Sub content")
            ]
        )
        
        clause_dict = clause.to_dict()
        assert clause_dict["id"] == "1"
        assert clause_dict["number"] == "1"
        assert clause_dict["title"] == "Test"
        assert clause_dict["text"] == "Content"
        assert len(clause_dict["children"]) == 1
        assert clause_dict["children"][0]["number"] == "1.1"
