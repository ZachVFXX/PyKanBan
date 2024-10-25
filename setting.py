import os
import sys

import customtkinter as ctk
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


EDIT_IMG = ctk.CTkImage(Image.open(resource("assets/edit_task.png")), size=(24, 24))
DELETE_IMG = ctk.CTkImage(Image.open(resource("assets/delete_task.png")), size=(24, 24))
ADD_IMG = ctk.CTkImage(Image.open(resource("assets/add_task.png")), size=(24, 24))
MORE_IMG = ctk.CTkImage(Image.open(resource("assets/more_task.png")), size=(24, 24))
