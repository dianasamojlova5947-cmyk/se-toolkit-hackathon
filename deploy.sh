#!/bin/bash

# Matrix Bot Deployment Script
# Run this script on Ubuntu 24.04

set -e

echo "=========================================="
echo "  Matrix Bot - Deployment Script"
echo "=========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please run as regular user (not root)"
    exit 1
fi

# Update system
echo "[1/6] Updating system packages..."
sudo apt-get update -qq

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "[2/6] Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    sudo usermod -aG docker $USER
    echo "Docker installed. You may need to logout/login for group changes to take effect."
else
    echo "[2/6] Docker already installed."
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "[3/6] Installing Docker Compose..."
    sudo apt-get install -y docker-compose-plugin
else
    echo "[3/6] Docker Compose already installed."
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo "[4/6] Creating .env file..."
    cp .env.example .env
    echo ""
    echo "=========================================="
    echo "  IMPORTANT: Edit .env file!"
    echo "=========================================="
    echo "1. Get your Bot Token from @BotFather"
    echo "2. Get your Telegram ID from @userinfobot"
    echo ""
    echo "Then edit .env:"
    echo "  nano .env"
    echo ""
    read -p "Press Enter after editing .env..."
else
    echo "[4/6] .env file exists."
fi

# Create necessary directories
echo "[5/6] Creating directories..."
mkdir -p data logs

# Build and run Docker container
echo "[6/6] Building and starting Docker container..."
docker-compose build
docker-compose up -d

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Bot is running in Docker container 'matrix-bot'"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f     # View logs"
echo "  docker-compose restart     # Restart bot"
echo "  docker-compose stop        # Stop bot"
echo "  docker-compose up -d       # Start bot"
echo ""
echo "Data directory: ./data"
echo "Logs directory: ./logs"
echo ""