# Kiwix LXC — Offline Wikipedia + Knowledge

A Kiwix LXC that serves offline Wikipedia (and other ZIM files) over your local network. Same pattern as Samba: small LXC, bind mount to bulk storage, systemd service.

## What this gets you

- **Offline Wikipedia** — full English with images (~115GB), accessible from any device on LAN
- **Other ZIMs** — Stack Overflow, Wikivoyage, Wiktionary, ArchWiki, Stack Exchange sites
- **Survives internet outages** — knowledge stays accessible when the WAN is down
- **Read-only by design** — bind mount prevents accidental writes to bulk storage

## Architecture

```
LAN devices (browsers)
 ↓ HTTP :8080
Kiwix LXC
 ↓ bind mount (read-only)
/mnt/pve/tank/zim/*.zim
```

One LXC, one bind mount, one systemd service serving all `.zim` files.

## Prerequisites

- Proxmox host with bulk storage at `/mnt/pve/tank/`
- ~120GB free for Wikipedia (or more for additional ZIMs)
- LXC will use ~4GB disk on `local-lvm`, ~512MB RAM
- Ubuntu 24.04 container template downloaded

## Setup

### 1. Download Wikipedia (or other ZIMs)

On the Proxmox host:

```bash
mkdir -p /mnt/pve/tank/zim
cd /mnt/pve/tank/zim
apt install aria2 screen -y
screen -S download
aria2c -x 16 -s 16 https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2026-02.zim
```

**Use `screen`.** Background downloads via `nohup` are fragile — exiting the shell can kill them and corrupt the file. With `screen`, press **Ctrl+A then D** to detach. Reattach with `screen -r download`.

Check https://download.kiwix.org/zim/wikipedia/ for the latest dated filename. Other ZIMs at https://download.kiwix.org/zim/.

### 2. Create the LXC

In Proxmox web UI → **Create CT**:

- **CT ID:** `<CTID>` (pick the next free ID, e.g. 102)
- **Hostname:** `kiwix`
- **Unprivileged:** ticked
- **Template:** `ubuntu-24.04-standard`
- **Disk:** 4GB on `local-lvm`
- **CPU:** 1 core
- **Memory:** 512 MiB + 512 MiB swap
- **Network:** vmbr0, DHCP

> Replace `<CTID>` throughout the rest of this doc with the actual ID you chose.

### 3. Add the bind mount

```bash
pct stop <CTID>
nano /etc/pve/lxc/<CTID>.conf
```

Add at the bottom:

```
mp0: /mnt/pve/tank/zim,mp=/data,ro=1
```

`ro=1` makes the mount read-only — Kiwix only needs to read ZIMs, never write.

```bash
pct start <CTID>
pct exec <CTID> -- ls -lh /data
```

The ZIM files should be visible. If you see “permission denied”:

```bash
chmod -R o+rX /mnt/pve/tank/zim
```

### 4. Set DNS (if needed)

If `apt update` fails inside the LXC with DNS errors, set DNS explicitly:

```bash
pct set <CTID> --nameserver 1.1.1.1
pct reboot <CTID>
```

### 5. Install Kiwix

```bash
pct enter <CTID>
apt update && apt upgrade -y
apt install kiwix-tools -y
```

### 6. Create the systemd service

```bash
nano /etc/systemd/system/kiwix.service
```

Paste:

```ini
[Unit]
Description=Kiwix Serve - Offline Wikipedia and knowledge
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

The `/bin/bash -c '...'` wrapper is **required**. systemd doesn’t expand glob patterns like `*.zim` directly — without the wrapper, kiwix-serve receives the literal string `*.zim` and fails.

### 7. Start everything

```bash
systemctl daemon-reload
systemctl enable kiwix
systemctl start kiwix
systemctl status kiwix --no-pager
```

Look for green `Active: active (running)`. Exit the LXC:

```bash
exit
```

## Connecting from any device

Open `http://<LXC-IP>:8080` in any browser on your network.

You’ll see one tile per ZIM file. **The library search filters tiles by ZIM title, not articles within them.** To search Wikipedia articles, click the Wikipedia tile to enter Wikipedia, then use Wikipedia’s own search bar at the top.

## Verifying it works

```bash
pct exec <CTID> -- systemctl status kiwix --no-pager
pct exec <CTID> -- ls -lh /data
```

