import os

TODO_FILE = "todo_list.txt"





def load_tasks():
    """
    Loads tasks from a specified file if it exists.

    - Checks if the TODO_FILE exists in the file system.
    - If the file exists:
        - Opens the file in read mode ('r') using a context manager (`with` statement).
        - Reads all lines from the file and strips any leading/trailing whitespace.
        - Stores each line (task) in a list called 'tasks'.
    - If the file does not exist:
        - Initializes 'tasks' as an empty list.

    Returns:
        list: A list of tasks loaded from the file, or an empty list if the file doesn't exist.
    """
    if os.path.exists(TODO_FILE):  # Check if the file exists
        with open(TODO_FILE, 'r') as file:  # Open the file in read mode
            tasks = [task.strip() for task in file.readlines()]  # Read and strip each line
    else:
        tasks = []  # Initialize an empty list if the file doesn't exist
    return tasks  # Return the list of tasks


def save_tasks(tasks):
    """
    Saves a list of tasks to a file.

    Args:
        tasks (list): A list of task strings to be saved.

    Process:
    1. Opens the file specified by the TODO_FILE variable in write mode ('w').
    2. Joins the tasks list into a single string with each task on a new line.
    3. Writes the resulting string to the file, overwriting its contents.
    4. Automatically closes the file when the 'with' block is exited.
    """
    with open(TODO_FILE, 'w') as file:
        file.write("\n".join(tasks))






def display_tasks(tasks):
    if not tasks:
        print("\nNo tasks in your to-do list.")
    else:
        print("\nTo-Do List:")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task}")



# Function: display_tasks
# Purpose: Displays the list of tasks in a formatted manner.
# Parameters: 
#   - tasks (list): A list of tasks to display.
# Behavior:
#   1. Checks if the list 'tasks' is empty.
#      - If empty, prints a message indicating there are no tasks.
#   2. If the list is not empty:
#      - Prints a header "To-Do List:".
#      - Iterates over the list of tasks using enumerate to display each task with its corresponding number.
