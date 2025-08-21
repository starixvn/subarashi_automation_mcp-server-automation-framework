import logging
from typing import List
from mcp.server.fastmcp.prompts import Prompt
from mcp.server.fastmcp.prompts.base import UserMessage
from .models import create_user_message

logger = logging.getLogger(__name__)


def get_default_prompts() -> List[Prompt]:
    def analyze_webpage(url: str, focus: str = "general analysis") -> List[UserMessage]:
        return [
            create_user_message(
                f"Please analyze the webpage at {url}. "
                f"Focus on: {focus}. "
                f"Provide insights about the page structure, content, "
                f"usability, performance, and any issues you notice."
            )
        ]

    def generate_test_script(
        feature: str, url: str, test_type: str = "functional"
    ) -> List[UserMessage]:
        return [
            create_user_message(
                f"Generate an automated test script for the following feature: {feature}\n"
                f"Location: {url}\n"
                f"Test type: {test_type}\n\n"
                f"Please provide:\n"
                f"1. Test steps and scenarios\n"
                f"2. Expected behaviors\n"
                f"3. Assertions to validate\n"
                f"4. Potential edge cases\n"
                f"5. Recommended test framework/tools"
            )
        ]

    def api_test_plan(
        endpoint: str, method: str, description: str = ""
    ) -> List[UserMessage]:
        return [
            create_user_message(
                f"Create a comprehensive test plan for this API endpoint:\n"
                f"Endpoint: {endpoint}\n"
                f"Method: {method}\n"
                f"Description: {description}\n\n"
                f"Please include:\n"
                f"1. Test scenarios (happy path, edge cases, error cases)\n"
                f"2. Request/response validation\n"
                f"3. Authentication testing\n"
                f"4. Performance considerations\n"
                f"5. Security testing aspects\n"
                f"6. Data validation tests"
            )
        ]

    def sql_query_optimization(
        query: str, database_type: str = "postgresql"
    ) -> List[UserMessage]:
        return [
            create_user_message(
                f"Analyze and optimize this SQL query for {database_type}:\n\n"
                f"```sql\n{query}\n```\n\n"
                f"Please provide:\n"
                f"1. Performance analysis\n"
                f"2. Optimization suggestions\n"
                f"3. Index recommendations\n"
                f"4. Rewritten optimized query\n"
                f"5. Potential issues and improvements\n"
                f"6. Explain query execution plan considerations"
            )
        ]

    def debug_automation_issue(
        issue_description: str, error_message: str = ""
    ) -> List[UserMessage]:
        error_section = f"\nError message: {error_message}\n" if error_message else ""

        return [
            create_user_message(
                f"Help debug this automation issue:\n"
                f"Issue: {issue_description}{error_section}\n"
                f"Please provide:\n"
                f"1. Possible root causes\n"
                f"2. Debugging steps\n"
                f"3. Common solutions\n"
                f"4. Prevention strategies\n"
                f"5. Alternative approaches\n"
                f"6. Best practices to avoid similar issues"
            )
        ]

    prompts = [
        Prompt.from_function(analyze_webpage, name="analyze-webpage"),
        Prompt.from_function(generate_test_script, name="generate-test-script"),
        Prompt.from_function(api_test_plan, name="api-test-plan"),
        Prompt.from_function(sql_query_optimization, name="sql-query-optimization"),
        Prompt.from_function(debug_automation_issue, name="debug-automation-issue"),
    ]

    return prompts


def get_prompt_by_name(name: str) -> Prompt | None:
    prompts = get_default_prompts()
    for prompt in prompts:
        if prompt.name == name:
            return prompt
    return None
