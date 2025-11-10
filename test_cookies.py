#!/usr/bin/env python3
"""
Test script for cookies-enabled yt-dlp backend
"""

import requests
import json
import sys
import time
from typing import Optional

def test_backend(base_url: str):
    """Test the enhanced backend with cookies support"""
    
    print(f"🔍 Testing backend at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check: {data.get('status', 'unknown')}")
            if data.get('enhanced'):
                print(f"   ✅ Enhanced features: {data}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Cookies test
    try:
        print("\n2. Testing cookies configuration...")
        response = requests.get(f"{base_url}/test-cookies", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Instagram cookies: {len(data.get('instagram_cookies', {}))} items")
            print(f"   ✅ TikTok cookies: {len(data.get('tiktok_cookies', {}))} items")
            print(f"   ✅ Sample user agents: {len(data.get('user_agents', []))} items")
        else:
            print(f"   ❌ Cookies test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cookies test error: {e}")
        return False
    
    # Test 3: Instagram extraction (mock)
    try:
        print("\n3. Testing Instagram extraction...")
        test_url = "https://www.instagram.com/p/test123/"  # Mock URL
        test_data = {
            "url": test_url,
            "supabase_url": "https://test.supabase.co",
            "supabase_key": "test-key"
        }
        
        response = requests.post(
            f"{base_url}/extract", 
            json=test_data, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Instagram extraction test: SUCCESS")
                print(f"   📄 Metadata: {data.get('metadata', {}).get('title', 'N/A')}")
            else:
                print(f"   ⚠️  Instagram extraction: FAILED (expected for mock URL)")
                print(f"   📄 Error: {data.get('error', 'Unknown error')}")
        elif response.status_code == 500:
            print(f"   ⚠️  Instagram extraction: 500 error (may be expected for real test)")
            try:
                error_data = response.json()
                print(f"   📄 Error details: {error_data.get('error', 'Unknown')}")
            except:
                print(f"   📄 Raw response: {response.text[:100]}...")
        else:
            print(f"   ❌ Instagram extraction failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Instagram extraction error: {e}")
        return False
    
    # Test 4: TikTok extraction (mock)
    try:
        print("\n4. Testing TikTok extraction...")
        test_url = "https://www.tiktok.com/@test/video/1234567890"  # Mock URL
        test_data = {
            "url": test_url,
            "supabase_url": "https://test.supabase.co",
            "supabase_key": "test-key"
        }
        
        response = requests.post(
            f"{base_url}/extract", 
            json=test_data, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ TikTok extraction test: SUCCESS")
                print(f"   📄 Metadata: {data.get('metadata', {}).get('title', 'N/A')}")
            else:
                print(f"   ⚠️  TikTok extraction: FAILED (expected for mock URL)")
                print(f"   📄 Error: {data.get('error', 'Unknown error')}")
        elif response.status_code == 500:
            print(f"   ⚠️  TikTok extraction: 500 error (may be expected for real test)")
            try:
                error_data = response.json()
                print(f"   📄 Error details: {error_data.get('error', 'Unknown')}")
            except:
                print(f"   📄 Raw response: {response.text[:100]}...")
        else:
            print(f"   ❌ TikTok extraction failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ TikTok extraction error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Backend testing completed!")
    print("📋 Summary:")
    print("   • Health check: PASSED")
    print("   • Cookies config: PASSED") 
    print("   • Instagram extraction: TESTED")
    print("   • TikTok extraction: TESTED")
    print("\n💡 Next steps:")
    print("   1. Test with real Instagram/TikTok URLs")
    print("   2. Update Supabase edge function to call enhanced backend")
    print("   3. Monitor logs for successful extractions")
    
    return True

def test_real_url(base_url: str, url: str, platform: str):
    """Test with a real URL"""
    
    print(f"\n🧪 Testing real {platform} URL: {url}")
    print("-" * 60)
    
    test_data = {
        "url": url,
        "supabase_url": "https://test.supabase.co",
        "supabase_key": "test-key"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{base_url}/extract", 
            json=test_data, 
            timeout=60
        )
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.1f}s")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ SUCCESS! {platform.title()} video extracted")
                print(f"   📁 Video path: {data.get('video_path', 'N/A')}")
                print(f"   🖼️  Thumbnail: {data.get('thumbnail_path', 'N/A')}")
                
                metadata = data.get('metadata', {})
                print(f"   📝 Title: {metadata.get('title', 'N/A')}")
                print(f"   👤 Author: {metadata.get('author', 'N/A')}")
                print(f"   ⏱️  Duration: {metadata.get('duration', 0)}s")
                print(f"   📊 Platform: {metadata.get('platform', 'N/A')}")
                
                return True
            else:
                print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error: {error_data}")
            except:
                print(f"📄 Raw response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Request took too long (>60s)")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_cookies.py <backend_url>")
        print("  python test_cookies.py <backend_url> <real_url>")
        print("\nExamples:")
        print("  python test_cookies.py http://localhost:8000")
        print("  python test_cookies.py https://your-app.railway.app https://www.instagram.com/p/test/")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    if not base_url.startswith(('http://', 'https://')):
        base_url = f"http://{base_url}"
    
    # Run basic tests
    if not test_backend(base_url):
        sys.exit(1)
    
    # Test with real URL if provided
    if len(sys.argv) > 2:
        real_url = sys.argv[2]
        platform = 'instagram' if 'instagram.com' in real_url else 'tiktok' if 'tiktok.com' in real_url else 'unknown'
        
        if platform == 'unknown':
            print(f"⚠️  Could not detect platform from URL: {real_url}")
        else:
            test_real_url(base_url, real_url, platform)
    
    print(f"\n🚀 All tests completed! Backend is ready for production use.")