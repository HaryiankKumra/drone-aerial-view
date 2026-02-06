# AWS EC2 Deployment Guide
## Campus Guardian Drone - Production Deployment on Amazon EC2

---

## 🎯 Deployment Overview

This guide walks you through deploying the Campus Guardian Drone system on AWS EC2 with:
- ✅ Automated deployment script
- ✅ Docker containerization
- ✅ SSL/HTTPS support (optional)
- ✅ Auto-restart on failure
- ✅ Domain name configuration (optional)
- ✅ Cost optimization tips

---

## 💰 AWS Cost Estimate

### Recommended Instance: **t3.medium** (2 vCPU, 4GB RAM)
- **On-Demand**: ~$0.042/hour = **$30/month**
- **Reserved (1-year)**: ~$20/month
- **Spot Instance**: ~$12-15/month (may be interrupted)

### Storage: **30GB gp3 SSD**
- ~$2.40/month

### Data Transfer: **Free Tier** = 100GB/month free

**Total Cost**: ~$32-35/month for production deployment

---

## 📋 Prerequisites

### 1. AWS Account
- Sign up at https://aws.amazon.com
- Add payment method
- Complete identity verification

### 2. Local Tools
```bash
# Install AWS CLI (macOS)
brew install awscli

# Or download from: https://aws.amazon.com/cli/

# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)
```

### 3. SSH Key Pair
```bash
# Create SSH key for EC2 access
ssh-keygen -t rsa -b 4096 -f ~/.ssh/drone_aws_key
# Press Enter for no passphrase (or set one)
```

---

## 🚀 Quick Deployment (Automated)

### Step 1: Download Deployment Script

```bash
cd "/Users/mohitkumra/Desktop/DL Notebooks/hack"

# The deploy_aws.sh script is already in your project
chmod +x deploy_aws.sh
```

### Step 2: Configure Environment Variables

```bash
# Edit .env file with production values
nano .env
```

**Required variables**:
```bash
# Cloudinary (for image storage)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Telegram (optional - for alerts)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Production settings
FLASK_ENV=production
PORT=8080
```

### Step 3: Run Deployment Script

```bash
./deploy_aws.sh
```

This will:
1. Create EC2 instance (t3.medium)
2. Configure security groups (ports 22, 80, 8080)
3. Install Docker and dependencies
4. Deploy application
5. Start server on port 8080
6. Print access URL

**After completion**, access your dashboard at:
```
http://YOUR_EC2_PUBLIC_IP:8080
```

---

## 🔧 Manual Deployment (Step-by-Step)

### Step 1: Launch EC2 Instance

#### Via AWS Console

1. **Login to AWS Console** → EC2 Dashboard
2. **Launch Instance**:
   - **Name**: `drone-guardian-server`
   - **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
   - **Instance type**: `t3.medium` (2 vCPU, 4GB RAM)
   - **Key pair**: Create new or select existing
   - **Network**: Default VPC
   - **Storage**: 30 GB gp3

3. **Configure Security Group**:
   - Name: `drone-guardian-sg`
   - **Inbound Rules**:
     - SSH (22) - Your IP
     - HTTP (80) - Anywhere (0.0.0.0/0)
     - Custom TCP (8080) - Anywhere (0.0.0.0/0)
     - HTTPS (443) - Anywhere (optional, for SSL)

4. **Launch Instance**

#### Via AWS CLI

```bash
# Create security group
aws ec2 create-security-group \
  --group-name drone-guardian-sg \
  --description "Security group for Campus Guardian Drone"

# Add inbound rules
aws ec2 authorize-security-group-ingress \
  --group-name drone-guardian-sg \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name drone-guardian-sg \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name drone-guardian-sg \
  --protocol tcp --port 8080 --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
  --image-id ami-0c7217cdde317cfec \
  --count 1 \
  --instance-type t3.medium \
  --key-name YOUR_KEY_NAME \
  --security-groups drone-guardian-sg \
  --block-device-mappings DeviceName=/dev/sda1,Ebs={VolumeSize=30}
```

### Step 2: Connect to EC2 Instance

