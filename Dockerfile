FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev

COPY . .

RUN mkdir -p storage/documents && chmod +x start.sh

EXPOSE 8000

CMD ["bash", "start.sh"]
