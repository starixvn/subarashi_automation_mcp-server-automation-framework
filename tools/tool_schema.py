from typing import Dict, Any, List, Optional, Callable, Awaitable, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError

if TYPE_CHECKING:
    from context import ServerContext


class ToolCapability(str, Enum):

    CORE = "core"
    VISION = "vision"
    TABS = "tabs"
    CONSOLE = "console"
    KEYBOARD = "keyboard"
    NETWORK = "network"
    FILES = "files"
    TESTING = "testing"
    WAIT = "wait"
    PDF = "pdf"
    HISTORY = "history"
    INSTALL = "install"
    API = "api"
    GOOGLE_SHEETS = "google_sheets"
    DATABASE = "database"


class ToolType(str, Enum):

    READ_ONLY = "readOnly"
    DESTRUCTIVE = "destructive"


class ToolInputSchema(BaseModel):

    class Config:
        extra = "forbid"
        validate_assignment = True


@dataclass
class ToolActionResult:

    content: Optional[List[Dict[str, Any]]] = None


@dataclass
class ToolResult:

    code: List[str]
    action: Optional[Callable[[], Awaitable[ToolActionResult]]] = None
    capture_snapshot: bool = False
    wait_for_network: bool = False
    result_override: Optional[ToolActionResult] = None


@dataclass
class ToolSchema:

    name: str
    title: str
    description: str
    input_schema: type[ToolInputSchema]
    tool_type: ToolType


class ModalStateType(str, Enum):

    DIALOG = "dialog"
    FILE_CHOOSER = "fileChooser"


@dataclass
class Tool:

    capability: ToolCapability
    schema: ToolSchema
    handle: Callable[["ServerContext", Dict[str, Any]], Awaitable[ToolResult]]
    clears_modal_state: Optional[str] = None
    browser_independent: bool = False  # Flag for tools that don't need browser context


ToolFactory = Callable[[bool], Tool]


def define_tool(
    capability: ToolCapability,
    name: str,
    title: str,
    description: str,
    input_schema: type[ToolInputSchema],
    tool_type: ToolType = ToolType.READ_ONLY,
    clears_modal_state: Optional[ModalStateType] = None,
) -> Callable[[Callable], Tool]:

    def decorator(
        func: Callable[["ServerContext", Dict[str, Any]], Awaitable[ToolResult]],
    ) -> Tool:
        schema = ToolSchema(
            name=name,
            title=title,
            description=description,
            input_schema=input_schema,
            tool_type=tool_type,
        )

        return Tool(
            capability=capability,
            schema=schema,
            clears_modal_state=clears_modal_state,
            handle=func,
        )

    return decorator


def define_tool_factory(
    capability: ToolCapability,
    name: str,
    title: str,
    description: str,
    input_schema: type[ToolInputSchema],
    tool_type: ToolType = ToolType.READ_ONLY,
    clears_modal_state: Optional[ModalStateType] = None,
) -> Callable[[Callable], ToolFactory]:

    def decorator(factory_func: Callable[[bool], Tool]) -> ToolFactory:
        return factory_func

    return decorator


def validate_tool_input(
    input_schema: type[ToolInputSchema], params: Dict[str, Any]
) -> ToolInputSchema:
    """Validate tool input parameters using Pydantic."""
    try:
        return input_schema(**params)
    except ValidationError as e:
        raise ValueError(f"Invalid input parameters: {e}")


def tool_to_mcp_schema(tool: Tool) -> Dict[str, Any]:
    pydantic_schema = tool.schema.input_schema.model_json_schema()

    return {
        "name": tool.schema.name,
        "description": tool.schema.description,
        "inputSchema": pydantic_schema,
        "annotations": {
            "title": tool.schema.title,
            "readOnlyHint": tool.schema.tool_type == ToolType.READ_ONLY,
            "destructiveHint": tool.schema.tool_type == ToolType.DESTRUCTIVE,
            "openWorldHint": True,
        },
    }


def filter_tools_by_capabilities(
    tools: List[Tool], capabilities: Optional[List[ToolCapability]] = None
) -> List[Tool]:
    if capabilities is None:
        return tools

    allowed_capabilities = set(capabilities)
    allowed_capabilities.add(ToolCapability.CORE)

    return [tool for tool in tools if tool.capability in allowed_capabilities]
