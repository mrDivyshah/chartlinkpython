#!/usr/bin/env bash

# Update and install Chromium and its dependencies
apt-get update
apt-get install -y chromium chromium-driver

# Verify installation
echo "Chromium version:"
chromium --version
