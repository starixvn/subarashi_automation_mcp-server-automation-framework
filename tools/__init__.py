from .tool_schema import (
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
    ToolFactory,
    ToolInputSchema,
    define_tool,
    define_tool_factory,
    validate_tool_input,
    tool_to_mcp_schema,
    filter_tools_by_capabilities,
)

from .registry import EnhancedToolRegistry

from .schemas import (
    EmptyInputSchema,
    NavigateInputSchema,
    ResizeInputSchema,
    ClickInputSchema,
    TypeInputSchema,
    HoverInputSchema,
    SelectOptionInputSchema,
    ScreenshotInputSchema,
    SaveScreenshotInputSchema,
    ScreenClickInputSchema,
    ScreenDragInputSchema,
    ScreenTypeInputSchema,
    ScreenMoveMouseInputSchema,
    DialogInputSchema,
    SelectTabInputSchema,
    NewTabInputSchema,
    CloseTabInputSchema,
    GetTextInputSchema,
    WaitForSelectorInputSchema,
    DragInputSchema,
    WaitForInputSchema,
    PressKeyInputSchema,
    SetRequestInterceptionInputSchema,
    UploadFileInputSchema,
    ApiRequestInputSchema,
    ApiTestInputSchema,
    DatabaseConnectInputSchema,
    DatabaseQueryInputSchema,
    DatabaseExecuteInputSchema,
    DatabaseListTablesInputSchema,
    DatabaseDescribeTableInputSchema,
    DatabaseCloseInputSchema,
    GetPageHtmlInputSchema,
    GetPageContentInputSchema,
)

from .core import get_core_tools
from .interaction import get_interaction_tools
from .snapshot import get_snapshot_tools, SNAPSHOT_TOOLS
from .vision import get_vision_tools, get_screenshot_tools
from .tabs import get_tab_tools
from .dialogs import get_dialog_tools
from .console import get_console_tools
from .keyboard import get_keyboard_tools
from .network import get_network_tools
from .files import get_file_tools
from .wait import get_wait_tools
from .pdf import get_pdf_tools
from .testing import get_testing_tools
from .api import get_api_tools
from .google_sheets import get_google_sheets_tools
from .database import get_database_tools
from .page_content import get_page_content_tools, PAGE_CONTENT_TOOLS

ALL_TOOLS = [
    *get_core_tools(),
    *get_vision_tools(),
    *get_screenshot_tools(),
    *get_tab_tools(),
    *get_dialog_tools(),
    *get_interaction_tools(),
    *SNAPSHOT_TOOLS,
    *get_console_tools(),
    *get_keyboard_tools(),
    *get_network_tools(),
    *get_file_tools(),
    *get_wait_tools(),
    *get_pdf_tools(),
    *get_testing_tools(),
    *get_api_tools(),
    *get_google_sheets_tools(),
    *get_database_tools(),
    *PAGE_CONTENT_TOOLS,
]


def get_all_tools(capabilities=None, capture_snapshot=True):
    all_tools = []

    if not capabilities or ToolCapability.CORE in capabilities:
        all_tools.extend(get_core_tools(capture_snapshot))

    if not capabilities or ToolCapability.VISION in capabilities:
        all_tools.extend(get_vision_tools(capture_snapshot))
        all_tools.extend(get_screenshot_tools(capture_snapshot))

    if not capabilities or ToolCapability.TABS in capabilities:
        all_tools.extend(get_tab_tools(capture_snapshot))

    if not capabilities or ToolCapability.CONSOLE in capabilities:
        all_tools.extend(get_console_tools(capture_snapshot))

    if not capabilities or ToolCapability.KEYBOARD in capabilities:
        all_tools.extend(get_keyboard_tools(capture_snapshot))

    if not capabilities or ToolCapability.NETWORK in capabilities:
        all_tools.extend(get_network_tools(capture_snapshot))

    if not capabilities or ToolCapability.FILES in capabilities:
        all_tools.extend(get_file_tools(capture_snapshot))

    if not capabilities or ToolCapability.TESTING in capabilities:
        all_tools.extend(get_testing_tools(capture_snapshot))

    if not capabilities or ToolCapability.WAIT in capabilities:
        all_tools.extend(get_wait_tools(capture_snapshot))

    if not capabilities or ToolCapability.PDF in capabilities:
        all_tools.extend(get_pdf_tools(capture_snapshot))

    if not capabilities or ToolCapability.API in capabilities:
        all_tools.extend(get_api_tools(capture_snapshot))

    if not capabilities or ToolCapability.GOOGLE_SHEETS in capabilities:
        all_tools.extend(get_google_sheets_tools())

    if not capabilities or ToolCapability.DATABASE in capabilities:
        all_tools.extend(get_database_tools(capture_snapshot))

    all_tools.extend(get_page_content_tools(capture_snapshot))
    all_tools.extend(get_dialog_tools(capture_snapshot))
    all_tools.extend(get_interaction_tools(capture_snapshot))
    all_tools.extend(get_snapshot_tools(capture_snapshot))

    return all_tools


__all__ = [
    "ToolCapability",
    "ToolType",
    "ToolResult",
    "ToolActionResult",
    "Tool",
    "ToolSchema",
    "ToolFactory",
    "ToolInputSchema",
    "define_tool",
    "define_tool_factory",
    "validate_tool_input",
    "tool_to_mcp_schema",
    "filter_tools_by_capabilities",
    "EnhancedToolRegistry",
    "EmptyInputSchema",
    "NavigateInputSchema",
    "ResizeInputSchema",
    "ClickInputSchema",
    "TypeInputSchema",
    "HoverInputSchema",
    "SelectOptionInputSchema",
    "ScreenshotInputSchema",
    "SaveScreenshotInputSchema",
    "ScreenClickInputSchema",
    "ScreenDragInputSchema",
    "ScreenTypeInputSchema",
    "ScreenMoveMouseInputSchema",
    "DialogInputSchema",
    "SelectTabInputSchema",
    "NewTabInputSchema",
    "CloseTabInputSchema",
    "GetTextInputSchema",
    "WaitForSelectorInputSchema",
    "DragInputSchema",
    "WaitForInputSchema",
    "PressKeyInputSchema",
    "SetRequestInterceptionInputSchema",
    "UploadFileInputSchema",
    "ApiRequestInputSchema",
    "ApiTestInputSchema",
    "DatabaseConnectInputSchema",
    "DatabaseQueryInputSchema",
    "DatabaseExecuteInputSchema",
    "DatabaseListTablesInputSchema",
    "DatabaseDescribeTableInputSchema",
    "DatabaseCloseInputSchema",
    "GetPageHtmlInputSchema",
    "GetPageContentInputSchema",
    "get_core_tools",
    "get_interaction_tools",
    "get_snapshot_tools",
    "SNAPSHOT_TOOLS",
    "get_vision_tools",
    "get_screenshot_tools",
    "get_tab_tools",
    "get_dialog_tools",
    "get_console_tools",
    "get_keyboard_tools",
    "get_network_tools",
    "get_file_tools",
    "get_wait_tools",
    "get_pdf_tools",
    "get_testing_tools",
    "get_api_tools",
    "ALL_TOOLS",
    "get_all_tools",
    "get_google_sheets_tools",
    "get_database_tools",
    "get_page_content_tools",
    "PAGE_CONTENT_TOOLS",
]
