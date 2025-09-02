# Development Environment Infrastructure

This directory contains the Terraform/OpenTofu configuration for the Family Helper development environment.

## Prerequisites

1. **OpenTofu/Terraform**: Install OpenTofu (recommended) or Terraform
   ```bash
   brew install opentofu
   # OR
   brew install terraform
   ```

2. **AWS CLI**: Install and configure AWS CLI
   ```bash
   brew install awscli
   aws configure
   ```

3. **AWS Credentials**: Ensure you have AWS credentials configured either through:
   - AWS CLI profile: `aws configure`
   - Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
   - IAM roles (for EC2/ECS)

## Infrastructure Overview

This configuration creates:

### Network Infrastructure
- **VPC**: Private network with DNS support
- **Public Subnets**: 2 subnets across different AZs for ALB and NAT Gateways
- **Private Subnets**: 2 subnets across different AZs for ECS tasks and RDS
- **Internet Gateway**: For public internet access
- **NAT Gateway**: Single NAT Gateway for cost optimization in dev (shared across AZs)
- **Route Tables**: Proper routing for public and private subnets

### Security Groups
- **ALB Security Group**: Allows HTTP (80) and HTTPS (443) inbound
- **ECS Security Group**: Allows traffic from ALB on all ports (container port mapping)
- **RDS Security Group**: Allows PostgreSQL (5432) from ECS tasks only

### Container Infrastructure
- **ECS Cluster**: Fargate-based cluster for containerized services
- **CloudWatch Log Groups**: Centralized logging for applications and ECS exec

## Usage

### Initialize
```bash
cd deploy/iac/envs/dev
tofu init
```

### Validate Configuration
```bash
tofu validate
```

### Plan Infrastructure Changes
```bash
tofu plan
```

### Apply Infrastructure (when ready)
```bash
tofu apply
```

### Destroy Infrastructure (cleanup)
```bash
tofu destroy
```

## Configuration

### Variables
See `variables.tf` for all configurable options. Key variables:

- `aws_region`: AWS region (default: us-east-1)
- `vpc_cidr`: VPC CIDR block (default: 10.0.0.0/16)
- `availability_zones`: AZs to use (default: us-east-1a, us-east-1b)
- `enable_nat_gateway`: Enable NAT Gateway (default: true)
- `single_nat_gateway`: Use single NAT Gateway for cost optimization (default: true)
- `log_retention_days`: CloudWatch log retention (default: 7 days)

### Customization
Modify `terraform.tfvars` to customize the environment:

```hcl
# terraform.tfvars
aws_region = "us-west-2"
availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]
single_nat_gateway = false  # Use multiple NAT Gateways for HA
log_retention_days = 30     # Longer log retention
```

## Cost Optimization

The development environment is optimized for cost:

1. **Single NAT Gateway**: Shared across all private subnets
2. **Short Log Retention**: 7 days for CloudWatch logs
3. **Fargate Spot**: Configured as capacity provider for cost savings
4. **Minimal Resources**: Only essential infrastructure components

## Outputs

After applying, the following outputs are available:

- **Network**: VPC ID, subnet IDs, route table IDs
- **Security**: Security group IDs for ALB, ECS, and RDS
- **ECS**: Cluster ID, name, and ARN
- **Logs**: CloudWatch log group names

Use outputs in other configurations:
```bash
tofu output vpc_id
tofu output -json | jq '.ecs_cluster_name.value'
```

## Remote State (Production)

For production use, configure remote state backend:

1. Create S3 bucket and DynamoDB table:
   ```bash
   aws s3 mb s3://family-helper-terraform-state
   aws dynamodb create-table \
     --table-name family-helper-terraform-locks \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST
   ```

2. Uncomment backend configuration in `main.tf`:
   ```hcl
   backend "s3" {
     bucket = "family-helper-terraform-state"
     key    = "dev/terraform.tfstate"
     region = "us-east-1"
     encrypt = true
     dynamodb_table = "family-helper-terraform-locks"
   }
   ```

3. Initialize with backend:
   ```bash
   tofu init -migrate-state
   ```

## Troubleshooting

### Common Issues

1. **Credential Errors**: Ensure AWS credentials are properly configured
2. **Region Availability**: Verify AZs exist in your chosen region
3. **Resource Limits**: Check AWS service limits for your account
4. **Permissions**: Ensure IAM user/role has necessary permissions

### Required AWS Permissions

The AWS credentials need permissions for:
- VPC and networking (vpc:*, ec2:*)
- ECS cluster management (ecs:*)
- CloudWatch logs (logs:*)
- IAM (for service roles)

## Security Considerations

- All resources are tagged with environment and project information
- Security groups follow principle of least privilege
- Private subnets are isolated from direct internet access
- CloudWatch logging enabled for audit trails
- Encryption at rest configured where applicable

## Next Steps

After infrastructure is created:
1. Deploy application services using the ECS cluster
2. Configure application load balancer with proper SSL certificates
3. Set up RDS database in private subnets
4. Configure monitoring and alerting
5. Set up CI/CD pipeline for deployments