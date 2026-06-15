# Use official lightweight Python 3.11 image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set system-level environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system-level dependencies for compiling C/C++ packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code and data assets
COPY src/ ./src/
COPY data/ ./data/

# Expose the API server port
EXPOSE 8000

# Run the Uvicorn production server binding to the dynamic port injected by Railway
CMD ["sh", "-c", "uvicorn src.app.api_server:app --host 0.0.0.0 --port ${PORT:-8000}"]