```bash
# Get public IP from AWS Console or:
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"

# SSH into instance
ssh -i ~/.ssh/drone_aws_key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt install -y git

# Logout and login again for Docker permissions
exit
ssh -i ~/.ssh/drone_aws_key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 4: Clone and Configure Project

```bash
# Clone repository
git clone https://github.com/HaryiankKumra/drone-aerial-view.git
cd drone-aerial-view

# Create .env file
nano .env
```

**Add production environment variables**:
```bash
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
FLASK_ENV=production
PORT=8080
```

### Step 5: Deploy with Docker

```bash
# Build and start containers
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 6: Verify Deployment

```bash
# Test server locally
curl http://localhost:8080/system_status

# From your computer:
curl http://YOUR_EC2_PUBLIC_IP:8080/system_status
```

**Open browser**: `http://YOUR_EC2_PUBLIC_IP:8080`

---

## 🌐 Domain Name Setup (Optional)

### Step 1: Register Domain (or use existing)
- Recommended: Namecheap, Google Domains, Route 53

### Step 2: Configure DNS (AWS Route 53)

```bash
# Create hosted zone
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)

# Create A record pointing to EC2 IP
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "drone.yourdomain.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "YOUR_EC2_PUBLIC_IP"}]
      }
    }]
  }'
```

### Step 3: Update Nameservers
- In your domain registrar, point nameservers to Route 53 NS records

---

## 🔒 SSL/HTTPS Setup with Let's Encrypt

### Install Certbot

```bash
# SSH into EC2
sudo apt install -y certbot python3-certbot-nginx

# Install Nginx
sudo apt install -y nginx
```

### Configure Nginx Reverse Proxy

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/drone
```

**Add this configuration**:
```nginx
server {
    listen 80;
    server_name drone.yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/drone /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Get SSL Certificate

```bash
# Obtain certificate
sudo certbot --nginx -d drone.yourdomain.com

# Follow prompts (enter email, agree to ToS, etc.)
# Certbot will auto-configure HTTPS redirect
```

**Access via HTTPS**: `https://drone.yourdomain.com`

### Auto-Renew SSL

```bash
# Test renewal
sudo certbot renew --dry-run

# Renewal is automatic (systemd timer runs twice daily)
```

---

## 🔄 Auto-Start on Reboot

Docker Compose containers already restart automatically, but to ensure Docker starts on boot:

```bash
sudo systemctl enable docker
```

---

## 📊 Monitoring and Maintenance

### View Logs

```bash
# Application logs
docker-compose logs -f app

# All containers
docker-compose logs -f

# System logs
sudo journalctl -xe
```

### Check Resource Usage

```bash
# Docker stats
docker stats

# System resources
htop  # Install: sudo apt install htop
```

### Update Application

```bash
cd ~/drone-aerial-view

# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

---

## 🛡️ Security Best Practices

### 1. Restrict SSH Access

```bash
# Edit security group to allow SSH only from your IP
aws ec2 authorize-security-group-ingress \
  --group-name drone-guardian-sg \
  --protocol tcp --port 22 --cidr YOUR_IP/32

# Or via Console: EC2 → Security Groups → Edit inbound rules
```

### 2. Set Up Firewall (UFW)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Disable Root Login

```bash
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd
```

### 4. Enable Automatic Security Updates

```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 💾 Backup Strategy

### Database Backup Script

```bash
# Create backup directory
mkdir -p ~/backups

# Create backup script
nano ~/backup.sh
```

**Add**:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/backups
cd ~/drone-aerial-view

# Backup databases
docker-compose exec -T app tar czf - data/ | cat > $BACKUP_DIR/data_$DATE.tar.gz

# Backup environment
cp .env $BACKUP_DIR/.env_$DATE

# Keep only last 7 days
find $BACKUP_DIR -name "data_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
chmod +x ~/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/ubuntu/backup.sh >> /home/ubuntu/backups/backup.log 2>&1
```

### S3 Backup (Optional)

```bash
# Install AWS CLI
sudo apt install awscli

# Sync backups to S3
aws s3 sync ~/backups s3://your-backup-bucket/drone-backups/
```

---

## 📈 Scaling Options

### Vertical Scaling (Bigger Instance)

```bash
# Stop instance
aws ec2 stop-instances --instance-ids i-1234567890abcdef0

# Change instance type
aws ec2 modify-instance-attribute \
  --instance-id i-1234567890abcdef0 \
  --instance-type "{\"Value\": \"t3.large\"}"

# Start instance
aws ec2 start-instances --instance-ids i-1234567890abcdef0
```

### Load Balancer (Multiple Instances)

For high-traffic scenarios:
1. Create Application Load Balancer
2. Launch multiple EC2 instances
3. Use RDS for shared database
4. Use S3 for shared storage

---

## 🧪 Testing Deployment

### From Your Computer

```bash
# Test basic connectivity
curl http://YOUR_EC2_PUBLIC_IP:8080/system_status

# Test telemetry
curl http://YOUR_EC2_PUBLIC_IP:8080/telemetry

# Send test RPi data
curl -X POST http://YOUR_EC2_PUBLIC_IP:8080/rpi/detect \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "Test-RPi",
    "location": "Test Location",
    "timestamp": "2026-02-07T12:00:00",
    "image": "data:image/jpeg;base64,/9j/4AAQ...",
    "gps_latitude": 30.3560,
    "gps_longitude": 76.3649,
    "speed": 2.5,
    "camera_ok": true,
    "model_ok": true
  }'
