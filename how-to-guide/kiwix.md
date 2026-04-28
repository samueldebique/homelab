# Self-Hosted Wikipedia with Kiwix on Proxmox

Run a full offline copy of Wikipedia (115GB, 6.7M+ articles with images) from a Proxmox LXC, accessible to every device on your network.

This guide uses an unprivileged LXC with a bind mount to external storage, following the principle of **disposable services, durable data**. The LXC can be deleted and rebuilt anytime — the ZIM files live on a separate storage tier and survive container changes.

## Architecture

```
Proxmox Host
├── /mnt/pve/tank/zim/          ← ZIM files live here (external HDD)
│   └── wikipedia_en_all_maxi_2026-02.zim
│
└── LXC 102 (kiwix)
    ├── Ubuntu 24.04 LTS
    ├── kiwix-serve (port 8080)
    └── /data/                   ← Bind mount → /mnt/pve/tank/zim/ (read-only)
```

**Why this pattern:**
- LXC runs on fast NVMe (low latency for serving)
- ZIM files live on bulk storage (cheap, large)
- Bind mount is read-only (LXC can't corrupt the ZIM even if compromised)
- LXC is disposable — destroy and rebuild without touching data

## Hardware

Tested on:
- Lenovo ThinkCentre M720q (i5, 32GB RAM)
- Proxmox VE 9.1
- 8TB WD Elements external HDD (`tank`)
- Internal NVMe for LXC root disk

Should work on any Proxmox host with enough storage for the ZIM files.

## Prerequisites

- Proxmox VE 8.x or 9.x running
- An Ubuntu 24.04 container template downloaded
- A storage pool for bulk data (we use `tank` mounted at `/mnt/pve/tank/`)
- ~120GB free on bulk storage for the Wikipedia ZIM
- At least 4GB free on `local-lvm` for the LXC root disk

## Step 1: Download Wikipedia ZIM

The Wikipedia ZIM is a static, monthly-updated archive of all English Wikipedia articles. We'll download it directly to bulk storage.

On the Proxmox host shell:

```bash
mkdir -p /mnt/pve/tank/zim
cd /mnt/pve/tank/zim
```

### Option A: wget (simple, single connection)

```bash
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2026-02.zim
```

The `-c` flag continues from where it stopped if interrupted.

### Option B: aria2 (fast, parallel chunks — recommended)

```bash
apt install aria2 -y
aria2c -x 16 -s 16 https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2026-02.zim
```

This splits the download into 16 parallel connections. Often 2-3x faster.

### Browse other ZIMs

The full Kiwix library is at https://download.kiwix.org/zim/. Useful options:

| ZIM | Size | What |
|---|---|---|
| `wikipedia_en_all_maxi_YYYY-MM.zim` | ~115GB | Full English Wikipedia with images |
| `wikipedia_en_all_nopic_YYYY-MM.zim` | ~48GB | All articles, no images |
| `wikipedia_en_all_mini_YYYY-MM.zim` | ~12GB | Top articles only |
| `stackoverflow.com_en_all_YYYY-MM.zim` | ~80GB | All Stack Overflow Q&A |
| `wikivoyage_en_all_maxi_YYYY-MM.zim` | ~2GB | Travel guides |
| `wiktionary_en_all_maxi_YYYY-MM.zim` | ~5GB | Dictionary |

**Note:** filenames include a date — check https://download.kiwix.org/zim/wikipedia/ for the latest version. There's no auto-updating "latest" symlink.

Download time depends on connection speed:
- 100 Mbps: ~2.5 hours
- 200 Mbps: ~1.5 hours
- 1 Gbps: ~20 minutes

Verify the file completed:

```bash
ls -lh /mnt/pve/tank/zim/
# Should show ~115G for the maxi file
```

Optional cleanup:

```bash
rm /mnt/pve/tank/zim/*.meta4   # aria2 leftover metadata, not needed
```

## Step 2: Create the Kiwix LXC

In the Proxmox web UI, click **Create CT** and use these settings:

### General
- **CT ID:** `102` (or any unused ID)
- **Hostname:** `kiwix`
- **Password:** set a root password
- **Unprivileged container:** ✅ ticked (security best practice)

### Template
- **Storage:** `local`
- **Template:** `ubuntu-24.04-standard`

### Disks
- **Storage:** `local-lvm` (LXC root must be on fast storage, NEVER on the bind-mount target)
- **Disk size (GiB):** `4`

The 4GB disk only holds the OS and Kiwix binary. The 115GB ZIM lives elsewhere via bind mount.

### CPU
- **Cores:** `1`

Kiwix-serve serves static files — minimal CPU needed.

### Memory
- **Memory (MiB):** `512`
- **Swap (MiB):** `512`

### Network
- **Bridge:** `vmbr0`
- **IPv4:** DHCP (or set static IP if you have a preference)

### Confirm
- ✅ Tick "Start after created"
- Click **Finish**

After ~30 seconds, the LXC is created and running. Note its IP from the Summary tab — you'll need it later.

## Step 3: Install Kiwix Tools

Open the LXC console (web UI → 102 (kiwix) → Console) or use `pct enter 102` from the Proxmox host.

Inside the LXC:

```bash
apt update && apt upgrade -y
apt install kiwix-tools -y
```

Verify the install:

```bash
kiwix-serve --version
```

Exit the LXC:

```bash
exit
```

## Step 4: Add the Bind Mount

The LXC needs access to the ZIM files. We add a bind mount that exposes the host's `/mnt/pve/tank/zim/` as `/data/` inside the LXC.

Stop the LXC first (config edits require it stopped):

```bash
pct stop 102
```

Edit the LXC config:

```bash
nano /etc/pve/lxc/102.conf
```

At the bottom of the file, add this line:

```
mp0: /mnt/pve/tank/zim,mp=/data,ro=1
```

Breakdown:
- `mp0` — mount point #0 (Proxmox uses `mp0`, `mp1`, `mp2`... for additional mounts)
- `/mnt/pve/tank/zim` — source folder on the host
- `mp=/data` — where it appears inside the LXC
- `ro=1` — read-only (Kiwix only reads ZIMs, never writes — safer)

Save with **Ctrl+X**, **Y**, **Enter**.

Start the LXC:

```bash
pct start 102
```

Verify the bind mount works:

```bash
pct exec 102 -- ls -lh /data
```

You should see the Wikipedia ZIM. Note: ownership may show as `nobody:nogroup` inside the LXC — this is expected behavior for unprivileged containers and does NOT prevent reading. The file IS readable as long as world-read permissions (`-rw-r--r--`) are set on the host.

If you see "permission denied" instead of `nobody:nogroup`, fix permissions on the host:

```bash
chmod -R o+rX /mnt/pve/tank/zim
```

## Step 5: Test Kiwix Manually

Before setting up systemd, verify Kiwix can serve the ZIM. Enter the LXC:

```bash
pct enter 102
```

Run kiwix-serve in the foreground:

```bash
kiwix-serve --port=8080 /data/*.zim
```

You should see:

```
The Kiwix server is running and can be accessed in the local network at: http://<LXC-IP>:8080
```

In your browser, navigate to `http://<LXC-IP>:8080`. You should see the Kiwix library with Wikipedia listed. Click the Wikipedia tile and search for any article to verify content loads correctly.

**Tip:** the search box on the library homepage filters ZIMs by title (not articles). To search Wikipedia articles, click into the Wikipedia tile first.

If you see "No result," check the URL bar — there may be a stale filter (e.g., `?q=birmingham`). Navigate to a clean `http://<LXC-IP>:8080/` to clear it.

Press **Ctrl+C** to stop the manual run.

## Step 6: Create a systemd Service

Now make Kiwix run automatically on boot and restart on failure.

Inside the LXC, create the service file:

```bash
nano /etc/systemd/system/kiwix.service
```

Paste this content:

```ini
[Unit]
Description=Kiwix Serve - Offline Wikipedia and knowledge
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

**Note:** Update the filename in `ExecStart` to match the actual ZIM filename you downloaded. To serve all ZIMs in `/data`, use `/data/*.zim` instead.

Save with **Ctrl+X**, **Y**, **Enter**.

Reload systemd, enable, and start the service:

```bash
systemctl daemon-reload
systemctl enable kiwix
systemctl start kiwix
systemctl status kiwix
```

Look for `Active: active (running)` in the output. Press **q** to exit the status view.

Exit the LXC:

```bash
exit
```

## Step 7: Verify Persistence

Test that the service survives a reboot. From the Proxmox host:

```bash
pct reboot 102
```

Wait ~30 seconds, then visit `http://<LXC-IP>:8080` from your Mac/phone. If Wikipedia loads, the systemd service auto-started correctly — you're done.

## Add to Devices

### iPhone (Safari)

1. Open `http://<LXC-IP>:8080` in Safari
2. Tap the Share button
3. Add to Home Screen → name it "Wikipedia"
4. Now you have an app-like icon on your home screen

### Mac

Bookmark `http://<LXC-IP>:8080` in your browser.

## Adding More ZIMs Later

Drop new `.zim` files into `/mnt/pve/tank/zim/` on the host. Then either:

**If serving with wildcard (`/data/*.zim` in service):**

```bash
pct exec 102 -- systemctl restart kiwix
```

Kiwix auto-discovers new ZIMs in `/data` on startup.

**If serving specific files in service file:**

Edit `/etc/systemd/system/kiwix.service` inside the LXC and add the new filename to `ExecStart`. Then:

```bash
systemctl daemon-reload
systemctl restart kiwix
```

## Updating Wikipedia (every few months)

Kiwix Foundation publishes new ZIMs roughly every 2-3 months. To update:

```bash
cd /mnt/pve/tank/zim
mv wikipedia_en_all_maxi_2026-02.zim wikipedia_old.zim
wget -c https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_<NEW-DATE>.zim

# Update the systemd service inside the LXC to point at the new filename
pct exec 102 -- nano /etc/systemd/system/kiwix.service

# Restart and verify, then delete the old file
pct exec 102 -- systemctl daemon-reload
pct exec 102 -- systemctl restart kiwix
rm wikipedia_old.zim
```

## Troubleshooting

### Library shows "No result"

You probably have a stale filter in the URL or cookies. The library search filters by ZIM title, not article content. Solutions:

- Clear the URL: navigate to plain `http://<IP>:8080/`
- Click the "reset filter" link if shown
- Hard refresh: Cmd+Shift+R (Mac) / Ctrl+Shift+R (Windows)
- Try in private/incognito window

### "Permission denied" on the ZIM file inside the LXC

Make the file world-readable on the host:

```bash
chmod -R o+rX /mnt/pve/tank/zim
```

The `nobody:nogroup` ownership inside an unprivileged LXC is normal — it's a UID mapping artifact, not a permission problem. As long as world-read permissions are set, Kiwix can read the file.

### Service fails to start

Check the logs:

```bash
journalctl -u kiwix --no-pager -n 50
```

Common causes:
- ZIM filename in the service file doesn't match the actual file
- Bind mount didn't apply (verify with `ls /data` inside the LXC)
- ZIM file is corrupt (re-download with `wget -c` to resume)

### Want a static IP instead of DHCP

Either configure DHCP reservation in your router (cleaner — keeps IP management centralised) or set a static IP in the LXC's network config:

```bash
nano /etc/pve/lxc/102.conf
```

Change the `net0` line from `ip=dhcp` to `ip=192.168.0.54/24,gw=192.168.0.1` (adjust for your network).

## What This Gets You

- **115GB of human knowledge** sitting on your hardware
- **Zero internet dependency** to access it
- **Sub-second search** across 6.7M articles
- **Available to every device on your network**
- **Free forever** — no subscription, no rate limits, no ads

If your ISP went down tomorrow, Wikipedia still works. If Wikipedia ever changed/disappeared, you have a snapshot. If you go off-grid camping with the homelab box, you bring all of human knowledge with you.

## Architectural Pattern

This setup demonstrates a reusable Proxmox pattern:

1. **App in LXC** — fast storage, disposable
2. **Data on bulk storage** — durable, survives LXC changes
3. **Bind mount** connects them, read-only when possible
4. **systemd service** for autostart and crash recovery
5. **Single-purpose LXC** — easy to reason about, easy to rebuild

Same pattern works for Jellyfin (media), Audiobookshelf (books), Samba (file sharing), and most self-hosted services.

## Credits

- [Kiwix Foundation](https://kiwix.org/) — maintains the ZIM format and serves the content
- [Wikimedia](https://wikimedia.org/) — Wikipedia content
- [Proxmox VE](https://www.proxmox.com/) — virtualization platform
