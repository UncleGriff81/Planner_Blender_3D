"""
Кнопки управления фрейма проекта (новый дизайн)
"""
import tkinter as tk


def create_action_buttons(parent, theme, start_callback, pause_callback, stop_callback,
                          deadline_callback, report_callback, blender_callback,
                          create_file_callback, launch_callback, delete_callback):
    """Создаёт все кнопки управления проектом (новый дизайн)"""
    btn_width = 10
    btn_height = 1
    
    bg_color = theme.get("frame_bg")
    accent_color = theme.get("accent_color")
    
    default_style = {
        "bg": bg_color,
        "fg": accent_color,
        "relief": "solid",
        "bd": 1,
        "highlightthickness": 0,
        "font": ("Arial", 10)
    }
    
    btn_start = tk.Button(parent, text="▶ Начать", width=btn_width, height=btn_height,
                         command=start_callback,
                         **default_style)
    btn_start.pack(side="left", padx=3)
    
    btn_pause = tk.Button(parent, text="⏸ Пауза", width=btn_width, height=btn_height,
                         command=pause_callback,
                         **default_style)
    btn_pause.pack(side="left", padx=3)
    
    btn_stop = tk.Button(parent, text="⏹ Стоп", width=btn_width, height=btn_height,
                        command=stop_callback,
                        **default_style)
    btn_stop.pack(side="left", padx=3)
    
    btn_deadline = tk.Button(parent, text="📅 Дедлайн", width=10, height=btn_height,
                            command=deadline_callback,
                            **default_style)
    btn_deadline.pack(side="left", padx=3)
    
    btn_report = tk.Button(parent, text="📄 Отчёт", width=10, height=btn_height,
                          command=report_callback,
                          **default_style)
    btn_report.pack(side="left", padx=3)
    
    btn_blender_choose = tk.Button(parent, text="🔧 Выбрать Blender", width=14, height=btn_height,
                                   command=blender_callback,
                                   **default_style)
    btn_blender_choose.pack(side="left", padx=3)
    
    btn_create_file = tk.Button(parent, text="📁 Создать файл", width=12, height=btn_height,
                                command=create_file_callback,
                                **default_style)
    btn_create_file.pack(side="left", padx=3)
    
    btn_launch = tk.Button(parent, text="🎨 Запустить Blender", width=14, height=btn_height,
                          command=launch_callback,
                          **default_style)
    btn_launch.pack(side="left", padx=3)
    
    btn_delete = tk.Button(parent, text="🗑 Удалить", width=10, height=btn_height,
                          command=delete_callback,
                          **default_style)
    btn_delete.pack(side="right", padx=3)
    
    def on_enter(btn):
        btn.config(bg=accent_color, fg=bg_color)
    
    def on_leave(btn):
        btn.config(bg=bg_color, fg=accent_color)
    
    for btn in [btn_start, btn_pause, btn_stop, btn_deadline, btn_report,
                btn_blender_choose, btn_create_file, btn_launch, btn_delete]:
        btn.bind("<Enter>", lambda e, b=btn: on_enter(b))
        btn.bind("<Leave>", lambda e, b=btn: on_leave(b))