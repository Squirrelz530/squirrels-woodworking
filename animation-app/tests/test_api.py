"""Tests for the API client."""

import pytest
from app.api import ImageGenerationAPI
from app.models import GenerationRequest


class TestImageGenerationAPI:
    """Tests for the ImageGenerationAPI class."""
    
    def test_init(self):
        """Test API initialization."""
        api = ImageGenerationAPI()
        assert api.timeout == 30
        
        api_custom = ImageGenerationAPI(timeout=60)
        assert api_custom.timeout == 60
    
    def test_validate_prompt_empty(self):
        """Test validating an empty prompt."""
        api = ImageGenerationAPI()
        is_valid, error = api.validate_prompt("")
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_validate_prompt_whitespace(self):
        """Test validating a whitespace-only prompt."""
        api = ImageGenerationAPI()
        is_valid, error = api.validate_prompt("   ")
        assert is_valid is False
    
    def test_validate_prompt_too_long(self):
        """Test validating a very long prompt."""
        api = ImageGenerationAPI()
        long_prompt = "a" * 1001
        is_valid, error = api.validate_prompt(long_prompt)
        assert is_valid is False
        assert "long" in error.lower()
    
    def test_validate_prompt_with_newlines(self):
        """Test validating a prompt with newlines."""
        api = ImageGenerationAPI()
        is_valid, error = api.validate_prompt("test\nprompt")
        assert is_valid is False
        assert "invalid" in error.lower() or "newline" in error.lower()
    
    def test_validate_prompt_valid(self):
        """Test validating a valid prompt."""
        api = ImageGenerationAPI()
        is_valid, error = api.validate_prompt("a beautiful sunset")
        assert is_valid is True
        assert error == ""
    
    def test_generate_image_empty_prompt(self):
        """Test generating with an empty prompt."""
        api = ImageGenerationAPI()
        request = GenerationRequest(prompt="")
        result = api.generate_image(request)
        
        assert result.success is False
        assert result.error_message is not None
    
    def test_generation_result_structure(self):
        """Test that generation result has expected structure."""
        api = ImageGenerationAPI()
        request = GenerationRequest(prompt="")
        result = api.generate_image(request)
        
        # Result should have these attributes
        assert hasattr(result, 'success')
        assert hasattr(result, 'image_data')
        assert hasattr(result, 'file_path')
        assert hasattr(result, 'error_message')
        assert hasattr(result, 'asset')
