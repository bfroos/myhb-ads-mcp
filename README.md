# Google Ads MCP Server

MCP-Server für Google Ads (30 Tools: GAQL, Search Ads, Assets, PMax).

## Setup

1. **GitHub Secrets hinzufügen** (Settings → Secrets):
   - `GOOGLE_ADS_DEVELOPER_TOKEN`
   - `GOOGLE_ADS_CLIENT_ID`
   - `GOOGLE_ADS_CLIENT_SECRET`
   - `GOOGLE_ADS_REFRESH_TOKEN`
   - `CONNECTOR_TOKEN`

2. **Lokal testen**: `cp .env.example .env` → edit → `python server.py`

3. **Deploy auf Hetzner**: `git push origin main` → Auto-Deploy per GitHub Actions

## Available Tools (30)

- `run_gaql_report`, `create_responsive_search_ad`, `update_ad_status`, `add_keywords`
- (+ 26 weitere für Assets, PMax, Locations, etc.)

## For Claude

Edit `server.py` → Push → Auto-Deploy live.

---
