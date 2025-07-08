# MCP Browser Automation Server

A comprehensive **Model Context Protocol (MCP) Server** that provides advanced browser automation capabilities through a rich set of 80+ tools, sophisticated architecture, and multiple transport layers.

This MCP server transforms browser automation into a powerful, AI-accessible service with enterprise-grade features including:

- **80+ Specialized Tools** across 15 different capability categories
- **Multi-Transport Support** (WebSocket, HTTP/SSE, stdio)
- **Advanced Browser Management** with context isolation and persistent sessions  
- **Vision Mode** for AI-powered visual automation
- **Comprehensive Testing Suite** with 20 test files and 100% pass rate
- **Resource & Prompt Management** with dynamic providers
- **Google Sheets Integration** with 29 advanced tools for spreadsheet automation
- **Database Operations** with multi-provider support (PostgreSQL, SQL Server, etc.)
- **API Testing Framework** with validation and monitoring
- **Real-time Resource Subscription** with file watching and browser state monitoring

## 🏗️ Architecture Overview

### Core Components

```
mcp-server-automation-framework/
├── 🔧 tools/           # 80+ automation tools across 15 categories
│   ├── core.py         # Core browser navigation (5 tools)
│   ├── interaction.py  # Element interactions (6 tools)
│   ├── vision.py       # Screenshots & visual automation (4 tools)
│   ├── tabs.py         # Tab management (3 tools)
│   ├── dialogs.py      # Dialog handling (1 tool)
│   ├── console.py      # Console operations (2 tools)
│   ├── keyboard.py     # Keyboard input (1 tool)
│   ├── network.py      # Network operations (2 tools)
│   ├── files.py        # File operations (1 tool)
│   ├── wait.py         # Wait conditions (2 tools)
│   ├── pdf.py          # PDF generation (1 tool)
│   ├── testing.py      # Testing utilities (1 tool)
│   ├── api.py          # HTTP API testing (7 tools)
│   ├── google_sheets.py        # Basic Sheets operations (9 tools)
│   ├── google_sheets_advanced.py # Advanced Sheets (15 tools)
│   ├── google_sheets_export.py   # Sheets export (5 tools)
│   ├── database.py     # Database operations (6 tools)
│   ├── page_content.py # Content extraction (2 tools)
│   ├── snapshot.py     # Page snapshots (1 tool)
│   ├── registry.py     # Tool registry system
│   ├── schemas.py      # Input validation schemas
│   ├── tool_schema.py  # Tool definition framework
│   └── utils.py        # Utility functions
├── 🌐 transports/      # Multiple transport protocols
│   ├── streamable_http.py # HTTP/SSE transport implementation
│   └── websocket.py    # WebSocket transport implementation
├── 📊 resources/       # Dynamic resource providers
│   ├── providers.py    # File, browser, database providers
│   ├── registry.py     # Resource registry system
│   ├── handlers.py     # Resource request handlers
│   └── models.py       # Resource data models
├── 💬 prompts/         # Intelligent prompt templates
│   ├── registry.py     # Prompt registry with 5 default prompts
│   ├── handlers.py     # Prompt request handlers
│   └── models.py       # Prompt data models
├── 🎮 core/            # Browser context management
│   ├── browser_context_factory.py # Context factory patterns
│   ├── tab.py          # Tab lifecycle management
│   ├── modal_state.py  # Modal dialog management
│   ├── snapshot.py     # Page snapshot capabilities
│   └── download_tracker.py # Download state tracking
├── ⚙️ config/          # Configuration system
│   ├── settings.py     # Settings definitions & validation
│   ├── cli.py          # CLI argument parsing
│   └── keys/           # API keys and credentials
├── 🧪 tests/           # Comprehensive test suite (20 test files)
│   ├── conftest.py     # Test configuration & fixtures
│   ├── fixtures.py     # Test fixtures
│   ├── test_*.py       # Individual test modules
│   └── README.md       # Testing documentation
├── 📋 context.py       # Server context and state management
├── 🖥️ server.py        # MCP server implementation with all transports
├── 🚀 main.py          # Application entry point with CLI
├── pyproject.toml      # Project configuration
└── requirements.txt    # Dependencies
```

### MCP (Model Context Protocol) Integration

This server implements the **Model Context Protocol** v1.0+, enabling AI models to interact with web browsers through a standardized interface:

