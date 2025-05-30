# MCP Server Automation Framework

A comprehensive Model Context Protocol (MCP) server providing advanced automation capabilities for browser control, API testing, database operations, and Google Sheets integration using Server-Sent Events (SSE) transport.

## 🚀 Overview

This MCP server framework delivers a robust automation testing platform with the following core capabilities:

- **Browser Automation**: Full-featured web automation using Playwright with support for Chromium, Firefox, and WebKit
- **API Testing**: Complete REST API client with authentication support (Basic, Bearer Token, OAuth2)
- **Database Operations**: SQL Server connectivity with comprehensive query and transaction support
- **Google Sheets Integration**: Service account-based Google Sheets API integration
- **Vision-Based Automation**: Screenshot capture and coordinate-based interactions
- **SSE Transport**: Real-time communication using Server-Sent Events


## 🛠️ Available Tools by Category

### Browser Core Tools (13 tools)
- `browser_navigate` - Navigate to URLs
- `browser_go_back` - Navigate back in history
- `browser_reload` - Reload current page
- `get_current_url` - Get current page URL and title
- `browser_click` - Click elements by selector
- `browser_fill` - Fill form fields (fast method)
- `browser_type_advanced` - Type with delays and auto-submit
- `browser_press_key` - Press keyboard keys
- `browser_hover` - Hover over elements
- `browser_find_by_xpath` - Find elements using XPath
- `browser_select_option` - Select dropdown options
- `clear_field` - Clear input field content
- `browser_close` - Close browser with cleanup options
- `browser_resize` - Resize browser window
- `browser_install` - Install browser dependencies

### Browser Advanced Tools (7 tools)
- `browser_drag` - Drag and drop between elements
- `browser_handle_dialog` - Handle alerts, confirms, prompts
- `browser_console_messages` - Capture console logs and errors
- `browser_scroll_to_top` - Scroll to page top
- `browser_scroll_to_bottom` - Scroll to page bottom
- `browser_scroll_to_element` - Scroll element into view
- `browser_scroll_one_step` - Incremental scrolling
- `browser_wait_for` - Wait for conditions (element visibility, text presence)

### Browser Data Tools (6 tools)
- `get_page_content` - Extract visible text content
- `get_page_html` - Get full HTML source
- `get_page_title` - Get page title and URL
- `clear_browser_data` - Clear cookies and storage
- `get_cookies` - Retrieve all cookies
- `browser_file_upload` - Upload files to input elements

### Browser Vision Tools (10 tools)
- `browser_capture_for_vision` - Take screenshots for AI analysis
- `browser_save_screenshot` - Save screenshots to files
- `browser_save_as_pdf` - Export pages as PDF
- `browser_screen_click` - Click at pixel coordinates
- `browser_screen_drag` - Drag between coordinates
- `browser_screen_move_mouse` - Move mouse to coordinates
- `browser_tab_list` - List all open tabs
- `browser_tab_new` - Open new tabs
- `browser_tab_select` - Switch between tabs
- `browser_tab_close` - Close specific tabs

### API Tools (9 tools)
- `api_init` - Initialize REST client
- `api_get` - HTTP GET requests
- `api_post` - HTTP POST requests
- `api_put` - HTTP PUT requests
- `api_delete` - HTTP DELETE requests
- `api_basic_auth` - Basic authentication
- `api_bearer_token` - Bearer token authentication
- `api_oauth2_client_credentials` - OAuth2 client credentials flow
- `api_clear_auth` - Clear authentication

### Database Tools (9 tools)
- `db_connect` - Connect to SQL Server
- `db_connect_with_string` - Connect with custom connection string
- `db_query` - Execute SELECT queries
- `db_execute` - Execute INSERT/UPDATE/DELETE
- `db_execute_many` - Batch execute with parameters
- `db_execute_script` - Run multi-statement scripts
- `db_get_tables` - List database tables
- `db_get_columns` - Get table column information
- `db_close` - Close database connection

### Google Sheets Tools (7 tools)
- `google_sheets_init` - Initialize with service account
- `google_sheets_read` - Read sheet data
- `google_sheets_write` - Write data to sheets
- `google_sheets_append` - Append rows to sheets
- `google_sheets_clear` - Clear sheet ranges
- `google_sheets_create_sheet` - Create new sheet tabs
- `google_sheets_get_sheets` - Get spreadsheet metadata

## 📋 Requirements

- **Python**: 3.11 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Disk Space**: 1GB for browser binaries and dependencies

