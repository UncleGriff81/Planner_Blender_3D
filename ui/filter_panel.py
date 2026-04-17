"""
Панель фильтрации и сортировки
"""
import tkinter as tk


def create_filter_panel(parent, theme, refresh_callback):
    """Создаёт панель с сортировкой и фильтрацией"""
    filter_frame = tk.Frame(parent, bg=theme.get("bg_color"))
    filter_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky="ew", padx=10)
    
    sort_label = tk.Label(filter_frame, text="Сортировка:", font=("Arial", 10), 
                          bg=theme.get("bg_color"), fg=theme.get("fg_color"))
    sort_label.pack(side="left", padx=(0, 10))
    
    sort_var = tk.StringVar(value="deadline_asc")
    sort_options = [
        ("📅 По дате создания (новые)", "date_desc"),
        ("📅 По дате создания (старые)", "date_asc"),
        ("⏰ По сроку (ближайшие)", "deadline_asc"),
        ("⏰ По сроку (дальние)", "deadline_desc"),
        ("🔤 По названию (А-Я)", "name_asc"),
        ("🔤 По названию (Я-А)", "name_desc"),
    ]
    
    sort_menu = tk.OptionMenu(filter_frame, sort_var, *[opt[1] for opt in sort_options], 
                              command=lambda x: refresh_callback())
    sort_menu.config(bg=theme.get("accent_color"), fg="white", relief="flat", 
                     font=("Arial", 9), width=20)
    sort_menu.pack(side="left", padx=(0, 20))
    
    urgent_var = tk.BooleanVar(value=False)
    urgent_check = tk.Checkbutton(filter_frame, text="Показать срочные проекты (менее 48 часов)",
                                  variable=urgent_var, command=lambda: refresh_callback(),
                                  bg=theme.get("bg_color"), fg=theme.get("fg_color"), 
                                  selectcolor=theme.get("bg_color"))
    urgent_check.pack(side="left", padx=(0, 20))
    
    refresh_btn = tk.Button(filter_frame, text="🔄 Обновить", command=refresh_callback,
                            bg=theme.get("info_color"), fg="white", relief="flat", font=("Arial", 9))
    refresh_btn.pack(side="right")
    
    return filter_frame, sort_var, urgent_var