FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install playwright==1.52.0 
ENV PLAYWRIGHT_BROWSERS_PATH=/app/playwright-browsers
RUN playwright install --with-deps

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget gnupg ca-certificates \
    libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxcb1 libxkbcommon0 libx11-6 \
    libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2 gcc unixodbc unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/playwright-browsers /app/playwright-browsers
ENV PLAYWRIGHT_BROWSERS_PATH=/app/playwright-browsers

COPY server.py .
COPY mcp_tools ./mcp_tools

RUN mkdir -p /app/logs && chmod 777 /app/logs

RUN adduser --disabled-password \
  --home /app \
  --gecos '' pythonuser && chown -R pythonuser /app && chown -R pythonuser /app/logs
USER pythonuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "5000"]
