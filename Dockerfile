FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    zlib1g-dev \
    libjpeg62-turbo-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev 2>/dev/null || uv sync --no-dev

COPY . .

RUN mkdir -p storage/documents && chmod +x start.sh

EXPOSE 8000

CMD ["bash", "start.sh"]
