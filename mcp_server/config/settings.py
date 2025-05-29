"""
MCP Server Framework Settings
Centralized configuration for all components
"""

import os
import tempfile
from typing import Dict, Any, Tuple

class Settings:
    """Central settings class for MCP Server Framework"""
    
    # =====================================================
    # SERVER CONFIGURATION
    # =====================================================
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 5000
    SERVER_DEBUG: bool = False
    SERVER_LOG_LEVEL: str = "INFO"
    
    # =====================================================
    # BROWSER CONFIGURATION
    # =====================================================
    BROWSER_TYPE: str = "chromium"  # chromium, firefox, webkit
    BROWSER_HEADLESS: bool = True
    BROWSER_VIEWPORT_WIDTH: int = 1200
    BROWSER_VIEWPORT_HEIGHT: int = 900
    
    # Browser Timeouts (milliseconds)
    BROWSER_NAVIGATION_TIMEOUT: int = 30000  # 30 seconds
    BROWSER_LOAD_STATE_TIMEOUT: int = 10000  # 10 seconds
    BROWSER_CLICK_TIMEOUT: int = 10000       # 10 seconds
    BROWSER_ELEMENT_TIMEOUT: int = 5000      # 5 seconds
    
    # Browser Wait Strategies
    BROWSER_WAIT_UNTIL: str = "domcontentloaded"  # load, domcontentloaded, networkidle
    BROWSER_SCROLL_DELAY: float = 0.5  # seconds
    
    # =====================================================
    # DATABASE CONFIGURATION
    # =====================================================
    DATABASE_DRIVER: str = "ODBC Driver 17 for SQL Server"
    DATABASE_CONNECTION_TIMEOUT: int = 30  # seconds
    DATABASE_QUERY_TIMEOUT: int = 30       # seconds
    DATABASE_MAX_RETRIES: int = 3
    DATABASE_RETRY_DELAY: int = 1          # seconds
    
    # =====================================================
    # API CLIENT CONFIGURATION
    # =====================================================
    API_REQUEST_TIMEOUT: int = 30          # seconds
    API_MAX_RETRIES: int = 3
    API_RETRY_DELAY: int = 1               # seconds
    API_DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "MCP-Automation-Framework/1.0.0",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # =====================================================
    # FILE SYSTEM CONFIGURATION
    # =====================================================
    TEMP_DIRECTORY: str = tempfile.gettempdir()
    OUTPUT_DIRECTORY: str = os.path.join(os.getcwd(), "output")
    SCREENSHOTS_DIRECTORY: str = os.path.join(OUTPUT_DIRECTORY, "screenshots")
    PDFS_DIRECTORY: str = os.path.join(OUTPUT_DIRECTORY, "pdfs")
    HTML_EXPORTS_DIRECTORY: str = os.path.join(OUTPUT_DIRECTORY, "html")
    
    # File naming patterns
    TIMESTAMP_FORMAT: str = "%Y%m%d_%H%M%S"
    SCREENSHOT_PREFIX: str = "screenshot"
    PDF_PREFIX: str = "page"
    HTML_PREFIX: str = "export"
    
    # =====================================================
    # GOOGLE SHEETS CONFIGURATION
    # =====================================================
    GOOGLE_SCOPES: list = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    GOOGLE_TOKEN_FILENAME: str = "token.json"
    GOOGLE_CREDENTIALS_FILENAME: str = "credentials.json"
    
    # =====================================================
    # LOGGING CONFIGURATION
    # =====================================================
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    LOG_FILE_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    
    # =====================================================
    # CONTENT EXTRACTION CONFIGURATION
    # =====================================================
    PDF_DEFAULT_FORMAT: str = "A4"
    PDF_DEFAULT_LANDSCAPE: bool = False
    PDF_MARGIN_TOP: str = "1cm"
    PDF_MARGIN_RIGHT: str = "1cm" 
    PDF_MARGIN_BOTTOM: str = "1cm"
    PDF_MARGIN_LEFT: str = "1cm"
    
    SCREENSHOT_FULL_PAGE: bool = True
    SCREENSHOT_QUALITY: int = 90  # 0-100
    SCREENSHOT_FORMAT: str = "png"  # png, jpeg
    
    # =====================================================
    # PERFORMANCE CONFIGURATION
    # =====================================================
    MAX_CONCURRENT_BROWSERS: int = 3
    MAX_CONCURRENT_API_REQUESTS: int = 10
    MAX_CONCURRENT_DB_CONNECTIONS: int = 5
    
    # Memory limits
    MAX_PAGE_SIZE_MB: int = 100
    MAX_RESPONSE_SIZE_MB: int = 50
    
    # =====================================================
    # SECURITY CONFIGURATION
    # =====================================================
    ALLOWED_DOMAINS: list = []  # Empty means all domains allowed
    BLOCKED_DOMAINS: list = [
        "malware.example.com",
        "phishing.example.com"
    ]
    
    # Content filtering
    MAX_URL_LENGTH: int = 2048
    MAX_XPATH_LENGTH: int = 500
    MAX_SELECTOR_LENGTH: int = 500
    
    # =====================================================
    # VALIDATION RULES
    # =====================================================
    VALID_BROWSER_TYPES: list = ["chromium", "firefox", "webkit"]
    VALID_PDF_FORMATS: list = ["A4", "A3", "A5", "letter", "legal", "tabloid"]
    VALID_SCREENSHOT_FORMATS: list = ["png", "jpeg"]
    VALID_WAIT_STRATEGIES: list = ["load", "domcontentloaded", "networkidle"]
    
    # =====================================================
    # HELPER METHODS
    # =====================================================
    @classmethod
    def get_browser_viewport(cls) -> Tuple[int, int]:
        """Get browser viewport as tuple"""
        return (cls.BROWSER_VIEWPORT_WIDTH, cls.BROWSER_VIEWPORT_HEIGHT)
    
    @classmethod
    def get_database_connection_string(cls, server: str, database: str, 
                                     username: str = None, password: str = None,
                                     trusted_connection: bool = False) -> str:
        """Build database connection string"""
        if trusted_connection:
            return f"DRIVER={{{cls.DATABASE_DRIVER}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        else:
            return f"DRIVER={{{cls.DATABASE_DRIVER}}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
    
    @classmethod
    def get_output_path(cls, filename: str, subdirectory: str = "") -> str:
        """Get full output path for a file"""
        if subdirectory:
            directory = os.path.join(cls.OUTPUT_DIRECTORY, subdirectory)
        else:
            directory = cls.OUTPUT_DIRECTORY
            
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, filename)
    
    @classmethod
    def validate_browser_type(cls, browser_type: str) -> bool:
        """Validate browser type"""
        return browser_type in cls.VALID_BROWSER_TYPES
    
    @classmethod
    def validate_pdf_format(cls, pdf_format: str) -> bool:
        """Validate PDF format"""
        return pdf_format in cls.VALID_PDF_FORMATS
    
    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate URL length and format"""
        if len(url) > cls.MAX_URL_LENGTH:
            return False
        return True
    
    @classmethod
    def validate_selector(cls, selector: str) -> bool:
        """Validate selector length"""
        if len(selector) > cls.MAX_SELECTOR_LENGTH:
            return False
        return True

# Create settings instance
settings = Settings()

# Export for easy importing
__all__ = ["settings", "Settings"] 