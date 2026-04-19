"""
Диалог создания нового проекта (с поддержкой выбора существующего .blend файла)
"""
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import datetime
import tempfile
import subprocess
from blender_utils import get_all_blender_versions
from date_utils import calculate_deadline_from_days, parse_deadline_date, format_deadline, create_calendar_window
from db_manager import save_project as save_to_db
from task_plan import Project


def create_project_dialog(root, theme, projects_objects_list, auto_saver, auto_save_callback, 
                          refresh_callback, update_monitor_callback, show_notification):
    """Создаёт диалог нового проекта"""
    available_versions = get_all_blender_versions()
    
    dialog = tk.Toplevel(root)
    dialog.title("Создать новый проект")
    dialog.configure(bg=theme.get("bg_color"))
    dialog.transient(root)
    dialog.grab_set()
    
    dialog.update_idletasks()
    width = 650
    height = 800
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")
    dialog.resizable(False, False)
    
    # Основной контейнер с прокруткой (на случай, если содержимое не помещается)
    main_canvas = tk.Canvas(dialog, bg=theme.get("bg_color"), highlightthickness=0)
    scrollbar = tk.Scrollbar(dialog, orient="vertical", command=main_canvas.yview)
    main_canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    main_canvas.pack(side="left", fill="both", expand=True)
    
    main_frame = tk.Frame(main_canvas, bg=theme.get("bg_color"))
    main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
    
    def configure_scroll_region(event):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    
    main_frame.bind("<Configure>", configure_scroll_region)
    
    # Используем grid для фиксации порядка
    row = 0
    
    # Заголовок
    tk.Label(main_frame, text="➕ Создание нового проекта", 
             font=("Arial", 14, "bold"),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).grid(row=row, column=0, columnspan=2, pady=(0, 20), sticky="ew")
    row += 1
    
    # ===== 1. СПОСОБ СОЗДАНИЯ =====
    creation_type_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    creation_type_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 15))
    
    tk.Label(creation_type_frame, text="📌 Способ создания:", font=("Arial", 11),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(anchor="w", pady=(0, 5))
    
    creation_type_var = tk.StringVar(value="new")
    
    new_file_radio = tk.Radiobutton(creation_type_frame, text="Создать новый .blend файл", 
                                    variable=creation_type_var, value="new",
                                    bg=theme.get("bg_color"), fg=theme.get("fg_color"),
                                    selectcolor=theme.get("bg_color"))
    new_file_radio.pack(anchor="w", padx=20)
    
    existing_file_radio = tk.Radiobutton(creation_type_frame, text="Использовать существующий .blend файл", 
                                         variable=creation_type_var, value="existing",
                                         bg=theme.get("bg_color"), fg=theme.get("fg_color"),
                                         selectcolor=theme.get("bg_color"))
    existing_file_radio.pack(anchor="w", padx=20)
    
    row += 1
    
    # Разделитель
    separator1 = tk.Frame(main_frame, height=1, bg=theme.get("accent_color"))
    separator1.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10, 15))
    row += 1
    
    # ===== 2. НАЗВАНИЕ ПРОЕКТА =====
    name_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    name_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
    
    name_label = tk.Label(name_frame, text="📌 Название проекта:", font=("Arial", 11),
                          bg=theme.get("bg_color"), fg=theme.get("fg_color"))
    name_label.pack(anchor="w")
    tk.Label(name_frame, text=" *", font=("Arial", 11, "bold"),
             bg=theme.get("bg_color"), fg="orange").place(in_=name_label, x=name_label.winfo_reqwidth() + 2, y=0)
    
    name_entry = tk.Entry(name_frame, font=("Arial", 11),
                          bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                          insertbackground=theme.get("fg_color"))
    name_entry.pack(fill="x", pady=(5, 0))
    name_entry.focus()
    
    name_status = tk.Label(name_frame, text="Название проекта не указано", font=("Arial", 9),
                           bg=theme.get("bg_color"), fg="orange")
    name_status.pack(anchor="w", pady=(2, 0))
    row += 1
    
    # ===== 3. ОПИСАНИЕ ПРОЕКТА =====
    desc_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    desc_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
    
    tk.Label(desc_frame, text="📝 Описание проекта:", font=("Arial", 11),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(anchor="w")
    
    desc_text = tk.Text(desc_frame, height=3, font=("Arial", 11),
                        bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                        insertbackground=theme.get("fg_color"), wrap="word")
    desc_text.pack(fill="x", pady=(5, 0))
    
    desc_status = tk.Label(desc_frame, text="Описание проекта не указано", font=("Arial", 9),
                           bg=theme.get("bg_color"), fg="orange")
    desc_status.pack(anchor="w", pady=(2, 0))
    row += 1
    
    # ===== 4. КОНТЕЙНЕРЫ ДЛЯ ФАЙЛОВ (оба всегда на месте, но один скрыт) =====
    
    # Контейнер для нового файла
    new_file_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    new_file_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
    
    # Имя файла
    filename_frame = tk.Frame(new_file_frame, bg=theme.get("bg_color"))
    filename_frame.pack(fill="x", pady=(0, 12))
    
    filename_label = tk.Label(filename_frame, text="📁 Имя файла (.blend):", font=("Arial", 11),
                              bg=theme.get("bg_color"), fg=theme.get("fg_color"))
    filename_label.pack(anchor="w")
    tk.Label(filename_frame, text=" *", font=("Arial", 11, "bold"),
             bg=theme.get("bg_color"), fg="orange").place(in_=filename_label, x=filename_label.winfo_reqwidth() + 2, y=0)
    
    filename_entry = tk.Entry(filename_frame, font=("Arial", 11),
                              bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                              insertbackground=theme.get("fg_color"))
    filename_entry.pack(fill="x", pady=(5, 0))
    
    filename_status = tk.Label(filename_frame, text="Имя файла не указано", font=("Arial", 9),
                               bg=theme.get("bg_color"), fg="orange")
    filename_status.pack(anchor="w", pady=(2, 0))
    
    # Папка сохранения
    folder_frame = tk.Frame(new_file_frame, bg=theme.get("bg_color"))
    folder_frame.pack(fill="x", pady=(0, 12))
    
    folder_label = tk.Label(folder_frame, text="📂 Папка сохранения:", font=("Arial", 11),
                            bg=theme.get("bg_color"), fg=theme.get("fg_color"))
    folder_label.pack(anchor="w")
    tk.Label(folder_frame, text=" *", font=("Arial", 11, "bold"),
             bg=theme.get("bg_color"), fg="orange").place(in_=folder_label, x=folder_label.winfo_reqwidth() + 2, y=0)
    
    folder_select_frame = tk.Frame(folder_frame, bg=theme.get("bg_color"))
    folder_select_frame.pack(fill="x", pady=(5, 0))
    
    folder_path_var = tk.StringVar()
    folder_entry = tk.Entry(folder_select_frame, textvariable=folder_path_var,
                            font=("Arial", 10), state="readonly",
                            bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                            readonlybackground=theme.get("frame_bg"))
    folder_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
    
    def choose_folder():
        folder = filedialog.askdirectory(
            title="Выберите папку для сохранения .blend файлов",
            initialdir=os.path.expanduser("~/Documents"),
            parent=dialog
        )
        if folder:
            folder = os.path.normpath(folder)
            folder_path_var.set(folder)
            folder_status_label.config(text="✅ Папка выбрана", fg=theme.get("success_color"))
    
    folder_btn = tk.Button(folder_select_frame, text="📁 Обзор",
                           bg=theme.get("accent_color"), fg="white",
                           relief="flat", command=choose_folder)
    folder_btn.pack(side="right")
    
    folder_status_label = tk.Label(folder_frame, text="Папка не выбрана", 
                                   font=("Arial", 9), bg=theme.get("bg_color"), fg="orange")
    folder_status_label.pack(anchor="w", pady=(2, 0))
    
    # Контейнер для существующего файла
    existing_file_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    existing_file_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 12))
    
    existing_file_select_frame = tk.Frame(existing_file_frame, bg=theme.get("bg_color"))
    existing_file_select_frame.pack(fill="x", pady=(0, 12))
    
    tk.Label(existing_file_select_frame, text="📂 Выберите существующий .blend файл:", font=("Arial", 11),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(anchor="w")
    
    existing_file_path_var = tk.StringVar()
    existing_file_entry = tk.Entry(existing_file_select_frame, textvariable=existing_file_path_var,
                                    font=("Arial", 10), state="readonly",
                                    bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                                    readonlybackground=theme.get("frame_bg"))
    existing_file_entry.pack(fill="x", pady=(5, 0))
    
    def choose_existing_file():
        file_path = filedialog.askopenfilename(
            title="Выберите существующий .blend файл",
            filetypes=[("Blender files", "*.blend"), ("All files", "*.*")],
            parent=dialog
        )
        if file_path:
            file_path = os.path.normpath(file_path)
            existing_file_path_var.set(file_path)
            existing_file_status.config(text="✅ Файл выбран", fg=theme.get("success_color"))
            
            # Предлагаем имя проекта из имени файла
            suggested_name = os.path.splitext(os.path.basename(file_path))[0]
            if not name_entry.get().strip():
                name_entry.delete(0, tk.END)
                name_entry.insert(0, suggested_name)
                name_status.config(text="✅", fg=theme.get("success_color"))
    
    existing_file_browse_btn = tk.Button(existing_file_select_frame, text="📁 Обзор",
                                          bg=theme.get("accent_color"), fg="white",
                                          relief="flat", command=choose_existing_file)
    existing_file_browse_btn.pack(pady=(5, 0))
    
    existing_file_status = tk.Label(existing_file_select_frame, text="Файл не выбран", 
                                     font=("Arial", 9), bg=theme.get("bg_color"), fg="orange")
    existing_file_status.pack(anchor="w", pady=(2, 0))
    
    existing_file_info = tk.Label(existing_file_select_frame, text="", 
                                   font=("Arial", 8), bg=theme.get("bg_color"), fg="gray")
    existing_file_info.pack(anchor="w", pady=(2, 0))
    
    # Функция обновления информации о выбранном файле
    def update_existing_file_info(*args):
        file_path = existing_file_path_var.get()
        if file_path and os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d.%m.%Y %H:%M')
            existing_file_info.config(text=f"Размер: {size_mb:.1f} МБ | Изменён: {modified}")
        else:
            existing_file_info.config(text="")
    
    existing_file_path_var.trace_add("write", update_existing_file_info)
    
    # Функция переключения видимости (оба фрейма уже на своих местах, просто скрываем/показываем)
    def toggle_creation_type(*args):
        if creation_type_var.get() == "new":
            new_file_frame.grid()
            existing_file_frame.grid_remove()
        else:
            new_file_frame.grid_remove()
            existing_file_frame.grid()
    
    creation_type_var.trace_add("write", toggle_creation_type)
    toggle_creation_type()  # Инициализация
    
    row += 1
    
    # ===== 5. ВЕРСИЯ BLENDER =====
    blender_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    blender_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 15))
    
    blender_label_title = tk.Label(blender_frame, text="🔧 Версия Blender:", font=("Arial", 11),
                                   bg=theme.get("bg_color"), fg=theme.get("fg_color"))
    blender_label_title.pack(anchor="w")
    tk.Label(blender_frame, text=" *", font=("Arial", 11, "bold"),
             bg=theme.get("bg_color"), fg="orange").place(in_=blender_label_title, x=blender_label_title.winfo_reqwidth() + 2, y=0)
    
    blender_select_frame = tk.Frame(blender_frame, bg=theme.get("bg_color"))
    blender_select_frame.pack(fill="x", pady=(5, 0))
    
    blender_var = tk.StringVar()
    blender_path_map = {}
    
    if available_versions:
        blender_options = []
        for v in available_versions:
            display = f"{v['version_str']} - {os.path.basename(os.path.dirname(v['path']))}"
            blender_options.append((display, v['path']))
        
        blender_dropdown = tk.OptionMenu(blender_select_frame, blender_var, *[opt[0] for opt in blender_options])
        blender_dropdown.config(bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                                relief="flat", width=50)
        blender_dropdown.pack(side="left", fill="x", expand=True)
        
        blender_path_map = {opt[0]: opt[1] for opt in blender_options}
        
        if blender_options:
            default_display = blender_options[0][0]
            blender_var.set(default_display)
    else:
        blender_entry = tk.Entry(blender_select_frame, font=("Arial", 10),
                                 bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                                 insertbackground=theme.get("fg_color"))
        blender_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        def browse_blender():
            path = filedialog.askopenfilename(
                title="Выберите исполняемый файл Blender",
                filetypes=[("Executable", "blender.exe"), ("All files", "*.*")],
                parent=dialog
            )
            if path:
                blender_entry.delete(0, tk.END)
                blender_entry.insert(0, path)
                blender_var.set(path)
                blender_status.config(text="✅", fg=theme.get("success_color"))
        
        blender_btn = tk.Button(blender_select_frame, text="📁 Обзор",
                                bg=theme.get("accent_color"), fg="white",
                                relief="flat", command=browse_blender)
        blender_btn.pack(side="right")
    
    blender_status = tk.Label(blender_frame, text="⚠️ Выберите Blender", font=("Arial", 9),
                              bg=theme.get("bg_color"), fg="orange")
    blender_status.pack(anchor="w", pady=(2, 0))
    row += 1
    
    # ===== 6. ДЕДЛАЙН =====
    deadline_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    deadline_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 15))
    
    tk.Label(deadline_frame, text="⏰ Срок выполнения (необязательно):", font=("Arial", 11),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(anchor="w")
    
    deadline_type_var = tk.StringVar(value="none")
    
    deadline_none = tk.Radiobutton(deadline_frame, text="Без срока", variable=deadline_type_var, value="none",
                                   bg=theme.get("bg_color"), fg=theme.get("fg_color"),
                                   selectcolor=theme.get("bg_color"))
    deadline_none.pack(anchor="w", padx=20)
    
    deadline_days_frame = tk.Frame(deadline_frame, bg=theme.get("bg_color"))
    deadline_days_frame.pack(anchor="w", padx=20)
    
    tk.Radiobutton(deadline_days_frame, text="Через дней:", variable=deadline_type_var, value="days",
                   bg=theme.get("bg_color"), fg=theme.get("fg_color"),
                   selectcolor=theme.get("bg_color")).pack(side="left")
    
    deadline_days_spinbox = tk.Spinbox(deadline_days_frame, from_=1, to=365, width=8,
                                        bg=theme.get("frame_bg"), fg=theme.get("fg_color"))
    deadline_days_spinbox.pack(side="left", padx=5)
    deadline_days_spinbox.delete(0, tk.END)
    deadline_days_spinbox.insert(0, "7")
    
    deadline_date_frame = tk.Frame(deadline_frame, bg=theme.get("bg_color"))
    deadline_date_frame.pack(anchor="w", padx=20)
    
    tk.Radiobutton(deadline_date_frame, text="Конкретная дата:", variable=deadline_type_var, value="date",
                   bg=theme.get("bg_color"), fg=theme.get("fg_color"),
                   selectcolor=theme.get("bg_color")).pack(side="left")
    
    deadline_date_entry = tk.Entry(deadline_date_frame, width=15, font=("Arial", 10),
                                   bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                                   insertbackground=theme.get("fg_color"))
    deadline_date_entry.pack(side="left", padx=5)
    deadline_date_entry.insert(0, datetime.datetime.now().strftime('%d.%m.%Y'))
    
    def show_calendar():
        create_calendar_window(deadline_date_entry, lambda date: deadline_date_entry.delete(0, tk.END) or deadline_date_entry.insert(0, date.strftime('%d.%m.%Y')))
    
    calendar_btn = tk.Button(deadline_date_frame, text="📅", width=3,
                             bg=theme.get("accent_color"), fg="white",
                             relief="flat", command=show_calendar)
    calendar_btn.pack(side="left", padx=2)
    row += 1
    
    # ===== 7. КНОПКИ =====
    buttons_frame_dialog = tk.Frame(main_frame, bg=theme.get("bg_color"))
    buttons_frame_dialog.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10, 0))
    
    # Валидация полей
    def validate_fields():
        valid = True
        
        name = name_entry.get().strip()
        if not name:
            name_status.config(text="⚠️ Название проекта не указано", fg="orange")
            valid = False
        else:
            name_status.config(text="✅", fg=theme.get("success_color"))
        
        description = desc_text.get("1.0", "end-1c").strip()
        if not description:
            desc_status.config(text="⚠️ Описание не указано", fg="orange")
        else:
            desc_status.config(text="✅", fg=theme.get("success_color"))
        
        if available_versions:
            selected_display = blender_var.get()
            if not selected_display or selected_display not in blender_path_map:
                blender_status.config(text="⚠️ Выберите версию Blender", fg="orange")
                valid = False
            else:
                blender_status.config(text="✅", fg=theme.get("success_color"))
        else:
            blender_path = blender_var.get()
            if not blender_path or not os.path.exists(blender_path):
                blender_status.config(text="⚠️ Выберите Blender", fg="orange")
                valid = False
            else:
                blender_status.config(text="✅", fg=theme.get("success_color"))
        
        if creation_type_var.get() == "new":
            blend_name = filename_entry.get().strip()
            if not blend_name:
                filename_status.config(text="⚠️ Имя файла не указано", fg="orange")
                valid = False
            else:
                filename_status.config(text="✅", fg=theme.get("success_color"))
            
            folder = folder_path_var.get()
            if not folder:
                folder_status_label.config(text="⚠️ Папка не выбрана", fg="orange")
                valid = False
            else:
                folder_status_label.config(text="✅ Папка выбрана", fg=theme.get("success_color"))
        else:
            file_path = existing_file_path_var.get()
            if not file_path or not os.path.exists(file_path):
                existing_file_status.config(text="⚠️ Файл не выбран или не существует", fg="orange")
                valid = False
            else:
                existing_file_status.config(text="✅ Файл выбран", fg=theme.get("success_color"))
        
        return valid
    
    # Создание проекта
    def create_new_project():
        if not validate_fields():
            messagebox.showerror("Ошибка", "Заполните все обязательные поля!", parent=dialog)
            return
        
        name = name_entry.get().strip()
        description = desc_text.get("1.0", "end-1c").strip()
        
        if available_versions:
            selected_display = blender_var.get()
            blender_selected_path = blender_path_map.get(selected_display, "")
        else:
            blender_selected_path = blender_var.get()
        
        if not blender_selected_path:
            messagebox.showerror("Ошибка", "Выберите версию Blender!", parent=dialog)
            return
        
        deadline_date = ""
        deadline_days = 0
        
        if deadline_type_var.get() == "days":
            deadline_days = int(deadline_days_spinbox.get())
            deadline_date_obj = calculate_deadline_from_days(deadline_days)
            if deadline_date_obj:
                deadline_date = deadline_date_obj.strftime('%Y-%m-%d %H:%M:%S')
        elif deadline_type_var.get() == "date":
            try:
                deadline_date_obj = parse_deadline_date(deadline_date_entry.get())
                if deadline_date_obj:
                    deadline_date = deadline_date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    deadline_days = max(1, (deadline_date_obj - datetime.datetime.now()).days)
            except:
                pass
        
        creation_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if creation_type_var.get() == "new":
            # Создание нового файла
            blend_name_raw = filename_entry.get().strip()
            blend_name_safe = "".join(c for c in blend_name_raw if c.isalnum() or c in (' ', '.', '_')).rstrip()
            if not blend_name_safe:
                messagebox.showerror("Ошибка", "Недопустимое имя файла!\nИспользуйте буквы, цифры, пробелы, точки и подчёркивания.", parent=dialog)
                return
            
            selected_folder = folder_path_var.get()
            full_file_path = os.path.join(selected_folder, f"{blend_name_safe}.blend")
            full_file_path = os.path.normpath(full_file_path)
            
            # Создаём файл через Blender
            show_notification("⏳ Создание проекта через Blender... Подождите 3-5 секунд", "info", 4000)
            dialog.update()
            
            file_created = False
            
            if blender_selected_path and os.path.exists(blender_selected_path):
                blender_path = os.path.normpath(blender_selected_path)
                try:
                    script_content = f'''
import bpy
bpy.ops.wm.save_as_mainfile(filepath=r'{full_file_path}')
'''
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                        f.write(script_content)
                        script_path = f.name
                    
                    cmd = [blender_path, '--background', '--python', script_path]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    
                    try:
                        os.unlink(script_path)
                    except:
                        pass
                    
                    if os.path.exists(full_file_path) and os.path.getsize(full_file_path) > 1024:
                        file_created = True
                        print(f"[CREATE] Файл успешно создан через Blender: {full_file_path}")
                    else:
                        print(f"[CREATE] Ошибка при создании файла: {result.stderr[:200] if result.stderr else 'неизвестная ошибка'}")
                except subprocess.TimeoutExpired:
                    print(f"[CREATE] Таймаут при создании файла")
                    messagebox.showerror("Ошибка", "Превышено время ожидания при создании файла.\nПроверьте, что Blender запускается корректно.", parent=dialog)
                    return
                except Exception as e:
                    print(f"[CREATE] Исключение при создании файла: {e}")
                    messagebox.showerror("Ошибка", f"Не удалось создать файл:\n{str(e)}", parent=dialog)
                    return
            
            if not file_created:
                messagebox.showerror("Ошибка", f"Не удалось создать файл:\n{full_file_path}\n\n"
                                   "Убедитесь, что выбранная версия Blender работает корректно.", parent=dialog)
                return
        else:
            # Использование существующего файла
            full_file_path = existing_file_path_var.get()
            if not os.path.exists(full_file_path):
                messagebox.showerror("Ошибка", f"Файл не найден:\n{full_file_path}", parent=dialog)
                return
            blend_name_safe = os.path.splitext(os.path.basename(full_file_path))[0]
        
        # Сохраняем проект в БД
        project_data_for_db = {
            'name': name,
            'description': description,
            'blend_file': blend_name_safe,
            'creation_date': creation_date,
            'elapsed_time': 0.0,
            'blender_path': blender_selected_path,
            'full_file_path': full_file_path,
            'deadline_date': deadline_date,
            'deadline_days': deadline_days
        }
        
        new_project_id_in_db = save_to_db(project_data_for_db)
        
        new_project_obj = Project(
            id=new_project_id_in_db,
            name=name,
            description=description,
            blend_file=blend_name_safe,
            creation_date=creation_date,
            elapsed_time=0.0,
            blender_path=blender_selected_path,
            deadline_date=deadline_date,
            deadline_days=deadline_days
        )
        new_project_obj.auto_save_callback = auto_save_callback
        new_project_obj.set_full_file_path(full_file_path)
        
        projects_objects_list.append(new_project_obj)
        auto_saver.add_project(new_project_obj)
        
        refresh_callback()
        update_monitor_callback()
        dialog.destroy()
        
        deadline_msg = ""
        if deadline_date:
            deadline_obj = new_project_obj.get_deadline_date_obj()
            if deadline_obj:
                deadline_msg = f"\n⏰ Дедлайн: {format_deadline(deadline_obj)}"
        
        show_notification(f"✅ Проект '{name}' успешно создан!", "success", 3000)
        
        messagebox.showinfo("Успех!", 
                           f"✅ Проект '{name}' успешно создан!\n\n"
                           f"📁 Файл: {full_file_path}{deadline_msg}\n\n"
                           f"Теперь:\n"
                           f"1. Нажмите '🎨 Запустить Blender', чтобы начать работу\n"
                           f"2. Таймер запустится автоматически при открытии файла",
                           parent=root)
    
    name_entry.bind('<KeyRelease>', lambda e: validate_fields())
    desc_text.bind('<KeyRelease>', lambda e: validate_fields())
    filename_entry.bind('<KeyRelease>', lambda e: validate_fields())
    
    btn_create = tk.Button(buttons_frame_dialog, text="✅ Создать проект",
                           bg=theme.get("success_color"), fg="white",
                           relief="flat", command=create_new_project, font=("Arial", 11))
    btn_create.pack(side="right", padx=5)
    
    btn_cancel = tk.Button(buttons_frame_dialog, text="❌ Отмена",
                           bg=theme.get("error_color"), fg="white",
                           relief="flat", command=dialog.destroy, font=("Arial", 11))
    btn_cancel.pack(side="right", padx=5)
    
    dialog.bind('<Return>', lambda e: create_new_project())
    dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    validate_fields()