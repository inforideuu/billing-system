import os

hba_path = r"C:\Program Files\PostgreSQL\16\data\pg_hba.conf"

try:
    if os.path.exists(hba_path):
        with open(hba_path, 'r') as f:
            content = f.read()
        print(f"SUCCESS: Read {len(content)} bytes from pg_hba.conf.")
    else:
        print("pg_hba.conf path does not exist.")
except Exception as e:
    print(f"Failed to read pg_hba.conf: {e}")
