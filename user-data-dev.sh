#!/bin/bash

# User Data Script for Development EC2 Instance
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
  postgresql-client \
  htop \
  vim \
  tmux \
  build-essential \
  libpq-dev \
  nodejs \
  npm

# Create application directory
mkdir -p /opt/skillforge
chown ubuntu:ubuntu /opt/skillforge

# Install Docker
curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
bash /tmp/get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create log directory
mkdir -p /var/log/skillforge
chown ubuntu:ubuntu /var/log/skillforge

# Setup Nginx (development)
cat > /etc/nginx/conf.d/skillforge-dev.conf << 'EOF'
upstream skillforge_backend {
    server 127.0.0.1:8001;
    keepalive 32;
}

server {
    listen 80 default_server;
    server_name _;

    location / {
        proxy_pass http://skillforge_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://skillforge_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
EOF

# Enable Nginx
systemctl enable nginx
systemctl start nginx

# Setup PM2 for Node.js development
npm install -g pm2

# Create systemd service for development backend (runs hotreload)
cat > /etc/systemd/system/skillforge-dev.service << 'EOF'
[Unit]
Description=SkillForge Development Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/skillforge/backend
Environment="PATH=/opt/skillforge/venv/bin"
EnvironmentFile=/opt/skillforge/backend/.env.development
ExecStart=/opt/skillforge/venv/bin/uvicorn \
  --host 127.0.0.1 \
  --port 8001 \
  --reload \
  app.main:app

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Development setup complete
echo "EC2 development user data script completed successfully"
echo "Ready for development deployment"
