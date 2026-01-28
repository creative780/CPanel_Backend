"""
Script to fake all migrations that are trying to create tables that already exist.
This fixes the migration state when tables exist but migrations haven't been recorded.
"""
import subprocess
import sys
import re

def run_command(cmd):
    """Run a command and return output - SECURE VERSION"""
    try:
        # Convert to list if string, validate
        if isinstance(cmd, str):
            import shlex
            cmd_list = shlex.split(cmd)
        else:
            cmd_list = cmd
        
        result = subprocess.run(
            cmd_list,  # List, not string
            # shell=True  # REMOVED - security risk
            capture_output=True,
            text=True,
            cwd="D:\\Abdullah\\CRM Backup\\12\\CRM_BACKEND"
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def get_unapplied_migrations():
    """Get list of unapplied migrations"""
    stdout, stderr, code = run_command("python manage.py showmigrations")
    if code != 0:
        print(f"Error getting migrations: {stderr}")
        return []
    
    unapplied = []
    current_app = None
    for line in stdout.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Check if it's an app name (no brackets)
        if not line.startswith('['):
            current_app = line
        # Check if it's an unapplied migration [ ]
        elif line.startswith('[ ]'):
            migration_name = line.replace('[ ]', '').strip()
            if current_app and migration_name:
                unapplied.append((current_app, migration_name))
    
    return unapplied

def fake_migration(app, migration):
    """Fake a specific migration"""
    print(f"Faking {app}.{migration}...")
    stdout, stderr, code = run_command(f"python manage.py migrate {app} {migration} --fake")
    if code == 0:
        print(f"✓ Successfully faked {app}.{migration}")
        return True
    else:
        # Check if it's a table already exists error
        if "already exists" in stderr or "already exists" in stdout:
            print(f"⚠ Table already exists for {app}.{migration}, trying to fake...")
            # Try to fake it anyway
            stdout2, stderr2, code2 = run_command(f"python manage.py migrate {app} {migration} --fake")
            if code2 == 0:
                print(f"✓ Successfully faked {app}.{migration}")
                return True
            else:
                print(f"✗ Failed to fake {app}.{migration}: {stderr2}")
                return False
        else:
            print(f"✗ Error faking {app}.{migration}: {stderr}")
            return False

def main():
    print("=" * 60)
    print("Migration Fix Script")
    print("=" * 60)
    print("\nThis script will attempt to fake migrations for tables that already exist.")
    print("It will run migrations normally, and if it encounters 'table already exists'")
    print("errors, it will fake those specific migrations.\n")
    
    # Try to run migrations normally first
    print("Step 1: Attempting normal migration...")
    stdout, stderr, code = run_command("python manage.py migrate")
    
    if code == 0:
        print("✓ All migrations applied successfully!")
        return 0
    
    # If we get table already exists errors, fake those migrations
    if "already exists" in stderr or "already exists" in stdout:
        print("\nStep 2: Found 'table already exists' errors. Attempting to fix...\n")
        
        # Extract app and migration from error
        # Pattern: table "app_model" already exists
        table_pattern = r'table "(\w+)_(\w+)" already exists'
        matches = re.findall(table_pattern, stderr + stdout)
        
        if matches:
            for app_name, model_name in matches:
                # Find the migration that creates this table
                # Usually it's the initial migration for the app
                print(f"Found existing table: {app_name}_{model_name}")
                # Try to fake the initial migration for this app
                fake_migration(app_name, "0001_initial")
        
        # Now try migrating again
        print("\nStep 3: Retrying migration...")
        stdout2, stderr2, code2 = run_command("python manage.py migrate")
        
        if code2 == 0:
            print("\n✓ All migrations applied successfully!")
            return 0
        else:
            print(f"\n⚠ Some migrations may still need attention:")
            print(stderr2)
            return 1
    else:
        print(f"\n✗ Migration failed with unexpected error:")
        print(stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())




