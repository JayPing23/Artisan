# Oracle Cloud Free Tier Deployment Guide

Oracle Cloud Free Tier is perfect for hosting Artisan! You get:
- **2 AMD-based Compute VMs** with 1/8 OCPU and 1 GB memory each
- **4 ARM-based Compute VMs** with 24 GB memory each
- **200 GB total storage**
- **10 TB data transfer**
- **Always Free** (no expiration)

## 🏗️ Recommended Architecture

For optimal performance on Oracle Free Tier, we'll use:
- **1 ARM VM (24GB RAM)** - Main application server
- **Block Storage** - For persistent model storage
- **Load Balancer** - For SSL termination and routing

## 📋 Prerequisites

1. **Oracle Cloud Account** - Sign up at [cloud.oracle.com](https://cloud.oracle.com)
2. **SSH Key Pair** - For secure server access
3. **Domain Name** (optional) - For custom URL

## 🚀 Step-by-Step Deployment

### Step 1: Create Oracle Cloud Infrastructure

1. **Log into Oracle Cloud Console**
   - Go to [cloud.oracle.com](https://cloud.oracle.com)
   - Navigate to Compute → Instances

2. **Create a New Instance**
   ```bash
   # Instance Details
   Name: artisan-app
   Image: Canonical Ubuntu 22.04
   Shape: VM.Standard.A1.Flex (ARM-based, 24GB RAM)
   OCPU: 4
   Memory: 24 GB
   ```

3. **Network Configuration**
   ```bash
   # Virtual Cloud Network
   VCN: Create new VCN
   Subnet: Public subnet
   Security List: Allow HTTP (80), HTTPS (443), SSH (22)
   ```

4. **Add Security Rules**
   ```bash
   # Ingress Rules
   Source: 0.0.0.0/0, Port: 80 (HTTP)
   Source: 0.0.0.0/0, Port: 443 (HTTPS)
   Source: 0.0.0.0/0, Port: 22 (SSH)
   ```

### Step 2: Connect to Your Instance

```bash
# SSH into your instance
ssh ubuntu@YOUR_INSTANCE_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for group changes
exit
ssh ubuntu@YOUR_INSTANCE_IP
```

### Step 3: Deploy Artisan

```bash
# Clone your repository
git clone <your-repo-url>
cd Artisan

# Create production docker-compose file
cp docker-compose.yml docker-compose.prod.yml
```

### Step 4: Configure Production Settings

Create a production-optimized docker-compose file:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - artisan_network

  ollama:
    image: ollama/ollama:latest
    ports:
      - "127.0.0.1:11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 16G
    networks:
      - artisan_network

  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "80:8000"
    depends_on:
      - redis
      - ollama
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - model_data:/app/models
    restart: unless-stopped
    networks:
      - artisan_network

  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    depends_on:
      - redis
      - ollama
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - model_data:/app/models
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 6G
    networks:
      - artisan_network

volumes:
  redis_data:
  ollama_data:
  model_data:

networks:
  artisan_network:
    driver: bridge
```

### Step 5: Start the Application

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up --build -d

# Install the AI model
docker-compose -f docker-compose.prod.yml exec ollama ollama pull codellama

# Check service status
docker-compose -f docker-compose.prod.yml ps
```

### Step 6: Configure Nginx (Optional)

For better performance and SSL support:

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/artisan
```

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/artisan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 SSL Configuration (Recommended)

### Using Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d YOUR_DOMAIN

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Monitor resource usage
htop
docker stats
```

### Backup Strategy

```bash
# Backup models
docker run --rm -v artisan_model_data:/data -v $(pwd):/backup alpine tar czf /backup/models-backup.tar.gz -C /data .

# Backup Ollama models
docker run --rm -v artisan_ollama_data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-backup.tar.gz -C /data .
```

### Update Process

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up --build -d
```

## 💰 Cost Optimization

### Oracle Free Tier Limits

- **Always Free**: 2 AMD VMs (1/8 OCPU, 1GB RAM each)
- **Always Free**: 4 ARM VMs (24GB RAM each)
- **Storage**: 200GB total
- **Bandwidth**: 10TB/month

### Resource Allocation

```yaml
# Optimized for Oracle Free Tier
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 16G  # Most of available RAM
          cpus: '3.0'  # 3 OCPUs

  worker:
    deploy:
      resources:
        limits:
          memory: 6G   # Remaining RAM
          cpus: '1.0'  # 1 OCPU

  web:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

## 🚨 Troubleshooting

### Common Issues

**Out of Memory**
```bash
# Check memory usage
free -h
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

**Ollama Model Issues**
```bash
# Check model status
docker-compose -f docker-compose.prod.yml exec ollama ollama list

# Reinstall model
docker-compose -f docker-compose.prod.yml exec ollama ollama rm codellama
docker-compose -f docker-compose.prod.yml exec ollama ollama pull codellama
```

**Port Conflicts**
```bash
# Check port usage
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Kill conflicting processes
sudo pkill -f nginx
sudo pkill -f apache
```

## 📈 Performance Tips

1. **Use ARM Instances** - Better price/performance ratio
2. **Enable Swap** - For memory-intensive operations
3. **Use SSD Storage** - Faster model generation
4. **Monitor Resources** - Stay within free tier limits
5. **Optimize Images** - Use multi-stage Docker builds

## 🔗 Useful Commands

```bash
# Quick status check
docker-compose -f docker-compose.prod.yml ps

# View real-time logs
docker-compose -f docker-compose.prod.yml logs -f web

# Restart specific service
docker-compose -f docker-compose.prod.yml restart worker

# Update application
git pull && docker-compose -f docker-compose.prod.yml up --build -d

# Backup everything
tar czf artisan-backup-$(date +%Y%m%d).tar.gz .
```

---

**Your Artisan instance will be available at:** `http://YOUR_INSTANCE_IP`

**For SSL:** `https://YOUR_DOMAIN` 