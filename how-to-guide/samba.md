# Samba LXC — Time Machine + Media Sharing

A single Samba LXC that handles both Mac Time Machine backups and a media file share. Same container, two purposes, one user account.

## What this gets you

- **Time Machine destination** — encrypted hourly Mac backups, capped at 2TB
- **Media share** — drag-drop folder for movies, TV, music, books, audiobooks
- **Bonjour discovery** — auto-appears in Finder sidebar on Mac
- Replaces a £300 Apple Time Capsule

## Architecture

```
Mac
 ├─ Time Machine → samba LXC → /mnt/pve/tank/timemachine/
 └─ Media drive  → samba LXC → /mnt/pve/tank/data/media/
```

One LXC, two bind mounts, two Samba shares.

## Prerequisites

- Proxmox host with bulk storage at `/mnt/pve/tank/`
- LXC will use ~4GB disk on `local-lvm`, ~512MB RAM

## Setup

### 1. Create folders on the host

```bash
mkdir -p /mnt/pve/tank/timemachine
mkdir -p /mnt/pve/tank/data/media/{movies,tv,music,books,audiobooks}
```

### 2. Create the LXC

In Proxmox web UI → **Create CT**:

- **CT ID:** `<CTID>` (pick the next free ID, e.g. 300)
- **Hostname:** `samba`
- **Unprivileged:** ticked
- **Template:** `ubuntu-24.04-standard`
- **Disk:** 4GB on `local-lvm`
- **CPU:** 1 core
- **Memory:** 512 MiB + 512 MiB swap
- **Network:** vmbr0, DHCP

> Replace `<CTID>` throughout the rest of this doc with the actual ID you chose.

### 3. Add bind mounts

```bash
pct stop <CTID>
nano /etc/pve/lxc/<CTID>.conf
```

Add at the bottom:

```
mp0: /mnt/pve/tank/timemachine,mp=/tm
mp1: /mnt/pve/tank/data/media,mp=/media
```

No `ro=1` — both shares need write access.

```bash
pct start <CTID>
```

### 4. Set DNS (if needed)

If `apt update` fails inside the LXC with DNS errors, set DNS explicitly:

```bash
pct set <CTID> --nameserver 1.1.1.1
pct reboot <CTID>
```

### 5. Install Samba and Avahi

```bash
pct enter <CTID>
apt update && apt upgrade -y
apt install samba avahi-daemon -y
```

### 6. Create the Samba user

```bash
useradd -M -s /usr/sbin/nologin samuel
smbpasswd -a samuel
```

Set a password — you’ll enter this once on the Mac, then macOS Keychain remembers it.

### 7. Set ownership (from the Proxmox HOST)

Unprivileged LXCs map UIDs. `chown` from inside the container will fail with “Operation not permitted” — you have to do it from the host using mapped UIDs.

Container UID 1000 = host UID 101000.

Exit the LXC and run from the Proxmox host:

```bash
exit
chown -R 101000:101000 /mnt/pve/tank/timemachine
chown -R 101000:101000 /mnt/pve/tank/data/media
```

Verify from inside the LXC:

```bash
pct exec <CTID> -- ls -la /tm
pct exec <CTID> -- ls -la /media
```

Should show `samuel samuel` as owner.

### 8. Configure Samba

Back inside the LXC:

```bash
pct enter <CTID>
> /etc/samba/smb.conf
nano /etc/samba/smb.conf
```

Paste:

```ini
[global]
   workgroup = WORKGROUP
   server string = %h homelab
   server role = standalone server
   log file = /var/log/samba/log.%m
   max log size = 1000
   logging = file
   panic action = /usr/share/samba/panic-action %d
   server min protocol = SMB2
   ea support = yes

   # macOS-friendly defaults
   vfs objects = catia fruit streams_xattr
   fruit:metadata = stream
   fruit:model = MacSamba
   fruit:posix_rename = yes
   fruit:veto_appledouble = no
   fruit:nfs_aces = no
   fruit:wipe_intentionally_left_blank_rfork = yes
   fruit:delete_empty_adfiles = yes
   spotlight = no

[TimeMachine]
   path = /tm
   valid users = samuel
   read only = no
   browseable = yes
   writable = yes
   create mask = 0600
   directory mask = 0700
   fruit:time machine = yes
   fruit:time machine max size = 2T

[Media]
   path = /media
   valid users = samuel
   read only = no
   browseable = yes
   writable = yes
   create mask = 0664
   directory mask = 0775
```

Test the config:

```bash
testparm
```

Should show no errors and list both shares.

### 9. Configure Avahi for Bonjour discovery

