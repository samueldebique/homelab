# Home Assistant

Home Assistant OS running as a VM on Proxmox. VM rather than LXC because HAOS is a full appliance that manages its own kernel and supervisor.

## Setup

### 1. Download the HAOS image

In the Proxmox shell:

```bash
cd /var/lib/vz/template/iso
wget https://github.com/home-assistant/operating-system/releases/latest/download/haos_ova-latest.qcow2.xz
xz -d haos_ova-latest.qcow2.xz
```

### 2. Create the VM

- **OS:** No media
- **System:** Machine `q35`, BIOS `OVMF (UEFI)`, add EFI disk
- **Disk:** Delete the default disk — you'll import the image instead
- **CPU:** 2 cores, type `host`
- **Memory:** 2048 MiB

### 3. Import the HAOS disk

```bash
qm importdisk <VMID> /var/lib/vz/template/iso/haos_ova-latest.qcow2 local-lvm
```

In the VM's **Hardware** tab, find the unused disk → double-click → set Bus/Device to `SCSI 0` → Add.

### 4. Set boot order

**Options → Boot Order** — enable the SCSI disk and move it to the top.

### 5. Start the VM

```bash
qm start <VMID>
```

Wait ~2 minutes for first boot, then open `http://homeassistant.local:8123` to begin onboarding.

## Verify

```bash
qm status <VMID>
```

Should show `running`. Onboarding screen should be reachable in the browser.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| VM won't boot | Check boot order — SCSI disk must be first |
| Web UI unreachable | Wait 2-3 minutes after first boot |
| No IP assigned | Check VM network is set to VirtIO on vmbr0 |
