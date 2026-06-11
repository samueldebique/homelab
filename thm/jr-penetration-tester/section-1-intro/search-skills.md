# Search Skills

## Summary
Overview of key resources used in cyber security research and reconnaissance. Covers Shodan, VirusTotal, CVE/ExploitDB, Linux man pages, and GitHub as research tools.

## Key tools

**Shodan**
Search engine for internet-connected devices — servers, cameras, industrial control systems, anything with a public network connection. Useful during recon and vulnerability assessments to find exposed services.

Useful filters:
- `country:GB` — restrict to a country
- `port:22` — filter by port
- `hostname:target.com` — match a domain
- `org:AS7224` — scope to an organisation or ASN

Example: searching `apache 2.4.1` returns all servers advertising that version, which you can cross-reference against known CVEs.

**VirusTotal**
Submits files, URLs, domains, or file hashes to 70+ antivirus engines in one place. Returns a consensus on whether something is malicious. Not foolproof but a quick first check on suspicious files or links. Commonly used in blue team workflows.

**CVE / ExploitDB**
CVE (Common Vulnerabilities and Exposures) is the universal dictionary of known vulnerabilities. Each gets a unique ID in the format `CVE-YEAR-NUMBER`. High-impact ones sometimes get names (Heartbleed, Log4Shell).

CVSS score measures severity based on:
- Impact — what damage can it cause
- Complexity — how hard is it to exploit
- Availability — how likely is exploitation

ExploitDB hosts PoC (Proof of Concept) code alongside CVE entries — scripts that demonstrate the vulnerability in practice. Organisations use CVSS scores to prioritise patching.

**Linux man pages**
Built-in documentation for any command on Linux. Always check here first when you don't know what a flag does.

`man <command>` — e.g. `man nc` pulls up the full netcat manual including example commands.

**GitHub**
Researchers publish PoC code, exploitation tools, and vulnerability analyses here — often faster than official channels. Search a CVE ID directly to find repos with scanners, exploits, or writeups.

Caution: not all PoCs are reliable. Some are incomplete, some intentionally broken, and occasionally a PoC repo is itself malicious. Always read the code before running anything.

## Notes
- Knowing where to search is as important as knowing what to search for
- Official tool documentation is always the first stop when troubleshooting
- VirusTotal consensus is useful but not definitive — some engines have false positives
- GitHub PoCs move faster than official advisories but carry more risk
