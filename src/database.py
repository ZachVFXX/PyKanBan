import sqlite3
from datetime import date
import sys
import os
import configparser


class Database:
    def __init__(self):
        self.DIR_PATH = os.path.dirname(sys.argv[0])
        self.CONFIG_FILE_NAME = "settings.ini"
        self.CONFIG_FILE_PATH = os.path.join(self.DIR_PATH, self.CONFIG_FILE_NAME)
        self.FILE_PATH = os.path.join(self.DIR_PATH, "database")
        print(self.FILE_PATH)
        self.NAME = "PyKanBan.db"
        self.DATABASE_PATH = os.path.join(self.DIR_PATH, self.FILE_PATH, self.NAME)

    def create_config_file(self):
        config = configparser.ConfigParser()
        config["DEFAULT"] = {
            "database_path": self.DATABASE_PATH,
        }
        with open(self.CONFIG_FILE_PATH, "w") as configfile:
            config.write(configfile)

    def read_config_file(self):
        config = configparser.ConfigParser()
        config.read(self.CONFIG_FILE_PATH)
        path = config["DEFAULT"]["database_path"]
        return path

    def modify_config_file(self, key, value):
        config = configparser.ConfigParser()
        config.read(self.CONFIG_FILE_PATH)
        config["DEFAULT"][key] = value
        with open(self.CONFIG_FILE_PATH, "w") as configfile:
            config.write(configfile)

    def initialize_database(self):
        """Initialize the database, creating tables if they don't exist."""
        self.create_database()
        if not self.get_kanbans():
            id = self.create_kanban("Default")
            self.create_column("To Do", id)
            self.create_column("In Progress", id)
            self.create_column("Done", id)

    def create_database(self):
        if not os.path.exists(self.read_config_file()):
            os.makedirs(self.FILE_PATH)

        self.DATABASE_PATH = os.path.join(self.read_config_file(), self.NAME)
        print("DATABASE_PATH", self.DATABASE_PATH)

        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        # Create tables for tasks, columns, and Kanban boards
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Task
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           title TEXT NOT NULL,
                           created_at TEXT NOT NULL)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Note
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           title TEXT NOT NULL,
                           content TEXT NOT NULL)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Kanban
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT UNIQUE NOT NULL)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS KanbanColumn
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           kanban_id INTEGER NOT NULL,
                           FOREIGN KEY (kanban_id) REFERENCES Kanban (id),
                           UNIQUE (name, kanban_id))"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS TaskColumnLink
                          (task_id INTEGER NOT NULL,
                           column_id INTEGER NOT NULL,
                           FOREIGN KEY (task_id) REFERENCES Task (id),
                           FOREIGN KEY (column_id) REFERENCES KanbanColumn (id),
                           PRIMARY KEY (task_id, column_id))"""
        )

        # Create last_kanban table
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS last_kanban
                              (id INTEGER PRIMARY KEY CHECK (id = 1),
                               kanban_id INTEGER,
                               FOREIGN KEY (kanban_id) REFERENCES Kanban (id))"""
        )

        cursor.execute(
            "INSERT OR IGNORE INTO last_kanban (id, kanban_id) VALUES (1, 1)"
        )

        conn.commit()
        conn.close()

    def update_current_kanban(self, kanban_id: int):
        """
        Update the last kanban ID in the database.
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE last_kanban SET kanban_id = ? WHERE id = 1", (kanban_id,)
            )
            conn.commit()

        except sqlite3.Error as e:
            print(f"Error updating last kanban ID: {e}")
        finally:
            conn.close()

    def get_current_kanban(self):
        """
        Retrieve the ID of the last kanban that was used.

        :return: The ID of the last kanban used, or None if no kanban has been used yet
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT kanban_id FROM last_kanban WHERE id = 1")
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None

        except sqlite3.Error as e:
            print(f"Error retrieving last kanban ID: {e}")
            return None
        finally:
            conn.close()

    def create_kanban(self, name):
        """
        Create a new Kanban board with the specified name.

        :argument name: The name of the new Kanban board.

        :return: The ID of the new Kanban board.
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
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

    def get_kanbans(self):
        """
        Retrieve all Kanban boards from the database.

        return: A list of tuples, where each tuple contains the ID and name of a Kanban board.
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM Kanban")
        kanbans = cursor.fetchall()
        conn.close()
        return kanbans

    def modify_kanban(self, kanban_id, new_name):
        """Modify a Kanban board's name in the database."""
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE Kanban SET name = ? WHERE id = ?", (new_name, kanban_id)
            )
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

    def delete_kanban(self, kanban_id):
        """Delete a Kanban board and all associated columns and tasks."""
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        try:
            # Delete associated task-column links
            cursor.execute(
                """
                DELETE FROM TaskColumnLink
                WHERE column_id IN (SELECT id FROM KanbanColumn WHERE kanban_id = ?)
            """,
                (kanban_id,),
            )

            # Delete associated columns
            cursor.execute("DELETE FROM KanbanColumn WHERE kanban_id = ?", (kanban_id,))

            # Delete the Kanban board
            cursor.execute("DELETE FROM Kanban WHERE id = ?", (kanban_id,))

            conn.commit()
            if cursor.rowcount > 0:
                print(
                    f"Kanban board with ID {kanban_id} and all associated data deleted."
                )
                return True
            else:
                print(f"Error: Kanban board with ID {kanban_id} not found.")
                return False
        finally:
            conn.close()

    def create_column(self, name, kanban_id):
        """Create a new Kanban column with the specified name in the given Kanban board."""
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO KanbanColumn (name, kanban_id) VALUES (?, ?)",
                (name, kanban_id),
            )
            conn.commit()
            print(f"Column '{name}' created successfully in Kanban board {kanban_id}.")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Error: Column '{name}' already exists in Kanban board {kanban_id}.")
            return None
        finally:
            conn.close()

    def get_columns(self, kanban_id):
        """Retrieve all Kanban columns for a specific Kanban board from the database."""
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, name FROM KanbanColumn WHERE kanban_id = ?", (kanban_id,)
        )
        columns = cursor.fetchall()
        conn.close()
        return columns

    def delete_column(self, column_id):
        """Delete a Kanban column with the specified ID."""
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        try:
            # Delete associated task-column links
            cursor.execute(
                "DELETE FROM TaskColumnLink WHERE column_id = ?", (column_id,)
            )

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

    def add_task(self, title: str, column_name: str, kanban_id: int):
        """Add a new task to the database, associating it with the specified column."""
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        # Get the column ID based on the name
        cursor.execute(
            "SELECT id FROM KanbanColumn WHERE name = ? AND kanban_id = ?",
            (column_name, kanban_id),
        )
        column_id = cursor.fetchone()

        if not column_id:
            print(f"Error: Kanban column '{column_name}' not found.")
            return None
        print(date.today())
        # Insert the task into the Task table
        cursor.execute(
            "INSERT INTO Task (title, created_at) VALUES (?, ?)",
            (title, date.today()),
        )
        task_id = cursor.lastrowid

        # Link the task to the column in the TaskColumnLink table
        cursor.execute(
            "INSERT INTO TaskColumnLink (task_id, column_id) VALUES (?, ?)",
            (task_id, column_id[0]),
        )

        conn.commit()
        conn.close()
        return task_id

    def get_tasks(self, column_id=None):
        """Retrieve tasks from the database, optionally filtering by column.

        Returns a list of tuples, where each tuple contains the task ID and the task text.
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        if column_id:
            # Get tasks associated with a specific column
            cursor.execute(
                """
                SELECT Task.id, Task.title, Task.created_at
                FROM Task
                INNER JOIN TaskColumnLink ON Task.id = TaskColumnLink.task_id
                INNER JOIN KanbanColumn ON TaskColumnLink.column_id = KanbanColumn.id
                WHERE KanbanColumn.id = ?
            """,
                (column_id,),
            )
        else:
            # Get all tasks from all columns
            cursor.execute("SELECT id, title, created_at FROM Task")

        tasks = cursor.fetchall()
        conn.close()
        return tasks

    def get_task_by_id(self, task_id):
        """Retrieve a task from the database by its ID.

        Returns a tuple containing the task ID and task text, or None if the task is not found.
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title FROM Task WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        conn.close()
        return task

    def modify_task(self, task_id, new_title=None, new_column_name=None):
        """Modify a task's text or column in the database.

        Args:
                    :param new_content: The new content for the task.
            task_id (int): The ID of the task to modify.
            new_text (str, optional): The new text for the task.
            new_column_name (str, optional): The new column name for the task.

        Returns:
            bool: True if the modification was successful, False otherwise.
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        try:
            if new_title:
                # Update the task text
                cursor.execute(
                    "UPDATE Task SET title = ? WHERE id = ?", (new_title, task_id)
                )

            if new_column_name:
                # Get the ID of the new column
                cursor.execute(
                    "SELECT id FROM KanbanColumn WHERE name = ?", (new_column_name,)
                )
                new_column_id = cursor.fetchone()[0]

                # Update the task-column link
                cursor.execute(
                    "UPDATE TaskColumnLink SET column_id = ? WHERE task_id = ?",
                    (new_column_id, task_id),
                )

            conn.commit()
            return True
        except Exception as e:
            print(f"Error modifying task: {e}")
            return False
        finally:
            conn.close()

    def delete_task(self, text):
        """Delete a task from the database based on its text."""
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        # Find the task ID based on text
        cursor.execute("SELECT id FROM Task WHERE title = ?", (text,))
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

    def get_kanban_name(self, kanban_id):
        """Retrieve the name of a Kanban board from its ID."""
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM Kanban WHERE id = ?", (kanban_id,))
        kanban_name = cursor.fetchone()
        conn.close()
        if kanban_name:
            return kanban_name[0]
        else:
            return "Kanban"

    def get_all_notes(self):
        """
        Retrieve all notes from the database.

        return: A list of tuples, where each tuple contains the ID of the note, its title, and its content.
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title, content FROM Note")
        notes = cursor.fetchall()
        conn.close()
        return notes

    def add_note(self, title, content):
        """
        Add a new note to the database.

        :param title: The title of the note.
        :param content: The content of the note.
        :return: The ID of the new note.
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Note (title, content) VALUES (?, ?)", (title, content)
        )
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_note(self, note_id):
        """
        Retrieve a note from the database by its ID.

        :param note_id: The ID of the note to retrieve.
        :return: A tuple containing the ID, title, and content of the note.
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM Note WHERE id = ?", (note_id,))
        note = cursor.fetchone()
        conn.close()
        return note

    def update_note(self, note_id, title, content):
        """
        Update a note in the database.

        :param note_id: The ID of the note to update.
        :param title: The new title of the note.
        :param content: The new content of the note.
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE Note SET title = ?, content = ? WHERE id = ?",
            (title, content, note_id),
        )
        conn.commit()
        conn.close()

    def delete_note(self, note_id):
        """
        Delete a note from the database.

        :param note_id: The ID of the note to delete.
        """
        conn = sqlite3.connect(self.DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM Note WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()
