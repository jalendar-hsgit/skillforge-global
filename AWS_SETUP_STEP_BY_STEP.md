# AWS Deployment: Complete Step-by-Step Guide (Dev + Prod)

**Date:** March 11, 2026  
**Target:** Zero to Production in AWS

---

## 📋 PHASE 1: AWS Account Setup & Preparation (30 minutes)

### Step 1.1: Create & Configure AWS Account

**Task 1: Create AWS Account**
```bash
# Visit: https://aws.amazon.com/
# Click "Create AWS Account"
# Fill out information:
  - Email address
  - AWS account name (e.g., "SkillForge")
  - Password (min 8 chars, complex)
  - Choose organization or personal
# Verify email
# Add payment method (credit card required even for free tier)
# Verify phone number
```

**Expected Outcome:** AWS account active, can log into console

---

### Step 1.2: Set Up IAM User (Security Best Practice)

**Task 1: Create IAM Admin User**
```bash
# Step 1: Go to AWS Console → IAM → Users
# Step 2: Click "Create user"
  - Username: "skillforge-admin"
  - Check: "Provide user access to AWS Management Console"
  - Console password: "Custom password"
  - Uncheck: "Users must create a new password on next sign in"
# Step 3: Click "Next"
# Step 4: Set permissions
  - Select: "Attach policies directly"
  - Search for: "AdministratorAccess"
  - Check the box
# Step 5: Click "Create user"
# Step 6: Go back → Click user → "Security credentials" tab
```

**Expected Outcome:** IAM user created with admin access

---

### Step 1.3: Create Access Keys for CLI

**Task 1: Generate Access Keys**
```bash
# In AWS Console → IAM → Users → skillforge-admin
# Click "Create access key"
  - Select: "Command Line Interface (CLI)"
  - Check: "I understand..."
  - Click "Create access key"
# SAVE THESE (show only once!):
  - Access key ID: AKIA...
  - Secret access key: ....
# Download CSV file for backup
```

**Task 2: Install AWS CLI**
```bash
# Windows PowerShell:
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi /qb

# MacOS:
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Linux:
curl "https://awscli.amazonaws.com/awscliv2.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

**Task 3: Configure CLI with Credentials**
```bash
# Run configuration
aws configure

# When prompted, enter:
  - AWS Access Key ID: [paste your access key]
  - AWS Secret Access Key: [paste your secret key]
  - Default region: us-east-1
  - Default output format: json

# Verify it worked
aws sts get-caller-identity
# Should return your user info
```

**Expected Outcome:** AWS CLI configured and tested

---

### Step 1.4: Create GitHub SSH Keys (Optional but Recommended)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"
# Save to: ~/.ssh/id_skillforge

# Add to SSH agent
ssh-add ~/.ssh/id_skillforge

# Copy public key
cat ~/.ssh/id_skillforge.pub

# Add to GitHub:
# GitHub Settings → SSH and GPG keys → New SSH key
# Paste the key from above
```

---

## 🏗️ PHASE 2: VPC & Network Setup (45 minutes)

### Step 2.1: Create VPC (Virtual Private Cloud)

**Task 1: Create VPC via Console**
```bash
# Go to: AWS Console → VPC → VPCs
# Click: "Create VPC"
  - VPC only
  - Name tag: skillforge-vpc
  - IPv4 CIDR block: 10.0.0.0/16
  - IPv6 CIDR block: No IPv6 CIDR block
  - Tenancy: Default
# Click: "Create VPC"
```

**Via CLI (Faster):**
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=skillforge-vpc}]'

# Output will show:
{
  "Vpc": {
    "VpcId": "vpc-0123456789abcdef0",  # SAVE THIS!
    "CidrBlock": "10.0.0.0/16",
    ...
  }
}

# Save the VPC ID for later use
VPC_ID="vpc-0123456789abcdef0"
```

**Expected Outcome:** VPC created with CIDR block 10.0.0.0/16

---

### Step 2.2: Create Subnets (Public for ALB, Private for Services)

**Task 1: Create Public Subnet (for ALB)**
```bash
# Via CLI
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=skillforg-public-subnet-1a}]'

# Response:
{
  "Subnet": {
    "SubnetId": "subnet-public1a",  # SAVE THIS!
    ...
  }
}

SUBNET_PUBLIC_1A="subnet-public1a"

