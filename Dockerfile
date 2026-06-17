FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    zlib1g-dev \
    libjpeg62-turbo-dev \
    libffi-dev \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p storage/documents && dos2unix start.sh && chmod +x start.sh

EXPOSE 8000

CMD ["bash", "start.sh"]
