"""
Unit tests for input validation utilities.
"""
import pytest
from utils.validation import validate_query, validate_file_path, ValidationError

class TestValidateQuery:
    """Test cases for query validation."""
    
    def test_valid_query(self):
        """Test valid query passes validation."""
        query = "What is the company vacation policy?"
        result = validate_query(query)
        assert result == query
    
    def test_empty_query(self):
        """Test empty query raises ValidationError."""
        with pytest.raises(ValidationError, match="Query cannot be empty"):
            validate_query("")
    
    def test_whitespace_only_query(self):
        """Test whitespace-only query raises ValidationError."""
        with pytest.raises(ValidationError, match="Query cannot be empty or only whitespace"):
            validate_query("   \n\t   ")
    
    def test_query_too_long(self):
        """Test query exceeding length limit raises ValidationError."""
        long_query = "a" * 2001
        with pytest.raises(ValidationError, match="Query too long"):
            validate_query(long_query)
    
    def test_query_too_short(self):
        """Test query below minimum length raises ValidationError."""
        with pytest.raises(ValidationError, match="Query too short"):
            validate_query("a")
    
    def test_malicious_script_tag(self):
        """Test script tag detection raises ValidationError."""
        malicious_query = "What is <script>alert('xss')</script> the policy?"
        with pytest.raises(ValidationError, match="potentially unsafe content"):
            validate_query(malicious_query)
    
    def test_javascript_url(self):
        """Test JavaScript URL detection raises ValidationError."""
        malicious_query = "javascript:alert('xss')"
        with pytest.raises(ValidationError, match="potentially unsafe content"):
            validate_query(malicious_query)
    
    def test_whitespace_normalization(self):
        """Test excessive whitespace is normalized."""
        query = "What   is   the    policy?"
        result = validate_query(query)
        assert result == "What is the policy?"

class TestValidateFilePath:
    """Test cases for file path validation."""
    
    def test_valid_txt_file(self):
        """Test valid .txt file path passes validation."""
        file_path = "document.txt"
        result = validate_file_path(file_path)
        assert result == file_path
    
    def test_valid_pdf_file(self):
        """Test valid .pdf file path passes validation."""
        file_path = "document.pdf"
        result = validate_file_path(file_path)
        assert result == file_path
    
    def test_empty_file_path(self):
        """Test empty file path raises ValidationError."""
        with pytest.raises(ValidationError, match="File path cannot be empty"):
            validate_file_path("")
    
    def test_path_traversal_attempt(self):
        """Test path traversal attempt raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid file path"):
            validate_file_path("../secret.txt")
    
    def test_absolute_path(self):
        """Test absolute path raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid file path"):
            validate_file_path("/etc/passwd")
    
    def test_unsupported_extension(self):
        """Test unsupported file extension raises ValidationError."""
        with pytest.raises(ValidationError, match="Only .txt and .pdf files are allowed"):
            validate_file_path("document.exe")
