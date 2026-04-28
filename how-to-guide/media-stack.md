# Self-Hosted Wikipedia with Kiwix on Proxmox

Run offline Wikipedia (115GB) from a Proxmox LXC, accessible to all devices on your network.

## Architecture

```
Proxmox Host
├── /mnt/pve/tank/zim/           ← ZIM files (external HDD)
└── LXC (kiwix)
    ├── Ubuntu 24.04
    ├── kiwix-serve on port 8080
    └── /data → bind mount to /mnt/pve/tank/zim/ (read-only)
```

## Step 1: Download Wikipedia

On the Proxmox host:

```bash
mkdir -p /mnt/pve/tank/zim
cd /mnt/pve/tank/zim
apt install aria2 -y
aria2c -x 16 -s 16 https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2026-02.zim
```

Check https://download.kiwix.org/zim/wikipedia/ for the latest dated filename.

Other ZIMs available at https://download.kiwix.org/zim/ — Stack Overflow, Wikivoyage, Wiktionary, etc.

## Step 2: Create the LXC

In the Proxmox web UI, click **Create CT**:

- **CT ID:** `102`
- **Hostname:** `kiwix`
- **Unprivileged:** ticked
- **Template:** `ubuntu-24.04-standard`
- **Storage:** `local-lvm`, 4GB disk
- **CPU:** 1 core
- **Memory:** 512MB RAM, 512MB swap
- **Network:** vmbr0, DHCP

Tick "Start after created" and click Finish.

Note the LXC's IP from the Summary tab.

## Step 3: Install Kiwix

Open the LXC console and run:

```bash
apt update && apt upgrade -y
apt install kiwix-tools -y
exit
```

## Step 4: Add the Bind Mount

On the Proxmox host:

```bash
pct stop 102
nano /etc/pve/lxc/102.conf
```

Add this line at the bottom:

```
mp0: /mnt/pve/tank/zim,mp=/data,ro=1
```

Save (Ctrl+X, Y, Enter), then:

```bash
pct start 102
pct exec 102 -- ls -lh /data
```

The Wikipedia ZIM should be visible. If you see "permission denied":

```bash
chmod -R o+rX /mnt/pve/tank/zim
```

## Step 5: Create the systemd Service

Inside the LXC:

```bash
nano /etc/systemd/system/kiwix.service
```

Paste:

```ini
[Unit]
Description=Kiwix Serve
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/kiwix-serve --port=8080 /data/wikipedia_en_all_maxi_2026-02.zim
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Update the filename in `ExecStart` to match your ZIM. Save and run:

```bash
systemctl daemon-reload
systemctl enable kiwix
systemctl start kiwix
systemctl status kiwix
```

Look for `Active: active (running)`.

## Step 6: Access

Open `http://<LXC-IP>:8080` in any browser on your network.

The library search filters ZIMs by title, not articles. Click the Wikipedia tile to enter Wikipedia, then use Wikipedia's search bar.

## Adding More ZIMs

Drop new `.zim` files into `/mnt/pve/tank/zim/` on the host, update `ExecStart` in the service file (or use `/data/*.zim` to load all), then:

```bash
systemctl daemon-reload
systemctl restart kiwix
```

## Updating Wikipedia

```bash
cd /mnt/pve/tank/zim
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_<NEW-DATE>.zim
# Update ExecStart in /etc/systemd/system/kiwix.service inside LXC
systemctl daemon-reload && systemctl restart kiwix
rm wikipedia_en_all_maxi_<OLD-DATE>.zim
```

## Troubleshooting

**Library shows "No result"** — stale URL filter. Clear the URL to plain `http://<IP>:8080/` or use a private window.

**`nobody:nogroup` ownership inside LXC** — normal for unprivileged containers. Not a problem if the file has world-read permissions (`-rw-r--r--`).

**Service fails to start** — check logs: `journalctl -u kiwix --no-pager -n 50`. Usually filename mismatch in `ExecStart` or bind mount didn't apply.

