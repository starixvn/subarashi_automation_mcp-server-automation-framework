import json
import os
import tempfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Literal
from datetime import datetime


class Settings:

    def __init__(
        self,
        browser_type: str = "chromium",
        headless: bool = False,
        enable_vision: bool = False,
        output_dir: Optional[str] = None,
        user_data_dir: Optional[str] = None,
        cdp_endpoint: Optional[str] = None,
        isolated: bool = False,
        storage_state: Optional[str] = None,
    ):
        self.browser_type = browser_type
        self.headless = headless
        self.enable_vision = enable_vision

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path.cwd() / "mcp_output"

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.user_data_dir = Path(user_data_dir) if user_data_dir else None
        self.cdp_endpoint = cdp_endpoint
        self.isolated = isolated
        self.storage_state = storage_state

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            browser_type=os.getenv("MCP_BROWSER_TYPE", "chromium"),
            headless=os.getenv("MCP_HEADLESS", "false").lower() == "true",
            enable_vision=os.getenv("MCP_ENABLE_VISION", "false").lower() == "true",
            output_dir=os.getenv("MCP_OUTPUT_DIR"),
            user_data_dir=os.getenv("MCP_USER_DATA_DIR"),
            cdp_endpoint=os.getenv("MCP_CDP_ENDPOINT"),
            isolated=os.getenv("MCP_ISOLATED", "false").lower() == "true",
            storage_state=os.getenv("MCP_STORAGE_STATE"),
        )

    def __str__(self) -> str:
        return (
            f"Settings(browser={self.browser_type}, headless={self.headless}, "
            f"vision={self.enable_vision}, isolated={self.isolated}, "
            f"storage_state={self.storage_state}, output_dir={self.output_dir})"
        )


@dataclass
class LaunchOptions:

    channel: Optional[str] = None
    executable_path: Optional[str] = None
    headless: Optional[bool] = None
    chromium_sandbox: Optional[bool] = None
    proxy: Optional[Dict[str, Any]] = None
    traces_dir: Optional[str] = None
    assistant_mode: bool = True


@dataclass
class ContextOptions:

    viewport: Optional[Dict[str, int]] = None
    storage_state: Optional[str] = None
    user_agent: Optional[str] = None
    ignore_https_errors: Optional[bool] = None
    service_workers: Optional[Literal["allow", "block"]] = None


@dataclass
class BrowserConfig:

    browser_agent: Optional[str] = None
    browser_name: Literal["chromium", "firefox", "webkit"] = "chromium"
    isolated: bool = False
    user_data_dir: Optional[str] = None
    launch_options: LaunchOptions = field(default_factory=LaunchOptions)
    context_options: ContextOptions = field(default_factory=ContextOptions)
    cdp_endpoint: Optional[str] = None
    remote_endpoint: Optional[str] = None


@dataclass
class ServerConfig:

    port: Optional[int] = None
    host: str = "localhost"


@dataclass
class NetworkConfig:

    allowed_origins: Optional[List[str]] = None
    blocked_origins: Optional[List[str]] = None


@dataclass
class CLIOptions:

    allowed_origins: Optional[List[str]] = None
    blocked_origins: Optional[List[str]] = None
    block_service_workers: bool = False
    browser: Optional[str] = None
    browser_agent: Optional[str] = None
    caps: Optional[str] = None
    cdp_endpoint: Optional[str] = None
    config: Optional[str] = None
    device: Optional[str] = None
    executable_path: Optional[str] = None
    headless: Optional[bool] = None
    host: Optional[str] = None
    ignore_https_errors: bool = False
    isolated: bool = False
    image_responses: Literal["allow", "omit", "auto"] = "auto"
    sandbox: bool = True
    output_dir: Optional[str] = None
    port: Optional[int] = None
    proxy_bypass: Optional[str] = None
    proxy_server: Optional[str] = None
    save_trace: bool = False
    storage_state: Optional[str] = None
    user_agent: Optional[str] = None
    user_data_dir: Optional[str] = None
    viewport_size: Optional[str] = None
    vision: bool = False
    extension: bool = False


@dataclass
class Config:

    browser: Optional[BrowserConfig] = None
    server: Optional[ServerConfig] = None
    capabilities: Optional[List[str]] = None
    vision: bool = False
    save_trace: bool = False
    output_dir: Optional[str] = None
    network: Optional[NetworkConfig] = None
    image_responses: Literal["allow", "omit", "auto"] = "auto"
    extension: bool = False


