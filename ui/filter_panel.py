"""
Панель фильтрации и сортировки
"""
import tkinter as tk


class ToolTip:
    """Всплывающая подсказка для виджетов"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind('<Enter>', self.show_tip)
        widget.bind('<Leave>', self.hide_tip)
    
    def show_tip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Arial", 9))
        label.pack()
    
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def create_filter_panel(parent, theme, refresh_callback, search_callback=None):
    """Создаёт панель с сортировкой, фильтрацией и поиском"""
    bg_color = theme.get("bg_color")
    accent_color = theme.get("accent_color")
    fg_color = theme.get("fg_color")
    frame_bg = theme.get("frame_bg")
    
    filter_frame = tk.Frame(parent, bg=bg_color)
    filter_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10)
    
    # ===== РАЗДЕЛИТЕЛЬНАЯ ПОЛОСА =====
    top_separator = tk.Frame(filter_frame, height=2, bg=accent_color)
    top_separator.pack(fill="x", pady=(0, 10))
    
    # ===== КОНТЕЙНЕР ДЛЯ СОДЕРЖИМОГО =====
    content_frame = tk.Frame(filter_frame, bg=bg_color)
    content_frame.pack(fill="x")
    
    # ===== ЛЕВАЯ ЧАСТЬ: Сортировка и галочка =====
    left_frame = tk.Frame(content_frame, bg=bg_color)
    left_frame.pack(side="left")
    
    sort_label = tk.Label(left_frame, text="Сортировка:", font=("Arial", 10),
                          bg=bg_color, fg=fg_color)
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
    
    sort_menu = tk.OptionMenu(left_frame, sort_var, *[opt[1] for opt in sort_options],
                              command=lambda x: refresh_callback())
    sort_menu.config(bg=accent_color, fg="white", relief="flat",
                     font=("Arial", 9), width=20)
    sort_menu.pack(side="left", padx=(0, 20))
    
    urgent_var = tk.BooleanVar(value=False)
    urgent_check = tk.Checkbutton(left_frame, variable=urgent_var, command=refresh_callback,
                                  bg=bg_color, fg=fg_color,
                                  selectcolor=bg_color)
    urgent_check.pack(side="left", padx=(0, 5))
    
    ToolTip(urgent_check, "Показать только проекты с дедлайном менее 48 часов")
    
    # ===== ЦЕНТР: Кнопка обновления =====
    center_frame = tk.Frame(content_frame, bg=bg_color)
    center_frame.pack(side="left", expand=True)
    
    refresh_btn = tk.Button(center_frame, text="🔄 Обновить", command=refresh_callback,
                            bg=bg_color, fg=accent_color, relief="solid", bd=1,
                            font=("Arial", 9), padx=15)
    refresh_btn.pack()
    
    def on_enter_btn(btn):
        btn.config(bg=accent_color, fg=bg_color)
    
    def on_leave_btn(btn):
        btn.config(bg=bg_color, fg=accent_color)
    
    refresh_btn.bind("<Enter>", lambda e, b=refresh_btn: on_enter_btn(b))
    refresh_btn.bind("<Leave>", lambda e, b=refresh_btn: on_leave_btn(b))
    
    # ===== ПРАВАЯ ЧАСТЬ: Поиск =====
    right_frame = tk.Frame(content_frame, bg=bg_color)
    right_frame.pack(side="right")
    
    search_frame = tk.Frame(right_frame, bg=bg_color)
    search_frame.pack()
    
    tk.Label(search_frame, text="🔍 Поиск:", font=("Arial", 10),
             bg=bg_color, fg=fg_color).pack(side="left", padx=(0, 5))
    
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Arial", 10),
                            bg=frame_bg, fg=fg_color,
                            insertbackground=fg_color, width=25)
    search_entry.pack(side="left", padx=(0, 5))
    
    def on_search(*args):
        if search_callback:
            search_callback(search_var.get())
    
    search_var.trace_add("write", on_search)
    
    def clear_search():
        search_var.set("")
        search_entry.focus()
    
    clear_btn = tk.Button(search_frame, text="Очистить", font=("Arial", 9),
                          bg=bg_color, fg=accent_color, relief="solid", bd=1,
                          command=clear_search)
    clear_btn.pack(side="left")
    
    clear_btn.bind("<Enter>", lambda e, b=clear_btn: on_enter_btn(b))
    clear_btn.bind("<Leave>", lambda e, b=clear_btn: on_leave_btn(b))
    
    ToolTip(search_entry, "Поиск по названию и описанию проекта")
    
    return filter_frame, sort_var, urgent_var, search_var