### Required Dependencies

**Core Dependencies:**
- `mcp[cli]>=1.8.0` - Model Context Protocol framework
- `requests>=2.32.0` - HTTP client library
- `nest-asyncio>=1.6.0` - Nested async loop support
- `playwright>=1.52.0` - Browser automation
- `psutil>=7.0.0` - System process management
- `pyodbc>=5.2.0` - SQL Server database connectivity

**Optional Dependencies:**
- `google-auth>=2.40.0` - Google API authentication
- `google-api-python-client>=2.169.0` - Google Sheets API

## 🚀 Installation

### Method 1: Using uv (Recommended)

```bash
# Clone the repository
git clone https://gitlab.nexdev.net/victor.nguyen1/mcp_server_automation_framework.git
cd mcp_server_automation_framework

# Install uv if you haven't already
pip install uv

# Create virtual environment and install dependencies
uv venv
uv sync

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install Playwright browsers
playwright install chromium

# Install additional browsers (optional)
playwright install firefox webkit
```

### Method 2: Using pip

```bash
# Clone the repository
git clone https://gitlab.nexdev.net/victor.nguyen1/mcp_server_automation_framework.git
cd mcp_server_automation_framework

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install additional browsers (optional)
playwright install firefox webkit
```

### Method 3: Using Docker

```bash
# Clone the repository
git clone https://gitlab.nexdev.net/victor.nguyen1/mcp_server_automation_framework.git
cd mcp_server_automation_framework

# Build Docker image
docker build -t mcp-automation-framework .

# Run container
docker run -p 5000:5000 mcp-automation-framework
```

## ⚙️ Configuration

### Environment Variables

```bash
# Server configuration
SERVER_HOST=127.0.0.1                    # Server host address
SERVER_PORT=5000                         # Server port number
SERVER_DEBUG=false                       # Enable debug mode

# Browser configuration  
BROWSER_TYPE=chromium                    # Browser type (chromium, firefox, webkit)
BROWSER_HEADLESS=false                   # Run browser in headless mode
BROWSER_VIEWPORT_WIDTH=1200              # Browser window width
BROWSER_VIEWPORT_HEIGHT=900              # Browser window height

# Database configuration
DATABASE_DRIVER="ODBC Driver 17 for SQL Server"  # SQL Server driver
DATABASE_CONNECTION_TIMEOUT=30                   # Connection timeout (seconds)
DATABASE_QUERY_TIMEOUT=30                       # Query timeout (seconds)

# API configuration
API_REQUEST_TIMEOUT=30                   # API request timeout (seconds)
API_MAX_RETRIES=3                       # Maximum retry attempts

# File system configuration
OUTPUT_DIRECTORY=./output               # Output directory for files
SCREENSHOTS_DIRECTORY=./output/screenshots  # Screenshot save location
PDFS_DIRECTORY=./output/pdfs           # PDF save location
```

### Google Sheets Setup

1. **Create a Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Sheets API and Google Drive API

2. **Create Service Account:**
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Fill in service account details
   - Download the JSON key file

3. **Configure Credentials:**
   - Place the JSON key file in `mcp_server/keys/service-account.json`
   - Or specify custom path when initializing

4. **Share Spreadsheets:**
   - Share your Google Sheets with the service account email
   - Grant appropriate permissions (Viewer/Editor)

## 🚀 Usage

### Starting the Server

```bash
# Basic startup
python server.py

# Custom host and port
python server.py --host 0.0.0.0 --port 8080

# Enable debug mode
python server.py --debug

# Using environment variables
export SERVER_HOST=0.0.0.0
export SERVER_PORT=8080
python server.py
```

### Server Endpoints

- **SSE Endpoint**: `http://localhost:5000/sse` - Main MCP communication
- **Messages**: `http://localhost:5000/messages/` - Message handling
- **Health Check**: `http://localhost:5000/health` - Server status
- **Tools List**: `http://localhost:5000/tools` - Available tools information

### Example Usage Scenarios

#### 1. Browser Automation

```python
# Connect to MCP server and use browser tools
# Navigate to a website
await mcp.call_tool("browser_navigate", {"url": "https://example.com"})

# Click an element
await mcp.call_tool("browser_click", {"selector": "#login-button"})

# Fill a form
await mcp.call_tool("browser_fill", {"selector": "#username", "text": "user@example.com"})

# Take a screenshot
await mcp.call_tool("browser_capture_for_vision", {"full_page": true})
```

