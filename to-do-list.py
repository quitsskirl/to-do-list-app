import os
import json
import sys
import datetime
import shutil
import argparse
import csv
START_DATE = datetime.date(2025, 1, 1)
TODO_FILE = "todo_list.json"
ARCHIVE_FILE = "archive_list.json"
CONFIG_FILE = "config.json"
BACKUP_FILE = "todo_list_backup.json"
RED = "\033[31m"
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
        return []

def save_tasks(tasks):
    # Overwrite single backup file before saving
    if os.path.exists(TODO_FILE):
        shutil.copyfile(TODO_FILE, BACKUP_FILE)

    with open(TODO_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def load_archive():
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, 'r') as f:
            return json.load(f)
    else:
        return []

def save_archive(archived):
    with open(ARCHIVE_FILE, 'w') as f:
        json.dump(archived, f, indent=2)

def parse_date(date_str):
    # Attempt to parse date in YYYY-MM-DD
    # Could be extended if you have different formats
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

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
        print("No tasks found.")
    else:
        print("\nTo-Do List:")
        for i, task in enumerate(filtered, 1):
            c = color_for_task(task)
            status = "[Done]" if task["completed"] else "[ ]"
            due_str = f" (Due: {task['due_date']})" if task.get("due_date") else ""
            cat_str = f" (Categories: {', '.join(task.get('categories', []))})" if task.get('categories') else ""
            prio_str = f" (Priority: {task.get('priority', 'Medium')})"
            recur_str = f" (Recurring: {task.get('recurring')})" if task.get('recurring') else ""
            title = task["title"]
            print(f"{c}{i}. {status} {title}{due_str}{prio_str}{cat_str}{recur_str}{RESET}")

def add_task(tasks, title=None, due_date=None, priority=None, recurring=None, categories=None):
    while True:
        if not title:
            title = input("Enter a new task (max 60 characters): ").strip()

        if len(title) > 60:
            print(RED + "Error: Task description exceeds 60 characters. Please try again." + RESET)
            continue

        if due_date is None:
            due_date = input("Enter due date (YYYY-MM-DD) or leave blank: ").strip()
            if due_date and not is_valid_date(due_date):
                print(RED + "Invalid date. Please enter a valid date in YYYY-MM-DD format." + RESET)
                continue

        if priority is None:
            priority = input("Enter priority (High/Medium/Low) or leave blank: ").strip() or "Medium"

        if recurring is None:
            recurring = input("Enter recurring interval (daily/weekly/monthly/yearly) or leave blank: ").strip().lower()
            if recurring not in ["", "daily", "weekly", "monthly", "yearly"]:
                print(RED + "Invalid recurring interval. Please enter daily, weekly, monthly, yearly, or leave blank." + RESET)
                recurring = None
                continue

        if categories is None:
            categories = input("Enter categories (comma separated) or leave blank: ").strip().split(",")
            categories = [c.strip() for c in categories if c.strip()]

        new_task = {
            "title": title,
            "completed": False,
            "due_date": due_date,
            "priority": priority,
            "recurring": recurring,
            "categories": categories,
            "completion_timestamp": None
        }
        tasks.append(new_task)
        print(GREEN + f"Task '{title}' added successfully." + RESET)
        return tasks

def remove_task(tasks):
    display_tasks(tasks)
    choice = input("\nEnter the task number(s) to remove (e.g. '1' or '1,2,3'): ").strip()
    if not choice:
        return tasks
    indices = [int(x)-1 for x in choice.split(",") if x.strip().isdigit()]
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if 0 <= idx < len(tasks):
            removed_task = tasks.pop(idx)
            print(f"Task '{removed_task['title']}' removed.")
        else:
            print(f"Invalid task number: {idx+1}")
    return tasks
def is_valid_date(date_str):
    """
    Validate that the provided date is not before the START_DATE (01-01-2025).
    """
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        if date < START_DATE:
            return False
        return True
    except ValueError:
        return False

def edit_task(tasks):
    display_tasks(tasks)
    choice = input("\nEnter the task number to edit: ").strip()
    if not choice.isdigit() or int(choice) - 1 not in range(len(tasks)):
        print(RED + "Invalid task number." + RESET)
        return tasks

    idx = int(choice) - 1
    task = tasks[idx]

    print(f"Editing task '{task['title']}'")
    new_title = input("Enter updated title (leave blank to keep current): ").strip()
    if new_title:
        if len(new_title) > 60:
            print(RED + "Error: Task description exceeds 60 characters. Update canceled." + RESET)
            return tasks
        task["title"] = new_title

    new_due = input("Enter updated due date (YYYY-MM-DD) or blank to keep current: ").strip()
    if new_due:
        if not is_valid_date(new_due):
            print(RED + f"Error: Date cannot be before {START_DATE.strftime('%Y-%m-%d')}. Update canceled." + RESET)
            return tasks
        task["due_date"] = new_due

    new_priority = input("Enter updated priority (High/Medium/Low) or blank to keep current: ").strip()
    if new_priority:
        task["priority"] = new_priority

    print(GREEN + f"Task '{task['title']}' updated successfully." + RESET)
    return tasks


