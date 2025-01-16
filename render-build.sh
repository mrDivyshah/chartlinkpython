#!/usr/bin/env bash

# Update package lists and install Chromium and Chromium driver
apt-get update && apt-get install -y chromium chromium-driver

# Verify installation
echo "Chromium version:"
chromium --version