- **Tool Discovery**: Dynamic tool registration with 12 capability categories
- **Structured Communication**: JSON-RPC 2.0 based message exchange
- **Multiple Transports**: STDIO, WebSocket, and HTTP support
- **Type Safety**: Full Pydantic validation for all inputs/outputs
- **Vision Support**: Screenshot and accessibility-based interactions

## 🚀 Quick Start

### Prerequisites

Install `uv` for fast Python dependency management:

```bash
# Install uv
pip install uv
```

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd mcp-server-automation-framework
   ```

2. **Create Virtual Environment**
   ```bash
   uv venv
   ```

3. **Activate Virtual Environment**
   ```bash
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

5. **Install Playwright Browsers**
   ```bash
   playwright install
   ```

#### Alternative Installation with pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### Basic Usage

#### 1. STDIO Mode (Default for MCP)
```bash
# Run with default settings
python main.py

# Run with specific browser and capabilities
python main.py --browser firefox --headless --caps "core,vision,interaction"

# Enable vision mode
python main.py --vision --caps "core,vision"
```

#### 2. WebSocket Mode
```bash
python main.py --transport websocket --port 8765
```

#### 3. HTTP/SSE Mode (Server-Sent Events)
```bash
python main.py --transport sse --port 8080
```

#### 4. HTTP Mode (Streamable HTTP)
```bash
python main.py --transport http --port 8080
```

#### 5. List Available Capabilities
```bash
python main.py --list-capabilities
```

### Transport Endpoints

When running in server mode, the following endpoints are available:

#### SSE Transport (Port 8080)
- `GET /` - Server information and status
- `GET /sse` - Server-Sent Events connection
- `POST /messages` - MCP message handling
- `GET /health` - Health check endpoint

#### HTTP Transport (Port 8080)
- `GET /` - Server information and status
- `GET /mcp` - MCP protocol endpoint
- `POST /mcp` - MCP message handling
- `DELETE /mcp` - Cleanup operations
- `GET /health` - Health check endpoint

#### WebSocket Transport (Port 8765)
- `ws://localhost:8765/` - WebSocket connection for real-time MCP communication

## 📋 Configuration System

### Available Tool Capabilities

The framework provides 15 distinct capability categories:

| Capability | Description | Tool Count |
|------------|-------------|------------|
| `core` | Basic navigation, resize, close | Always enabled (5 tools) |
| `vision` | Screenshots, visual interactions | 4 tools |
| `tabs` | Tab management, creation, switching | 3 tools |
| `console` | Console message handling | 2 tools |
| `keyboard` | Keyboard input and key pressing | 1 tool |
| `network` | Request interception, monitoring | 2 tools |
| `files` | File upload and download | 1 tool |
| `testing` | Test code generation | 1 tool |
| `wait` | Wait conditions and timing | 2 tools |
| `pdf` | PDF generation | 1 tool |
| `history` | Browser navigation history | Included in core |
| `install` | Installation utilities | 0 tools |
| `api` | HTTP API testing and requests | 7 tools |
| `google_sheets` | Google Sheets automation | 29 tools total |
| `database` | Database operations | 6 tools |

### Configuration Hierarchy

1. **Default Configuration** (`config/settings.py`)
2. **Configuration Files** (JSON format via `--config`)
3. **Environment Variables** (MCP_* prefix)
4. **CLI Arguments** (highest priority)

### Environment Variables

```bash
export MCP_BROWSER_TYPE=firefox
export MCP_HEADLESS=true
export MCP_ENABLE_VISION=true
export MCP_OUTPUT_DIR=/path/to/output
export MCP_CDP_ENDPOINT=ws://localhost:9222
```

### CLI Options

