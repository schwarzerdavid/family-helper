#!/bin/bash
set -e

echo "🚀 Validating Terraform Infrastructure"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "Checking prerequisites..."

# Check if tofu/terraform is installed
if command -v tofu &> /dev/null; then
    TERRAFORM_CMD="tofu"
    echo -e "${GREEN}✅ OpenTofu found${NC}"
elif command -v terraform &> /dev/null; then
    TERRAFORM_CMD="terraform"
    echo -e "${GREEN}✅ Terraform found${NC}"
else
    echo -e "${RED}❌ Neither OpenTofu nor Terraform found. Please install one of them.${NC}"
    echo "Install OpenTofu: brew install opentofu"
    echo "Install Terraform: brew install terraform"
    exit 1
fi

echo
echo "📁 Validating Network Module"
echo "-----------------------------"

cd modules/network

# Initialize network module
$TERRAFORM_CMD init > /dev/null 2>&1
print_status $? "Network module initialized"

# Validate network module
$TERRAFORM_CMD validate > /dev/null 2>&1
print_status $? "Network module validation"

# Format check
$TERRAFORM_CMD fmt -check > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_status 0 "Network module formatting"
else
    print_warning "Network module formatting needs updates (run 'terraform fmt')"
fi

cd - > /dev/null

echo
echo "🏗️  Validating Development Environment" 
echo "------------------------------------"

cd envs/dev

# Initialize dev environment
$TERRAFORM_CMD init > /dev/null 2>&1
print_status $? "Dev environment initialized"

# Validate dev environment
$TERRAFORM_CMD validate > /dev/null 2>&1
print_status $? "Dev environment validation"

# Format check
$TERRAFORM_CMD fmt -check > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_status 0 "Dev environment formatting"
else
    print_warning "Dev environment formatting needs updates (run 'terraform fmt')"
fi

# Test plan (without AWS credentials - just syntax)
echo
echo "📋 Testing Configuration Parsing"
echo "-------------------------------"

if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "AWS credentials detected - running full plan..."
    $TERRAFORM_CMD plan > /dev/null 2>&1
    print_status $? "Terraform plan generation"
else
    print_warning "AWS credentials not configured - skipping full plan"
    echo "To test with AWS:"
    echo "  export AWS_ACCESS_KEY_ID=your_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret"
    echo "  $TERRAFORM_CMD plan"
fi

cd - > /dev/null

echo
echo "📊 Configuration Summary"
echo "----------------------"
echo "Network Module:"
echo "  - VPC with public/private subnets"
echo "  - Internet Gateway and NAT Gateway"
echo "  - Route tables and associations"
echo "  - Configurable AZ and CIDR settings"
echo
echo "Development Environment:"
echo "  - ECS Fargate cluster"
echo "  - Security groups (ALB, ECS, RDS)"
echo "  - CloudWatch log groups"
echo "  - Cost-optimized (single NAT Gateway)"
echo

echo -e "${GREEN}🎉 All validations passed!${NC}"
echo
echo "Next steps:"
echo "1. Configure AWS credentials: aws configure"
echo "2. Initialize environment: cd envs/dev && $TERRAFORM_CMD init"  
echo "3. Plan infrastructure: $TERRAFORM_CMD plan"
echo "4. Apply when ready: $TERRAFORM_CMD apply"