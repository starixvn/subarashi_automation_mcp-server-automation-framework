import argparse
import logging
import os
from typing import List, Optional

from .settings import (
    CLIOptions,
    resolve_cli_config,
    validate_config,
)

logger = logging.getLogger(__name__)


def semicolon_separated_list(value: str) -> List[str]:
    return [v.strip() for v in value.split(";")]


def comma_separated_list(value: str) -> List[str]:
    return [v.strip() for v in value.split(",")]


def create_enhanced_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcp-automation-server",
        description="MCP Automation Server with Enhanced Configuration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with headless mode
  python -m mcp_server_new --headless
  
  # Use specific browser with custom viewport
  python -m mcp_server_new --browser chrome --viewport-size "1920,1080"
  
  # Connect to existing browser via CDP
  python -m mcp_server_new --cdp-endpoint ws://localhost:9222
  
  # Use configuration file
  python -m mcp_server_new --config config.json
  
  # Enable specific capabilities only
  python -m mcp_server_new --caps "core,navigation,interaction"
  
  # Run with proxy and custom output directory
  python -m mcp_server_new --proxy-server http://proxy:8080 --output-dir ./output
        """,
    )

    parser.add_argument(
        "--allowed-origins",
        type=semicolon_separated_list,
        help="semicolon-separated list of origins to allow the browser to request. Default is to allow all.",
        metavar="ORIGINS",
    )
    parser.add_argument(
        "--blocked-origins",
        type=semicolon_separated_list,
        help="semicolon-separated list of origins to block the browser from requesting. Blocklist is evaluated before allowlist. If used without the allowlist, requests not matching the blocklist are still allowed.",
        metavar="ORIGINS",
    )
    parser.add_argument(
        "--block-service-workers", action="store_true", help="block service workers"
    )

    parser.add_argument(
        "--browser",
        choices=[
            "chrome",
            "chrome-beta",
            "chrome-canary",
            "chrome-dev",
            "chromium",
            "firefox",
            "webkit",
            "msedge",
            "msedge-beta",
            "msedge-canary",
            "msedge-dev",
        ],
        help="browser or chrome channel to use, possible values: chrome, firefox, webkit, msedge.",
    )
    parser.add_argument(
        "--browser-agent", help="Use browser agent (experimental).", metavar="ENDPOINT"
    )

    parser.add_argument(
        "--caps",
        help="comma-separated list of capabilities to enable, possible values: core, vision, tabs, console, keyboard, network, files, testing, wait, pdf, api. Default is all.",
        metavar="CAPS",
    )

    parser.add_argument(
        "--cdp-endpoint", help="CDP endpoint to connect to.", metavar="ENDPOINT"
    )

    parser.add_argument(
        "--config", help="path to the configuration file.", metavar="PATH"
    )

    parser.add_argument(
        "--device", help='device to emulate, for example: "iPhone 15"', metavar="DEVICE"
    )

    parser.add_argument(
        "--executable-path", help="path to the browser executable.", metavar="PATH"
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="run browser in headless mode, headed by default",
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="host to bind server to. Default is localhost. Use 0.0.0.0 to bind to all interfaces.",
        metavar="HOST",
    )

    parser.add_argument(
        "--ignore-https-errors", action="store_true", help="ignore https errors"
    )

    parser.add_argument(
        "--isolated",
        action="store_true",
        help="keep the browser profile in memory, do not save it to disk.",
    )

    parser.add_argument(
        "--image-responses",
        choices=["allow", "omit", "auto"],
        default="auto",
        help='whether to send image responses to the client. Can be "allow", "omit", or "auto". Defaults to "auto", which sends images if the client can display them.',
    )

    parser.add_argument(
        "--no-sandbox",
        action="store_true",
        help="disable the sandbox for all process types that are normally sandboxed.",
    )

    parser.add_argument(
        "--output-dir", help="path to the directory for output files.", metavar="PATH"
    )

    parser.add_argument(
        "--port", type=int, help="port to listen on for SSE transport.", metavar="PORT"
    )

    parser.add_argument(
        "--proxy-bypass",
        help='comma-separated domains to bypass proxy, for example ".com,chromium.org,.domain.com"',
        metavar="BYPASS",
    )
    parser.add_argument(
        "--proxy-server",
        help='specify proxy server, for example "http://myproxy:3128" or "socks5://myproxy:8080"',
        metavar="PROXY",
    )

    parser.add_argument(
        "--save-trace",
        action="store_true",
        help="Whether to save the Playwright Trace of the session into the output directory.",
    )

    parser.add_argument(
        "--storage-state",
        help="path to the storage state file for isolated sessions.",
        metavar="PATH",
    )

    parser.add_argument(
        "--user-agent", help="specify user agent string", metavar="UA_STRING"
    )

    parser.add_argument(
        "--user-data-dir",
        help="path to the user data directory. If not specified, a temporary directory will be created.",
        metavar="PATH",
    )

    parser.add_argument(
        "--viewport-size",
        help='specify browser viewport size in pixels, for example "1280,720"',
        metavar="SIZE",
    )

    parser.add_argument(
        "--vision",
        action="store_true",
        help="Run server that uses screenshots (Aria snapshots are used by default)",
    )

    parser.add_argument(
        "--extension",
        action="store_true",
        help=argparse.SUPPRESS,  # Hidden option like Playwright MCP
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "websocket", "sse", "http"],
        default="stdio",
        help="Transport method to use (default: stdio)",
    )

    parser.add_argument(
        "--list-capabilities",
        action="store_true",
        help="List all available capabilities and exit",
    )

    return parser


def parse_enhanced_args(args: Optional[List[str]] = None) -> CLIOptions:
    parser = create_enhanced_parser()
    parsed_args = parser.parse_args(args)
    cli_options = CLIOptions(
        allowed_origins=parsed_args.allowed_origins,
        blocked_origins=parsed_args.blocked_origins,
        block_service_workers=parsed_args.block_service_workers,
        browser=parsed_args.browser,
        browser_agent=parsed_args.browser_agent,
        caps=parsed_args.caps,
        cdp_endpoint=parsed_args.cdp_endpoint,
        config=parsed_args.config,
        device=parsed_args.device,
        executable_path=parsed_args.executable_path,
        headless=parsed_args.headless,
        host=parsed_args.host,
        ignore_https_errors=parsed_args.ignore_https_errors,
        isolated=parsed_args.isolated,
        image_responses=parsed_args.image_responses,
        sandbox=not parsed_args.no_sandbox,  # Invert no_sandbox
        output_dir=parsed_args.output_dir,
        port=parsed_args.port,
        proxy_bypass=parsed_args.proxy_bypass,
        proxy_server=parsed_args.proxy_server,
        save_trace=parsed_args.save_trace,
        storage_state=parsed_args.storage_state,
        user_agent=parsed_args.user_agent,
        user_data_dir=parsed_args.user_data_dir,
        viewport_size=parsed_args.viewport_size,
        vision=parsed_args.vision,
        extension=parsed_args.extension,
    )

    cli_options.transport = parsed_args.transport  # type: ignore
    cli_options.list_capabilities = parsed_args.list_capabilities  # type: ignore
    if not cli_options.storage_state and cli_options.transport == "stdio":
        default_storage = "config/keys/storage_state.json"
        if os.path.exists(default_storage):
            cli_options.storage_state = default_storage
        else:
            logger.warning(f"Default storage state file not found: {default_storage}")
            logger.info("Server will run without authentication state")

    return cli_options


def validate_cli_options(cli_options: CLIOptions):
    if cli_options.storage_state and not os.path.exists(cli_options.storage_state):
        logger.warning(f"Storage state file not found: {cli_options.storage_state}")
        logger.info("Server will run without authentication state")
        cli_options.storage_state = None

    if cli_options.device and cli_options.cdp_endpoint:
        raise ValueError("Device emulation is not supported with cdpEndpoint.")
    if cli_options.device and cli_options.extension:
        raise ValueError("Device emulation is not supported with extension mode.")

    if cli_options.extension:
        if not cli_options.port:
            raise ValueError("--port parameter is required for extension mode")

    if cli_options.viewport_size:
        try:
            width_str, height_str = cli_options.viewport_size.split(",")
            width, height = int(width_str.strip()), int(height_str.strip())
            if width <= 0 or height <= 0:
                raise ValueError("Viewport dimensions must be positive")
        except (ValueError, IndexError):
            raise ValueError(
                'Invalid viewport size format: use "width,height", for example --viewport-size="800,600"'
            )


def list_capabilities():
    print("Available tool capabilities:")
    capabilities = [
        "core",
        "vision",
        "tabs",
        "console",
        "keyboard",
        "network",
        "files",
        "wait",
        "api",
        "google_sheets",
        "database",
    ]
    for capability in capabilities:
        print(f"  - {capability}")


async def resolve_enhanced_config(cli_options: CLIOptions):
    validate_cli_options(cli_options)

    config = await resolve_cli_config(cli_options)

    validate_config(config)

    return config


def print_config_summary(config):
    logger.info("Configuration Summary:")
    logger.info(f"  Browser: {config.browser.browser_name}")
    logger.info(f"  Headless: {config.browser.launch_options.headless}")
    logger.info(f"  Isolated: {config.browser.isolated}")
    logger.info(f"  Vision: {config.vision}")
    logger.info(f"  Output Dir: {config.output_dir}")

    if config.browser.cdp_endpoint:
        logger.info(f"  CDP Endpoint: {config.browser.cdp_endpoint}")

    if config.browser.user_data_dir:
        logger.info(f"  User Data Dir: {config.browser.user_data_dir}")

    if config.capabilities:
        logger.info(f"  Capabilities: {', '.join(config.capabilities)}")

    if config.server.port:
        logger.info(f"  Server Port: {config.server.port}")
        logger.info(f"  Server Host: {config.server.host}")


def parse_capabilities(capabilities_str: Optional[str]) -> Optional[List[str]]:
    if not capabilities_str:
        return None

    capabilities = [cap.strip() for cap in capabilities_str.split(",")]

    valid_capabilities = {
        "core",
        "vision",
        "tabs",
        "console",
        "keyboard",
        "network",
        "files",
        "wait",
        "api",
        "google_sheets",
        "database",
    }
    invalid_capabilities = set(capabilities) - valid_capabilities

    if invalid_capabilities:
        logger.warning(f"Invalid capabilities: {invalid_capabilities}")
        logger.info(f"Valid capabilities: {sorted(valid_capabilities)}")
        capabilities = [cap for cap in capabilities if cap in valid_capabilities]

    return capabilities if capabilities else None
