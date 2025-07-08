import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING

from .tool_schema import (
    Tool,
    ToolCapability,
    ToolResult,
    ToolActionResult,
    filter_tools_by_capabilities,
    tool_to_mcp_schema,
    validate_tool_input,
)

from .core import get_core_tools
from .interaction import get_interaction_tools
from .vision import get_vision_tools
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
from .vision import get_vision_screen_tools, get_screenshot_tools       
from .snapshot import get_snapshot_tools
from .utils import wait_for_completion
from .google_sheets import GOOGLE_SHEETS_TOOLS
from .google_sheets_advanced import GOOGLE_SHEETS_ADVANCED_TOOLS
from .google_sheets_export import GOOGLE_SHEETS_EXPORT_TOOLS
from .database import get_database_tools
from .page_content import get_page_content_tools
# Import new tools here

if TYPE_CHECKING:
    from ..context import ServerContext

logger = logging.getLogger(__name__)


def create_snapshot_tools() -> List[Tool]:
    tools = []
    tools.extend(get_core_tools(capture_snapshot=True))
    tools.extend(get_interaction_tools(capture_snapshot=True))
    tools.extend(get_snapshot_tools(capture_snapshot=True))
    tools.extend(get_dialog_tools(capture_snapshot=True))
    tools.extend(get_tab_tools(capture_snapshot=True))
    tools.extend(get_screenshot_tools(capture_snapshot=True))
    tools.extend(get_console_tools(capture_snapshot=True))
    tools.extend(get_keyboard_tools(capture_snapshot=True))
    tools.extend(get_network_tools(capture_snapshot=True))
    tools.extend(get_file_tools(capture_snapshot=True))
    tools.extend(get_wait_tools(capture_snapshot=True))
    tools.extend(get_pdf_tools(capture_snapshot=True))
    tools.extend(get_testing_tools(capture_snapshot=True))
    tools.extend(get_api_tools(capture_snapshot=False))
    tools.extend(GOOGLE_SHEETS_TOOLS)
    tools.extend(GOOGLE_SHEETS_ADVANCED_TOOLS)
    tools.extend(GOOGLE_SHEETS_EXPORT_TOOLS)
    tools.extend(get_database_tools(capture_snapshot=True))
    tools.extend(get_page_content_tools(capture_snapshot=True))
    # Add new tools here

    return tools


def create_vision_tools() -> List[Tool]:
    tools = []
    tools.extend(get_core_tools(capture_snapshot=False))
    tools.extend(get_interaction_tools(capture_snapshot=False))
    tools.extend(get_snapshot_tools(capture_snapshot=False))
    tools.extend(get_dialog_tools(capture_snapshot=False))
    tools.extend(get_tab_tools(capture_snapshot=False))
    tools.extend(get_vision_screen_tools(capture_snapshot=False))
    tools.extend(get_console_tools(capture_snapshot=False))
    tools.extend(get_keyboard_tools(capture_snapshot=False))
    tools.extend(get_network_tools(capture_snapshot=False))
    tools.extend(get_file_tools(capture_snapshot=False))
    tools.extend(get_wait_tools(capture_snapshot=False))
    tools.extend(get_pdf_tools(capture_snapshot=False))
    tools.extend(get_testing_tools(capture_snapshot=False))
    tools.extend(get_api_tools(capture_snapshot=False))
    tools.extend(GOOGLE_SHEETS_TOOLS)
    tools.extend(GOOGLE_SHEETS_ADVANCED_TOOLS)
    tools.extend(GOOGLE_SHEETS_EXPORT_TOOLS)
    tools.extend(get_database_tools(capture_snapshot=False))
    tools.extend(get_page_content_tools(capture_snapshot=False))
    # Add new tools here
    return tools


snapshotTools = create_snapshot_tools()
visionTools = create_vision_tools()


