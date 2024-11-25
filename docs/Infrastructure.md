# Infrastructure

Define project infrastructure using AWS and document the deployment strategy.

## Deployment Strategy Overview

The project uses AWS EC2 instances to deploy and run a Python agent that passively observes content using Selenium. The infrastructure consists of a Dockerized environment managed through GitHub Actions workflows, enabling automation for building, deploying, and executing the agent on a scheduled basis.

### AWS EC2 Infrastructure

- **EC2 Instances**: The infrastructure is built using Amazon EC2 instances. These instances are used to deploy the Docker container that runs the passive observation agent. Docker is installed on EC2, and the instances are configured for remote access using SSH.
- **Docker Environment**: Docker containers are used to provide an isolated environment for the agent. The Docker image is built locally and then transferred to the EC2 instance for execution.
- **AWS S3 Storage**: After the agent runs, data collected during the observation is synced to an AWS S3 bucket for persistent storage.

### GitHub Actions Workflows

The deployment strategy relies heavily on GitHub Actions to automate both the deployment and the daily execution of the agent. There are two separate workflows that manage this process:

#### 1. Build and Deploy Workflow
- **Trigger Conditions**: This workflow is triggered when changes are made to files in the `src` directory of the main branch. This ensures that Docker images are rebuilt only when necessary.
- **Docker Image Build and Deployment**: The workflow builds the Docker image based on the updated source code, then transfers the image to the EC2 instance. The image is then loaded onto the instance, ready for execution.
- **SSH Key Management**: The SSH key required to access the EC2 instance is securely managed through GitHub Secrets. During the workflow, the key is decoded and used temporarily for deployment, ensuring a secure connection.

#### 2. Daily Start Workflow
- **Scheduled Execution**: The daily start workflow is scheduled to run at 8 AM Bratislava time. The workflow ensures that the agent runs at the specified time each day.
- **Anonymous and Authorized User Execution**: The workflow runs the Docker container twice—once as an anonymous user and again with credentials for an authorized user. The credentials for the authorized user are securely loaded from GitHub Secrets.
- **Data Synchronization**: After execution, collected data is synchronized to an AWS S3 bucket for storage. The local data directory is then cleaned up to maintain the instance's storage efficiency.

### Security Considerations

- **SSH Key Management**: SSH keys used to access the EC2 instances are stored as GitHub Secrets, ensuring secure access without exposing sensitive information.
- **Environment Variables**: Credentials for the authorized user are also managed as GitHub Secrets, allowing them to be injected into the Docker container securely during runtime.
- **Host Key Verification**: To prevent MITM attacks, the known host's fingerprint is added to the workflow's trusted list before accessing the EC2 instance.

### Summary
The deployment strategy is designed to automate the build, deployment, and execution of the agent while maintaining a high level of security. By utilizing AWS EC2, Docker, and GitHub Actions, the infrastructure ensures efficient, repeatable deployments and scheduled task execution with appropriate security measures in place. If you want step by step replicate the infrastructure steps you can lookup our [aws cloud deployment guide](aws-cloud-deployment.md).

