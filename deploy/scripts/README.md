# Deployment Scripts

Utility scripts for deployment, maintenance, and operational tasks.

## Scripts Overview

### Infrastructure Scripts

**`setup-aws.sh`**
Initial AWS account setup:
- Create Terraform state bucket
- Set up OIDC provider for GitHub Actions
- Create initial IAM roles and policies

**`deploy-env.sh`**
Environment deployment wrapper:
```bash
./deploy-env.sh dev    # Deploy development environment
./deploy-env.sh prod   # Deploy production environment
```

### Application Scripts

**`update-services.sh`**
Update ECS services with new image versions:
```bash
./update-services.sh gateway-edge:latest dev
./update-services.sh identity:v1.2.3 prod
```

**`smoke-tests.sh`**
Health check validation after deployment:
```bash
./smoke-tests.sh https://api.dev.familyhelper.app
```

### Database Scripts

**`db-migrate.sh`**
Database schema migrations:
```bash
./db-migrate.sh dev up      # Apply pending migrations
./db-migrate.sh prod status # Check migration status
```

**`db-backup.sh`**
Manual database backup:
```bash
./db-backup.sh prod s3://fh-backups/manual/
```

### Monitoring Scripts

**`health-check.sh`**
Comprehensive system health validation:
- Service endpoint health
- Database connectivity
- Queue depth monitoring
- External service dependencies

**`logs.sh`**
Centralized log access:
```bash
./logs.sh identity dev --tail    # Follow identity service logs
./logs.sh --all prod --since 1h  # All services, last hour
```

## Script Standards

All scripts follow these conventions:
- **Bash compatibility**: Works on Ubuntu/macOS
- **Error handling**: Proper exit codes and error messages
- **Help documentation**: `--help` flag with usage examples
- **Environment validation**: Check required tools and credentials
- **Logging**: Structured output with timestamps

## Configuration

Scripts read configuration from:
- **Environment variables**: `AWS_REGION`, `ENV_NAME`, etc.
- **Config files**: `.env.{environment}` files
- **AWS Parameter Store**: Runtime configuration values

## Usage Examples

```bash
# Complete environment setup
./setup-aws.sh
./deploy-env.sh dev

# Service update workflow  
./update-services.sh identity:v1.3.0 dev
./smoke-tests.sh https://api.dev.familyhelper.app/health
./health-check.sh dev

# Maintenance tasks
./db-migrate.sh dev up
./logs.sh identity dev --tail
```