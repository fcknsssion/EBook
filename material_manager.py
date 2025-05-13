import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from datetime import datetime
import logging
from utils import resource_path, extract_number, normalize_path
from file_reader import try_read_file

# Configure logging
logging.basicConfig(filename='material_manager.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class MaterialManager:
    def __init__(self, base_dir):
        self.materials = {
            "Лекции": [], "Практика": [], "Лабораторные работы": [],
            "СРС": [], "СРСП": [], "Тесты": [], "Глоссарий": [], "Список литературы": []
        }
        self.materials_base_dir = base_dir

    def load_materials(self):
        json_file = resource_path("materials.json")
        supported_extensions = ('.txt', '.pdf', '.docx', '.doc', '.md', '.log')

        for category in self.materials:
            self.materials[category] = []

        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    loaded_materials = json.load(f)
                    for category in self.materials:
                        if category in loaded_materials:
                            unique_paths = set()
                            for path in loaded_materials[category]:
                                abs_path = os.path.abspath(path)
                                if os.path.exists(abs_path):
                                    norm_path = normalize_path(abs_path, self.materials_base_dir)
                                    if norm_path not in unique_paths:
                                        unique_paths.add(norm_path)
                                        self.materials[category].append(abs_path)
                            self.materials[category] = sorted(
                                self.materials[category],
                                key=lambda x: extract_number(os.path.basename(x))
                            )
            except Exception as e:
                logging.error(f"Failed to load materials from JSON: {e}")
                messagebox.showerror("Ошибка", f"Не удалось загрузить материалы из JSON: {e}")

        for category in self.materials:
            category_dir = os.path.join(self.materials_base_dir, category)
            if not os.path.exists(category_dir):
                os.makedirs(category_dir, exist_ok=True)
            try:
                files = sorted(os.listdir(category_dir), key=extract_number)
                for filename in files:
                    file_path = os.path.join(category_dir, filename)
                    if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in supported_extensions:
                        norm_path = normalize_path(file_path, self.materials_base_dir)
                        if norm_path not in {normalize_path(p, self.materials_base_dir) for p in
                                             self.materials[category]}:
                            self.materials[category].append(file_path)
                self.materials[category] = sorted(
                    self.materials[category],
                    key=lambda x: extract_number(os.path.basename(x))
                )
            except Exception as e:
                logging.error(f"Failed to load materials from {category_dir}: {e}")
                messagebox.showerror("Ошибка", f"Не удалось загрузить материалы из {category_dir}: {e}")

        self.save_materials()

    def save_materials(self):
        json_file = resource_path("materials.json")
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.materials, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"Failed to save materials: {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить материалы: {e}")

    def add_literature_list(self):
        category = "Список литературы"
        category_dir = os.path.join(self.materials_base_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        # Literature list content in Markdown
        literature_content = """# НЕОБХОДИМЫЕ РЕСУРСЫ

## Основная литература
- "Кибербезопасность. Руководство для начинающих". Автор: Юрий Диогенес, Эрдаль Озкайя
- "Kali Linux: Тестирование на проникновение". Автор: Уильям Поллак
- "Информационная безопасность. Защита и нападение". Автор: Андрей Бирюков
- "Компьютерные сети. Принципы, технологии, протоколы". Автор: Уильям Столлингс
- "Искусственный интеллект в кибербезопасности". Автор: Абхишек Дубей
- "Программная безопасность: Технические подходы к защите". Автор: Гэри Макгроу
- "Практическая криптография". Автор: Брюс Шнайер
- "Хакинг: Искусство эксплойта". Автор: Джон Эриксон
- "Мобильная безопасность: руководство разработчика". Автор: Доминик Шейн
- "Безопасность веб-приложений". Автор: Иван Ристич
- "Обнаружение атак в реальном времени". Автор: Кристофер Сандерс
- "Linux для хакеров". Автор: Джошуа Д. Картрайт
- "Реверс-инжиниринг программного обеспечения". Автор: Эльдар Шейнов
- "Этика хакера". Автор: Кевин Митник
- "Современные угрозы и защита от них". Автор: Маркус Ранум

## Электронные ресурсы
- **Coursera**: Курсы по кибербезопасности от ведущих университетов (Stanford, IBM): [coursera.org](https://coursera.org)
- **edX**: Курсы по кибербезопасности, включая основы разработки безопасного ПО: [edx.org](https://edx.org)
- **Udemy**: Практические курсы по этическому хакингу, защите данных и разработке защищенного ПО: [udemy.com](https://udemy.com)
- **Cisco Networking Academy**: Программы обучения сетевой безопасности и разработке защитных решений: [cisco.com](https://www.cisco.com)
- **Springer Link**: Научные статьи и книги по кибербезопасности: [springer.com](https://link.springer.com)
"""

        # Create temporary file
        temp_file = resource_path("temp_literature_list.md")
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(literature_content)

            # Generate unique filename
            base_name = "literature_list"
            ext = ".md"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_file_name = f"{base_name}_{timestamp}{ext}"
            new_path = os.path.join(category_dir, new_file_name)

            # Copy file
            shutil.copy2(temp_file, new_path)
            norm_path = normalize_path(new_path, self.materials_base_dir)

            # Add to materials if not present
            if norm_path not in {normalize_path(p, self.materials_base_dir) for p in self.materials[category]}:
                self.materials[category].append(new_path)
                self.materials[category] = sorted(
                    self.materials[category],
                    key=lambda x: extract_number(os.path.basename(x))
                )
                self.save_materials()

            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

            return True, f"Литература успешно добавлена в '{category}'!"
        except Exception as e:
            logging.error(f"Failed to add literature list: {e}")
            return False, f"Не удалось добавить литературу: {e}"

def add_material(app):
    from ui_components import view_materials
    app.clear_content()
    header_frame = tk.Frame(app.content_frame, bg="#2D2D44", height=40, bd=1, relief=tk.RAISED)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_label = tk.Label(header_frame, text="Добавить материал",
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
    tk.Label(main_frame, text="Добавить материал",
             font=(app.font_family, 18, 'bold'),
             fg=app.text_color, bg=app.bg_color).pack(pady=10)
    tk.Label(main_frame, text="Выберите категорию:",
             font=(app.font_family, app.font_size),
             fg=app.text_color, bg=app.bg_color).pack(pady=5)

    category_var = tk.StringVar()
    category_menu = ttk.Combobox(main_frame, textvariable=category_var,
                                 values=["Лекции", "Практика", "Лабораторные работы",
                                         "СРС", "СРСП", "Тесты", "Глоссарий", "Список литературы"])
    category_menu.pack(pady=5)
    tk.Label(main_frame, text="Выберите файл:",
             font=(app.font_family, app.font_size),
             fg=app.text_color, bg=app.bg_color).pack(pady=5)

    file_label = tk.Label(main_frame, text="Файл не выбран",
                          font=(app.font_family, app.font_size),
                          fg=app.text_color, bg=app.bg_color)
    file_label.pack(pady=5)
    file_path = [None]
    tk.Button(main_frame, text="Обзор",
              command=lambda: select_file(file_label, file_path),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 10, 'bold'),
              relief=tk.FLAT, bd=0).pack(pady=5)
    tk.Button(main_frame, text="Сохранить",
              command=lambda: save_material(app, category_var.get(), file_path[0]),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 12, 'bold'),
              relief=tk.FLAT, bd=0).pack(pady=10, ipadx=20, ipady=5)

