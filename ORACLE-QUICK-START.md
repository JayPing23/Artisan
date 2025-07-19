# Oracle Cloud Quick Start 🚀

## 1. Create Oracle Cloud Account
- Go to [cloud.oracle.com](https://cloud.oracle.com)
- Sign up for **Always Free Tier**
- Verify your account (credit card required, no charges)

## 2. Launch VM Instance
```bash
# Instance Configuration
Name: artisan-app
Image: Canonical Ubuntu 22.04
Shape: VM.Standard.A1.Flex (ARM)
OCPU: 4
Memory: 24 GB
Network: Public subnet
Security: Allow HTTP(80), HTTPS(443), SSH(22)
```

## 3. Connect & Deploy
```bash
# SSH into your instance
ssh ubuntu@YOUR_INSTANCE_IP

# Download and run deployment script
wget https://raw.githubusercontent.com/your-repo/Artisan/main/deploy-oracle.sh
chmod +x deploy-oracle.sh
./deploy-oracle.sh
```

## 4. Access Your App
- **URL**: `http://YOUR_INSTANCE_IP`
- **Test**: Enter "a low-poly rocket ship" and generate!

## 🔧 Resource Allocation
- **Ollama**: 16GB RAM, 3 OCPUs
- **Worker**: 6GB RAM, 1 OCPU  
- **Web**: 1GB RAM, 0.5 OCPU
- **Redis**: 512MB RAM, 0.5 OCPU

## 📊 Monitoring
```bash
# Check status
~/artisan/monitor.sh

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Create backup
~/artisan/backup.sh
```

## 🔒 SSL Setup (Optional)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d YOUR_DOMAIN
```

## 💰 Cost: $0/month
- **Always Free** - No expiration
- **24GB RAM** - Perfect for AI workloads
- **200GB Storage** - Plenty for models
- **10TB Bandwidth** - Generous limits

---

**Need help?** See [oracle-deployment.md](oracle-deployment.md) for detailed instructions. 