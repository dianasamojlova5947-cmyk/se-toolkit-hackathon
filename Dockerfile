FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY config.py .
COPY bot.py .
COPY handlers/ ./handlers/
COPY keyboards/ ./keyboards/
COPY services/ ./services/
COPY utils/ ./utils/

# Create necessary directories
RUN mkdir -p logs data

# Copy initial menu data (will be overridden by volume if mounted)
COPY menu.json ./data/menu.json

# Run the bot
CMD ["python", "bot.py"]