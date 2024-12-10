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

            def parse_date(date_str):
                return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            def is_overdue(task):
                due_date_str = task.get("due_date")
                if due_date_str:
                    due = parse_date(due_date_str)
                    return datetime.date.today() > due
                return False
            
            def is_due_soon(task, days_ahead):
                due_date_str=task.get("due_date")
                if due_date_str:
                    due= parse_date(due_date_str)
                    return 0<=(due-datetime.date.today()).days<= days_ahead
                return False
            
            def color_for_task(task):
                if task["completed"]:
                    return GREEN
                if is_overdue(task):
                    return RED
                if task.get("priority", "MEDIUM") == "high":
                    return YELLOW
                return RESET
            
            def display_tasks(tasks, show_all=True, sort_by=None, filter_category=None, search_query=None):
                filtered = tasks
                if not show_all:
                    filtered = [t for t in filtered if not t["completed"]]
                if filter_category:
                    filtered = [t for t in filtered if filter_category in t.get("categories", [])]
                if search_query:
                    filtered = [t for t in filtered if search_query.lower() in t["title"].lower()]
                if sort_by == "due_date":
                   filtered.sort(key=lambda t: t.get("due_date") or "9999-12-31")
                elif sort_by == "priority":
                   prio_order = {"High": 1, "Medium": 2, "Low": 3}
                   filtered.sort(key=lambda t: prio_order.get(t.get("priority", "Medium"), 2))
                elif sort_by == "category":
                   filtered.sort(key=lambda t: (t.get("categories") or ["zzzz"]))
                   