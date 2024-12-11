from logging import config
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
       
       if not filtered:
           print("no tasks found.")
       else:
           print("\nTo-Do List:")
           for i, task in enumerate(filtered,1):
               c=color_for_task(task)
               status="[Done]"if task["completed"]else"[]"
               due_str= f"(Due:{task['due_date']})"if task.get("due_date") else""
               cat_str=f"(Categories:{','.join(task.get('categories',[]))})"if task.get('categories')else""
               prio_str=f"(Priority:{task.get('priority','Medium')})"
               recur_str=f"(Recurring:{task.get('recurring')})"if task.get('recurring')else""
               title=task["title"]
               print(f"{c}{i}.{status}{title}{due_str}{prio_str}{cat_str}{recur_str}{RESET}")

def add_task(tasks, title=None, due_date=None, priority=None, recurring=None, categories=None):
    if not title:
        title= input("enter a new task: ").strip()
    if not title:
         print("task cannot be empty.")
         return tasks
    if due_date is None:
         due_date= input("enter due date (YYYY/MM/DD) or leave blank: ").strip()
    if not due_date:
        due_date=None
    if priority is None:
         priority = input("Enter priority (High/Medium/Low) or leave blank: ").strip() or config.get("default_priority", "Medium")
    if recurring is None:
        recurring = input("Enter recurring interval (daily/weekly/monthly/yearly) or leave blank for one-time:").strip() or None
    if categories is None:
        cat_input = input("Enter categories (comma separated) or leave blank: ").strip()
        categories = [c.strip() for c in cat_input.split(",") if c.strip()] if cat_input else []

        new_task={
            "title":title,
            "due_date":due_date,
            "priority":priority,
            "recurring":recurring,
            "categories":categories,
            "completion_timestamp":None
        }
        tasks.append(new_task)
        print(f"Task '{title}'added.")
        return tasks
    
    def remove_task(tasks):
        display_tasks(tasks)
        choice = input("\nEnter the task number(s) to remove (e.g'1'or'1,2,3'): ").strip()
        if not choice:
            return tasks
        indices = [int(x)-1 for x in choice.split(",") if x.strip().isdigit()]
        indices = sorted(indices, reverse=True)
        for idx in indices:
            if 0 <= idx < len(tasks):
                removed_task = tasks.pop(idx)
                print(f"Task '{removed_task['title']}' removed.")
            else:
                print(f"Invalid task number:{idx+1}")
                return tasks
    

        

