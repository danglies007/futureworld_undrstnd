# Cloud Deployment Guide for CrewAI Application

This guide explains how to deploy your CrewAI application to the cloud using Docker containers. This approach provides a consistent environment, scalability, and cost efficiency.

## Prerequisites

- Docker installed on your local machine
- A cloud provider account (Google Cloud, AWS, or Azure)
- API keys for all services used in your application

## Option 1: AWS Fargate in South Africa (Recommended)

AWS Fargate is a serverless compute engine for containers that works with Amazon ECS. The South Africa (Cape Town) region provides lower latency for African users.

### Setup Steps

1. **Install AWS CLI (globally, outside of any virtual environment)**

   **For Mac users (recommended):**
   ```bash
   # Install using Homebrew
   brew install awscli
   
   # Configure AWS credentials
   aws configure  # Enter your AWS credentials when prompted
   ```
   
   **Alternative installation methods:**
   ```bash
   # Exit any active virtual environments first if needed
   # deactivate  # If you're in a virtual environment
   
   # Install AWS CLI globally with pip
   pip install awscli --user
   
   # Or with UV
   uv pip install awscli --user
   ```
   
   > **Note**: Install AWS CLI globally since it's a deployment tool that should be available system-wide, not just within your project's environment. On Mac, the Homebrew installation is recommended as it handles updates and dependencies more cleanly.

2. **Set up Environment Variables**
   - Copy the `cloud.env.example` file to `.env.cloud`
   - Fill in all your API keys and configuration values
   ```bash
   cp cloud.env.example .env.cloud
   # Edit .env.cloud with your actual API keys
   ```

3. **Deploy the Application**
   ```bash
   ./deploy_to_aws_fargate.sh
   ```
   
   This script will:
   - Create an ECR repository if it doesn't exist
   - Build and push your Docker image
   - Create an ECS cluster in the South Africa region
   - Set up the task definition with your environment variables
   - Deploy the service with Fargate

4. **Monitor Your Application**
   - Use the AWS ECS Console to monitor your application
   - View CloudWatch logs for detailed application logs

## Option 2: Google Cloud Run

Google Cloud Run is a fully managed platform that automatically scales your containerized applications.

### Setup Steps

1. **Install Google Cloud SDK**
   - Download and install from: https://cloud.google.com/sdk/docs/install

2. **Authenticate with Google Cloud**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Set up Environment Variables**
   - Copy the `cloud.env.example` file to `.env.cloud`
   - Fill in all your API keys and configuration values
   ```bash
   cp cloud.env.example .env.cloud
   # Edit .env.cloud with your actual API keys
   ```

4. **Update the Deployment Script**
   - Edit `deploy_to_cloud_run.sh` and update the `PROJECT_ID` variable with your Google Cloud project ID
   - Adjust other variables as needed (region, memory, CPU)

5. **Deploy the Application**
   ```bash
   ./deploy_to_cloud_run.sh
   ```

6. **Monitor Your Application**
   - Visit the Google Cloud Console to monitor your application
   - View logs and performance metrics

## AWS Fargate Deployment Details

The `deploy_to_aws_fargate.sh` script handles the entire deployment process, but here's what's happening behind the scenes:

### 1. ECR Repository Management

The script creates an Amazon Elastic Container Registry (ECR) repository to store your Docker images:

```bash
aws ecr create-repository --repository-name undrstnd-crew-ai --region af-south-1
```

### 2. Docker Image Build and Push

The script builds your Docker image and pushes it to ECR:

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region af-south-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.af-south-1.amazonaws.com

# Build and tag the image
docker build -t undrstnd-crew-ai .
docker tag undrstnd-crew-ai:latest YOUR_ACCOUNT_ID.dkr.ecr.af-south-1.amazonaws.com/undrstnd-crew-ai:latest

# Push the image
docker push YOUR_ACCOUNT_ID.dkr.ecr.af-south-1.amazonaws.com/undrstnd-crew-ai:latest
```

### 3. ECS Cluster and Task Definition

The script creates an ECS cluster and task definition with your environment variables:

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name undrstnd-cluster --region af-south-1

# Create task definition with environment variables from .env.cloud
aws ecs register-task-definition --cli-input-json file://task-definition.json --region af-south-1
```

### 4. Service Deployment

Finally, it creates or updates an ECS service using Fargate:

```bash
aws ecs create-service \
  --cluster undrstnd-cluster \
  --service-name undrstnd-crew-service \
  --task-definition YOUR_TASK_DEFINITION_ARN \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={...}" \
  --region af-south-1
```

### 5. Persistent Storage with S3

For persistent storage in AWS, you can use Amazon S3 buckets in the af-south-1 region:

