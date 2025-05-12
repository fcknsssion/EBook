import tkinter as tk
from ui_components import create_menu_buttons, show_welcome
from material_manager import MaterialManager
from utils import resource_path
from file_reader import image_cache


class EBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Электронный учебник по кибербезопасности")
        self.root.geometry("1200x800")
        self.bg_color = "#1E1E2F"
        self.text_color = "#E0E0E0"
        self.menu_bg = "#2D2D44"
        self.button_bg = "#3D3D5C"
        self.accent_color = "#00A3E0"
        self.font_family = "Arial"
        self.font_size = 12
        self.root.configure(bg=self.bg_color)

        self.image_cache = image_cache
        self.material_manager = MaterialManager(resource_path("Materials"))
        self.material_manager.load_materials()

        self.menu_frame = tk.Frame(root, bg="#2D2D44", height=50, bd=1, relief=tk.RAISED)
        self.menu_frame.pack(fill=tk.X)
        create_menu_buttons(self)

        self.content_frame = tk.Frame(root, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        show_welcome(self)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.last_category = None

    def on_closing(self):
        self.material_manager.save_materials()
        self.image_cache.clear()
        self.root.destroy()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()