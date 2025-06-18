# MCP Server Automation Framework

A powerful **Model Context Protocol (MCP) Server** implementation for browser automation and testing using Python and Playwright. This framework provides full compatibility and supports advanced features including vision-based interactions, accessibility snapshots, multi-transport support, and comprehensive browser automation capabilities.

## 🏗️ Architecture Overview

### Project Structure

```
MCP_Server_Automation_Framework/
├── config/                 # Configuration management system
│   ├── __init__.py        # Configuration exports
│   ├── cli.py             # CLI argument parsing
│   └── settings.py        # Settings definitions
├── core/                  # Core browser automation components
│   ├── __init__.py        # Core exports
│   ├── browser.py         # Browser management
│   ├── browser_context_factory.py  # Context factory patterns
│   ├── download_tracker.py # Download state tracking
│   ├── modal_state.py     # Modal dialog management
│   ├── snapshot.py        # Page snapshot capabilities
│   └── tab.py             # Tab lifecycle management
├── tools/                 # Tool registry and implementations
│   ├── __init__.py        # Tool exports
│   ├── console.py         # Console message tools
│   ├── core.py            # Core navigation tools
│   ├── dialogs.py         # Dialog interaction tools
│   ├── files.py           # File upload/download tools
│   ├── interaction.py     # Element interaction tools
│   ├── keyboard.py        # Keyboard input tools
│   ├── network.py         # Network interception tools
│   ├── pdf.py             # PDF generation tools
│   ├── registry.py        # Tool registry system
│   ├── schemas.py         # Input schema definitions
│   ├── tabs.py            # Tab management tools
│   ├── testing.py         # Testing utilities
│   ├── tool_schema.py     # Tool schema framework
│   ├── utils.py           # Utility functions
│   ├── vision.py          # Vision and screenshot tools
│   └── wait.py            # Wait condition tools
├── transports/            # Multiple transport protocols
│   ├── __init__.py        # Transport exports
│   ├── streamable_http.py # HTTP transport
│   └── websocket.py       # WebSocket transport
├── tests/                 # Comprehensive test suite
│   ├── conftest.py        # Test configuration
│   ├── fixtures.py        # Test fixtures
│   ├── test_*.py          # Individual test modules
│   └── README.md          # Testing documentation
├── context.py             # Server context and state management
├── server.py              # Main MCP server implementation
├── main.py                # CLI entry point
├── __init__.py            # Package initialization
├── pyproject.toml         # Project configuration
├── requirements.txt       # Dependencies
└── README.md              # This documentation
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

- **Python 3.11+** (Required)
- **Playwright** browsers
- **uv** (recommended) or pip for package management

### Installation

#### Using uv (Recommended)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone <repository-url>
cd MCP_Server_Automation_Framework

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

#### Using pip

```bash
pip install -r requirements.txt
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

#### 3. HTTP Mode
```bash
python main.py --transport http --port 8080
```

#### 4. List Available Capabilities
```bash
python main.py --list-capabilities
```

## 📋 Configuration System

### Available Tool Capabilities

The framework provides 13 distinct capability categories:

| Capability | Description | Tool Count |
|------------|-------------|------------|
| `core` | Basic navigation, resize, close | Always enabled |
| `vision` | Screenshots, visual interactions | 8 tools |
| `tabs` | Tab management, creation, switching | 4 tools |
| `console` | Console message handling | 2 tools |
| `keyboard` | Keyboard input and key pressing | 1 tool |
| `network` | Request interception, monitoring | 2 tools |
| `files` | File upload and download | 1 tool |
| `testing` | Test code generation | 1 tool |
| `wait` | Wait conditions and timing | 3 tools |
| `pdf` | PDF generation | 1 tool |
| `history` | Browser navigation history | 2 tools |
| `install` | Installation utilities | 0 tools |
| `api` | HTTP API testing and requests | 7 tools |

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
    """Enhanced server context matching Playwright MCP's Context functionality."""
    
    def __init__(self, settings: Settings, capabilities: Optional[List[str]] = None):
        self.settings = settings
        self.client_version: Optional[str] = None
        self._browser_context_manager = get_browser_context_manager(settings)
        self._tabs: List[Tab] = []
        self._modal_states: List[ModalStateWithTab] = []
        self._download_tracker = DownloadTracker(settings.output_dir)
        self._pending_action: Optional[Dict[str, Any]] = None
        self.tool_registry = EnhancedToolRegistry(self, capabilities)
