import json
import os
import shutil
from datetime import datetime

# Files
TODO_FILE = "todo_list.json"
ARCHIVE_FILE = "archive_list.json"
CONFIG_FILE = "config.json"
BACKUP_FILE = "todo_list_backup.json"

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading config: {e}")
        return {
            "default_recurring": None,
            "reminder_days_ahead": 1,
            "default_priority": "Medium"
        }
    return {
        "default_recurring": None,
        "reminder_days_ahead": 1,
        "default_priority": "Medium"
    }

def load_tasks():
    try:
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading tasks: {e}")
        return []
    return []

def save_tasks(tasks):
    try:
        if os.path.exists(TODO_FILE):
            shutil.copyfile(TODO_FILE, BACKUP_FILE)
        with open(TODO_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
    except IOError as e:
        print(f"Error saving tasks: {e}")

def load_archive():
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, 'r') as f:
            return json.load(f)
    return []

def save_archive(archived):
    with open(ARCHIVE_FILE, 'w') as f:
        json.dump(archived, f, indent=2) 