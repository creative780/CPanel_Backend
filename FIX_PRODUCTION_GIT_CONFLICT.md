# Fix Production Git Conflict

## Problem
Production has local changes to migration files that conflict with the updated files in git.

## Solution: Stash Local Changes and Pull

On **production server**, run these commands:

### Option 1: Stash and Pull (Recommended)

```bash
# Stash local changes (saves them temporarily)
git stash

# Pull the latest changes from git
git pull origin main

# If you need the stashed changes back (usually you don't):
# git stash pop
```

### Option 2: Remove Local Changes and Pull

```bash
# Remove the conflicting files (they'll be replaced by git)
rm monitoring/migrations/0009_add_token_field.py
rm monitoring/migrations/0013_alter_device_options_alter_deviceuserbind_options_and_more.py
rm monitoring/migrations/0019_merge_0007_0018.py

# Pull the latest changes
git pull origin main
```

### Option 3: Force Overwrite with Git Version

```bash
# Discard local changes and use git version
git checkout -- monitoring/migrations/0009_add_token_field.py
git checkout -- monitoring/migrations/0013_alter_device_options_alter_deviceuserbind_options_and_more.py

# Remove untracked file
rm monitoring/migrations/0019_merge_0007_0018.py

# Pull the latest changes
git pull origin main
```

## After Pulling

Verify the files are correct:

```bash
# Check migration graph
python manage.py migrate --check

# If check passes, apply migrations
python manage.py migrate
```

## Recommended: Use Option 1 (Stash)

This is the safest method - it saves your local changes in case you need them later.


