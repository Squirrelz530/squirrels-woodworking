"""API client for cloud AI image generation.

Uses Pollinations.ai as the default provider (no authentication required).
"""

import requests
from typing import Optional, Tuple

from .models import GenerationRequest, GenerationResult


# Default timeout for API requests (seconds)
DEFAULT_TIMEOUT = 30


class ImageGenerationAPI:
    """Client for cloud AI image generation APIs."""
    
    POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """Initialize the API client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
    
    def validate_prompt(self, prompt: str) -> Tuple[bool, str]:
        """Validate and sanitize a prompt.
        
        Args:
            prompt: The prompt text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not prompt or not prompt.strip():
            return False, "Prompt cannot be empty"
        
        # Check for extremely long prompts
        if len(prompt) > 1000:
            return False, "Prompt is too long (max 1000 characters)"
        
        # Check for potentially problematic characters
        # Pollinations.ai should handle most characters, but we'll be cautious
        if any(char in prompt for char in ['\n', '\r', '\t']):
            return False, "Prompt contains invalid characters (newlines or tabs)"
        
        return True, ""
    
    def generate_image(self, request: GenerationRequest) -> GenerationResult:
        """Generate an image using the Pollinations.ai API.
        
        Args:
            request: The generation request
            
        Returns:
            GenerationResult with the image data or error
        """
        # Validate the request
        is_valid, error_msg = self.validate_prompt(request.prompt)
        if not is_valid:
            return GenerationResult(
                success=False,
                error_message=error_msg,
            )
        
        try:
            # Build URL with query parameters
            url = self.POLLINATIONS_BASE_URL
            params = request.to_pollinations_params()
            
            # Make the request
            response = requests.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Get the image data
            image_data = response.content
            
            # Validate that we got image data
            if not image_data or len(image_data) < 100:
                return GenerationResult(
                    success=False,
                    error_message="Received empty or invalid image data",
                )
            
            # Check if it looks like a valid image (PNG header)
            if not image_data.startswith(b'\x89PNG\r\n\x1a\n'):
                # Might be another format or an error message
                try:
                    error_text = image_data.decode('utf-8')
                    return GenerationResult(
                        success=False,
                        error_message=f"Server returned an error: {error_text}",
                    )
                except UnicodeDecodeError:
                    pass
            
            return GenerationResult(
                success=True,
                image_data=image_data,
                error_message=None,
            )
            
        except requests.exceptions.Timeout:
            return GenerationResult(
                success=False,
                error_message=f"Request timed out after {self.timeout} seconds",
            )
        except requests.exceptions.ConnectionError:
            return GenerationResult(
                success=False,
                error_message="Failed to connect to the server. Check your internet connection.",
            )
        except requests.exceptions.HTTPError as e:
            return GenerationResult(
                success=False,
                error_message=f"HTTP error: {e.response.status_code} - {e.response.reason}",
            )
        except requests.exceptions.RequestException as e:
            return GenerationResult(
                success=False,
                error_message=f"Request failed: {str(e)}",
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
            )
