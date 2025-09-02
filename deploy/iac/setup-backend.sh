#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up Terraform Backend Infrastructure${NC}"
echo "=============================================="

# Configuration
BUCKET_NAME="family-helper-terraform-state"
TABLE_NAME="family-helper-terraform-locks"
REGION="us-east-1"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS CLI not configured or credentials invalid${NC}"
    echo "Please run: aws configure"
    exit 1
fi

echo -e "${GREEN}✅ AWS credentials validated${NC}"
echo

# Get current AWS account info
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
USER_ARN=$(aws sts get-caller-identity --query Arn --output text)

echo "AWS Account: $ACCOUNT_ID"
echo "User/Role: $USER_ARN"
echo "Region: $REGION"
echo

# Check if S3 bucket exists
echo -e "${BLUE}📦 Setting up S3 bucket for state storage...${NC}"

if aws s3api head-bucket --bucket "$BUCKET_NAME" --region "$REGION" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  S3 bucket '$BUCKET_NAME' already exists${NC}"
else
    echo "Creating S3 bucket '$BUCKET_NAME'..."
    
    # Create bucket
    aws s3api create-bucket \
        --bucket "$BUCKET_NAME" \
        --region "$REGION"
    
    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "$BUCKET_NAME" \
        --versioning-configuration Status=Enabled
    
    # Enable server-side encryption
    aws s3api put-bucket-encryption \
        --bucket "$BUCKET_NAME" \
        --server-side-encryption-configuration '{
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    },
                    "BucketKeyEnabled": true
                }
            ]
        }'
    
    # Block public access
    aws s3api put-public-access-block \
        --bucket "$BUCKET_NAME" \
        --public-access-block-configuration \
        BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
    
    echo -e "${GREEN}✅ S3 bucket '$BUCKET_NAME' created and configured${NC}"
fi

# Check if DynamoDB table exists
echo -e "${BLUE}🗃️  Setting up DynamoDB table for state locking...${NC}"

if aws dynamodb describe-table --table-name "$TABLE_NAME" --region "$REGION" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  DynamoDB table '$TABLE_NAME' already exists${NC}"
else
    echo "Creating DynamoDB table '$TABLE_NAME'..."
    
    aws dynamodb create-table \
        --table-name "$TABLE_NAME" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region "$REGION"
    
    # Wait for table to be active
    echo "Waiting for table to become active..."
    aws dynamodb wait table-exists --table-name "$TABLE_NAME" --region "$REGION"
    
    echo -e "${GREEN}✅ DynamoDB table '$TABLE_NAME' created${NC}"
fi

echo
echo -e "${GREEN}🎉 Backend infrastructure setup complete!${NC}"
echo
echo -e "${BLUE}Next steps:${NC}"
echo "1. Uncomment the backend configuration in your main.tf:"
echo
echo "   terraform {"
echo "     backend \"s3\" {"
echo "       bucket = \"$BUCKET_NAME\""
echo "       key    = \"dev/terraform.tfstate\""
echo "       region = \"$REGION\""
echo "       encrypt = true"
echo "       dynamodb_table = \"$TABLE_NAME\""
echo "     }"
echo "   }"
echo
echo "2. Run 'terraform init -migrate-state' to migrate to remote backend"
echo
echo -e "${YELLOW}💰 Cost Information:${NC}"
echo "- S3 storage: ~\$0.023 per GB per month (minimal for state files)"
echo "- DynamoDB: Pay-per-request (minimal cost for state locking)"
echo "- Estimated monthly cost: < \$1 for typical usage"
echo
echo -e "${BLUE}🔐 Security Features Enabled:${NC}"
echo "- S3 bucket encryption (AES-256)"
echo "- S3 versioning (for state history)"
echo "- S3 public access blocked"
echo "- DynamoDB state locking (prevents concurrent operations)"