```bash
nano /etc/avahi/services/samba.service
```

Paste:

```xml
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi.dtd">
<service-group>
  <name replace-wildcards="yes">%h</name>

  <service>
    <type>_smb._tcp</type>
    <port>445</port>
  </service>

  <service>
    <type>_device-info._tcp</type>
    <port>0</port>
    <txt-record>model=TimeCapsule8,119</txt-record>
  </service>

  <service>
    <type>_adisk._tcp</type>
    <port>9</port>
    <txt-record>dk0=adVN=TimeMachine,adVF=0x82</txt-record>
    <txt-record>sys=waMa=0,adVF=0x100</txt-record>
  </service>
</service-group>
```

The `dk0=adVN=TimeMachine` MUST exactly match the share name `[TimeMachine]` in `smb.conf`. Case-sensitive.

### 10. Start everything

```bash
systemctl restart smbd nmbd avahi-daemon
systemctl enable smbd nmbd avahi-daemon
```

Verify all three are running:

```bash
systemctl status smbd nmbd avahi-daemon --no-pager
```

Exit the LXC:

```bash
exit
```

## Connecting from Mac

### Mount the shares

1. Open Finder → **Network** in sidebar
1. Wait ~30 seconds for `samba` to appear
1. Click → **Connect As…**
1. Username: `samuel`, password: from `smbpasswd`
1. Tick **Remember in keychain**
1. Both `TimeMachine` and `Media` shares appear

If Bonjour discovery is slow, manually connect with `Cmd+K` → `smb://<LXC-IP>`.

### Configure Time Machine

1. **System Settings** → **General** → **Time Machine**
1. **Add Backup Disk** → select `TimeMachine`
1. **Set Up Disk** → choose **Encrypt Backup**
1. Set encryption password (store in password manager — needed for restore)
1. First backup runs in background (hours), incrementals are quick

### Use the Media share

Drag-drop files from Finder. To auto-mount at login:

1. With Media share already mounted, open **System Settings** → **General** → **Login Items**
1. Click `+` → navigate to and select the Media share

Folder structure:

```
/media/
├── movies/
├── tv/
├── music/
├── books/
└── audiobooks/
```

## Verifying it works

After first backup runs for ~10 minutes:

```bash
pct exec <CTID> -- ls -lh /tm/
```

Should show a `.sparsebundle` (encrypted Time Machine container).

Watch backup progress:

```bash
watch -n 5 'pct exec <CTID> -- du -sh /tm/'
```

## Troubleshooting

### `chown` fails with “Operation not permitted”

You’re running it from inside the LXC. You can’t — unprivileged LXCs can’t change ownership of host files. Run from the Proxmox host using mapped UIDs (100000 + container UID).

### `apt update` hangs at 0%

DNS issue inside the LXC. Fix from the host:

```bash
pct set <CTID> --nameserver 1.1.1.1
pct reboot <CTID>
```

### Share doesn’t appear in Finder sidebar

Avahi might not be advertising. Check inside LXC:

```bash
avahi-browse -t _smb._tcp
```

Should list `samba`. If not, restart `avahi-daemon`.

### Time Machine “backup disk not available” after Mac sleep

Reconnect via terminal:

```bash
sudo tmutil setdestination -p smb://samuel@<LXC-IP>/TimeMachine
```

### Slow first backup

Normal. Expected speeds:

- Wired Gigabit: 80–100 MB/s
- WiFi 5: 30–60 MB/s
- WiFi 6: 50–100 MB/s

Subsequent backups are incremental (minutes).

## Why this design

**One LXC, multiple shares** — simpler than two separate LXCs:

- One service to maintain, one user, one config
- Shares stay independent (different permissions, sizes, options)
- Time Machine settings isolated from media (different VFS modules per-share)

**Different masks per share:**

- Time Machine: `0600/0700` — strictly private
- Media: `0664/0775` — group-readable so Jellyfin (later) can read

**Bind mounts, not network protocols** for service-to-storage:

- Apps that need media access (e.g., Jellyfin) get their OWN bind mount to `/mnt/pve/tank/data/media/`
- They don’t go through Samba — that’s only for Mac access
- Direct kernel access, no overhead

## Key gotchas

- `chown` on bind-mounted folders only works from the Proxmox host with mapped UIDs
- Avahi `adVN=` value must exactly match the SMB share name (case-sensitive)
- `fruit:time machine max size` prevents Time Machine eating the whole drive
- `spotlight = no` disables Spotlight indexing (eats CPU, not needed for backups)
- `.local` suffix is mDNS/Bonjour, separate from your router’s `.lan` domain — both work, no conflict
