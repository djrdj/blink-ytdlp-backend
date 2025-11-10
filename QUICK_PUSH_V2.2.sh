#!/bin/bash
# QUICK PUSH V2.2 - Built-in Custom Extractors
# Koristiti na lokalnoj mašini

echo "🚀 Push V2.2 (built-in custom extractors) na GitHub..."

cd /path/to/your/blink-ytdlp-backend

# Fetch i push
git fetch origin
git push origin main

echo "✅ Push završen! Railway će deploy-ovati v2.2 za 5-10 minuta."
echo "🌐 URL: https://blink-ytdlp-backend-production.up.railway.app/"
echo ""
echo "🧪 Test sa TikTok/Instagram linkom:"
echo 'curl -X POST https://blink-ytdlp-backend-production.up.railway.app/extract \'
echo '  -H "Content-Type: application/json" \'
echo '  -d "{\"url\": \"https://www.tiktok.com/@user/video/REAL_ID\", \"supabase_url\": \"test\", \"supabase_key\": \"test\"}"'
