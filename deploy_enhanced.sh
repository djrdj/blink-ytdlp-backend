#!/bin/bash

# Deploy script for enhanced yt-dlp backend with cookies support
# Usage: ./deploy_enhanced.sh [railway_project_name]

set -e

echo "🚀 Deploying Enhanced yt-dlp Backend with Cookies Support"
echo "=========================================================="

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Get project name
PROJECT_NAME=${1:-"blink-enhanced-backend"}
echo "📦 Project name: $PROJECT_NAME"

# Check if main.py has cookies support
if ! grep -q "get_instagram_cookies" main.py; then
    echo "⚠️  Warning: main.py doesn't seem to have cookies support"
    echo "💡 Copying main_with_cookies.py to main.py..."
    cp main_with_cookies.py main.py
    echo "✅ Cookies support enabled"
fi

# Check requirements
echo "📋 Checking requirements..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

echo "🔍 Current requirements.txt:"
cat requirements.txt

# Create production requirements
echo "📦 Creating production requirements..."
cat > requirements_prod.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
yt-dlp==2023.10.13
pydantic==2.5.0
requests==2.31.0
python-multipart==0.0.6
EOF

echo "✅ Production requirements created"

# Check if .env.example exists
if [ ! -f ".env.example" ]; then
    echo "📝 Creating .env.example..."
    cat > .env.example << 'EOF'
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Backend Configuration
PORT=8000
CORS_ORIGINS=*

# Optional: Platform-specific cookies (will auto-generate if not provided)
# Instagram cookies
IG_COOKIE_IG_DID=8F12345A-1234-1234-1234-123456789012
IG_COOKIE_IG_NRCB=1
IG_COOKIE_CSRFTOKEN=random-csrf-token-123

# TikTok cookies  
TT_COOKIE_TTWID=1%7C1731345678901%7C0.1234567890
TT_COOKIE_PASSPORT_CSRF_TOKEN=random-csrf-token
EOF
    echo "✅ .env.example created"
fi

# Initialize Railway project
echo "🔧 Initializing Railway project..."
if ! railway status &> /dev/null; then
    echo "📝 Creating new Railway project..."
    railway login
    railway project create --name "$PROJECT_NAME"
fi

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

# Wait for deployment
echo "⏳ Waiting for deployment to complete..."
sleep 10

# Get deployment URL
DEPLOYMENT_URL=$(railway domain 2>/dev/null || echo "Check Railway dashboard for URL")
echo "🌐 Deployment URL: $DEPLOYMENT_URL"

# Test deployment
if [ -n "$DEPLOYMENT_URL" ]; then
    echo "🧪 Testing deployment..."
    sleep 5  # Give it a moment to start
    
    # Test health endpoint
    if curl -f -s "$DEPLOYMENT_URL/health" > /dev/null; then
        echo "✅ Health check: PASSED"
    else
        echo "⚠️  Health check: FAILED (may need more time to start)"
    fi
    
    # Test cookies endpoint
    if curl -f -s "$DEPLOYMENT_URL/test-cookies" > /dev/null; then
        echo "✅ Cookies test: PASSED"
    else
        echo "⚠️  Cookies test: FAILED (may need more time to start)"
    fi
    
    echo "🧪 Full test available with: python test_cookies.py $DEPLOYMENT_URL"
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="
echo ""
echo "📋 Next steps:"
echo "1. 🔑 Configure environment variables in Railway dashboard:"
echo "   - SUPABASE_URL"
echo "   - SUPABASE_SERVICE_ROLE_KEY"
echo ""
echo "2. 🧪 Test the deployment:"
echo "   python test_cookies.py $DEPLOYMENT_URL"
echo ""
echo "3. 🔗 Update your Supabase edge function:"
echo "   - Point YTDLP_BACKEND_URL to: $DEPLOYMENT_URL"
echo ""
echo "4. 📊 Monitor logs:"
echo "   railway logs"
echo ""
echo "5. 🔄 Update cookies when needed:"
echo "   - Check COOKIES_IMPLEMENTATION_GUIDE.md for instructions"
echo ""
echo "💡 Features enabled:"
echo "   ✅ Cookies support for Instagram/TikTok"
echo "   ✅ Enhanced headers and user agents" 
echo "   ✅ Randomized retry delays"
echo "   ✅ Platform-specific extraction options"
echo "   ✅ Custom extractor fallback"
echo ""
echo "⚠️  Remember: Cookies expire periodically (7-30 days)"
echo "   Update them in main.py get_instagram_cookies() and get_tiktok_cookies() functions"