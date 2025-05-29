# MCP Server Framework Configuration

This directory contains centralized configuration for the MCP Automation Testing Framework.

## Settings Configuration

All configuration values are defined in `settings.py` and are **fixed values** (not read from environment variables). This ensures consistent behavior across all deployments.

### Configuration Categories

#### 1. Server Configuration
- `SERVER_HOST`: Server host address (default: "127.0.0.1")
- `SERVER_PORT`: Server port (default: 5000)
- `SERVER_DEBUG`: Debug mode (default: False)
- `SERVER_LOG_LEVEL`: Logging level (default: "INFO")

#### 2. Browser Configuration
- `BROWSER_TYPE`: Browser engine (default: "chromium")
- `BROWSER_HEADLESS`: Headless mode (default: True)
- `BROWSER_VIEWPORT_WIDTH/HEIGHT`: Viewport size (default: 1200x900)
- `BROWSER_NAVIGATION_TIMEOUT`: Page navigation timeout (default: 30000ms)
- `BROWSER_CLICK_TIMEOUT`: Element click timeout (default: 10000ms)
- `BROWSER_SCROLL_DELAY`: Scroll animation delay (default: 0.5s)

#### 3. Database Configuration
- `DATABASE_DRIVER`: ODBC driver name (default: "ODBC Driver 17 for SQL Server")
- `DATABASE_CONNECTION_TIMEOUT`: Connection timeout (default: 30s)
- `DATABASE_QUERY_TIMEOUT`: Query execution timeout (default: 30s)

#### 4. API Client Configuration
- `API_REQUEST_TIMEOUT`: HTTP request timeout (default: 30s)
- `API_DEFAULT_HEADERS`: Default HTTP headers including User-Agent
- `API_MAX_RETRIES`: Maximum retry attempts (default: 3)

#### 5. File System Configuration
- `TEMP_DIRECTORY`: Temporary files directory
- `OUTPUT_DIRECTORY`: Main output directory
- `SCREENSHOTS_DIRECTORY`: Screenshots output directory
- `PDFS_DIRECTORY`: PDF files output directory
- `HTML_EXPORTS_DIRECTORY`: HTML exports directory

#### 6. Google Sheets Configuration
- `GOOGLE_SCOPES`: OAuth2 scopes for Google Sheets API
- `GOOGLE_TOKEN_FILENAME`: Token file name (default: "token.json")
- `GOOGLE_CREDENTIALS_FILENAME`: Credentials file name (default: "credentials.json")

#### 7. Security Configuration
- `MAX_URL_LENGTH`: Maximum URL length (default: 2048)
- `MAX_SELECTOR_LENGTH`: Maximum CSS selector length (default: 500)
- `MAX_XPATH_LENGTH`: Maximum XPath expression length (default: 500)
- `ALLOWED_DOMAINS`: List of allowed domains (empty = all allowed)
- `BLOCKED_DOMAINS`: List of blocked domains

#### 8. Performance Configuration
- `MAX_CONCURRENT_BROWSERS`: Maximum concurrent browser instances (default: 3)
- `MAX_CONCURRENT_API_REQUESTS`: Maximum concurrent API requests (default: 10)
- `MAX_CONCURRENT_DB_CONNECTIONS`: Maximum concurrent database connections (default: 5)

### Usage

```python
from mcp_server.config.settings import settings

# Access configuration values
browser_type = settings.BROWSER_TYPE
viewport = settings.get_browser_viewport()
connection_string = settings.get_database_connection_string(
    server="localhost",
    database="test",
    trusted_connection=True
)

# Validation
is_valid = settings.validate_url("https://example.com")
is_valid_pdf = settings.validate_pdf_format("A4")
```

### Helper Methods

- `get_browser_viewport()`: Returns viewport as (width, height) tuple
- `get_database_connection_string()`: Builds database connection string
- `get_output_path()`: Gets full output path with directory creation
- `validate_browser_type()`: Validates browser type
- `validate_pdf_format()`: Validates PDF format
- `validate_url()`: Validates URL length
- `validate_selector()`: Validates selector length

### Configuration Updates

To modify configuration values:

1. Edit `mcp_server/config/settings.py`
2. Update the class variables in the `Settings` class
3. Restart the server for changes to take effect

**Note**: All values are hardcoded and not read from environment variables to ensure consistent behavior across environments.

### Examples

#### Browser Configuration
```python
# Browser settings affect all browser operations
BROWSER_TYPE = "chromium"          # Use Chromium browser
BROWSER_HEADLESS = True            # Run in headless mode
BROWSER_VIEWPORT_WIDTH = 1920      # Wider viewport
BROWSER_VIEWPORT_HEIGHT = 1080     # Taller viewport
```

#### Timeout Configuration
```python
# Timeout settings affect operation reliability
BROWSER_NAVIGATION_TIMEOUT = 45000  # 45 seconds for slow pages
BROWSER_CLICK_TIMEOUT = 15000       # 15 seconds for element clicks
API_REQUEST_TIMEOUT = 60            # 60 seconds for API calls
```

#### Security Configuration
```python
# Security settings protect against malicious content
ALLOWED_DOMAINS = ["example.com", "trusted-site.org"]  # Only allow specific domains
MAX_URL_LENGTH = 1024                                  # Stricter URL length limit
MAX_XPATH_LENGTH = 200                                 # Shorter XPath expressions
```

This centralized configuration approach ensures:
- **Consistency**: Same behavior across all environments
- **Maintainability**: Single location for all configuration
- **Validation**: Built-in validation for configuration values
- **Documentation**: Clear understanding of all settings
- **Performance**: Optimized defaults for common use cases 