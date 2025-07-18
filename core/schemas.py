from typing import Optional, List, Dict, Any, Literal, Union
import json
from pydantic import Field, field_validator
from core.tool_schema import ToolInputSchema


class EmptyInputSchema(ToolInputSchema):
    pass


class NavigateInputSchema(ToolInputSchema):
    url: str = Field(description="The URL to navigate to")

    @field_validator("url")
    @classmethod
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
    full_page: Optional[Union[bool, str]] = Field(
        default=True, description="Take full page screenshot instead of viewport only"
    )
    quality: Optional[Union[int, str]] = Field(
        default=80,
        ge=1,
        le=100,
        description="Image quality for JPEG format (1-100, higher is better)",
    )
    format: Optional[Literal["png", "jpeg"]] = Field(
        default="png",
        description="Image format - PNG for lossless, JPEG for smaller file size",
    )
    element_selector: Optional[str] = Field(
        default=None, description="CSS selector to screenshot only specific element"
    )
    clip_region: Optional[Dict[str, int]] = Field(
        default=None,
        description="Clip region as {x, y, width, height} for partial screenshot",
    )
    omit_background: Optional[Union[bool, str]] = Field(
        default=False, description="Hide default white background for transparent PNG"
    )
    scale: Optional[Literal["css", "device"]] = Field(
        default="css",
        description="Whether to use CSS pixels or device pixels for scaling",
    )

    @field_validator("full_page", "omit_background", mode="before")
    @classmethod
    def convert_string_to_bool(cls, v):
        """Convert string representations to boolean for LLM compatibility"""
        if isinstance(v, str):
            if v.lower() in ("true", "1", "yes", "on"):
                return True
            elif v.lower() in ("false", "0", "no", "off"):
                return False
        return v

    @field_validator("quality", mode="before")
    @classmethod
    def convert_string_to_int(cls, v):
        """Convert string representations to int for LLM compatibility"""
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                pass
        return v

    @field_validator("clip_region")
    @classmethod
    def validate_clip_region(cls, v):
        if v is not None:
            required_keys = {"x", "y", "width", "height"}
            if not all(key in v for key in required_keys):
                raise ValueError(f"clip_region must contain {required_keys}")
            if any(val < 0 for val in v.values()):
                raise ValueError("clip_region coordinates must be non-negative")
            if v["width"] <= 0 or v["height"] <= 0:
                raise ValueError("clip_region width and height must be positive")
        return v


class SaveScreenshotInputSchema(ToolInputSchema):
    filename: str = Field(description="Filename for the screenshot")
    full_page: Optional[Union[bool, str]] = Field(
        default=True, description="Take full page screenshot"
    )
    quality: Optional[Union[int, str]] = Field(
        default=80, ge=1, le=100, description="Image quality for JPEG format"
    )
    format: Optional[Literal["png", "jpeg"]] = Field(
        default="png", description="Image format"
    )
    element_selector: Optional[str] = Field(
        default=None, description="CSS selector to screenshot only specific element"
    )
    clip_region: Optional[Dict[str, int]] = Field(
        default=None, description="Clip region as {x, y, width, height}"
    )
    create_directories: Optional[Union[bool, str]] = Field(
        default=True, description="Create parent directories if they don't exist"
    )
    overwrite: Optional[Union[bool, str]] = Field(
        default=True, description="Overwrite existing file if it exists"
    )

    @field_validator("full_page", "create_directories", "overwrite", mode="before")
    @classmethod
    def convert_string_to_bool(cls, v):
        if isinstance(v, str):
            if v.lower() in ("true", "1", "yes", "on"):
                return True
            elif v.lower() in ("false", "0", "no", "off"):
                return False
        return v

    @field_validator("quality", mode="before")
    @classmethod
    def convert_string_to_int(cls, v):
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                pass
        return v

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v):
        if not v.strip():
            raise ValueError("Filename cannot be empty")

        import os

        if ".." in v or os.path.isabs(v):
            raise ValueError("Filename cannot contain '..' or be absolute path")

        valid_extensions = {".png", ".jpg", ".jpeg"}
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            v += ".png"

        return v.strip()

    @field_validator("clip_region")
    @classmethod
    def validate_clip_region(cls, v):
        if v is not None:
            required_keys = {"x", "y", "width", "height"}
            if not all(key in v for key in required_keys):
                raise ValueError(f"clip_region must contain {required_keys}")
            if any(val < 0 for val in v.values()):
                raise ValueError("clip_region coordinates must be non-negative")
            if v["width"] <= 0 or v["height"] <= 0:
                raise ValueError("clip_region width and height must be positive")
        return v


