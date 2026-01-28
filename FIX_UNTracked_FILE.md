# Fix Untracked File Conflict

## Problem
Git is blocking the pull because an untracked file `monitoring/migrations/0019_merge_0007_0018.py` would be overwritten.

## Solution: Remove the File and Pull

On **production server**, run:

```bash
# Remove the untracked file
rm monitoring/migrations/0019_merge_0007_0018.py

# Pull the latest changes
git pull origin main

# Test migrations
python manage.py migrate --check
python manage.py migrate
```

The file will be replaced by the correct version from git.


