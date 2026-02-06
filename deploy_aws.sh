#!/bin/bash

###############################################################################
# Campus Guardian Drone - AWS EC2 Deployment Script
# Automated deployment to Amazon EC2
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTANCE_TYPE="t3.medium"
AMI_ID="ami-0c7217cdde317cfec"  # Ubuntu 22.04 LTS (us-east-1)
KEY_NAME="drone-guardian-key"
SECURITY_GROUP="drone-guardian-sg"
REGION="us-east-1"
VOLUME_SIZE=30

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Campus Guardian Drone - AWS EC2 Deployment              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found!${NC}"
    echo "Install it with: brew install awscli"
    echo "Or download from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured!${NC}"
    echo "Run: aws configure"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI configured${NC}"

# Get current AWS account info
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${BLUE}📊 AWS Account: ${ACCOUNT_ID}${NC}"
echo -e "${BLUE}📍 Region: ${REGION}${NC}"
echo ""

# Confirm deployment
echo -e "${YELLOW}⚠️  This will create AWS resources (charges will apply):${NC}"
echo "   - EC2 Instance: ${INSTANCE_TYPE} (~$30/month)"
echo "   - EBS Volume: ${VOLUME_SIZE}GB gp3 (~$2.40/month)"
echo "   - Elastic IP: Free (while attached)"
echo ""
echo -e "${YELLOW}   Estimated cost: ~$32-35/month${NC}"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}🚀 Starting deployment...${NC}"
echo ""

# Step 1: Create or verify SSH key pair
echo -e "${BLUE}[1/8] Checking SSH key pair...${NC}"
if aws ec2 describe-key-pairs --key-names ${KEY_NAME} --region ${REGION} &> /dev/null; then
    echo -e "${GREEN}✅ Key pair '${KEY_NAME}' already exists${NC}"
else
    echo "Creating key pair..."
    aws ec2 create-key-pair \
        --key-name ${KEY_NAME} \
        --region ${REGION} \
        --query 'KeyMaterial' \
        --output text > ~/.ssh/${KEY_NAME}.pem
    
    chmod 400 ~/.ssh/${KEY_NAME}.pem
    echo -e "${GREEN}✅ Key pair created and saved to ~/.ssh/${KEY_NAME}.pem${NC}"
fi

# Step 2: Create security group
echo ""
echo -e "${BLUE}[2/8] Setting up security group...${NC}"

# Check if security group exists
SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=${SECURITY_GROUP}" \
    --region ${REGION} \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "None")

if [ "$SG_ID" != "None" ]; then
    echo -e "${GREEN}✅ Security group '${SECURITY_GROUP}' already exists (${SG_ID})${NC}"
else
    # Get default VPC ID
    VPC_ID=$(aws ec2 describe-vpcs \
        --filters "Name=isDefault,Values=true" \
        --region ${REGION} \
        --query 'Vpcs[0].VpcId' \
        --output text)
    
    # Create security group
    SG_ID=$(aws ec2 create-security-group \
        --group-name ${SECURITY_GROUP} \
        --description "Security group for Campus Guardian Drone" \
        --vpc-id ${VPC_ID} \
        --region ${REGION} \
        --query 'GroupId' \
        --output text)
    
    # Add inbound rules
    aws ec2 authorize-security-group-ingress \
        --group-id ${SG_ID} \
        --protocol tcp --port 22 --cidr 0.0.0.0/0 \
        --region ${REGION} > /dev/null
    
    aws ec2 authorize-security-group-ingress \
        --group-id ${SG_ID} \
        --protocol tcp --port 80 --cidr 0.0.0.0/0 \
        --region ${REGION} > /dev/null
    
    aws ec2 authorize-security-group-ingress \
        --group-id ${SG_ID} \
        --protocol tcp --port 8080 --cidr 0.0.0.0/0 \
        --region ${REGION} > /dev/null
    
    aws ec2 authorize-security-group-ingress \
        --group-id ${SG_ID} \
        --protocol tcp --port 443 --cidr 0.0.0.0/0 \
        --region ${REGION} > /dev/null
    
    echo -e "${GREEN}✅ Security group created (${SG_ID})${NC}"
    echo "   - Port 22 (SSH): Open"
    echo "   - Port 80 (HTTP): Open"
    echo "   - Port 8080 (App): Open"
    echo "   - Port 443 (HTTPS): Open"
fi

# Step 3: Launch EC2 instance
echo ""
echo -e "${BLUE}[3/8] Launching EC2 instance...${NC}"

INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ${AMI_ID} \
    --count 1 \
    --instance-type ${INSTANCE_TYPE} \
    --key-name ${KEY_NAME} \
    --security-group-ids ${SG_ID} \
    --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=${VOLUME_SIZE},VolumeType=gp3}" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=drone-guardian-server}]" \
    --region ${REGION} \
    --query 'Instances[0].InstanceId' \
    --output text)

echo -e "${GREEN}✅ Instance launched: ${INSTANCE_ID}${NC}"
echo "   Waiting for instance to start..."

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids ${INSTANCE_ID} --region ${REGION}

# Get instance public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids ${INSTANCE_ID} \
    --region ${REGION} \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo -e "${GREEN}✅ Instance running${NC}"
echo "   Public IP: ${PUBLIC_IP}"

# Step 4: Wait for SSH to be ready
echo ""
echo -e "${BLUE}[4/8] Waiting for SSH to be ready...${NC}"
echo "   (This may take 1-2 minutes)"

