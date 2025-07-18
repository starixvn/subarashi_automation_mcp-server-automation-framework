import asyncio
import json
import time
from typing import Dict, Any, Optional, TYPE_CHECKING
import aiohttp
from core.tool_schema import (
    define_tool_factory,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
)
from core.schemas import ApiRequestInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext


@define_tool_factory(
    capability=ToolCapability.API,
    name="api_request",
    title="Make API Request",
    description="Make HTTP API request with specified method, headers and body",
    input_schema=ApiRequestInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def api_request_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = ApiRequestInputSchema(**params)

        code = [
            f"# Making {validated_params.method} request to {validated_params.url}",
            f"# Method: {validated_params.method}",
            f"# URL: {validated_params.url}",
        ]

        if validated_params.headers:
            code.append(f"# Headers: {json.dumps(validated_params.headers)}")

        if validated_params.body and validated_params.method in [
            "POST",
            "PUT",
            "PATCH",
        ]:
            code.append(f"# Body: {json.dumps(validated_params.body)}")

        code.extend(["# Processing response", "# Extracting response data"])

        async def action() -> ToolActionResult:
            start_time = time.time()

            try:
                timeout = aiohttp.ClientTimeout(total=validated_params.timeout)

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    kwargs = {
                        "method": validated_params.method,
                        "url": validated_params.url,
                        "headers": validated_params.headers or {},
                    }

                    if validated_params.body and validated_params.method in [
                        "POST",
                        "PUT",
                        "PATCH",
                    ]:
                        if validated_params.headers and "content-type" in {
                            k.lower() for k in validated_params.headers.keys()
                        }:
                            content_type = next(
                                (
                                    v
                                    for k, v in validated_params.headers.items()
                                    if k.lower() == "content-type"
                                ),
                                "",
                            )
                            if "application/json" in content_type.lower():
                                try:
                                    kwargs["json"] = json.loads(validated_params.body)
                                except json.JSONDecodeError:
                                    kwargs["data"] = validated_params.body
                            else:
                                kwargs["data"] = validated_params.body
                        else:
                            kwargs["data"] = validated_params.body

                    async with session.request(**kwargs) as response:
                        response_text = await response.text()
                        duration = time.time() - start_time

                        result_lines = [
                            f"### API Request Results",
                            f"**URL:** {validated_params.url}",
                            f"**Method:** {validated_params.method}",
                            f"**Status:** {response.status} {response.reason}",
                            f"**Duration:** {duration:.3f}s",
                        ]

                        if response.headers:
                            result_lines.append("**Response Headers:**")
                            for key, value in response.headers.items():
                                result_lines.append(f"  - {key}: {value}")

                        result_lines.append("**Response Body:**")
                        if response_text:
                            try:
                                parsed_json = json.loads(response_text)
                                result_lines.append(
                                    f"```json\n{json.dumps(parsed_json, indent=2)}\n```"
                                )
                            except json.JSONDecodeError:
                                result_lines.append(f"```\n{response_text}\n```")
                        else:
                            result_lines.append("(empty)")

                        return ToolActionResult(
                            content=[{"type": "text", "text": "\n".join(result_lines)}]
                        )

            except asyncio.TimeoutError:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Request timeout after {validated_params.timeout}s",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[{"type": "text", "text": f"Request failed: {str(e)}"}]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="api_request",
        title="Make API Request",
        description="Make HTTP API request with specified method, headers and body",
        input_schema=ApiRequestInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(
        capability=ToolCapability.API,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


def get_api_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        api_request_factory(capture_snapshot),
    ]


API_TOOLS = get_api_tools()
