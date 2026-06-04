# Nginx Proxy Manager

Reverse proxy with SSL via Docker. Routes subdomains to internal services with automatic Let's Encrypt certificates.

## Setup

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
```

### 2. Create the compose file

```bash
mkdir -p ~/nginx-proxy-manager && cd ~/nginx-proxy-manager
nano docker-compose.yml
```

```yaml
version: "3"
services:
  app:
    image: jc21/nginx-proxy-manager:latest
    restart: unless-stopped
    ports:
      - "80:80"
      - "81:81"
      - "443:443"
    volumes:
      - ./data:/data
      - ./letsencrypt:/etc/letsencrypt
```

```bash
docker compose up -d
```

### 3. Configure DNS

At your domain provider, create an A record pointing your subdomain to your public IP:

```bash
curl ifconfig.me
```

Forward ports 80 and 443 to this machine on your router.

### 4. Access the dashboard

Open `http://<NPM-IP>:81`. Default credentials — change immediately after first login:

- Email: `admin@example.com`
- Password: `changeme`

### 5. Add a proxy host

**Hosts → Proxy Hosts → Add Proxy Host:**

- **Domain:** your subdomain
- **Scheme:** `http`
- **Forward Hostname/IP:** your service's local IP
- **Forward Port:** service port
- Tick **Websockets Support** and **Block Common Exploits**

In the **SSL tab** — select **Request a new SSL Certificate**, tick Force SSL, HTTP/2 Support, HSTS Enabled, agree to Let's Encrypt ToS, then Save.

## Verify

Visit your subdomain — it should load over HTTPS with a valid certificate.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| SSL certificate fails | Check DNS A record is correct and ports 80/443 are forwarded |
| Dashboard unreachable | `docker ps` — check container is running |
| Service not loading through proxy | Verify forward IP and port, check Websockets is ticked |