def toggle_task_status(tasks):
    display_tasks(tasks)  # Display all tasks for user to choose from
    choice = input("\nEnter the task number(s) to toggle: ").strip()
    if not choice:
        return tasks

    indices = [int(x) - 1 for x in choice.split(",") if x.strip().isdigit()]

    for idx in indices:
        if 0 <= idx < len(tasks):
            task = tasks[idx]
            if task["completed"]:
                # Mark as incomplete and remove timestamp
                task["completed"] = False
                task["completion_timestamp"] = None
                print(f"Task '{task['title']}' marked as incomplete.")
            else:
                # Mark as complete and set timestamp
                task["completed"] = True
                task["completion_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Task '{task['title']}' marked as complete. Completion time: {task['completion_timestamp']}")
                
                # Add next occurrence for recurring tasks
                if task.get("recurring"):
                    add_next_occurrence(tasks, task)
        else:
            print(f"Invalid task number: {idx+1}")
    return tasks

def add_next_occurrence(tasks, completed_task):
    if not completed_task.get("due_date"):
        print("Cannot add next occurrence without a due date.")
        return

    # Calculate the next due date
    current_due_date = datetime.datetime.strptime(completed_task["due_date"], "%Y-%m-%d").date()
    interval = completed_task.get("recurring")

    if interval == "daily":
        next_due_date = current_due_date + datetime.timedelta(days=1)
    elif interval == "weekly":
        next_due_date = current_due_date + datetime.timedelta(weeks=1)
    elif interval == "monthly":
        next_due_date = current_due_date + datetime.timedelta(days=30)  # Approximate 30-day months
    elif interval == "yearly":
        next_due_date = current_due_date + datetime.timedelta(days=365)
    else:
        print("Invalid recurring interval.")
        return

    # Add the next occurrence as a new task
    new_task = {
        "title": completed_task["title"],
        "completed": False,
        "due_date": next_due_date.strftime("%Y-%m-%d"),
        "priority": completed_task.get("priority", "Medium"),
        "recurring": interval,
        "categories": completed_task.get("categories", []),
        "completion_timestamp": None
    }
    tasks.append(new_task)
    print(f"New recurring occurrence added for '{new_task['title']}' due on {new_task['due_date']}.")

def archive_completed_tasks(tasks):
    archived = load_archive()
    incompleted = []
    for t in tasks:
        if t["completed"]:
            archived.append(t)
        else:
            incompleted.append(t)
    save_archive(archived)
    print("Completed tasks archived.")
    return incompleted

def display_completed_tasks(tasks):
    print("\nCompleted Tasks:")
    has_completed_tasks = False
    for task in tasks:
        if task["completed"]:
            has_completed_tasks = True
            timestamp = task.get("completion_timestamp", "N/A")
            print(f"Task: {task['title']} | Completed On: {timestamp}")
    if not has_completed_tasks:
        print("No completed tasks found.")

def search_tasks(tasks):
    query = input("Enter search query: ").strip()
    display_tasks(tasks, show_all=True, search_query=query)

def filter_by_category(tasks):
    cat = input("Enter category to filter: ").strip()
    display_tasks(tasks, show_all=True, filter_category=cat)

def toggle_view_incomplete(tasks):
    display_tasks(tasks, show_all=False)