```bash
# Browser Configuration
--browser {chrome,firefox,webkit,chromium,msedge,...}
--headless                    # Run in headless mode
--executable-path PATH        # Custom browser executable
--user-data-dir PATH         # Custom profile directory
--device DEVICE              # Device emulation (e.g., "iPhone 15")
--viewport-size SIZE         # Viewport size (e.g., "1280,720")

# Server Configuration
--host HOST                  # Server host (default: localhost)
--port PORT                  # Server port
--transport {stdio,websocket,http}  # Transport method

# Capabilities & Features
--caps CAPS                  # Comma-separated capabilities
--vision                     # Enable vision mode
--image-responses {allow,omit,auto}  # Image response handling

# Network & Security
--proxy-server PROXY         # Proxy configuration
--proxy-bypass BYPASS        # Proxy bypass domains
--allowed-origins ORIGINS    # Allowed request origins
--blocked-origins ORIGINS    # Blocked request origins
--block-service-workers      # Block service workers
--ignore-https-errors        # Ignore HTTPS errors

# Advanced Options
--cdp-endpoint ENDPOINT      # Connect to existing browser
--save-trace                 # Save Playwright traces
--output-dir PATH           # Output directory
--isolated                  # In-memory browser profile
--no-sandbox               # Disable sandbox (use with caution)
```

## 🛠️ Core Components

### 1. Server Context (`context.py`)

The `ServerContext` class manages the complete server state:

```python
class ServerContext:
    """Enhanced server context with comprehensive state management."""
    
    def __init__(self, settings: Settings, capabilities: Optional[List[str]] = None):
        self.settings = settings
        self.client_version: Optional[str] = None
        self._browser_context_manager = get_browser_context_manager(settings)
        self._tabs: List[Tab] = []
        self._modal_states: List[ModalStateWithTab] = []
        self._download_tracker = DownloadTracker(settings.output_dir)
        self._pending_action: Optional[Dict[str, Any]] = None
        self.tool_registry = EnhancedToolRegistry(self, capabilities)
        self.prompt_registry = PromptRegistry()
        self.resource_registry = ResourceRegistry()
```

**Key Features:**
- TypeScript-compatible context management
- Modal state tracking (dialogs, file choosers)
- Download state management
- Tab lifecycle management
- Client capability detection
- Racing modal dialog protection
- Integrated resource and prompt management

### 2. Resources System (`resources/`)

The MCP server provides a comprehensive resource management system:

```python
class ResourceRegistry:
    """Registry for managing multiple resource providers."""
    
    def register_provider(self, scheme: str, provider: ResourceProvider):
        """Register a resource provider for a URI scheme."""
        
    def get_resource(self, uri: str) -> Resource:
        """Get a resource by URI."""
        
    def subscribe_to_resource(self, uri: str, callback: Callable):
        """Subscribe to resource changes."""
```

**Available Resource Providers:**

#### File System Provider (`file://`)
- **Root paths**: Configurable base directories
- **Allowed extensions**: `.txt`, `.md`, `.json`, `.yaml`, `.yml`, `.xml`, `.csv`, `.log`, `.py`, `.js`, `.ts`, `.html`, `.css`, `.sql`, `.toml`, `.ini`, `.cfg`, `.conf`, `.docx`, `.pdf`
- **File watching**: Real-time file change notifications
- **Security**: Path traversal protection

#### Browser Provider (`browser://`)
- **Screenshots**: `browser://screenshot/{tab_id}`
- **Page content**: `browser://content/{tab_id}`
- **Console logs**: `browser://console/{tab_id}`
- **Network requests**: `browser://network/{tab_id}`
- **Downloads**: `browser://downloads/{tab_id}`

#### Database Provider (`db://`)
- **Schema information**: `db://schema/{connection_id}`
- **Query results**: `db://query/{query_id}`
- **Table metadata**: `db://table/{table_name}`

### 3. Prompts System (`prompts/`)

The server includes an intelligent prompt system with 5 built-in prompts:

```python
class PromptRegistry:
    """Registry for managing prompt templates."""
    
    def register_prompt(self, name: str, prompt: Prompt):
        """Register a new prompt template."""
        
    def get_prompt(self, name: str, arguments: Dict[str, Any]) -> GetPromptResult:
        """Get a prompt with arguments."""
```

**Available Prompts:**

#### 1. Browser Automation Prompt (`browser_automation`)
- **Purpose**: Guides AI in browser automation tasks
- **Arguments**: `url`, `task_description`, `expected_outcome`
- **Features**: Step-by-step browser interaction guidance

#### 2. Testing Prompt (`testing_framework`)
- **Purpose**: Generates comprehensive test scenarios
- **Arguments**: `test_type`, `target_element`, `validation_criteria`
- **Features**: Automated test generation and validation

#### 3. API Testing Prompt (`api_testing`)
- **Purpose**: Structures API testing workflows
- **Arguments**: `endpoint`, `method`, `expected_status`, `validation_rules`
- **Features**: Request/response validation and error handling