# Create second public subnet for redundancy
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=skillforge-public-subnet-1b}]'

SUBNET_PUBLIC_1B="subnet-public1b"
```

**Task 2: Create Private Subnets (for EC2/RDS)**
```bash
# Private subnet 1a
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.3.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=skillforge-private-subnet-1a}]'

SUBNET_PRIVATE_1A="subnet-private1a"

# Private subnet 1b
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.4.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=skillforge-private-subnet-1b}]'

SUBNET_PRIVATE_1B="subnet-private1b"
```

**Expected Outcome:** 4 subnets created (2 public, 2 private)

**VPC Layout:**
```
VPC: 10.0.0.0/16
├── Public Subnet 1a: 10.0.1.0/24 (ALB)
├── Public Subnet 1b: 10.0.2.0/24 (ALB redundancy)
├── Private Subnet 1a: 10.0.3.0/24 (EC2, RDS)
└── Private Subnet 1b: 10.0.4.0/24 (RDS redundancy)
```

---

### Step 2.3: Create Internet Gateway

**Task 1: Create IGW**
```bash
# Create internet gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=skillforge-igw}]'

# Response:
{
  "InternetGateway": {
    "InternetGatewayId": "igw-0123456789abcdef0",  # SAVE THIS!
    ...
  }
}

IGW_ID="igw-0123456789abcdef0"

# Attach to VPC
aws ec2 attach-internet-gateway \
  --internet-gateway-id $IGW_ID \
  --vpc-id $VPC_ID
```

**Expected Outcome:** Internet Gateway created and attached to VPC

---

### Step 2.4: Create Route Tables

**Task 1: Create Public Route Table**
```bash
# Create route table
aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=skillforge-public-rt}]'

# Response:
{
  "RouteTable": {
    "RouteTableId": "rtb-public",  # SAVE THIS!
    ...
  }
}

PUBLIC_RT="rtb-public"

# Add route to internet gateway
aws ec2 create-route \
  --route-table-id $PUBLIC_RT \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID

# Associate with public subnets
aws ec2 associate-route-table \
  --subnet-id $SUBNET_PUBLIC_1A \
  --route-table-id $PUBLIC_RT

aws ec2 associate-route-table \
  --subnet-id $SUBNET_PUBLIC_1B \
  --route-table-id $PUBLIC_RT
```

**Task 2: Create Private Route Table**
```bash
# Create private route table (no internet route)
aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=skillforge-private-rt}]'

PRIVATE_RT="rtb-private"

# Associate with private subnets
aws ec2 associate-route-table \
  --subnet-id $SUBNET_PRIVATE_1A \
  --route-table-id $PRIVATE_RT

aws ec2 associate-route-table \
  --subnet-id $SUBNET_PRIVATE_1B \
  --route-table-id $PRIVATE_RT
```

**Expected Outcome:** Route tables configured for public and private subnets

---

### Step 2.5: Create Security Groups

**Task 1: Create ALB Security Group**
```bash
# ALB security group
aws ec2 create-security-group \
  --group-name skillforge-alb-sg \
  --description "ALB for SkillForge" \
  --vpc-id $VPC_ID

# Response:
{
  "GroupId": "sg-alb"  # SAVE THIS!
}

SG_ALB="sg-alb"

# Add HTTP inbound rule (anyone can access)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ALB \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Add HTTPS inbound rule
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ALB \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

**Task 2: Create Backend Security Group**
```bash
# Backend EC2 security group
aws ec2 create-security-group \
  --group-name skillforge-backend-sg \
  --description "Backend EC2 for SkillForge" \
  --vpc-id $VPC_ID

SG_BACKEND="sg-backend"

# Allow traffic from ALB only
aws ec2 authorize-security-group-ingress \
  --group-id $SG_BACKEND \
  --protocol tcp \
  --port 8001 \
  --source-security-group-id $SG_ALB

# Allow SSH from your IP (replace with your IP)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_BACKEND \
  --protocol tcp \
  --port 22 \
  --cidr YOUR_IP/32
  # Example: 203.0.113.42/32
```

**Task 3: Create RDS Security Group**
```bash
# RDS database security group
aws ec2 create-security-group \
  --group-name skillforge-rds-sg \
  --description "RDS PostgreSQL for SkillForge" \
  --vpc-id $VPC_ID

SG_RDS="sg-rds"

# Allow traffic from backend EC2 only
aws ec2 authorize-security-group-ingress \
  --group-id $SG_RDS \
  --protocol tcp \
  --port 5432 \
  --source-security-group-id $SG_BACKEND
```

