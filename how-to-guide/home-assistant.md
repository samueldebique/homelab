# Home Assistant OS VM

Home Assistant OS running as a VM on Proxmox. VM (not LXC) because HAOS is a full appliance OS with its own supervisor — it expects to control the kernel.

## What this gets you

- **Smart home hub** — Zigbee/Z-Wave/Wi-Fi/Matter/Thread device control in one place
- **Local-first** — works without cloud accounts, processes locally
- **Add-ons** — one-click installs for MQTT, Node-RED, ESPHome, AdGuard, etc. (managed by HAOS supervisor, separate from your other LXCs)
- **Web UI + companion apps** — accessible from any device on LAN, plus iOS/Android apps with notifications
- **Survives Proxmox reboots** — auto-starts with the host

## Architecture

```
Phones / tablets / browsers
 ↓ HTTP :8123
Home Assistant OS (VM)
 ├── Supervisor (manages add-ons)
 ├── Core (the HA app itself)
 └── Add-ons (MQTT broker, Node-RED, ESPHome, etc.)
 ↓ Zigbee/Z-Wave (USB stick passthrough, optional)
 ↓ LAN (Wi-Fi/Matter devices)
```

VM, not LXC — HAOS is an appliance and won’t run in an LXC.

## Prerequisites

- Proxmox VE 8.x or 9.x
- ~32GB free on `local-lvm` (HAOS image is ~6GB, give it room to grow)
- 2GB+ RAM available to dedicate to the VM
- Optional: USB Zigbee/Z-Wave dongle for direct device control

## Setup

### 1. Download the HAOS image

In the Proxmox web UI, click your node → **Shell**:

```bash
cd /var/lib/vz/template/iso
wget https://github.com/home-assistant/operating-system/releases/latest/download/haos_ova-latest.qcow2.xz
xz -d haos_ova-latest.qcow2.xz
```

The download URL pattern stays stable — `haos_ova-latest` always points at the newest release. Decompressing produces `haos_ova-latest.qcow2`.

For the exact latest version number, check https://github.com/home-assistant/operating-system/releases.

### 2. Create an empty VM

In Proxmox web UI → **Create VM**:

**General**

- **VM ID:** `<VMID>` (pick the next free ID, e.g. 100)
- **Name:** `homeassistant`

> Replace `<VMID>` throughout the rest of this doc with the actual ID you chose.

**OS**

- **Do not use any media** (we’ll attach the qcow2 manually)
- **Guest OS:** Linux, 6.x - 2.6 Kernel

**System**

- **Machine:** `q35`
- **BIOS:** `OVMF (UEFI)`
- **Add EFI Disk:** ticked, on `local-lvm`
- **Pre-Enroll keys:** ticked

**Disks**

- Delete the default disk (we’ll import the qcow2 next)

**CPU**

- **Cores:** `2`
- **Type:** `host`

**Memory**

- **Memory:** `2048` MiB (2GB)

**Network**

- **Bridge:** `vmbr0`
- **Model:** `VirtIO (paravirtualized)`

Click Finish but **do not start the VM yet**.

### 3. Import the HAOS image

In the Proxmox shell:

```bash
qm importdisk <VMID> /var/lib/vz/template/iso/haos_ova-latest.qcow2 local-lvm
```

This imports the qcow2 as a disk attached to the VM (initially as “Unused Disk 0”).

### 4. Attach the imported disk

In the web UI:

1. Click your VM → **Hardware**
1. You’ll see “Unused Disk 0” — double-click it
1. Bus: `SATA`, set as boot device
1. Click **Add**

### 5. Configure boot order

1. **Hardware** → **Options** → **Boot Order**
1. Tick the SATA disk (the imported HAOS image)
1. Drag it to the top
1. Save

### 6. Optional: pass through a USB Zigbee/Z-Wave dongle

If you have a USB stick (e.g. Sonoff Zigbee 3.0, Conbee II):

1. Plug it into the Proxmox host
1. **Hardware** → **Add** → **USB Device**
1. Select **Use USB Vendor/Device ID** (more stable than port number across reboots)
1. Pick your dongle from the list
1. Save

### 7. Start the VM

Click **Start**. Open the **Console** tab to watch HAOS boot. First boot takes 5–10 minutes — it’s downloading the supervisor and core.

When ready you’ll see something like:

```
homeassistant login:
```

And below it: `http://homeassistant.local:8123` or `http://<VM-IP>:8123`.

### 8. Initial setup in the web UI

