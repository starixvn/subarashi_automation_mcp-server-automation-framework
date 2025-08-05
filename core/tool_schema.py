from typing import (
    Optional,
    List,
    Dict,
    Any,
    Literal,
    Callable,
    Awaitable,
    TYPE_CHECKING,
)
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel

from core.modal_state import ModalStateType

if TYPE_CHECKING:
    from context import ServerContext


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


def convert_to_n8n_compatible_schema(
    pydantic_schema: Dict[str, Any],
) -> Dict[str, Any]:
    defs = pydantic_schema.get("$defs", {})

    def resolve_ref(ref_path: str) -> Dict[str, Any]:
        if ref_path.startswith("#/$defs/"):
            def_name = ref_path[8:]
            if def_name in defs:
                return defs[def_name].copy()
        return {"type": "object"}

    def fix_property(prop: Dict[str, Any]) -> Dict[str, Any]:
        prop = prop.copy()

        if "$ref" in prop:
            resolved = resolve_ref(prop["$ref"])
            prop = fix_property(resolved)
            return prop

        if "anyOf" in prop:
            main_type = None
            is_nullable = False
            ref_resolved = None
            preferred_type = None

            def flatten_anyof_options(options, depth=0):
                if depth > 3:
                    return options

                flattened = []
                for option in options:
                    if "anyOf" in option:
                        constraints = {k: v for k, v in option.items() if k != "anyOf"}
                        nested_options = flatten_anyof_options(
                            option["anyOf"], depth + 1
                        )
                        for nested_option in nested_options:
                            merged_option = nested_option.copy()
                            merged_option.update(constraints)
                            flattened.append(merged_option)
                    else:
                        flattened.append(option)
                return flattened

            flattened_options = flatten_anyof_options(prop["anyOf"])

            for option in flattened_options:
                if option.get("type") == "null":
                    is_nullable = True
                elif "$ref" in option:
                    ref_resolved = resolve_ref(option["$ref"])
                elif option.get("type"):
                    option_type = option.get("type")
                    if option_type in [
                        "integer",
                        "number",
                        "boolean",
                        "array",
                        "object",
                    ]:
                        preferred_type = option.copy()
                    elif main_type is None:
                        main_type = option.copy()
                elif "anyOf" not in option and not option.get("type"):
                    if preferred_type and not preferred_type.get("constraints_added"):
                        preferred_type.update(
                            {
                                k: v
                                for k, v in option.items()
                                if k not in ["type", "anyOf"]
                            }
                        )
                        preferred_type["constraints_added"] = True

            if ref_resolved:
                prop.update(fix_property(ref_resolved))
                del prop["anyOf"]
                if is_nullable:
                    prop["nullable"] = True
            elif preferred_type:
                del prop["anyOf"]
                if "constraints_added" in preferred_type:
                    del preferred_type["constraints_added"]
                prop.update(preferred_type)
                if is_nullable:
                    base_type = preferred_type.get("type")
                    if base_type:
                        prop["type"] = [base_type, "null"]
            elif main_type:
                prop.update(main_type)
                del prop["anyOf"]
                if is_nullable:
                    base_type = main_type.get("type")
                    if base_type:
                        prop["type"] = [base_type, "null"]

        if isinstance(prop.get("type"), list):
            type_list = prop["type"]
            if "null" in type_list and len(type_list) == 2:
                pass
            else:
                for t in type_list:
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

        if "additionalProperties" in prop:
            del prop["additionalProperties"]

        if "ge" in prop:
            prop["minimum"] = prop.pop("ge")
        if "le" in prop:
            prop["maximum"] = prop.pop("le")
        if "gt" in prop:
            prop["exclusiveMinimum"] = prop.pop("gt")
        if "lt" in prop:
            prop["exclusiveMaximum"] = prop.pop("lt")
        if prop.get("nullable") and prop.get("type") in [
            "object",
            "array",
            "string",
            "integer",
            "number",
            "boolean",
        ]:
            base_type = prop.get("type")
            prop["type"] = [base_type, "null"]
            del prop["nullable"]
        if (
            prop.get("type") == "string"
            and prop.get("default") is None
            and not prop.get("nullable")
            and not isinstance(prop.get("type"), list)
        ):
            prop["type"] = ["string", "null"]

        if (
            prop.get("type") in ["integer", "number", "boolean", "array", "object"]
            and prop.get("default") is None
            and not prop.get("nullable")
            and not isinstance(prop.get("type"), list)
        ):
            base_type = prop.get("type")
            prop["type"] = [base_type, "null"]

        return prop

    result = pydantic_schema.copy()

    if "$defs" in result:
        del result["$defs"]

    if "properties" in result:
        result["properties"] = {
            k: fix_property(v) for k, v in result["properties"].items()
        }

    if "additionalProperties" in result:
        del result["additionalProperties"]

    if "required" in result and not isinstance(result["required"], list):
        result["required"] = []

    return result


def tool_to_mcp_schema(tool: Tool) -> Dict[str, Any]:
    try:
        pydantic_schema = tool.schema.input_schema.model_json_schema()
        compatible_schema = convert_to_n8n_compatible_schema(pydantic_schema)
        if compatible_schema.get("type") != "object":
            compatible_schema = {
                "type": "object",
                "properties": {"value": compatible_schema},
                "required": ["value"],
            }

        if "properties" not in compatible_schema:
            compatible_schema["properties"] = {}

        mcp_schema = {
            "name": tool.schema.name,
            "description": tool.schema.description or "",
            "inputSchema": compatible_schema,
            "annotations": {
                "title": tool.schema.title,
                "readOnlyHint": tool.schema.tool_type == ToolType.READ_ONLY,
                "destructiveHint": tool.schema.tool_type == ToolType.DESTRUCTIVE,
                "openWorldHint": True,
            },
        }

        if hasattr(tool, "clears_modal_state") and tool.clears_modal_state:
            mcp_schema["clearsModalState"] = tool.clears_modal_state

        return mcp_schema

    except Exception as e:
        return {
            "name": tool.schema.name,
            "description": tool.schema.description or f"Tool: {tool.schema.name}",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
            "annotations": {
                "title": tool.schema.title,
                "readOnlyHint": False,
                "destructiveHint": False,
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
