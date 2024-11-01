from CTkMenuBar import CustomDropdownMenu
import pywinstyles
import database
from animation import fade_in, fade_out
from setting import *
from ui.ctk_column import KanbanColumn
from ui.ctk_dialog import TaskDialog
from ui.ctk_task import DraggableTask


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.deactivate_automatic_dpi_awareness()  # Its messed up with the drag and drop
        self.title("PyKanBan")
        self.geometry("800x600")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.iconbitmap(LOGO_PATH)
        self.FONT = ctk.CTkFont(family="Poppins", size=16)
        self.BOLD_FONT = ctk.CTkFont(family="Poppins", size=16, weight="bold")

        database.initialize_database()

        self.create_menu_bar()

        self.create_kanban(database.get_current_kanban())

    def rename_kanban(self, kanban_id):
        task_dialog = TaskDialog(
            self, "Rename Kanban", "Enter the new name:", "Save edit"
        )
        task_dialog.update()
        self.wait_window(task_dialog)
        if task_dialog.task_title:
            database.modify_kanban(kanban_id, task_dialog.task_title)
            self.title(f"Kanban - {task_dialog.task_title}")
            self.create_submenu()

    def delete_kanban(self, kanban_id):
        database.delete_kanban(kanban_id)
        self.destroy_columns()
        if database.get_kanbans():
            self.create_kanban(database.get_kanbans()[0][0])
        else:
            self.create_new_kanban()
        self.create_submenu()

    def create_kanban(self, kanban_id):
        # Create the columns and tasks
        self.columns = []
        self.tasks = []
        list_of_columns = database.get_columns(kanban_id)
        for i, column_name in enumerate(list_of_columns):
            self.columns.append(KanbanColumn(self, column_name[1], self))
            for tasks in database.get_tasks(column_name[0]):
                task = DraggableTask(
                    master=self.columns[i].task_frame,
                    text=tasks[1],
                    id=tasks[0],
                    app=self,
                )
                task.pack(fill="x", padx=5, pady=2)
                self.tasks.append(task)
                pywinstyles.set_opacity(task.winfo_id(), value=0.0)

        # Set the grid layout for the columns
        for i, column in enumerate(self.columns):
            column.grid(row=1, column=i, padx=4, pady=4, sticky="nsew")
            pywinstyles.set_opacity(column.winfo_id(), value=0.0)
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Fade in the columns and tasks
        for column in self.columns:
            fade_in(self, column.winfo_id())
        for task in self.tasks:
            fade_in(self, task.winfo_id())

        # Set the kanban ID and update the title
        self.kanban_id = kanban_id
        self.title(f"Kanban - {database.get_kanban_name(kanban_id)}")
        self.file_button.configure(text=database.get_kanban_name(kanban_id))
        database.update_current_kanban(kanban_id)
        self.create_submenu()

    def destroy_columns(self):
        print(self.columns)
        if self.columns is not None:
            for column in self.columns:
                fade_out(self, column.winfo_id())
                column.destroy()
                self.columns = []

    def switch_kanban(self, kanban_id):
        self.destroy_columns()
        self.create_kanban(kanban_id)

    def create_new_kanban(self):
        task_dialog = TaskDialog(
            self, "Create Kanban", "Enter the name of the new kanban:", "Create"
        )
        self.wait_window(task_dialog)
        if task_dialog.task_title:
            kanban_id = database.create_kanban(task_dialog.task_title)
            database.create_column("To Do", kanban_id)
            database.create_column("In Progress", kanban_id)
            database.create_column("Done", kanban_id)
            self.destroy_columns()
            self.create_kanban(kanban_id)

    def handle_drop(self, task, event):
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()

        for column in self.columns:
            if column.winfo_x() <= x <= column.winfo_x() + column.winfo_width():
                print("IN A COLUMN", column.title)
                fade_out(self, task.winfo_id())
                task.place_forget()  # Remove it from the current place
                task.pack_forget()  # Remove it from the current pack geometry manager
                task = DraggableTask(
                    column.task_frame, task.text, task.id, self
                )  # Create a new task
                task.pack(fill="x", padx=5, pady=2)  # Pack the task into the new column
                fade_in(self, task.winfo_id())
                task.edit(column.title)
                break
        else:
            # If not dropped in any column, return to original position
            task.place_forget()
            task.pack(fill="x", padx=5, pady=2)

    def on_closing(self):
        self.destroy()

    def create_submenu(self):
        for option in self.submenu._options_list:
            option.destroy()
        for kanban in database.get_kanbans():
            self.submenu.add_option(
                option=kanban[1], command=lambda e=kanban[0]: self.switch_kanban(e)
            )

    def create_menu_bar(self):
        self.file_button = ctk.CTkButton(self, text="Kanban", font=self.FONT)
        self.file_button.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        self.dropdown = CustomDropdownMenu(widget=self.file_button)
        self.dropdown.add_option(option="New KanBan", command=self.create_new_kanban)

        self.submenu = self.dropdown.add_submenu(submenu_name="Open KanBan")
        self.create_submenu()

        self.dropdown.add_option(
            option="Rename current Kanban",
            command=lambda: self.rename_kanban(self.kanban_id),
        )

        self.dropdown.add_option(
            option="Delete current Kanban",
            command=lambda: self.delete_kanban(self.kanban_id),
        )

        self.dropdown.add_option(option="Quit", command=lambda: self.on_closing())


if __name__ == "__main__":
    app = App()
    app.mainloop()