@dataclass
class FullConfig(Config):

    browser: BrowserConfig = field(default_factory=BrowserConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    output_dir: str = ""

    def __post_init__(self):
        if not self.output_dir:
            timestamp = datetime.now().isoformat().replace(":", "-").replace(".", "-")
            self.output_dir = str(
                Path(tempfile.gettempdir()) / "mcp-automation-output" / timestamp
            )


def sanitize_for_file_path(name: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "_")
    return name


def get_default_config() -> FullConfig:
    timestamp = datetime.now().isoformat().replace(":", "-").replace(".", "-")
    output_dir = str(
        Path(tempfile.gettempdir())
        / "mcp-automation-output"
        / sanitize_for_file_path(timestamp)
    )

    return FullConfig(
        browser=BrowserConfig(
            browser_name="chromium",
            launch_options=LaunchOptions(
                channel="chrome",
                headless=os.name == "posix" and not os.environ.get("DISPLAY"),
                chromium_sandbox=True,
            ),
            context_options=ContextOptions(
                viewport=None,
            ),
        ),
        network=NetworkConfig(
            allowed_origins=None,
            blocked_origins=None,
        ),
        server=ServerConfig(),
        output_dir=output_dir,
    )


async def resolve_config(config: Config) -> FullConfig:
    return merge_config(get_default_config(), config)


async def resolve_cli_config(cli_options: CLIOptions) -> FullConfig:
    config_in_file = await load_config(cli_options.config)
    cli_overrides = await config_from_cli_options(cli_options)
    result = merge_config(
        merge_config(get_default_config(), config_in_file), cli_overrides
    )

    if result.save_trace and result.browser.launch_options:
        result.browser.launch_options.traces_dir = str(
            Path(result.output_dir) / "traces"
        )

    return result


def validate_config(config: Config):
    if config.extension:
        if config.browser and config.browser.browser_name != "chromium":
            raise ValueError("Extension mode is only supported for Chromium browsers.")


async def config_from_cli_options(cli_options: CLIOptions) -> Config:
    browser_name: Optional[Literal["chromium", "firefox", "webkit"]] = None
    channel: Optional[str] = None

    if cli_options.browser:
        browser_lower = cli_options.browser.lower()
        if browser_lower in [
            "chrome",
            "chrome-beta",
            "chrome-canary",
            "chrome-dev",
            "chromium",
            "msedge",
            "msedge-beta",
            "msedge-canary",
            "msedge-dev",
        ]:
            browser_name = "chromium"
            channel = cli_options.browser
        elif browser_lower == "firefox":
            browser_name = "firefox"
        elif browser_lower == "webkit":
            browser_name = "webkit"

    launch_options = LaunchOptions(
        channel=channel,
        executable_path=cli_options.executable_path,
        headless=cli_options.headless,
    )

    if not cli_options.sandbox:
        launch_options.chromium_sandbox = False

    if cli_options.proxy_server:
        launch_options.proxy = {"server": cli_options.proxy_server}
        if cli_options.proxy_bypass:
            launch_options.proxy["bypass"] = cli_options.proxy_bypass

    if cli_options.device and cli_options.cdp_endpoint:
        raise ValueError("Device emulation is not supported with cdpEndpoint.")
    if cli_options.device and cli_options.extension:
        raise ValueError("Device emulation is not supported with extension mode.")

    context_options = ContextOptions()

    if cli_options.storage_state:
        context_options.storage_state = cli_options.storage_state

    if cli_options.user_agent:
        context_options.user_agent = cli_options.user_agent

    if cli_options.viewport_size:
        try:
            width_str, height_str = cli_options.viewport_size.split(",")
            width, height = int(width_str.strip()), int(height_str.strip())
            context_options.viewport = {"width": width, "height": height}
        except (ValueError, IndexError):
            raise ValueError(
                'Invalid viewport size format: use "width,height", for example --viewport-size="800,600"'
            )

    if cli_options.ignore_https_errors:
        context_options.ignore_https_errors = True

    if cli_options.block_service_workers:
        context_options.service_workers = "block"

    browser_config = BrowserConfig(
        browser_agent=cli_options.browser_agent or os.environ.get("PW_BROWSER_AGENT"),
        browser_name=browser_name or "chromium",
        isolated=cli_options.isolated,
        user_data_dir=cli_options.user_data_dir,
        launch_options=launch_options,
        context_options=context_options,
        cdp_endpoint=cli_options.cdp_endpoint,
    )

    server_config = ServerConfig(
        port=cli_options.port,
        host=cli_options.host or "localhost",
    )

    network_config = NetworkConfig(
        allowed_origins=cli_options.allowed_origins,
        blocked_origins=cli_options.blocked_origins,
    )

    capabilities = None
    if cli_options.caps:
        capabilities = [cap.strip() for cap in cli_options.caps.split(",")]

    return Config(
        browser=browser_config,
        server=server_config,
        capabilities=capabilities,
        vision=cli_options.vision,
        extension=cli_options.extension,
        network=network_config,
        save_trace=cli_options.save_trace,
        output_dir=cli_options.output_dir,
        image_responses=cli_options.image_responses,
    )


async def load_config(config_file: Optional[str]) -> Config:
    if not config_file:
        return Config()

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return dict_to_config(data)
    except Exception as error:
        raise ValueError(f"Failed to load config file: {config_file}, {error}")


async def output_file(config: FullConfig, name: str) -> str:
    os.makedirs(config.output_dir, exist_ok=True)
    file_name = sanitize_for_file_path(name)
    return str(Path(config.output_dir) / file_name)


def pick_defined(obj: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not obj:
        return {}
    return {k: v for k, v in obj.items() if v is not None}


def merge_config(base: FullConfig, overrides: Config) -> FullConfig:
    base_dict = asdict(base)
    overrides_dict = asdict(overrides) if overrides else {}

    browser_config = {
        **pick_defined(base_dict.get("browser", {})),
        **pick_defined(overrides_dict.get("browser", {})),
    }

    overrides_browser = overrides_dict.get("browser") or {}
    base_browser = base_dict.get("browser") or {}

    browser_config["browser_name"] = (
        overrides_browser.get("browser_name")
        or base_browser.get("browser_name")
        or "chromium"
    )
    browser_config["isolated"] = (
        overrides_browser.get("isolated") or base_browser.get("isolated") or False
    )

    base_launch = base_browser.get("launch_options") or {}
    overrides_launch = overrides_browser.get("launch_options") or {}

    launch_options = {
        **pick_defined(base_launch),
        **pick_defined(overrides_launch),
        "assistant_mode": True,
    }

    if browser_config["browser_name"] != "chromium" and "channel" in launch_options:
        del launch_options["channel"]

    browser_config["launch_options"] = launch_options

    base_context = base_browser.get("context_options") or {}
    overrides_context = overrides_browser.get("context_options") or {}

    browser_config["context_options"] = {
        **pick_defined(base_context),
        **pick_defined(overrides_context),
    }

    result_dict = {
        **pick_defined(base_dict),
        **pick_defined(overrides_dict),
        "browser": browser_config,
        "network": {
            **pick_defined(base_dict.get("network", {})),
            **pick_defined(overrides_dict.get("network", {})),
        },
        "server": {
            **pick_defined(base_dict.get("server", {})),
            **pick_defined(overrides_dict.get("server", {})),
        },
    }

    return dict_to_full_config(result_dict)


def dict_to_config(data: Dict[str, Any]) -> Config:
    browser_data = data.get("browser", {})
    browser_config = None
    if browser_data:
        launch_options = LaunchOptions(**browser_data.get("launch_options", {}))
        context_options = ContextOptions(**browser_data.get("context_options", {}))
        browser_config = BrowserConfig(
            **{
                k: v
                for k, v in browser_data.items()
                if k not in ["launch_options", "context_options"]
            },
            launch_options=launch_options,
            context_options=context_options,
        )

    server_data = data.get("server", {})
    server_config = ServerConfig(**server_data) if server_data else None

    network_data = data.get("network", {})
    network_config = NetworkConfig(**network_data) if network_data else None

    return Config(
        browser=browser_config,
        server=server_config,
        network=network_config,
        **{k: v for k, v in data.items() if k not in ["browser", "server", "network"]},
    )


def dict_to_full_config(data: Dict[str, Any]) -> FullConfig:
    browser_data = data.get("browser", {})
    launch_options = LaunchOptions(**browser_data.get("launch_options", {}))
    context_options = ContextOptions(**browser_data.get("context_options", {}))
    browser_config = BrowserConfig(
        **{
            k: v
            for k, v in browser_data.items()
            if k not in ["launch_options", "context_options"]
        },
        launch_options=launch_options,
        context_options=context_options,
    )

    server_data = data.get("server", {})
    server_config = ServerConfig(**server_data)

    network_data = data.get("network", {})
    network_config = NetworkConfig(**network_data)

    return FullConfig(
        browser=browser_config,
        server=server_config,
        network=network_config,
        **{k: v for k, v in data.items() if k not in ["browser", "server", "network"]},
    )


def config_to_settings(config: FullConfig) -> Settings:
    return Settings(
        browser_type=config.browser.browser_name,
        headless=config.browser.launch_options.headless or False,
        enable_vision=config.vision,
        output_dir=config.output_dir,
        user_data_dir=config.browser.user_data_dir,
        cdp_endpoint=config.browser.cdp_endpoint,
        isolated=config.browser.isolated,
        storage_state=config.browser.context_options.storage_state,
    )


def settings_to_config(settings: Settings) -> FullConfig:
    browser_config = BrowserConfig(
        browser_name=settings.browser_type,
        isolated=settings.isolated,
        user_data_dir=settings.user_data_dir,
        cdp_endpoint=settings.cdp_endpoint,
        launch_options=LaunchOptions(
            headless=settings.headless,
        ),
        context_options=ContextOptions(
            storage_state=settings.storage_state,
        ),
    )

    return FullConfig(
        browser=browser_config,
        vision=settings.enable_vision,
        output_dir=str(settings.output_dir),
    )
