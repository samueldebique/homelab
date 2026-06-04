# Media Stack

Jellyfin, Radarr, Sonarr, Prowlarr, qBittorrent, and Jellyseerr running via Docker Compose.

## Setup

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
exit && su $USER
```

### 2. Create the compose file

```bash
mkdir -p /data && cd /data
nano docker-compose.yml
```

Start everything:

```bash
docker compose up -d
```

Fix permissions if needed:

```bash
sudo chown -R 1000:1000 /data
```

### 3. Jellyfin — `http://<IP>:8096`

1. Create admin user
2. Add media libraries pointing to your movie and TV folders

### 4. qBittorrent — `http://<IP>:8080`

1. Get the temporary password: `docker logs <container-id>`
2. Change the password under **Tools → Web UI**

### 5. Radarr — `http://<IP>:7878`

1. Set Authentication Method to **Forms**
2. **Settings → Download Clients** → Add qBittorrent
3. **Settings → Media Management** → Add Root Folder
4. **Settings → General** → copy API key for later

### 6. Sonarr — `http://<IP>:8989`

Same steps as Radarr.

### 7. Prowlarr — `http://<IP>:9696`

1. **Settings → Apps** → Add Radarr and Sonarr (paste API keys)
2. **Indexers** → Add indexers

### 8. Jellyseerr — `http://<IP>:5055`

1. Log in with Jellyfin admin account
2. Add Radarr and Sonarr with their API keys
3. Set root folders and enable Movies + TV Shows

## Verify

```bash
docker ps
```

All containers should show `Up`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Container not starting | `docker logs <container-id>` |
| Permission denied on media folders | `sudo chown -R 1000:1000 /data` |
| qBittorrent temp password not visible | Check bottom of `docker logs <container-id>` |
