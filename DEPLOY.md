# StormCommand Deployment Guide

## Quick Deploy to Digital Ocean

### 1. Create Digital Ocean Droplet
- Ubuntu 22.04 LTS
- Basic plan ($6-12/month)
- Choose datacenter closest to you
- Add SSH key

### 2. Connect to Droplet
```bash
ssh root@your-droplet-ip
```

### 3. Clone Repository
```bash
cd /var/www
git clone https://github.com/your-username/StormCommand.git stormcommand
cd stormcommand
```

### 4. Run Deployment Script
```bash
chmod +x deploy-digitalocean.sh
./deploy-digitalocean.sh
```

### 5. Create Environment File
```bash
nano .env
```

Add your keys:
```
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

### 6. Update Domain
Edit nginx config:
```bash
sudo nano /etc/nginx/sites-available/stormcommand
```

Replace `your-domain.com` with your actual domain.

### 7. Get SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

### 8. Restart Services
```bash
sudo systemctl restart stormcommand
sudo systemctl restart nginx
```

## Your app is now live! 🚀

### Useful Commands

Check status:
```bash
sudo systemctl status stormcommand
```

View logs:
```bash
sudo journalctl -u stormcommand -f
```

Update code:
```bash
cd /var/www/stormcommand
git pull
sudo systemctl restart stormcommand
```

## Domain Setup

Point these domains to your droplet IP:
- stormcommand.yourdomain.com (main dashboard)
- houston-glass.yourdomain.com (future)
- nc-architects-glass.yourdomain.com (future)
- hotels-glass.yourdomain.com (future)