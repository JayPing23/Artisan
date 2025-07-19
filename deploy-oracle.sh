#!/bin/bash

# Artisan Oracle Cloud Deployment Script
# This script automates the deployment of Artisan on Oracle Cloud Free Tier

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as ubuntu user."
   exit 1
fi

print_status "Starting Artisan deployment on Oracle Cloud..."

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing required packages..."
sudo apt install -y curl wget git htop unzip

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    print_success "Docker installed successfully"
else
    print_success "Docker already installed"
fi

# Install Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed successfully"
else
    print_success "Docker Compose already installed"
fi

# Create swap file for memory management
print_status "Setting up swap file..."
if ! swapon --show | grep -q "/swapfile"; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    print_success "Swap file created (4GB)"
else
    print_success "Swap file already exists"
fi

# Create application directory
print_status "Setting up application directory..."
mkdir -p ~/artisan
cd ~/artisan

# Check if repository exists
if [ ! -d ".git" ]; then
    print_warning "Git repository not found. Please clone your repository manually:"
    echo "git clone <your-repo-url> ."
    echo "Then run this script again."
    exit 1
fi

# Create production docker-compose file if it doesn't exist
if [ ! -f "docker-compose.prod.yml" ]; then
    print_status "Creating production docker-compose configuration..."
    cp docker-compose.yml docker-compose.prod.yml
fi

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Start Docker services
print_status "Starting Docker services..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 30

# Check service status
print_status "Checking service status..."
docker-compose -f docker-compose.prod.yml ps

# Install Ollama model
print_status "Installing Code Llama model..."
docker-compose -f docker-compose.prod.yml exec -T ollama ollama pull codellama

# Create systemd service for auto-start
print_status "Creating systemd service for auto-start..."
sudo tee /etc/systemd/system/artisan.service > /dev/null <<EOF
[Unit]
Description=Artisan 3D Generator
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/artisan
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
User=ubuntu
Group=ubuntu

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable artisan.service

# Create monitoring script
print_status "Creating monitoring script..."
cat > ~/artisan/monitor.sh << 'EOF'
#!/bin/bash
echo "=== Artisan Service Status ==="
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "=== Resource Usage ==="
docker stats --no-stream
echo ""
echo "=== Recent Logs ==="
docker-compose -f docker-compose.prod.yml logs --tail=20
EOF

chmod +x ~/artisan/monitor.sh

# Create backup script
print_status "Creating backup script..."
cat > ~/artisan/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/ubuntu/artisan/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

echo "Creating backup: artisan_backup_$DATE.tar.gz"

# Backup models
docker run --rm -v artisan_model_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/models_$DATE.tar.gz -C /data .

# Backup Ollama models
docker run --rm -v artisan_ollama_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/ollama_$DATE.tar.gz -C /data .

# Backup application files
tar czf $BACKUP_DIR/app_$DATE.tar.gz --exclude=backups --exclude=.git .

echo "Backup completed: $BACKUP_DIR/artisan_backup_$DATE.tar.gz"
EOF

chmod +x ~/artisan/backup.sh

# Create update script
print_status "Creating update script..."
cat > ~/artisan/update.sh << 'EOF'
#!/bin/bash
echo "Updating Artisan..."

# Pull latest changes
git pull origin main

# Stop services
docker-compose -f docker-compose.prod.yml down

# Rebuild and start
docker-compose -f docker-compose.prod.yml up --build -d

echo "Update completed!"
EOF

chmod +x ~/artisan/update.sh

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)

# Final status
print_success "Deployment completed successfully!"
echo ""
echo "=== Artisan is now running! ==="
echo "🌐 Public URL: http://$PUBLIC_IP"
echo "📁 Application directory: ~/artisan"
echo ""
echo "=== Useful Commands ==="
echo "📊 Monitor services: ~/artisan/monitor.sh"
echo "💾 Create backup: ~/artisan/backup.sh"
echo "🔄 Update application: ~/artisan/update.sh"
echo "📋 View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "🛑 Stop services: docker-compose -f docker-compose.prod.yml down"
echo "▶️  Start services: docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "=== Next Steps ==="
echo "1. Test the application at http://$PUBLIC_IP"
echo "2. Set up SSL certificate with Let's Encrypt (optional)"
echo "3. Configure domain name (optional)"
echo "4. Set up monitoring and alerts (optional)"
echo ""
print_success "Artisan is ready to generate 3D models! 🎨✨" 