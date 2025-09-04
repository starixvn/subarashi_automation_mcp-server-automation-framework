import asyncio
import json
import time
from typing import Dict, Optional
import aiohttp
from .base_service import BaseService, ServiceResult


class ApiService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        timeout: int = 30,
    ) -> ServiceResult:
        try:
            start_time = time.time()

            client_timeout = aiohttp.ClientTimeout(total=timeout)

            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                kwargs = {
                    "method": method.upper(),
                    "url": url,
                    "headers": headers or {},
                }

                if body and method.upper() in ["POST", "PUT", "PATCH"]:
                    if headers and "content-type" in {
                        k.lower() for k in headers.keys()
                    }:
                        content_type = next(
                            (
                                v
                                for k, v in headers.items()
                                if k.lower() == "content-type"
                            ),
                            "",
                        )
                        if "application/json" in content_type.lower():
                            if body.strip():
                                try:
                                    kwargs["json"] = json.loads(body)
                                except json.JSONDecodeError:
                                    kwargs["data"] = body
                            else:
                                kwargs["json"] = {}
                        else:
                            kwargs["data"] = body
                    else:
                        if body.strip().startswith(("{", "[")):
                            try:
                                kwargs["json"] = json.loads(body)
                                if not headers:
                                    kwargs["headers"] = {
                                        "Content-Type": "application/json"
                                    }
                                else:
                                    kwargs["headers"]["Content-Type"] = (
                                        "application/json"
                                    )
                            except json.JSONDecodeError:
                                kwargs["data"] = body
                        else:
                            kwargs["data"] = body

                async with session.request(**kwargs) as response:
                    response_text = await response.text()
                    duration = time.time() - start_time

                    result_text = "### API Request Results\n"
                    result_text += f"**URL:** {url}\n"
                    result_text += f"**Method:** {method.upper()}\n"
                    result_text += f"**Status:** {response.status} {response.reason}\n"
                    result_text += f"**Duration:** {duration:.3f}s\n"

                    if response.headers:
                        result_text += "**Response Headers:**\n"
                        for key, value in response.headers.items():
                            result_text += f"  - {key}: {value}\n"

                    result_text += "**Response Body:**\n"
                    if response_text:
                        try:
                            parsed_json = json.loads(response_text)
                            result_text += (
                                f"```json\n{json.dumps(parsed_json, indent=2)}\n```"
                            )
                        except json.JSONDecodeError:
                            result_text += f"```\n{response_text}\n```"
                    else:
                        result_text += "(empty)"

                    return ServiceResult(
                        success=True,
                        message="API request completed",
                        data={
                            "status": response.status,
                            "reason": response.reason,
                            "response_text": response_text,
                            "headers": dict(response.headers),
                            "duration": duration,
                            "formatted_result": result_text,
                        },
                    )

        except asyncio.TimeoutError:
            return ServiceResult(
                success=False,
                message=f"Request timeout after {timeout}s",
                error="timeout",
            )
        except Exception as e:
            return ServiceResult(
                success=False, message=f"API request failed: {str(e)}", error=str(e)
            )
