from playwright.sync_api import sync_playwright
from pathlib import Path
import json
import os

script_dir = Path(__file__).parent
keys_dir = script_dir / "keys"
storage_file = str(keys_dir / "storage_state.json")
os.makedirs(keys_dir, exist_ok=True)


def load_existing_storage_state(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except:
            return None
    return None


def merge_storage_states(existing_state, new_state):
    if not existing_state:
        return new_state

    existing_cookies = existing_state.get("cookies", [])
    new_cookies = new_state.get("cookies", [])

    merged_cookies = []
    existing_cookie_keys = set()

    for cookie in existing_cookies:
        key = f"{cookie.get('domain', '')}:{cookie.get('name', '')}"
        existing_cookie_keys.add(key)
        merged_cookies.append(cookie)

    for cookie in new_cookies:
        key = f"{cookie.get('domain', '')}:{cookie.get('name', '')}"
        if key not in existing_cookie_keys:
            merged_cookies.append(cookie)

    existing_origins = existing_state.get("origins", [])
    new_origins = new_state.get("origins", [])

    merged_origins = []
    existing_origin_urls = set()

    for origin in existing_origins:
        origin_url = origin.get("origin", "")
        existing_origin_urls.add(origin_url)
        merged_origins.append(origin)

    for origin in new_origins:
        origin_url = origin.get("origin", "")
        if origin_url not in existing_origin_urls:
            merged_origins.append(origin)
        else:
            for existing_origin in merged_origins:
                if existing_origin.get("origin") == origin_url:
                    existing_local = existing_origin.get("localStorage", [])
                    new_local = origin.get("localStorage", [])
                    existing_origin["localStorage"] = existing_local + new_local

                    existing_session = existing_origin.get("sessionStorage", [])
                    new_session = origin.get("sessionStorage", [])
                    existing_origin["sessionStorage"] = existing_session + new_session
                    break

    return {"cookies": merged_cookies, "origins": merged_origins}


def save_storage_state(url, storage_file):
    existing_state = load_existing_storage_state(storage_file)

    if existing_state:
        print(
            f"📂 Found existing storage state with {len(existing_state.get('cookies', []))} cookies"
        )
        print("🔄 Will merge with new authentication data")
    else:
        print("📄 Creating new storage state file")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        if existing_state:
            context = browser.new_context(storage_state=existing_state)
        else:
            context = browser.new_context()

        page = context.new_page()

        page.goto(url)

        print(f"🌐 Navigated to: {url}")
        print("=" * 50)
        print("✅ Authentication Instructions:")
        print("   1. Login to the current site")
        print("   2. Open new tabs (Ctrl+T) for other sites you need")
        print("   3. Login to each site in separate tabs")
        print("   4. Keep all tabs open when done")
        print("=" * 50)

        input(">>> Press ENTER when you've completed all authentications...")

        new_state = context.storage_state()

        final_state = merge_storage_states(existing_state, new_state)

        with open(storage_file, "w") as f:
            json.dump(final_state, f, indent=2)

        print(f"✅ Storage state saved!")
        print(
            f"📊 Final state: {len(final_state.get('cookies', []))} cookies, {len(final_state.get('origins', []))} origins"
        )
        print(f"💾 Saved to: {storage_file}")

        browser.close()


if __name__ == "__main__":
    print("🔐 MCP Storage State Generator")
    print("=" * 40)

    default_url = "https://nexdev.net/"
    user_url = input(
        f"Enter URL to start authentication (default: {default_url}): "
    ).strip()

    if not user_url:
        user_url = default_url

    if not user_url.startswith(("http://", "https://")):
        user_url = "https://" + user_url

    save_storage_state(user_url, storage_file)