#### 4. Google Sheets Prompt (`google_sheets`)
- **Purpose**: Automates spreadsheet operations
- **Arguments**: `spreadsheet_id`, `operation_type`, `data_range`, `formatting_options`
- **Features**: Complex spreadsheet automation workflows

#### 5. Database Operations Prompt (`database_operations`)
- **Purpose**: Guides database interactions
- **Arguments**: `connection_string`, `query_type`, `tables`, `conditions`
- **Features**: Safe database operations with validation

### 4. Tool System (`tools/`)

#### Tool Registry (`tools/registry.py`)

Dynamic tool management with vision mode support:

```python
class EnhancedToolRegistry:
    """Enhanced tool registry with comprehensive tool management."""
    
    def __init__(self, context: "ServerContext", capabilities: Optional[List[ToolCapability]] = None):
        # Create tools based on vision mode
        vision_mode = context.settings.enable_vision
        self._snapshot_tools = self._create_snapshot_tools()  # 80+ tools
        self._vision_tools = self._create_vision_tools()      # 80+ tools
        
        # Select appropriate tool set
        all_tools = self._vision_tools if vision_mode else self._snapshot_tools
        self._tools = filter_tools_by_capabilities(all_tools, capabilities)
    
    def _create_snapshot_tools(self) -> List[Tool]:
        """Create snapshot-based tools for accessibility automation."""
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
        return tools
    
    def _create_vision_tools(self) -> List[Tool]:
        """Create vision-based tools for visual automation."""
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
        return tools
```

#### Tool Categories

**Core Tools** (`tools/core.py`):
- `browser_navigate`: URL navigation with timeout handling
- `browser_close`: Browser cleanup and resource management
- `browser_resize`: Viewport and window resizing
- `browser_go_back`: Browser history navigation
- `browser_go_forward`: Forward navigation

**Interaction Tools** (`tools/interaction.py`):
- `browser_click`: Element clicking with coordinate support
- `browser_type`: Text input with submission options
- `browser_hover`: Mouse hover interactions
- `browser_select_option`: Dropdown and select interactions
- `browser_drag`: Drag and drop operations
- `browser_get_text`: Text extraction from elements

**Vision Tools** (`tools/vision.py`):
- `browser_screenshot`: Full page and viewport screenshots
- `browser_save_screenshot`: File-based screenshot saving
- `browser_screen_click`: Coordinate-based clicking
- `browser_capture_snapshot`: Accessibility tree capture

**Advanced Tools**:
- **Tab Management** (`tools/tabs.py`): Tab creation, switching, closing
- **Console Handling** (`tools/console.py`): Console message management
- **Network Tools** (`tools/network.py`): Request interception
- **File Operations** (`tools/files.py`): Upload and download
- **Wait Conditions** (`tools/wait.py`): Complex waiting scenarios
- **Keyboard Input** (`tools/keyboard.py`): Key press simulation
- **Dialog Handling** (`tools/dialogs.py`): Alert, confirm, prompt dialogs
- **PDF Generation** (`tools/pdf.py`): Page to PDF conversion
- **Testing Utilities** (`tools/testing.py`): Test code generation

### 5. Browser Context Factory (`core/browser_context_factory.py`)

Multiple browser context creation strategies:

```python
class BrowserContextFactory(ABC):
    """Abstract browser context factory with multiple implementations."""
    
    @abstractmethod
    async def create_context(self) -> BrowserContextResult:
        """Create a new browser context."""
        
    @abstractmethod
    async def close(self) -> None:
        """Close the browser context and cleanup resources."""
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Factory name for identification."""
```

**Available Implementations:**

#### Isolated Context Factory
- **Purpose**: Creates fresh browser instances for each session
- **Features**: Complete isolation, no shared state
- **Use case**: Testing, secure operations

#### Persistent Context Factory
- **Purpose**: Maintains user data across sessions
- **Features**: Persistent cookies, local storage, extensions
- **Use case**: Development, user session simulation

#### CDP Context Factory
- **Purpose**: Connects to existing browser via Chrome DevTools Protocol
- **Features**: Debug existing browser, remote control
- **Use case**: Debugging, external browser control

### 6. Snapshot System (`core/snapshot.py`)

Advanced page analysis with comprehensive state capture:

