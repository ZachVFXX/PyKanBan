import pywinstyles

import database
from animation import fade_out
from setting import *
from ui.ctk_dialog import TaskDialog


class DraggableTask(ctk.CTkFrame):
    """
    A task that can be dragged and dropped into a Kanban column.
    """

    def __init__(self, master, text, content, id, app):
        super().__init__(master, border_width=2)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.app = app
        self.text = text
        self.id = id
        self.content = content

        global FONT
        FONT = ctk.CTkFont(family="Poppins", size=16)
        global BOLD_FONT
        BOLD_FONT = ctk.CTkFont(family="Poppins", size=16, weight="bold")

        self.label = ctk.CTkLabel(
            self, text=text, wraplength=150, anchor="e", justify="left", font=FONT
        )
        self.label.grid(row=0, column=0, rowspan=5, padx=16, pady=8, sticky="nsw")

        self.edit_button = ctk.CTkButton(
            self, text="", image=EDIT_IMG, command=self.edit_task, width=48
        )
        self.edit_button.grid(
            row=1, column=1, padx=8, pady=(8, 4), sticky="e", columnspan=2
        )

        self.delete_button = ctk.CTkButton(
            self, text="", image=DELETE_IMG, command=self.delete, width=48
        )
        self.delete_button.grid(
            row=2, column=1, padx=8, pady=(4, 8), sticky="e", columnspan=2
        )

        self.content_box = None

        self.dummy_task = None
        self.last_column = None

        self.setup_bindings(self.label)
        self.setup_bindings(self)

    def task_info(self):
        if self.content_box is not None:
            self.content_box.destroy()
            self.content_box = None
        elif self.content is not None:
            self.content_box = ctk.CTkLabel(
                self,
                text=self.content,
                wraplength=150,
                anchor="e",
                justify="left",
                font=FONT,
            )
            self.content_box.grid(
                row=3, column=0, rowspan=5, padx=16, pady=8, sticky="nsw"
            )

    def setup_bindings(self, widget):
        widget.bind("<Double-Button-1>", lambda event: self.task_info())
        widget.bind("<ButtonPress-1>", self.start_drag)
        widget.bind("<ButtonRelease-1>", self.stop_drag)
        widget.bind("<B1-Motion>", self.on_drag)

    def edit_task(self):
        task_dialog = TaskDialog(
            self,
            "Edit Task",
            "Enter the new task description:",
            "Save edit",
            self.content,
        )
        task_dialog.update()
        self.wait_window(task_dialog)
        if task_dialog.task_title:
            database.modify_task(task_id=self.id, new_title=task_dialog.task_title)
            self.label.configure(text=task_dialog.task_title)
            self.text = task_dialog.task_title
        if task_dialog.task_content:
            database.modify_task(task_id=self.id, new_content=task_dialog.task_content)
            self.content = task_dialog.task_content

    def edit(self, current_column):
        database.modify_task(
            task_id=self.id,
            new_title=self.text,
            new_content=self.content,
            new_column_name=current_column,
        )

    def delete(self):
        database.delete_task(self.text)
        fade_out(self, self.winfo_id())
        self.destroy()

    def get_position(self):
        pointer_x = self.winfo_pointerx()
        pointer_y = self.winfo_pointery()

        # Get the app window's top-left corner position relative to the screen
        app_x = self.app.winfo_rootx()
        app_y = self.app.winfo_rooty()

        # Calculate the position relative to the app window
        relative_x = pointer_x - app_x
        relative_y = pointer_y - app_y
        return relative_x, relative_y

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        self.initial_master = self.master
        self.lift()

        # Create a dummy task to follow the mouse during dragging

        self.dummy = ctk.CTkFrame(
            self.app,
            width=self.winfo_width(),
            height=self.winfo_height(),
            border_width=2,
        )
        self.dummy.grid_columnconfigure(2, weight=1)
        self.dummy.grid_rowconfigure(2, weight=1)
        self.label = ctk.CTkLabel(
            self.dummy,
            text=self.text,
            wraplength=150,
            anchor="e",
            justify="left",
            font=FONT,
        )
        self.label.grid(row=0, column=0, rowspan=5, padx=16, pady=8, sticky="nsw")
        self.edit_button = ctk.CTkButton(self.dummy, text="", image=EDIT_IMG, width=48)
        self.edit_button.grid(
            row=1, column=1, padx=8, pady=(8, 4), sticky="e", columnspan=2
        )
        self.delete_button = ctk.CTkButton(
            self.dummy, text="", image=DELETE_IMG, width=48
        )
        self.delete_button.grid(
            row=2, column=1, padx=8, pady=(4, 8), sticky="e", columnspan=2
        )
        pywinstyles.set_opacity(self.dummy.winfo_id(), value=0.5)
        self.dummy.place(
            x=self.get_position()[0] - self.drag_start_x,
            y=self.get_position()[1] - self.drag_start_y,
        )

    def get_current_column(self):
        x = self.app.winfo_pointerx() - self.app.winfo_rootx()
        y = self.app.winfo_pointery() - self.app.winfo_rooty()
        for column in self.app.columns:
            if column.winfo_x() <= x <= column.winfo_x() + column.winfo_width():
                if self.dummy_task is None:
                    self.dummy_task = DraggableTask(
                        master=column.task_frame,
                        text=self.text,
                        content=self.content,
                        id=self.id,
                        app=self,
                    )  # Create a new task
                    self.dummy_task.pack(
                        fill="x", padx=5, pady=2
                    )  # Pack the task into the new column
                    pywinstyles.set_opacity(self.dummy_task.winfo_id(), value=0.7)
                elif self.dummy_task is not None and self.last_column != column.title:
                    self.dummy_task.destroy()
                    self.dummy_task = None
                elif self.dummy_task is not None and self.last_column == column.title:
                    pass
                else:
                    self.dummy_task.destroy()
                    self.dummy_task = None
                self.last_column = column.title
                self.update()

    def on_drag(self, event):
        self.dummy.place(
            x=self.get_position()[0] - self.drag_start_x,
            y=self.get_position()[1] - self.drag_start_y,
        )  # Move the dummy to follow the cursor
        self.get_current_column()

    def stop_drag(self, event):
        # After stopping the drag, handle the drop and remove the dummy
        try:
            self.dummy.destroy()
            self.dummy = None
            self.dummy_task.destroy()
            self.dummy_task = None
            self.app.handle_drop(self, event)
        except Exception as e:
            print(f"Error: {e}")
