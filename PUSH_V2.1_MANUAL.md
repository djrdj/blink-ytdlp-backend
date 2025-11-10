# 🚀 PUSH V2.1 CUSTOM EXTRACTORS - RUČNO

## Problem
Git push iz workspace-a nije uspeo zbog timeout-a. **Moraš da push-uješ ručno sa svoje lokalne mašine.**

## Fajlovi su spremni ✅
- `custom_no_cookies.py` - Custom TikTok/Instagram extractors bez cookies
- `main.py` - Ažuriran sa import custom_no_cookies  
- `requirements.txt` - Dodani beautifulsoup4 i lxml

## Šta treba da uradiš:

### 1. Na svojoj lokalnoj mašini:
```bash
# Navigiraj do repozitorijuma
cd /path/to/your/blink-ytdlp-backend

# Fetch najnovije izmene
git fetch origin

# Push-uj local commit-ove
git push origin main
```

### 2. Ako traži autentifikaciju:
- Koristi svoj **GitHub Personal Access Token** umesto password-a
- Format: `https://github_personal_token@github.com/djrdj/blink-ytdlp-backend.git`

### 3. Nakon uspešnog push-a:
- Railway će automatski deploy-ovati v2.1
- Sačekaj 5-10 minuta
- Testiraj sa pravim TikTok/Instagram linkom

## Commit-ovi koje push-uješ:
1. 🔥 V2.0: Add cookies support for TikTok/Instagram anti-scraping bypass
2. Sync commits
3. 🚀 V2.1: Add custom extractors without cookies - 100% secure!

## Nakon Railway deploy-a:
Railway će biti dostupan na: https://blink-ytdlp-backend-production.up.railway.app/

**Test komanda:**
```bash
curl -X POST https://blink-ytdlp-backend-production.up.railway.app/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@user/video/REAL_ID", "supabase_url": "test", "supabase_key": "test"}'
```