Service should be `active (running)` and `/data` should list your ZIM files. From a browser, `http://<LXC-IP>:8080` should show the Kiwix library.

## Adding more ZIMs

Drop new `.zim` files into `/mnt/pve/tank/zim/` on the host. The wildcard in `ExecStart` picks them up automatically — just restart:

```bash
pct exec <CTID> -- systemctl restart kiwix
```

**Test new ZIMs individually first.** A single corrupt ZIM in the wildcard makes kiwix-serve fail entirely. Verify before relying:

```bash
pct exec <CTID> -- kiwix-serve --port=8081 /data/<new-file>.zim
```

If it loads cleanly (visit `http://<LXC-IP>:8081`), it’s safe. Press Ctrl+C and add to the main service.

## Updating Wikipedia

```bash
cd /mnt/pve/tank/zim
screen -S update
aria2c -x 16 -s 16 https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_<NEW-DATE>.zim
# Ctrl+A, D to detach
# Wait for completion, then:
rm wikipedia_en_all_maxi_<OLD-DATE>.zim
pct exec <CTID> -- systemctl restart kiwix
```

The wildcard `ExecStart` means no service edits needed — it picks up whatever `.zim` files are present.

## Troubleshooting

### Service fails to start with status=1/FAILURE

Almost always one of three causes:

1. **Glob not wrapped in bash** — check `ExecStart` includes `/bin/bash -c '...'`
1. **Corrupt ZIM in `/data`** — one bad file kills the whole service. Check logs: `journalctl -u kiwix -n 50 --no-pager`
1. **Bind mount didn’t apply** — `pct exec <CTID> -- ls /data` should list ZIMs. If empty, recheck `/etc/pve/lxc/<CTID>.conf`.

### “Internal Server Error — Assertion failed at cluster.cpp”

The ZIM file is corrupt. Almost always from an interrupted download. Move it aside:

```bash
mkdir -p /mnt/pve/tank/zim/parked
mv /mnt/pve/tank/zim/<bad-file>.zim /mnt/pve/tank/zim/parked/
pct exec <CTID> -- systemctl restart kiwix
```

Then re-download with `screen` so the next attempt survives shell exits.

### Library shows “No result”

Stale URL filter from a previous search (`?q=something` in the URL). Navigate to clean `http://<LXC-IP>:8080/` or open in a private window.

### `apt update` hangs at 0%

DNS issue inside the LXC. Fix from the host:

```bash
pct set <CTID> --nameserver 1.1.1.1
pct reboot <CTID>
```

### `nobody:nogroup` ownership inside the LXC

Normal for unprivileged containers — UID mapping artifact. As long as the host has world-read permissions (`-rw-r--r--`), the LXC can read fine. Don’t `chown` to fix it.

### `.aria2` files left over after a download

aria2c keeps `.aria2` files as resume metadata. Only safe to delete after the download log shows “Download complete”. Otherwise the partial file is unrecoverable garbage even if the size looks right.

## Why this design

**Bind mount to bulk storage** instead of putting ZIMs inside the LXC:

- LXC stays tiny (4GB root disk) and disposable
- Nuke and rebuild the container without losing 100GB+ of ZIMs
- Same pattern as Samba and other storage-consuming services

**Read-only bind mount (`ro=1`):**

- Kiwix never writes — no reason to allow it
- Defence in depth against bugs or compromised containers

**Wildcard `/data/*.zim`:**

- Adding new ZIMs requires zero service edits
- Just drop the file in, restart, done
- Trade-off: one corrupt file kills the whole service (test individually first)

**Single LXC for all ZIMs** instead of one per topic:

- One service to maintain
- One bookmark for users
- All knowledge in one place

## Key gotchas

- systemd doesn’t expand globs — wrap `*.zim` in `/bin/bash -c '...'`
- One corrupt ZIM in the wildcard kills the whole service
- Always use `screen` for downloads >5 minutes — `nohup` is fragile
- Don’t delete `.aria2` files until the download log confirms completion
- `nobody:nogroup` ownership inside unprivileged LXCs is normal, not a bug
- Library search filters ZIMs by title, not articles within them
- Stack Overflow ZIM hasn’t been regenerated since 2023-11 (still useful, just not current)
