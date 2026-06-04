# Windows 11

Windows 11 running as a VM on Proxmox with VirtIO drivers for performance.

You'll need both the Windows 11 ISO and the VirtIO drivers ISO uploaded to Proxmox storage before starting. VirtIO ISO: `https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso`

## Setup

### 1. Create the VM

- **OS:** Select Windows 11 ISO, Guest OS = Microsoft Windows 11
- **System:** Machine `q35`, BIOS `OVMF (UEFI)`, tick **Add TPM**, add EFI disk
- **Disk:** VirtIO Block. If on SSD, enable **SSD emulation** and **Discard**
- **CPU:** Type `host`, 2+ cores
- **Memory:** 4096 MiB minimum
- **Network:** VirtIO

Add a second CD/DVD drive and attach the VirtIO ISO.

### 2. Boot the installer

Start the VM. If you see "No bootable disk found", go to **Options → Boot Order** and move the Windows ISO to the top.

### 3. Load the VirtIO storage driver

When the installer shows "No drives found":

1. Click **Load Driver**
2. Browse to the VirtIO ISO → `viostor\w11\amd64`
3. Load the driver — the disk will appear
4. Continue installation normally

### 4. Post-install drivers

Once Windows boots, open File Explorer and browse to the VirtIO ISO. Install:

- **NetKVM** (`NetKVM\w11\amd64`) — network
- **Balloon** — memory ballooning
- **QEMU Guest Agent** (`guest-agent\qemu-ga-x86_64.msi`)

## Verify

The VM should show a valid IP under **Summary** in Proxmox once the guest agent is running.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No bootable disk found" | Fix boot order — Windows ISO must be first |
| "No drives found" in installer | Load VirtIO storage driver from `viostor\w11\amd64` |
| No network after install | Install NetKVM driver from VirtIO ISO |
| No IP shown in Proxmox | Install QEMU Guest Agent |