```python
import boto3

def save_to_s3(bucket_name, file_path, s3_key):
    s3_client = boto3.client('s3', region_name='af-south-1')
    s3_client.upload_file(file_path, bucket_name, s3_key)
```

## Option 3: Google Cloud Run

## Option 3: Azure Container Instances

Azure Container Instances offers a simple way to run containers without managing servers.

### Setup Steps

1. **Install Azure CLI**
   ```bash
   curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
   az login
   ```

2. **Create a Resource Group**
   ```bash
   az group create --name undrstnd-crew-ai-group --location eastus
   ```

3. **Create an Azure Container Registry**
   ```bash
   az acr create --resource-group undrstnd-crew-ai-group --name undrstndcrewai --sku Basic
   az acr login --name undrstndcrewai
   ```

4. **Build and Push Docker Image**
   ```bash
   docker build -t undrstndcrewai.azurecr.io/undrstnd-crew-ai:latest .
   docker push undrstndcrewai.azurecr.io/undrstnd-crew-ai:latest
   ```

5. **Deploy to Azure Container Instances**
   ```bash
   az container create \
     --resource-group undrstnd-crew-ai-group \
     --name undrstnd-crew-ai \
     --image undrstndcrewai.azurecr.io/undrstnd-crew-ai:latest \
     --registry-login-server undrstndcrewai.azurecr.io \
     --registry-username $(az acr credential show --name undrstndcrewai --query username --output tsv) \
     --registry-password $(az acr credential show --name undrstndcrewai --query passwords[0].value --output tsv) \
     --dns-name-label undrstnd-crew-ai \
     --ports 80 \
     --cpu 2 \
     --memory 4 \
     --environment-variables $(cat .env.cloud | tr '\n' ' ')
   ```

## Persistent Storage Considerations

Your CrewAI application generates output files. To persist these files across container restarts:

1. **AWS S3 in South Africa**:
   ```python
   # Example code to save to S3 in South Africa region
   import boto3
   
   def save_to_s3(bucket_name, file_path, s3_key):
       s3_client = boto3.client('s3', region_name='af-south-1')
       s3_client.upload_file(file_path, bucket_name, s3_key)
       return f"https://{bucket_name}.s3.af-south-1.amazonaws.com/{s3_key}"
   
   # Example usage in your CrewAI application
   def save_output_to_s3(output_data, filename):
       import json
       import os
       
       # Save locally first
       local_path = f"outputs/{filename}"
       os.makedirs(os.path.dirname(local_path), exist_ok=True)
       
       with open(local_path, 'w') as f:
           json.dump(output_data, f)
       
       # Upload to S3
       bucket_name = "undrstnd-outputs"
       s3_key = f"crew-outputs/{filename}"
       s3_url = save_to_s3(bucket_name, local_path, s3_key)
       
       return s3_url
   ```

2. **Google Cloud Storage**: Use Cloud Storage buckets
   ```python
   # Example code to save to Cloud Storage
   from google.cloud import storage
   
   def save_to_cloud_storage(bucket_name, source_file_name, destination_blob_name):
       storage_client = storage.Client()
       bucket = storage_client.bucket(bucket_name)
       blob = bucket.blob(destination_blob_name)
       blob.upload_from_filename(source_file_name)
   ```

3. **Azure**: Use Azure Blob Storage

## Monitoring and Logging

For all cloud providers, set up:

1. **Logging**: Direct application logs to the cloud provider's logging service
2. **Monitoring**: Set up alerts for errors or high resource usage
3. **Cost Management**: Set up budgets to avoid unexpected costs

## Managing Requirements with UV

The CrewAI application has complex dependencies. Using UV (Ultraviolet) instead of standard pip is recommended for more accurate dependency resolution and better deployment outcomes.

### Why UV is Preferred

UV offers significant advantages over standard pip:

1. **More accurate dependency resolution**: UV resolves complex dependency trees better than pip
2. **Faster installation**: UV can install packages in parallel
3. **Better conflict detection**: UV identifies and reports dependency conflicts more clearly
4. **Reproducible builds**: UV creates more consistent environments across systems

### Tools for Managing Requirements

Four tools are provided to help manage requirements:

#### 1. Direct UV Requirements Generator (Recommended)

The `get_actual_uv_requirements.sh` script:
- Gets requirements directly from your current UV environment
- Uses `uv pip list --format=freeze` to ensure accuracy
- Creates `requirements.uv.actual.txt` with your exact UV packages
- Checks for known conflicts automatically

This is the most accurate method and recommended for deployment:
```bash
./get_actual_uv_requirements.sh
```

After running, you can use the generated file for deployment:
```bash
cp requirements.uv.actual.txt requirements.txt
```

#### 2. Simple UV Requirements Generator

