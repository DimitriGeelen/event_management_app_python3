import sqlite3
import os
import shutil
from datetime import datetime

def backup_database():
    # Source database path
    src_db = 'app/events.db'
    
    # Create backups directory if it doesn't exist
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'events_backup_{timestamp}.db'
    dst_path = os.path.join(backup_dir, backup_file)
    
    try:
        # Copy the database file
        shutil.copy2(src_db, dst_path)
        print(f'Database backup created successfully: {dst_path}')
        return True
    except Exception as e:
        print(f'Error creating backup: {str(e)}')
        return False

def restore_database(backup_file):
    # Paths
    backup_path = os.path.join('backups', backup_file)
    target_db = 'app/events.db'
    
    try:
        # Copy the backup file to the original location
        shutil.copy2(backup_path, target_db)
        print(f'Database restored successfully from: {backup_file}')
        return True
    except Exception as e:
        print(f'Error restoring backup: {str(e)}')
        return False

def list_backups():
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        print('No backups found')
        return []
    
    backups = [f for f in os.listdir(backup_dir) if f.startswith('events_backup_') and f.endswith('.db')]
    backups.sort(reverse=True)  # Most recent first
    
    if not backups:
        print('No backups found')
    else:
        print('Available backups:')
        for backup in backups:
            size = os.path.getsize(os.path.join(backup_dir, backup)) / 1024  # Size in KB
            timestamp = backup[14:-3]  # Extract timestamp from filename
            print(f'- {backup} ({size:.1f} KB) - Created: {timestamp}')
    
    return backups

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print('Usage:')
        print('  backup: python3 backup_db.py backup')
        print('  list: python3 backup_db.py list')
        print('  restore: python3 backup_db.py restore <backup_file>')
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'backup':
        backup_database()
    elif command == 'list':
        list_backups()
    elif command == 'restore' and len(sys.argv) == 3:
        restore_database(sys.argv[2])
    else:
        print('Invalid command or missing backup file')
