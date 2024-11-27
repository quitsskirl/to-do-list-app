import os

# File to store the tasks
TODO_FILE = "todo_list.txt"

# Load tasks from file
def load_tasks():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as file:
            tasks = [task.strip() for task in file.readlines()]
    else:
        tasks = []
    return tasks

# Save tasks to file
def save_tasks(tasks):
    with open(TODO_FILE, 'w') as file:
        file.write("\n".join(tasks))

# Display tasks
def display_tasks(tasks):
    if not tasks:
        print("\nNo tasks in your to-do list.")
    else:
        print("\nTo-Do List:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")

# Add a new task
def add_task(tasks):
    task = input("Enter a new task: ")
    if task.strip():
        tasks.append(task)
        print(f"Task '{task}' added.")
    else:
        print("Task cannot be empty.")
    return tasks

# Remove a task by its number
def remove_task(tasks):
    display_tasks(tasks)
    try:
        task_num = int(input("\nEnter the task number to remove: ")) - 1
        if 0 <= task_num < len(tasks):
            removed_task = tasks.pop(task_num)
            print(f"Task '{removed_task}' removed.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")
    return tasks

# Main function to run the app
def main():
    tasks = load_tasks()

    while True:
        print("\nOptions:")
        print("1. View tasks")
        print("2. Add task")
        print("3. Remove task")
        print("4. Exit")

        choice = input("\nChoose an option: ")
        if choice == "1":
            display_tasks(tasks)
        elif choice == "2":
            tasks = add_task(tasks)
            save_tasks(tasks)
        elif choice == "3":
            tasks = remove_task(tasks)
            save_tasks(tasks)
        elif choice == "4":
            print("Exiting To-Do List application. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

# Run the app
if __name__ == "__main__":
    main()