The `generate_uv_requirements.sh` script:
- Creates a clean virtual environment using UV
- Installs your current requirements
- Generates a fresh `requirements.uv.txt` file
- Shows differences between your current and UV-generated requirements

Run it with:
```bash
./generate_uv_requirements.sh
```

#### 3. Comprehensive Requirements Analyzer and Merger

The `update_requirements.py` script provides a more sophisticated solution:
- Uses your actual UV environment packages (same as `uv pip list`)
- Compares pip and UV requirements side-by-side
- Identifies packages only in pip, only in UV, and with version differences
- Highlights critical packages (CrewAI, LiteLLM, etc.)
- Creates a merged requirements file that takes the best from both
- Automatically detects dependency conflicts and suggests fixes

Run it to analyze without making changes:
```bash
./update_requirements.py
```

Or apply the changes directly:
```bash
./update_requirements.py --apply
```

#### 4. Dependency Conflict Fixer

The `fix_requirements.py` script specifically addresses known dependency conflicts:
- Fixes the conflict between embedchain and chromadb (embedchain requires chromadb<0.6.0)
- Creates a backup of your requirements file
- Generates a fixed requirements file with compatible versions
- Tests if the fixed requirements work correctly
- Gives you the option to apply the fix

Run it to fix dependency conflicts:
```bash
./fix_requirements.py
```

### Best Practices for Requirements Management

Follow these steps before deployment:

1. **Generate requirements directly from your UV environment** (recommended approach):
   ```bash
   ./get_actual_uv_requirements.sh
   cp requirements.uv.actual.txt requirements.txt
   ```
   This ensures your deployment uses the exact same dependencies as your local environment.

2. **Fix any dependency conflicts**:
   ```bash
   ./fix_requirements.py
   ```
   This will address known conflicts like the embedchain vs chromadb issue.

3. **Validate requirements**:
   ```bash
   ./validate_requirements.sh
   ```
   or
   ```bash
   ./validate_requirements_docker.sh
   ```

4. **Check for critical package versions**:
   Ensure these packages have correct versions:
   - crewai
   - litellm
   - openai
   - agentops
   - langchain
   - pydantic

5. **Use pinned versions** for critical dependencies

6. **Test locally before deployment** to catch any issues early

### Why Direct UV Requirements Are Preferred

There can be significant differences between:
- Standard `pip freeze` output
- Requirements generated in a temporary environment
- The actual packages in your UV environment (`uv pip list`)

Using `get_actual_uv_requirements.sh` ensures your deployment matches your development environment exactly, reducing the risk of "works on my machine" issues.

### Known Dependency Conflicts

#### embedchain vs chromadb

The most common conflict in this codebase is between embedchain and chromadb:

- **Issue**: `embedchain==0.1.125` requires `chromadb<0.6.0`, but the default is `chromadb==0.6.3`
- **Solution**: Downgrade chromadb to version 0.5.10
- **Fix Command**: `./fix_requirements.py`

This conflict will cause deployment to fail if not addressed, as UV will be unable to resolve the dependencies.

## Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables for all secrets**
3. **Set up IAM roles with minimal permissions**
4. **Enable audit logging**
5. **Regularly update dependencies**

## Troubleshooting

### AWS Fargate Troubleshooting

1. **Check ECS Service Status**:
   ```bash
   aws ecs describe-services --cluster undrstnd-cluster --services undrstnd-crew-service --region af-south-1
   ```

2. **View CloudWatch Logs**:
   ```bash
   # Get the latest log stream
   LOG_STREAM=$(aws logs describe-log-streams --log-group-name /ecs/undrstnd-task --order-by LastEventTime --descending --limit 1 --query 'logStreams[0].logStreamName' --output text --region af-south-1)
   
   # View logs
   aws logs get-log-events --log-group-name /ecs/undrstnd-task --log-stream-name $LOG_STREAM --region af-south-1
   ```

3. **Check Task Status**:
   ```bash
   # List running tasks
   TASK_ARN=$(aws ecs list-tasks --cluster undrstnd-cluster --region af-south-1 --query 'taskArns[0]' --output text)
   
   # Describe task
   aws ecs describe-tasks --cluster undrstnd-cluster --tasks $TASK_ARN --region af-south-1
   ```

4. **Common Issues**:
   - **Task fails to start**: Check IAM roles and permissions
   - **Container exits**: Check environment variables and memory limits
   - **API connectivity issues**: Verify VPC settings and security groups

### General Troubleshooting

1. Check container logs
2. Verify all environment variables are set correctly
3. Ensure sufficient memory and CPU are allocated
4. Check for network connectivity issues to external APIs

## Cost Optimization

To minimize costs:

1. Use serverless options when possible (Cloud Run, AWS Lambda)
2. Set up auto-scaling to scale down when not in use
3. Monitor usage and adjust resource allocation accordingly
