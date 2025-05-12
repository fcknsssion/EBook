import os
import tkinter as tk
from tkinter import ttk, messagebox
import re
from file_reader import try_read_file
from utils import normalize_path, extract_number


def show_tests(app):
    from ui_components import view_materials
    app.clear_content()
    header_frame = tk.Frame(app.content_frame, bg="#2D2D44", height=40, bd=1, relief=tk.RAISED)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_label = tk.Label(header_frame, text="Тесты",
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
    tk.Label(main_frame, text="Тесты",
             font=(app.font_family, 18, 'bold'),
             fg=app.text_color, bg=app.bg_color).pack(pady=10)

    if not app.material_manager.materials["Тесты"]:
        tk.Label(main_frame, text="Тесты отсутствуют",
                 font=(app.font_family, app.font_size),
                 fg=app.text_color, bg=app.bg_color).pack(pady=10)
    else:
        tk.Label(main_frame, text="Список тестов:",
                 font=(app.font_family, app.font_size),
                 fg=app.text_color, bg=app.bg_color).pack(pady=5)

        # Создаем прокручиваемый список
        test_list_frame = tk.Frame(main_frame, bg="#2D2D44")
        test_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        canvas = tk.Canvas(test_list_frame, bg="#2D2D44", highlightthickness=0)
        scrollbar = tk.Scrollbar(test_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2D2D44")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def delete_test(test_path, test_name):
            # Подтверждение удаления
            if not messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить тест '{test_name}'?"):
                return
            try:
                # Удаляем файл теста
                if os.path.exists(test_path):
                    os.remove(test_path)
                # Удаляем тест из списка
                norm_path = normalize_path(test_path, app.material_manager.materials_base_dir)
                if norm_path in {normalize_path(p, app.material_manager.materials_base_dir) for p in
                                 app.material_manager.materials["Тесты"]}:
                    app.material_manager.materials["Тесты"].remove(test_path)
                    app.material_manager.save_materials()
                messagebox.showinfo("Успех", f"Тест '{test_name}' успешно удален!")
                show_tests(app)  # Обновляем интерфейс
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить тест: {e}")

        # Заполняем список тестов
        for test_path in app.material_manager.materials["Тесты"]:
            test_name = os.path.basename(test_path)
            test_frame = tk.Frame(scrollable_frame, bg="#2D2D44")
            test_frame.pack(fill=tk.X, padx=15, pady=2)

            # Кнопка для выбора теста
            btn = tk.Button(test_frame, text=test_name.split(".")[0],
                            command=lambda path=test_path, name=test_name: start_test(app, name),
                            bg="#3D3D5C", fg=app.text_color, relief=tk.FLAT,
                            font=(app.font_family, 10), anchor="w", justify="left",
                            wraplength=400)
            btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Кнопка для удаления теста
            delete_btn = tk.Button(test_frame, text="Удалить",
                                   command=lambda path=test_path, name=test_name: delete_test(path, name),
                                   bg="#FF5555", fg="white", relief=tk.FLAT,
                                   font=(app.font_family, 10))
            delete_btn.pack(side=tk.RIGHT, padx=5)

    tk.Button(main_frame, text="Создать тест",
              command=lambda: create_test(app),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 12, 'bold'),
              relief=tk.FLAT, bd=0).pack(pady=10, ipadx=20, ipady=5)


def create_test(app):
    from ui_components import view_materials  # Moved import here to avoid circular dependency
    app.clear_content()
    header_frame = tk.Frame(app.content_frame, bg="#2D2D44", height=40, bd=1, relief=tk.RAISED)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_label = tk.Label(header_frame, text="Создать тест",
                            font=(app.font_family, 14, 'bold'),
                            fg=app.text_color, bg="#2D2D44")
    header_label.pack(side=tk.LEFT, pady=5, padx=10)
    tk.Button(header_frame, text="Назад",
              command=lambda: show_tests(app),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 10, 'bold'),
              relief=tk.FLAT, bd=0).pack(side=tk.RIGHT, padx=10, pady=5)

    main_frame = tk.Frame(app.content_frame, bg=app.bg_color)
    main_frame.pack(fill=tk.BOTH, expand=True)
    tk.Label(main_frame, text="Создать новый тест",
             font=(app.font_family, 18, 'bold'),
             fg=app.text_color, bg=app.bg_color).pack(pady=10)

    # Test name input
    tk.Label(main_frame, text="Название теста:",
             font=(app.font_family, app.font_size),
             fg=app.text_color, bg=app.bg_color).pack(pady=5)
    test_name_var = tk.StringVar()
    test_name_entry = tk.Entry(main_frame, textvariable=test_name_var, width=50,
                               font=(app.font_family, app.font_size))
    test_name_entry.pack(pady=5)

    # Questions input area
    questions = []
    question_frame = tk.Frame(main_frame, bg=app.bg_color)
    question_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    canvas = tk.Canvas(question_frame, bg=app.bg_color, highlightthickness=0)
    scrollbar = tk.Scrollbar(question_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=app.bg_color)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Функция для обработки прокрутки колесика мыши
    def on_mouse_wheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # Привязываем событие колесика мыши к Canvas и его содержимому
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Для Windows
    canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))  # Для Linux (прокрутка вверх)
    canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))  # Для Linux (прокрутка вниз)

    def add_question():
        q_frame = tk.Frame(scrollable_frame, bg=app.bg_color)
        q_frame.pack(fill=tk.X, pady=20, padx=80)
        question = {"question": tk.StringVar(), "options": [tk.StringVar() for _ in range(4)],
                    "correct": tk.StringVar(value="A")}

        tk.Label(q_frame, text=f"Вопрос {len(questions) + 1}:",
                 font=(app.font_family, app.font_size, 'bold'),
                 fg=app.text_color, bg=app.bg_color).pack(anchor="w")
        tk.Entry(q_frame, textvariable=question["question"], width=60,
                 font=(app.font_family, app.font_size)).pack(anchor="w", pady=2, padx=20)

        for i, opt in enumerate(["A", "B", "C", "D"]):
            tk.Label(q_frame, text=f"{opt})",
                     font=(app.font_family, app.font_size),
                     fg=app.text_color, bg=app.bg_color).pack(anchor="w")
            tk.Entry(q_frame, textvariable=question["options"][i], width=60,
                     font=(app.font_family, app.font_size)).pack(anchor="w", pady=2, padx=20)

        tk.Label(q_frame, text="Правильный ответ:",
                 font=(app.font_family, app.font_size),
                 fg=app.text_color, bg=app.bg_color).pack(anchor="w")
        correct_menu = ttk.Combobox(q_frame, textvariable=question["correct"],
                                    values=["A", "B", "C", "D"], width=5)
        correct_menu.pack(anchor="w", pady=2)

        questions.append(question)
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    tk.Button(main_frame, text="Добавить вопрос",
              command=add_question,
              bg=app.accent_color, fg="white",
              font=(app.font_family, 10, 'bold'),
              relief=tk.FLAT, bd=0).pack(pady=5)

    def save_test():
        test_name = test_name_var.get().strip()
        if not test_name:
            messagebox.showerror("Ошибка", "Введите название теста!")
            return
        if not questions:
            messagebox.showerror("Ошибка", "Добавьте хотя бы один вопрос!")
            return

        # Validate questions
        for i, q in enumerate(questions, 1):
            if not q["question"].get().strip():
                messagebox.showerror("Ошибка", f"Вопрос {i} не заполнен!")
                return
            for j, opt in enumerate(q["options"], 1):
                if not opt.get().strip():
                    messagebox.showerror("Ошибка", f"Вариант ответа {chr(65 + j)} для вопроса {i} не заполнен!")
                    return
            if q["correct"].get() not in ["A", "B", "C", "D"]:
                messagebox.showerror("Ошибка", f"Неверный правильный ответ для вопроса {i}!")
                return

        # Generate test content
        test_content = []
        for i, q in enumerate(questions, 1):
            test_content.append(f"Question {i}: {q['question'].get()}")
            for j, opt in enumerate(q["options"]):
                test_content.append(f"{chr(65 + j)}) {opt.get()}")
            test_content.append(f"Correct: {q['correct'].get()}")
            test_content.append("")

        # Save test to file
        category_dir = os.path.join(app.material_manager.materials_base_dir, "Тесты")
        os.makedirs(category_dir, exist_ok=True)
        base_name = test_name.replace(" ", "_").lower()
        new_file_name = f"{base_name}.txt"
        new_path = os.path.join(category_dir, new_file_name)
        counter = 1
        while os.path.exists(new_path):
            new_file_name = f"{base_name}_{counter}.txt"
            new_path = os.path.join(category_dir, new_file_name)
            counter += 1

        try:
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(test_content))
            norm_path = normalize_path(new_path, app.material_manager.materials_base_dir)
            if norm_path not in {normalize_path(p, app.material_manager.materials_base_dir) for p in
                                 app.material_manager.materials["Тесты"]}:
                app.material_manager.materials["Тесты"].append(new_path)
                app.material_manager.materials["Тесты"] = sorted(
                    app.material_manager.materials["Тесты"],
                    key=lambda x: extract_number(os.path.basename(x))
                )
                app.material_manager.save_materials()
            messagebox.showinfo("Успех", f"Тест '{new_file_name}' успешно создан!")
            show_tests(app)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить тест: {e}")

    tk.Button(main_frame, text="Сохранить тест",
              command=save_test,
              bg=app.accent_color, fg="white",
              font=(app.font_family, 12, 'bold'),
              relief=tk.FLAT, bd=0).pack(pady=10, ipadx=20, ipady=5)


