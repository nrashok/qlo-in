FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 10000

# Set environment variables
ENV PORT=10000
ENV DATA_FILE=/data/urls.json

# Run the application
CMD ["python", "app.py"]
