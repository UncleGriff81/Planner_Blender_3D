"""
Панель основных кнопок
"""
import tkinter as tk


def create_buttons_panel(parent, theme, create_project, generate_reports, show_statistics, 
                         check_updates, toggle_startup, minimize_to_tray, is_pystray_available):
    """Создаёт панель с основными кнопками"""
    buttons_frame = tk.Frame(parent, bg=theme.get("bg_color"))
    buttons_frame.grid(row=3, column=0, columnspan=2, pady=(0, 15), sticky="we", padx=10)
    
    create_btn = tk.Button(buttons_frame, text="➕ Создать проект", font=("Arial", 11),
                           bg=theme.get("accent_color"), fg="white", relief="flat", command=create_project)
    create_btn.pack(side="left", padx=(0, 10))
    
    report_btn = tk.Button(buttons_frame, text="📊 Отчёт", font=("Arial", 10),
                           bg=theme.get("info_color"), fg="white", relief="flat", command=generate_reports)
    report_btn.pack(side="left", padx=5)
    
    stats_btn = tk.Button(buttons_frame, text="📊 Статистика", font=("Arial", 10),
                          bg=theme.get("accent_color"), fg="white", relief="flat", command=show_statistics)
    stats_btn.pack(side="left", padx=5)
    
    update_btn = tk.Button(buttons_frame, text="🔄 Проверить обновления", font=("Arial", 10),
                           bg=theme.get("accent_color"), fg="white", relief="flat", command=check_updates)
    update_btn.pack(side="left", padx=5)
    
    startup_btn = tk.Button(buttons_frame, text="⚙️ Автозагрузка", font=("Arial", 10),
                            bg=theme.get("accent_color"), fg="white", relief="flat", command=toggle_startup)
    startup_btn.pack(side="left", padx=5)
    
    # Кнопка свернуть в трей (всегда показываем, если библиотека доступна)
    if is_pystray_available:
        tray_btn = tk.Button(buttons_frame, text="📌 Свернуть в трей", font=("Arial", 10),
                             bg=theme.get("info_color"), fg="white", relief="flat", command=minimize_to_tray)
        tray_btn.pack(side="left", padx=5)
    
    return buttons_frame