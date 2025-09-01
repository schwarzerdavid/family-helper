# Infrastructure as Code (Terraform)

Terraform configuration for provisioning AWS infrastructure for Family Helper platform.

## Role

Manages all AWS resources required for the platform:
- Networking (VPC, subnets, security groups)
- Compute (ECS, Fargate, Load Balancers) 
- Storage (RDS, Redis, S3)
- Security (IAM, Secrets Manager, KMS)
- Messaging (SNS, SQS)

## Structure

```
iac/
├── modules/           # Reusable Terraform modules
│   ├── network/      # VPC, subnets, security groups
│   ├── compute/      # ECS cluster, services, ALB
│   ├── storage/      # RDS, Redis, S3 buckets
│   ├── messaging/    # SNS topics, SQS queues
│   └── security/     # IAM roles, Secrets Manager
├── envs/
│   └── dev/          # Development environment
└── shared/           # Cross-environment resources
```

## Module Design Principles

1. **Composable**: Modules can be combined for different environments
2. **Parameterized**: All values configurable via variables  
3. **Tagged**: Consistent resource tagging for cost allocation
4. **Secured**: Least privilege IAM, encryption at rest/transit

## Example Usage

```hcl
# envs/dev/main.tf
module "network" {
  source = "../../modules/network" 
  
  name = "fh-dev"
  cidr = "10.0.0.0/16"
  azs  = ["us-east-1a", "us-east-1b"]
}

module "storage" {
  source = "../../modules/storage"
  
  env    = "dev"
  vpc_id = module.network.vpc_id
  subnet_ids = module.network.private_subnet_ids
}
```

## State Management

- **Backend**: S3 bucket with DynamoDB locking
- **Workspaces**: Separate state per environment
- **Encryption**: State encrypted with KMS

## Best Practices

- Plan before apply: `terraform plan -out=tf.plan`
- Use consistent naming: `{project}-{env}-{resource}`
- Tag all resources with environment and project
- Store sensitive values in Secrets Manager
- Use data sources for cross-module references