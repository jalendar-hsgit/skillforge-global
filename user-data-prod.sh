#!/bin/bash

# User Data Script for Production EC2 Instance
# This runs automatically on instance launch

set -e
set -x

# Log output
exec > >(tee /var/log/user-data.log)
exec 2>&1

# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y \
  python3.11 \
  python3-pip \
  python3-venv \
  git \
  curl \
  wget \
  nginx \
  certbot \
  python3-certbot-nginx \
  htop \
  vim \
  tmux \
  build-essential \
  libpq-dev

# Create application directory
mkdir -p /opt/skillforge
chown ubuntu:ubuntu /opt/skillforge

# Install Docker (optional)
curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
bash /tmp/get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb

# Create log directory with proper permissions
mkdir -p /var/log/skillforge
chown ubuntu:ubuntu /var/log/skillforge
chmod 755 /var/log/skillforge

# Create systemd service for application
cat > /etc/systemd/system/skillforge.service << 'EOF'
[Unit]
Description=SkillForge FastAPI Backend
After=network.target

[Service]
Type=notify
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

# Resource limits
MemoryMax=2G
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
cat > /etc/nginx/conf.d/skillforge.conf << 'EOF'
upstream skillforge_backend {
    server 127.0.0.1:8001;
    keepalive 32;
}

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

# Enable and start Nginx
systemctl enable nginx
systemctl start nginx

# System setup complete
echo "EC2 user data script completed successfully"
