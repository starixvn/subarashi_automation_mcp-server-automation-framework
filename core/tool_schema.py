from typing import Optional, List, Dict, Any, Literal, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel

from core.modal_state import ModalStateType


class ToolType(Enum):
    READ_ONLY = "read_only"
    DESTRUCTIVE = "destructive"


class ToolCapability(Enum):
    CORE = "core"
    VISION = "vision"
    TABS = "tabs"
    CONSOLE = "console"
    KEYBOARD = "keyboard"
    NETWORK = "network"
    FILES = "files"
    WAIT = "wait"
    PDF = "pdf"
    API = "api"
    GOOGLE_SHEETS = "google_sheets"
    DATABASE = "database"
    PAGE_CONTENT = "page_content"
    HISTORY = "history"


class ToolInputSchema(BaseModel):
    class Config:
        extra = "forbid"


@dataclass
class ToolActionResult:
    content: List[Dict[str, Any]]


@dataclass
class ToolResult:
    code: Any
    action: Optional[Callable[[], Awaitable[ToolActionResult]]] = None
    result_override: Optional[ToolActionResult] = None
    capture_snapshot: bool = True
    wait_for_network: bool = False


@dataclass
class ToolSchema:
    name: str
    title: str
    description: str
    input_schema: type[ToolInputSchema]
    tool_type: ToolType


@dataclass
class Tool:
    capability: ToolCapability
    schema: ToolSchema
    handle: Callable[["ServerContext", Dict[str, Any]], Awaitable[ToolResult]]
    clears_modal_state: Optional[str] = None
    browser_independent: bool = False


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
    def decorator(func: Callable[[bool], Tool]) -> ToolFactory:
        return func

    return decorator


def convert_to_google_compatible_schema(
    pydantic_schema: Dict[str, Any],
) -> Dict[str, Any]:
    def fix_property(prop: Dict[str, Any]) -> Dict[str, Any]:
        prop = prop.copy()

        if "anyOf" in prop:
            main_type = None
            is_nullable = False

            for option in prop["anyOf"]:
                if option.get("type") == "null":
                    is_nullable = True
                elif option.get("type"):
                    if main_type is None:
                        main_type = option

            if main_type:
                prop = {**prop, **main_type}
                del prop["anyOf"]

        if isinstance(prop.get("type"), list):
            for t in prop["type"]:
                if t != "null":
                    prop["type"] = t
                    break
            else:
                prop["type"] = "string"

        if "properties" in prop:
            prop["properties"] = {
                k: fix_property(v) for k, v in prop["properties"].items()
            }

        if "items" in prop:
            if not prop["items"] or prop["items"] == {}:
                prop["items"] = {"type": "object"}
            else:
                prop["items"] = fix_property(prop["items"])

        return prop

    result = pydantic_schema.copy()

    if "properties" in result:
        result["properties"] = {
            k: fix_property(v) for k, v in result["properties"].items()
        }

    return result


def tool_to_mcp_schema(tool: Tool) -> Dict[str, Any]:
    pydantic_schema = tool.schema.input_schema.model_json_schema()

    compatible_schema = convert_to_google_compatible_schema(pydantic_schema)

    return {
        "name": tool.schema.name,
        "description": tool.schema.description,
        "inputSchema": compatible_schema,
        "annotations": {
            "title": tool.schema.title,
            "readOnlyHint": tool.schema.tool_type == ToolType.READ_ONLY,
            "destructiveHint": tool.schema.tool_type == ToolType.DESTRUCTIVE,
            "openWorldHint": True,
        },
    }


def filter_tools_by_capabilities(
    tools: List[Tool], capabilities: Optional[List[ToolCapability]]
) -> List[Tool]:
    if not capabilities:
        return tools

    return [tool for tool in tools if tool.capability in capabilities]


def validate_tool_input(schema_class: type[ToolInputSchema], params: Dict[str, Any]):
    try:
        return schema_class(**params)
    except Exception as e:
        raise ValueError(f"Invalid tool input: {e}")