```

**Key Features:**
- TypeScript-compatible context management
- Modal state tracking (dialogs, file choosers)
- Download state management
- Tab lifecycle management
- Client capability detection
- Racing modal dialog protection

### 2. Tool System (`tools/`)

#### Tool Registry (`tools/registry.py`)

Dynamic tool management with vision mode support:

```python
class EnhancedToolRegistry:
    """Enhanced tool registry matching Playwright MCP's tool management."""
    
    def __init__(self, context: "ServerContext", capabilities: Optional[List[ToolCapability]] = None):
        # Create tools based on vision mode
        vision_mode = context.settings.enable_vision
        self._snapshot_tools = self._create_snapshot_tools()  # 30 tools
        self._vision_tools = self._create_vision_tools()      # 30 tools
        
        # Select appropriate tool set
        all_tools = self._vision_tools if vision_mode else self._snapshot_tools
        self._tools = filter_tools_by_capabilities(all_tools, capabilities)
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

### 3. Browser Context Factory (`core/browser_context_factory.py`)

Multiple browser context creation strategies:

```python
class BrowserContextFactory(ABC):
    """Abstract browser context factory matching Playwright MCP patterns."""
    
# Available Implementations:
# - IsolatedContextFactory: Fresh browser instances
# - PersistentContextFactory: Persistent user data
# - CDPContextFactory: Connect to existing browser via CDP
```

### 4. Snapshot System (`core/snapshot.py`)

Advanced page analysis with TypeScript compatibility:

```python
class PageSnapshot:
    """Page snapshot with accessibility tree and element references."""
    
    async def capture(self, include_screenshot: bool = True) -> None:
        """Capture comprehensive page snapshot."""
        await self._capture_accessibility_tree()
        await self._capture_element_references()
        if include_screenshot:
            await self._capture_screenshot()
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

Comprehensive testing with **19 test files** covering all components:

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
  --transport http \
  --host 0.0.0.0 \
  --port 8080 \
  --headless \
  --isolated \
  --caps "core,vision,interaction" \
  --output-dir /var/log/mcp-server \
  --save-trace
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
mcp>=1.0.0                    # Model Context Protocol
playwright>=1.40.0            # Browser automation
pydantic>=2.0.0              # Data validation
anyio>=4.0.0                 # Async primitives
starlette>=0.27.0            # Web framework
uvicorn>=0.24.0              # ASGI server
websockets>=12.0             # WebSocket support
```

### Development Dependencies

```
pytest>=7.4.0                # Testing framework
pytest-asyncio>=0.21.0       # Async test support
pytest-mock>=3.11.0          # Mocking utilities
black                        # Code formatting
ruff                         # Fast linting
mypy                         # Type checking
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

*This implementation achieves 100% compatibility with the TypeScript playwright-mcp while providing additional Python-specific enhancements and comprehensive testing coverage.*

# MCP Client Framework

## 🎯 Testing với MCP Server Automation Framework

Framework này được thiết kế để kết nối với **MCP Server Automation Framework** (browser automation server) của bạn.

### 📋 Hướng Dẫn Test Đầy Đủ

#### **Bước 1: Khởi động MCP Server của bạn**

```bash
# Khởi động MCP Server Automation Framework
python start_mcp_server.py
```

Server sẽ chạy trên:
- **HTTP/SSE**: `http://localhost:8000`
- **WebSocket**: `ws://localhost:8765`

#### **Bước 2: Test tất cả Transport Types**

