#!/bin/bash
# Script to deploy the CrewAI application to Google Cloud Run

# Exit on error
set -e

# Function to validate requirements
validate_requirements() {
  echo "🔍 Validating requirements.txt before deployment..."
  
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
  if ! docker run --rm requirements-validator; then
    echo "❌ Requirements validation failed! Please fix your requirements.txt before deploying."
    rm Dockerfile.validate
    exit 1
  fi

  # Clean up
  rm Dockerfile.validate
  echo "✅ Requirements validation successful!"
}

# Configuration
PROJECT_ID="futureworld-undrstnd"  # Replace with your GCP project ID
IMAGE_NAME="undrstnd-crew-ai"
REGION="us-central1"  # Choose your preferred region
SERVICE_NAME="undrstnd-crew-service"

# Validate requirements before deployment
validate_requirements

# Build the Docker image
echo "Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/$IMAGE_NAME .

# Push the image to Google Container Registry
echo "Pushing image to Google Container Registry..."
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --set-env-vars="PYTHONUNBUFFERED=1"

echo "Deployment complete! Your service is now running at:"
gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)'
