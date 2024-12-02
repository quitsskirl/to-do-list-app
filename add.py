def load_tasks():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, 'r') as file:
            tasks = [task.strip() for task in file.readlines()]
    else:
        tasks = []
    return tasks


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





def add_task(tasks):
    task = input("Enter a new task: ")
    if task.strip():
        tasks.append(task)
        print(f"Task '{task}' added.")
    else:
        print("Task cannot be empty.")
    return tasks