def start_test(app, test_name):
    if not test_name:
        messagebox.showerror("Ошибка", "Выберите тест!")
        return
    test_path = next((path for path in app.material_manager.materials["Тесты"] if os.path.basename(path) == test_name),
                     None)
    if not test_path or not os.path.exists(test_path):
        messagebox.showerror("Ошибка", "Тест не найден или файл отсутствует!")
        return
    content_with_styles, images, error = try_read_file(test_path)
    if error or content_with_styles is None:
        messagebox.showerror("Ошибка", error if error else "Тест должен быть текстовым файлом (.txt).")
        return
    content = "\n".join(text for text, _, _, _, _, _, _ in content_with_styles)
    questions = []
    current_question = None
    lines = content.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if re.match(r"^Question\s*(?:\d+)?\s*:?\s*.+", line, re.IGNORECASE):
            if current_question and len(current_question["options"]) >= 2 and current_question["correct"]:
                questions.append(current_question)
            current_question = {"question": line, "options": [], "correct": None}
        elif re.match(r"^[A-E]\)\s*.+", line) and current_question:
            current_question["options"].append(line)
        elif re.match(r"^(Correct|Answer):\s*[A-E]", line, re.IGNORECASE) and current_question:
            correct_answer = re.search(r"^(Correct|Answer):\s*([A-E])", line, re.IGNORECASE)
            if correct_answer:
                correct_answer = correct_answer.group(2).upper()
                if correct_answer in [opt[0] for opt in current_question["options"]]:
                    current_question["correct"] = correct_answer
                else:
                    current_question = None
        i += 1
    if current_question and len(current_question["options"]) >= 2 and current_question["correct"]:
        questions.append(current_question)
    if not questions:
        messagebox.showerror("Ошибка",
                             "Тест пуст или имеет неверный формат!\nОжидаемый формат:\nQuestion X: [вопрос]\n"
                             "A) [ответ]\nB) [ответ]\n...\nCorrect: [A/B/C/D/E]\n(не менее 2 вариантов ответа)")
        return
    app.clear_content()
    header_frame = tk.Frame(app.content_frame, bg="#2D2D44", height=40, bd=1, relief=tk.RAISED)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_label = tk.Label(header_frame, text=f"Тест: {test_name}",
                            font=(app.font_family, 14, 'bold'),
                            fg=app.text_color, bg="#2D2D44")
    header_label.pack(side=tk.LEFT, pady=5, padx=10)
    tk.Button(header_frame, text="Назад",
              command=lambda: show_tests(app),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 10, 'bold'),
              relief=tk.FLAT, bd=0).pack(side=tk.RIGHT, padx=10, pady=5)

    test_frame = tk.Frame(app.content_frame, bg=app.bg_color)
    test_frame.pack(fill=tk.BOTH, expand=True)
    canvas = tk.Canvas(test_frame, bg=app.bg_color)
    scrollbar = tk.Scrollbar(test_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=app.bg_color)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    app.user_answers = {}
    for idx, q in enumerate(questions):
        question_frame = tk.Frame(scrollable_frame, bg=app.bg_color)
        question_frame.pack(fill=tk.X, pady=10)
        tk.Label(question_frame, text=q["question"],
                 font=(app.font_family, app.font_size, 'bold'),
                 fg=app.text_color, bg=app.bg_color,
                 wraplength=900, justify="left").pack(anchor="w")
        var = tk.StringVar(value="")
        app.user_answers[idx] = var
        for option in q["options"]:
            tk.Radiobutton(question_frame, text=option, variable=var, value=option[0],
                           font=(app.font_family, app.font_size),
                           fg=app.text_color, bg=app.bg_color,
                           selectcolor=app.bg_color, activebackground=app.bg_color,
                           activeforeground=app.text_color).pack(anchor="w")
    app.current_test = questions
    tk.Button(app.content_frame, text="Отправить ответы",
              command=lambda: evaluate_test(app),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 12, 'bold'),
              relief=tk.FLAT, bd=0).pack(pady=10, ipadx=20, ipady=5)


