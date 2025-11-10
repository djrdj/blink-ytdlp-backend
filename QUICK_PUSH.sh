#!/bin/bash
# QUICK PUSH V2.1 - Custom Extractors
# Koristiti na lokalnoj mašini

echo "🚀 Push V2.1 custom extractors na GitHub..."

cd /path/to/your/blink-ytdlp-backend

# Fetch i push
git fetch origin
git push origin main

echo "✅ Push završen! Railway će deploy-ovati v2.1 za 5-10 minuta."
echo "🌐 URL: https://blink-ytdlp-backend-production.up.railway.app/"
