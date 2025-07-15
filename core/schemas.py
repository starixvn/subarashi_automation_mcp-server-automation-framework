from typing import Optional, List, Dict, Any
import json
from pydantic import Field, validator
from core.tool_schema import ToolInputSchema


class EmptyInputSchema(ToolInputSchema):
    pass


class NavigateInputSchema(ToolInputSchema):
    url: str = Field(description="The URL to navigate to")

    @validator("url")
    def validate_url(cls, v):
        if not v.strip():
            raise ValueError("URL cannot be empty")
        return v.strip()


class ResizeInputSchema(ToolInputSchema):
    width: int = Field(description="Width of the browser window", ge=100, le=3840)
    height: int = Field(description="Height of the browser window", ge=100, le=2160)


class ElementInputSchema(ToolInputSchema):
    element: str = Field(description="Human-readable element description")
    ref: str = Field(description="Exact element reference from page snapshot")


class ClickInputSchema(ElementInputSchema):
    pass


class TypeInputSchema(ElementInputSchema):
    text: str = Field(description="Text to type into the element")
    submit: Optional[bool] = Field(
        default=False, description="Whether to submit entered text (press Enter after)"
    )
    slowly: Optional[bool] = Field(
        default=False, description="Whether to type one character at a time"
    )


class HoverInputSchema(ElementInputSchema):
    pass


class SelectOptionInputSchema(ElementInputSchema):
    values: List[str] = Field(description="Array of values to select in the dropdown")


class GetTextInputSchema(ToolInputSchema):
    selector: str = Field(description="CSS selector for the element")


class WaitForSelectorInputSchema(ToolInputSchema):
    selector: str = Field(description="CSS selector to wait for")
    timeout: Optional[float] = Field(
        default=10.0, description="Timeout in seconds", ge=0, le=60
    )


class ScreenshotInputSchema(ToolInputSchema):
    full_page: Optional[bool] = Field(
        default=True, description="Take full page screenshot"
    )


class SaveScreenshotInputSchema(ToolInputSchema):
    filename: str = Field(description="Filename for the screenshot")
    full_page: Optional[bool] = Field(
        default=True, description="Take full page screenshot"
    )

    @validator("filename")
    def validate_filename(cls, v):
        if not v.strip():
            raise ValueError("Filename cannot be empty")
        return v.strip()


class ScreenClickInputSchema(ToolInputSchema):
    element: str = Field(description="Human-readable element description")
    x: int = Field(description="X coordinate", ge=0)
    y: int = Field(description="Y coordinate", ge=0)


class ScreenDragInputSchema(ToolInputSchema):
    element: str = Field(description="Human-readable element description")
    start_x: int = Field(description="Start X coordinate", ge=0)
    start_y: int = Field(description="Start Y coordinate", ge=0)
    end_x: int = Field(description="End X coordinate", ge=0)
    end_y: int = Field(description="End Y coordinate", ge=0)


class ScreenTypeInputSchema(ToolInputSchema):
    text: str = Field(description="Text to type")
    submit: Optional[bool] = Field(
        default=False, description="Whether to submit entered text"
    )


class ScreenMoveMouseInputSchema(ToolInputSchema):
    element: str = Field(description="Human-readable element description")
    x: int = Field(description="X coordinate", ge=0)
    y: int = Field(description="Y coordinate", ge=0)


class NewTabInputSchema(ToolInputSchema):
    url: Optional[str] = Field(
        None,
        description="The URL to navigate to in the new tab. If not provided, the new tab will be blank.",
    )


class SelectTabInputSchema(ToolInputSchema):
    index: int = Field(..., description="The index of the tab to select")


class CloseTabInputSchema(ToolInputSchema):
    index: Optional[int] = Field(
        None,
        description="The index of the tab to close. Closes current tab if not provided.",
    )


class WaitForInputSchema(ToolInputSchema):
    time: Optional[float] = Field(
        default=None, description="Time to wait in seconds", ge=0, le=30
    )
    text: Optional[str] = Field(default=None, description="Text to wait for to appear")
    text_gone: Optional[str] = Field(
        default=None, description="Text to wait for to disappear"
    )

    @validator("time", "text", "text_gone")
    def validate_at_least_one(cls, v, values):
        if not any(
            [values.get("time"), values.get("text"), values.get("text_gone"), v]
        ):
            raise ValueError(
                "At least one of time, text, or text_gone must be provided"
            )
        return v


class PressKeyInputSchema(ToolInputSchema):
    key: str = Field(description="Name of the key to press or character to generate")

    @validator("key")
    def validate_key(cls, v):
        if not v.strip():
            raise ValueError("Key cannot be empty")
        return v.strip()


class DragInputSchema(ToolInputSchema):
    start_element: str = Field(description="Human-readable source element description")
    start_ref: str = Field(
        description="Exact source element reference from page snapshot"
    )
    end_element: str = Field(description="Human-readable target element description")
    end_ref: str = Field(
        description="Exact target element reference from page snapshot"
    )


class UploadFileInputSchema(ToolInputSchema):
    file_paths: List[str] = Field(description="List of file paths to upload")

    @validator("file_paths")
    def validate_file_paths(cls, v):
        if not v:
            raise ValueError("At least one file path must be provided")
        return v


class HandleDialogInputSchema(ToolInputSchema):
    accept: bool = Field(description="Whether to accept or dismiss the dialog")
    prompt_text: Optional[str] = Field(
        default=None, description="Text to enter in prompt dialogs"
    )


