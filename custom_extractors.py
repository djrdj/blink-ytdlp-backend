import yt_dlp
import requests
import re
import json
import time
import random
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class InstagramCustomExtractor:
    """
    Custom Instagram extractor that uses direct API calls to bypass yt-dlp blocking
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Instagram 76.0.0.15.395 Android (24/7.0; 640dpi; 1440x2560; samsung; SM-G930F; herolte; samsungexynos8890; en_US)',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': '*/*',
            'Connection': 'keep-alive',
        })
    
    def extract_instagram_video(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract Instagram video using custom method
        """
        try:
            # Method 1: Try to get video ID from URL
            video_id = self._extract_instagram_video_id(url)
            if not video_id:
                return None
            
            # Method 2: Try alternative extraction methods
            return self._extract_with_alternative_methods(url, video_id)
            
        except Exception as e:
            logger.error(f"Instagram custom extraction failed: {e}")
            return None
    
    def _extract_instagram_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from Instagram URL
        """
        patterns = [
            r'instagram\.com/p/([^/]+)/?',
            r'instagram\.com/reel/([^/]+)/?',
            r'instagram\.com/tv/([^/]+)/?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_with_alternative_methods(self, url: str, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Try different extraction methods
        """
        methods = [
            self._method_oembed,
            self._method_graphql,
            self._method_public_api,
        ]
        
        for method in methods:
            try:
                result = method(url, video_id)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Method {method.__name__} failed: {e}")
                continue
        
        return None
    
    def _method_oembed(self, url: str, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Try Instagram oEmbed API
        """
        oembed_url = f"https://www.instagram.com/oembed/?url={requests.utils.quote(url)}"
        
        try:
            response = self.session.get(oembed_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', 'Instagram Video'),
                    'author_name': data.get('author_name', ''),
                    'thumbnail_url': data.get('thumbnail_url', ''),
                    'html': data.get('html', ''),
                    'method': 'oembed'
                }
        except Exception as e:
            logger.warning(f"OEmbed method failed: {e}")
        
        return None
    
    def _method_graphql(self, url: str, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Try Instagram GraphQL API
        """
        graphql_url = f"https://www.instagram.com/p/{video_id}/?hl=en"
        
        try:
            response = self.session.get(graphql_url, timeout=10)
            if response.status_code == 200:
                html = response.text
                
                # Extract video URL from HTML
                video_pattern = r'"video_url":"([^"]+)"'
                match = re.search(video_pattern, html)
                
                if match:
                    video_url = match.group(1).replace('\\/', '/')
                    
                    # Extract thumbnail
                    thumbnail_pattern = r'"display_url":"([^"]+)"'
                    thumbnail_match = re.search(thumbnail_pattern, html)
                    thumbnail_url = thumbnail_match.group(1).replace('\\/', '/') if thumbnail_match else None
                    
                    return {
                        'title': 'Instagram Video',
                        'video_url': video_url,
                        'thumbnail_url': thumbnail_url,
                        'method': 'graphql'
                    }
        except Exception as e:
            logger.warning(f"GraphQL method failed: {e}")
        
        return None
    
    def _method_public_api(self, url: str, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Try public Instagram API services
        """
        # This would use a third-party service like InstaAPI or similar
        # For demo purposes, showing the structure
        api_services = [
            "https://www.instagram.com/api/v1/oembed/",
            # Add more API services as needed
        ]
        
        for service in api_services:
            try:
                # This is a placeholder - real implementation would call actual APIs
                logger.info(f"Trying API service: {service}")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.warning(f"API service {service} failed: {e}")
                continue
        
        return None

class TikTokCustomExtractor:
    """
    Custom TikTok extractor
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def extract_tiktok_video(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract TikTok video using custom method
        """
        try:
            return self._extract_tiktok_alternative(url)
        except Exception as e:
            logger.error(f"TikTok custom extraction failed: {e}")
            return None
    
    def _extract_tiktok_alternative(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Alternative TikTok extraction methods
        """
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                html = response.text
                
                # Extract video data from HTML
                patterns = [
                    r'"downloadAddr":"([^"]+)"',
                    r'"playAddr":"([^"]+)"',
                    r'"originalCover":"([^"]+)"',
                ]
                
                video_data = {}
                for pattern in patterns:
                    match = re.search(pattern, html)
                    if match:
                        value = match.group(1).replace('\\/', '/')
                        if 'downloadAddr' in pattern:
                            video_data['video_url'] = value
                        elif 'playAddr' in pattern:
                            video_data['play_url'] = value
                        elif 'originalCover' in pattern:
                            video_data['thumbnail_url'] = value
                
                if video_data:
                    video_data['title'] = 'TikTok Video'
                    video_data['method'] = 'html_extraction'
                    return video_data
                    
        except Exception as e:
            logger.warning(f"TikTok HTML extraction failed: {e}")
        
        return None

class CustomExtractor:
    """
    Main custom extractor class
    """
    
    def __init__(self):
        self.instagram_extractor = InstagramCustomExtractor()
        self.tiktok_extractor = TikTokCustomExtractor()
    
    def extract(self, url: str, platform: str) -> Optional[Dict[str, Any]]:
        """
        Extract video using custom extractor based on platform
        """
        if platform == 'instagram':
            return self.instagram_extractor.extract_instagram_video(url)
        elif platform == 'tiktok':
            return self.tiktok_extractor.extract_tiktok_video(url)
        else:
            logger.warning(f"No custom extractor for platform: {platform}")
            return None
    
    def extract_with_fallback(self, url: str, platform: str, original_yt_dlp_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract with fallback to original yt-dlp if custom fails
        """
        # First try custom extractor
        custom_result = self.extract(url, platform)
        
        if custom_result:
            logger.info(f"Custom extractor succeeded for {platform}")
            return {
                'success': True,
                'method': f'custom_{custom_result.get("method", "unknown")}',
                'data': custom_result,
                'fallback_used': False
            }
        
        # Fallback to original yt-dlp result
        if original_yt_dlp_result:
            logger.info(f"Falling back to yt-dlp for {platform}")
            return {
                'success': True,
                'method': 'yt_dlp_fallback',
                'data': original_yt_dlp_result,
                'fallback_used': True
            }
        
        logger.error(f"Both custom and fallback extraction failed for {platform}")
        return {
            'success': False,
            'error': 'All extraction methods failed',
            'fallback_used': False
        }

# Custom yt-dlp extractors
class InstagramCustomYTDLExtractor(yt_dlp.extractor.common.InfoExtractor):
    IE_NAME = 'instagram:custom'
    _VALID_URL = r'instagram\.com/(?:p|reel|tv)/[^/]+'
    
    def _real_extract(self, url):
        """
        Custom Instagram extractor for yt-dlp
        """
        custom_extractor = InstagramCustomExtractor()
        result = custom_extractor.extract_instagram_video(url)
        
        if not result:
            self.raise_error('Failed to extract Instagram video')
        
        return {
            'id': url.split('/')[-2],
            'title': result.get('title', 'Instagram Video'),
            'description': '',
            'thumbnail': result.get('thumbnail_url', ''),
            'url': result.get('video_url', ''),
        }

class TikTokCustomYTDLExtractor(yt_dlp.extractor.common.InfoExtractor):
    IE_NAME = 'tiktok:custom'
    _VALID_URL = r'tiktok\.com/@[^/]+/video/\d+'
    
    def _real_extract(self, url):
        """
        Custom TikTok extractor for yt-dlp
        """
        custom_extractor = TikTokCustomExtractor()
        result = custom_extractor.extract_tiktok_video(url)
        
        if not result:
            self.raise_error('Failed to extract TikTok video')
        
        return {
            'id': url.split('/')[-1],
            'title': result.get('title', 'TikTok Video'),
            'description': '',
            'thumbnail': result.get('thumbnail_url', ''),
            'url': result.get('video_url', ''),
        }

def register_custom_extractors():
    """
    Register custom extractors with yt-dlp
    """
    yt_dlp.extractor.extractors.append(InstagramCustomYTDLExtractor)
    yt_dlp.extractor.extractors.append(TikTokCustomYTDLExtractor)
    logger.info("Custom extractors registered successfully")

# Usage example
if __name__ == "__main__":
    # Test custom extractors
    extractor = CustomExtractor()
    
    # Test Instagram
    test_instagram_url = "https://www.instagram.com/p/test123/"
    result = extractor.extract_with_fallback(test_instagram_url, 'instagram')
    print(f"Instagram result: {result}")
    
    # Test TikTok
    test_tiktok_url = "https://www.tiktok.com/@user/video/1234567890"
    result = extractor.extract_with_fallback(test_tiktok_url, 'tiktok')
    print(f"TikTok result: {result}")