**Expected Outcome:** 3 security groups configured with proper rules

---

## 💾 PHASE 3: Database Setup (45 minutes)

### Step 3.1: Create RDS Subnet Group

**Task 1: Create DB Subnet Group**
```bash
# Create subnet group for RDS (must span 2 AZs)
aws rds create-db-subnet-group \
  --db-subnet-group-name skillforge-db-subnet \
  --db-subnet-group-description "Subnet group for SkillForge RDS" \
  --subnet-ids $SUBNET_PRIVATE_1A $SUBNET_PRIVATE_1B

# Response:
{
  "DBSubnetGroup": {
    "DBSubnetGroupName": "skillforge-db-subnet",
    ...
  }
}
```

**Expected Outcome:** DB subnet group created across 2 AZs

---

### Step 3.2: Create RDS PostgreSQL Instance (Production)

**Task 1: Create Production Database**
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier skillforge-prod-db \
  --db-instance-class db.t3.small \
  --engine postgres \
  --engine-version 15.3 \
  --master-username admin \
  --master-user-password 'Your$ecureP@ssw0rd123!' \
  --allocated-storage 20 \
  --storage-type gp3 \
  --backup-retention-period 30 \
  --db-subnet-group-name skillforge-db-subnet \
  --vpc-security-group-ids $SG_RDS \
  --publicly-accessible false \
  --multi-az \
  --db-name skillforge \
  --storage-encrypted \
  --tags "Key=Environment,Value=production" "Key=Project,Value=SkillForge"
```

**Wait for RDS to be available (5-10 minutes):**
```bash
# Check status
aws rds describe-db-instances \
  --db-instance-identifier skillforge-prod-db \
  --query 'DBInstances[0].DBInstanceStatus'

# Should eventually return: "available"
# Get the endpoint:
aws rds describe-db-instances \
  --db-instance-identifier skillforge-prod-db \
  --query 'DBInstances[0].Endpoint.Address'

# Output: skillforge-prod-db.c9akciq32.us-east-1.rds.amazonaws.com
# SAVE THIS!
RDS_ENDPOINT_PROD="skillforge-prod-db.c9akciq32.us-east-1.rds.amazonaws.com"
```

**Expected Outcome:** Production RDS PostgreSQL instance created and available

---

### Step 3.3: Create RDS PostgreSQL Instance (Development)

**Task 1: Create Development Database**
```bash
# Create dev RDS (smaller, single-AZ, less backups)
aws rds create-db-instance \
  --db-instance-identifier skillforge-dev-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username admin \
  --master-user-password 'Dev$ecureP@ssw0rd123!' \
  --allocated-storage 10 \
  --storage-type gp3 \
  --backup-retention-period 7 \
  --db-subnet-group-name skillforge-db-subnet \
  --vpc-security-group-ids $SG_RDS \
  --publicly-accessible false \
  --no-multi-az \
  --db-name skillforge_dev \
  --storage-encrypted \
  --tags "Key=Environment,Value=development" "Key=Project,Value=SkillForge"

# Get dev endpoint
RDS_ENDPOINT_DEV="skillforge-dev-db.c9akciq32.us-east-1.rds.amazonaws.com"
```

**Wait for creation (5-10 minutes)**

**Expected Outcome:** Development RDS instance created

---

## 🖥️ PHASE 4: EC2 Setup (1 hour)

### Step 4.1: Create EC2 Key Pair

**Task 1: Create SSH Key Pair**
```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name skillforge-prod-key \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/skillforge-prod-key.pem

# Set permissions (Linux/Mac)
chmod 400 ~/.ssh/skillforge-prod-key.pem

# Windows PowerShell: (right-click → Properties → Security → 
# Edit → Remove inheritance → Apply)
```

**Create development key pair:**
```bash
aws ec2 create-key-pair \
  --key-name skillforge-dev-key \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/skillforge-dev-key.pem

chmod 400 ~/.ssh/skillforge-dev-key.pem
```

**Expected Outcome:** SSH key pairs created and saved

---

### Step 4.2: Launch EC2 Instance (Production)

**Task 1: Get Latest Ubuntu AMI**
```bash
# Find latest Ubuntu 22.04 LTS AMI
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images[0].ImageId' \
  --output text

