# Windows 11 VM on Proxmox — Setup Guide

## Overview
This guide walks through creating and configuring a **Windows 11** virtual machine on **Proxmox**, including virtIO driver setup and performance tuning.


## Step 1: Create the VM
1. **Download the Windows 11 ISO** and **VirtIO ISO**.  
2. In Proxmox, create a new VM:  
- Choose **Windows 11** as the Guest OS.  
- And add additonal drive for VirtIO driver and attach the VirtoIO driver.

     
  <img width="573" height="283" alt="image" src="https://github.com/user-attachments/assets/cf41aab5-5bd6-4d5f-98f1-e5767b748f1f" />

  
3. Add **QEMU Guest Agent** support.


   <img width="578" height="270" alt="image" src="https://github.com/user-attachments/assets/c896649d-0c1b-4875-bac9-ffcef12dece4" />


4. If you are installing this on an SSD enable these settings


<img width="571" height="370" alt="image" src="https://github.com/user-attachments/assets/3a36de0b-8e3c-4f76-8f73-6ec108be3cb1" />


5. **Choose “Host” CPU type** for best performance.  
- If migrating between Proxmox nodes with different CPUs, use a compatible type (e.g. `x86-64-v2`).


  <img width="578" height="135" alt="image" src="https://github.com/user-attachments/assets/bcabe349-f472-4157-987d-d4a028eec974" />


6. **Enable VirtIO network and storage drivers**:
- Add VirtIO device for disk and network.  
- Under “Options”, ensure the boot order lists your Windows ISO **first**.
     
<img width="579" height="181" alt="image" src="https://github.com/user-attachments/assets/20ecedfb-0c6c-4d5e-9cc4-a70d922954be" />


## Step 2: Boot the Installer
1. Start the VM — if you see  
   > “No bootable disk found”  
   open the **Boot Order** settings and move the Windows ISO to the top.
   
   <img width="509" height="158" alt="image" src="https://github.com/user-attachments/assets/ed6efaab-9f8f-447b-ac54-75f2d573c8ea" />

2. Proceed with the installer.  
3. When you reach the **“No drives found”** screen:  
- Click **Load Driver**.  
- Browse to the **VirtIO ISO** → `viostor\w11\amd64`.  
- Load the driver, and your disk should now appear.  
4. Continue installation normally.


## Step 3: Post-Install Drivers
Once Windows boots:
In **File Explorer**, open the mounted drive and:
- Install **netKVM** driver → `NetKVM\w11\amd64`.  
- Install **Balloon**, **QEMU guest agent**, and any other missing drivers.  

