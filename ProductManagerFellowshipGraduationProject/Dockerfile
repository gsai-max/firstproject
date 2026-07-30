# Use official lightweight Python 3.12 image
FROM python:3.12-slim

# Prevent Python from writing pyc files to disk and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and pre-computed datasets
COPY . .

# Expose FastAPI backend port
EXPOSE 8000

# Default command to run FastAPI backend with Uvicorn (evaluates dynamic $PORT on Render)
CMD ["sh", "-c", "uvicorn src.app.api_server:app --host 0.0.0.0 --port ${PORT:-8000}"]
