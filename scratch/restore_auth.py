import shutil
import os

hba_path = r"C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
backup_path = hba_path + ".bak"

try:
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, hba_path)
        print("SUCCESS: Restored pg_hba.conf from backup.")
    else:
        print("Backup file not found.")
except Exception as e:
    print(f"Failed to restore backup: {e}")