Open `http://homeassistant.local:8123` (or the VM’s IP if Bonjour is slow).

1. Wait for the loading screen to finish (can take a few minutes)
1. Create your admin account
1. Set location, units, currency
1. Allow or skip optional analytics
1. Click through device discovery — HAOS auto-finds devices on your network

### 9. Enable auto-start with Proxmox

In the web UI:

1. Click VM → **Options**
1. **Start at boot:** Yes
1. **Start/Shutdown order:** `1` (boots first when Proxmox starts)

## Verifying it works

```bash
qm status <VMID>
```

Should show `status: running`.

From any device on your LAN, `http://homeassistant.local:8123` should load the HA dashboard.

For the companion app:

- iOS: App Store → “Home Assistant”
- Android: Play Store → “Home Assistant”
- Sign in with your HA account, point it at `http://<VM-IP>:8123`

## Renaming the VM

To change the display name in Proxmox (cosmetic only, doesn’t affect HAOS internally):

1. Click VM → **Options** → **Name**
1. Edit and save

The HAOS hostname inside (`homeassistant`) can’t easily be changed — HAOS is a locked-down appliance OS. Just rename the Proxmox display label.

## Backups

HAOS has its own snapshot system separate from Proxmox. Use both:

- **HAOS snapshots** — Settings → System → Backups. Captures HA config, automations, add-on data. Great for “I’m about to do something risky in HA” rollbacks.
- **Proxmox VZDump** — full VM image backup. Captures everything (HAOS itself plus all data). Use for “the VM died, restore from scratch” scenarios.

Configure Proxmox backups under **Datacenter** → **Backup**. Schedule nightly to your backup storage.

## Troubleshooting

### VM won’t boot — black screen or “no bootable device”

Boot order or disk type wrong. Check:

1. **Hardware** — the imported HAOS disk should be SATA, not SCSI or VirtIO Block
1. **Options → Boot Order** — SATA disk ticked and at the top
1. **Options → BIOS** — must be OVMF (UEFI), not SeaBIOS

If still failing, the qcow2 import may have gone to the wrong storage. Verify with:

```bash
qm config <VMID>
```

You should see a line like `sata0: local-lvm:vm-<VMID>-disk-1,...`.

### `homeassistant.local` doesn’t resolve

Bonjour/mDNS issue on your network. Use the VM’s IP directly. Find it from the Proxmox console (login screen shows it) or from your router’s connected devices list.

### HA web UI loads but is extremely slow

VM is RAM-starved. Bump memory:

1. **Hardware** → **Memory** → edit
1. Bump to `4096` MiB (4GB)
1. Reboot the VM

### Zigbee/Z-Wave dongle disappears after Proxmox reboot

USB passthrough by port number breaks if you unplug/replug. Use **Vendor/Device ID** instead (step 6).

### Add-on store is empty

Supervisor still finishing first-time setup. Wait 10 minutes after first boot. If still empty, check **Settings** → **System** → **Logs** for errors.

## Why a VM (not LXC)

HAOS is an appliance OS with its own supervisor that manages Docker containers internally. It expects:

- Direct kernel control (for USB/Bluetooth/Zigbee)
- Its own systemd, journald, etc.
- Read-only root filesystem with overlay
- Atomic OS upgrades via supervisor

LXC containers share the host kernel, which conflicts with HAOS’s design. The “Home Assistant Container” Docker image exists for advanced users running on a generic Linux host, but you lose the supervisor and add-on store. Not worth it for homelab use.

VM gives you the full HA experience including one-click add-on installs.

## Why these specs

- **2 cores, 2GB RAM** — fine for typical home setups (50–200 devices). Bump to 4 cores/4GB if running heavy add-ons (Frigate, Plex, etc.).
- **q35 + UEFI** — required for HAOS’s bootloader
- **VirtIO network** — paravirtualized NIC, much faster than emulated e1000
- **SATA disk** — HAOS expects this in its bootloader. VirtIO Block doesn’t work.

## Key gotchas

- HAOS is a VM, not an LXC — can’t be installed any other way on Proxmox
- Must be UEFI (OVMF) with q35 machine type — SeaBIOS won’t boot HAOS
- Disk must be SATA — VirtIO Block fails
- USB passthrough should be by Vendor/Device ID, not port — survives reboots
- VM display name (Proxmox) is separate from HAOS hostname (which is locked to `homeassistant`)
- First boot takes 5–10 minutes — don’t panic if the web UI isn’t ready immediately
- Use both HAOS snapshots AND Proxmox VZDump backups — they cover different failure modes
