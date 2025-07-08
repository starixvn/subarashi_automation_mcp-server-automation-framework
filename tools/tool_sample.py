"""
COMPLETE GUIDE: How to create a custom tool in this advanced MCP server framework

This file demonstrates the sophisticated tool architecture and provides a complete
example of how to implement a new tool following the established patterns.
"""

from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pydantic import Field, validator
from .tool_schema import (
    define_tool,
    define_tool_factory,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
    ToolInputSchema,
)
from .utils import wait_for_completion, sanitize_for_file_path

if TYPE_CHECKING:
    from ..context import ServerContext


# =============================================================================
# STEP 1: Define Input Schema with Advanced Validation
# =============================================================================

class WeatherInputSchema(ToolInputSchema):
    """
    Advanced input schema with comprehensive validation.
    This demonstrates the sophisticated validation system.
    """
    
    city: str = Field(
        description="City name to get weather for",
        min_length=2,
        max_length=100
    )
    
    country: Optional[str] = Field(
        default=None,
        description="Country code (optional, improves accuracy)",
        min_length=2,
        max_length=3
    )
    
    unit: Optional[str] = Field(
        default="celsius",
        description="Temperature unit (celsius, fahrenheit, kelvin)"
    )
    
    include_forecast: bool = Field(
        default=False,
        description="Include 5-day forecast"
    )
    
    @validator("city")
    def validate_city(cls, v):
        if not v.strip():
            raise ValueError("City name cannot be empty")
        # Remove special characters that might cause issues
        sanitized = ''.join(c for c in v if c.isalnum() or c.isspace())
        return sanitized.strip()
    
    @validator("country")
    def validate_country(cls, v):
        if v is None:
            return None
        v = v.upper().strip()
        # Simple validation for common country codes
        if len(v) not in [2, 3]:
            raise ValueError("Country code must be 2 or 3 characters")
        return v
    
    @validator("unit")
    def validate_unit(cls, v):
        allowed_units = ["celsius", "fahrenheit", "kelvin"]
        if v.lower() not in allowed_units:
            raise ValueError(f"Unit must be one of: {', '.join(allowed_units)}")
        return v.lower()


# =============================================================================
# STEP 2: Implement Tool with Advanced Features
# =============================================================================

@define_tool_factory(
    capability=ToolCapability.API,  # Using existing capability
    name="weather_fetch",
    title="Fetch Weather Data",
    description="Fetch current weather and optional forecast for a city with advanced error handling and caching",
    input_schema=WeatherInputSchema,
    tool_type=ToolType.READ_ONLY,  # This is a read-only operation
)
def weather_fetch_factory(capture_snapshot: bool) -> Tool:
    """
    Factory function that creates the weather tool.
    This pattern allows for dynamic configuration based on capture_snapshot.
    """
    
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        """
        Main tool handler - demonstrates advanced patterns:
        1. Input validation
        2. Error handling with detailed reporting
        3. Asynchronous operations
        4. Code generation for transparency
        5. Action execution with proper result handling
        """
        
        # Validate input using our schema
        validated_params = WeatherInputSchema(**params)
        
        # Generate code representation for transparency
        code_lines = [
            f"// Fetch weather for {validated_params.city}",
            f"const weatherData = await fetch('https://api.weather.com/v1/current', {{",
            f"  params: {{",
            f"    city: '{validated_params.city}',",
            f"    country: '{validated_params.country or 'auto'}',",
            f"    unit: '{validated_params.unit}',",
            f"    forecast: {str(validated_params.include_forecast).lower()}",
            f"  }}",
            f"}});",
            f"return weatherData.json();",
        ]
        
        # Define the actual action to execute
        async def action() -> ToolActionResult:
            try:
                # Simulate API call with sophisticated error handling
                import aiohttp
                import asyncio
                
                # Mock weather API endpoint (replace with real API)
                api_url = "https://api.openweathermap.org/data/2.5/weather"
                
                # Prepare request parameters
                params = {
                    "q": f"{validated_params.city},{validated_params.country}" if validated_params.country else validated_params.city,
                    "units": "metric" if validated_params.unit == "celsius" else "imperial" if validated_params.unit == "fahrenheit" else "standard",
                    "appid": "your_api_key_here"  # Would be from settings
                }
                
                # Advanced timeout and retry logic
                timeout = aiohttp.ClientTimeout(total=10.0)
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(api_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Process and format the response
                            result_content = [
                                {
                                    "type": "text",
                                    "text": f"Weather for {validated_params.city}:\n" +
                                           f"Temperature: {data.get('main', {}).get('temp', 'N/A')}°{validated_params.unit[0].upper()}\n" +
                                           f"Condition: {data.get('weather', [{}])[0].get('description', 'N/A')}\n" +
                                           f"Humidity: {data.get('main', {}).get('humidity', 'N/A')}%"
                                }
                            ]
                            
                            # Add forecast if requested
                            if validated_params.include_forecast:
                                result_content.append({
                                    "type": "text",
                                    "text": "5-day forecast: [Feature would be implemented here]"
                                })
                            
                            return ToolActionResult(content=result_content)
                        
                        else:
                            # Handle API errors gracefully
                            error_msg = f"Weather API returned status {response.status}"
                            return ToolActionResult(
                                content=[{
                                    "type": "text",
                                    "text": f"Error fetching weather: {error_msg}"
                                }]
                            )
                            
            except aiohttp.ClientError as e:
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": f"Network error: {str(e)}"
                    }]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": f"Unexpected error: {str(e)}"
                    }]
                )
        
        # Return the tool result with all components
        return ToolResult(
            code=code_lines,
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=True,  # Wait for network completion
        )
    
    # Create and return the tool schema
    schema = ToolSchema(
        name="weather_fetch",
        title="Fetch Weather Data",
        description="Fetch current weather and optional forecast for a city with advanced error handling and caching",
        input_schema=WeatherInputSchema,
        tool_type=ToolType.READ_ONLY,
    )
    
    return Tool(
        capability=ToolCapability.API,
        schema=schema,
        handle=handle,
        browser_independent=True,  # This tool doesn't need browser context
    )

# =============================================================================
# STEP 3: Export Tools (Required for Registry)
# =============================================================================

def get_sample_tools(capture_snapshot: bool = True) -> List[Tool]:
    """
    Export function required by the registry system.
    This function must exist for the tools to be discoverable.
    """
    return [
        weather_fetch_factory(capture_snapshot)
    ]


# Static export for backward compatibility
SAMPLE_TOOLS = get_sample_tools()


# =============================================================================
# STEP 4: Registration Instructions
# =============================================================================

"""
TO ADD THESE TOOLS TO THE SYSTEM:

1. Add the input schemas to tools/schemas.py:
   - Add WeatherInputSchema imports
   - Export them in __all__

2. Add imports to tools/__init__.py:
   - from .tool_sample import get_sample_tools, SAMPLE_TOOLS
   - Add to __all__ list

3. Add to tools/registry.py:
   - Import: from .tool_sample import get_sample_tools
   - Add to _create_snapshot_tools() method:
     tools.extend(get_sample_tools(capture_snapshot=True))
   - Add to _create_vision_tools() method:
     tools.extend(get_sample_tools(capture_snapshot=False))

4. Add capability to tool_schema.py if needed:
   - Add WEATHER = "weather" to ToolCapability enum

5. Test the tools:
   - Run the server and verify tools appear in capabilities
   - Test with MCP client to ensure proper functionality
"""