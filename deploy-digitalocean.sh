#!/bin/bash

# DigitalOcean Deployment Script for WAF Platform
# Run this script on your DigitalOcean Droplet

set -e

echo "🚀 Deploying WAF Platform on DigitalOcean..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Create application directory
echo "📁 Setting up application directory..."
mkdir -p /opt/waf
cd /opt/waf

# Clone repository (replace with your repository URL)
echo "📥 Cloning repository..."
# git clone <your-repository-url> .

# Copy files (if running locally)
if [ -f "/home/baron/aurumV1/docker-compose.yml" ]; then
    cp -r /home/baron/aurumV1/* .
fi

# Setup environment
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "Please edit .env file with your configuration:"
    echo "nano .env"
    echo ""
    echo "Important settings to configure:"
    echo "- ADMIN_PASSWORD: Set a strong admin password"
    echo "- DB_PASSWORD: Set a secure database password"
    echo "- SECRET_KEY: Generate a random secret key"
    echo ""
    read -p "Press Enter after configuring .env file..."
fi

# Create logs directory
mkdir -p logs

# Start services
echo "🚀 Starting WAF services..."
docker-compose up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker-compose ps

# Display access information
echo ""
echo "✅ WAF Platform deployed successfully!"
echo ""
echo "🌐 Access your WAF admin dashboard at:"
echo "   http://$(curl -s ifconfig.me)"
echo ""
echo "🔐 Login with your admin password configured in .env"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update: git pull && docker-compose up -d --build"
echo ""
echo "🔧 Configuration files:"
echo "   Environment: /opt/waf/.env"
echo "   Logs: /opt/waf/logs/"
echo ""

# Setup log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/waf > /dev/null <<EOF
/opt/waf/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF

echo "🎉 Deployment complete!"
echo "Your WAF Platform is now running and ready to protect your websites!"
