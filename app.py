import streamlit as st
import requests
import uuid
import time
import subprocess
import sys

# Configure page
st.set_page_config(
    page_title="Gemini MCP Client", layout="wide", initial_sidebar_state="expanded"
)

# API endpoints
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if "client_id" not in st.session_state:
    st.session_state.client_id = str(uuid.uuid4())
    st.session_state.connected = False
    st.session_state.messages = []
    st.session_state.available_tools = []
    st.session_state.gemini_api_key = ""
    st.session_state.server_url = "http://localhost:8080/sse"
    st.session_state.playwright_checked = False

st.title("Gemini MCP Client")

# Sidebar with connection settings
with st.sidebar:
    st.header("Cài đặt kết nối")

    # Playwright setup guide
    with st.expander(
        "Hướng dẫn cài đặt Playwright (Bắt buộc)",
        expanded=not st.session_state.playwright_checked,
    ):
        st.markdown(
            """
        ### Cài đặt Playwright (Bắt buộc)
        
        Trước khi sử dụng ứng dụng, bạn cần cài đặt Playwright và các trình điều khiển web:
        
        1. Mở terminal hoặc command prompt
        2. Chạy lệnh sau:
        ```
        pip install playwright
        python -m playwright install --with-deps
        ```
        
        Lệnh này sẽ cài đặt Playwright và tất cả các trình duyệt cần thiết (Chromium, Firefox, WebKit).
        """
        )

    # Check Playwright installation
    if st.button("Kiểm tra cài đặt Playwright"):
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "from playwright.sync_api import sync_playwright; print('OK')",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            if "OK" in result.stdout:
                st.session_state.playwright_checked = True
                st.success("✅ Playwright đã được cài đặt thành công!")
            else:
                st.error("❌ Playwright chưa được cài đặt đúng cách.")
        except subprocess.CalledProcessError:
            st.error("❌ Playwright chưa được cài đặt.")
            st.info("Vui lòng cài đặt theo hướng dẫn.")
        except Exception as e:
            st.error(f"❌ Lỗi kiểm tra: {str(e)}")

    st.divider()

    # API key input
    api_key = st.text_input(
        "Gemini API Key",
        value=st.session_state.gemini_api_key,
        type="password",
        help="Nhập API key của Google Gemini",
    )

    # Server URL input
    server_url = st.text_input(
        "MCP Server URL",
        value=st.session_state.server_url,
        help="Nhập URL của MCP Server (ví dụ: http://localhost:8080/sse)",
    )

    # Save settings button
    if st.button("Lưu cài đặt"):
        st.session_state.gemini_api_key = api_key
        st.session_state.server_url = server_url
        st.success("✅ Đã lưu cài đặt!")

    # Connect button
    connect_disabled = not st.session_state.playwright_checked
    if connect_disabled:
        st.warning("Vui lòng kiểm tra cài đặt Playwright trước khi kết nối")

    if st.button("Kết nối", disabled=connect_disabled):
        if not api_key:
            st.error("Vui lòng nhập Gemini API Key")
        elif not server_url:
            st.error("Vui lòng nhập URL của server")
        else:
            with st.spinner("Đang kết nối..."):
                try:
                    # Gọi API để kết nối
                    response = requests.post(
                        f"{API_BASE_URL}/connect",
                        json={
                            "server_url": server_url,
                            "api_key": api_key,
                            "client_id": st.session_state.client_id,
                        },
                        timeout=30,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.connected = True
                        st.session_state.client_id = data["client_id"]
                        st.session_state.available_tools = data.get(
                            "available_tools", []
                        )
                        st.success("✅ Kết nối thành công!")
                    else:
                        st.error(
                            f"❌ Lỗi kết nối: {response.json().get('detail', 'Không rõ lỗi')}"
                        )

                except requests.RequestException as e:
                    st.error(f"❌ Lỗi kết nối API: {str(e)}")
                    st.info("Đảm bảo API server đang chạy tại " + API_BASE_URL)

# Main chat interface
st.divider()

# Show connection status and info
col1, col2 = st.columns([3, 1])
with col1:
    if st.session_state.connected:
        st.success(
            f"✅ Đã kết nối đến MCP Server - Client ID: {st.session_state.client_id[:8]}..."
        )
        if st.session_state.available_tools:
            with st.expander("Công cụ có sẵn"):
                st.write(", ".join(st.session_state.available_tools))
    else:
        st.warning("⚠️ Chưa kết nối đến MCP Server")
with col2:
    if st.button("Xóa lịch sử chat"):
        st.session_state.messages = []
        st.rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input (only enabled if connected)
user_input = st.chat_input("Nhập câu hỏi...", disabled=not st.session_state.connected)
if user_input and st.session_state.connected:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process query and display response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.info("Đang xử lý...")

        try:
            # Gọi API để xử lý query
            response = requests.post(
                f"{API_BASE_URL}/query",
                json={"query": user_input, "client_id": st.session_state.client_id},
                timeout=120,  # 2 phút timeout
            )

            if response.status_code == 200:
                result = response.json()["response"]
                message_placeholder.markdown(result)
                st.session_state.messages.append(
                    {"role": "assistant", "content": result}
                )
            else:
                error_message = response.json().get("detail", "Lỗi không xác định")
                message_placeholder.error(f"❌ Lỗi: {error_message}")
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"❌ Lỗi: {error_message}"}
                )

        except requests.RequestException as e:
            error_message = f"❌ Lỗi kết nối API: {str(e)}"
            message_placeholder.error(error_message)
            st.session_state.messages.append(
                {"role": "assistant", "content": error_message}
            )

# Add disconnect handler when Streamlit app stops
if st.session_state.connected:
    try:
        requests.delete(f"{API_BASE_URL}/disconnect/{st.session_state.client_id}")
    except:
        pass  # Ignore errors on page reload

# Footer
st.sidebar.divider()
st.sidebar.caption("Gemini MCP Client v1.0")
with st.sidebar.expander("Thông tin"):
    st.markdown(
        """
    ### Về MCP Client
    - Sử dụng Google Gemini 2.0 Flash
    - Kết nối với server thông qua SSE
    - Hỗ trợ các công cụ của MCP (tools)
    
    ### Vấn đề thường gặp
    - **Trình duyệt không mở**: Đảm bảo Playwright đã cài đặt đúng cách
    - **Timeout**: Thử lại với yêu cầu đơn giản hơn
    - **Lỗi kết nối**: Kiểm tra URL server và mạng
    """
    )
