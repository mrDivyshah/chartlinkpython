#!/usr/bin/env bash

# Update packages
apt-get update

# Install Chromium browser and its dependencies
apt-get install -y chromium chromium-driver

# Verify installation
echo "Chromium version:"
chromium --version
echo "Chromedriver version:"
chromedriver --version
