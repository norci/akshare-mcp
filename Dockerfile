FROM astral/uv:python3.13-alpine

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN uv pip install --system --index-url https://mirrors.aliyun.com/pypi/simple/ -e .

# No port needed for stdio transport
CMD ["python", "-m", "akshare_mcp"]
