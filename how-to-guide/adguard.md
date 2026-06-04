# AdGuard Home LXC

Network-wide DNS filtering in an LXC on Proxmox. Blocks ads, trackers, and malware for every device on the LAN.

## Setup

### 1. Create the LXC

- **Unprivileged:** ticked
- **Disk:** 4GB
- **CPU:** 1 core
- **Memory:** 512 MiB + 512 MiB swap
- **IP:** Static — DNS servers need a fixed address

### 2. Update packages

```bash
apt update && apt upgrade -y && apt install curl wget -y
```

If `apt update` hangs, fix DNS from the host:

```bash
pct set <CTID> --nameserver 1.1.1.1 && pct reboot <CTID>
```

### 4. Disable systemd-resolved

Ubuntu's stub resolver occupies port 53. Free it before installing AdGuard:

```bash
systemctl disable systemd-resolved --now
rm /etc/resolv.conf
echo "nameserver 1.1.1.1" > /etc/resolv.conf
echo "nameserver 9.9.9.9" >> /etc/resolv.conf
```

### 5. Install AdGuard Home

```bash
curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sh -s -- -v
```

### 6. Run the setup wizard

Open `http://<LXC-IP>:3000`. Accept defaults, set an admin username and password, skip the device config step.

### 7. Add blocklists

**Filters → DNS blocklists → Add blocklist → Choose from the list:**

- AdGuard DNS filter
- EasyList
- EasyPrivacy
- OISD Big

### 8. Set encrypted upstream DNS

**Settings → DNS settings → Upstream DNS servers:**

```
https://dns.cloudflare.com/dns-query
https://dns.quad9.net/dns-query
tls://1.1.1.1
tls://9.9.9.9
```

Click **Test upstreams** then **Apply**.

### 9. Point your router at AdGuard

In your router's DHCP/LAN settings, set Primary DNS to the AdGuard LXC IP. Leave Secondary blank — traffic via secondary bypasses filtering.

## Verify

```bash
pct exec <CTID> -- systemctl status AdGuardHome --no-pager
```

From any device, `nslookup doubleclick.net` should return `0.0.0.0`. The dashboard should show live query traffic.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `apt update` hangs | `pct set <CTID> --nameserver 1.1.1.1 && pct reboot <CTID>` |
| Port 53 already in use | `systemd-resolved` still running — redo step 4 |
| Devices not using AdGuard | Force DHCP lease renewal on each device |
| Sites broken after enabling | Check Query Log, whitelist with `@@\|\|example.com^` |
| Web UI not loading | `journalctl -u AdGuardHome -n 50 --no-pager` inside LXC |
