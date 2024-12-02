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
