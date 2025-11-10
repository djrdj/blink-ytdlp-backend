# Custom Extractors - NO COOKIES VERSION
# Public API endpoints - Zero risk for user accounts

import requests
import json
import re
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def tiktok_oembed_extract(url: str) -> dict:
    """Extract TikTok video using oEmbed API (no cookies needed)"""
    try:
        # TikTok oEmbed endpoint
        oembed_url = f"https://www.tiktok.com/oembed?url={url}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(oembed_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract video info from oEmbed response
            return {
                "success": True,
                "method": "oembed",
                "title": data.get('title', ''),
                "author_name": data.get('author_name', ''),
                "author_url": data.get('author_url', ''),
                "video_url": data.get('thumbnail_url', ''),  # oEmbed doesn't provide video URL directly
                "thumbnail_url": data.get('thumbnail_url', ''),
                "duration": 0,
                "description": data.get('title', '')
            }
        else:
            logger.warning(f"TikTok oEmbed failed: {response.status_code}")
            return {"success": False, "error": f"oEmbed failed: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"TikTok oEmbed error: {e}")
        return {"success": False, "error": str(e)}

def tiktok_html_extract(url: str) -> dict:
    """Extract TikTok video using HTML parsing"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Extract video URL from script tags
        video_matches = re.findall(r'"playAddr":"([^"]*)"', response.text)
        if video_matches:
            video_url = video_matches[0].replace('\\u0026', '&').replace('\\/', '/')
            
            # Extract thumbnail
            thumbnail_matches = re.findall(r'"cover":"([^"]*)"', response.text)
            thumbnail_url = thumbnail_matches[0].replace('\\u0026', '&').replace('\\/', '/') if thumbnail_matches else ''
            
            # Extract title and author
            title_match = re.findall(r'"desc":"([^"]*)"', response.text)
            author_match = re.findall(r'"uniqueId":"([^"]*)"', response.text)
            
            return {
                "success": True,
                "method": "html_parsing",
                "title": title_match[0] if title_match else '',
                "author_name": author_match[0] if author_match else '',
                "video_url": video_url,
                "thumbnail_url": thumbnail_url,
                "duration": 0,
                "description": title_match[0] if title_match else ''
            }
        else:
            return {"success": False, "error": "Could not find video URL in HTML"}
            
    except Exception as e:
        logger.error(f"TikTok HTML extraction error: {e}")
        return {"success": False, "error": str(e)}

def instagram_oembed_extract(url: str) -> dict:
    """Extract Instagram video using oEmbed API (no cookies needed)"""
    try:
        # Facebook oEmbed API for Instagram
        oembed_url = f"https://graph.facebook.com/v18.0/instagram_oembed?url={url}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(oembed_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                "success": True,
                "method": "oembed",
                "title": data.get('title', ''),
                "author_name": data.get('author_name', ''),
                "author_url": data.get('author_url', ''),
                "video_url": data.get('thumbnail_url', ''),
                "thumbnail_url": data.get('thumbnail_url', ''),
                "duration": 0,
                "description": data.get('title', '')
            }
        else:
            logger.warning(f"Instagram oEmbed failed: {response.status_code}")
            return {"success": False, "error": f"oEmbed failed: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Instagram oEmbed error: {e}")
        return {"success": False, "error": str(e)}

def instagram_html_extract(url: str) -> dict:
    """Extract Instagram video using HTML parsing"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.instagram.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Try to extract JSON data from script tags
        json_matches = re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>', response.text)
        
        for match in json_matches:
            try:
                data = json.loads(match)
                if 'video' in data:
                    return {
                        "success": True,
                        "method": "json_ld",
                        "title": data.get('name', ''),
                        "author_name": data.get('author', {}).get('name', ''),
                        "video_url": data.get('video', {}).get('url', ''),
                        "thumbnail_url": data.get('thumbnailUrl', ''),
                        "duration": 0,
                        "description": data.get('description', '')
                    }
            except:
                continue
        
        # Fallback: try to find video URL in meta tags
        video_meta = re.search(r'<meta[^>]*property="og:video"[^>]*content="([^"]*)"', response.text)
        if video_meta:
            video_url = video_meta.group(1)
            
            # Extract title from meta tags
            title_meta = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', response.text)
            title = title_meta.group(1) if title_meta else ''
            
            return {
                "success": True,
                "method": "meta_tags",
                "title": title,
                "author_name": '',
                "video_url": video_url,
                "thumbnail_url": '',
                "duration": 0,
                "description": title
            }
        
        return {"success": False, "error": "Could not find video URL in Instagram page"}
        
    except Exception as e:
        logger.error(f"Instagram HTML extraction error: {e}")
        return {"success": False, "error": str(e)}

def custom_extract_video(url: str, platform: str) -> dict:
    """Main custom extraction function - tries multiple methods without cookies"""
    
    logger.info(f"Custom extraction: {platform} - {url}")
    
    if platform == 'tiktok':
        # Try oEmbed first
        result = tiktok_oembed_extract(url)
        if result['success']:
            return result
        
        # Try HTML parsing as fallback
        logger.info("TikTok oEmbed failed, trying HTML parsing...")
        result = tiktok_html_extract(url)
        if result['success']:
            return result
    
    elif platform == 'instagram':
        # Try oEmbed first
        result = instagram_oembed_extract(url)
        if result['success']:
            return result
        
        # Try HTML parsing as fallback
        logger.info("Instagram oEmbed failed, trying HTML parsing...")
        result = instagram_html_extract(url)
        if result['success']:
            return result
    
    return {
        "success": False,
        "error": f"Custom extraction failed for {platform}",
        "method": "none"
    }

def create_success_response(result: dict, video_path: str, thumbnail_path: str) -> dict:
    """Create standardized success response"""
    return {
        "success": True,
        "video_path": video_path if result['success'] else None,
        "thumbnail_path": thumbnail_path if result['success'] else None,
        "metadata": {
            "title": result.get('title', ''),
            "description": result.get('description', ''),
            "author_name": result.get('author_name', ''),
            "duration": result.get('duration', 0),
            "video_url": result.get('video_url', ''),
            "thumbnail_url": result.get('thumbnail_url', ''),
            "extraction_method": result.get('method', 'unknown')
        },
        "extraction_method": result.get('method', 'unknown')
    }