# Output: ami-0c55b159cbfafe1f0
AMI_ID="ami-0c55b159cbfafe1f0"
```

**Task 2: Launch Production EC2**
```bash
# Launch instance
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.medium \
  --key-name skillforge-prod-key \
  --security-group-ids $SG_BACKEND \
  --subnet-id $SUBNET_PRIVATE_1A \
  --Associate-public-ip-address \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=30,VolumeType=gp3,DeleteOnTermination=true}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=skillforge-backend-prod}]' \
  --user-data file://user-data-prod.sh

# Response:
{
  "Instances": [
    {
      "InstanceId": "i-prod0123"  # SAVE THIS!
      ...
    }
  ]
}

INSTANCE_ID_PROD="i-prod0123"
```

**Task 3: Get Instance Details**
```bash
# Get public IP
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID_PROD \
  --query 'Reservations[0].Instances[0].PublicIpAddress'

# Example: 54.165.123.456
PUBLIC_IP_PROD="54.165.123.456"

# Get private IP
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID_PROD \
  --query 'Reservations[0].Instances[0].PrivateIpAddress'

# Example: 10.0.3.42
PRIVATE_IP_PROD="10.0.3.42"
```

**Wait for instance to be running:**
```bash
# Check status
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID_PROD \
  --query 'Reservations[0].Instances[0].State.Name'

# Should be: "running"
```

**Expected Outcome:** Production EC2 instance running in private subnet

---

### Step 4.3: Launch EC2 Instance (Development)

**Task 1: Launch Development EC2**
```bash
# Smaller dev instance
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t3.small \
  --key-name skillforge-dev-key \
  --security-group-ids $SG_BACKEND \
  --subnet-id $SUBNET_PRIVATE_1B \
  --Associate-public-ip-address \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=20,VolumeType=gp3,DeleteOnTermination=true}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=skillforge-backend-dev}]' \
  --user-data file://user-data-dev.sh

INSTANCE_ID_DEV="i-dev0123"
PUBLIC_IP_DEV="54.165.123.457"
PRIVATE_IP_DEV="10.0.4.42"
```

**Expected Outcome:** Development EC2 instance running

---

## 🔌 PHASE 5: Load Balancer Setup (30 minutes)

### Step 5.1: Create Application Load Balancer

**Task 1: Create ALB**
```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name skillforge-alb \
  --subnets $SUBNET_PUBLIC_1A $SUBNET_PUBLIC_1B \
  --security-groups $SG_ALB \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --tags "Key=Name,Value=skillforge-alb"

# Response:
{
  "LoadBalancers": [
    {
      "LoadBalancerArn": "arn:aws:elasticloadbalancing:us-east-1:...:loadbalancer/app/skillforge-alb/...",
      "DNSName": "skillforge-alb-1234567890.us-east-1.elb.amazonaws.com",
      ...
    }
  ]
}

ALB_ARN="arn:aws:elasticloadbalancing:us-east-1:...:loadbalancer/app/skillforge-alb/..."
ALB_DNS="skillforge-alb-1234567890.us-east-1.elb.amazonaws.com"
```

**Expected Outcome:** ALB created and available

---

### Step 5.2: Create Target Groups

**Task 1: Create Target Group for Backend**
```bash
# Create target group
aws elbv2 create-target-group \
  --name skillforge-backend-tg \
  --protocol HTTP \
  --port 8001 \
  --vpc-id $VPC_ID \
  --health-check-enabled \
  --health-check-protocol HTTP \
  --health-check-path /api/v1/health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --matcher "HttpCode=200,307" \
  --tags "Key=Name,Value=skillforge-backend-tg"

# Response:
{
  "TargetGroups": [
    {
      "TargetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:...:targetgroup/skillforge-backend-tg/...",
      ...
    }
  ]
}

TG_BACKEND="arn:aws:elasticloadbalancing:us-east-1:...:targetgroup/skillforge-backend-tg/..."
```

**Task 2: Register Backend Instances**
```bash
# Register production instance
aws elbv2 register-targets \
  --target-group-arn $TG_BACKEND \
  --targets "Id=$INSTANCE_ID_PROD,Port=8001"

