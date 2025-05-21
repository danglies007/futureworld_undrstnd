#!/bin/bash
# Script to deploy the CrewAI application to AWS Fargate

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
AWS_REGION="af-south-1"  # South Africa (Cape Town) region
ECR_REPOSITORY_NAME="undrstnd-crew-ai"
ECS_CLUSTER_NAME="undrstnd-cluster"
ECS_SERVICE_NAME="undrstnd-crew-service"
ECS_TASK_FAMILY="undrstnd-task"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY_NAME}"

# Validate requirements before deployment
validate_requirements

# Load environment variables from .env.cloud
if [ -f .env.cloud ]; then
  echo "Loading environment variables from .env.cloud"
  export $(cat .env.cloud | grep -v '^#' | xargs)
else
  echo "Error: .env.cloud file not found. Please create it first."
  exit 1
fi

# Create ECR repository if it doesn't exist
echo "Checking if ECR repository exists..."
if ! aws ecr describe-repositories --repository-names ${ECR_REPOSITORY_NAME} --region ${AWS_REGION} &> /dev/null; then
  echo "Creating ECR repository..."
  aws ecr create-repository --repository-name ${ECR_REPOSITORY_NAME} --region ${AWS_REGION}
fi

# Authenticate Docker to ECR
echo "Authenticating Docker to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY_URI}

# Build the Docker image
echo "Building Docker image..."
docker build -t ${ECR_REPOSITORY_NAME}:latest .

# Tag the image for ECR
echo "Tagging image for ECR..."
docker tag ${ECR_REPOSITORY_NAME}:latest ${ECR_REPOSITORY_URI}:latest

# Push the image to ECR
echo "Pushing image to ECR..."
docker push ${ECR_REPOSITORY_URI}:latest

# Create ECS cluster if it doesn't exist
echo "Checking if ECS cluster exists..."
if ! aws ecs describe-clusters --clusters ${ECS_CLUSTER_NAME} --region ${AWS_REGION} --query "clusters[?clusterName=='${ECS_CLUSTER_NAME}']" --output text | grep -q ${ECS_CLUSTER_NAME}; then
  echo "Creating ECS cluster..."
  aws ecs create-cluster --cluster-name ${ECS_CLUSTER_NAME} --region ${AWS_REGION}
fi

# Create task definition JSON file with environment variables
echo "Creating task definition..."
cat > task-definition.json << EOF
{
  "family": "${ECS_TASK_FAMILY}",
  "networkMode": "awsvpc",
  "executionRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "${ECR_REPOSITORY_NAME}",
      "image": "${ECR_REPOSITORY_URI}:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8080,
          "hostPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "OPENAI_API_KEY", "value": "${OPENAI_API_KEY}"},
        {"name": "SERPER_API_KEY", "value": "${SERPER_API_KEY}"},
        {"name": "AGENTOPS_API_KEY", "value": "${AGENTOPS_API_KEY}"},
        {"name": "BRAVE_API_KEY", "value": "${BRAVE_API_KEY}"},
        {"name": "EXA_API_KEY", "value": "${EXA_API_KEY}"},
        {"name": "FIRECRAWL_API_KEY", "value": "${FIRECRAWL_API_KEY}"},
        {"name": "SCRAPFLY_API_KEY", "value": "${SCRAPFLY_API_KEY}"},
        {"name": "PERPLEXITYAI_API_KEY", "value": "${PERPLEXITYAI_API_KEY}"},
        {"name": "PERPLEXITY_API_KEY", "value": "${PERPLEXITY_API_KEY}"},
        {"name": "GEMINI_API_KEY", "value": "${GEMINI_API_KEY}"},
        {"name": "ANTHROPIC_API_KEY", "value": "${ANTHROPIC_API_KEY}"},
        {"name": "OPENROUTER_API_KEY", "value": "${OPENROUTER_API_KEY}"},
        {"name": "HF_API_KEY", "value": "${HF_API_KEY}"},
        {"name": "HF_TOKEN", "value": "${HF_TOKEN}"},
        {"name": "CEREBRAS_API_KEY", "value": "${CEREBRAS_API_KEY}"},
        {"name": "LITELLM_DEBUG", "value": "true"},
        {"name": "PYTHONUNBUFFERED", "value": "1"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/${ECS_TASK_FAMILY}",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "memory": 4096,
      "cpu": 1024
    }
  ],
  "requiresCompatibilities": [
    "FARGATE"
  ],
  "cpu": "1024",
  "memory": "4096"
}
EOF

# Register the task definition
echo "Registering task definition..."
TASK_DEFINITION_ARN=$(aws ecs register-task-definition --cli-input-json file://task-definition.json --region ${AWS_REGION} --query 'taskDefinition.taskDefinitionArn' --output text)

# Create CloudWatch Logs group if it doesn't exist
echo "Creating CloudWatch Logs group..."
aws logs create-log-group --log-group-name "/ecs/${ECS_TASK_FAMILY}" --region ${AWS_REGION} || true

# Check if service exists
echo "Checking if ECS service exists..."
SERVICE_EXISTS=$(aws ecs list-services --cluster ${ECS_CLUSTER_NAME} --region ${AWS_REGION} --query "serviceArns[?contains(@,'${ECS_SERVICE_NAME}')]" --output text)

if [ -z "$SERVICE_EXISTS" ]; then
  # Create service
  echo "Creating ECS service..."
  aws ecs create-service \
    --cluster ${ECS_CLUSTER_NAME} \
    --service-name ${ECS_SERVICE_NAME} \
    --task-definition ${TASK_DEFINITION_ARN} \
    --desired-count 1 \
    --launch-type FARGATE \
    --platform-version LATEST \
    --network-configuration "awsvpcConfiguration={subnets=[$(aws ec2 describe-subnets --region ${AWS_REGION} --query 'Subnets[0].SubnetId' --output text)],securityGroups=[$(aws ec2 describe-security-groups --region ${AWS_REGION} --query 'SecurityGroups[0].GroupId' --output text)],assignPublicIp=ENABLED}" \
    --region ${AWS_REGION}
else
  # Update service
  echo "Updating ECS service..."
  aws ecs update-service \
    --cluster ${ECS_CLUSTER_NAME} \
    --service ${ECS_SERVICE_NAME} \
    --task-definition ${TASK_DEFINITION_ARN} \
    --region ${AWS_REGION}
fi

echo "Deployment to AWS Fargate complete!"
echo "To view your service status, run:"
echo "aws ecs describe-services --cluster ${ECS_CLUSTER_NAME} --services ${ECS_SERVICE_NAME} --region ${AWS_REGION}"
echo "To view logs, visit the CloudWatch console or run:"
echo "aws logs get-log-events --log-group-name /ecs/${ECS_TASK_FAMILY} --log-stream-name \$(aws logs describe-log-streams --log-group-name /ecs/${ECS_TASK_FAMILY} --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text) --region ${AWS_REGION}"

# Clean up temporary files
rm task-definition.json
