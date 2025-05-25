import os
import shutil
from datetime import datetime
import sqlite3
import subprocess

def backup_database(db_path, backup_dir):
    """Create a backup of the database"""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'contacts_{timestamp}.db')
    shutil.copy2(db_path, backup_path)
    print(f"Database backed up to {backup_path}")

def sync_to_server():
    """Sync local database to server"""
    local_db = 'instance/contacts.db'
    remote_user = 'ddiemeo9zafc'
    remote_host = 'contactbook.oerna.de'
    remote_dir = '~/mapcontacts/instance'
    
    # Backup local database
    backup_database(local_db, 'backups')
    
    # Sync to server
    cmd = f'scp {local_db} {remote_user}@{remote_host}:{remote_dir}/contacts.db'
    subprocess.run(cmd, shell=True)
    print("Database synced to server")

def sync_from_server():
    """Sync server database to local"""
    local_db = 'instance/contacts.db'
    remote_user = 'ddiemeo9zafc'
    remote_host = 'contactbook.oerna.de'
    remote_dir = '~/mapcontacts/instance'
    
    # Backup local database
    backup_database(local_db, 'backups')
    
    # Sync from server
    cmd = f'scp {remote_user}@{remote_host}:{remote_dir}/contacts.db {local_db}'
    subprocess.run(cmd, shell=True)
    print("Database synced from server")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2 or sys.argv[1] not in ['to', 'from']:
        print("Usage: python sync_db.py [to|from]")
        sys.exit(1)
    
    if sys.argv[1] == 'to':
        sync_to_server()
    else:
        sync_from_server() 