MAX_ATTEMPTS=30
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if ssh -i ~/.ssh/${KEY_NAME}.pem -o StrictHostKeyChecking=no -o ConnectTimeout=5 ubuntu@${PUBLIC_IP} "echo 'SSH ready'" &> /dev/null; then
        echo -e "${GREEN}✅ SSH connection established${NC}"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo -e "${RED}❌ SSH connection timeout${NC}"
        exit 1
    fi
    sleep 10
    echo -n "."
done

# Step 5: Install dependencies
echo ""
echo -e "${BLUE}[5/8] Installing dependencies on EC2...${NC}"

ssh -i ~/.ssh/${KEY_NAME}.pem -o StrictHostKeyChecking=no ubuntu@${PUBLIC_IP} << 'ENDSSH'
#!/bin/bash
set -e

echo "📦 Updating system packages..."
sudo apt update -qq
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y -qq

echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh > /dev/null 2>&1
sudo usermod -aG docker ubuntu

echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose > /dev/null 2>&1
sudo chmod +x /usr/local/bin/docker-compose

echo "📚 Installing Git..."
sudo apt install -y git -qq

echo "✅ Dependencies installed"
ENDSSH

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 6: Clone repository and configure
echo ""
echo -e "${BLUE}[6/8] Deploying application...${NC}"

# Copy .env file
echo "   Copying environment file..."
scp -i ~/.ssh/${KEY_NAME}.pem -o StrictHostKeyChecking=no .env ubuntu@${PUBLIC_IP}:~/deployment.env

ssh -i ~/.ssh/${KEY_NAME}.pem -o StrictHostKeyChecking=no ubuntu@${PUBLIC_IP} << 'ENDSSH'
#!/bin/bash
set -e

echo "📥 Cloning repository..."
git clone https://github.com/HaryiankKumra/drone-aerial-view.git > /dev/null 2>&1 || {
    cd drone-aerial-view
    git pull origin main > /dev/null 2>&1
}

cd drone-aerial-view

# Use deployment env file
mv ~/deployment.env .env

echo "✅ Application deployed"
ENDSSH

echo -e "${GREEN}✅ Application deployed${NC}"

# Step 7: Build and start Docker containers
echo ""
echo -e "${BLUE}[7/8] Building and starting containers...${NC}"
echo "   (This may take 2-3 minutes)"

ssh -i ~/.ssh/${KEY_NAME}.pem -o StrictHostKeyChecking=no ubuntu@${PUBLIC_IP} << 'ENDSSH'
#!/bin/bash
set -e

cd drone-aerial-view

echo "🔨 Building Docker image..."
docker-compose build > /dev/null 2>&1

echo "🚀 Starting containers..."
docker-compose up -d

# Wait for server to be ready
echo "⏳ Waiting for server to start..."
sleep 10

# Check if server is running
if curl -s http://localhost:8080/system_status > /dev/null; then
    echo "✅ Server is running"
else
    echo "⚠️  Server may still be starting..."
fi
ENDSSH

echo -e "${GREEN}✅ Containers started${NC}"

# Step 8: Final verification
echo ""
echo -e "${BLUE}[8/8] Verifying deployment...${NC}"

# Test from local machine
sleep 5
if curl -s http://${PUBLIC_IP}:8080/system_status > /dev/null; then
    echo -e "${GREEN}✅ Server is accessible from internet${NC}"
else
    echo -e "${YELLOW}⚠️  Server may still be initializing...${NC}"
fi

# Print success message
echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🎉 DEPLOYMENT SUCCESSFUL!                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Details:${NC}"
echo "   Instance ID: ${INSTANCE_ID}"
echo "   Instance Type: ${INSTANCE_TYPE}"
echo "   Public IP: ${PUBLIC_IP}"
echo "   Region: ${REGION}"
echo ""
echo -e "${BLUE}🌐 Access URLs:${NC}"
echo "   Dashboard: ${GREEN}http://${PUBLIC_IP}:8080${NC}"
echo "   API Endpoint: ${GREEN}http://${PUBLIC_IP}:8080${NC}"
echo ""
echo -e "${BLUE}🔐 SSH Access:${NC}"
echo "   ${YELLOW}ssh -i ~/.ssh/${KEY_NAME}.pem ubuntu@${PUBLIC_IP}${NC}"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "   1. Open dashboard: http://${PUBLIC_IP}:8080"
echo "   2. Configure RPi client to use: http://${PUBLIC_IP}:8080"
echo "   3. Set up geofencing zones on dashboard"
echo "   4. (Optional) Configure domain name (see AWS_DEPLOYMENT.md)"
echo "   5. (Optional) Set up SSL/HTTPS (see AWS_DEPLOYMENT.md)"
echo ""
echo -e "${BLUE}🛠️  Management Commands:${NC}"
echo "   View logs:    ${YELLOW}ssh ... 'cd drone-aerial-view && docker-compose logs -f'${NC}"
echo "   Restart app:  ${YELLOW}ssh ... 'cd drone-aerial-view && docker-compose restart'${NC}"
echo "   Update app:   ${YELLOW}ssh ... 'cd drone-aerial-view && git pull && docker-compose up -d --build'${NC}"
echo ""
echo -e "${YELLOW}💰 Cost: ~$32-35/month${NC}"
echo ""
echo -e "${GREEN}✅ Deployment complete! Your system is now running on AWS EC2.${NC}"
echo ""
