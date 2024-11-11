import os
import sys

import customtkinter as ctk
from hPyT import maximize_minimize_button
from PIL import Image


def resource(relative_path: str) -> str:
    """
    Returns the path to the specified resource file.
    If the application is running as a bundle, the path is relative to the bundle.
    Otherwise, the path is relative to the current working directory.

    :argument relative_path: The path to the resource file, relative to the bundle or current working directory.

    :return: The absolute path to the resource file.
    """
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


PIN_IMG = ctk.CTkImage(Image.open(resource("assets/keep.png")))
PIN_OFF_IMG = ctk.CTkImage(Image.open(resource("assets/keep_off.png")))


class PyStickyNote(ctk.CTkToplevel):
    def __init__(
        self,
        master=None,
        title: str = "PyStickyNote",
        content: str = "Hello World",
        geometry: str = "200x200",
        icon: Image = None,
        no_maximize_minimize_button: bool = False,
        font: tuple[str, int] = ("Poppins", 20, "bold"),
        pinned: bool = False,
    ):
        super().__init__()
        self.title(title)
        self.geometry(geometry)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.font = font
        self.pinned = pinned

        if icon is not None:
            self.iconbitmap(icon)
        if not no_maximize_minimize_button:
            maximize_minimize_button.hide(self)
        padx = (5, 0)
        pady = (5, 5)

        self.tool_bar = ctk.CTkFrame(self, height=30)
        self.tool_bar.grid(row=0, column=0, padx=0, pady=0, sticky="new")
        self.pin_button = ctk.CTkButton(
            self.tool_bar,
            text="",
            image=PIN_IMG,
            width=30,
            height=30,
            command=self.toggle_pin,
        )
        self.pin_button.grid(row=0, column=0, padx=padx, pady=pady, sticky="new")

        self.content = ctk.CTkTextbox(self, corner_radius=0, font=self.font)
        self.content.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        self.content.insert("end", content)

        self.update_pinned()

        self.update()
        self.focus()

    def update_pinned(self):
        self.attributes("-topmost", self.pinned)

    def toggle_pin(self):
        if self.pinned:
            self.pin_button.configure(image=PIN_IMG)
            self.pinned = False
        else:
            self.pin_button.configure(image=PIN_OFF_IMG)
            self.pinned = True
        self.update_pinned()
