# Proxmox Post-Install Setup

Essential post-install steps for a fresh Proxmox VE: fix repositories, run updates, remove the subscription nag, and add additional drives as usable storage.

## What this gets you

- Working `apt update` (default repos fail with 401 Unauthorized)
- Latest packages and kernel
- No subscription nag dialog on every login
- Static IP reservation
- Additional drives added as storage for VMs/LXCs/ISOs

## Architecture

```
Proxmox host (pve)
├── NVMe          → local-lvm (VMs/LXCs)
├── SATA SSD      → Directory storage (ISOs, backups)
└── External HDD  → Directory storage (bulk data)
```

## Prerequisites

- Proxmox VE 8.x or 9.x installed and booted
- Web UI reachable at `https://<host-IP>:8006`
- Root password set during install

## Setup

### 1. Access the Web UI

In a browser on another machine on the same network:

```
https://<your-proxmox-IP>:8006
```

Accept the self-signed cert warning (**Advanced** → **Proceed**).

Log in with:

- **User name:** `root`
- **Password:** the one set during install
- **Realm:** `Linux PAM standard authentication`

### 2. Open the Shell

In the web UI, click your node (e.g. `pve`) in the left sidebar → click **Shell** in the middle panel. This gives you a root terminal in the browser. No `sudo` needed.

### 3. Disable enterprise repositories

Proxmox 9 uses the new `.sources` format. Add `Enabled: false` to each enterprise file.

```bash
nano /etc/apt/sources.list.d/pve-enterprise.sources
```

Add at the bottom:

```
Enabled: false
```

Save (Ctrl+X, Y, Enter). Repeat for the Ceph enterprise repo:

```bash
nano /etc/apt/sources.list.d/ceph.sources
```

Add `Enabled: false`, save, exit.

### 4. Add the no-subscription repository

```bash
nano /etc/apt/sources.list.d/pve-no-subscription.sources
```

Paste:

```
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
```

`trixie` = Debian 13 (Proxmox 9). On Proxmox 8, use `bookworm`.

### 5. Update the system

```bash
apt update
apt dist-upgrade -y
reboot
```

Use `dist-upgrade`, not `upgrade` — it handles kernel updates properly. Wait ~60 seconds after reboot, refresh browser, log back in.

### 6. Remove the subscription nag

```bash
sed -i.bak "s/data.status.*{/data.status \!== 'Active'){/g" /usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js && systemctl restart pveproxy.service
```

Hard-refresh the browser (Cmd+Shift+R / Ctrl+Shift+R). Re-run after major Proxmox updates if the nag returns.

### 7. Reserve a static IP at your router

1. Log into your router’s admin page (`192.168.1.1` or `192.168.0.1`)
1. Find DHCP reservations / static leases
1. Find your Proxmox node in the device list
1. Reserve its current IP

### 8. Wipe additional drives

If a second drive has leftover data from an old install:

1. Click your node in the sidebar → **Disks**
1. Select the drive (e.g. `sda`)
1. Click **Wipe Disk** at the top
1. Confirm

Do not wipe the drive Proxmox is installed on.

### 9. Add drives as storage

Pick a storage type based on intended use:

- **LVM-Thin** — for VM/LXC disks. Thin-provisioned, snapshot-capable. Best for fast drives (NVMe/SSD) where VMs run.
- **Directory** — for ISOs, backups, templates. ext4 on top of the drive. Best for bulk storage where speed doesn’t matter.
- **ZFS** — checksumming, snapshots, compression, built-in RAID. Needs ~1GB RAM per 1TB. Most useful with two or more drives to mirror. Overkill for single-drive setups. Create from **Disks** → **ZFS** → **Create: ZFS**.

For a typical homelab with one NVMe + one SATA SSD:

- **NVMe** → LVM-Thin for VMs/LXCs (set up automatically by installer)
- **SATA** → Directory for ISOs and backups

### 10. Upload or download ISOs

In the web UI:

- Click your node → expand the storage set up for ISOs (usually `local` or your new Directory)
- Click **ISO Images** → **Upload** (from your computer) or **Download from URL** (direct)

Useful sources:

- **Windows 11**: microsoft.com
- **VirtIO drivers** (for Windows VMs): `https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso`
- **Ubuntu Server**: `https://ubuntu.com/download/server`
- **Debian**: `https://www.debian.org/distrib/`
- **LXC templates**: built into Proxmox under **CT Templates** → **Templates**

## Verifying it works

```bash
apt update            # No 401 errors, lists pve-no-subscription repo
pveversion            # Shows current Proxmox version
df -h                 # All storage mounted and visible
```

In the web UI, check:

- No subscription nag on login
- All drives visible under **Datacenter** → **Storage**

## Troubleshooting

### `apt update` returns 401 Unauthorized

Enterprise repo still enabled. Check `pve-enterprise.sources` and `ceph.sources` both have `Enabled: false` at the bottom.

### Subscription nag returns after Proxmox update

The patch in step 6 gets overwritten by major upgrades. Re-run the same command.

### New drive doesn’t appear

If the drive is brand new or has GPT/LVM remnants:

1. **Disks** → select drive → **Wipe Disk**
1. Then add it as storage

### Lost access after reboot

If the IP changed because no DHCP reservation was set, find the new IP via your router’s connected devices list. Then do step 7 properly.

## Why this design

**No-subscription repo** instead of paying for Enterprise:

- Same packages, slightly delayed release
- Fine for homelabs; Enterprise is for production support contracts

**Three-tier storage by role:**

- NVMe = compute (VM/LXC disks)
- SATA SSD = backups
- External HDD = bulk replaceable data

**Directory over ZFS for single drives:**

- ZFS only earns its keep with multiple disks
- Wastes RAM on single-disk setups
- ext4 is faster, simpler, and rock-solid for homelab scale

## Key gotchas

- Use `dist-upgrade`, not `upgrade` — kernel updates need it
- The `.sources` format is new in Proxmox 9 — old `.list` syntax won’t work
- Subscription nag patch must be re-run after every major Proxmox update
- LXC for lightweight Linux services (Pi-hole, Nginx, Docker host); VM for Windows or full kernel-level isolation
