#!/usr/bin/env bash

# Update system packages
apt-get update

# Install dependencies for Chrome/Chromium
apt-get install -y wget unzip apt-transport-https curl software-properties-common
apt-get install -y libnss3 libxss1 libappindicator1 libindicator7 libfontconfig1 libdbus-glib-1-2
apt-get install -y libasound2 libatk1.0-0 libpangocairo-1.0-0 libcups2 libxcomposite1 libxrandr2
apt-get install -y libgconf-2-4 libpango1.0-0 libxdamage1 libxext6 libxi6 xdg-utils

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y
rm google-chrome-stable_current_amd64.deb

# Verify Chrome installation
google-chrome --version
