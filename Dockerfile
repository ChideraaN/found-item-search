FROM python:3.12

# uv is the package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Keep the virtual environment outside /app so the dev volume mount
# (.:/app in docker-compose.yml) doesn't hide it
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install dependencies first so Docker can cache this step
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .

EXPOSE 8000

CMD ["uvicorn", "found_item_search.server:app", "--host", "0.0.0.0", "--port", "8000"]
