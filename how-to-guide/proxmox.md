# Proxmox Post-Install Setup Guide

This guide picks up after the Proxmox VE installer finishes (so you've booted into your fresh install, pulled the USB, and can log into the web UI at `https://<your_ip>:8006`). It covers the essential post-install steps: fixing the repositories, running updates, removing the subscription nag, and adding additional drives as usable storage.

## 1. Access the Web UI

On another machine on the same network, open a browser and go to:
```
https://<your_proxmox_ip>:8006
```

You'll get a certificate warning because Proxmox uses a self-signed cert — this is expected. Click **Advanced** → **Proceed**.

Log in with:
- **User name:** `root`
- **Password:** the one you set during install
- **Realm:** `Linux PAM standard authentication`

## 2. Open the Shell

In the web UI, click your node (e.g. `pve`) in the left sidebar, then click **Shell** in the middle panel. This gives you a root terminal directly in the browser — no SSH setup needed.

Proxmox logs you in as `root` by default, so you don't need `sudo` for any commands.

## 3. Disable Enterprise Repositories

Proxmox ships pointing at the paid enterprise repos. Without disabling them, updates fail with `401 Unauthorized`.

Proxmox 9 uses the new `.sources` format, so we add `Enabled: false` to each enterprise file.

Open the first file:
```bash
nano /etc/apt/sources.list.d/pve-enterprise.sources
```

Add a new line at the bottom:
```
Enabled: false
```

Save and exit: **Ctrl+O**, Enter, **Ctrl+X**.

Do the same for the Ceph enterprise repo:
```bash
nano /etc/apt/sources.list.d/ceph.sources
```

Add `Enabled: false` at the bottom, save, exit.

## 4. Add the No-Subscription Repository

Create a new file for the free community repo:
```bash
nano /etc/apt/sources.list.d/pve-no-subscription.sources
```

Paste in:
```
Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
```

Save and exit.

`trixie` is Debian 13, used by Proxmox 9. On Proxmox 8, use `bookworm` instead.

## 5. Update the System

Refresh package lists:
```bash
apt update
```

Run the full upgrade:
```bash
apt dist-upgrade -y
```

Use `dist-upgrade`, not `upgrade` — it handles kernel updates properly.

Reboot to pick up the new kernel:
```bash
reboot
```

Wait ~60 seconds, refresh your browser, log back in.

## 6. Remove the Subscription Nag

Every login pops up a "No valid subscription" dialog. To remove it:
```bash
sed -i.bak "s/data.status.*{/data.status \!== 'Active'){/g" /usr/share/javascript/proxmox-widget-toolkit/proxmoxlib.js && systemctl restart pveproxy.service
```

Hard-refresh your browser (Cmd+Shift+R / Ctrl+Shift+R). Re-run the command after major Proxmox updates if it comes back.

## 7. Reserve a Static IP at Your Router

Proxmox's IP shouldn't change. The cleanest way is a DHCP reservation at your router:
1. Log into your router's admin page (usually `192.168.1.1` or `192.168.0.1`)
2. Find DHCP reservations / static leases
3. Find your Proxmox node in the connected devices list
4. Reserve its current IP

## 8. Wipe Additional Drives

If you have a second drive with leftover data (e.g. an old install), wipe it from the web UI:
1. Click your node in the sidebar → **Disks**
2. Select the drive (e.g. `sda`)
3. Click **Wipe Disk** at the top
4. Confirm

Do not wipe the drive Proxmox is installed on.

## 9. Add Drives as Storage

Once wiped, add the drive as usable Proxmox storage. Pick a storage type based on what you plan to use it for.

**LVM-Thin** — for holding VM and LXC disks. Thin-provisioned, snapshot-capable, efficient. Best for fast drives (NVMe/SSD) where VMs will run.

**Directory** — for ISOs, backups, templates. Simple filesystem (ext4) on top of the drive. Best for bulk storage where speed doesn't matter.

**ZFS** — advanced option offering checksumming, snapshots, compression, and built-in RAID. Requires more RAM (roughly 1GB per 1TB of storage) and is most useful when you have **two or more drives to mirror**. Overkill for a single-drive home setup. ZFS pools can be created from **Disks → ZFS → Create: ZFS**.

For a typical homelab with one NVMe + one SATA SSD, the sensible split is:
- **NVMe** → LVM-Thin for VMs/LXCs (set up automatically by installer)
- **SATA** → Directory for ISOs and backups

## 10. Upload or Download ISOs

Before building a VM, you need an operating system ISO. In the web UI:
- Click your node → expand the storage set up for ISOs (usually `local` or your new Directory)
- Click **ISO Images** → **Upload** to upload one from your computer
- Or click **Download from URL** to pull directly from the internet

Handy ISO sources:
- **Windows 11**: microsoft.com (download directly)
- **VirtIO drivers** (needed for Windows VMs): `https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso`
- **Ubuntu Server**: `https://ubuntu.com/download/server`
- **Debian**: `https://www.debian.org/distrib/`
- **LXC templates** (for containers): Proxmox has built-in downloads under **CT Templates → Templates**

## 11. You're Done

Proxmox is fully set up. From here you can create VMs or LXC containers through the web UI.

Rule of thumb: LXC for lightweight Linux services (Pi-hole, Nginx, Docker host), VM for Windows or when you need full kernel-level isolation.
