
import logging
from typing import Dict, List, Optional, Any
from .models import (
    Prompt, 
    PromptArgument, 
    PromptMessage, 
    PromptGenerator,
    create_user_message,
    create_assistant_message
)

logger = logging.getLogger(__name__)


class PromptRegistry:
    
    def __init__(self):
        self._prompts: Dict[str, Prompt] = {}
        self._setup_default_prompts()
    
    def register_prompt(self, prompt: Prompt) -> None:
        
        if prompt.name in self._prompts:
            logger.warning(f"Prompt '{prompt.name}' already exists, replacing")
        
        self._prompts[prompt.name] = prompt
        logger.debug(f"Registered prompt: {prompt.name}")
    
    def get_prompt(self, name: str) -> Optional[Prompt]:
        
        return self._prompts.get(name)
    
    def list_prompts(self) -> List[Prompt]:
        
        return list(self._prompts.values())
    
    def unregister_prompt(self, name: str) -> bool:
        
        if name in self._prompts:
            del self._prompts[name]
            logger.debug(f"Unregistered prompt: {name}")
            return True
        return False
    
    def clear(self) -> None:
        
        self._prompts.clear()
        logger.debug("Cleared all prompts")
    
    def _setup_default_prompts(self) -> None:
        
        async def analyze_webpage_generator(args: Dict[str, Any]) -> List[PromptMessage]:
            url = args.get("url", "")
            focus = args.get("focus", "general analysis")
            
            return [
                create_user_message(
                    f"Please analyze the webpage at {url}. "
                    f"Focus on: {focus}. "
                    f"Provide insights about the page structure, content, "
                    f"usability, performance, and any issues you notice."
                )
            ]
        
        analyze_webpage = Prompt(
            name="analyze-webpage",
            description="Analyze a webpage for insights, issues, or opportunities",
            arguments=[
                PromptArgument(
                    name="url",
                    description="URL of the webpage to analyze", 
                    required=True
                ),
                PromptArgument(
                    name="focus",
                    description="Specific aspect to focus on (accessibility, performance, seo, content, etc.)",
                    required=False
                )
            ],
            generator=analyze_webpage_generator
        )
        
        async def generate_test_script_generator(args: Dict[str, Any]) -> List[PromptMessage]:
            feature = args.get("feature", "")
            url = args.get("url", "")
            test_type = args.get("test_type", "functional")
            
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
        
        generate_test_script = Prompt(
            name="generate-test-script", 
            description="Generate automated test script for a web application feature",
            arguments=[
                PromptArgument(
                    name="feature",
                    description="Description of the feature to test",
                    required=True
                ),
                PromptArgument(
                    name="url", 
                    description="URL where the feature is located",
                    required=True
                ),
                PromptArgument(
                    name="test_type",
                    description="Type of test (functional, integration, e2e, performance)",
                    required=False
                )
            ],
            generator=generate_test_script_generator
        )
        
        async def api_test_plan_generator(args: Dict[str, Any]) -> List[PromptMessage]:
            api_endpoint = args.get("api_endpoint", "")
            method = args.get("method", "GET")
            description = args.get("description", "")
            
            return [
                create_user_message(
                    f"Create a comprehensive API testing plan for:\n"
                    f"Endpoint: {api_endpoint}\n"
                    f"Method: {method}\n"
                    f"Description: {description}\n\n"
                    f"Include:\n"
                    f"1. Functional test cases (positive/negative)\n"
                    f"2. Authentication and authorization tests\n"
                    f"3. Input validation tests\n"
                    f"4. Error handling scenarios\n"
                    f"5. Performance considerations\n"
                    f"6. Security test cases\n"
                    f"7. Example request/response formats"
                )
            ]
        
        api_test_plan = Prompt(
            name="api-test-plan",
            description="Create comprehensive API testing plan and test cases",
            arguments=[
                PromptArgument(
                    name="api_endpoint",
                    description="API endpoint URL to test",
                    required=True
                ),
                PromptArgument(
                    name="method",
                    description="HTTP method (GET, POST, PUT, DELETE, etc.)",
                    required=True
                ),
                PromptArgument(
                    name="description",
                    description="Description of what the API does",
                    required=False
                )
            ],
            generator=api_test_plan_generator
        )
        
        async def sql_query_optimization_generator(args: Dict[str, Any]) -> List[PromptMessage]:
            query = args.get("query", "")
            database_type = args.get("database_type", "postgresql")
            
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
        
        sql_optimization = Prompt(
            name="sql-query-optimization",
            description="Analyze and optimize SQL queries for better performance",
            arguments=[
                PromptArgument(
                    name="query",
                    description="SQL query to analyze and optimize",
                    required=True
                ),
                PromptArgument(
                    name="database_type",
                    description="Database type (postgresql, mysql, sqlserver, etc.)",
                    required=False
                )
            ],
            generator=sql_query_optimization_generator
        )
        
        async def debug_automation_issue_generator(args: Dict[str, Any]) -> List[PromptMessage]:
            issue_description = args.get("issue_description", "")
            error_message = args.get("error_message", "")
            
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
        
        debug_automation = Prompt(
            name="debug-automation-issue",
            description="Help debug and troubleshoot automation script issues",
            arguments=[
                PromptArgument(
                    name="issue_description",
                    description="Description of the automation issue",
                    required=True
                ),
                PromptArgument(
                    name="error_message",
                    description="Error message or logs (if available)",
                    required=False
                )
            ],
            generator=debug_automation_issue_generator
        )
        
        for prompt in [analyze_webpage, generate_test_script, api_test_plan, sql_optimization, debug_automation]:
            self.register_prompt(prompt)
        
        logger.info(f"Initialized prompt registry with {len(self._prompts)} default prompts")


# Global prompt registry instance
prompt_registry = PromptRegistry() 