class DialogInputSchema(ToolInputSchema):
    accept: bool = Field(..., description="Whether to accept the dialog.")
    prompt_text: Optional[str] = Field(
        None, description="The text of the prompt in case of a prompt dialog."
    )


class SetRequestInterceptionInputSchema(ToolInputSchema):
    enabled: bool = Field(description="Whether to enable request interception")
    patterns: Optional[List[str]] = Field(
        default=None, description="URL patterns to intercept"
    )


class ApiRequestInputSchema(ToolInputSchema):
    url: str = Field(description="API endpoint URL")
    method: str = Field(description="HTTP method (GET, POST, PUT, DELETE, PATCH)")
    headers: Optional[Dict[str, str]] = Field(default=None, description="HTTP headers")
    body: Optional[str] = Field(
        default=None, description="Request body for POST/PUT/PATCH"
    )
    timeout: Optional[int] = Field(
        default=30, description="Request timeout in seconds", ge=1, le=300
    )

    @validator("headers", pre=True)
    def parse_headers(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                raise ValueError("Headers must be a valid JSON object or dictionary")
        if isinstance(v, dict):
            return v
        raise ValueError("Headers must be a dictionary or JSON string")

    @validator("method")
    def validate_method(cls, v):
        allowed_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        if v.upper() not in allowed_methods:
            raise ValueError(f"Method must be one of: {', '.join(allowed_methods)}")
        return v.upper()

    @validator("url")
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class ApiTestInputSchema(ToolInputSchema):
    url: str = Field(description="API endpoint URL")
    method: str = Field(description="HTTP method (GET, POST, PUT, DELETE, PATCH)")
    headers: Optional[Dict[str, str]] = Field(default=None, description="HTTP headers")
    body: Optional[str] = Field(
        default=None, description="Request body for POST/PUT/PATCH"
    )
    expected_status: Optional[int] = Field(
        default=None, description="Expected HTTP status code"
    )
    expected_contains: Optional[str] = Field(
        default=None, description="Text that response should contain"
    )
    timeout: Optional[int] = Field(
        default=30, description="Request timeout in seconds", ge=1, le=300
    )

    @validator("headers", pre=True)
    def parse_headers(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                headers = {}
                for item in v.split(","):
                    if ":" in item:
                        key, value = item.split(":", 1)
                        headers[key.strip()] = value.strip()
                return headers
        return v

    @validator("method")
    def validate_method(cls, v):
        if v.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            raise ValueError("Method must be GET, POST, PUT, DELETE, or PATCH")
        return v.upper()

    @validator("url")
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class DatabaseConnectInputSchema(ToolInputSchema):
    host: str = Field(description="SQL Server host")
    port: Optional[int] = Field(
        default=None, description="SQL Server port (default: 1433)"
    )
    database: str = Field(description="Database name")
    username: Optional[str] = Field(
        default=None, description="Username (optional, uses default if not provided)"
    )
    password: Optional[str] = Field(
        default=None, description="Password (optional, uses default if not provided)"
    )
    connection_name: Optional[str] = Field(
        default="default", description="Connection identifier"
    )
    packet_size: Optional[int] = Field(
        default=None, description="SQL Server packet size"
    )
    trust_server_certificate: Optional[bool] = Field(
        default=None, description="Trust server certificate"
    )
    integrated_security: Optional[bool] = Field(
        default=None, description="Use integrated security"
    )
    connection_timeout: Optional[int] = Field(
        default=None, description="Connection timeout in seconds"
    )


class DatabaseQueryInputSchema(ToolInputSchema):
    query: str = Field(description="SQL query to execute")
    connection_name: Optional[str] = Field(
        default="default", description="Connection identifier"
    )
    params: Optional[List[Any]] = Field(default=None, description="Query parameters")


class DatabaseExecuteInputSchema(ToolInputSchema):
    query: str = Field(description="SQL statement to execute (INSERT/UPDATE/DELETE)")
    connection_name: Optional[str] = Field(
        default="default", description="Connection identifier"
    )
    params: Optional[List[Any]] = Field(default=None, description="Query parameters")


class DatabaseListTablesInputSchema(ToolInputSchema):
    connection_name: Optional[str] = Field(
        default="default", description="Connection identifier"
    )
    schema_name: Optional[str] = Field(
        default=None, description="Schema name to filter tables"
    )


class DatabaseDescribeTableInputSchema(ToolInputSchema):
    table_name: str = Field(description="Table name to describe")
    connection_name: Optional[str] = Field(
        default="default", description="Connection identifier"
    )
    schema_name: Optional[str] = Field(default=None, description="Schema name")


class DatabaseCloseInputSchema(ToolInputSchema):
    connection_name: Optional[str] = Field(
        default="default", description="Connection identifier"
    )


class GetPageHtmlInputSchema(ToolInputSchema):
    """Input schema for getting complete page HTML optimized for element mapping"""

    format_html: bool = Field(
        default=True, description="Format HTML with line breaks for readability"
    )
    max_length: int = Field(
        default=150000,
        description="Maximum HTML length before truncation",
        ge=10000,
        le=500000,
    )


class GetPageContentInputSchema(ToolInputSchema):
    """Input schema for getting page content with options"""

    include_meta: bool = Field(
        default=False, description="Include meta tags in the output"
    )
    include_links: bool = Field(
        default=False, description="Include links in the output"
    )
    include_images: bool = Field(
        default=False, description="Include images in the output"
    )
    max_length: int = Field(
        default=50000, description="Maximum length of text content", ge=1000, le=200000
    )


# Add new schemas here
