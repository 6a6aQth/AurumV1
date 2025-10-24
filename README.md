# Web Application Firewall (WAF) Platform

A production-ready Web Application Firewall platform designed for single admin management. This WAF acts as a reverse proxy between the public internet and your protected websites, providing comprehensive security inspection and monitoring.

## 🚀 Features

### Core Security Features
- **SQL Injection Protection** - Detects and blocks SQL injection attempts
- **XSS Attack Prevention** - Prevents Cross-Site Scripting attacks
- **Command Injection Protection** - Blocks command injection attempts
- **Path Traversal Prevention** - Prevents directory traversal attacks
- **Malformed Request Detection** - Identifies and blocks malformed requests
- **Suspicious Header Analysis** - Analyzes headers for malicious content
- **File Extension Filtering** - Blocks dangerous file extensions
- **Rate Limiting** - Configurable rate limiting per IP address

### Admin Dashboard
- **Single Admin Mode** - No user registration, password-only authentication
- **Domain Management** - Add, edit, and remove protected domains
- **Real-time Monitoring** - Live dashboard with security statistics
- **Security Logs** - Detailed logs of all blocked requests
- **Analytics** - Attack statistics and trends
- **CSV Export** - Export security logs for analysis

### Architecture
- **Backend**: FastAPI with Python
- **Frontend**: React with TailwindCSS
- **Database**: PostgreSQL
- **Reverse Proxy**: Nginx
- **Caching**: Redis for rate limiting
- **Containerization**: Docker + Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- DigitalOcean Droplet (or any VPS)
- Domain name (optional, for SSL)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd aurumV1
```

### 2. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp env.example .env
```

Edit `.env` with your settings:

```env
# Database Configuration
DB_PASSWORD=your_secure_db_password_here
DATABASE_URL=postgresql://waf_user:your_secure_db_password_here@db:5432/waf_db

# Admin Configuration
ADMIN_PASSWORD=your_secure_admin_password_here

# Security
SECRET_KEY=your-secret-key-change-this-to-something-random

# Redis Configuration
REDIS_URL=redis://redis:6379

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
```

### 3. Build and Start Services

```bash
docker-compose up -d --build
```

This will start all services:
- PostgreSQL database
- FastAPI backend
- React frontend
- Nginx reverse proxy
- Redis cache

### 4. Access the Admin Dashboard

Open your browser and navigate to:
- **HTTP**: `http://your-server-ip`
- **HTTPS**: `https://your-server-ip` (if SSL is configured)

Login with your admin password configured in the `.env` file.

## 🔧 Configuration

### Adding Protected Domains

1. Log into the admin dashboard
2. Navigate to "Domain Management"
3. Click "Add Domain"
4. Fill in the domain details:
   - **Domain Name**: The domain you want to protect (e.g., `example.com`)
   - **Target URL**: The backend URL where traffic should be forwarded
   - **Security Level**: Choose from Relaxed, Moderate, or Strict
   - **Rate Limit**: Requests per hour limit
   - **Active**: Enable/disable the domain

### Security Levels

- **Relaxed**: Basic protection with minimal false positives
- **Moderate**: Balanced protection (recommended)
- **Strict**: Maximum protection with higher false positive risk

### Rate Limiting

Configure rate limits per domain:
- Default: 1000 requests per hour
- Adjustable per domain
- Uses Redis for distributed rate limiting

## 🔒 Security Features

### Attack Detection Patterns

The WAF detects various attack patterns:

#### SQL Injection
- Detects common SQL keywords and patterns
- Blocks UNION-based attacks
- Prevents database manipulation attempts

#### XSS Attacks
- Detects script injection attempts
- Blocks JavaScript execution
- Prevents iframe and object injections

#### Command Injection
- Detects shell command patterns
- Blocks system command execution
- Prevents code injection attempts

#### Path Traversal
- Detects directory traversal attempts
- Blocks `../` patterns
- Prevents unauthorized file access

### Request Analysis

Every request is analyzed for:
- Request size limits (10MB default)
- Malformed headers
- Suspicious user agents
- Null byte injections
- URL length limits

