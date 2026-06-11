# Offensive Security Intro

## Summary
Intro room. Used Gobuster to brute-force a fake bank website and find a hidden /bank-transfer page.

## Commands
gobuster -u http://fakebank.thm -w wordlist.txt dir
# -u = target URL
# -w = wordlist to use
# dir = directory brute-force mode

## Notes
- Offensive security = simulating hacker actions to find vulnerabilities before real attackers do
- Gobuster finds hidden pages by trying every word in a wordlist against the target URL
- Status 200 = page exists, Status 301 = redirect
