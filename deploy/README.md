# Deployment Infrastructure

Infrastructure as Code (IaC) and deployment automation for the Family Helper platform.

## Structure

- **`iac/`** - Terraform modules and environment configurations
- **`pipelines/`** - CI/CD pipeline definitions (GitHub Actions)
- **`scripts/`** - Deployment and utility scripts

## Deployment Strategy

1. **Infrastructure First**: Terraform provisions AWS resources
2. **Container Build**: Services built into Docker images
3. **Service Deploy**: ECS services updated with new images
4. **Smoke Tests**: Health checks validate deployment

## Environment Progression

- **dev** - Development environment (single AZ, minimal resources)
- **staging** - Pre-production testing (multi-AZ, production-like)  
- **prod** - Production environment (multi-AZ, high availability)

## AWS Resources Managed

- **Networking**: VPC, subnets, security groups, NAT gateways
- **Compute**: ECS clusters, Fargate services, Application Load Balancer
- **Data**: RDS PostgreSQL, ElastiCache Redis, S3 buckets
- **Messaging**: SNS topics, SQS queues (FIFO)
- **Security**: Secrets Manager, KMS keys, IAM roles
- **Monitoring**: CloudWatch logs/metrics, X-Ray tracing

## Quick Start

```bash
# Deploy development environment
cd deploy/iac/envs/dev
terraform init
terraform plan
terraform apply

# Deploy services via CI/CD
git push origin main  # Triggers GitHub Actions pipeline
```