## 📊 Monitoring and Logging

### Dashboard Statistics

The admin dashboard provides:
- Total and active domains
- Request statistics
- Blocked request counts
- Recent attack trends
- Top attack types

### Security Logs

All security events are logged with:
- Timestamp
- Client IP address
- Request method and path
- Block reason
- User agent
- Additional details

### Log Export

Export security logs to CSV for:
- External analysis
- Compliance reporting
- Security audits

## 🚀 DigitalOcean Deployment

### 1. Create a Droplet

- Choose Ubuntu 20.04 or newer
- Minimum 2GB RAM, 2 CPU cores
- 50GB SSD storage

### 2. Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

### 3. Deploy the WAF

```bash
# Clone the repository
git clone <repository-url>
cd aurumV1

# Configure environment
cp env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d --build
```

### 4. Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

### 5. SSL Configuration (Optional)

For production use with SSL:

1. Obtain SSL certificates (Let's Encrypt recommended)
2. Place certificates in `nginx/ssl/` directory
3. Uncomment SSL configuration in `nginx/conf.d/default.conf`
4. Update `REACT_APP_API_URL` to use HTTPS

## 🔧 Maintenance

### Updating the WAF

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Database Backup

```bash
# Backup database
docker-compose exec db pg_dump -U waf_user waf_db > backup.sql

# Restore database
docker-compose exec -T db psql -U waf_user waf_db < backup.sql
```

### Log Rotation

Logs are stored in the `logs/` directory. Configure log rotation:

```bash
# Install logrotate
sudo apt install logrotate

# Create logrotate config
sudo nano /etc/logrotate.d/waf
```

Add:
```
/home/user/aurumV1/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

## 🐛 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check logs
docker-compose logs

# Check specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx
```

#### Database Connection Issues
```bash
# Check database status
docker-compose exec db psql -U waf_user -d waf_db -c "SELECT 1;"
```

#### Frontend Not Loading
- Check if `REACT_APP_API_URL` is correct
- Verify backend is running on port 8000
- Check browser console for errors

#### Rate Limiting Issues
```bash
# Check Redis status
docker-compose exec redis redis-cli ping
```

### Performance Optimization

#### Increase Resources
- Upgrade Droplet to higher specs
- Add more CPU cores and RAM
- Use SSD storage

#### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_security_logs_timestamp ON security_logs(timestamp);
CREATE INDEX idx_security_logs_client_ip ON security_logs(client_ip);
CREATE INDEX idx_security_logs_reason ON security_logs(reason);
```

#### Nginx Optimization
- Enable gzip compression
- Configure caching headers
- Optimize worker processes

## 📈 Scaling

### Horizontal Scaling

To handle more traffic:

1. **Load Balancer**: Use DigitalOcean Load Balancer
2. **Multiple Instances**: Deploy multiple WAF instances
3. **Database Clustering**: Use PostgreSQL clustering
4. **Redis Cluster**: Implement Redis clustering

### Vertical Scaling

- Upgrade Droplet resources
- Use dedicated database instances
- Implement CDN for static assets

## 🔐 Security Best Practices

### Production Deployment

1. **Change Default Passwords**: Use strong, unique passwords
2. **Enable SSL**: Always use HTTPS in production
3. **Regular Updates**: Keep all components updated
4. **Monitor Logs**: Regularly review security logs
5. **Backup Data**: Implement regular database backups
6. **Firewall Rules**: Configure proper firewall rules
7. **Access Control**: Limit SSH access to specific IPs

### Environment Security

```bash
# Secure the server
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Disable root login
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart ssh
```

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review Docker logs
3. Check GitHub issues
4. Create a new issue with detailed information

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🎯 Roadmap

Future features planned:

- [ ] Multi-admin support
- [ ] API for remote management
- [ ] Auto SSL provisioning
- [ ] Stripe integration
- [ ] Advanced analytics
- [ ] Custom rule engine
- [ ] Integration with threat intelligence feeds
- [ ] Mobile app for monitoring

---

**Built with ❤️ for secure web applications**
