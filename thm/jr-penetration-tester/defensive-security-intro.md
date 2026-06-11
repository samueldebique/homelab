# Defensive Security Intro

## Summary
Overview of defensive security and its subfields. Covered the role of a SOC (Security Operations Center), Threat Intelligence, DFIR (Digital Forensics and Incident Response), and Malware Analysis. Simulated a SOC analyst workflow by investigating alerts inside a SIEM (Security Information and Event Management) dashboard and identifying a malicious event.

## Key concepts

**Defensive security** — concerned with two things: preventing intrusions from occurring, and detecting and responding to intrusions when they do occur. Blue teams handle defensive security.

**SOC (Security Operations Center)**
A team of cyber security professionals that monitors a network and its systems for malicious activity. Key areas:
- Vulnerabilities — finding and patching weaknesses before attackers exploit them
- Policy violations — detecting when users break security rules e.g. uploading sensitive data externally
- Unauthorised activity — detecting stolen credentials being used to log in
- Network intrusions — detecting when an attacker gains access via a malicious link or exposed service

**Threat Intelligence**
Collecting and analysing information about actual and potential adversaries. Goal is a threat-informed defence — understanding who might attack you and how, so you can prepare. Data is collected from network logs, public forums, and other sources, then processed and analysed to identify attacker tactics, techniques, and procedures (TTPs).

**DFIR (Digital Forensics and Incident Response)**
- Digital Forensics = analysing evidence of an attack. Covers file systems, system memory, system logs, and network logs
- Incident Response = the process followed when an attack occurs

Four phases of Incident Response:
1. Preparation — having a trained team and preventive measures in place
2. Detection and Analysis — identifying and understanding the incident
3. Containment, Eradication, and Recovery — stopping the spread, removing the threat, restoring systems
4. Post-Incident Activity — writing a report and sharing lessons learned

**Malware Analysis**
- Static analysis = inspecting malicious code without running it. Requires knowledge of assembly language
- Dynamic analysis = running malware in a controlled environment and observing its behaviour

Malware types:
- Virus = attaches to programs, spreads between computers, corrupts or deletes files
- Trojan Horse = disguised as legitimate software, hides malicious functionality
- Ransomware = encrypts user files and demands payment for the decryption key

**SIEM (Security Information and Event Management)**
Aggregates security events and logs from multiple sources into a single dashboard. Generates alerts when suspicious activity is detected. Not all alerts are malicious — analyst judgment is required to triage them.

## Notes
- Blue team = defensive security, Red team = offensive security
- SIEM is a core tool in any SOC environment
- Threat intelligence helps predict attacker behaviour based on known TTPs (Tactics, Techniques, and Procedures)
