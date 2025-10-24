# WAF Platform - Development Scripts

#!/bin/bash

# Development setup script
echo "Setting up WAF Platform for development..."

# Copy environment file
if [ ! -f .env ]; then
    cp env.example .env
    echo "Created .env file from env.example"
    echo "Please edit .env with your configuration"
fi

# Create logs directory
mkdir -p logs
echo "Created logs directory"

# Set permissions
chmod +x scripts/*.sh 2>/dev/null || true

echo "Development setup complete!"
echo "Run 'docker-compose up -d --build' to start the services"
