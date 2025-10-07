import subprocess
import re
import requests
import time
from datetime import datetime

#Discord webhook URL
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/XXXXX"

#Web log file path
WEB_LOG_FILE = "/var/log/pveproxy/access.log"


#Send Discord message
def send_discord(msg):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg})
    except Exception as e:
        print(f"Error sending to Discord: {e}")


#Monitor SSH logins in real time
def monitor_ssh():
    cmd = ["journalctl", "-f", "-u", "ssh.service", "--no-pager"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in process.stdout:
        if "Failed password" in line or "Accepted password" in line:
            status = "FAILED" if "Failed password" in line else "SUCCESSFUL"
            ip_match = re.search(r'from ([\d\.]+)', line)
            ip = ip_match.group(1) if ip_match else "Unknown"
            user_match = re.search(r'for (\w+)', line)
            user = user_match.group(1) if user_match else "Unknown"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            msg = (
                f"🔑 **SSH Login {status}**\n"
                f"🕒 Time: `{timestamp}`\n"
                f"👤 User: `{user}`\n"
                f"🌍 IP: `{ip}`"
            )
            send_discord(msg)

#Monitor Proxmox Web logins in real time
def monitor_web():
    cmd = ["tail", "-F", WEB_LOG_FILE]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in process.stdout:
        if "POST /api2/json/access/ticket" in line or "POST /api2/extjs/access/ticket" in line:
            ip_match = re.search(r'::ffff:([\d\.]+)', line)
            ip = ip_match.group(1) if ip_match else "Unknown"
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            msg = (
                f"🌐 **Proxmox Web Login Attempt**\n"
                f"🕒 Time: `{timestamp}`\n"
                f"🌍 IP: `{ip}`"
            )
            send_discord(msg)


#Run both watchers
if __name__ == "__main__":
    import threading
    t1 = threading.Thread(target=monitor_ssh, daemon=True)
    t2 = threading.Thread(target=monitor_web, daemon=True)

    t1.start()
    t2.start()

    # Keep script alive
    while True:
        time.sleep(1)
