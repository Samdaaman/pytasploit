# Requirements
## Overall Goals
- Easy to add commands / processes / modules
- Minimal filesystem presence
- Extendable to multiple communication protocols (ie TCP/IP, HTTP, DNS exfiltration)
   - Ideally this includes the staged deployment mechanism (could use pastebin idea)
- Support for old python3 versions (3.5 ideally)
- Modules loadable at runtime and reloadable

## Features
- Background forking process (doesn't block caller)
- Keepalive measures (ie Pacemaker)
- Encrypted communication
- Allow spawning from SSH directly (ie if valid SSH keys are found)
- Running enumeration scripts and saving results
- Uploading/downloading files
- Enumerating/browsing remote database
- Known password bruteforce of existing users

## Commands
- Ping/pong
- Open shell
- Self destruct
- TODO Run enum script
- TODO Custom enum script / modules
  - Enum files  
  - Enum services / open ports and compare
  - Enum users
  - Enum/share databases
  - Load SSH keys and save to pytasploit
- TODO Download file
- TODO Upload file
- TODO Do stealth