```bash
# Test nhanh tất cả transport
python test_all_transports.py

# Test đầy đủ với báo cáo chi tiết
python complete_test_guide.py
```

#### **Bước 3: Test Web Interface**

```bash
# Khởi động API server (terminal 1)
python run_server.py

# Khởi động Web UI (terminal 2)  
streamlit run run_ui.py
```

Mở browser: `http://localhost:8501`

### 🔧 Cấu Hình Transport Types

#### **SSE (Server-Sent Events) - Recommended**
```python
config = MCPConfig.for_sse(
    server_url="http://localhost:8000/sse",
    timeout=30.0
)
```

#### **WebSocket - Real-time**
```python
config = MCPConfig.for_websocket(
    server_url="ws://localhost:8765",
    timeout=30.0
)
```

#### **StreamableHTTP - Alternative**
```python
config = MCPConfig.for_streamablehttp(
    server_url="http://localhost:8000/mcp",
    timeout=30.0
)
```

### 🎮 Browser Automation Tools

Server cung cấp các tools cho browser automation:

- **Core**: `browser_navigate`, `browser_close`, `browser_resize`
- **Interaction**: `browser_click`, `browser_type`, `browser_hover`
- **Vision**: `browser_screenshot`, `browser_capture_snapshot`
- **Tabs**: Tab management tools
- **Files**: Upload/download tools
- **Network**: Request interception

### 📊 Test Results

Sau khi chạy test, bạn sẽ thấy:

```
============================================================
🚀 TEST SUMMARY REPORT
============================================================

📊 Overall Results:
   • Total Transports Tested: 3
   • Successful Connections: 3
   • Success Rate: 100.0%

Transport Details
------------------------------------------------------------

SSE (Server-Sent Events) : ✅ PASS
   Server: MCP Server Automation Framework
   Tools: 30 total, 12 browser tools
   ✅ Browser navigation test passed

WebSocket                : ✅ PASS
   Server: MCP Server Automation Framework  
   Tools: 30 total, 12 browser tools
   ✅ Browser navigation test passed

StreamableHTTP           : ✅ PASS
   Server: MCP Server Automation Framework
   Tools: 30 total, 12 browser tools
```

### 🚀 Production Usage

#### **Direct Client Usage**
```python
from mcp_framework.core.config import MCPConfig
from mcp_framework.core.client_advanced import MCPClientAdvanced

# Connect to your browser automation server
config = MCPConfig.for_sse("http://localhost:8000/sse")
client = MCPClientAdvanced(config)

await client.connect()

# Use browser automation tools
result = await client.call_tool("browser_navigate", {
    "url": "https://example.com"
})

result = await client.call_tool("browser_screenshot", {
    "full_page": True
})

await client.disconnect()
```

#### **API Server Integration**
```bash
# Start API server
python run_server.py

# Connect via REST API
curl -X POST http://localhost:8001/api/v1/connect \
  -H "Content-Type: application/json" \
  -d '{
    "transport": "sse",
    "server_url": "http://localhost:8000/sse"
  }'
```

### 🏗️ Architecture

- **Core**: `MCPClientAdvanced`, `MCPConfig`, Transport Factory
- **Transports**: SSE, WebSocket, StreamableHTTP support
- **API**: FastAPI REST interface on port 8001
- **UI**: Streamlit web interface on port 8501  
- **AI**: Gemini integration for chat interface

### 📝 Configuration

Environment variables:
```bash
export GEMINI_API_KEY=your_api_key
export MCP_SERVER_URL=http://localhost:8000
export API_SERVER_PORT=8001
```

### 🐛 Troubleshooting

**Server not responding:**
```bash
# Check if your MCP server is running
python start_mcp_server.py

# Check ports
netstat -an | grep :8000
netstat -an | grep :8765
```

**Transport failed:**
- SSE: Check `http://localhost:8000/sse`
- WebSocket: Check `ws://localhost:8765`
- Check firewall settings

**Performance:**
- SSE: Best for most cases
- WebSocket: Real-time updates
- StreamableHTTP: Alternative if SSE fails
