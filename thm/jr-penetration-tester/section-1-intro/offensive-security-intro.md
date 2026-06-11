# Offensive Security Intro

## Summary
Introductory room covering what offensive security is and how ethical hackers operate. Used Gobuster (a directory brute-forcing tool) to find a hidden page on a simulated bank website called FakeBank, then accessed the hidden admin transfer page to demonstrate how an attacker could exploit it.

## Key tools

**Gobuster**
A command-line tool used to brute-force directories and pages on a web server. It takes a wordlist and tries each entry against the target URL, reporting back any pages that exist. Pre-installed on Kali Linux — on standard Debian/Ubuntu install with `apt install gobuster`.

## Commands
`gobuster -u http://fakebank.thm -w wordlist.txt dir`

- `-u` = target URL
- `-w` = wordlist to use
- `dir` = directory brute-force mode

## Notes
- Offensive security = simulating hacker actions to find vulnerabilities before real attackers do
- Gobuster finds hidden pages by trying every word in a wordlist against the target URL
- Status 200 = page exists, Status 301 = redirect
- Hidden admin pages are a common real-world vulnerability — not making them private is a configuration mistake
