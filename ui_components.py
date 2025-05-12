import tkinter as tk
from tkinter import ttk, messagebox
import os
from material_manager import add_material, view_document
from test_manager import show_tests
from constants import welcome_text


def create_menu_buttons(app):
    menu_items = [
        ("Добавить материал", lambda: add_material(app)),
        ("Просмотреть материалы", lambda: view_materials(app)),
        ("Тесты", lambda: show_tests(app)),
        ("Авторы", lambda: show_authors(app)),
        ("Настройки", lambda: show_settings(app)),
        ("Выйти", app.on_closing)
    ]
    for text, command in menu_items:
        btn = tk.Button(app.menu_frame, text=text, command=command,
                        bg="#2D2D44", fg=app.text_color, relief=tk.FLAT,
                        font=(app.font_family, 10), activebackground=app.accent_color,
                        activeforeground="white")
        btn.pack(side=tk.LEFT, padx=10, pady=10)


def show_welcome(app):
    app.clear_content()
    header_frame = tk.Frame(app.content_frame, bg="#2D2D44", height=40, bd=1, relief=tk.RAISED)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_label = tk.Label(header_frame, text="Электронный учебник по кибербезопасности",
                            font=(app.font_family, 14, 'bold'),
                            fg=app.text_color, bg="#2D2D44")
    header_label.pack(side=tk.LEFT, pady=5, padx=10)

    main_frame = tk.Frame(app.content_frame, bg=app.bg_color)
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_frame = tk.Frame(main_frame, bg=app.bg_color)
    header_frame.pack(pady=20)
    tk.Label(header_frame,
             text="Электронный учебник по кибербезопасности",
             font=(app.font_family, 20, 'bold'),
             fg=app.accent_color,
             bg=app.bg_color).pack()
    tk.Label(header_frame,
             text="для студентов всех специальностей",
             font=(app.font_family, 14),
             fg=app.text_color,
             bg=app.bg_color).pack(pady=5)

    text_frame = tk.Frame(main_frame, bg=app.bg_color)
    text_frame.pack(fill=tk.BOTH, expand=True)
    canvas = tk.Canvas(text_frame, bg=app.bg_color, highlightthickness=0)
    scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=app.bg_color)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    for text, is_important in welcome_text:
        label = tk.Label(scrollable_frame, text=text,
                         font=(app.font_family, app.font_size, 'bold' if is_important else 'normal'),
                         fg=app.accent_color if is_important else app.text_color, bg=app.bg_color,
                         wraplength=900, justify="left")
        label.pack(pady=5, padx=20, anchor="w")

    button_frame = tk.Frame(main_frame, bg=app.bg_color)
    button_frame.pack(pady=20)
    tk.Button(button_frame, text="Начать изучение",
              command=lambda: view_materials(app),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 12, 'bold'),
              relief=tk.FLAT, bd=0, activebackground="#008BB5").pack(pady=10, ipadx=20, ipady=5)


def view_materials(app):
    app.clear_content()
    header_frame = tk.Frame(app.content_frame, bg="#2D2D44", height=40, bd=1, relief=tk.RAISED)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_label = tk.Label(header_frame, text="Материалы",
                            font=(app.font_family, 14, 'bold'),
                            fg=app.text_color, bg="#2D2D44")
    header_label.pack(side=tk.LEFT, pady=5, padx=10)
    tk.Button(header_frame, text="Назад",
              command=lambda: show_welcome(app),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 10, 'bold'),
              relief=tk.FLAT, bd=0).pack(side=tk.RIGHT, padx=10, pady=5)

    main_frame = tk.Frame(app.content_frame, bg=app.bg_color)
    main_frame.pack(fill=tk.BOTH, expand=True)

    left_panel = tk.Frame(main_frame, bg="#2D2D44", width=300, bd=1, relief=tk.SUNKEN)
    left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
    right_panel = tk.Frame(main_frame, bg=app.bg_color)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    app.material_list_frame = tk.Frame(left_panel, bg="#2D2D44")
    app.material_list_frame.pack(fill=tk.BOTH, expand=True)
    populate_material_list(app, left_panel, right_panel)

    tk.Label(right_panel, text="Выберите материал для просмотра",
             font=(app.font_family, 16), fg=app.text_color, bg=app.bg_color).pack(pady=20)


