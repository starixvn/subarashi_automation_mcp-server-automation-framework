FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

COPY requirements.txt pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --upgrade pip setuptools wheel
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

ENV PLAYWRIGHT_BROWSERS_PATH=/app/playwright-browsers
RUN --mount=type=cache,target=/tmp/playwright \
    playwright install --with-deps chromium
RUN playwright install-deps

FROM python:3.11-slim-bookworm AS base

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    curl wget gnupg ca-certificates \
    libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxcb1 libxkbcommon0 libx11-6 \
    libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2 libxss1 \
    gcc procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /var/cache/apt/*

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc unixodbc-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /var/cache/apt/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/playwright-browsers /app/playwright-browsers

ENV PLAYWRIGHT_BROWSERS_PATH=/app/playwright-browsers
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

COPY __init__.py ./
COPY pyproject.toml pytest.ini ./

COPY config/ ./config/
COPY core/ ./core/
COPY prompts/ ./prompts/
COPY resources/ ./resources/
COPY services/ ./services/
COPY tools/ ./tools/
COPY transports/ ./transports/

COPY context.py server.py main.py ./

COPY docker-config.json ./config/docker-default.json

RUN mkdir -p /app/output /app/mcp_output /app/logs && \
    chmod 755 /app/output /app/mcp_output /app/logs

ENV MCP_BROWSER_TYPE=chromium
ENV MCP_HEADLESS=true
ENV MCP_OUTPUT_DIR=/app/output
ENV MCP_ISOLATED=true
ENV MCP_NO_SANDBOX=true
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV TZ="Asia/Ho_Chi_Minh"

RUN adduser --disabled-password \
    --home /app \
    --gecos '' mcpuser && chown -R mcpuser /app && chown -R mcpuser /tmp
USER mcpuser

EXPOSE 5000

CMD ["python", "main.py", \
    "--config", "config/docker-default.json", \
    "--transport", "sse", \
    "--host", "0.0.0.0", \
    "--headless", \
    "--isolated", \
    "--no-sandbox", \
    "--port", "5000", \
    "--vision"]
