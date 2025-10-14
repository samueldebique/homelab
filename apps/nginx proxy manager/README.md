# Nginx Proxy Manager — Quick Setup Guide

## Intsallation
```bash
curl -fsSL https://get.docker.com | sh
 ```

Create the Nginx Proxy Manager folder
```bash
mkdir -p ~/nginx-proxy-manager && cd ~/nginx-proxy-manager
```

Create docker-compose.yml
``` yaml
version: "3"
services:
  app:
    image: jc21/nginx-proxy-manager:latest
    restart: unless-stopped
    ports:
      - "80:80"     # HTTP
      - "81:81"     # Web UI
      - "443:443"   # HTTPS
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
```

Run the container
```bash
sudo docker compose up -d
```

```bash
curl ifconfig.me
```

## Configuration

Configure DNS
to point A record to the public IP

Log into Nginx Proxy Manager
port 81

Default credentials:
Email:    admin@example.com
Password: changeme

Add your first Proxy Host
Tick:
- I agree to the Let’s Encrypt Terms
- Force SSL
- HTTP/2 Support
- HSTS Enabled
- Click Save