# Register development instance (optional)
aws elbv2 register-targets \
  --target-group-arn $TG_BACKEND \
  --targets "Id=$INSTANCE_ID_DEV,Port=8001"
```

**Expected Outcome:** Target group created and instances registered

---

### Step 5.3: Configure ALB Listeners

**Task 1: Create HTTP Listener (Redirect to HTTPS)**
```bash
# HTTP listener that redirects to HTTPS
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions "Type=redirect,RedirectConfig={Protocol=HTTPS,Port=443,StatusCode=HTTP_301}"
```

**Task 2: Create HTTPS Listener**
```bash
# First, request SSL certificate from ACM

# Create HTTPS listener
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates "CertificateArn=arn:aws:acm:us-east-1:...:certificate/..." \
  --default-actions "Type=forward,TargetGroupArn=$TG_BACKEND"
```

**Expected Outcome:** Listeners configured for HTTP → HTTPS redirect

---

## 📡 PHASE 6: S3 & CloudFront Setup for Frontend (30 minutes)

### Step 6.1: Create S3 Bucket

**Task 1: Create S3 Bucket**
```bash
# Create bucket
aws s3api create-bucket \
  --bucket skillforge-frontend-prod \
  --region us-east-1
  # (For regions other than us-east-1, add --create-bucket-configuration LocationConstraint=region)

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket skillforge-frontend-prod \
  --versioning-configuration Status=Enabled

# Block public access (CloudFront will use OAI)
aws s3api put-public-access-block \
  --bucket skillforge-frontend-prod \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

**Expected Outcome:** S3 bucket created with proper security

---

### Step 6.2: Create CloudFront Distribution

**Task 1: Create Origin Access Identity (OAI)**
```bash
# Create OAI for S3
aws cloudfront create-cloud-front-origin-access-identity \
  --cloud-front-origin-access-identity-config CallerReference=skillforge-$(date +%s),Comment="OAI for SkillForge S3"

# Response:
{
  "CloudFrontOriginAccessIdentity": {
    "Id": "E12345EXAMPLE",
    ...
  }
}

OAI_ID="E12345EXAMPLE"
```

**Task 2: Update S3 Bucket Policy**
```bash
# Allow CloudFront to access S3
cat > /tmp/s3-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity $OAI_ID"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::skillforge-frontend-prod/*"
    }
  ]
}
EOF

# Update bucket policy (replace $OAI_ID in file)
# Then apply:
aws s3api put-bucket-policy \
  --bucket skillforge-frontend-prod \
  --policy file:///tmp/s3-policy.json
```

**Task 3: Create CloudFront Distribution**
```bash
# Create distribution
aws cloudfront create-distribution \
  --origin-domain-name skillforge-frontend-prod.s3.us-east-1.amazonaws.com \
  --default-root-object index.html \
  --cloudfront-origin-access-identity-config ~/cloudfront-config.json

# Response includes:
{
  "Distribution": {
    "Id": "E3ZZZZZ",
    "DomainName": "d111111abcdef8.cloudfront.net",
    ...
  }
}

CF_DOMAIN="d111111abcdef8.cloudfront.net"
```

**Expected Outcome:** CloudFront distribution created

---

## 🔐 PHASE 7: DNS & SSL Configuration (30 minutes)

### Step 7.1: Get SSL Certificate from ACM

**Task 1: Request Certificate**
```bash
# Request public certificate
aws acm request-certificate \
  --domain-name skillforge.com \
  --subject-alternative-names api.skillforge.com www.skillforge.com \
  --validation-method DNS \
  --options CertificateTransparencyLoggingPreference=ENABLED

# Response:
{
  "CertificateArn": "arn:aws:acm:us-east-1:...:certificate/abc123..."
}

CERT_ARN="arn:aws:acm:us-east-1:...:certificate/abc123..."
```

**Task 2: Validate Certificate (DNS Method)**
```bash
# Get validation records
aws acm describe-certificate \
  --certificate-arn $CERT_ARN \
  --query 'Certificate.DomainValidationOptions'

# Output:
[
  {
    "DomainName": "skillforge.com",
    "ValidationDomain": "skillforge.com",
    "ResourceRecord": {
      "Name": "_abc123.skillforge.com",
      "Type": "CNAME",
      "Value": "_xyz789.acm-validations.aws."
    }
  },
  ...
]

# Add these CNAME records to your Domain Registrar (GoDaddy, Namecheap, etc.)
# Or use Route 53 (next step)
```

