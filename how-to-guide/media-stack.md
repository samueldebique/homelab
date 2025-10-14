# 🎬 Media ARR Stack Setup Guide

> This setup combines Jellyfin, Radarr, Sonarr, Prowlarr, qBittorrent, Bazarr, Jellyseerr, and Gluetun into one automated media management system.  
> Designed for homelab environments — use responsibly and for educational purposes only.

---
## 1. Installation

Install Docker:
```bash
curl -fsSL https://get.docker.com | sh
```

```bash
~/data/arr/
├── jellyfin/
├── qbittorrent/
├── radarr/
├── sonarr/
├── prowlarr/
├── bazarr/
├── gluetun/
└── jellyseerr/

```
## 2. Docker Compose Setup

``` bash
mkdir -p ~/data && cd ~/data
nano docker-compose.yml
```

Put all the docker configs into this docker compose

## 3. Launch the Stack
Once your file is saved, start everything:
```bash
sudo docker compose up -d
```
To view running containers:
```bash
docker ps
```
Different folders will be mix match between being created by root or the user. 
```bash
sudo chown -R 1000:1000 /data/arr
```

## 4. Connecting Services
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




