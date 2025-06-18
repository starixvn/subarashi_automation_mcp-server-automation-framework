import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from config.settings import (
    Config,
    Settings,
    get_default_config,
    config_to_settings,
    BrowserConfig,
    ServerConfig,
    NetworkConfig,
)


def test_default_config():
    config = get_default_config()

    assert config.browser.browser_name == "chromium"
    assert config.browser.launch_options.headless is not None
    assert config.server.host == "localhost"
    assert config.output_dir is not None


def test_config_to_settings():
    config = Config(
        browser=BrowserConfig(browser_name="firefox"),
        server=ServerConfig(host="0.0.0.0", port=8080),
        capabilities=["core", "vision"],
    )

    full_config = get_default_config()
    if config.browser:
        full_config.browser.browser_name = config.browser.browser_name
    if config.server:
        if config.server.host:
            full_config.server.host = config.server.host
        if config.server.port:
            full_config.server.port = config.server.port
    if config.capabilities:
        full_config.capabilities = config.capabilities

    settings = config_to_settings(full_config)

    assert isinstance(settings, Settings)
    assert settings.browser_type == "firefox"


def test_config_validation():
    config = Config(
        browser=BrowserConfig(browser_name="chromium"), capabilities=["core"]
    )
    assert config.browser.browser_name == "chromium"


def test_config_loading_from_dict():
    config_dict = {
        "browser": {"browser_name": "firefox", "launch_options": {"headless": False}},
        "server": {"host": "127.0.0.1", "port": 9000},
        "capabilities": ["core", "vision"],
    }

    config = Config(
        browser=BrowserConfig(browser_name=config_dict["browser"]["browser_name"]),
        server=ServerConfig(
            host=config_dict["server"]["host"], port=config_dict["server"]["port"]
        ),
        capabilities=config_dict["capabilities"],
    )

    assert config.browser.browser_name == "firefox"
    assert config.server.host == "127.0.0.1"
    assert config.server.port == 9000
    assert config.capabilities == ["core", "vision"]


def test_config_merging():
    base_config = get_default_config()
    override_config = Config(
        browser=BrowserConfig(browser_name="firefox"), capabilities=["vision"]
    )

    merged_config = Config(
        browser=BrowserConfig(
            browser_name=override_config.browser.browser_name,
        ),
        server=base_config.server,
        network=base_config.network,
        capabilities=override_config.capabilities,
    )

    assert merged_config.browser.browser_name == "firefox"
    assert merged_config.capabilities == ["vision"]  # from override


def test_browser_name_validation():
    valid_browsers = ["chromium", "firefox", "webkit"]

    for browser in valid_browsers:
        config = Config(browser=BrowserConfig(browser_name=browser))
        assert config.browser.browser_name == browser


def test_capability_validation():
    valid_capabilities = [
        ["core"],
        ["vision"],
        ["core", "vision"],
        ["vision", "core"],
    ]

    for caps in valid_capabilities:
        config = Config(capabilities=caps)
        assert set(config.capabilities) == set(caps)


def test_config_to_settings_conversion():
    full_config = get_default_config()
    full_config.browser.browser_name = "firefox"
    full_config.server.host = "0.0.0.0"
    full_config.server.port = 8080
    full_config.capabilities = ["core", "vision"]

    settings = config_to_settings(full_config)

    assert settings.browser_type == "firefox"


def test_settings_to_config_conversion():
    settings = Settings(browser_type="webkit", headless=True, output_dir="/tmp/test")

    config = Config(
        browser=BrowserConfig(
            browser_name=settings.browser_type,
        ),
        server=ServerConfig(host="localhost", port=3000),
        capabilities=["core"],
    )

    assert config.browser.browser_name == "webkit"
    assert config.server.host == "localhost"
    assert config.server.port == 3000
    assert config.capabilities == ["core"]