def select_file(file_label, file_path):
    selected_file = filedialog.askopenfilename(
        filetypes=[("All supported files", "*.txt *.pdf *.docx *.doc *.md *.log"),
                   ("Text files", "*.txt *.md *.log"),
                   ("PDF files", "*.pdf"),
                   ("Word files", "*.docx *.doc"),
                   ("All files", "*.*")])
    if selected_file:
        file_path[0] = selected_file
        file_label.config(text=os.path.basename(selected_file))

def save_material(app, category, file_path):
    from ui_components import view_materials
    if not category or category not in app.material_manager.materials:
        messagebox.showerror("Ошибка", "Выберите действительную категорию!")
        return
    if not file_path or not os.path.exists(file_path):
        messagebox.showerror("Ошибка", "Выберите существующий файл!")
        return

    category_dir = os.path.join(app.material_manager.materials_base_dir, category)
    os.makedirs(category_dir, exist_ok=True)

    # Generate a unique file name
    base_name, ext = os.path.splitext(os.path.basename(file_path))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_file_name = f"{base_name}_{timestamp}{ext}"
    new_path = os.path.join(category_dir, new_file_name)

    try:
        shutil.copy2(file_path, new_path)
        norm_path = normalize_path(new_path, app.material_manager.materials_base_dir)
        if norm_path not in {normalize_path(p, app.material_manager.materials_base_dir) for p in
                             app.material_manager.materials[category]}:
            app.material_manager.materials[category].append(new_path)
            app.material_manager.materials[category] = sorted(
                app.material_manager.materials[category],
                key=lambda x: extract_number(os.path.basename(x))
            )
            app.material_manager.save_materials()
        messagebox.showinfo("Успех", f"Материал '{new_file_name}' успешно добавлен в категорию '{category}'!")
        view_materials(app)
    except Exception as e:
        logging.error(f"Failed to save material {file_path}: {e}")
        messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

