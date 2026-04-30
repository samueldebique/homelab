# AdGuard Home LXC

Network-wide DNS filtering. Blocks ads, trackers, malware, and adult content for every device on your LAN — phones, TVs, IoT — without installing anything on each device.

## What this gets you

- **Network-wide ad blocking** — all DNS queries from your LAN filtered at one point
- **Tracker and malware blocking** — block lists from EasyList, EasyPrivacy, OISD, etc.
- **Per-device rules** — block YouTube on the kids’ tablet, allow on yours
- **Local DNS** — assign hostnames like `pve.lan` to your homelab IPs
- **Encrypted upstream DNS** — DoH/DoT to Cloudflare/Quad9, your ISP can’t snoop
- **Query log + stats** — see exactly what each device is asking for
- Replaces Pi-hole with a more polished UI and built-in DoH/DoT

## Architecture

```
LAN devices (phones, laptops, IoT, etc.)
 ↓ DNS queries (port 53)
Router (DHCP hands out AdGuard's IP as DNS)
 ↓
AdGuard LXC (192.168.0.x)
 ├── Filters via blocklists
 └── Forwards clean queries upstream (DoH/DoT to Cloudflare/Quad9)
```

LXC, not VM — AdGuard is a single Go binary, runs fine in a container.

## Prerequisites

- Proxmox VE 8.x or 9.x
- Ubuntu 24.04 container template downloaded
- ~4GB free on `local-lvm`
- Router that lets you set custom DNS server (most do)

## Setup

### 1. Create the LXC

In Proxmox web UI → **Create CT**:

- **CT ID:** `<CTID>` (pick the next free ID, e.g. 101)
- **Hostname:** `adguard`
- **Unprivileged:** ticked
- **Template:** `ubuntu-24.04-standard`
- **Disk:** 4GB on `local-lvm`
- **CPU:** 1 core
- **Memory:** 512 MiB + 512 MiB swap
- **Network:** vmbr0, **static IP** (see step 2 — DHCP doesn’t work for a DNS server)

> Replace `<CTID>` throughout the rest of this doc with the actual ID you chose.

### 2. Configure a static IP

AdGuard needs a fixed IP because every device on your network will be configured to use it as DNS. DHCP would change the IP and break everything.

In the **Create CT** wizard’s Network step (or after creation under **Network**):

- **IPv4:** Static
- **IPv4/CIDR:** `192.168.0.123/24` (pick something outside your DHCP range)
- **Gateway:** your router IP (e.g. `192.168.0.1`)
- **DNS** (in the DNS tab): `1.1.1.1` initially, so the LXC itself can resolve domains for `apt update`

Pick an IP in the static range your router lets you reserve. Common pattern: DHCP serves `.100–.200`, statics live in `.2–.99` or `.201–.254`.

### 3. Start and enter the LXC

```bash
pct start <CTID>
pct enter <CTID>
```

### 4. Update and install dependencies

```bash
apt update && apt upgrade -y
apt install curl wget -y
```

If `apt update` hangs at 0%, DNS issue. Set DNS explicitly from the host:

```bash
pct set <CTID> --nameserver 1.1.1.1
pct reboot <CTID>
```

### 5. Disable systemd-resolved

Ubuntu’s stub resolver listens on port 53, which conflicts with AdGuard. Disable it:

```bash
systemctl disable systemd-resolved --now
rm /etc/resolv.conf
echo "nameserver 1.1.1.1" > /etc/resolv.conf
echo "nameserver 9.9.9.9" >> /etc/resolv.conf
```

This frees port 53 for AdGuard and points the LXC’s own DNS at Cloudflare + Quad9.

### 6. Install AdGuard Home

Use the official installer:

```bash
curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sh -s -- -v
```

This downloads, extracts, and installs AdGuard Home as a systemd service. Output ends with the URL for first-time setup.

### 7. Initial setup wizard

Open `http://<LXC-IP>:3000` in a browser (port 3000 is for setup, then it switches to 80).

1. **Welcome** — click Next
1. **Admin Web Interface** — leave defaults (port 80, all interfaces)
1. **DNS Server** — port 53, all interfaces
1. **Authentication** — set admin username and a strong password, store in password manager
1. **Configure Devices** — skip, we’ll do this at the router
1. **Open AdGuard Home** — log in with the credentials you just set

Exit the LXC:

```bash
exit
```

### 8. Add filter lists

In AdGuard web UI:

1. **Filters** → **DNS blocklists**
1. **Add blocklist** → **Choose from the list**
1. Tick at minimum:
- **AdGuard DNS filter** (default, already enabled)
- **EasyList**
- **EasyPrivacy**
- **OISD Big** — best general-purpose list
- **HaGeZi’s Pro DNS Blocklist** (optional, more aggressive)
1. **Save**

### 9. Configure upstream DNS (DoH/DoT)

For privacy, send queries upstream encrypted. **Settings** → **DNS settings** → **Upstream DNS servers** — replace the contents with:

```
https://dns.cloudflare.com/dns-query
https://dns.quad9.net/dns-query
tls://1.1.1.1
tls://9.9.9.9
```

This uses DNS-over-HTTPS to Cloudflare and Quad9, with DNS-over-TLS as fallback. Your ISP can no longer see what domains you’re resolving.

Click **Test upstreams** to verify they all work, then **Apply**.

### 10. Point your router at AdGuard

Now the critical step — make every device on your network use AdGuard:

