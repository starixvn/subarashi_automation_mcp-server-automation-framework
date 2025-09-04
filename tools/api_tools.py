from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import ApiService
import json
from typing import Union, Dict, Any, List


def parse_headers_improved(headers_str: str) -> dict:
    if not headers_str or not headers_str.strip():
        return {}

    headers_str = headers_str.strip()

    if headers_str.startswith("{") and headers_str.endswith("}"):
        try:
            return json.loads(headers_str)
        except json.JSONDecodeError:
            pass

    headers_dict = {}

    if "\\n" in headers_str or "\n" in headers_str:
        normalized = (
            headers_str.replace("\\n", "\n")
            .replace("\\r\\n", "\n")
            .replace("\\r", "\n")
        )
        lines = normalized.split("\n")
    else:
        lines = []
        current_header = ""
        in_quotes = False
        colon_found = False

        i = 0
        while i < len(headers_str):
            char = headers_str[i]

            if char == '"' and (i == 0 or headers_str[i - 1] != "\\"):
                in_quotes = not in_quotes
                current_header += char
            elif char == ":" and not in_quotes:
                colon_found = True
                current_header += char
            elif char == "," and not in_quotes and colon_found:
                rest = headers_str[i + 1 :].strip()
                if ":" in rest:
                    next_colon = rest.find(":")
                    potential_header = rest[:next_colon].strip()
                    if (
                        len(potential_header) < 50
                        and not potential_header.startswith('"')
                        and potential_header.replace("-", "").replace("_", "").isalnum()
                    ):
                        lines.append(current_header.strip())
                        current_header = ""
                        colon_found = False
                    else:
                        current_header += char
                else:
                    current_header += char
            else:
                current_header += char

            i += 1

        if current_header.strip():
            lines.append(current_header.strip())

    for line in lines:
        line = line.strip()
        if not line or ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]

        headers_dict[key] = value

    return headers_dict


def normalize_body_input(body: Union[str, Dict[str, Any], List[Any], None]) -> str:
    if body is None:
        return ""

    if isinstance(body, (dict, list)):
        try:
            return json.dumps(body)
        except (TypeError, ValueError):
            return str(body)

    if isinstance(body, str):
        return body

    return str(body)


def validate_and_format_json_body(body_str: str) -> tuple[str, bool]:
    if not body_str or not body_str.strip():
        return "", False

    try:
        parsed = json.loads(body_str)
        formatted = json.dumps(parsed, separators=(",", ":"))
        return formatted, True
    except json.JSONDecodeError:
        return body_str, False


def register_api_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def api_request(
        method: str,
        url: str,
        context: Context,
        headers: str = "",
        body: Union[str, Dict[str, Any], List[Any], None] = "",
    ) -> str:
        service = ApiService(server_context)

        try:
            normalized_body = normalize_body_input(body)

            if normalized_body and normalized_body.strip():
                formatted_body, is_valid_json = validate_and_format_json_body(
                    normalized_body
                )
                if not is_valid_json:
                    formatted_body = normalized_body
            else:
                formatted_body = ""

        except Exception:
            formatted_body = body if body else ""

        headers_dict = None
        if headers:
            try:
                headers_dict = parse_headers_improved(headers)
            except Exception:
                headers_dict = (
                    {"Content-Type": "application/json"} if formatted_body else None
                )
        else:
            if formatted_body:
                _, is_json = validate_and_format_json_body(formatted_body)
                if is_json:
                    headers_dict = {"Content-Type": "application/json"}

        result = await service.make_request(
            method, url, headers_dict, formatted_body if formatted_body else None
        )

        if result.success:
            response_data = result.data
            return f"API Request successful:\nStatus: {response_data['status']}\nResponse: {response_data.get('response_text', '')}"
        else:
            return f"API request failed: {result.error}"
