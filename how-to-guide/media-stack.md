# Media Stack Setup Guide

## 1. Installation

Install Docker:
```bash
curl -fsSL https://get.docker.com | sh
```

### 2. Docker Compose Setup and Permissions
Give yourself permissions to docker
```bash
sudo usermod -aG docker user
```
Now exit and switch user to update your permissions
```bash
exit && su samuel
```

Now make the folder to store your compose files
``` bash
mkdir -p /data && cd /data
nano docker-compose.yml
```


### 3. Launch the compose file
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
### 4. Log onto jellyfin
- Jellyfin — http://<your_ip>:8096
	1.	Create an admin user and save credentials.
	2.	Add media libraries:
	-	/path/to/movie
	-	/path/to/tvshows
	
### 5. Log onto Radarr
- Radarr — http://<your_ip>:7878
- Create an admin user and save the credentials
	1.	Set Authentication Method → Forms
	2.	Navigate to Settings -> Download Clients -> Add -> Transmission 
	3.	Navigate to Settings -> Media Management -> Add Root Folder 
	4.	Navigate to Settings -> General -> API Key -> copy it for the next steps 
	
### 6. Log onto Sonarr
- Sonarr — http://<your_ip>:8989
- Same steps as Radarr

### 7. Log onto Prowlarr
- Prowlarr — http://<your_ip>:9696
- Create an admin user and save the credentials
- Navigate to Settings -> Apps -> Add:
	- 	Radarr (paste API key)
	-	Sonarr (paste API key)
- Go back to Indexers -> Add New Indexers

### 7. Log onto jellyseerr
- Jellyseerr (optional) — http://<your_ip>:5055
	1.	Log in with Jellyfin admin account.
	2.	Add Radarr and Sonarr:
	 -	Hostname: localhost
	 -	Port: 7878 (Radarr), 8989 (Sonarr)
	 -	API Keys: from previous steps
	3.	Enable Movies + TV Shows
	4.	Set Root folders /movies and /tv
	5.	Enable scan:true
