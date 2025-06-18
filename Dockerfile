FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install playwright==1.52.0 
ENV PLAYWRIGHT_BROWSERS_PATH=/app/playwright-browsers
RUN playwright install --with-deps

FROM python:3.11-slim-bookworm AS production

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    curl wget gnupg ca-certificates \
    libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxcb1 libxkbcommon0 libx11-6 \
    libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2 gcc unixodbc unixodbc-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /var/cache/apt/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/playwright-browsers /app/playwright-browsers

ENV PLAYWRIGHT_BROWSERS_PATH=/app/playwright-browsers

COPY __init__.py .
COPY context.py .
COPY main.py .
COPY server.py .
COPY config/ ./config/
COPY core/ ./core/
COPY tools/ ./tools/
COPY transports/ ./transports/

COPY docker-config.json ./config/docker-default.json

RUN mkdir -p /app/output && \
    chmod 755 /app/output

RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser && \
    chown -R appuser:appuser /app

USER appuser

ENV MCP_BROWSER_TYPE=chromium
ENV MCP_HEADLESS=true
ENV MCP_OUTPUT_DIR=/app/output
ENV MCP_ISOLATED=true

EXPOSE 5000
EXPOSE 8080

CMD ["python", "main.py", "--config", "config/docker-default.json", "--transport", "sse", "--host", "0.0.0.0", "--port", "5000", "--headless", "--isolated"]
