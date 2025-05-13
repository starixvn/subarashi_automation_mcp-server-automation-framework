import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic


class AnthropicService:
    """Service for interacting with the Anthropic API."""

    def __init__(self):
        # Load API key from the mcp .env file
        env_path = Path("config/environments/mcp/.env")
        load_dotenv(dotenv_path=env_path)
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 1000

    def generate_response(self, messages, tools=None):
        """Generate a response from the Anthropic API.
        
        Args:
            messages: List of message objects with role and content
            tools: Optional list of tools available to the model
            
        Returns:
            The response from the Anthropic API
        """
        return self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,
            tools=tools if tools else None,
        ) 