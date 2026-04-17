"""
Кнопки управления фрейма проекта
"""
import tkinter as tk


def create_action_buttons(parent, theme, start_callback, pause_callback, stop_callback,
                          deadline_callback, report_callback, blender_callback,
                          create_file_callback, launch_callback, delete_callback):
    """Создаёт все кнопки управления проектом (без таймера)"""
    btn_width = 10
    btn_height = 1
    
    btn_start = tk.Button(parent, text="▶ Начать", width=btn_width, height=btn_height,
                         bg=theme.get("success_color"), fg="white",
                         relief="flat", command=start_callback, font=("Arial", 10))
    btn_start.pack(side="left", padx=3)
    
    btn_pause = tk.Button(parent, text="⏸ Пауза", width=btn_width, height=btn_height,
                         bg=theme.get("warning_color"), fg="white",
                         relief="flat", command=pause_callback, font=("Arial", 10))
    btn_pause.pack(side="left", padx=3)
    
    btn_stop = tk.Button(parent, text="⏹ Стоп", width=btn_width, height=btn_height,
                        bg=theme.get("error_color"), fg="white",
                        relief="flat", command=stop_callback, font=("Arial", 10))
    btn_stop.pack(side="left", padx=3)
    
    btn_deadline = tk.Button(parent, text="📅 Дедлайн", width=10, height=btn_height,
                            bg=theme.get("info_color"), fg="white",
                            relief="flat", command=deadline_callback, font=("Arial", 10))
    btn_deadline.pack(side="left", padx=3)
    
    btn_report = tk.Button(parent, text="📄 Отчёт", width=10, height=btn_height,
                          bg=theme.get("info_color"), fg="white",
                          relief="flat", command=report_callback, font=("Arial", 10))
    btn_report.pack(side="left", padx=3)
    
    btn_blender_choose = tk.Button(parent, text="🔧 Выбрать Blender", width=14, height=btn_height,
                                   bg=theme.get("accent_color"), fg="white",
                                   relief="flat", command=blender_callback, font=("Arial", 10))
    btn_blender_choose.pack(side="left", padx=3)
    
    btn_create_file = tk.Button(parent, text="📁 Создать файл", width=12, height=btn_height,
                                bg=theme.get("info_color"), fg="white",
                                relief="flat", command=create_file_callback, font=("Arial", 10))
    btn_create_file.pack(side="left", padx=3)
    
    btn_launch = tk.Button(parent, text="🎨 Запустить Blender", width=14, height=btn_height,
                          bg=theme.get("success_color"), fg="white",
                          relief="flat", command=launch_callback, font=("Arial", 10))
    btn_launch.pack(side="left", padx=3)
    
    btn_delete = tk.Button(parent, text="🗑 Удалить", width=10, height=btn_height,
                          bg=theme.get("error_color"), fg="white",
                          relief="flat", command=delete_callback, font=("Arial", 10))
    btn_delete.pack(side="right", padx=3)