**Wait for validation (can take 5-30 minutes)**

---

### Step 7.2: Set Up Route 53 DNS

**Task 1: Create Hosted Zone**
```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name skillforge.com \
  --caller-reference skillforge-$(date +%s)

# Response:
{
  "HostedZone": {
    "Id": "/hostedzone/Z1234567890ABC",
    "Name": "skillforge.com.",
    "ResourceRecordSetCount": 2
  },
  "NameServers": [
    "ns-123.awsdns-45.com",
    "ns-456.awsdns-78.com",
    "ns-789.awsdns-01.com",
    "ns-234.awsdns-56.com"
  ]
}

ZONE_ID="Z1234567890ABC"
```

**Update your domain registrar with these Name Servers**

**Task 2: Create Route 53 Records**
```bash
# Create CNAME record for ACM validation
aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID \
  --change-batch file:///tmp/route53-validation.json

# Create alias record for ALB (backend API)
cat > /tmp/api-record.json << 'EOF'
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.skillforge.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",  # ALB zone ID for us-east-1
          "DNSName": "skillforge-alb-1234567890.us-east-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }
  ]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID \
  --change-batch file:///tmp/api-record.json

# Create CloudFront alias (frontend)
cat > /tmp/cf-record.json << 'EOF'
{
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "skillforge.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",  # CloudFront zone ID
          "DNSName": "d111111abcdef8.cloudfront.net",
          "EvaluateTargetHealth": false
        }
      }
    },
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.skillforge.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "d111111abcdef8.cloudfront.net",
          "EvaluateTargetHealth": false
        }
      }
    }
  ]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID \
  --change-batch file:///tmp/cf-record.json
```

**Expected Outcome:** DNS records configured, pointing to ALB and CloudFront

---

## 🚀 PHASE 8: Application Deployment (1.5 hours)

### Step 8.1: Connect to Production EC2

**Task 1: SSH into Instance**
```bash
# Get instance details
aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID_PROD \
  --query 'Reservations[0].Instances[0].PublicIpAddress'

PUBLIC_IP="54.165.123.456"

# SSH in
ssh -i ~/.ssh/skillforge-prod-key.pem ubuntu@$PUBLIC_IP

# First time, you might need to wait a moment and accept the key
# Type: yes
```

**Expected Outcome:** Connected to production EC2 instance

---

### Step 8.2: Install Dependencies on EC2

**Task 1: Update System**
```bash
# On EC2:
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y \
  python3.11 \
  python3-pip \
  python3-venv \
  git \
  curl \
  wget \
  nginx \
  certbot \
  python3-certbot-nginx

# Install Docker (optional, for containerized deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

**Expected Outcome:** System prepared for application deployment

---

### Step 8.3: Deploy Backend Application

**Task 1: Clone Repository**
```bash
# On EC2:
cd /opt
sudo mkdir -p skillforge
sudo chown ubuntu:ubuntu skillforge
cd skillforge

# Clone repo
git clone https://github.com/YOUR_ORG/skillforge-global.git .

# Or with SSH key:
git clone git@github.com:YOUR_ORG/skillforge-global.git .
```

**Task 2: Set Up Python Environment**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r backend/requirements.txt
```

**Task 3: Configure Environment Variables**
```bash
# Create .env.production file
cat > backend/.env.production << 'EOF'
# Database
DATABASE_URL=postgresql://admin:Your$ecureP@ssw0rd123!@skillforge-prod-db.c9akciq32.us-east-1.rds.amazonaws.com:5432/skillforge

# Stripe
STRIPE_SECRET_KEY=sk_live_your_actual_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_stripe_public_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# JWT
JWT_SECRET_KEY=your-super-secret-random-key-minimum-32-characters-long

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=https://skillforge.com,https://www.skillforge.com,https://api.skillforge.com
EOF

# Secure file
chmod 600 backend/.env.production
```

**Task 4: Initialize Database**
```bash
# From /opt/skillforge:
cd backend
python init_db.py

# Seed demo data (optional)
python seed_all_demo_data.py
```

**Expected Outcome:** Application code deployed, database initialized

---

### Step 8.4: Configure Gunicorn & Nginx

