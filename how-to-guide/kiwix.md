# Kiwix

Offline Wikipedia and other ZIM files served over LAN from an LXC on Proxmox.

## Setup

### 1. Download ZIM files

On the Proxmox host, create a folder on your bulk storage and download ZIMs using `screen` — don't use `nohup`, it's fragile for long downloads:

```bash
apt install aria2 screen -y
screen -S download
aria2c -x 16 -s 16 <zim-url>
```

Detach with **Ctrl+A then D**, reattach with `screen -r download`. Find ZIMs at https://download.kiwix.org/zim/.

### 2. Create the LXC

- **Unprivileged:** ticked
- **Disk:** 4GB
- **CPU:** 1 core
- **Memory:** 512 MiB + 512 MiB swap

### 3. Add the bind mount

```bash
pct stop <CTID>
nano /etc/pve/lxc/<CTID>.conf
```

Add at the bottom (adjust path to your ZIM folder):

```
mp0: /path/to/zim,mp=/data,ro=1
```

```bash
pct start <CTID>
pct exec <CTID> -- ls -lh /data
```

If permission denied: `chmod -R o+rX /path/to/zim`

### 4. Install Kiwix

```bash
pct enter <CTID>
apt update && apt upgrade -y
apt install kiwix-tools -y
```

### 5. Create the systemd service

```bash
nano /etc/systemd/system/kiwix.service
```

```ini
[Unit]
Description=Kiwix Serve
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/bin/bash -c '/usr/bin/kiwix-serve --port=8080 /data/*.zim'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

The `/bin/bash -c` wrapper is required — systemd does not expand glob patterns directly.

### 6. Start the service

```bash
systemctl daemon-reload
systemctl enable kiwix
systemctl start kiwix
exit
```

## Verify

```bash
pct exec <CTID> -- systemctl status kiwix --no-pager
```

Open `http://<LXC-IP>:8080` — you should see the Kiwix library.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Service fails to start | Check `ExecStart` has `/bin/bash -c` wrapper; check for corrupt ZIM |
| "Assertion failed at cluster.cpp" | Corrupt ZIM — remove it and re-download |
| `apt update` hangs | `pct set <CTID> --nameserver 1.1.1.1 && pct reboot <CTID>` |
| Library shows "No result" | Stale URL filter — navigate to clean `http://<LXC-IP>:8080/` |
| `nobody:nogroup` ownership | Normal for unprivileged LXCs — not a bug |
