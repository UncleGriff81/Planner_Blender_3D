"""
deadline_notification.py - Диалог уведомления о срочных и просроченных проектах
"""
import tkinter as tk
import subprocess
import sys
import os
from datetime import datetime
from date_utils import get_time_left_string


def show_deadline_notification(root, theme, projects_objects_list, on_dont_show_today):
    """Показывает окно с проектами, у которых дедлайн <= 2 дней ИЛИ просрочен"""
    today = datetime.now()
    urgent_projects = []
    
    for project in projects_objects_list:
        deadline = project.get_deadline_date_obj()
        if deadline:
            days_left = (deadline - today).days
            # Показываем как срочные (0-2 дня), так и просроченные (отрицательные)
            if days_left <= 2:
                urgent_projects.append((project, days_left))
    
    if not urgent_projects:
        return
    
    # Сортируем: сначала самые просроченные, потом срочные
    urgent_projects.sort(key=lambda x: x[1])
    
    notification_window = tk.Toplevel(root)
    notification_window.title("⚠️ Срочные проекты")
    notification_window.configure(bg=theme.get("bg_color"))
    notification_window.transient(root)
    notification_window.grab_set()
    notification_window.geometry("650x550")
    notification_window.resizable(False, False)
    
    notification_window.update_idletasks()
    x = (notification_window.winfo_screenwidth() // 2) - 325
    y = (notification_window.winfo_screenheight() // 2) - 275
    notification_window.geometry(f"650x550+{x}+{y}")
    
    main_frame = tk.Frame(notification_window, bg=theme.get("bg_color"))
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    tk.Label(main_frame, text="⚠️ Срочные и просроченные проекты",
             font=("Arial", 14, "bold"),
             bg=theme.get("bg_color"), fg=theme.get("error_color")).pack(pady=(0, 10))
    
    tk.Label(main_frame, text="У следующих проектов поджимают или уже просрочены сроки:",
             font=("Arial", 10),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(pady=(0, 15))
    
    # Фрейм со списком проектов (с прокруткой)
    list_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    list_frame.pack(fill="both", expand=True, pady=(0, 15))
    
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")
    
    canvas = tk.Canvas(list_frame, bg=theme.get("frame_bg"), highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    inner_frame = tk.Frame(canvas, bg=theme.get("frame_bg"))
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")
    
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    inner_frame.bind("<Configure>", on_frame_configure)
    
    # Заполняем список проектов с кнопками
    for project, days_left in urgent_projects:
        item_frame = tk.Frame(inner_frame, bg=theme.get("frame_bg"), pady=5)
        item_frame.pack(fill="x", padx=10, pady=5)
        
        deadline = project.get_deadline_date_obj()
        time_left = get_time_left_string(deadline)
        
        # Определяем статус
        if days_left < 0:
            status = "🔴 ПРОСРОЧЕН"
            status_color = "red"
        elif days_left == 0:
            status = "🔴 СЕГОДНЯ"
            status_color = "orange"
        elif days_left == 1:
            status = "🟡 ЗАВТРА"
            status_color = "orange"
        else:
            status = "🟠 СКОРО"
            status_color = "yellow"
        
        status_label = tk.Label(item_frame, text=status, font=("Arial", 10, "bold"),
                                 bg=theme.get("frame_bg"), fg=status_color, width=12)
        status_label.pack(side="left", padx=(0, 10))
        
        name_label = tk.Label(item_frame, text=project.name, font=("Arial", 10),
                              bg=theme.get("frame_bg"), fg=theme.get("fg_color"), anchor="w")
        name_label.pack(side="left", fill="x", expand=True)
        
        time_label = tk.Label(item_frame, text=time_left, font=("Arial", 9),
                              bg=theme.get("frame_bg"), fg="gray")
        time_label.pack(side="left", padx=(10, 10))
        
        def open_in_blender(p=project):
            file_path = p.get_full_file_path()
            if file_path and os.path.exists(file_path):
                if p.blender_path and os.path.exists(p.blender_path):
                    # Запускаем Blender без консоли на Windows
                    if sys.platform == "win32":
                        subprocess.Popen([p.blender_path, file_path], shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
                    else:
                        subprocess.Popen([p.blender_path, file_path], shell=False)
                else:
                    # Если путь к Blender не задан, пытаемся открыть файл по умолчанию
                    if sys.platform == "win32":
                        os.startfile(file_path)
                    else:
                        subprocess.Popen(["open", file_path])
        
        open_btn = tk.Button(item_frame, text="🎨 Перейти в Blender", font=("Arial", 9),
                             bg=theme.get("info_color"), fg="white", relief="flat",
                             command=open_in_blender)
        open_btn.pack(side="right", padx=5)
    
    # Чекбокс "Больше не показывать сегодня"
    dont_show_var = tk.BooleanVar(value=False)
    dont_show_check = tk.Checkbutton(main_frame, text="Больше не показывать сегодня",
                                      variable=dont_show_var,
                                      bg=theme.get("bg_color"), fg=theme.get("fg_color"),
                                      selectcolor=theme.get("bg_color"))
    dont_show_check.pack(anchor="w", pady=(5, 10))
    
    def on_close():
        if dont_show_var.get():
            on_dont_show_today()
        notification_window.destroy()
    
    close_btn = tk.Button(main_frame, text="Закрыть",
                          font=("Arial", 10),
                          bg=theme.get("accent_color"), fg="white",
                          relief="flat", padx=20, pady=5,
                          command=on_close)
    close_btn.pack()