def evaluate_test(app):
    from ui_components import view_materials  # Moved import here to avoid circular dependency
    if not hasattr(app, 'current_test'):
        messagebox.showerror("Ошибка", "Тест не загружен!")
        return
    unanswered = [idx for idx, var in app.user_answers.items() if not var.get()]
    if unanswered:
        response = messagebox.askyesno("Предупреждение",
                                       f"Вы не ответили на {len(unanswered)} вопрос(ов). Продолжить отправку?")
        if not response:
            return
    score = 0
    total = len(app.current_test)
    mistakes = []
    for idx, question in enumerate(app.current_test):
        user_answer = app.user_answers[idx].get()
        correct_answer = question["correct"]
        if not user_answer:
            mistakes.append({
                "question": question["question"],
                "user_answer": "Не выбран",
                "correct_answer": next(opt for opt in question["options"] if opt.startswith(correct_answer))
            })
            continue
        if user_answer == correct_answer:
            score += 1
        else:
            mistakes.append({
                "question": question["question"],
                "user_answer": next((opt for opt in question["options"] if opt.startswith(user_answer)), "Не выбран"),
                "correct_answer": next(opt for opt in question["options"] if opt.startswith(correct_answer))
            })
    app.clear_content()
    header_frame = tk.Frame(app.content_frame, bg="#2D2D44", height=40, bd=1, relief=tk.RAISED)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_label = tk.Label(header_frame, text="Результаты теста",
                            font=(app.font_family, 14, 'bold'),
                            fg=app.text_color, bg="#2D2D44")
    header_label.pack(side=tk.LEFT, pady=5, padx=10)
    tk.Button(header_frame, text="Назад",
              command=lambda: show_tests(app),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 10, 'bold'),
              relief=tk.FLAT, bd=0).pack(side=tk.RIGHT, padx=10, pady=5)

    main_frame = tk.Frame(app.content_frame, bg=app.bg_color)
    main_frame.pack(fill=tk.BOTH, expand=True)
    tk.Label(main_frame, text="Результаты теста",
             font=(app.font_family, 18, 'bold'),
             fg=app.text_color, bg=app.bg_color).pack(pady=10)
    tk.Label(main_frame, text=f"Ваш результат: {score} из {total}",
             font=(app.font_family, app.font_size),
             fg=app.text_color, bg=app.bg_color).pack(pady=10)
    if mistakes:
        tk.Label(main_frame, text="Ошибки:",
                 font=(app.font_family, 16, 'bold'),
                 fg=app.text_color, bg=app.bg_color).pack(pady=5)
        mistakes_frame = tk.Frame(main_frame, bg=app.bg_color)
        mistakes_frame.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(mistakes_frame, bg=app.bg_color)
        scrollbar = tk.Scrollbar(mistakes_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=app.bg_color)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        for mistake in mistakes:
            mistake_frame = tk.Frame(scrollable_frame, bg=app.bg_color)
            mistake_frame.pack(fill=tk.X, pady=5)
            tk.Label(mistake_frame, text=mistake["question"],
                     font=(app.font_family, app.font_size, 'bold'),
                     fg=app.text_color, bg=app.bg_color,
                     wraplength=900, justify="left").pack(anchor="w")
            tk.Label(mistake_frame, text=f"Ваш ответ: {mistake['user_answer']}",
                     font=(app.font_family, app.font_size),
                     fg="red", bg=app.bg_color,
                     wraplength=900, justify="left").pack(anchor="w")
            tk.Label(mistake_frame, text=f"Правильный ответ: {mistake['correct_answer']}",
                     font=(app.font_family, app.font_size),
                     fg="green", bg=app.bg_color,
                     wraplength=900, justify="left").pack(anchor="w")