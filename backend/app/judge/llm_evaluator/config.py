"""Configuration module for LLM-based code evaluation."""

import os
from typing import Optional
from app.core.config import settings


class LLMConfig:
    """Configuration for LLM-based code evaluation."""
    
    def __init__(self):
        """Initialize LLM configuration with default values."""
        # Default model
        self.model_name = "gpt-3.5-turbo"
        
        # API configuration
        self._api_key = os.getenv("OPENAI_API_KEY", "")
        self._api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        
        # Load from app settings if available
        if not self._api_key and hasattr(settings, "OPENAI_API_KEY"):
            self._api_key = settings.OPENAI_API_KEY
            
        if hasattr(settings, "OPENAI_API_BASE"):
            self._api_base = settings.OPENAI_API_BASE
            
        # LLM parameters
        self.temperature = 0.2
        self.response_format_json = True
    
    @property
    def api_key(self) -> str:
        """Get the API key."""
        return self._api_key
    
    @property
    def api_base(self) -> str:
        """Get the API base URL."""
        return self._api_base
    
    def setup_environment(self) -> None:
        """Set up environment variables for API access."""
        # 设置API基础URL（如果不是默认值）
        if self._api_base != "https://api.openai.com/v1":
            os.environ["OPENAI_API_BASE"] = self._api_base
            print(f"使用API基础URL: {self._api_base}")
    
    def get_model_kwargs(self) -> dict:
        """Get model parameters for LangChain."""
        kwargs = {}
        
        # Add JSON response format if needed
        if self.response_format_json:
            kwargs["response_format"] = {"type": "json_object"}
            
        return kwargs


# Create a singleton config instance
llm_config = LLMConfig()
