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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def detect_platform(url: str) -> str:
    """
    Detect platform from URL
    """
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
    """
    Get rotated user agent to avoid rate limiting
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    ]
    return random.choice(user_agents)

app = FastAPI(title="Blink Video Extraction Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExtractionRequest(BaseModel):
    url: str
    supabase_url: str
    supabase_key: str

class ExtractionResponse(BaseModel):
    success: bool
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    metadata: dict = {}
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"status": "Blink yt-dlp extraction service running", "version": "1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/extract", response_model=ExtractionResponse)
async def extract_video(request: ExtractionRequest):
    """
    Extract video from social media URL using yt-dlp with enhanced Instagram support
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
        
        # Create temporary directory for downloads
        with tempfile.TemporaryDirectory() as temp_dir:
            # Platform-specific yt-dlp options
            if platform == 'instagram':
                # Enhanced options for Instagram
                ydl_opts = await get_instagram_ytdlp_options(temp_dir)
            elif platform == 'tiktok':
                # Standard options for TikTok  
                ydl_opts = get_standard_ytdlp_options(temp_dir)
            else:
                # Standard options for other platforms
                ydl_opts = get_standard_ytdlp_options(temp_dir)
            
            # Try extraction with retry logic
            max_attempts = 5 if platform == 'instagram' else 3
            for attempt in range(max_attempts):
                try:
                    logger.info(f"Attempt {attempt + 1}: Extracting video info...")
                    
                    # Add delay between attempts to avoid rate limiting
                    if attempt > 0:
                        if platform == 'instagram':
                            time.sleep(5)  # Longer delay for Instagram
                        else:
                            time.sleep(2)
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(request.url, download=True)
                        
                        # Find downloaded video file
                        video_file = None
                        thumbnail_file = None
                        
                        for file in os.listdir(temp_dir):
                            file_path = os.path.join(temp_dir, file)
                            if file.endswith(('.mp4', '.webm', '.mkv')) and os.path.isfile(file_path):
                                video_file = file_path
                                logger.info(f"Found video file: {file} ({os.path.getsize(file_path)} bytes)")
                            elif file.endswith(('.jpg', '.jpeg', '.png', '.webp')) and os.path.isfile(file_path):
                                thumbnail_file = file_path
                                logger.info(f"Found thumbnail: {file} ({os.path.getsize(file_path)} bytes)")
                        
                        if not video_file:
                            raise Exception("Video file not found after download")
                        
                        # Get metadata
                        metadata = {
                            'title': info.get('title', 'Video'),
                            'description': info.get('description', ''),
                            'author': info.get('uploader', '') or info.get('channel', ''),
                            'duration': info.get('duration', 0),
                            'platform': info.get('extractor_key', platform).lower(),
                            'thumbnail_url': info.get('thumbnail', ''),
                            'upload_date': info.get('upload_date', ''),
                            'view_count': info.get('view_count', 0),
                        }
                        
                        logger.info(f"Video info extracted: {metadata['title']}")
                        
                        # Upload video to Supabase Storage
                        logger.info("Uploading video to Supabase Storage...")
                        video_storage_path = await upload_to_supabase(
                            video_file,
                            f"video_{os.urandom(8).hex()}.mp4",
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
                                f"thumb_{os.urandom(8).hex()}.jpg",
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
                    if attempt == 2:  # Last attempt
                        raise
                    else:
                        continue
                
    except Exception as e:
        logger.error(f"Extraction failed after all attempts: {str(e)}")
        return ExtractionResponse(
            success=False,
            error=str(e)
        )

def get_standard_ytdlp_options(temp_dir: str) -> dict:
    """
    Get standard yt-dlp options for most platforms
    """
    user_agent = get_rotated_user_agent()
    video_path = os.path.join(temp_dir, 'video.%(ext)s')
    
    return {
        'format': 'best[ext=mp4]/best',  # Prefer MP4 format
        'outtmpl': video_path,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'nocheckcertificate': True,
        'user_agent': user_agent,
        'http_headers': {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
            'Connection': 'keep-alive',
        },
        'writethumbnail': True,
        'writesubtitles': False,
        'retries': 3,
        'fragment_retries': 3,
        'extractor_retries': 3,
        'skip_unavailable_fragments': True,
    }

async def get_instagram_ytdlp_options(temp_dir: str) -> dict:
    """
    Get enhanced yt-dlp options specifically for Instagram
    """
    user_agent = get_rotated_user_agent()
    video_path = os.path.join(temp_dir, 'video.%(ext)s')
    
    return {
        'format': 'best[ext=mp4]/best',
        'outtmpl': video_path,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'nocheckcertificate': True,
        'user_agent': user_agent,
        'http_headers': {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        },
        'writethumbnail': True,
        'writesubtitles': False,
        'retries': 5,  # More retries for Instagram
        'fragment_retries': 5,
        'extractor_retries': 5,
        'skip_unavailable_fragments': True,
        'extractor_args': {
            'instagram': {
                'add_metadata': True,
            }
        },
        'youtube_dl_args': [
            '--extractor-args', 'instagram:cookies=cookies.txt'
        ]
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