1. Log into your router admin page (e.g. `192.168.0.1`)
1. Find **DHCP Settings** or **LAN Settings** → **DNS Servers**
1. Set **Primary DNS** to your AdGuard LXC IP (e.g. `192.168.0.123`)
1. Leave Secondary blank, OR set to `1.1.1.1` as a fallback (note: traffic via secondary won’t be filtered)
1. Save

Devices renew their DHCP lease over the next few hours. To force immediate update, restart your phone/laptop or toggle Wi-Fi off and on.

### 11. Verify filtering works

From a device on your network:

```bash
nslookup doubleclick.net
```

Should return `0.0.0.0` or fail to resolve — that’s AdGuard blocking it. If it returns a real IP, the device isn’t using AdGuard yet.

Or visit https://d3ward.github.io/toolz/adblock for an automated test.

## Verifying it works

In AdGuard web UI:

- **Dashboard** — should show queries flowing in real-time as your devices browse
- **Query Log** — every DNS query, color-coded (green = allowed, red = blocked)
- **Top clients** — should list your devices by IP/hostname

```bash
pct exec <CTID> -- systemctl status AdGuardHome --no-pager
```

Should show `active (running)`.

## Local DNS (optional but useful)

Assign friendly names to your homelab services:

1. **Filters** → **DNS rewrites**
1. **Add DNS rewrite**
1. Examples:
- Domain: `pve.lan` → Answer: `192.168.0.21`
- Domain: `kiwix.lan` → Answer: `192.168.0.54`
- Domain: `samba.lan` → Answer: `192.168.0.55`

Now `http://pve.lan:8006` resolves anywhere on your network without messing with `/etc/hosts` on every device.

## Per-device rules (optional)

Block specific domains for specific devices:

1. **Settings** → **Client settings** → **Add client**
1. Identifier: device’s IP or MAC address
1. Tags: name it (e.g. “kids-tablet”)
1. Set custom blocked services for that client (YouTube, TikTok, gambling sites, etc.)

## Troubleshooting

### `apt update` hangs at 0%

DNS issue inside the LXC. Fix from the host:

```bash
pct set <CTID> --nameserver 1.1.1.1
pct reboot <CTID>
```

### AdGuard installer fails with “port 53 already in use”

`systemd-resolved` still running. See step 5 — disable it and remove its stub `resolv.conf`.

### Devices not using AdGuard after router change

DHCP leases haven’t renewed. Force one device to test:

- **Mac:** System Settings → Wi-Fi → Details → DHCP Lease → Renew
- **iPhone:** Settings → Wi-Fi → tap your network → Renew Lease
- **Windows:** `ipconfig /release` then `ipconfig /renew` in cmd

Verify on the device:

```bash
scutil --dns | grep nameserver        # macOS
ipconfig /all | findstr DNS           # Windows
```

Should show your AdGuard IP.

### AdGuard web UI not loading

Service crashed or didn’t start. Check inside LXC:

```bash
pct exec <CTID> -- systemctl status AdGuardHome --no-pager
pct exec <CTID> -- journalctl -u AdGuardHome -n 50 --no-pager
```

Common cause: port 53 conflict with `systemd-resolved` (re-do step 5).

### Some sites broken after enabling filtering

Filter list too aggressive. Check **Query Log** for the blocked domain, then either:

- **Whitelist:** Filters → Custom filtering rules → add `@@||example.com^`
- **Disable a list:** Filters → DNS blocklists → toggle off whichever is too eager (HaGeZi Pro is usually the culprit)

### Slow DNS resolution after install

Probably the upstream DoH/DoT servers being slow to handshake. Check:

- **Settings** → **DNS settings** → **DNS cache configuration** → bump cache size to `4194304` (4MB)
- Or fall back to plain `1.1.1.1` and `9.9.9.9` if DoH is unreliable on your network

## Why this design

**LXC, not VM** — AdGuard is a single Go binary, no kernel needs. LXC is lighter (less RAM, faster boot) and shares the host kernel cleanly.

**Static IP** — every device on your network is configured to use this IP as DNS. If it changed, the entire LAN loses internet.

**DoH/DoT upstream** — your ISP can see WHICH SERVER you’re asking, but not WHICH DOMAIN. Combined with HTTPS for actual web traffic, your browsing history is opaque to your ISP.

**Disable systemd-resolved** — Ubuntu’s stub resolver squats on port 53, which is what AdGuard needs. Either runs alone, not both.

**Filter at DNS, not at HTTP/HTTPS:**

- Works for every protocol (apps, IoT, smart TVs, not just browsers)
- No certificate trust required
- Single chokepoint = single config
- Trade-off: can’t block based on URL path, only domain. CSS/script-level blocking still needs uBlock Origin in the browser.

## Key gotchas

- AdGuard needs a **static IP** — DHCP would break every device on your network
- `systemd-resolved` MUST be disabled — it squats on port 53
- After changing router DNS, devices take hours to pick it up unless you force-renew leases
- **Don’t set Secondary DNS to `1.1.1.1` blindly** — traffic via secondary bypasses filtering. Either leave blank or accept the bypass.
- Test sites you actually use after enabling — overly aggressive lists break things (banking, ticket sites, some Microsoft services)
- AdGuard’s port 3000 is for **first-time setup only**. After that, the UI moves to port 80.
- DNS rewrites only work for devices using AdGuard as DNS — won’t override hardcoded DNS on smart TVs etc.
