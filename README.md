# Blink yt-dlp Backend Service

Production-grade video extraction service using yt-dlp for the Blink application.

## Features

- Extract videos from Instagram, TikTok, Facebook, X (Twitter), and 1000+ sites
- Download actual MP4 video files
- Upload to Supabase Storage automatically
- RESTful API with FastAPI
- Docker containerized for easy deployment

## Local Development

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for non-Docker development)

### Run with Docker
```bash
docker-compose up --build
```

Service runs on: `http://localhost:8000`

### Run without Docker
```bash
pip install -r requirements.txt
python main.py
```

## API Endpoints

### GET /
Health check and service info

### GET /health
Service health status

### POST /extract
Extract video from URL

**Request Body:**
```json
{
  "url": "https://www.tiktok.com/@user/video/123456",
  "supabase_url": "https://your-project.supabase.co",
  "supabase_key": "your-service-role-key"
}
```

**Response:**
```json
{
  "success": true,
  "video_path": "video_abc123.mp4",
  "thumbnail_path": "thumb_abc123.jpg",
  "metadata": {
    "title": "Video Title",
    "description": "Video description",
    "author": "Username",
    "duration": 30,
    "platform": "tiktok"
  }
}
```

## Deployment Options

### Option 1: Railway.app (Recommended)

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Deploy:
```bash
railway up
```

4. Get deployment URL:
```bash
railway status
```

Cost: ~$5-10/month

### Option 2: Render.com

1. Create account at render.com
2. Create new "Web Service"
3. Connect to GitHub repository or upload code
4. Set build command: `docker build -t ytdlp-backend .`
5. Set start command: `docker run -p $PORT:8000 ytdlp-backend`

Free tier available (limited)

### Option 3: Fly.io

1. Install Fly CLI:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Login and launch:
```bash
fly auth login
fly launch
```

3. Deploy:
```bash
fly deploy
```

Pay-as-you-go pricing

### Option 4: Your Own Server

1. Build Docker image:
```bash
docker build -t blink-ytdlp .
```

2. Run container:
```bash
docker run -d -p 8000:8000 --name blink-ytdlp blink-ytdlp
```

## Environment Variables

- `PORT`: Server port (default: 8000)

## Integration with Supabase Edge Function

Update the edge function to call this backend:

```typescript
// In extract-video edge function
const YTDLP_BACKEND_URL = 'https://your-backend.railway.app'; // Replace with actual URL

const response = await fetch(`${YTDLP_BACKEND_URL}/extract`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: sourceUrl,
    supabase_url: supabaseUrl,
    supabase_key: serviceRoleKey
  })
});

const result = await response.json();
```

## Supported Platforms

- TikTok
- Instagram (posts, reels, stories)
- Facebook (videos, watch)
- X/Twitter
- YouTube
- And 1000+ more sites supported by yt-dlp

## Troubleshooting

### Video extraction fails
- Check if the URL is accessible publicly
- Verify platform is supported
- Check yt-dlp version (update if needed)

### Upload fails
- Verify Supabase credentials
- Check storage bucket exists ("blink-videos")
- Verify bucket has public access or proper RLS policies

### Container won't start
- Check Docker logs: `docker logs <container-id>`
- Verify port 8000 is available
- Ensure ffmpeg is installed in container

## Updates

To update yt-dlp version:
1. Update version in requirements.txt
2. Rebuild Docker image
3. Redeploy

## Security Notes

- Service role key is passed in request (secure over HTTPS)
- No persistent storage of credentials
- Temporary files cleaned up after processing
- CORS enabled for Supabase Edge Function access

## Monitoring

Check service health:
```bash
curl https://your-backend.railway.app/health
```

## Cost Estimation

- Railway: $5-10/month for 1GB RAM
- Render: Free tier available, $7/month for persistent
- Fly.io: ~$3-5/month for minimal usage
- VPS: $5-20/month depending on provider

## License

Part of the Blink video extraction application.