def view_document(app, filepath, right_panel, refresh=False):
    from ui_components import view_materials
    if not refresh:
        app.current_document_path = filepath
        app.current_document_panel = right_panel

    for widget in right_panel.winfo_children():
        widget.destroy()

    def display_content(content_with_styles, images, error):
        if error or (content_with_styles is None and not images):
            tk.Label(right_panel, text=error if error else "Не удалось извлечь содержимое файла.",
                     font=(app.font_family, app.font_size, 'italic'),
                     fg="red", bg=app.bg_color).pack(pady=20)
            return

        control_frame = tk.Frame(right_panel, bg=app.bg_color)
        control_frame.pack(fill=tk.X, pady=5)
        # Remove .pdf, .docx, .doc extensions from header
        base_name, ext = os.path.splitext(os.path.basename(filepath))
        display_name = base_name if ext.lower() in ['.pdf', '.docx', '.doc'] else os.path.basename(filepath)
        tk.Label(control_frame, text=display_name,
                 font=(app.font_family, 16, 'bold'), fg=app.text_color, bg=app.bg_color).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="Назад",
                  command=lambda: view_materials(app),
                  bg=app.accent_color, fg="white",
                  font=(app.font_family, 10, 'bold'),
                  relief=tk.FLAT, bd=0).pack(side=tk.RIGHT, padx=10, pady=5)

        content_frame = tk.Frame(right_panel, bg=app.bg_color, bd=2, relief=tk.SUNKEN)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        app.current_document_frame = content_frame

        canvas = tk.Canvas(content_frame, bg=app.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=app.bg_color)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        app.current_document_canvas = canvas

        def on_mouse_wheel(event):
            if canvas.winfo_exists():
                canvas.yview_scroll(-1 * (event.delta // 120), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)

        app.image_references = []
        if not content_with_styles and not images:
            tk.Label(scrollable_frame, text="Файл пуст или не содержит поддерживаемого содержимого.",
                     font=(app.font_family, app.font_size, 'italic'),
                     fg="gray", bg=app.bg_color).pack(pady=20)
        else:
            for item, is_list_item, is_title, is_italic, font_size, is_bold, alignment in (content_with_styles or []):
                if isinstance(item, list):
                    table_frame = tk.Frame(scrollable_frame, bg=app.bg_color)
                    table_frame.pack(fill=tk.X, padx=15, pady=10)
                    tree = ttk.Treeview(table_frame, show="headings", height=len(item))
                    columns = list(range(len(item[0])))
                    tree["columns"] = columns
                    for col in columns:
                        tree.heading(col, text=f"Колонка {col + 1}")
                        tree.column(col, width=150, anchor="w")
                    for row in item:
                        tree.insert("", tk.END, values=row)
                    tree.pack(fill=tk.X)
                elif item:
                    font_weight = "bold" if is_bold or is_title else "normal"
                    font_style = "italic" if is_italic else font_weight
                    font_size = int(font_size) if font_size else (app.font_size + 4 if is_title else app.font_size)
                    font = (app.font_family, font_size, font_style)
                    color = app.accent_color if is_bold else app.text_color
                    justify = "left" if alignment == "justify" else alignment
                    anchor_map = {"left": "w", "center": "center", "right": "e", "justify": "w"}
                    anchor = anchor_map.get(alignment, "w")
                    pady = 8 if is_title else 4
                    if is_list_item:
                        prefix = "• " if item.startswith("- ") else f"{item[:item.find('. ') + 1]} "
                        text = item.lstrip("- ").lstrip("0123456789. ")
                        lbl = tk.Label(scrollable_frame, text=prefix + text, font=font, fg=color, bg=app.bg_color,
                                       wraplength=850, justify=justify, anchor=anchor)
                    else:
                        lbl = tk.Label(scrollable_frame, text=item, font=font, fg=color, bg=app.bg_color,
                                       wraplength=850, justify=justify, anchor=anchor)
                    lbl.pack(fill=tk.X, padx=15, pady=pady, anchor=anchor)

            for image_path in images:
                try:
                    cache_key = image_path
                    if cache_key not in app.image_cache:
                        img = Image.open(image_path)
                        max_width = 850
                        max_height = 600
                        if img.width > max_width or img.height > max_height:
                            ratio = min(max_width / img.width, max_height / img.height)
                            new_size = (int(img.width * ratio), int(img.height * ratio))
                            img = img.resize(new_size, Image.Resampling.LANCZOS, reducing_gap=3.0)
                        app.image_cache[cache_key] = img
                    else:
                        img = app.image_cache[cache_key]
                    photo = ImageTk.PhotoImage(img)
                    img_frame = tk.Frame(scrollable_frame, bg=app.bg_color)
                    img_frame.pack(fill=tk.X, pady=10)
                    lbl = tk.Label(img_frame, image=photo, bg=app.bg_color, cursor="hand2")
                    lbl.image = photo
                    lbl.pack(anchor="center")
                    caption = tk.Label(img_frame, text=f"Изображение: {os.path.basename(image_path)}",
                                       font=(app.font_family, app.font_size - 2, 'italic'),
                                       fg=app.text_color, bg=app.bg_color)
                    caption.pack(anchor="center")
                    lbl.bind("<Button-1>", lambda e, path=image_path: show_full_image(app, path))
                    app.image_references.append(photo)
                except Exception as e:
                    tk.Label(scrollable_frame, text=f"[Ошибка загрузки изображения: {os.path.basename(image_path)}]",
                             font=(app.font_family, app.font_size, 'italic'),
                             fg="red", bg=app.bg_color).pack(pady=8, anchor="center")

        def cleanup_temp_images():
            temp_dir = resource_path("temp_images")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            canvas.unbind_all("<MouseWheel>")

        right_panel.bind("<Destroy>", lambda e: cleanup_temp_images())

    if not refresh:
        async_read_file(app, filepath, display_content)
    else:
        content, images, error = try_read_file(filepath)
        display_content(content, images, error)

def show_full_image(app, image_path):
    try:
        img = Image.open(image_path)
        max_width = 1200
        max_height = 800
        if img.width > max_width or img.height > max_height:
            ratio = min(max_width / img.width, max_height / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        top = tk.Toplevel(app.root)
        top.title(os.path.basename(image_path))
        top.geometry(f"{img.width}x{img.height}")
        tk.Label(top, image=photo).pack()
        top.image = photo
    except Exception as e:
        logging.error(f"Failed to open image {image_path}: {e}")
        messagebox.showerror("Ошибка", f"Не удалось открыть изображение: {e}")

def async_read_file(app, filepath, callback):
    def read_file():
        content, images, error = try_read_file(filepath)
        app.root.after(0, lambda: callback(content, images, error))

    import threading
    threading.Thread(target=read_file, daemon=True).start()