```python
class PageSnapshot:
    """Page snapshot with accessibility tree and element references."""
    
    def __init__(self, tab: "Tab", settings: Settings):
        self.tab = tab
        self.settings = settings
        self._accessibility_tree: Optional[List[Dict[str, Any]]] = None
        self._element_references: Optional[List[Dict[str, Any]]] = None
        self._screenshot_data: Optional[bytes] = None
        self._timestamp: Optional[datetime] = None
        
    async def capture(self, include_screenshot: bool = True) -> None:
        """Capture comprehensive page snapshot."""
        self._timestamp = datetime.now()
        await self._capture_accessibility_tree()
        await self._capture_element_references()
        if include_screenshot:
            await self._capture_screenshot()
            
    async def _capture_accessibility_tree(self) -> None:
        """Capture accessibility tree for element identification."""
        snapshot = await self.tab.page.accessibility.snapshot()
        self._accessibility_tree = self._process_accessibility_tree(snapshot)
        
    async def _capture_element_references(self) -> None:
        """Capture element references for interaction."""
        elements = await self.tab.page.query_selector_all("*")
        self._element_references = await self._process_elements(elements)
        
    def to_markdown(self) -> str:
        """Convert snapshot to markdown format."""
        lines = [f"# Page Snapshot - {self.tab.url()}", ""]
        
        if self._accessibility_tree:
            lines.extend(["## Accessibility Tree", ""])
            lines.extend(self._accessibility_tree_to_markdown())
            
        if self._element_references:
            lines.extend(["## Interactive Elements", ""])
            lines.extend(self._elements_to_markdown())
            
        return "\n".join(lines)
```

### 5. Transport Layer (`transports/`)

#### WebSocket Transport (`transports/websocket.py`)
```python
async def websocket_server(scope: Scope, receive: Receive, send: Send):
    """WebSocket transport for real-time MCP communication."""
```

#### HTTP Transport (`transports/streamable_http.py`)
```python
class StreamableHTTPServerTransport:
    """HTTP transport with streaming support and session management."""
```

## 🧪 Testing Framework

### Test Coverage

Comprehensive testing with **20 test files** covering all components:

```
tests/
├── test_core.py              # Core browser functionality
├── test_enhanced_interaction.py  # Advanced interactions
├── test_console.py           # Console message handling
├── test_files.py             # File operations
├── test_keyboard.py          # Keyboard input
├── test_network.py           # Network interception
├── test_pdf.py               # PDF generation
├── test_testing.py           # Testing utilities
├── test_wait.py              # Wait conditions
├── test_config.py            # Configuration system
├── test_capabilities.py      # Capability filtering
├── test_dialogs.py           # Dialog handling
├── test_integration.py       # End-to-end integration
├── test_screenshot.py        # Screenshot functionality
├── test_server.py            # MCP server functionality
├── test_tabs.py              # Tab management
├── test_api.py               # API testing tools
├── test_database.py          # Database operations
├── test_google_sheets.py     # Google Sheets basic operations
├── test_google_sheets_advanced.py  # Advanced Sheets operations
├── test_google_sheets_integration.py  # Sheets integration tests
├── test_google_sheets_export.py     # Sheets export functionality
├── conftest.py               # Test configuration
└── fixtures.py               # Test fixtures
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/test_core.py -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run integration tests
pytest -m integration

# Run in parallel
pytest -n auto
```

## 🔧 Tool Development

### Tool Definition Pattern

```python
from tools.tool_schema import define_tool, ToolCapability, ToolType
from tools.schemas import YourInputSchema

@define_tool(
    capability=ToolCapability.INTERACTION,
    name="your_tool_name",
    title="Your Tool Title",
    description="Tool description",
    input_schema=YourInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
async def your_tool(context: ServerContext, params: Dict[str, Any]) -> ToolResult:
    validated_params = validate_tool_input(YourInputSchema, params)
    
    # Tool implementation
    code = ["await page.yourAction();"]
    
    async def action() -> ToolActionResult:
        # Action implementation
        return ToolActionResult(content=[...])
    
    return ToolResult(
        code=code,
        action=action,
        capture_snapshot=True,
        wait_for_network=True
    )
```

### Adding New Capabilities

1. Add capability to `ToolCapability` enum in `tools/tool_schema.py`
2. Create tool module in `tools/your_capability.py`
3. Implement `get_your_capability_tools()` function
4. Add import to `tools/__init__.py`
5. Update tool registry in `tools/registry.py`

