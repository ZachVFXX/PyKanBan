import os
import sqlite3

DATABASE_PATH = "database/PyKanBan.db"

def initialize_database():
    """Initialize the database, creating tables if they don't exist."""
    create_database()
    if not get_kanbans():
        create_kanban("Default")
        create_column("To Do", 1)
        create_column("In Progress", 1)
        create_column("Done", 1)

def create_database():
    if not os.path.exists("database"):
        os.makedirs("database")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create tables for tasks, columns, and Kanban boards
    cursor.execute('''CREATE TABLE IF NOT EXISTS Task
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       text TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Kanban
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT UNIQUE NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS KanbanColumn
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       kanban_id INTEGER NOT NULL,
                       FOREIGN KEY (kanban_id) REFERENCES Kanban (id),
                       UNIQUE (name, kanban_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS TaskColumnLink
                      (task_id INTEGER NOT NULL,
                       column_id INTEGER NOT NULL,
                       FOREIGN KEY (task_id) REFERENCES Task (id),
                       FOREIGN KEY (column_id) REFERENCES KanbanColumn (id),
                       PRIMARY KEY (task_id, column_id))''')

    conn.commit()
    conn.close()

def create_kanban(name):
    """Create a new Kanban board with the specified name."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO Kanban (name) VALUES (?)", (name,))
        conn.commit()
        print(f"Kanban board '{name}' created successfully.")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"Error: Kanban board '{name}' already exists.")
        return None
    finally:
        conn.close()

def get_kanbans():
    """Retrieve all Kanban boards from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM Kanban")
    kanbans = cursor.fetchall()
    conn.close()
    return kanbans

def modify_kanban(kanban_id, new_name):
    """Modify a Kanban board's name in the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE Kanban SET name = ? WHERE id = ?", (new_name, kanban_id))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Kanban board with ID {kanban_id} renamed to '{new_name}'.")
            return True
        else:
            print(f"Error: Kanban board with ID {kanban_id} not found.")
            return False
    except sqlite3.IntegrityError:
        print(f"Error: Kanban board name '{new_name}' already exists.")
        return False
    finally:
        conn.close()

def delete_kanban(kanban_id):
    """Delete a Kanban board and all associated columns and tasks."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Delete associated task-column links
        cursor.execute("""
            DELETE FROM TaskColumnLink
            WHERE column_id IN (SELECT id FROM KanbanColumn WHERE kanban_id = ?)
        """, (kanban_id,))

        # Delete associated columns
        cursor.execute("DELETE FROM KanbanColumn WHERE kanban_id = ?", (kanban_id,))

        # Delete the Kanban board
        cursor.execute("DELETE FROM Kanban WHERE id = ?", (kanban_id,))

        conn.commit()
        if cursor.rowcount > 0:
            print(f"Kanban board with ID {kanban_id} and all associated data deleted.")
            return True
        else:
            print(f"Error: Kanban board with ID {kanban_id} not found.")
            return False
    finally:
        conn.close()

def create_column(name, kanban_id):
    """Create a new Kanban column with the specified name in the given Kanban board."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO KanbanColumn (name, kanban_id) VALUES (?, ?)", (name, kanban_id))
        conn.commit()
        print(f"Column '{name}' created successfully in Kanban board {kanban_id}.")
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"Error: Column '{name}' already exists in Kanban board {kanban_id}.")
        return None
    finally:
        conn.close()

def get_columns(kanban_id):
    """Retrieve all Kanban columns for a specific Kanban board from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM KanbanColumn WHERE kanban_id = ?", (kanban_id,))
    columns = cursor.fetchall()
    conn.close()
    return columns

def delete_column(column_id):
    """Delete a Kanban column with the specified ID."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Delete associated task-column links
        cursor.execute("DELETE FROM TaskColumnLink WHERE column_id = ?", (column_id,))

        # Delete the column
        cursor.execute("DELETE FROM KanbanColumn WHERE id = ?", (column_id,))

        conn.commit()
        if cursor.rowcount > 0:
            print(f"Column with ID {column_id} and all associated links deleted.")
            return True
        else:
            print(f"Error: Column with ID {column_id} not found.")
            return False
    finally:
        conn.close()


def add_task(text, column_name, kanban_id):
    """Add a new task to the database, associating it with the specified column."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get the column ID based on the name
    cursor.execute("SELECT id FROM KanbanColumn WHERE name = ? AND kanban_id = ?", (column_name, kanban_id))
    column_id = cursor.fetchone()

    if not column_id:
        print(f"Error: Kanban column '{column_name}' not found.")
        return None

    # Insert the task into the Task table
    cursor.execute("INSERT INTO Task (text) VALUES (?)", (text,))
    task_id = cursor.lastrowid

    # Link the task to the column in the TaskColumnLink table
    cursor.execute("INSERT INTO TaskColumnLink (task_id, column_id) VALUES (?, ?)", (task_id, column_id[0]))

    conn.commit()
    conn.close()
    return task_id


def get_tasks(column_id=None):
    """Retrieve tasks from the database, optionally filtering by column.

    Returns a list of tuples, where each tuple contains the task ID and the task text.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    if column_id:
        # Get tasks associated with a specific column
        cursor.execute("""
            SELECT Task.id, Task.text
            FROM Task
            INNER JOIN TaskColumnLink ON Task.id = TaskColumnLink.task_id
            INNER JOIN KanbanColumn ON TaskColumnLink.column_id = KanbanColumn.id
            WHERE KanbanColumn.id = ?
        """, (column_id,))
    else:
        # Get all tasks from all columns
        cursor.execute("SELECT id, text FROM Task")

    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_task_by_id(task_id):
    """Retrieve a task from the database by its ID.

    Returns a tuple containing the task ID and task text, or None if the task is not found.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, text FROM Task WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return task

def modify_task(task_id, new_text=None, new_column_name=None):
    """Modify a task's text or column in the database.

    Args:
        task_id (int): The ID of the task to modify.
        new_text (str, optional): The new text for the task.
        new_column_name (str, optional): The new column name for the task.

    Returns:
        bool: True if the modification was successful, False otherwise.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        if new_text:
            # Update the task text
            cursor.execute("UPDATE Task SET text = ? WHERE id = ?", (new_text, task_id))

        if new_column_name:
            # Get the ID of the new column
            cursor.execute("SELECT id FROM KanbanColumn WHERE name = ?", (new_column_name,))
            new_column_id = cursor.fetchone()[0]

            # Update the task-column link
            cursor.execute("UPDATE TaskColumnLink SET column_id = ? WHERE task_id = ?", (new_column_id, task_id))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error modifying task: {e}")
        return False
    finally:
        conn.close()
def delete_task(text):
    """Delete a task from the database based on its text."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Find the task ID based on text
    cursor.execute("SELECT id FROM Task WHERE text = ?", (text,))
    task_id = cursor.fetchone()

    if not task_id:
        print(f"Error: Task with text '{text}' not found.")
        return

    # Delete the link to the column (assuming you only want to remove from one column)
    cursor.execute("DELETE FROM TaskColumnLink WHERE task_id = ?", (task_id[0],))

    # Delete the task itself
    cursor.execute("DELETE FROM Task WHERE id = ?", (task_id[0],))

    conn.commit()
    conn.close()


def get_kanban_name(kanban_id):
    """Retrieve the name of a Kanban board from its ID."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM Kanban WHERE id = ?", (kanban_id,))
    kanban_name = cursor.fetchone()
    conn.close()
    return kanban_name[0]