def populate_material_list(app, left_panel, right_panel):
    for widget in app.material_list_frame.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(app.material_list_frame, bg="#2D2D44", highlightthickness=0)
    scrollbar = tk.Scrollbar(app.material_list_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#2D2D44")
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    main_categories = ["Лекции", "Практика", "Лабораторные работы", "СРС", "СРСП", "Тесты", "Глоссарий",
                       "Список литературы"]
    for category in main_categories:
        if not app.material_manager.materials[category]:
            continue
        cat_label = tk.Label(scrollable_frame, text=category,
                             font=(app.font_family, 12, 'bold'), fg=app.accent_color, bg="#2D2D44")
        cat_label.pack(anchor="w", padx=10, pady=5)
        for material_path in app.material_manager.materials[category]:
            file_name = os.path.basename(material_path)
            btn = tk.Button(scrollable_frame, text=file_name.split(".")[0],
                            command=lambda path=material_path: view_document(app, path, right_panel),
                            bg="#3D3D5C", fg=app.text_color, relief=tk.FLAT,
                            font=(app.font_family, 10), anchor="w", justify="left",
                            wraplength=250)
            btn.pack(fill=tk.X, padx=15, pady=2)


def show_authors(app):
    app.clear_content()
    header_frame = tk.Frame(app.content_frame, bg="#2D2D44", height=40, bd=1, relief=tk.RAISED)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_label = tk.Label(header_frame, text="Авторы",
                            font=(app.font_family, 14, 'bold'),
                            fg=app.text_color, bg="#2D2D44")
    header_label.pack(side=tk.LEFT, pady=5, padx=10)
    tk.Button(header_frame, text="Назад",
              command=lambda: show_welcome(app),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 10, 'bold'),
              relief=tk.FLAT, bd=0).pack(side=tk.RIGHT, padx=10, pady=5)

    main_frame = tk.Frame(app.content_frame, bg=app.bg_color)
    main_frame.pack(fill=tk.BOTH, expand=True)
    tk.Label(main_frame, text="Авторы",
             font=(app.font_family, 18, 'bold'),
             fg=app.text_color, bg=app.bg_color).pack(pady=10)
    authors = [
        "Байдрахманова Г.А. - PhD доктор, ст. преподаватель",
        "Жайлыбаева А.О. - магистр, преподаватель",
        "Абай И.А. - Студент 3 курса, специальность: 'ВТиПО'"
    ]
    for author in authors:
        tk.Label(main_frame, text=author,
                 font=(app.font_family, app.font_size),
                 bg="#2D2D44", fg=app.text_color,
                 bd=1, relief=tk.RIDGE, width=80).pack(pady=5)


# Определение тем
THEMES = {
    "Тёмная": {
        "bg_color": "#1E1E2F",
        "text_color": "#FFFFFF",
        "accent_color": "#00A1D6",
        "menu_bg": "#2D2D44",
        "button_bg": "#3D3D5C"
    },
    "Светлая": {
        "bg_color": "#F5F5F5",
        "text_color": "#000000",
        "accent_color": "#0078D4",
        "menu_bg": "#E0E0E0",
        "button_bg": "#D0D0D0"
    },
    "Тёмно-зелёная": {
        "bg_color": "#1A2B2A",
        "text_color": "#D4D4D4",
        "accent_color": "#2ECC71",
        "menu_bg": "#263D3C",
        "button_bg": "#344C4B"
    }
}

def update_theme(app, theme_name):
    """Обновляет тему приложения."""
    try:
        theme = THEMES.get(theme_name, THEMES["Тёмная"])  # По умолчанию тёмная тема
        app.bg_color = theme["bg_color"]
        app.text_color = theme["text_color"]
        app.accent_color = theme["accent_color"]
        app.menu_bg = theme["menu_bg"]
        app.button_bg = theme["button_bg"]

        # Обновление всех виджетов (перерисовка текущего экрана)
        app.root.configure(bg=app.bg_color)
        app.menu_frame.configure(bg=app.menu_bg)
        app.content_frame.configure(bg=app.bg_color)

        # Перерисовка текущего экрана
        if app.current_screen == "welcome":
            show_welcome(app)
        elif app.current_screen == "materials":
            view_materials(app)
        elif app.current_screen == "authors":
            show_authors(app)
        elif app.current_screen == "settings":
            show_settings(app)
        elif app.current_screen == "references":
            show_references(app)

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось изменить тему: {e}")

