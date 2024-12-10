import os
import json
import sys
import datetime
import shutil
import argparse
import csv

TODO_FILE = "todo_list.json"
ARCHIVE_FILE = "archive_list.json"
CONFIG_FILE = "config.json"
BACKUP_FILE = "todo_list_backup.json"

RED ="\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:

         return {
            "default_recurring": None,
            "reminder_days_ahead": 1,
            "default_priority": "Medium"
        }
    
    config = load_config() 
def load_tasks():         
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as f:
            return json.load(f)
    else:
        return[]
    
    def save_tasks(tasks):
        if os.path.exists(TODO_FILE):
            shutil.copyfile(TODO_FILE,BACKUP_FILE)
            with open(TODO_FILE, 'W') as f:
                json.dump(tasks,f,indent=2)

    def load_archive():
        if os.path.exists(ARCHIVE_FILE):
            with open(ARCHIVE_FILE, 'r') as f:
                return json.load(f)
        else:
            return[]

    def save_archive(archived):
        with open(ARCHIVE_FILE, 'w') as f:
            json.dump(archived, f, indent=2)