from setting import *


class TaskDialog(ctk.CTkToplevel):
    def __init__(
        self,
        parent,
        title: str,
        description: str,
        button_text: str,
        content: str | None = None,
    ):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x300")
        self.task_title = None
        self.task_content = None
        self.content = content

        self.label = ctk.CTkLabel(self, text=description)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.entry = ctk.CTkEntry(self, width=200)
        self.entry.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        if self.content:
            self.content_box = ctk.CTkTextbox(self, height=100, width=200)
            self.content_box.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
            self.content_box.insert("end", content)

        self.button = ctk.CTkButton(self, text=button_text, command=self.on_add)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.entry.bind("<Return>", self.on_add)

        self.update()
        self.entry.focus()

    def on_add(self, event=None):
        if self.content:
            self.task_content = self.content_box.get("0.0", "end")
        self.task_title = self.entry.get()
        self.destroy()