#### 2. API Testing

```python
# Initialize API client
await mcp.call_tool("api_init", {"base_url": "https://api.example.com"})

# Set authentication
await mcp.call_tool("api_bearer_token", {"token": "your-api-token"})

# Make API requests
await mcp.call_tool("api_get", {"endpoint": "/users"})
await mcp.call_tool("api_post", {"endpoint": "/users", "json_data": {"name": "John Doe"}})
```

#### 3. Database Operations

```python
# Connect to SQL Server
await mcp.call_tool("db_connect", {
    "server": "localhost",
    "database": "TestDB",
    "trusted_connection": true
})

# Execute queries
await mcp.call_tool("db_query", {"query": "SELECT * FROM Users"})
await mcp.call_tool("db_execute", {"query": "INSERT INTO Users (name) VALUES (?)", "params": ["John Doe"]})
```

#### 4. Google Sheets Integration

```python
# Initialize Google Sheets
await mcp.call_tool("google_sheets_init", {"credentials_file": "path/to/service-account.json"})

# Read data
await mcp.call_tool("google_sheets_read", {
    "spreadsheet_id": "your-spreadsheet-id",
    "range_name": "Sheet1!A1:D10"
})

# Write data
await mcp.call_tool("google_sheets_write", {
    "spreadsheet_id": "your-spreadsheet-id",
    "range_name": "Sheet1!A1",
    "data": [["Name", "Age"], ["John", 30], ["Jane", 25]]
})
```

## 🔧 Advanced Configuration

### Custom Settings

Modify `mcp_server/config/settings.py` to customize:

- **Timeouts**: Navigation, click, API, database timeouts
- **Limits**: URL length, selector length, XPath length
- **Browser Settings**: Viewport size, wait strategies
- **File Paths**: Output directories, naming patterns
- **Security**: Allowed/blocked domains, validation rules

### Performance Tuning

```python
# Concurrent operations limits
MAX_CONCURRENT_BROWSERS = 3
MAX_CONCURRENT_API_REQUESTS = 10
MAX_CONCURRENT_DB_CONNECTIONS = 5

# Memory limits
MAX_PAGE_SIZE_MB = 100
MAX_RESPONSE_SIZE_MB = 50
```

## 🔒 Security Considerations

### Browser Security
- Browsers run in controlled environment
- Domain filtering available for blocking malicious sites
- Headless mode recommended for production

### Database Security
- Uses parameterized queries to prevent SQL injection
- Connection string encryption recommended
- Limited connection timeouts

### API Security
- Supports multiple authentication methods
- Request/response size limits
- Rate limiting capabilities

### Google Sheets Security
- Service account authentication (no user credentials stored)
- Scoped API access
- Automatic token refresh

## 🐛 Troubleshooting

### Common Issues

#### Browser Installation Problems
```bash
# Reinstall Playwright browsers
playwright install --force chromium

# Install system dependencies (Linux)
playwright install-deps chromium
```

#### Database Connection Issues
```bash
# Install ODBC driver for SQL Server
# Windows: Download from Microsoft
# Linux: apt-get install unixodbc-dev
# macOS: brew install unixodbc
```

#### Google Sheets Authentication
```bash
# Verify service account file
python -c "import json; print(json.load(open('path/to/service-account.json'))['client_email'])"

# Check API enablement in Google Cloud Console
# Ensure Sheets API and Drive API are enabled
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
python server.py --debug
```

### Log Files

Check log files in `/app/logs/` directory:
- Application logs
- Error traces
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
uv add --dev pytest black flake8 mypy

# Run tests
pytest tests/

# Code formatting
black mcp_server/
flake8 mcp_server/

# Type checking
mypy mcp_server/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏗️ Architecture

### Core Components

1. **MCP Server**: FastMCP-based server with SSE transport
2. **Service Context**: Shared state management across tools
3. **Playwright Manager**: Singleton browser instance management
4. **Configuration System**: Centralized settings with validation
5. **Tool Registration**: Automatic discovery and registration of MCP tools


## 🔄 Version History

### v1.0.0 (Current)
- Initial release with full MCP automation framework
- Browser automation with Playwright
- REST API testing capabilities
- SQL Server database integration
- Google Sheets API support
- SSE-based transport

## 🎯 Roadmap

### Planned Features
- [ ] Built-in test recording and playback
- [ ] Mobile browser automation support
---

**MCP Server Automation Framework** - Empowering automation through Model Context Protocol