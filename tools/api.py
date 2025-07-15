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
from core.schemas import ApiRequestInputSchema, ApiTestInputSchema

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


@define_tool_factory(
    capability=ToolCapability.API,
    name="api_get",
    title="GET Request",
    description="Make HTTP GET request to specified URL",
    input_schema=ApiRequestInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def api_get_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        params = params.copy()
        params["method"] = "GET"
        return await api_request_factory(capture_snapshot).handle(context, params)

    schema = ToolSchema(
        name="api_get",
        title="GET Request",
        description="Make HTTP GET request to specified URL",
        input_schema=ApiRequestInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(
        capability=ToolCapability.API,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.API,
    name="api_post",
    title="POST Request",
    description="Make HTTP POST request with data",
    input_schema=ApiRequestInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def api_post_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        params = params.copy()
        params["method"] = "POST"
        return await api_request_factory(capture_snapshot).handle(context, params)

    schema = ToolSchema(
        name="api_post",
        title="POST Request",
        description="Make HTTP POST request with data",
        input_schema=ApiRequestInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.API,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.API,
    name="api_put",
    title="PUT Request",
    description="Make HTTP PUT request with data",
    input_schema=ApiRequestInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def api_put_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        params = params.copy()
        params["method"] = "PUT"
        return await api_request_factory(capture_snapshot).handle(context, params)

    schema = ToolSchema(
        name="api_put",
        title="PUT Request",
        description="Make HTTP PUT request with data",
        input_schema=ApiRequestInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.API,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.API,
    name="api_delete",
    title="DELETE Request",
    description="Make HTTP DELETE request",
    input_schema=ApiRequestInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def api_delete_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        params = params.copy()
        params["method"] = "DELETE"
        return await api_request_factory(capture_snapshot).handle(context, params)

    schema = ToolSchema(
        name="api_delete",
        title="DELETE Request",
        description="Make HTTP DELETE request",
        input_schema=ApiRequestInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.API,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.API,
    name="api_patch",
    title="PATCH Request",
    description="Make HTTP PATCH request with data",
    input_schema=ApiRequestInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def api_patch_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        params = params.copy()
        params["method"] = "PATCH"
        return await api_request_factory(capture_snapshot).handle(context, params)

    schema = ToolSchema(
        name="api_patch",
        title="PATCH Request",
        description="Make HTTP PATCH request with data",
        input_schema=ApiRequestInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.API,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.API,
    name="api_test",
    title="Test API Endpoint",
    description="Test API endpoint with assertions and validations",
    input_schema=ApiTestInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def api_test_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = ApiTestInputSchema(**params)

        code = [
            f"# Testing {validated_params.method} request to {validated_params.url}",
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

        code.extend(
            [
                "# Processing response",
                "# Validating response",
            ]
        )

        if validated_params.expected_status:
            code.append(
                f"# Assert status code equals {validated_params.expected_status}"
            )

        if validated_params.expected_contains:
            code.append(
                f"# Assert response contains '{validated_params.expected_contains}'"
            )

        async def action() -> ToolActionResult:
            start_time = time.time()
            test_results = []

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
                            f"### API Test Results",
                            f"**URL:** {validated_params.url}",
                            f"**Method:** {validated_params.method}",
                            f"**Status:** {response.status} {response.reason}",
                            f"**Duration:** {duration:.3f}s",
                            "",
                            "### Test Assertions:",
                        ]

                        all_passed = True

                        if validated_params.expected_status:
                            status_passed = (
                                response.status == validated_params.expected_status
                            )
                            result_lines.append(
                                f"- **Status Code:** {validated_params.expected_status} {'✅ PASS' if status_passed else '❌ FAIL'} (got {response.status})"
                            )
                            if not status_passed:
                                all_passed = False

                        if validated_params.expected_contains:
                            contains_passed = (
                                validated_params.expected_contains in response_text
                            )
                            result_lines.append(
                                f"- **Contains Text:** '{validated_params.expected_contains}' {'✅ PASS' if contains_passed else '❌ FAIL'}"
                            )
                            if not contains_passed:
                                all_passed = False

                        result_lines.append("")
                        result_lines.append(
                            f"### Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}"
                        )

                        if response.headers:
                            result_lines.append("")
                            result_lines.append("**Response Headers:**")
                            for key, value in response.headers.items():
                                result_lines.append(f"  - {key}: {value}")

                        result_lines.append("")
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
                            "text": f"❌ Test failed: Request timeout after {validated_params.timeout}s",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[{"type": "text", "text": f"❌ Test failed: {str(e)}"}]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="api_test",
        title="Test API Endpoint",
        description="Test API endpoint with assertions and validations",
        input_schema=ApiTestInputSchema,
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
        api_get_factory(capture_snapshot),
        api_post_factory(capture_snapshot),
        api_put_factory(capture_snapshot),
        api_delete_factory(capture_snapshot),
        api_patch_factory(capture_snapshot),
        api_test_factory(capture_snapshot),
    ]


API_TOOLS = get_api_tools()
