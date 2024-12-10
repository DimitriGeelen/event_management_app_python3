#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored status messages
print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[x]${NC} $1"
}

# Function to check if a command was successful
check_status() {
    if [ $? -eq 0 ]; then
        print_status "$1"
    else
        print_error "$2"
        exit 1
    fi
}

# Make sure script is not run as root
if [ "$(id -u)" = "0" ]; then
    print_error "This script should NOT be run as root"
    print_warning "Please run without sudo"
    exit 1
fi

# Welcome message
echo "================================================================="
echo "Event Management Application Installation Script"
echo "================================================================="
echo

# Check if running on Ubuntu 24.04
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$VERSION_ID" != "24.04" ]; then
        print_warning "This script is designed for Ubuntu 24.04. You're running: $PRETTY_NAME"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Update package list and install required packages
print_status "Updating package list and installing required packages..."
sudo apt update
check_status "Package list updated" "Failed to update package list"

sudo apt install -y python3-venv python3-pip
check_status "Required packages installed" "Failed to install required packages"

# Create and activate virtual environment
print_status "Creating virtual environment..."
python3 -m venv .venv
check_status "Virtual environment created" "Failed to create virtual environment"

print_status "Activating virtual environment..."
source .venv/bin/activate
check_status "Virtual environment activated" "Failed to activate virtual environment"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip
check_status "Pip upgraded" "Failed to upgrade pip"

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt
check_status "Dependencies installed" "Failed to install dependencies"

# Create necessary directories
print_status "Creating upload directory..."
mkdir -p app/static/uploads
check_status "Upload directory created" "Failed to create upload directory"

# Set correct permissions for uploads directory
print_status "Setting correct permissions for uploads directory..."
chmod 755 app/static/uploads
check_status "Permissions set" "Failed to set permissions"

# Initialize the database
print_status "Initializing database..."
python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
EOF
check_status "Database initialized" "Failed to initialize database"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')" > .env
    check_status ".env file created with random secret key" "Failed to create .env file"
fi

# Configuration for LAN access
print_status "Checking firewall status..."
if sudo ufw status | grep -q "Status: active"; then
    print_status "Configuring firewall to allow port 5000..."
    sudo ufw allow 5000/tcp
    check_status "Firewall configured" "Failed to configure firewall"
else
    print_warning "Firewall is not active. No configuration needed."
fi

# Display IP addresses
echo "\nSystem IP Addresses:"
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1'

# Installation complete
echo "\n================================================================="
print_status "Installation completed successfully!"
echo "================================================================="
echo -e "\nTo start the application:\n"
echo "1. Make sure you're in the project directory"
echo "2. Activate the virtual environment (if not already activated):"
echo "   source .venv/bin/activate"
echo "\n3. Start the application using either method:"
echo "   Method 1: flask run --host=0.0.0.0"
echo "   Method 2: python3 run.py"
echo "\nAccess the application at:"
echo "- Local: http://localhost:5000"
echo "- LAN: http://<your-ip-address>:5000"
echo "================================================================="
