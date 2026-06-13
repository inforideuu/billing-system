import shutil
import os

hba_path = r"C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
backup_path = hba_path + ".bak"

try:
    # 1. Backup file
    if not os.path.exists(backup_path):
        shutil.copy2(hba_path, backup_path)
        print(f"Backup created at: {backup_path}")
    else:
        print("Backup already exists.")
        
    # 2. Read contents
    with open(hba_path, 'r') as f:
        lines = f.readlines()
        
    modified = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        # Look for the local IPv4 and IPv6 lines
        if not stripped.startswith('#') and 'scram-sha-256' in line:
            if '127.0.0.1/32' in line or '::1/128' in line:
                old_line = line
                line = line.replace('scram-sha-256', 'trust')
                print(f"Modifying line:\n  OLD: {old_line.strip()}\n  NEW: {line.strip()}")
                modified = True
        new_lines.append(line)
        
    if modified:
        with open(hba_path, 'w') as f:
            f.writelines(new_lines)
        print("Successfully updated pg_hba.conf to 'trust' mode for local connections!")
    else:
        print("No lines modified - could they already be set to trust, or not found?")
        
except Exception as e:
    print(f"Failed to modify pg_hba.conf: {e}")
