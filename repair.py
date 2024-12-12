import os
import sys
from pathlib import Path

# Print initial state
print("Current directory:", os.getcwd())
print("Python path:", sys.path)
print("\nInitial directory structure:")
os.system('ls -R')

# Move all files up one level if we're in a nested structure
current_dir = Path(os.getcwd())
subdir = current_dir / 'event_management_app_python3'
if subdir.exists() and subdir.is_dir():
    print("\nFound nested directory, fixing structure...")
    for item in subdir.iterdir():
        if item.name not in os.listdir(current_dir):
            os.system(f'mv {str(item)} .')
    os.system('rmdir event_management_app_python3')

# Create necessary directories
os.makedirs('app/static/uploads', exist_ok=True)
os.makedirs('cert', exist_ok=True)

# Set correct permissions
os.system('chmod 755 app/static/uploads')

# Initialize python package
if not (Path('app') / '__init__.py').exists():
    print("\nCreating __init__.py...")
    (Path('app') / '__init__.py').touch()

print("\nFinal directory structure:")
os.system('ls -R')

print("\nNow try running:")
print("python3 -c \"from app import app, db; \"\"\" ")
print("with app.app_context():\n    db.create_all()\n    \"\"\"")