class EnhancedToolRegistry:

    def __init__(
        self,
        context: "ServerContext",
        capabilities: Optional[List[ToolCapability]] = None,
    ):
        self.context = context
        self.capabilities = capabilities

        vision_mode = context.settings.enable_vision
        self._snapshot_tools = self._create_snapshot_tools()
        self._vision_tools = self._create_vision_tools()

        all_tools = self._vision_tools if vision_mode else self._snapshot_tools

        self._tools = filter_tools_by_capabilities(all_tools, capabilities)

        self._tool_lookup = {tool.schema.name: tool for tool in self._tools}

        logger.info(
            f"Initialized tool registry with {len(self._tools)} tools (vision={vision_mode})"
        )

    def _create_snapshot_tools(self) -> List[Tool]:
        tools = []

        tools.extend(get_core_tools(capture_snapshot=True))
        tools.extend(get_interaction_tools(capture_snapshot=True))
        tools.extend(get_snapshot_tools(capture_snapshot=True))
        tools.extend(get_dialog_tools(capture_snapshot=True))
        tools.extend(get_tab_tools(capture_snapshot=True))
        tools.extend(get_screenshot_tools(capture_snapshot=True))
        tools.extend(get_console_tools(capture_snapshot=True))
        tools.extend(get_keyboard_tools(capture_snapshot=True))
        tools.extend(get_network_tools(capture_snapshot=True))
        tools.extend(get_file_tools(capture_snapshot=True))
        tools.extend(get_wait_tools(capture_snapshot=True))
        tools.extend(get_pdf_tools(capture_snapshot=True))
        tools.extend(get_testing_tools(capture_snapshot=True))
        tools.extend(get_api_tools(capture_snapshot=False))
        tools.extend(GOOGLE_SHEETS_TOOLS)
        tools.extend(GOOGLE_SHEETS_ADVANCED_TOOLS)
        tools.extend(GOOGLE_SHEETS_EXPORT_TOOLS)
        tools.extend(get_database_tools(capture_snapshot=True))
        tools.extend(get_page_content_tools(capture_snapshot=True))
        # Add new tools here
        return tools

    def _create_vision_tools(self) -> List[Tool]:
        tools = []

        tools.extend(get_core_tools(capture_snapshot=False))
        tools.extend(get_interaction_tools(capture_snapshot=False))
        tools.extend(get_snapshot_tools(capture_snapshot=False))
        tools.extend(get_dialog_tools(capture_snapshot=False))
        tools.extend(get_tab_tools(capture_snapshot=False))
        tools.extend(get_vision_screen_tools(capture_snapshot=False))
        tools.extend(get_console_tools(capture_snapshot=False))
        tools.extend(get_keyboard_tools(capture_snapshot=False))
        tools.extend(get_network_tools(capture_snapshot=False))
        tools.extend(get_file_tools(capture_snapshot=False))
        tools.extend(get_wait_tools(capture_snapshot=False))
        tools.extend(get_pdf_tools(capture_snapshot=False))
        tools.extend(get_testing_tools(capture_snapshot=False))
        tools.extend(get_api_tools(capture_snapshot=False))
        tools.extend(GOOGLE_SHEETS_TOOLS)
        tools.extend(GOOGLE_SHEETS_ADVANCED_TOOLS)
        tools.extend(GOOGLE_SHEETS_EXPORT_TOOLS)
        tools.extend(get_database_tools(capture_snapshot=False))
        tools.extend(get_page_content_tools(capture_snapshot=False))
        # Add new tools here
        return tools

    def get_all_tools(self) -> List[Tool]:
        return self._tools.copy()

    def get_tool_names(self) -> List[str]:
        return list(self._tool_lookup.keys())

    def get_tools_count(self) -> int:
        return len(self._tools)

    def get_tool_by_name(self, name: str) -> Optional[Tool]:
        return self._tool_lookup.get(name)

    def get_tools_by_capability(self, capability: ToolCapability) -> List[Tool]:
        return [tool for tool in self._tools if tool.capability == capability]

    def get_mcp_tools_schema(self) -> List[Dict[str, Any]]:
        schemas = []
        for tool in self._tools:
            schema = tool_to_mcp_schema(tool)
            if tool.clears_modal_state:
                schema["clearsModalState"] = tool.clears_modal_state
            schemas.append(schema)
        return schemas

    async def list_tools(self) -> List[Dict[str, Any]]:
        return self.get_mcp_tools_schema()

    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> ToolActionResult:
        tool = self._tool_lookup.get(tool_name)
        if not tool:
            raise KeyError(f"Tool '{tool_name}' not found")

        modal_states = self.context.modal_states()
        modal_state_types = [state.type.value for state in modal_states]

        if tool.clears_modal_state and tool.clears_modal_state not in modal_state_types:
            error_msg = f'The tool "{tool_name}" can only be used when there is related modal state present.'
            if modal_states:
                error_msg += "\n" + "\n".join(self.context.modal_states_markdown())
            return ToolActionResult(content=[{"type": "text", "text": error_msg}])

        if not tool.clears_modal_state and modal_state_types:
            error_msg = f'Tool "{tool_name}" does not handle the modal state.'
            error_msg += "\n" + "\n".join(self.context.modal_states_markdown())
            return ToolActionResult(content=[{"type": "text", "text": error_msg}])

        try:
            return await self._run_tool_typescript_style(tool, arguments)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return ToolActionResult(
                content=[
                    {
                        "type": "text",
                        "text": f"Error executing tool {tool_name}: {str(e)}",
                    }
                ]
            )

    async def _run_tool_typescript_style(
        self, tool: Tool, arguments: Dict[str, Any]
    ) -> ToolActionResult:
        validated_params = validate_tool_input(tool.schema.input_schema, arguments)

        if not tool.handle:
            raise Exception(f"Tool '{tool.schema.name}' has no handler")

        logger.debug(f"Executing tool {tool.schema.name} with arguments: {arguments}")
        tool_result = await tool.handle(self.context, arguments)

        if tool_result.result_override:
            return tool_result.result_override

        if getattr(tool, "browser_independent", False):
            if tool_result.action:
                action_result = await tool_result.action()
                if action_result and action_result.content:
                    return action_result

            result_lines = []
            result_lines.append("- Executed API operation:")
            result_lines.append("```js")
            if isinstance(tool_result.code, list):
                result_lines.extend(tool_result.code)
            else:
                result_lines.append(str(tool_result.code))
            result_lines.append("```")

            return ToolActionResult(
                content=[{"type": "text", "text": "\n".join(result_lines)}]
            )

        if not self.context._current_tab:
            return ToolActionResult(
                content=[
                    {
                        "type": "text",
                        "text": 'No open pages available. Use the "browser_navigate" tool to navigate to a page first.',
                    }
                ]
            )

        tab = self.context.current_tab_or_die()

        action_result = None
        if tool_result.action:
            logger.debug(f"Executing tool action for {tool.schema.name}")

            async def racing_action():
                return await self.context._race_against_modal_dialogs(
                    tool_result.action
                )

            if tool_result.wait_for_network:

                action_result = await wait_for_completion(
                    self.context, tab, racing_action
                )
            else:
                action_result = await racing_action()

        if tool_result.capture_snapshot and not self._javascript_blocked():
            await tab.capture_snapshot()

        result_lines = []
        result_lines.append("- Ran Playwright code:")
        result_lines.append("```js")

        if isinstance(tool_result.code, list):
            result_lines.extend(tool_result.code)
        else:
            logger.error(
                f"Tool {tool.schema.name} returned non-list code: {type(tool_result.code)}"
            )
            result_lines.append(str(tool_result.code))

        result_lines.append("```")
        result_lines.append("")

        if self.context.modal_states():
            result_lines.extend(self.context.modal_states_markdown())
            return ToolActionResult(
                content=[{"type": "text", "text": "\n".join(result_lines)}]
            )

        download_lines = self.context.get_downloads_markdown()
        if download_lines:
            result_lines.extend(download_lines)
            result_lines.append("")

        if len(self.context.tabs()) > 1:
            result_lines.append(await self.context.list_tabs_markdown())
            result_lines.append("")
            result_lines.append("### Current tab")

        result_lines.append(f"- Page URL: {tab.url()}")
        result_lines.append(f"- Page Title: {await tab.title()}")

        if tool_result.capture_snapshot and tab.has_snapshot():
            result_lines.append(tab.snapshot_or_die().text())

        content = []
        if action_result and action_result.content:
            content.extend(action_result.content)

        content.append({"type": "text", "text": "\n".join(result_lines)})

        return ToolActionResult(content=content)

    def _javascript_blocked(self) -> bool:
        return any(
            state.type.value == "dialog" for state in self.context.modal_states()
        )

    def validate_capabilities(self) -> None:
        if not self.capabilities:
            return

        supported_capabilities = set(ToolCapability)
        unsupported = set(self.capabilities) - supported_capabilities

        if unsupported:
            raise ValueError(f"Unsupported capabilities: {unsupported}")

    def get_capabilities_summary(self) -> Dict[str, int]:
        summary = {}
        for tool in self._tools:
            capability = tool.capability.value
            summary[capability] = summary.get(capability, 0) + 1
        return summary

    def __str__(self) -> str:
        return f"EnhancedToolRegistry(tools={len(self._tools)}, capabilities={self.capabilities})"


