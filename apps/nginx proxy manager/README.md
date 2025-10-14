Install Docker
curl -fsSL https://get.docker.com | sh

Create the Nginx Proxy Manager folder
mkdir -p ~/nginx-proxy-manager && cd ~/nginx-proxy-manager

Create docker-compose.yml

Run the container
sudo docker compose up -d

curl ifconfig.me

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
