# 🖥️ Windows 11 VM on Proxmox — Setup Guide

## Overview
This guide walks through creating and configuring a **Windows 11** virtual machine on **Proxmox**, including virtIO driver setup and performance tuning.

---

## 🧰 Requirements
- Windows 11 ISO  
- VirtIO drivers ISO (from [Fedora’s virtio-win project](https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/latest-virtio/))  
- Proxmox VE (latest version)  
- Optional: `qemu-agent` package for better integration  

---

## 🧾 Step 1: Create the VM
1. **Download the Windows 11 ISO** and **VirtIO ISO**.  
2. In Proxmox, create a new VM:  
   - Choose **Windows 11** as the Guest OS.  
   - And add additonal drive for VirtIO driver and attach the VirtoIO driver. 
   - Use **virtIO SCSI** as the disk bus.  
   - Add **QEMU Guest Agent** support.  
   - Assign **8 GB RAM** (or more if available).  
3. Make sure the storage location points to where your other VMs are stored.
<img width="573" height="283" alt="image" src="https://github.com/user-attachments/assets/cf41aab5-5bd6-4d5f-98f1-e5767b748f1f" />

---

## ⚙️ Step 2: Configure VM Settings
1. **Choose “Host” CPU type** for best performance.  
   - If migrating between Proxmox nodes with different CPUs, use a compatible type (e.g. `x86-64-v2`).  
2. **Enable VirtIO network and storage drivers**:
   - Add VirtIO device for disk and network.  
   - Under “Options”, ensure the boot order lists your Windows ISO **first**.

![Proxmox VM Configuration](./A89B1511-B90B-4377-9045-A18C8CDD80E8.png)

---

## 💾 Step 3: Boot the Installer
1. Start the VM — if you see  
   > “No bootable disk found”  
   open the **Boot Order** settings and move the Windows ISO to the top.  
2. Proceed with the installer.  
3. When you reach the **“No drives found”** screen:  
   - Click **Load Driver**.  
   - Browse to the **VirtIO ISO** → `viostor\w11\amd64`.  
   - Load the driver, and your disk should now appear.  
4. Continue installation normally.

![VirtIO Load Driver](./6454CA45-FA59-4052-AE8A-F6B56728461E.png)

---

## 🧩 Step 4: Post-Install Drivers
Once Windows boots:
1. Mount the **VirtIO ISO** again (if unmounted).  
2. In **File Explorer**, open the mounted drive and:
   - Install **netKVM** driver → `NetKVM\w11\amd64`.  
   - Install **Balloon**, **QEMU guest agent**, and any other missing drivers.  
3. Optionally, install Windows updates and enable RDP or Spice tools.

![VirtIO Drivers Install](./D6B6A593-E6A1-4DE8-80ED-E922223993CE.png)

---

## 🧠 Notes
- Always use VirtIO for both disk and network for best performance.  
- Avoid IDE or SATA virtual disks; VirtIO gives near-native speed.  
- If using TPM + Secure Boot, enable them before first boot.  
- Back up your VM config (`qm config <vmid> > win11.conf`) once working.

---

## ✅ Summary
| Component | Setting | Notes |
|------------|----------|-------|
| OS | Windows 11 | ISO from Microsoft |
| Storage | VirtIO SCSI | High performance |
| Network | VirtIO | Requires drivers |
| RAM | 8 GB (min) | Adjust as needed |
| Drivers | virtio-win ISO | Must load during setup |