**Task 1: Create Systemd Service**
```bash
# Create service file
sudo tee /etc/systemd/system/skillforge.service > /dev/null << 'EOF'
[Unit]
Description=SkillForge FastAPI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/skillforge/backend
Environment="PATH=/opt/skillforge/venv/bin"
EnvironmentFile=/opt/skillforge/backend/.env.production
ExecStart=/opt/skillforge/venv/bin/gunicorn \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8001 \
  --timeout 60 \
  --access-logfile /var/log/skillforge/access.log \
  --error-logfile /var/log/skillforge/error.log \
  app.main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create log directory
sudo mkdir -p /var/log/skillforge
sudo chown ubuntu:ubuntu /var/log/skillforge

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable skillforge
sudo systemctl start skillforge

# Check status
sudo systemctl status skillforge
```

**Task 2: Configure Nginx as Reverse Proxy**
```bash
# Create Nginx config
sudo tee /etc/nginx/conf.d/skillforge.conf > /dev/null << 'EOF'
upstream skillforge_backend {
    server 127.0.0.1:8001;
    keepalive 32;
}

# Redirect HTTP to HTTPS (handled by ALB)
# Nginx just proxies to Gunicorn

server {
    listen 80 default_server;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://skillforge_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        proxy_pass http://skillforge_backend/api/v1/health;
        access_log off;
    }
}
EOF

# Test Nginx config
sudo nginx -t

# Enable and restart
sudo systemctl enable nginx
sudo systemctl restart nginx
```

**Expected Outcome:** Backend running via Gunicorn, proxied by Nginx

---

### Step 8.5: Deploy Frontend to S3 + CloudFront

**Task 1: Build Frontend**
```bash
# On your local machine (not EC2):
cd /path/to/skillforge-global

# Set environment variables
export NEXT_PUBLIC_API_BASE="https://api.skillforge.com"
export NEXT_PUBLIC_STRIPE_KEY="pk_live_your_actual_stripe_public_key"

# Install dependencies
npm ci

# Build
npm run build

# Verify build
ls -la .next/
```

**Task 2: Push to S3**
```bash
# Upload static assets (cache for 1 year)
aws s3 sync .next/static s3://skillforge-frontend-prod/.next/static \
  --cache-control "public, max-age=31536000, immutable" \
  --delete

# Upload public files
aws s3 sync public s3://skillforge-frontend-prod/public \
  --cache-control "public, max-age=2592000"

# Upload HTML files (cache for 5 minutes)
aws s3 sync . s3://skillforge-frontend-prod \
  --cache-control "public, max-age=300" \
  --exclude ".next/*" \
  --exclude "public/*" \
  --exclude "*.ts" \
  --exclude "*.tsx" \
  --exclude "node_modules/*" \
  --include "*.html" \
  --delete
```

**Task 3: Invalidate CloudFront Cache**
```bash
# Get distribution ID
aws cloudfront list-distributions \
  --query "DistributionList.Items[?DomainName=='d111111abcdef8.cloudfront.net'].Id" \
  --output text

DIST_ID="E3ZZZZZ"

# Invalidate all files
aws cloudfront create-invalidation \
  --distribution-id $DIST_ID \
  --paths "/*"
```

**Expected Outcome:** Frontend deployed to S3 and accessible via CloudFront

---

## ✅ PHASE 9: Verification & Testing (30 minutes)

### Step 9.1: Test Backend API

**Task 1: Check Health Endpoint**
```bash
# Test directly via ALB DNS
curl http://skillforge-alb-1234567890.us-east-1.elb.amazonaws.com/api/v1/health

# Should return 200 OK

# Test via custom domain (once DNS propagates)
curl https://api.skillforge.com/api/v1/health
```

**Task 2: Test API Endpoints**
```bash
# Register user
curl -X POST https://api.skillforge.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@skillforge.com",
    "password":"TestPassword123!",
    "name":"Test User"
  }'

# Login
curl -X POST https://api.skillforge.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@skillforge.com",
    "password":"TestPassword123!"
  }'

# List courses
curl https://api.skillforge.com/api/v1x/marketplace/courses
```

**Task 3: Test Database Connection**
```bash
# SSH to EC2, test psql
psql -h skillforge-prod-db.c9akciq32.us-east-1.rds.amazonaws.com \
  -U admin \
  -d skillforge \
  -c "SELECT COUNT(*) FROM marketplace_courses;"

# Should return count of courses
```

---

### Step 9.2: Test Frontend

