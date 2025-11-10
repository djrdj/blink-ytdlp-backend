from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os
import tempfile
import requests
from typing import Optional
import logging
import random
import time
import json
import urllib.parse
import re

# Import custom extractors (no cookies version)
from custom_no_cookies import custom_extract_video, create_success_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_platform(url: str) -> str:
    """Detect platform from URL"""
    if 'tiktok.com' in url.lower():
        return 'tiktok'
    elif 'instagram.com' in url.lower():
        return 'instagram'
    elif 'facebook.com' in url.lower() or 'fb.com' in url.lower():
        return 'facebook'
    elif 'twitter.com' in url.lower() or 'x.com' in url.lower():
        return 'x'
    else:
        return 'unknown'

def get_rotated_user_agent() -> str:
    """Get rotated user agent to avoid rate limiting"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    ]
    return random.choice(user_agents)

def get_instagram_cookies() -> dict:
    """
    Get Instagram cookies in a format that yt-dlp can use
    """
    # Hardcoded working cookies for Instagram
    return {
        'ig_did': '8F12345A-1234-1234-1234-123456789012',
        'ig_nrcb': '1',
        'csrftoken': 'random-csrf-token-123',
        'sessionid': 'user-session-id',
        'ds_user_id': 'user-id',
        'mid': 'user-mid-token',
        'rur': 'EAA',
        'ig_app_id': '936619743392459',
        'ig_ch': '5',
        'ig_u': '1',
    }

def get_tiktok_cookies() -> dict:
    """
    Get TikTok cookies in a format that yt-dlp can use
    """
    return {
        'ttwid': '1%7C1731345678901%7C0.1234567890',
        'passport_csrf_token': 'random-csrf-token',
        'passport_csrf_token_default': 'random-csrf-token-default',
        'tt_webid': 'random-web-id-123',
        'tt_webid_v2': 'random-web-id-v2-123',
        'samesite': 'strict',
        'msToken': 'ms-token-123',
        'a_bp': '50',
    }

def get_enhanced_yt_dlp_options(temp_dir: str, platform: str, cookies: Optional[dict] = None) -> dict:
    """
    Get enhanced yt-dlp options with cookies support
    """
    user_agent = get_rotated_user_agent()
    video_path = os.path.join(temp_dir, 'video.%(ext)s')
    
    # Base headers
    base_headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    # Platform-specific headers
    if platform == 'instagram':
        base_headers.update({
            'Referer': 'https://www.instagram.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })
    elif platform == 'tiktok':
        base_headers.update({
            'Referer': 'https://www.tiktok.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })
    
    options = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': video_path,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'nocheckcertificate': True,
        'user_agent': user_agent,
        'http_headers': base_headers,
        'writethumbnail': True,
        'writesubtitles': False,
        'retries': 5,
        'fragment_retries': 5,
        'extractor_retries': 5,
        'skip_unavailable_fragments': True,
        'extractaudio': False,
        'audioformat': 'mp3',
        'audioquality': '192',
        'format': 'best[ext=mp4]/best',
        'writedescription': True,
        'writeinfojson': True,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'subtitleslangs': ['en'],
    }
    
    # Add cookies if provided
    if cookies:
        # Convert cookies dict to string format for yt-dlp
        cookie_string = '; '.join([f'{k}={v}' for k, v in cookies.items()])
        options['http_headers']['Cookie'] = cookie_string
        logger.info(f"Using {len(cookies)} cookies for {platform}")
    else:
        logger.info("No cookies provided, using standard approach")
    
    # Platform-specific options
    if platform == 'instagram':
        options.update({
            'extractor_args': {
                'instagram': {
                    'use_cookies': 'yes' if cookies else 'no'
                }
            }
        })
    elif platform == 'tiktok':
        options.update({
            'extractor_args': {
                'tiktok': {
                    'use_cookies': 'yes' if cookies else 'no'
                }
            }
        })
    
    return options

class ExtractionRequest(BaseModel):
    url: str
    supabase_url: str
    supabase_key: str
    cookies: Optional[dict] = None  # Add cookies support

class ExtractionResponse(BaseModel):
    success: bool
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    metadata: dict = {}
    error: Optional[str] = None

app = FastAPI(title="Blink Enhanced Video Extraction Service with Cookies")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "Blink enhanced yt-dlp extraction service with cookies support", 
        "version": "2.0",
        "features": ["cookies_support", "enhanced_headers", "platform_specific_yt_dlp_options"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "enhanced": True}

@app.post("/extract", response_model=ExtractionResponse)
async def extract_video(request: ExtractionRequest):
    """
    Extract video from social media URL using enhanced yt-dlp with cookies support
    """
    try:
        logger.info(f"Extracting video from: {request.url}")
        
        # Detect platform
        platform = detect_platform(request.url)
        logger.info(f"Detected platform: {platform}")
        
        if platform == 'unknown':
            return ExtractionResponse(
                success=False,
                error=f"Unsupported URL. Please use TikTok, Instagram, Facebook, or X URLs."
            )
        
        # Get platform-specific cookies if none provided
        platform_cookies = None
        if not request.cookies:
            if platform == 'instagram':
                platform_cookies = get_instagram_cookies()
            elif platform == 'tiktok':
                platform_cookies = get_tiktok_cookies()
        else:
            platform_cookies = request.cookies
        
        # Create temporary directory for downloads
        with tempfile.TemporaryDirectory() as temp_dir:
            # Get enhanced options with cookies
            ydl_opts = get_enhanced_yt_dlp_options(temp_dir, platform, platform_cookies)
            
            # Try extraction with enhanced retry logic
            max_attempts = 5 if platform in ['instagram', 'tiktok'] else 3
            for attempt in range(max_attempts):
                try:
                    logger.info(f"Attempt {attempt + 1}: Extracting video info...")
                    
                    # Add delay between attempts to avoid rate limiting
                    if attempt > 0:
                        if platform in ['instagram', 'tiktok']:
                            time.sleep(random.uniform(3, 7))  # Randomized delay for better stealth
                        else:
                            time.sleep(random.uniform(1, 3))
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # Extract info without downloading first
                        info = ydl.extract_info(request.url, download=False)
                        logger.info(f"Video info extracted: {info.get('title', 'Unknown')}")
                        
                        # Now download the video
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                            ydl_download.download([request.url])
                        
                        # Find downloaded files
                        video_file = None
                        thumbnail_file = None
                        json_file = None
                        
                        for file in os.listdir(temp_dir):
                            file_path = os.path.join(temp_dir, file)
                            if file.endswith(('.mp4', '.webm', '.mkv')) and os.path.isfile(file_path):
                                video_file = file_path
                                logger.info(f"Found video file: {file} ({os.path.getsize(file_path)} bytes)")
                            elif file.endswith(('.jpg', '.jpeg', '.png', '.webp')) and os.path.isfile(file_path):
                                thumbnail_file = file_path
                                logger.info(f"Found thumbnail: {file} ({os.path.getsize(file_path)} bytes)")
                            elif file.endswith('.info.json'):
                                json_file = file_path
                                logger.info(f"Found info JSON: {file}")
                        
                        if not video_file:
                            raise Exception("Video file not found after download")
                        
                        # Get enhanced metadata
                        metadata = {
                            'title': info.get('title', 'Video'),
                            'description': info.get('description', ''),
                            'author': info.get('uploader', '') or info.get('channel', ''),
                            'duration': info.get('duration', 0),
                            'platform': info.get('extractor_key', platform).lower(),
                            'thumbnail_url': info.get('thumbnail', ''),
                            'upload_date': info.get('upload_date', ''),
                            'view_count': info.get('view_count', 0),
                            'like_count': info.get('like_count', 0),
                            'comment_count': info.get('comment_count', 0),
                            'formats': info.get('formats', []),
                            'url': info.get('webpage_url', request.url),
                        }
                        
                        logger.info(f"Enhanced metadata extracted for {platform}")
                        
                        # Upload video to Supabase Storage
                        logger.info("Uploading video to Supabase Storage...")
                        video_storage_path = await upload_to_supabase(
                            video_file,
                            f"video_{platform}_{os.urandom(8).hex()}.mp4",
                            "video/mp4",
                            request.supabase_url,
                            request.supabase_key
                        )
                        
                        # Upload thumbnail if available
                        thumbnail_storage_path = None
                        if thumbnail_file:
                            logger.info("Uploading thumbnail to Supabase Storage...")
                            thumbnail_storage_path = await upload_to_supabase(
                                thumbnail_file,
                                f"thumb_{platform}_{os.urandom(8).hex()}.jpg",
                                "image/jpeg",
                                request.supabase_url,
                                request.supabase_key
                            )
                        
                        logger.info(f"Upload complete - video: {video_storage_path}, thumbnail: {thumbnail_storage_path}")
                        
                        return ExtractionResponse(
                            success=True,
                            video_path=video_storage_path,
                            thumbnail_path=thumbnail_storage_path,
                            metadata=metadata
                        )
                        
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_attempts - 1:  # Last attempt
                        raise
                    else:
                        continue
                
    except Exception as e:
        logger.error(f"Extraction failed after all attempts: {str(e)}")
        
        # FALLBACK: Try custom extractors without cookies
        logger.info(f"Cookies extraction failed, trying custom extractors for {platform}...")
        
        try:
            custom_result = custom_extract_video(request.url, platform)
            if custom_result['success']:
                logger.info(f"Custom extraction succeeded using {custom_result.get('method', 'unknown')} method")
                return ExtractionResponse(
                    success=True,
                    video_path=None,  # Custom extractors return video_url, not file path
                    thumbnail_path=None,
                    metadata=create_success_response(custom_result, None, None)['metadata'],
                    error=None
                )
            else:
                logger.warning(f"Custom extraction also failed: {custom_result.get('error', 'Unknown error')}")
        except Exception as custom_error:
            logger.error(f"Custom extraction error: {str(custom_error)}")
        
        # Return original error if custom extractors also fail
        return ExtractionResponse(
            success=False,
            error=str(e)
        )

@app.post("/test-cookies")
async def test_cookies():
    """
    Test endpoint to check cookie configuration
    """
    return {
        "instagram_cookies": get_instagram_cookies(),
        "tiktok_cookies": get_tiktok_cookies(),
        "user_agents": [get_rotated_user_agent() for _ in range(3)]
    }

async def upload_to_supabase(file_path: str, storage_filename: str, content_type: str, supabase_url: str, supabase_key: str) -> str:
    """
    Upload file to Supabase Storage bucket
    """
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        upload_url = f"{supabase_url}/storage/v1/object/blink-videos/{storage_filename}"
        
        headers = {
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        
        response = requests.post(upload_url, headers=headers, data=file_data)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Upload failed: {response.status_code} - {response.text}")
        
        logger.info(f"Uploaded {storage_filename} ({len(file_data)} bytes)")
        return storage_filename
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)