def get_tools(capabilities: Optional[List[ToolCapability]] = None) -> List[Tool]:

    all_tools = []

    if not capabilities or ToolCapability.CORE in capabilities:
        all_tools.extend(get_core_tools())

    if not capabilities or ToolCapability.VISION in capabilities:
        all_tools.extend(get_vision_tools())

    if not capabilities or ToolCapability.TABS in capabilities:
        all_tools.extend(get_tab_tools())

    if not capabilities or ToolCapability.CONSOLE in capabilities:
        all_tools.extend(get_console_tools())

    if not capabilities or ToolCapability.KEYBOARD in capabilities:
        all_tools.extend(get_keyboard_tools())

    if not capabilities or ToolCapability.NETWORK in capabilities:
        all_tools.extend(get_network_tools())

    if not capabilities or ToolCapability.FILES in capabilities:
        all_tools.extend(get_file_tools())

    if not capabilities or ToolCapability.WAIT in capabilities:
        all_tools.extend(get_wait_tools())

    if not capabilities or ToolCapability.PDF in capabilities:
        all_tools.extend(get_pdf_tools())

    if not capabilities or ToolCapability.TESTING in capabilities:
        all_tools.extend(get_testing_tools())

    if not capabilities or ToolCapability.API in capabilities:
        all_tools.extend(get_api_tools())

    if not capabilities or ToolCapability.GOOGLE_SHEETS in capabilities:
        all_tools.extend(GOOGLE_SHEETS_TOOLS)
        all_tools.extend(GOOGLE_SHEETS_ADVANCED_TOOLS)
        all_tools.extend(GOOGLE_SHEETS_EXPORT_TOOLS)

    if not capabilities or ToolCapability.DATABASE in capabilities:
        all_tools.extend(get_database_tools())

    all_tools.extend(get_page_content_tools())

    all_tools.extend(get_interaction_tools())
    all_tools.extend(get_snapshot_tools())
    all_tools.extend(get_dialog_tools())
    # Add new tools here

    return all_tools
