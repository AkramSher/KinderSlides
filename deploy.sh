#!/bin/bash

# KinderSlides Deployment Script
# This script helps deploy KinderSlides to your own server

echo "🎓 KinderSlides Deployment Script"
echo "================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ Please don't run this script as root. Use your regular user account."
   exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    echo "   Install with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

if ! command_exists git; then
    echo "❌ Git is required but not installed."
    echo "   Install with: sudo apt install git"
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Get deployment information
read -p "🌐 Enter your domain name (e.g., kinderslides.com): " DOMAIN
read -p "📁 Enter deployment directory (default: /var/www/kinderslides): " DEPLOY_DIR
DEPLOY_DIR=${DEPLOY_DIR:-/var/www/kinderslides}

read -p "🔑 Enter your Pixabay API key: " PIXABAY_KEY
read -p "🤖 Enter your OpenAI API key: " OPENAI_KEY

# Generate random session secret
SESSION_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

echo ""
echo "🚀 Starting deployment..."

# Create deployment directory
echo "📁 Creating deployment directory..."
sudo mkdir -p "$DEPLOY_DIR"
sudo chown $USER:$USER "$DEPLOY_DIR"

# Copy files
echo "📄 Copying application files..."
cp -r . "$DEPLOY_DIR/"
cd "$DEPLOY_DIR"

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r deployment_requirements.txt

# Create environment file
echo "⚙️  Creating environment configuration..."
cat > .env << EOF
# API Keys
PIXABAY_API_KEY=$PIXABAY_KEY
OPENAI_API_KEY=$OPENAI_KEY

# Security
SESSION_SECRET=$SESSION_SECRET

# Optional: Database (uncomment if using PostgreSQL)
# DATABASE_URL=postgresql://username:password@localhost/kinderslides
EOF

# Set proper permissions
echo "🔒 Setting file permissions..."
chmod 600 .env
chmod +x deploy.sh

# Test the application
echo "🧪 Testing application..."
if python3 -c "from main import app; print('✅ App imports successfully')"; then
    echo "✅ Application test passed!"
else
    echo "❌ Application test failed. Please check the logs."
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your web server (Nginx/Apache) to proxy to port 5000"
echo "2. Set up a process manager (systemd/supervisor) to run the app"
echo "3. Configure SSL certificate for HTTPS"
echo "4. Test your domain: http://$DOMAIN"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo ""
echo "🚀 To start the application manually:"
echo "   cd $DEPLOY_DIR"
echo "   source venv/bin/activate" 
echo "   gunicorn --bind 0.0.0.0:5000 main:app"
echo ""
echo "🌐 Your application will be available at: http://$DOMAIN"