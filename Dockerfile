FROM astral/uv:python3.13-alpine

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN uv pip install --system --index-url https://mirrors.aliyun.com/pypi/simple/ -e .

EXPOSE 8000

CMD ["python", "-m", "akshare_mcp", "8000", "http"]
