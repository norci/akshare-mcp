FROM astral/uv:alpine

WORKDIR /app

ENV PIP_INDEX_URL="https://mirrors.aliyun.com/pypi/simple/"
ENV PIP_MAX_WORKERS=10
ENV UV_CONCURRENT_DOWNLOADS=8
ENV UV_CONCURRENT_INSTALLS=8
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN uv pip install --system --index-url https://mirrors.aliyun.com/pypi/simple/ -e .

EXPOSE 8000

CMD ["python", "-m", "akshare_mcp"]