def show_settings(app):
    app.clear_content()
    app.current_screen = "settings"  # Для отслеживания текущего экрана

    header_frame = tk.Frame(app.content_frame, bg=app.menu_bg, height=40, bd=1, relief=tk.RAISED)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_label = tk.Label(header_frame, text="Настройки",
                            font=(app.font_family, 14, 'bold'),
                            fg=app.text_color, bg=app.menu_bg)
    header_label.pack(side=tk.LEFT, pady=5, padx=10)
    tk.Button(header_frame, text="Назад",
              command=lambda: show_welcome(app),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 10, 'bold'),
              relief=tk.FLAT, bd=0).pack(side=tk.RIGHT, padx=10, pady=5)

    main_frame = tk.Frame(app.content_frame, bg=app.bg_color)
    main_frame.pack(fill=tk.BOTH, expand=True)
    tk.Label(main_frame, text="Настройки",
             font=(app.font_family, 18, 'bold'),
             fg=app.text_color, bg=app.bg_color).pack(pady=10)

    # Настройка шрифта
    font_frame = tk.Frame(main_frame, bg=app.bg_color)
    font_frame.pack(pady=10)
    tk.Label(font_frame, text="Шрифт",
             bg=app.bg_color, fg=app.text_color).pack(side=tk.LEFT, padx=5)
    font_var = tk.StringVar(value=app.font_family)
    font_entry = ttk.Combobox(font_frame, textvariable=font_var,
                              values=["Arial", "Times New Roman", "Calibri"])
    font_entry.pack(side=tk.LEFT)
    tk.Button(font_frame, text="Изменить шрифт",
              command=lambda: update_font(app, font_var.get()),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 10, 'bold'),
              relief=tk.FLAT, bd=0).pack(side=tk.LEFT, padx=5)

    # Настройка темы
    theme_frame = tk.Frame(main_frame, bg=app.bg_color)
    theme_frame.pack(pady=10)
    tk.Label(theme_frame, text="Тема",
             bg=app.bg_color, fg=app.text_color).pack(side=tk.LEFT, padx=5)
    theme_var = tk.StringVar(value="Тёмная")  # Тема по умолчанию
    theme_entry = ttk.Combobox(theme_frame, textvariable=theme_var,
                               values=list(THEMES.keys()))
    theme_entry.pack(side=tk.LEFT)
    tk.Button(theme_frame, text="Изменить тему",
              command=lambda: update_theme(app, theme_var.get()),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 10, 'bold'),
              relief=tk.FLAT, bd=0).pack(side=tk.LEFT, padx=5)


def update_font(app, font):
    try:
        app.font_family = font
        app.root.option_add("*Font", (font, app.font_size))
        show_settings(app)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось изменить шрифт: {e}")


def show_references(app):
    app.clear_content()
    header_frame = tk.Frame(app.content_frame, bg="#2D2D44", height=40, bd=1, relief=tk.RAISED)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_label = tk.Label(header_frame, text="Список литературы",
                            font=(app.font_family, 14, 'bold'),
                            fg=app.text_color, bg="#2D2D44")
    header_label.pack(side=tk.LEFT, pady=5, padx=10)
    tk.Button(header_frame, text="Назад",
              command=lambda: view_materials(app),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 10, 'bold'),
              relief=tk.FLAT, bd=0).pack(side=tk.RIGHT, padx=10, pady=5)

    main_frame = tk.Frame(app.content_frame, bg=app.bg_color)
    main_frame.pack(fill=tk.BOTH, expand=True)
    tk.Label(main_frame, text="Список литературы",
             font=(app.font_family, 18, 'bold'),
             fg=app.text_color, bg=app.bg_color).pack(pady=10)

    text_frame = tk.Frame(main_frame, bg=app.bg_color)
    text_frame.pack(fill=tk.BOTH, expand=True)
    canvas = tk.Canvas(text_frame, bg=app.bg_color, highlightthickness=0)
    scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=app.bg_color)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    references = [
        "НЕОБХОДИМЫЕ РЕСУРСЫ",
        "Основная литература",
        "1. 'Кибербезопасность. Руководство для начинающих'. Автор: Юрий Диогенес, Эрдал Озкайя",
        "2. 'Основы кибербезопасности'. Автор: Майкл Гудинг",
        "Электронные ресурсы:",
        "1. https://www.kaspersky.ru/resource-center/definitions/what-is-cybersecurity",
    ]
    for ref in references:
        if ref in ["НЕОБХОДИМЫЕ РЕСУРСЫ", "Основная литература", "Электронные ресурсы:"]:
            label = tk.Label(scrollable_frame, text=ref,
                             font=(app.font_family, app.font_size, 'bold'),
                             fg=app.accent_color, bg=app.bg_color,
                             wraplength=900, justify="left")
        else:
            label = tk.Label(scrollable_frame, text=ref,
                             font=(app.font_family, app.font_size),
                             fg=app.text_color, bg=app.bg_color,
                             wraplength=900, justify="left")
        label.pack(pady=2, padx=20, anchor="w")