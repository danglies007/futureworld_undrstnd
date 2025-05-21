#!/bin/bash
# Script to validate requirements.txt in a Docker container (similar to deployment environment)

# Exit on error
set -e

echo "🔍 Validating requirements.txt in Docker container..."

# Create a temporary Dockerfile for validation
cat > Dockerfile.validate << EOF
FROM python:3.10-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Try to install all requirements
RUN pip install --no-cache-dir -r requirements.txt

# Test importing key packages
CMD ["python", "-c", "import crewai; import litellm; import openai; import agentops; print('✅ All key imports successful')"]
EOF

# Build and run the validation container
echo "Building validation container..."
docker build -t requirements-validator -f Dockerfile.validate .

echo "Running validation container..."
docker run --rm requirements-validator

# Clean up
rm Dockerfile.validate

echo "✅ Docker validation complete! Your requirements.txt should work in the deployment environment."
