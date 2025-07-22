# KinderSlides Deployment Guide

This guide explains how to deploy KinderSlides to your own domain and hosting.

## Prerequisites

- A web hosting service (VPS, shared hosting with Python support, or cloud platform)
- Your domain name
- Python 3.11+ support on your hosting
- SSH access (for VPS/dedicated hosting)

## Deployment Options

### Option 1: VPS/Dedicated Server (Recommended)

#### 1. Server Requirements
- Linux server (Ubuntu 20.04+ recommended)
- Python 3.11+
- At least 1GB RAM
- 10GB+ disk space

#### 2. Installation Steps

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.11 python3.11-pip python3.11-venv nginx supervisor -y

# Create application directory
sudo mkdir -p /var/www/kinderslides
cd /var/www/kinderslides

# Upload your code (use git, scp, or FTP)
git clone <your-repository-url> .
# OR upload files manually

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 3. Create requirements.txt
Create this file in your project root:

```
Flask==3.0.0
gunicorn==21.2.0
python-pptx==0.6.23
requests==2.31.0
openai==1.3.8
email-validator==2.1.0
flask-sqlalchemy==3.1.1
psycopg2-binary==2.9.9
```

#### 4. Environment Configuration
Create `/var/www/kinderslides/.env`:

```
# API Keys
PIXABAY_API_KEY=your_pixabay_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Security
SESSION_SECRET=your_random_secret_key_here

# Optional: Database (if using PostgreSQL)
# DATABASE_URL=postgresql://username:password@localhost/kinderslides
```

#### 5. Nginx Configuration
Create `/etc/nginx/sites-available/kinderslides`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }

    location /static {
        alias /var/www/kinderslides/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/kinderslides /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 6. Supervisor Configuration
Create `/etc/supervisor/conf.d/kinderslides.conf`:

```ini
[program:kinderslides]
command=/var/www/kinderslides/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 3 --timeout 120 main:app
directory=/var/www/kinderslides
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/kinderslides.log
environment=PATH="/var/www/kinderslides/venv/bin"
```

Start the application:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start kinderslides
```

#### 7. SSL Certificate (Recommended)
Install Let's Encrypt for free SSL:

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Option 2: Shared Hosting (cPanel/Plesk)

#### 1. Check Python Support
- Verify your hosting supports Python 3.11+
- Check if you have access to pip and virtual environments

#### 2. Upload Files
- Upload all project files to your domain's public_html folder
- Ensure file permissions are correct (755 for directories, 644 for files)

#### 3. Create Virtual Environment
```bash
cd public_html
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Configure WSGI
Create `passenger_wsgi.py` in your domain root:

```python
import sys
import os

# Add your project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import your Flask app
from main import app as application

if __name__ == "__main__":
    application.run()
```

#### 5. Environment Variables
Add to `.htaccess` or use hosting panel:

```
SetEnv PIXABAY_API_KEY your_pixabay_api_key_here
SetEnv OPENAI_API_KEY your_openai_api_key_here
SetEnv SESSION_SECRET your_random_secret_key_here
```

### Option 3: Cloud Platforms

#### Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name

# Add buildpack
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set PIXABAY_API_KEY=your_key_here
heroku config:set OPENAI_API_KEY=your_key_here
heroku config:set SESSION_SECRET=your_secret_here

# Deploy
git push heroku main
```

#### DigitalOcean App Platform
1. Create a new app from your Git repository
2. Set environment variables in the app settings
3. Deploy with one click

## Domain Configuration

### DNS Settings
Point your domain to your server:

- **A Record**: `@` → `your_server_ip`
- **CNAME**: `www` → `yourdomain.com`

### Subdomain (Optional)
Create a subdomain like `slides.yourdomain.com`:

- **A Record**: `slides` → `your_server_ip`

## Environment Variables

Make sure to set these on your hosting:

| Variable | Description | Required |
|----------|-------------|----------|
| `PIXABAY_API_KEY` | Your Pixabay API key for images | Yes |
| `OPENAI_API_KEY` | Your OpenAI API key for AI validation | Yes |
| `SESSION_SECRET` | Random secret for Flask sessions | Yes |
| `DATABASE_URL` | PostgreSQL connection (if using database) | No |

## Security Considerations

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Enable SSL/HTTPS** for production
4. **Keep dependencies updated** regularly
5. **Use strong passwords** for server access
6. **Backup your data** regularly

## Monitoring and Maintenance

### Log Files
- Application logs: `/var/log/kinderslides.log`
- Nginx logs: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`

### Updating the Application
```bash
cd /var/www/kinderslides
git pull origin main  # or upload new files
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart kinderslides
```

### Performance Optimization
- Enable gzip compression in Nginx
- Set up caching for static files
- Monitor resource usage
- Scale workers based on traffic

## Troubleshooting

### Common Issues

1. **500 Internal Server Error**
   - Check application logs
   - Verify environment variables are set
   - Ensure all dependencies are installed

2. **Images not loading**
   - Verify Pixabay API key is correct
   - Check internet connectivity from server
   - Review API rate limits

3. **AI validation not working**
   - Check OpenAI API key
   - Monitor API usage and limits
   - Review logs for specific errors

### Support Commands
```bash
# Check application status
sudo supervisorctl status kinderslides

# View logs
sudo tail -f /var/log/kinderslides.log

# Restart application
sudo supervisorctl restart kinderslides

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## Getting Help

If you encounter issues during deployment:

1. Check the logs first
2. Verify all environment variables are set correctly
3. Ensure your hosting meets the requirements
4. Contact your hosting provider for Python/Flask support

For additional help, consult your hosting provider's documentation or consider hiring a system administrator for complex deployments.