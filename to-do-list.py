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

categories = [
    ["Category ID", "Category Name", "Description"],
    [1, "Work", "Tasks related to your job or career"],
    [2, "Personal", "Personal tasks and errands"],
    [3, "Fitness", "Workouts, health, and fitness-related tasks"],
    [4, "Shopping", "Grocery lists, online purchases, etc."],
    [5, "Learning", "Educational tasks like courses or reading"],
]


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
    try:
        # Attempt to parse date in YYYY-MM-DD format
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        # If the date format is invalid, return None
        return None


def is_overdue(task):
    due_date_str = task.get("due_date")
    if due_date_str:
        due = parse_date(due_date_str)
        if due is None:  # Handle invalid date
            print(f"Warning: Task '{task.get('title', 'Unknown')}' has an invalid due date: {due_date_str}")
            return False
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

def get_category_name(category_id, categories):
    """
    Retrieve the category name based on the category ID.
    """
    for category in categories[1:]:  # Skip the header row
        if category[0] == category_id:
            return category[1]
    return "Unknown"

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
            cat_names = [get_category_name(cat_id, categories) for cat_id in task.get("categories", [])]
            cat_str = f" (Categories: {', '.join(cat_names)})" if cat_names else ""
            prio_str = f" (Priority: {task.get('priority', 'Medium')})"
            recur_str = f" (Recurring: {task.get('recurring')})" if task.get('recurring') else ""
            title = task["title"]
            print(f"{c}{i}. {status} {title}{due_str}{prio_str}{cat_str}{recur_str}{RESET}")

