import sys
import argparse
from datetime import datetime
from models import (
    load_config, load_tasks, save_tasks, load_archive, 
    save_archive
)
from utils import (
    RED, GREEN, YELLOW, BLUE, RESET,
    parse_date, validate_due_date, is_overdue, is_due_soon,
    color_for_task, export_tasks_to_csv, export_tasks_to_json
)

config = load_config()

def display_tasks(tasks, show_all=True, sort_by=None, filter_category=None, search_query=None):
    # [Keep the existing display_tasks function]
    pass

def add_task(tasks, title=None, due_date=None, priority=None, recurring=None, categories=None):
    # [Keep the existing add_task function]
    pass

# [Keep all other task manipulation functions]

def print_help():
    # [Keep the existing print_help function]
    pass

def parse_args(tasks):
    parser = argparse.ArgumentParser(description='To-Do List Application')
    parser.add_argument('-a', '--add', help='Add a new task')
    parser.add_argument('-d', '--due', help='Set due date (YYYY-MM-DD)')
    parser.add_argument('-p', '--priority', choices=['Low', 'Medium', 'High'], help='Set priority')
    parser.add_argument('-l', '--list', action='store_true', help='List all tasks')
    parser.add_argument('-c', '--complete', type=int, help='Complete a task by ID')
    
    args = parser.parse_args()
    
    if args.add:
        add_task(tasks, title=args.add, due_date=args.due, priority=args.priority)
    elif args.list:
        display_tasks(tasks)
    elif args.complete is not None:
        complete_task(tasks, args.complete)
        
    save_tasks(tasks)
    return tasks

def archive_completed_tasks(tasks):
    """Move completed tasks to archive"""
    archive = load_archive()
    current_tasks = []
    
    for task in tasks:
        if task.get("completed"):
            task["completion_timestamp"] = datetime.now().isoformat()
            archive.append(task)
        else:
            current_tasks.append(task)
    
    if len(tasks) != len(current_tasks):
        save_archive(archive)
        print(f"{BLUE}Archived {len(tasks) - len(current_tasks)} completed tasks{RESET}")
    
    return current_tasks

def show_overdue_alerts(tasks):
    """Show alerts for overdue tasks"""
    overdue = [task for task in tasks if not task["completed"] and is_overdue(task)]
    if overdue:
        print(f"\n{RED}Overdue tasks:{RESET}")
        for task in overdue:
            print(f"- {task['title']} (Due: {task['due_date']})")

def complete_task(tasks, task_id):
    """Mark a task as completed by its ID"""
    if 0 <= task_id < len(tasks):
        tasks[task_id]["completed"] = True
        print(f"{GREEN}Marked task '{tasks[task_id]['title']}' as completed{RESET}")
        save_tasks(tasks)
    else:
        print(f"{RED}Invalid task ID{RESET}")

def main():
    try:
        tasks = load_tasks()
        show_overdue_alerts(tasks)
        remind_tasks(tasks)
        tasks = archive_completed_tasks(tasks)

        if len(sys.argv) > 1:
            tasks = parse_args(tasks)
            return

        # [Keep the existing main menu loop]

    except KeyboardInterrupt:
        print("\nExiting To-Do List application. Goodbye!")
    except Exception as e:
        print(f"{RED}A critical error occurred: {e}{RESET}")
        sys.exit(1)

def remind_tasks(tasks):
    """Remind about tasks due within the next few days"""
    days_ahead = config.get('reminder_days', 3)  # Default to 3 days
    due_soon = [task for task in tasks if is_due_soon(task, days_ahead)]
    
    if due_soon:
        print(f"\n{YELLOW}Upcoming tasks in the next {days_ahead} days:{RESET}")
        for task in due_soon:
            print(f"- {task['title']} (Due: {task['due_date']})")

if __name__ == "__main__":
    main()
