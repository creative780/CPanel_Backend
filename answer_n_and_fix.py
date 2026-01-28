#!/usr/bin/env python
import subprocess
import sys
import os
import shlex

def run_django_command_with_input(command, input_text="N\n"):
    """Run a Django command with automatic input - SECURE VERSION"""
    try:
        # Split command safely - don't use shell=True
        cmd_list = shlex.split(command)
        
        # Validate command starts with expected programs
        allowed_commands = ['python', 'manage.py']
        if cmd_list and not any(cmd_list[0].endswith(cmd) for cmd in allowed_commands):
            raise ValueError(f"Command not allowed: {cmd_list[0]}")
        
        process = subprocess.Popen(
            cmd_list,  # List, not string
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            # shell=True  # REMOVED - security risk
        )
        
        stdout, stderr = process.communicate(input=input_text)
        
        print("STDOUT:", stdout)
        if stderr:
            print("STDERR:", stderr)
            
        return process.returncode
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    # First try to run showmigrations to see the current state
    print("Checking migration status...")
    run_django_command_with_input("python manage.py showmigrations")
    
    # Then try to run the column fix
    print("\nFixing column name...")
    run_django_command_with_input("python manage.py shell -c \"from django.db import connection; cursor = connection.cursor(); cursor.execute('ALTER TABLE orders_designapproval CHANGE COLUMN responded_at reviewed_at DATETIME(6) NULL'); print('Column renamed successfully')\"")