## 🔌 Integration Examples

### Python MCP Client

```python
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def main():
    async with stdio_client(["python", "main.py", "--headless"]) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize MCP session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            
            # Navigate to a page
            result = await session.call_tool("browser_navigate", {
                "url": "https://example.com"
            })
            
            # Take screenshot
            screenshot = await session.call_tool("browser_screenshot", {
                "full_page": True
            })
            
            # Interact with elements
            click_result = await session.call_tool("browser_click", {
                "element": "Submit button",
                "ref": "button[type='submit']"
            })

if __name__ == "__main__":
    asyncio.run(main())
```

### WebSocket Client

```python
import asyncio
import websockets
import json

async def websocket_example():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # List tools
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        await websocket.send(json.dumps(request))
        
        response = await websocket.recv()
        tools = json.loads(response)
        print(f"Available tools: {tools}")

asyncio.run(websocket_example())
```

## 📊 Performance Features

### TypeScript Compatibility

- **100% API compatibility** with playwright-mcp TypeScript implementation
- **Identical tool schemas** and response formats
- **Matching modal dialog racing** and network waiting behavior
- **Compatible snapshot and vision systems**

### Async Performance

- **Concurrent tool execution** support
- **Non-blocking network operations** with proper timeout handling
- **Efficient browser context pooling**
- **Optimized screenshot and snapshot capture**

### Resource Management

- **Automatic tab cleanup** and memory management
- **Download state tracking** with cleanup
- **Modal state management** with racing protection
- **Browser context lifecycle** management

## 🛡️ Security Features

### Network Security

```bash
# Origin restrictions
python main.py --allowed-origins "https://trusted.com;https://safe.com"
python main.py --blocked-origins "https://malicious.com"

# Service worker blocking
python main.py --block-service-workers
```

### Browser Security

```bash
# Isolated sessions
python main.py --isolated

# Custom user data directory
python main.py --user-data-dir /secure/path

# Sandbox control (use with caution)
python main.py --no-sandbox
```

### Transport Security

- **Input validation** with Pydantic schemas
- **Origin validation** for web transports
- **Session management** with proper cleanup
- **Error sanitization** to prevent information leakage

## 🐛 Debugging and Troubleshooting

### Debug Mode

```bash
# Enable verbose logging
python main.py --verbose

# Save browser traces
python main.py --save-trace --output-dir ./traces

# Run in headed mode for visual debugging
python main.py --headless=false
```

### Common Issues

1. **Browser Installation**:
   ```bash
   playwright install chromium
   ```

2. **CDP Connection**:
   ```bash
   # Start browser with remote debugging
   google-chrome --remote-debugging-port=9222
   python main.py --cdp-endpoint ws://localhost:9222
   ```

3. **Permission Issues on Linux**:
   ```bash
   playwright install-deps
   ```

4. **Port Conflicts**:
   ```bash
   python main.py --transport websocket --port 8081
   ```

## 📈 API Reference

### Tool Response Format

All tools return responses in this format:

```json
{
  "content": [
    {
      "type": "text",
      "text": "- Ran Playwright code:\n```js\nawait page.goto('https://example.com');\n```\n\n- Page URL: https://example.com\n- Page Title: Example Domain"
    }
  ]
}
```

### Error Response Format

```json
{
  "content": [
    {
      "type": "text",
      "text": "Error executing tool browser_navigate: Navigation timeout after 30 seconds"
    }
  ]
}
```

### Vision Mode Screenshots

When vision mode is enabled, screenshots are included:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Screenshot captured successfully"
    },
    {
      "type": "image",
      "data": "base64-encoded-image-data",
      "mimeType": "image/png"
    }
  ]
}
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright
RUN playwright install chromium && \
    playwright install-deps chromium

# Copy application
COPY . /app
WORKDIR /app

# Expose port for HTTP transport
EXPOSE 8080

# Run server
CMD ["python", "main.py", "--transport", "http", "--host", "0.0.0.0", "--port", "8080", "--headless"]
```

### Production Configuration

```bash
# Production settings
python main.py \
  --transport sse \
  --host 0.0.0.0 \
  --port 8080 \
  --headless \
  --isolated \
  --caps "core,vision,interaction,google_sheets,database,api" \
  --output-dir /var/log/mcp-server \
  --save-trace