**Task 1: Visit Website**
```bash
# Open browser
https://skillforge.com

# Should load and show:
- Homepage
- Navigation menu
- Marketplace courses
- Login/Register buttons
```

**Task 2: Test User Journey**
```bash
# 1. Register new account
# 2. Login
# 3. Navigate to marketplace
# 4. View courses
# 5. Add course to cart
# 6. Proceed to checkout
# 7. Complete payment (use Stripe test card)
# 8. Verify order created
```

**Task 3: Test Admin Panel**
```bash
# Login as admin (email: admin@skillforge.com)
# Visit https://skillforge.com/admin
# Check:
- Dashboard metrics
- User list
- Course management
- Order history
- Payment reconciliation
```

---

### Step 9.3: Monitor Applications

**Task 1: Check Logs**
```bash
# Backend logs (on EC2)
sudo journalctl -u skillforge -f

# Or check log file
tail -f /var/log/skillforge/error.log

# Access logs
tail -f /var/log/skillforge/access.log
```

**Task 2: Check CloudWatch Metrics**
```bash
# View EC2 metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID_PROD \
  --start-time 2024-03-11T00:00:00Z \
  --end-time 2024-03-11T23:59:59Z \
  --period 300 \
  --statistics Average

# View ALB metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --start-time 2024-03-11T00:00:00Z \
  --end-time 2024-03-11T23:59:59Z \
  --period 300 \
  --statistics Average
```

---

## 🎯 Development Environment Setup

Repeat Phases 2-9 for development, but use:

**Key Differences:**
- Use `skillforge-dev-vpc` (can share with prod or separate)
- Use `skillforge-dev-db` (t3.micro, 1 AZ, fewer backups)
- Use `skillforge-backend-dev` EC2 (t3.small)
- Use `skillforge-frontend-dev` S3 bucket
- Use `dev.skillforge.com` domain
- Less restrictive security groups
- Can publicly access database for testing

---

## 📊 Resources Summary Sheet

Save these values somewhere safe:

```bash
# VPC & Networking
VPC_ID="vpc-0123456789abcdef0"
SUBNET_PUBLIC_1A="subnet-public1a"
SUBNET_PUBLIC_1B="subnet-public1b"
SUBNET_PRIVATE_1A="subnet-private1a"
SUBNET_PRIVATE_1B="subnet-private1b"

# Security Groups
SG_ALB="sg-alb"
SG_BACKEND="sg-backend"
SG_RDS="sg-rds"

# RDS Databases
RDS_ENDPOINT_PROD="skillforge-prod-db.c9akciq32.us-east-1.rds.amazonaws.com"
RDS_ENDPOINT_DEV="skillforge-dev-db.c9akciq32.us-east-1.rds.amazonaws.com"
RDS_USER="admin"
RDS_PASSWORD="Your$ecureP@ssw0rd123!"

# EC2 Instances
INSTANCE_ID_PROD="i-prod0123"
PUBLIC_IP_PROD="54.165.123.456"
INSTANCE_ID_DEV="i-dev0123"
PUBLIC_IP_DEV="54.165.123.457"

# Load Balancer
ALB_ARN="arn:aws:elasticloadbalancing:us-east-1:...:loadbalancer/app/skillforge-alb/..."
ALB_DNS="skillforge-alb-1234567890.us-east-1.elb.amazonaws.com"

# Certificate
CERT_ARN="arn:aws:acm:us-east-1:...:certificate/abc123..."

# CloudFront
CF_DOMAIN="d111111abcdef8.cloudfront.net"
DIST_ID="E3ZZZZZ"

# S3
BUCKET="skillforge-frontend-prod"

# Route 53
ZONE_ID="Z1234567890ABC"
```

---

## 🔄 Post-Deployment Checklist

- [ ] All services running and healthy
- [ ] Database seeded with demo data
- [ ] Users can register and login
- [ ] Marketplace courses visible
- [ ] Payment processing working (test transaction)
- [ ] Admin panel accessible
- [ ] Logs being written properly
- [ ] CloudWatch metrics visible
- [ ] DNS propagated (can resolve domains)
- [ ] SSL certificate valid (green lock in browser)
- [ ] Backups configured
- [ ] Monitoring alerts set up

---

**Total Time: 4-6 hours for complete production + dev setup**

All resources created, tested, and ready for production traffic!
