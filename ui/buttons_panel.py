"""
Панель основных кнопок (новый дизайн)
"""
import tkinter as tk


def create_buttons_panel(parent, theme, create_project, generate_reports, show_statistics, 
                         check_updates, toggle_startup, minimize_to_tray, is_pystray_available):
    """Создаёт панель с основными кнопками (новый дизайн)"""
    buttons_frame = tk.Frame(parent, bg=theme.get("bg_color"))
    buttons_frame.grid(row=2, column=0, columnspan=2, pady=(0, 15), sticky="we", padx=10)
    
    bg_color = theme.get("bg_color")
    accent_color = theme.get("accent_color")
    
    default_style = {
        "bg": bg_color,
        "fg": accent_color,
        "relief": "solid",
        "bd": 1,
        "highlightthickness": 0
    }
    
    create_btn = tk.Button(buttons_frame, text="➕ Создать проект", font=("Arial", 11),
                           command=create_project,
                           **default_style)
    create_btn.pack(side="left", padx=(0, 10))
    
    report_btn = tk.Button(buttons_frame, text="📊 Отчёт", font=("Arial", 10),
                           command=generate_reports,
                           **default_style)
    report_btn.pack(side="left", padx=5)
    
    stats_btn = tk.Button(buttons_frame, text="📊 Статистика", font=("Arial", 10),
                          command=show_statistics,
                          **default_style)
    stats_btn.pack(side="left", padx=5)
    
    update_btn = tk.Button(buttons_frame, text="🔄 Проверить обновления", font=("Arial", 10),
                           command=check_updates,
                           **default_style)
    update_btn.pack(side="left", padx=5)
    
    startup_btn = tk.Button(buttons_frame, text="⚙️ Автозагрузка", font=("Arial", 10),
                            command=toggle_startup,
                            **default_style)
    startup_btn.pack(side="left", padx=5)
    
    if is_pystray_available:
        tray_btn = tk.Button(buttons_frame, text="📌 Свернуть в трей", font=("Arial", 10),
                             command=minimize_to_tray,
                             **default_style)
        tray_btn.pack(side="left", padx=5)
    
    def on_enter(btn):
        btn.config(bg=accent_color, fg=bg_color)
    
    def on_leave(btn):
        btn.config(bg=bg_color, fg=accent_color)
    
    for btn in [create_btn, report_btn, stats_btn, update_btn, startup_btn]:
        btn.bind("<Enter>", lambda e, b=btn: on_enter(b))
        btn.bind("<Leave>", lambda e, b=btn: on_leave(b))
    
    if is_pystray_available:
        tray_btn.bind("<Enter>", lambda e, b=tray_btn: on_enter(b))
        tray_btn.bind("<Leave>", lambda e, b=tray_btn: on_leave(b))
    
    return buttons_frame