```

### From Raspberry Pi

```bash
# On your RPi, run client pointing to EC2
python3 rpi_client.py \
  --server http://YOUR_EC2_PUBLIC_IP:8080 \
  --device-id RPi-Test-01 \
  --location "Test Gate"
```

---

## 🔧 Troubleshooting

### Can't Access Dashboard

```bash
# Check if server is running
docker-compose ps

# Check logs for errors
docker-compose logs app

# Verify port 8080 is open
sudo netstat -tulpn | grep 8080

# Check security group allows inbound on 8080
```

### High CPU Usage

```bash
# Check container stats
docker stats

# Limit CPU/memory in docker-compose.yml:
# resources:
#   limits:
#     cpus: '1.0'
#     memory: 2G
```

### Disk Full

```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a

# Clean old logs
sudo journalctl --vacuum-time=7d
```

---

## 💡 Cost Optimization Tips

1. **Use Reserved Instances** - Save 30-60% for 1-3 year commitment
2. **Enable EBS Optimization** - Use gp3 instead of gp2 (20% cheaper)
3. **Elastic IP** - Free if attached to running instance
4. **CloudWatch Alarms** - Set billing alerts
5. **Instance Scheduler** - Auto-stop during off-hours if not 24/7
6. **Spot Instances** - 70-90% discount (can be interrupted)

---

## ✅ Deployment Checklist

- [ ] EC2 instance launched (t3.medium recommended)
- [ ] Security group configured (ports 22, 80, 8080)
- [ ] SSH access working
- [ ] Docker and Docker Compose installed
- [ ] Repository cloned
- [ ] .env file configured with production credentials
- [ ] Docker containers running (`docker-compose ps` shows Up)
- [ ] Dashboard accessible at `http://EC2_IP:8080`
- [ ] Cloudinary configured (test image upload)
- [ ] RPi client tested (if using)
- [ ] SSL certificate installed (if using domain)
- [ ] Auto-restart configured
- [ ] Backups scheduled
- [ ] Monitoring alerts set up

---

## 📞 Next Steps

1. **Test thoroughly**: Run simulation, verify all features
2. **Connect RPi**: Deploy edge devices with rpi_client.py
3. **Configure geofencing**: Set up campus zones
4. **Test alerts**: Verify Telegram notifications (if configured)
5. **Monitor 24/7**: Check metrics, logs, uptime
6. **Scale as needed**: Add more EC2 capacity or RPi devices

---

## 🎉 Success!

Your Campus Guardian Drone system is now running on AWS EC2!

**Dashboard**: `http://YOUR_EC2_PUBLIC_IP:8080`  
**API**: See [API_REFERENCE.md](API_REFERENCE.md)  
**Support**: Check logs with `docker-compose logs -f`

---

**Estimated Setup Time**: 20-30 minutes  
**Monthly Cost**: ~$32-35 (t3.medium + 30GB storage)  
**Uptime**: 99.9%+ with Docker auto-restart
