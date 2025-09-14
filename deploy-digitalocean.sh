#!/bin/bash

echo "================================================"
echo "   StormCommand Digital Ocean Deployment"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Digital Ocean droplet
if [ ! -f /etc/digitalocean ]; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Digital Ocean droplet${NC}"
fi

echo -e "${GREEN}Step 1: Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

echo -e "${GREEN}Step 2: Installing Python and dependencies...${NC}"
sudo apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

echo -e "${GREEN}Step 3: Creating application directory...${NC}"
sudo mkdir -p /var/www/stormcommand
sudo chown $USER:$USER /var/www/stormcommand

echo -e "${GREEN}Step 4: Setting up Python virtual environment...${NC}"
cd /var/www/stormcommand
python3 -m venv venv
source venv/bin/activate

echo -e "${GREEN}Step 5: Installing Python packages...${NC}"
pip install --upgrade pip
pip install flask gunicorn folium feedparser openai anthropic python-dotenv

echo -e "${GREEN}Step 6: Creating systemd service...${NC}"
sudo tee /etc/systemd/system/stormcommand.service > /dev/null <<EOF
[Unit]
Description=StormCommand Flask Application
After=network.target

[Service]
User=$USER
WorkingDirectory=/var/www/stormcommand
Environment="PATH=/var/www/stormcommand/venv/bin"
ExecStart=/var/www/stormcommand/venv/bin/gunicorn --workers 4 --bind unix:stormcommand.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}Step 7: Creating Nginx configuration...${NC}"
sudo tee /etc/nginx/sites-available/stormcommand > /dev/null <<'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/stormcommand/stormcommand.sock;
    }

    location /static {
        alias /var/www/stormcommand/static;
    }

    client_max_body_size 5M;
}
EOF

echo -e "${GREEN}Step 8: Enabling services...${NC}"
sudo systemctl start stormcommand
sudo systemctl enable stormcommand
sudo ln -s /etc/nginx/sites-available/stormcommand /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

echo -e "${GREEN}Step 9: Setting up firewall...${NC}"
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "================================================"
echo -e "${GREEN}Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Upload your application files to /var/www/stormcommand"
echo "2. Create .env file with your API keys"
echo "3. Update Nginx config with your domain"
echo "4. Run: sudo certbot --nginx -d your-domain.com"
echo "5. Restart services:"
echo "   sudo systemctl restart stormcommand"
echo "   sudo systemctl restart nginx"
echo "================================================"