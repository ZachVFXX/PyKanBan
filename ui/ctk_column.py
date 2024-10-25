import customtkinter as ctk

import database
from animation import fade_in
from setting import *
from ui.ctk_dialog import TaskDialog
from ui.ctk_task import DraggableTask


class KanbanColumn(ctk.CTkFrame):
    def __init__(self, master, title, app):
        super().__init__(master, corner_radius=10)
        self.app = app
        self.title = title

        FONT = ctk.CTkFont(family="Poppins", size=16)
        BOLD_FONT = ctk.CTkFont(family="Poppins", size=16, weight="bold")

        self.title_label = ctk.CTkLabel(self, text=title, font=BOLD_FONT)
        self.title_label.pack(pady=10)

        self.task_frame = ctk.CTkScrollableFrame(self)
        self.task_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.add_task_button = ctk.CTkButton(
            self, text="Add Task", image=ADD_IMG, command=self.add_task, font=FONT
        )
        self.add_task_button.pack(pady=10)

    def add_task(self):
        task_dialog = TaskDialog(
            self, "Add Task", "Enter task description:", "Add", content=" "
        )
        task_dialog.update()
        self.wait_window(task_dialog)
        if task_dialog.task_title:
            id = database.add_task(
                title=task_dialog.task_title,
                content=task_dialog.task_content,
                column_name=self.title,
                kanban_id=self.app.kanban_id,
            )
            if id:
                task = DraggableTask(
                    master=self.task_frame,
                    text=task_dialog.task_title,
                    content=task_dialog.task_content,
                    id=id,
                    app=self.app,
                )
                task.pack(fill="x", padx=5, pady=2)
                fade_in(self, task.winfo_id())
