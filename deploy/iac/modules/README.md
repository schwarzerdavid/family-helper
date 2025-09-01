# Terraform Modules

Reusable infrastructure components for the Family Helper platform.

## Available Modules

### network/
VPC and networking infrastructure:
- VPC with public/private subnets across multiple AZs
- Internet Gateway and NAT Gateways
- Route tables and security groups
- VPC endpoints for AWS services

**Usage:**
```hcl
module "network" {
  source = "./modules/network"
  name   = "fh-dev"
  cidr   = "10.0.0.0/16"
  azs    = ["us-east-1a", "us-east-1b", "us-east-1c"]
}
```

### compute/
Container orchestration and load balancing:
- ECS Fargate cluster
- Application Load Balancer with SSL termination
- Auto Scaling groups and policies
- CloudWatch log groups

### storage/
Persistent storage services:
- RDS PostgreSQL with Multi-AZ for production
- ElastiCache Redis cluster
- S3 buckets for object storage
- Parameter Store for configuration

### messaging/
Event-driven messaging infrastructure:
- SNS topics for event publishing
- SQS FIFO queues for reliable processing
- Dead Letter Queues for failed messages
- CloudWatch alarms for queue depth

### security/
IAM roles, policies, and secrets management:
- Service-specific IAM roles with least privilege
- KMS keys for encryption
- Secrets Manager for sensitive configuration
- WAF rules for API protection

## Module Standards

Each module includes:
- **variables.tf** - Input parameters
- **main.tf** - Resource definitions  
- **outputs.tf** - Exported values
- **README.md** - Usage documentation
- **examples/** - Sample configurations

## Development

```bash
# Validate module
terraform init
terraform validate

# Format code  
terraform fmt -recursive

# Generate documentation
terraform-docs markdown table --output-file README.md .
```