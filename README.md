# StormCommand - Glass Strategies Lead Generation Dashboard

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run locally:
```bash
python app.py
```

3. Access at http://localhost:5000

## Digital Ocean Deployment

1. Create a droplet with Ubuntu 22.04
2. SSH into the droplet
3. Clone the repository
4. Run the deployment script:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Features

- **Dashboard**: Stats overview and hurricane risk map
- **100 Apps Grid**: 50 cities + 50 business categories
- **Email Generator**: AI-powered personalized outreach
- **Reports**: Lead analytics and CSV export
- **About**: Implementation details and roadmap

## Active Apps (Live Now)
- Houston: https://houston-glass.stormcommand.com
- NC Architects: https://nc-architects-glass.stormcommand.com
- Hotels: https://hotels-glass.stormcommand.com

## Environment Variables

Create a `.env` file with:
```
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## Production

Use gunicorn for production:
```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 wsgi:app
```