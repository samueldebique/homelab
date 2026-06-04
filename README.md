# Homelab

Personal homelab running on a Lenovo ThinkCentre M720q with Proxmox VE. This repo documents my infrastructure, self-hosted services, and setup guides.

---

## Hardware

| Component | Details |
|-----------|---------|
| Host | Lenovo ThinkCentre M720q |
| Hypervisor | Proxmox VE |
| Networking | Pi-hole (DNS), WireGuard (VPN), Nginx Proxy Manager (reverse proxy) |

---

## Services

| Service | Description |
|---------|-------------|
| Pi-hole | Network-wide ad blocking and local DNS |
| Vaultwarden | Self-hosted Bitwarden password manager |
| Nginx Proxy Manager | Reverse proxy with SSL for all services |
| WireGuard | VPN for secure remote access |
| Ollama | Local LLM inference |
| Home Assistant | Home automation |
| AdGuard Home | DNS-level filtering (LXC) |

---

## Structure

```
homelab/
├── apps/           # Docker compose files and app configs
├── how-to-guide/   # Step-by-step setup guides for each service
└── scripts/        # Automation and utility scripts
```

---

## Guides

Setup guides live in [`how-to-guide/`](./how-to-guide/) — each service has its own documented walkthrough including install steps, config, and any gotchas.

---

## Scripts

Utility scripts in [`scripts/`](./scripts/) for log analysis, maintenance, and automation.

---

*Documentation is a work in progress and updated as the lab evolves.*