class PdfInputSchema(ToolInputSchema):
    """Schema for PDF generation operations"""

    filename: str = Field(description="Filename for the PDF file")
    full_page: Optional[bool] = Field(default=True, description="Save full page as PDF")
    format: Optional[Literal["A4", "A3", "Letter", "Legal"]] = Field(
        default="A4", description="Paper format for PDF"
    )
    landscape: Optional[bool] = Field(
        default=False, description="Use landscape orientation"
    )
    margin: Optional[Dict[str, str]] = Field(
        default=None, description="Page margins as {top, right, bottom, left}"
    )
    scale: Optional[float] = Field(
        default=1.0, ge=0.1, le=2.0, description="Scale factor for PDF generation"
    )
    print_background: Optional[bool] = Field(
        default=True, description="Include background graphics in PDF"
    )
    header_template: Optional[str] = Field(
        default=None, description="HTML template for page header"
    )
    footer_template: Optional[str] = Field(
        default=None, description="HTML template for page footer"
    )
    display_header_footer: Optional[bool] = Field(
        default=False, description="Display header and footer"
    )

    @field_validator("filename")
    @classmethod
    def validate_pdf_filename(cls, v):
        if not v.strip():
            raise ValueError("Filename cannot be empty")

        import os

        if ".." in v or os.path.isabs(v):
            raise ValueError("Filename cannot contain '..' or be absolute path")

        # For PDF files, ensure .pdf extension
        if not v.lower().endswith(".pdf"):
            v += ".pdf"

        return v.strip()

    @field_validator("margin")
    @classmethod
    def validate_margin(cls, v):
        if v is not None:
            required_keys = {"top", "right", "bottom", "left"}
            if not all(key in v for key in required_keys):
                raise ValueError("margin must contain top, right, bottom, left")
            # Validate margin values are valid CSS units
            for key, value in v.items():
                if not isinstance(value, str) or not value.strip():
                    raise ValueError(f"margin.{key} must be a non-empty string")
        return v


class ScreenClickInputSchema(ToolInputSchema):
    element: str = Field(description="Human-readable element description")
    x: int = Field(description="X coordinate", ge=0)
    y: int = Field(description="Y coordinate", ge=0)
    click_type: Optional[Literal["left", "right", "double", "middle"]] = Field(
        default="left", description="Type of click to perform"
    )
    modifiers: Optional[List[Literal["Alt", "Control", "Meta", "Shift"]]] = Field(
        default_factory=list, description="Keyboard modifiers to hold during click"
    )
    button_delay: Optional[int] = Field(
        default=0,
        ge=0,
        le=5000,
        description="Delay between mousedown and mouseup in milliseconds",
    )
    click_count: Optional[int] = Field(
        default=1,
        ge=1,
        le=3,
        description="Number of clicks to perform (1=single, 2=double, 3=triple)",
    )
    force: Optional[bool] = Field(
        default=False,
        description="Force click even if coordinates are outside viewport",
    )
    validate_bounds: Optional[bool] = Field(
        default=True, description="Validate coordinates are within viewport bounds"
    )

    @field_validator("modifiers")
    @classmethod
    def validate_modifiers(cls, v):
        if v:
            seen = set()
            result = []
            for modifier in v:
                if modifier not in seen:
                    seen.add(modifier)
                    result.append(modifier)
            return result
        return v or []


