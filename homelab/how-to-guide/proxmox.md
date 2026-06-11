# Proxmox

Essential steps after a fresh Proxmox VE install — fix repositories and update.

## Setup

### 1. Access the web UI

Open `https://<host-IP>:8006`, accept the cert warning, log in as `root` with Linux PAM authentication.

### 2. Open the Shell

Click your node in the left sidebar → **Shell**.

### 3. Disable enterprise repositories

```bash
nano /etc/apt/sources.list.d/pve-enterprise.sources
```

Add at the bottom: `Enabled: false`. Repeat for Ceph:

```bash
nano /etc/apt/sources.list.d/ceph.sources
```

### 4. Add the no-subscription repository

```bash
nano /etc/apt/sources.list.d/pve-no-subscription.sources
```

```
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
```

`trixie` = Proxmox 9. Use `bookworm` for Proxmox 8.

### 5. Update the system

```bash
apt update
apt dist-upgrade -y
reboot
```

Use `dist-upgrade`, not `upgrade` — it handles kernel updates correctly.

### 6. Reserve a static IP at your router

Find your Proxmox node in your router's DHCP device list and create a static lease for its current IP.

### 7. Add additional drives

**Node → Disks → Wipe Disk** on any drive with leftover data first, then add as storage:

- **LVM-Thin** — for VM/LXC disks on fast drives (NVMe/SSD)
- **Directory** — for ISOs, backups, and bulk storage

## Verify

```bash
apt update       # No 401 errors
pveversion
df -h
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `apt update` returns 401 | Check both `.sources` files have `Enabled: false` |
| New drive doesn't appear | Wipe it first via Node → Disks → Wipe Disk |
| Lost access after reboot | Check router for new IP, then set a static lease |
