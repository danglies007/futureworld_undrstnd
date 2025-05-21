FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "src/scan_sources/main.py"]
