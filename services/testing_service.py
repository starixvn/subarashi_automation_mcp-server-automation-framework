from typing import Dict, Any
from .base_service import BaseService, ServiceResult


class TestingService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def generate_test(self) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            url = tab.url()
            title = await tab.title()

            test_code = [
                "import { test, expect } from '@playwright/test';",
                "",
                f"test('Test for {title}', async ({{ page }}) => {{",
                f"  await page.goto('{url}');",
                f"  await expect(page).toHaveTitle('{title}');",
                "});",
            ]

            return ServiceResult(
                success=True,
                message="Test code generated successfully",
                data={"url": url, "title": title, "test_code": "\n".join(test_code)},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to generate test: {str(e)}",
                error=str(e),
            )
