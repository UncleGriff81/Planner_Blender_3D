"""
Утилиты для работы с датами и сроками проектов
"""
import datetime
from datetime import timedelta
import calendar
import tkinter as tk


def get_deadline_color(deadline_date):
    """
    Возвращает цвет для строки проекта на основе дедлайна
    """
    if not deadline_date:
        return None
    
    now = datetime.datetime.now()
    time_left = deadline_date - now
    
    if time_left.total_seconds() <= 24 * 3600:
        return "red"
    elif time_left.total_seconds() <= 48 * 3600:
        return "yellow"
    else:
        return None


def calculate_deadline_from_days(days):
    """Рассчитывает дату дедлайна из количества дней"""
    if days is None or days <= 0:
        return None
    return datetime.datetime.now() + timedelta(days=days)


def format_deadline(deadline_date):
    """Форматирует дату дедлайна для отображения"""
    if not deadline_date:
        return "Не указан"
    return deadline_date.strftime('%d.%m.%Y %H:%M')


def parse_deadline_date(date_str):
    """Парсит дату из строки в формате ДД.ММ.ГГГГ"""
    try:
        return datetime.datetime.strptime(date_str, '%d.%m.%Y')
    except ValueError:
        return None


def get_time_left_string(deadline_date):
    """Возвращает строку с оставшимся временем"""
    if not deadline_date:
        return ""
    
    now = datetime.datetime.now()
    time_left = deadline_date - now
    
    if time_left.total_seconds() < 0:
        return "❗ Просрочен"
    
    days = time_left.days
    hours = time_left.seconds // 3600
    minutes = (time_left.seconds % 3600) // 60
    
    if days > 0:
        return f"⏰ {days}д {hours}ч"
    elif hours > 0:
        return f"⏰ {hours}ч {minutes}м"
    else:
        return f"⏰ {minutes}м"


