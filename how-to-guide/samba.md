# Samba

Samba file sharing in an LXC on Proxmox. Handles Mac Time Machine backups and a general file share from a single container.

## Setup

### 1. Create folders on the host

Create your Time Machine and media folders on bulk storage before creating the LXC.

### 2. Create the LXC

- **Unprivileged:** ticked
- **Disk:** 4GB
- **CPU:** 1 core
- **Memory:** 512 MiB + 512 MiB swap

### 3. Add bind mounts

```bash
pct stop <CTID>
nano /etc/pve/lxc/<CTID>.conf
```

Add at the bottom (adjust paths to your folders):

```
mp0: /path/to/timemachine,mp=/tm
mp1: /path/to/media,mp=/media
```

```bash
pct start <CTID>
```

### 4. Install Samba and Avahi

```bash
pct enter <CTID>
apt update && apt upgrade -y
apt install samba avahi-daemon -y
```

### 5. Create the Samba user

```bash
useradd -M -s /usr/sbin/nologin <username>
smbpasswd -a <username>
```

### 6. Set ownership from the host

Unprivileged LXCs map UIDs — container UID 1000 = host UID 101000. Run from the Proxmox host, not inside the LXC:

```bash
exit
chown -R 101000:101000 /path/to/timemachine
chown -R 101000:101000 /path/to/media
```

### 7. Configure Samba

```bash
pct enter <CTID>
> /etc/samba/smb.conf
nano /etc/samba/smb.conf
```

```ini
[global]
   workgroup = WORKGROUP
   server string = %h homelab
   server role = standalone server
   server min protocol = SMB2
   ea support = yes
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
   valid users = <username>
   read only = no
   browseable = yes
   writable = yes
   create mask = 0600
   directory mask = 0700
   fruit:time machine = yes
   fruit:time machine max size = 2T

[Media]
   path = /media
   valid users = <username>
   read only = no
   browseable = yes
   writable = yes
   create mask = 0664
   directory mask = 0775
```

Test config: `testparm`

### 8. Configure Avahi

```bash
nano /etc/avahi/services/samba.service
```

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

`adVN=TimeMachine` must exactly match the `[TimeMachine]` share name — case-sensitive.

### 9. Start everything

```bash
systemctl restart smbd nmbd avahi-daemon
systemctl enable smbd nmbd avahi-daemon
exit
```

## Connecting from Mac

Finder → **Network** → connect to the Samba host → log in with your Samba credentials. For Time Machine: **System Settings → General → Time Machine → Add Backup Disk** → select `TimeMachine` → enable encryption.

## Verify

```bash
pct exec <CTID> -- systemctl status smbd --no-pager
```

After the first backup starts: `pct exec <CTID> -- ls -lh /tm/` should show a `.sparsebundle`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `chown` fails inside LXC | Run from Proxmox host using mapped UIDs (101000) |
| `apt update` hangs | `pct set <CTID> --nameserver 1.1.1.1 && pct reboot <CTID>` |
| Share not in Finder | Check Avahi: `avahi-browse -t _smb._tcp` inside LXC |
| Time Machine unavailable after sleep | `sudo tmutil setdestination -p smb://<username>@<LXC-IP>/TimeMachine` |
