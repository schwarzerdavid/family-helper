# Development Environment

Terraform configuration for the development environment of Family Helper platform.

## Purpose

Provides a cost-optimized development environment for:
- Local development and testing
- CI/CD integration testing
- Feature branch deployments
- Developer experimentation

## Architecture

- **Single AZ deployment** (cost optimization)
- **Minimal instance sizes** (t3.micro, db.t3.micro)
- **Single NAT Gateway** (shared across subnets)
- **Development-grade RDS** (no Multi-AZ, smaller backups)

## Configuration

```hcl
# main.tf
locals {
  env = "dev"
  project = "family-helper"
}

module "network" {
  source = "../../modules/network"
  name   = "${local.project}-${local.env}"
  cidr   = "10.0.0.0/16"
  azs    = ["us-east-1a", "us-east-1b"]
}

module "compute" {
  source = "../../modules/compute"
  env    = local.env
  vpc_id = module.network.vpc_id
  subnet_ids = module.network.private_subnet_ids
}
```

## Resource Sizing

| Service | Instance Type | Notes |
|---------|---------------|-------|
| ECS Tasks | 0.25 vCPU, 512 MB RAM | Minimal for dev workloads |
| RDS | db.t3.micro | Single AZ, 20GB storage |
| Redis | cache.t3.micro | Single node |
| ALB | Application Load Balancer | Shared across services |

## Deployment

```bash
# Initialize Terraform
terraform init -backend-config=backend.hcl

# Plan changes
terraform plan -var-file=dev.tfvars -out=tf.plan

# Apply changes  
terraform apply tf.plan

# Get outputs
terraform output
```

## Backend Configuration

```hcl
# backend.hcl
bucket         = "fh-terraform-state"
key            = "envs/dev/terraform.tfstate"
region         = "us-east-1"  
dynamodb_table = "fh-terraform-locks"
encrypt        = true
```

## Cost Management

- Resources tagged with `Environment=dev` for cost allocation
- Scheduled stop/start of non-critical resources
- Spot instances where appropriate (non-production workloads)