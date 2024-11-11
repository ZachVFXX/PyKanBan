from src.setting import *


class TaskDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, description: str, button_text: str):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")
        self.task_title = None
        self.task_content = None
        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text=description)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.entry = ctk.CTkEntry(self, width=200)
        self.entry.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.button = ctk.CTkButton(self, text=button_text, command=self.on_add)
        self.button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.entry.bind("<Return>", self.on_add)

        self.update()
        self.entry.focus()

    def on_add(self, event=None):
        self.task_title = self.entry.get()
        self.destroy()