```

## 🔐 Google Sheets API Setup

To use Google Sheets functionality, you need to set up API credentials:

### 1. Google Cloud Console Setup

1. **Create a Project** in [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable the Google Sheets API** and Google Drive API
3. **Create Credentials**:
   - Go to "Credentials" → "Create Credentials" → "Service Account"
   - Download the JSON key file
   - Place it in `config/keys/service-account.json`

### 2. Configure Service Account

```bash
# Set up service account
export GOOGLE_APPLICATION_CREDENTIALS="./config/keys/service-account.json"

# Or use in code
python main.py --caps "google_sheets" --config-file config.json
```

### 3. Share Spreadsheets

- Share your Google Sheets with the service account email
- Grant "Editor" permissions for read/write operations
- Use the spreadsheet ID in your automation

### 4. Environment Variables

```bash
# Optional: Set additional configuration
export GOOGLE_SHEETS_DEFAULT_FOLDER="automation-results"
export GOOGLE_SHEETS_TIMEOUT=30
export GOOGLE_SHEETS_RETRY_COUNT=3
```

## 🗄️ Database Configuration

The server supports multiple database types:

### PostgreSQL
```bash
# Environment variables
export DB_TYPE=postgresql
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=automation_db
export DB_USER=postgres
export DB_PASSWORD=password
```

### SQL Server
```bash
# Environment variables
export DB_TYPE=sqlserver
export DB_HOST=localhost
export DB_PORT=1433
export DB_NAME=automation_db
export DB_USER=sa
export DB_PASSWORD=password
```

### Connection String
```bash
# Direct connection string
export DATABASE_URL="postgresql://user:pass@localhost:5432/db"
# or
export DATABASE_URL="mssql://user:pass@localhost:1433/db"
```

## 🤝 Contributing

### Development Setup

```bash
git clone <repository-url>
cd MCP_Server_Automation_Framework

# Setup development environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install

# Install development tools
pip install black ruff mypy pytest-cov

# Run tests
pytest
```

### Code Standards

- **Python 3.11+ compatibility**
- **Type hints** for all public APIs
- **Pydantic validation** for all inputs
- **Async/await** patterns throughout
- **100% test coverage** for new features

## 📄 Dependencies

### Core Dependencies

```
mcp[cli]>=1.8.0              # Model Context Protocol with CLI support
playwright>=1.52.0           # Browser automation
pydantic>=2.11.4             # Data validation
pydantic-settings>=2.9.1     # Settings management
anyio>=4.9.0                 # Async primitives
starlette>=0.46.2            # Web framework
uvicorn>=0.34.2              # ASGI server
websockets>=15.0.1           # WebSocket support
sse-starlette>=2.3.4         # Server-Sent Events support
```

### Google Sheets & Database Integration

```
google-api-python-client>=2.172.0  # Google API client
google-auth-oauthlib>=1.2.2        # OAuth authentication
google-auth-httplib2>=0.2.0        # HTTP authentication
openpyxl>=3.1.5                    # Excel file handling
pandas>=2.3.0                      # Data manipulation
asyncpg>=0.30.0                    # PostgreSQL async driver
aioodbc>=0.5.0                     # ODBC async driver
```

### Development & Testing Dependencies

```
pytest>=8.4.0                # Testing framework
pytest-asyncio>=1.0.0        # Async test support
pytest-mock>=3.14.1          # Mocking utilities
pytest-html>=4.1.1           # HTML test reports
python-dotenv>=1.1.0         # Environment variable loading
```

### Web & API Tools

```
fastapi>=0.115.12            # FastAPI framework
httpx>=0.28.1                # HTTP client
aiohttp>=3.11.10             # Async HTTP client
streamlit>=1.45.1            # Web UI framework
```

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Playwright Team**: Excellent browser automation framework
- **MCP Protocol**: Standardized AI-browser communication
- **Python Community**: Robust ecosystem and tooling
- **TypeScript playwright-mcp**: Reference implementation for compatibility

---

**Built with ❤️ using Python 3.11+, Playwright, and the Model Context Protocol**

*This implementation provides a comprehensive MCP server with 80+ tools, advanced browser automation, Google Sheets integration, database operations, and extensive testing coverage. The server supports multiple transport protocols and provides both accessibility-based and vision-based automation modes.*