def create_calendar_window(parent, callback):
    """Создаёт окно с календарём для выбора даты"""
    
    # Определяем цветовую тему
    try:
        bg_color = parent.winfo_toplevel().cget("bg")
        accent_color = parent.winfo_topleplevel().cget("accent_color") if hasattr(parent.winfo_toplevel(), 'cget') else "#4a4a4a"
        error_color = parent.winfo_toplevel().cget("error_color") if hasattr(parent.winfo_toplevel(), 'cget') else "#c62828"
    except:
        bg_color = "#282828"
        accent_color = "#ff8c00"
        error_color = "#e63946"
    
    calendar_window = tk.Toplevel(parent)
    calendar_window.title("Выберите дату")
    calendar_window.configure(bg=bg_color)
    calendar_window.transient(parent)
    calendar_window.grab_set()
    calendar_window.geometry("300x280")
    
    # Центрируем окно
    calendar_window.update_idletasks()
    x = (calendar_window.winfo_screenwidth() // 2) - 150
    y = (calendar_window.winfo_screenheight() // 2) - 140
    calendar_window.geometry(f"300x280+{x}+{y}")
    
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month
    
    year_var = tk.IntVar(value=current_year)
    month_var = tk.IntVar(value=current_month)
    
    days_frame = None
    
    def update_calendar():
        nonlocal days_frame
        if days_frame:
            for widget in days_frame.winfo_children():
                widget.destroy()
        else:
            days_frame = tk.Frame(calendar_window, bg=bg_color)
            days_frame.pack(pady=10)
        
        year = year_var.get()
        month = month_var.get()
        
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(weekdays):
            tk.Label(days_frame, text=day, font=("Arial", 9, "bold"),
                    bg=bg_color, fg="gray").grid(row=0, column=i, padx=2, pady=2)
        
        cal = calendar.monthcalendar(year, month)
        
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue
                
                btn = tk.Button(days_frame, text=str(day), width=4, height=1,
                               bg=bg_color, fg="white",
                               relief="flat", command=lambda d=day: select_date(year, month, d))
                btn.grid(row=week_idx + 1, column=day_idx, padx=2, pady=2)
    
    def select_date(year, month, day):
        selected_date = datetime.datetime(year, month, day)
        callback(selected_date)
        calendar_window.destroy()
    
    control_frame = tk.Frame(calendar_window, bg=bg_color)
    control_frame.pack(pady=10)
    
    tk.Button(control_frame, text="◀", command=lambda: month_var.set(month_var.get() - 1 if month_var.get() > 1 else 12),
             bg=bg_color, fg="white", relief="flat").pack(side="left", padx=5)
    
    month_spinbox = tk.Spinbox(control_frame, from_=1, to=12, width=5, textvariable=month_var,
                               bg=bg_color, fg="white",
                               buttonbackground=bg_color)
    month_spinbox.pack(side="left", padx=5)
    
    year_spinbox = tk.Spinbox(control_frame, from_=2000, to=2100, width=6, textvariable=year_var,
                              bg=bg_color, fg="white",
                              buttonbackground=bg_color)
    year_spinbox.pack(side="left", padx=5)
    
    tk.Button(control_frame, text="▶", command=lambda: month_var.set(month_var.get() + 1 if month_var.get() < 12 else 1),
             bg=bg_color, fg="white", relief="flat").pack(side="left", padx=5)
    
    days_frame = tk.Frame(calendar_window, bg=bg_color)
    days_frame.pack(pady=10)
    
    month_var.trace_add("write", lambda *args: update_calendar())
    year_var.trace_add("write", lambda *args: update_calendar())
    
    update_calendar()
    
    today_btn = tk.Button(calendar_window, text="Сегодня", command=lambda: select_date(now.year, now.month, now.day),
                         bg=accent_color, fg="white", relief="flat")
    today_btn.pack(pady=5)
    
    cancel_btn = tk.Button(calendar_window, text="Отмена", command=calendar_window.destroy,
                          bg=error_color, fg="white", relief="flat")
    cancel_btn.pack(pady=5)


def show_notification(message, color="success", duration=2000):
    """
    Показывает временное всплывающее уведомление.
    Эта функция должна вызываться из main.py с переданным root-окном.
    """
    try:
        root = tk._default_root
        if root is None:
            print(f"[NOTIFICATION] {message}")
            return
        
        # Определяем цвета (если есть тема)
        try:
            from theme_manager import ThemeManager
            theme = ThemeManager()
            if color == "success":
                bg_color = theme.get("success_color")
            elif color == "warning":
                bg_color = theme.get("warning_color")
            elif color == "error":
                bg_color = theme.get("error_color")
            elif color == "info":
                bg_color = theme.get("info_color")
            else:
                bg_color = theme.get("accent_color")
        except:
            # Цвета по умолчанию
            colors = {
                "success": "#7cb518",
                "warning": "#ffb347",
                "error": "#e63946",
                "info": "#ff8c00"
            }
            bg_color = colors.get(color, "#ff8c00")
        
        notification = tk.Toplevel(root)
        notification.title("Planner_Blender_3D")
        notification.configure(bg=bg_color)
        notification.overrideredirect(True)
        notification.attributes('-topmost', True)
        
        notification.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() // 2) - 200
        y = root.winfo_y() + (root.winfo_height() // 2) - 40
        notification.geometry(f"400x80+{x}+{y}")
        
        icon = "✅"
        if color == "warning":
            icon = "⚠️"
        elif color == "error":
            icon = "❌"
        elif color == "info":
            icon = "ℹ️"
        
        tk.Label(notification, text=f"{icon} {message}", 
                font=("Arial", 12, "bold"),
                bg=bg_color, 
                fg="white").pack(expand=True, pady=20)
        
        notification.after(duration, notification.destroy)
    except Exception as e:
        print(f"[NOTIFICATION ERROR] {e}")
        print(f"[NOTIFICATION] {message}")