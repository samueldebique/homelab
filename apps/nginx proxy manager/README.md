# Nginx Proxy Manager — Quick Setup Guide
This guide explains how to quickly set up **Nginx Proxy Manager (NPM)** in Docker to manage reverse proxies, SSL certificates, and domain routing for your self-hosted apps.
## Intsallation

To begin, install Docker by running the official installation script:
```bash
curl -fsSL https://get.docker.com | sh
 ```

Next, create a dedicated folder for NPM. This keeps all configuration and persistent data organised in one location:
```bash
mkdir -p ~/nginx-proxy-manager && cd ~/nginx-proxy-manager
```

Now, create the docker-compose.yml file that defines the NPM container and its ports. This configuration exposes ports 80, 81, and 443, and mounts local folders for data and SSL certificate storage. 
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

With the file ready, start the container. This will pull the NPM image, create the container, and start it in detached mode. 
```bash
sudo docker compose up -d
```
To identify your public IP address (needed for DNS setup), run:
```bash
curl ifconfig.me
```

## Configuration

At your domain provider (e.g. Namecheap, Cloudflare, or GoDaddy), create A records that point your domain and subdomains to your public IP. For example, set one for your root domain (@) and another for a specific service like Jellyfin. Once done, log in to your router and forward ports 80 and 443 to your server’s local IP. This ensures traffic from the internet can reach your proxy and allows Let’s Encrypt to verify your domain for SSL certificates.

### Access the Dashboard

Open a browser and go to: http://<your-NPM-IP>:81

You should see the login screen. The default credentials are:
Email:    admin@example.com
Password: changeme
After logging in, you’ll be asked to change these details. Use a real email address so Let’s Encrypt notifications can reach you.

To expose your Jellyfin server, click Hosts → Proxy Hosts → Add Proxy Host. In the Details tab, enter your subdomain , select http as the scheme, set the Forward Hostname / IP to your Jellyfin machine, and the Forward Port to 8096. Make sure to tick Websockets Support and Block Common Exploits to ensure compatibility and security.

Next, switch to the SSL tab. Choose Request a new SSL Certificate and tick the boxes for I agree to the Let’s Encrypt Terms, Force SSL, HTTP/2 Support and HSTS Enabled. Finally, click Save. NPM will automatically request and install a valid certificate for your domain.

