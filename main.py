import customtkinter
import customtkinter as ctk
from CTkMenuBar import CustomDropdownMenu
from PIL import Image
import pywinstyles
import database
from database import initialize_database

EDIT_IMG = ctk.CTkImage(Image.open("assets/edit_task.png"), size=(24, 24))
DELETE_IMG = ctk.CTkImage(Image.open("assets/delete_task.png"), size=(24, 24))
ADD_IMG = ctk.CTkImage(Image.open("assets/add_task.png"), size=(24, 24))
MORE_IMG = ctk.CTkImage(Image.open("assets/more_task.png"), size=(24, 24))

class DraggableTask(ctk.CTkFrame):
    def __init__(self, master, text, id, app):
        super().__init__(master, border_width=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.app = app
        self.text = text
        self.id = id

        self.label = ctk.CTkLabel(self, text=text, wraplength=150, anchor="e", justify="left", font=FONT)
        self.label.grid(row=0, column=0, rowspan=5, padx=16, pady=8, sticky="nsw")

        self.edit_button = ctk.CTkButton(self, text="", image=EDIT_IMG, command=self.edit_task, width=48)
        self.edit_button.grid(row=1, column=1, padx=8, pady=(8, 4), sticky="e", columnspan=2)

        self.delete_button = ctk.CTkButton(self, text="", image=DELETE_IMG, command=self.delete, width=48)
        self.delete_button.grid(row=2, column=1, padx=8, pady=(4, 8), sticky="e", columnspan=2)

        self.dummy_task = None
        self.last_column = None

        self.setup_bindings(self.label)
        self.setup_bindings(self)

    def setup_bindings(self, widget, drag=True):
        if drag:
            widget.bind("<ButtonPress-1>", self.start_drag)
            widget.bind("<ButtonRelease-1>", self.stop_drag)
            widget.bind("<B1-Motion>", self.on_drag)

    def save(self, current_column):
        database.add_task(self.text, current_column, self.app.kanban_id)
        print("SAVED")

    def edit_task(self):
        task_dialog = TaskDialog(self, "Edit Task", "Enter the new task description:", "Save edit")
        task_dialog.update()
        task_dialog.focus()
        self.wait_window(task_dialog)
        if task_dialog.task_text:
            database.modify_task(self.id, task_dialog.task_text)
            self.label.configure(text=task_dialog.task_text)
            self.text = task_dialog.task_text

    def edit(self, current_column):
        database.modify_task(self.id, self.text, current_column)

    def delete(self):
        database.delete_task(self.text)
        self.destroy()

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        # Get the mouse pointer's position relative to the app window
        pointer_x = self.winfo_pointerx()
        pointer_y = self.winfo_pointery()

        # Get the app window's top-left corner position relative to the screen
        app_x = self.app.winfo_rootx()
        app_y = self.app.winfo_rooty()

        # Calculate the position relative to the app window
        relative_x = pointer_x - app_x
        relative_y = pointer_y - app_y

        self.initial_master = self.master
        self.lift()

        # Create a dummy task to follow the mouse during dragging

        self.dummy = ctk.CTkFrame(self.app, width=self.winfo_width(), height=self.winfo_height(), border_width=2)
        self.dummy.grid_columnconfigure(2, weight=1)
        self.dummy.grid_rowconfigure(2, weight=1)
        self.label = ctk.CTkLabel(self.dummy, text=self.text, wraplength=150, anchor="e", justify="left", font=FONT)
        self.label.grid(row=0, column=0, rowspan=5, padx=16, pady=8, sticky="nsw")
        self.edit_button = ctk.CTkButton(self.dummy, text="", image=EDIT_IMG, width=48)
        self.edit_button.grid(row=1, column=1, padx=8, pady=(8, 4), sticky="e", columnspan=2)
        self.delete_button = ctk.CTkButton(self.dummy, text="", image=DELETE_IMG, width=48)
        self.delete_button.grid(row=2, column=1, padx=8, pady=(4, 8), sticky="e", columnspan=2)
        pywinstyles.set_opacity(self.dummy, value=0.5)
        self.dummy.place(x=relative_x - self.drag_start_x,
                         y=relative_y - self.drag_start_y)

    def on_drag(self, event):
        # Move the dummy task along with the mouse
        # Get the mouse pointer's position relative to the app window
        pointer_x = self.winfo_pointerx()
        pointer_y = self.winfo_pointery()

        # Get the app window's top-left corner position relative to the screen
        app_x = self.app.winfo_rootx()
        app_y = self.app.winfo_rooty()

        # Calculate the position relative to the app window
        relative_x = pointer_x - app_x
        relative_y = pointer_y - app_y

        self.dummy.place(x=relative_x - self.drag_start_x,
                         y=relative_y - self.drag_start_y)  # Move the dummy to follow the cursor
        self.lift()  # Keep the task on top during the drag

        x = self.app.winfo_pointerx() - self.app.winfo_rootx()
        y = self.app.winfo_pointery() - self.app.winfo_rooty()
        for column in self.app.columns:
            if column.winfo_x() <= x <= column.winfo_x() + column.winfo_width():
                if self.dummy_task is None:
                    self.dummy_task = DraggableTask(column.task_frame, self.text, self.id, self)  # Create a new task
                    self.dummy_task.pack(fill="x", padx=5, pady=2)  # Pack the task into the new column
                    pywinstyles.set_opacity(self.dummy_task, value=0.7)
                elif self.dummy_task is not None and self.last_column != column.title:
                    self.dummy_task.destroy()
                    self.dummy_task = None
                elif self.dummy_task is not None and self.last_column == column.title:
                    pass
                else:
                    self.dummy_task.destroy()
                    self.dummy_task = None
                self.last_column = column.title

    def stop_drag(self, event):
        # After stopping the drag, handle the drop and remove the dummy
        try:
            self.dummy.destroy()
            self.dummy_task.destroy()
            self.dummy_task = None
            self.app.handle_drop(self, event)
        except:
            print("Error")


class KanbanColumn(ctk.CTkFrame):
    def __init__(self, master, title, app):
        super().__init__(master, corner_radius=10)
        self.app = app
        self.title = title

        self.title_label = ctk.CTkLabel(self, text=title, font=BOLD_FONT)
        self.title_label.pack(pady=10)

        self.task_frame = ctk.CTkScrollableFrame(self)
        self.task_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.add_task_button = ctk.CTkButton(self, text="Add Task", image=ADD_IMG, command=self.add_task, font=FONT)
        self.add_task_button.pack(pady=10)

    def add_task(self):
        task_dialog = TaskDialog(self, "Add Task", "Enter task description:", "Add")
        task_dialog.update()
        task_dialog.focus()
        self.wait_window(task_dialog)
        if task_dialog.task_text:
            id = database.add_task(task_dialog.task_text, self.title, self.app.kanban_id)
            if id:
                task = DraggableTask(self.task_frame, task_dialog.task_text, id, self.app)
                task.pack(fill="x", padx=5, pady=2)


class TaskDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, description, button_text):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.task_text = None

        self.label = ctk.CTkLabel(self, text=description)
        self.label.pack(pady=10)

        self.entry = ctk.CTkEntry(self, width=200)
        self.entry.pack(pady=10)

        self.button = ctk.CTkButton(self, text=button_text, command=self.on_add)
        self.button.pack(pady=10)

    def on_add(self):
        self.task_text = self.entry.get()
        self.destroy()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        customtkinter.deactivate_automatic_dpi_awareness()  # Its messed up with the drag and drop
        self.title("PyKanBan")
        self.geometry("800x600")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        global FONT
        FONT = ctk.CTkFont(family="Poppins", size=16)
        global BOLD_FONT
        BOLD_FONT = ctk.CTkFont(family="Poppins", size=16, weight="bold")

        initialize_database()

        self.create_menu_bar()

        self.create_kanban(1)

    def rename_kanban(self, kanban_id):
        task_dialog = TaskDialog(self, "Rename Kanban", "Enter the new name:", "Save edit")
        task_dialog.update()
        task_dialog.focus()
        self.wait_window(task_dialog)
        if task_dialog.task_text:
            database.modify_kanban(kanban_id, task_dialog.task_text)
            self.title(f'Kanban - {task_dialog.task_text}')

    def delete_kanban(self, kanban_id):
        database.delete_kanban(kanban_id)
        for column in self.columns:
            column.destroy()

    def create_kanban(self, kanban_id):
        self.columns = []
        columns_names = database.get_columns(kanban_id)
        print(f'columns_names: {columns_names}')
        print(f'kanban_id: {kanban_id}')
        print(f'self.columns: {self.columns}')
        for i, column_name in enumerate(columns_names):
            self.columns.append(KanbanColumn(self, column_name[1], self))
            for tasks in database.get_tasks(column_name[0]):
                print(f'tasks: {tasks}')
                print(f'column_name: {column_name}')
                print(f'i: {i}')
                task = DraggableTask(self.columns[i].task_frame, tasks[1], tasks[0], self)
                task.pack(fill="x", padx=5, pady=2)
        for i, column in enumerate(self.columns):
            column.grid(row=1, column=i, padx=4, pady=4, sticky="nsew")
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.kanban_id = kanban_id
        self.title(f'Kanban - {database.get_kanban_name(kanban_id)}')
        self.file_button.configure(text=database.get_kanban_name(kanban_id))

    def switch_kanban(self, kanban_id):
        for column in self.columns:
            column.destroy()
        self.create_kanban(kanban_id)

    def create_new_kanban(self):
        task_dialog = TaskDialog(self, "Create Kanban", "Enter the name of the new kanban:", "Create")
        task_dialog.update()
        task_dialog.focus()
        self.wait_window(task_dialog)
        if task_dialog.task_text:
            kanban_id = database.create_kanban(task_dialog.task_text)
            database.create_column("To Do", kanban_id)
            database.create_column("In Progress", kanban_id)
            database.create_column("Done", kanban_id)
            for column in self.columns:
                column.destroy()
            self.create_kanban(kanban_id)

    def handle_drop(self, task, event):
        x = self.winfo_pointerx() - self.winfo_rootx()
        y = self.winfo_pointery() - self.winfo_rooty()

        for column in self.columns:
            if column.winfo_x() <= x <= column.winfo_x() + column.winfo_width():
                print("IN A COLUMN", column.title)
                task.place_forget()  # Remove it from the current place
                task.pack_forget()  # Remove it from the current pack geometry manager
                task = DraggableTask(column.task_frame, task.text, task.id, self)  # Create a new task
                task.pack(fill="x", padx=5, pady=2)  # Pack the task into the new column
                task.edit(column.title)
                break
        else:
            # If not dropped in any column, return to original position
            task.place_forget()
            task.pack(fill="x", padx=5, pady=2)

    def on_closing(self):
        self.destroy()

    def create_menu_bar(self):
        self.file_button = ctk.CTkButton(self, text=database.get_kanban_name(1), font=FONT)
        self.file_button.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")
        dropdown1 = CustomDropdownMenu(widget=self.file_button)
        dropdown1.add_option(option="New KanBan", command=self.create_new_kanban)

        submenu = dropdown1.add_submenu(submenu_name="Open KanBan")
        for kanban in database.get_kanbans():
            submenu.add_option(option=kanban[1], command=lambda e=kanban[0]: self.switch_kanban(e))

        dropdown1.add_option(option="Rename current Kanban", command=lambda: self.rename_kanban(self.kanban_id))

        dropdown1.add_option(option="Delete current Kanban", command=lambda: self.delete_kanban(self.kanban_id))

        dropdown1.add_option(option="Quit", command=lambda: self.on_closing())


if __name__ == "__main__":
    app = App()
    app.mainloop()