class ScreenDragInputSchema(ToolInputSchema):
    element: str = Field(description="Human-readable element description")
    from_x: int = Field(description="Starting X coordinate", ge=0)
    from_y: int = Field(description="Starting Y coordinate", ge=0)
    to_x: int = Field(description="Ending X coordinate", ge=0)
    to_y: int = Field(description="Ending Y coordinate", ge=0)
    modifiers: Optional[List[Literal["Alt", "Control", "Meta", "Shift"]]] = Field(
        default_factory=list, description="Keyboard modifiers to hold during drag"
    )
    steps: Optional[int] = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of intermediate steps for smooth dragging",
    )
    validate_bounds: Optional[bool] = Field(
        default=True, description="Validate coordinates are within viewport bounds"
    )

    @field_validator("modifiers")
    @classmethod
    def validate_modifiers(cls, v):
        if v:
            seen = set()
            result = []
            for modifier in v:
                if modifier not in seen:
                    seen.add(modifier)
                    result.append(modifier)
            return result
        return v or []


class ScreenTypeInputSchema(ToolInputSchema):
    element: str = Field(description="Human-readable element description")
    x: int = Field(description="X coordinate to click before typing", ge=0)
    y: int = Field(description="Y coordinate to click before typing", ge=0)
    text: str = Field(description="Text to type")
    delay: Optional[int] = Field(
        default=0, ge=0, le=1000, description="Delay between keystrokes in milliseconds"
    )
    clear_first: Optional[bool] = Field(
        default=False, description="Clear existing text before typing"
    )
    validate_bounds: Optional[bool] = Field(
        default=True, description="Validate coordinates are within viewport bounds"
    )


class ScreenMoveMouseInputSchema(ToolInputSchema):
    element: str = Field(description="Human-readable element description")
    x: int = Field(description="X coordinate", ge=0)
    y: int = Field(description="Y coordinate", ge=0)
    steps: Optional[int] = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of intermediate steps for smooth movement",
    )
    validate_bounds: Optional[bool] = Field(
        default=True, description="Validate coordinates are within viewport bounds"
    )


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

    @field_validator("time", "text", "text_gone")
    @classmethod
    def validate_at_least_one(cls, v, info):
        field_name = info.field_name
        data = info.data

        if not any([data.get("time"), data.get("text"), data.get("text_gone"), v]):
            raise ValueError(
                "At least one of time, text, or text_gone must be provided"
            )
        return v


class PressKeyInputSchema(ToolInputSchema):
    key: str = Field(description="Name of the key to press or character to generate")

    @field_validator("key")
    @classmethod
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

    @field_validator("file_paths")
    @classmethod
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
    headers: Optional[Union[Dict[str, str], str]] = Field(
        default=None, description="HTTP headers"
    )
    body: Optional[str] = Field(
        default=None, description="Request body for POST/PUT/PATCH"
    )
    timeout: Optional[int] = Field(
        default=30, description="Request timeout in seconds", ge=1, le=300
    )

    @field_validator("headers", mode="before")
    @classmethod
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

    @field_validator("method")
    @classmethod
    def validate_method(cls, v):
        allowed_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        if v.upper() not in allowed_methods:
            raise ValueError(f"Method must be one of: {', '.join(allowed_methods)}")
        return v.upper()

    @field_validator("url")
    @classmethod
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


class EvaluateJavaScriptInputSchema(ToolInputSchema):
    function: str = Field(
        description="JavaScript function to evaluate: '() => { /* code */ }' or '(element) => { /* code */ }' when element is provided"
    )
    element: Optional[str] = Field(
        default=None,
        description="Human-readable element description used to obtain permission to interact with the element",
    )
    ref: Optional[str] = Field(
        default=None,
        description="Exact target element reference from the page snapshot",
    )


# Add new schemas here
