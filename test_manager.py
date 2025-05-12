import os
import tkinter as tk
from tkinter import ttk, messagebox
import re
from file_reader import try_read_file


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
        return
    tk.Label(main_frame, text="Выберите тест:",
             font=(app.font_family, app.font_size),
             fg=app.text_color, bg=app.bg_color).pack(pady=5)
    test_var = tk.StringVar()
    test_menu = ttk.Combobox(main_frame, textvariable=test_var,
                             values=[os.path.basename(path) for path in app.material_manager.materials["Тесты"]])
    test_menu.pack(pady=5)
    tk.Button(main_frame, text="Начать тест",
              command=lambda: start_test(app, test_var.get()),
              bg=app.accent_color, fg="white",
              font=(app.font_family, 12, 'bold'),
              relief=tk.FLAT, bd=0).pack(pady=10, ipadx=20, ipady=5)


def start_test(app, test_name):
    try:
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
    except:
        pass


def evaluate_test(app):
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