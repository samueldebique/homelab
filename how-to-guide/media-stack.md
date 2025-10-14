# 🎬 Media ARR Stack Setup Guide

> This setup combines Jellyfin, Radarr, Sonarr, Prowlarr, qBittorrent, Bazarr, Jellyseerr, and Gluetun into one automated media management system.  
> Designed for homelab environments — use responsibly and for educational purposes only.

---

## 1. Prerequisites

Before starting, ensure your system has:
- Ubuntu or Debian-based OS  
- Docker and Docker Compose installed  
- Correctly forwarded ports **(80, 443, and any app-specific ports)**  
- Sufficient storage under `/data/arr`

Install Docker:
```bash
curl -fsSL https://get.docker.com | sh
```

## 2. Directory Structure
/data/arr/
    ├── jellyfin/
    ├── qbittorrent/
    ├── radarr/
    ├── sonarr/
    ├── prowlarr/
    ├── bazarr/
    └── jellyseerr/

## 3. Docker Compose Setup

``` bash
mkdir -p ~/arr && cd ~/arr
nano docker-compose.yml
```

Put all the docker configs into this docker compose

## 4. Launch the Stack
Once your file is saved, start everything:
```bash
sudo docker compose up -d
```
To view running containers:
```bash
docker ps
```

## 5. Connecting Services
1.	qBittorrent → Radarr/Sonarr
	•	Host: localhost
	•	Port: 8080
	•	Username/password from WebUI setup.
2.	Radarr/Sonarr → Prowlarr
	•	Copy Prowlarr’s API key (from General settings).
	•	Add Radarr and Sonarr under Settings → Apps in Prowlarr.
3.	Jellyseerr → Jellyfin
	•	Set your Jellyfin URL.
	•	Link Radarr and Sonarr using their API keys.




