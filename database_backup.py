import os
import datetime
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def run_backup():
    # Database configuration from .env
    db_name = os.getenv('DB_NAME', 'chit_fund_db')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', '127.0.0.1')
    
    # Create backups directory if it doesn't exist
    backup_dir = os.path.join(os.getcwd(), 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created directory: {backup_dir}")

    # Generate filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file = os.path.join(backup_dir, f"backup_{db_name}_{timestamp}.sql")

    # Common paths for mysqldump on Windows/XAMPP
    possible_mysqldump_paths = [
        "mysqldump", # If in PATH
        r"C:\xampp\mysql\bin\mysqldump.exe",
        r"C:\xampp3.0\mysql\bin\mysqldump.exe", # Based on your current directory structure
        r"D:\xampp\mysql\bin\mysqldump.exe",
    ]
    
    dump_exe = "mysqldump"
    for path in possible_mysqldump_paths:
        # Check if the path is an absolute path and exists
        if os.path.isabs(path) and os.path.exists(path):
            dump_exe = f"\"{path}\""
            break

    # Construct mysqldump command
    if db_password:
        command = f"{dump_exe} -h {db_host} -u {db_user} -p{db_password} {db_name} > \"{backup_file}\""
    else:
        command = f"{dump_exe} -h {db_host} -u {db_user} {db_name} > \"{backup_file}\""

    try:
        print(f"Starting backup for {db_name}...")
        # Use shell=True for redirection to work on Windows
        subprocess.run(command, shell=True, check=True)
        print(f"SUCCESS: Backup saved to {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Backup failed. Make sure 'mysqldump' is installed and accessible.")
        print(f"Details: {e}")

if __name__ == "__main__":
    run_backup()