def add_task(tasks, title=None, due_date=None, priority=None, recurring=None, categories=None):
    while True:
        if not title:
            title = input("Enter a new task (max 60 characters): ").strip()

        # Check if the task exceeds 60 characters
        if len(title) > 60:
            print(RED + "Error: Task description exceeds 60 characters. Please try again." + RESET)
            title = None  # Reset title to force re-entry
            continue

        if not title:
            print(RED + "Task cannot be empty. Please try again." + RESET)
            continue

        # Date validation
        while True:
            if due_date is None:
                due_date = input("Enter due date (YYYY-MM-DD) or leave blank: ").strip()
            if due_date:
                try:
                    parsed_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
                    if parsed_date < datetime.date(2025, 1, 1):
                        print(RED + f"Error: Date cannot be before 2025-01-01. Please try again." + RESET)
                        due_date = None  # Reset due_date to retry
                        continue
                    break  # Valid date
                except ValueError:
                    print(RED + "Error: Invalid date format. Please enter a valid date in YYYY-MM-DD format." + RESET)
                    due_date = None  # Reset due_date to retry
                    continue
            else:
                break  # Allow blank due date

        if priority is None:
            priority = input("Enter priority (High/Medium/Low) or leave blank: ").strip() or "Medium"

        if recurring is None:
            recurring = input("Enter recurring interval (daily/weekly/monthly/yearly) or leave blank: ").strip() or None

        # Display categories and allow selection
        display_categories(categories)
        cat_input = input("Enter category IDs (comma separated) or leave blank: ").strip()
        selected_categories = [int(cat_id.strip()) for cat_id in cat_input.split(",") if cat_id.strip().isdigit()]

        # Validate category IDs
        valid_category_ids = [category[0] for category in categories[1:]]
        selected_categories = [cat_id for cat_id in selected_categories if cat_id in valid_category_ids]

        new_task = {
            "title": title,
            "completed": False,
            "due_date": due_date,
            "priority": priority,
            "recurring": recurring,
            "categories": selected_categories,
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
    completed = [t for t in tasks if t["completed"]]
    if not completed:
        print("No completed tasks found.")
    else:
        for i, task in enumerate(completed, 1):
            c = GREEN
            title = task["title"]
            timestamp = f" (Completed On: {task.get('completion_timestamp', 'N/A')})"
            print(f"{c}{i}. {title}{timestamp}{RESET}")

def search_tasks(tasks):
    query = input("Enter search query: ").strip()
    display_tasks(tasks, show_all=True, search_query=query)

def display_categories(categories):
    print("\nCategories:")
    for category in categories[1:]:  # Skip the header row
        print(f"ID: {category[0]} | Name: {category[1]} | Description: {category[2]}")
def add_category(categories):
    next_id = max(category[0] for category in categories[1:]) + 1  # Generate the next ID
    name = input("Enter category name: ").strip()
    if not name:
        print("Category name cannot be empty.")
        return categories
    description = input("Enter category description: ").strip()
    categories.append([next_id, name, description])
    print(f"Category '{name}' added successfully with ID {next_id}.")
    return categories
def view_tasks_by_day(tasks):
    """
    Display tasks for a specific day.
    """
    date_str = input("Enter the date (YYYY-MM-DD) to view tasks for that day: ").strip()
    try:
        selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(RED + "Error: Invalid date format. Please enter a date in YYYY-MM-DD format." + RESET)
        return

    # Filter tasks for the selected date
    tasks_for_day = [task for task in tasks if task.get("due_date") == date_str]

    if not tasks_for_day:
        print(GREEN + f"No tasks scheduled for {selected_date}." + RESET)
    else:
        print(BLUE + f"Tasks scheduled for {selected_date}:" + RESET)
        display_tasks(tasks_for_day, show_all=True)


def filter_tasks_by_category(tasks, categories):
    display_categories(categories)  # Show all categories
    cat_id_input = input("Enter the category ID to filter tasks: ").strip()
    if not cat_id_input.isdigit():
        print("Invalid category ID. Please enter a numeric value.")
        return
    cat_id = int(cat_id_input)
    filtered_tasks = [task for task in tasks if cat_id in task.get("categories", [])]
    if not filtered_tasks:
        print("No tasks found for this category.")
    else:
        print(f"\nTasks in Category ID {cat_id}:")
        display_tasks(filtered_tasks, show_all=True)  # Display filtered tasks



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

    # Ensure categories are initialized
    global categories
    categories = [
        ["Category ID", "Category Name", "Description"],
        [1, "Work", "Tasks related to your job or career"],
        [2, "Personal", "Personal tasks and errands"],
        [3, "Fitness", "Workouts, health, and fitness-related tasks"],
        [4, "Shopping", "Grocery lists, online purchases, etc."],
        [5, "Learning", "Educational tasks like courses or reading"],
    ]

    if len(sys.argv) > 1:
        tasks = parse_args(tasks)
        return

    while True:
        if tasks:
            print("\nOptions:")
            print("1. View tasks (incomplete tasks only)")
            print("2. View tasks by day")  # Updated to option 2
            print("3. Add task")
            print("4. Remove task")
            print("5. Edit task")
            print("6. Mark task as complete/incomplete")
            print("7. Filter by category")
            print("8. Search tasks")
            print("9. Show only incomplete tasks")
            print("10. Sort tasks (by due_date/priority/category)")
            print("11. Show report")
            print("12. Export tasks")
            print("13. Archive completed tasks")
            print("14. Display completed tasks")
            print("15. Manage categories")
            print("16. Exit")
        else:
            print("\nOptions:")
            print("1. Add task")
            print("2. Exit")

        choice = input("\nChoose an option: ").strip()

        if not tasks:
            # Limited options when no tasks are present
            if choice == "1":
                tasks = add_task(tasks, categories=categories)  # Pass categories to add_task
                save_tasks(tasks)
            elif choice == "2":
                print("Exiting program. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")
        else:
            # Full options when tasks are present
            if choice == "1":
                display_tasks(tasks, show_all=False)
            elif choice == "2":
                view_tasks_by_day(tasks)  # Updated to option 2
            elif choice == "3":
                tasks = add_task(tasks, categories=categories)  # Pass categories to add_task
                save_tasks(tasks)
            elif choice == "4":
                tasks = remove_task(tasks)
                save_tasks(tasks)
            elif choice == "5":
                tasks = edit_task(tasks)
                save_tasks(tasks)
            elif choice == "6":
                tasks = toggle_task_status(tasks)
                save_tasks(tasks)
            elif choice == "7":
                filter_tasks_by_category(tasks, categories)  # Use the corrected function name
            elif choice == "8":
                search_tasks(tasks)
            elif choice == "9":
                toggle_view_incomplete(tasks)
            elif choice == "10":
                sort_option = input("Enter sort field (due_date/priority/category): ").strip()
                display_tasks(tasks, show_all=True, sort_by=sort_option)
            elif choice == "11":
                show_report(tasks)
            elif choice == "12":
                fmt = input("Enter format (csv/json): ").strip().lower()
                if fmt == "csv":
                    export_tasks_to_csv(tasks)
                else:
                    export_tasks_to_json(tasks)
            elif choice == "13":
                tasks = archive_completed_tasks(tasks)
                save_tasks(tasks)
            elif choice == "14":
                display_completed_tasks(tasks)
            elif choice == "15":
                # Manage categories
                print("\nCategory Options:")
                print("1. View categories")
                print("2. Add category")
                cat_choice = input("Choose an option: ").strip()
                if cat_choice == "1":
                    display_categories(categories)
                elif cat_choice == "2":
                    categories = add_category(categories)
                else:
                    print("Invalid option. Returning to main menu.")
            elif choice == "16":
                print("Exiting To-Do List application. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()

