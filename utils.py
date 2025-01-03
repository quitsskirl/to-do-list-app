from datetime import datetime, timedelta
import csv
import json

# ANSI color codes
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
RESET = "\033[0m"

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"{RED}Invalid date format. Please use YYYY-MM-DD{RESET}")
        return None

def validate_due_date(date_str):
    try:
        due_date = datetime.strptime(date_str, '%Y-%m-%d')
        min_date = datetime.strptime('2025-01-01', '%Y-%m-%d')
        
        if due_date < min_date:
            raise ValueError("Due date must be January 1st, 2025 or later")
            
        return date_str
    except ValueError as e:
        if "must be January 1st, 2025 or later" in str(e):
            raise
        raise ValueError("Invalid date format. Please use YYYY-MM-DD format")

def is_overdue(task):
    due_date_str = task.get("due_date")
    if due_date_str:
        due = parse_date(due_date_str)
        return datetime.date.today() > due
    return False

def is_due_soon(task, days_ahead):
    due_date_str = task.get("due_date")
    if due_date_str:
        due = parse_date(due_date_str)
        return 0 <= (due - datetime.date.today()).days <= days_ahead
    return False

def color_for_task(task):
    if task["completed"]:
        return GREEN
    if is_overdue(task):
        return RED
    if task.get("priority", "Medium") == "High":
        return YELLOW
    return RESET

def export_tasks_to_csv(tasks, filename="tasks_export.csv"):
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ["title", "completed", "due_date", "priority", "recurring", "categories", "completion_timestamp"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for t in tasks:
                writer.writerow(t)
        print(f"{GREEN}Tasks exported to {filename}{RESET}")
    except IOError as e:
        print(f"{RED}Error exporting to CSV: {e}{RESET}")

def export_tasks_to_json(tasks, filename="tasks_export.json"):
    try:
        with open(filename, 'w') as f:
            json.dump(tasks, f, indent=2)
        print(f"{GREEN}Tasks exported to {filename}{RESET}")
    except IOError as e:
        print(f"{RED}Error exporting to JSON: {e}{RESET}") 