def export_tasks_to_csv(tasks, filename="tasks_export.csv"):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["title", "completed", "due_date", "priority", "recurring", "categories", "completion_timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for t in tasks:
            writer.writerow(t)
    print(f"Tasks exported to {filename}")

def export_tasks_to_json(tasks, filename="tasks_export.json"):
    with open(filename, 'w') as f:
        json.dump(tasks, f, indent=2)
    print(f"Tasks exported to {filename}")

def show_report(tasks):
    total = len(tasks)
    completed = sum(t["completed"] for t in tasks)
    overdue = sum(is_overdue(t) for t in tasks if not t["completed"])
    print("Task Report:")
    print(f"Total tasks: {total}")
    print(f"Completed tasks: {completed}")
    print(f"Overdue tasks: {overdue}")

def remind_tasks(tasks):
    # Show tasks due soon based on config
    days_ahead = config.get("reminder_days_ahead", 1)
    soon = [t for t in tasks if not t["completed"] and is_due_soon(t, days_ahead)]
    if soon:
        print("\nReminder: The following tasks are due soon:")
        for t in soon:
            print(f"- {t['title']} (Due: {t['due_date']})")

def show_overdue_alerts(tasks):
    overdue_tasks = [t for t in tasks if is_overdue(t) and not t["completed"]]
    if overdue_tasks:
        print(RED + "\nWARNING: You have overdue tasks!" + RESET)
        for t in overdue_tasks:
            print(f"- {t['title']} (Due: {t['due_date']})")

def print_help():
    print("Usage:")
    print("  python todo.py [--help] [--add 'Task Title'] [--due 'YYYY-MM-DD'] [--priority PRIORITY]")
    print("                 [--recurring INTERVAL] [--category CATEGORY] [--list] [--search QUERY]")
    print("                 [--filter CATEGORY] [--sort SORT_BY] [--report] [--export CSV|JSON]")
    print("\nOptions:")
    print("  --help               Show this help message")
    print("  --add 'Task Title'   Add a task with the given title")
    print("  --due YYYY-MM-DD     Set due date for the added task")
    print("  --priority PRIORITY  Set priority (High, Medium, Low) for the added task")
    print("  --recurring INTERVAL Set recurring interval (daily/weekly/monthly/yearly)")
    print("                       Leave blank or omit for one-time tasks.")
    print("  --category CAT       Add category to the task")
    print("  --list               List tasks")
    print("  --search QUERY       Search tasks by title")
    print("  --filter CAT         Filter tasks by category")
    print("  --sort FIELD         Sort tasks by 'due_date', 'priority', or 'category'")
    print("  --report             Show task statistics")
    print("  --export FORMAT      Export tasks to CSV or JSON")
    print("\nWithout arguments, interactive mode is used.")

def parse_args(tasks):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--help", action="store_true")
    parser.add_argument("--add", type=str, default=None)
    parser.add_argument("--due", type=str, default=None)
    parser.add_argument("--priority", type=str, default=None)
    parser.add_argument("--recurring", type=str, default=None)
    parser.add_argument("--category", action='append', default=[])
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--search", type=str, default=None)
    parser.add_argument("--filter", type=str, default=None)
    parser.add_argument("--sort", type=str, default=None)
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--export", type=str, default=None)
    args = parser.parse_args()

    if args.help:
        print_help()
        sys.exit(0)

    if args.add:
        tasks = add_task(tasks, title=args.add, due_date=args.due, priority=args.priority,
                         recurring=args.recurring, categories=args.category)
        save_tasks(tasks)

    if args.list:
        display_tasks(tasks, show_all=True, sort_by=args.sort)

    if args.search:
        display_tasks(tasks, show_all=True, search_query=args.search, sort_by=args.sort)

    if args.filter:
        display_tasks(tasks, show_all=True, filter_category=args.filter, sort_by=args.sort)

    if args.report:
        show_report(tasks)

    if args.export:
        if args.export.lower() == "csv":
            export_tasks_to_csv(tasks)
        elif args.export.lower() == "json":
            export_tasks_to_json(tasks)

    if len(sys.argv) > 1:
        sys.exit(0)

    return tasks

def main():
    tasks = load_tasks()
    show_overdue_alerts(tasks)
    remind_tasks(tasks)
    tasks = archive_completed_tasks(tasks)

    if len(sys.argv) > 1:
        tasks = parse_args(tasks)
        return

    while True:
        print("\nOptions:")
        print("1. View tasks")
        print("2. Add task")
        print("3. Remove task")
        print("4. Edit task")
        print("5. Mark task as complete/incomplete")
        print("6. Filter by category")
        print("7. Search tasks")
        print("8. Show only incomplete tasks")
        print("9. Sort tasks (by due_date/priority/category)")
        print("10. Show report")
        print("11. Export tasks")
        print("12. Archive completed tasks")
        print("13. Display completed tasks")
        print("14. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            display_tasks(tasks, show_all=True)
        elif choice == "2":
            tasks = add_task(tasks)
            save_tasks(tasks)
        elif choice == "3":
            tasks = remove_task(tasks)
            save_tasks(tasks)
        elif choice == "4":
            tasks = edit_task(tasks)
            save_tasks(tasks)
        elif choice == "5":
            tasks = toggle_task_status(tasks)
            save_tasks(tasks)
        elif choice == "6":
            filter_by_category(tasks)
        elif choice == "7":
            search_tasks(tasks)
        elif choice == "8":
            toggle_view_incomplete(tasks)
        elif choice == "9":
            sort_option = input("Enter sort field (due_date/priority/category): ").strip()
            display_tasks(tasks, show_all=True, sort_by=sort_option)
        elif choice == "10":
            show_report(tasks)
        elif choice == "11":
            fmt = input("Enter format (csv/json): ").strip().lower()
            if fmt == "csv":
                export_tasks_to_csv(tasks)
            else:
                export_tasks_to_json(tasks)
        elif choice == "12":
            tasks = archive_completed_tasks(tasks)
            save_tasks(tasks)
        elif choice == "13":
            display_completed_tasks(tasks)
        elif choice == "14":
            print("Exiting To-Do List application. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
