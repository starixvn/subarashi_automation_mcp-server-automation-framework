from .base_service import BaseService, ServiceResult


class NetworkService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def get_network_requests(self) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()
            requests = tab.get_network_requests()

            if not requests:
                return ServiceResult(
                    success=True,
                    message="No network requests found",
                    data={"requests": [], "count": 0},
                )

            formatted_requests = []
            for req in requests:
                formatted_requests.append(
                    {
                        "method": req.get("method", "GET"),
                        "url": req.get("url", ""),
                        "status": req.get("status"),
                        "response_headers": req.get("response_headers", {}),
                        "request_headers": req.get("request_headers", {}),
                    }
                )

            return ServiceResult(
                success=True,
                message=f"Retrieved {len(requests)} network requests",
                data={"requests": formatted_requests, "count": len(requests)},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to get network requests: {str(e)}",
                error=str(e),
            )

