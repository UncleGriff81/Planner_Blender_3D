"""
Колбэки для редактирования дедлайна проекта
"""
import tkinter as tk
from tkinter import messagebox
import datetime
from date_utils import format_deadline, parse_deadline_date, create_calendar_window
from db_manager import update_project_deadline


def edit_deadline(project, force_update_callback):
    """Открывает диалог редактирования дедлайна"""
    theme = force_update_callback.__self__ if hasattr(force_update_callback, '__self__') else None
    if theme is None:
        from theme_manager import ThemeManager
        theme = ThemeManager()
    
    edit_window = tk.Toplevel()
    edit_window.title(f"Редактирование дедлайна: {project.name}")
    edit_window.configure(bg=theme.get("bg_color"))
    edit_window.transient()
    edit_window.grab_set()
    edit_window.geometry("450x320")
    
    edit_window.update_idletasks()
    x = (edit_window.winfo_screenwidth() // 2) - 225
    y = (edit_window.winfo_screenheight() // 2) - 160
    edit_window.geometry(f"450x320+{x}+{y}")
    
    main_frame = tk.Frame(edit_window, bg=theme.get("bg_color"))
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    tk.Label(main_frame, text="Установка срока выполнения", 
            font=("Arial", 12, "bold"),
            bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(pady=(0, 15))
    
    type_var = tk.StringVar(value="days" if project.deadline_days > 0 else "none")
    
    days_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    days_frame.pack(fill="x", pady=5)
    
    tk.Radiobutton(days_frame, text="Количество дней", variable=type_var, value="days",
                   bg=theme.get("bg_color"), fg=theme.get("fg_color"),
                   selectcolor=theme.get("bg_color")).pack(side="left", padx=5)
    
    days_spinbox = tk.Spinbox(days_frame, from_=1, to=365, width=10,
                               bg=theme.get("frame_bg"), fg=theme.get("fg_color"))
    days_spinbox.pack(side="left", padx=10)
    days_spinbox.delete(0, tk.END)
    days_spinbox.insert(0, str(project.deadline_days) if project.deadline_days > 0 else "7")
    
    date_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    date_frame.pack(fill="x", pady=10)
    
    tk.Radiobutton(date_frame, text="Конкретная дата", variable=type_var, value="date",
                   bg=theme.get("bg_color"), fg=theme.get("fg_color"),
                   selectcolor=theme.get("bg_color")).pack(side="left", padx=5)
    
    date_entry = tk.Entry(date_frame, width=15, font=("Arial", 10),
                          bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                          insertbackground=theme.get("fg_color"))
    date_entry.pack(side="left", padx=5)
    
    def show_calendar():
        create_calendar_window(date_entry, lambda date: date_entry.delete(0, tk.END) or date_entry.insert(0, date.strftime('%d.%m.%Y')))
    
    calendar_btn = tk.Button(date_frame, text="📅", width=3,
                             bg=theme.get("accent_color"), fg="white",
                             relief="flat", command=show_calendar)
    calendar_btn.pack(side="left", padx=2)
    
    current_date = project.get_deadline_date_obj()
    if current_date:
        date_entry.insert(0, current_date.strftime('%d.%m.%Y'))
    else:
        date_entry.insert(0, datetime.datetime.now().strftime('%d.%m.%Y'))
    
    # Радиокнопка "Без срока"
    none_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    none_frame.pack(fill="x", pady=5)
    
    tk.Radiobutton(none_frame, text="Без срока", variable=type_var, value="none",
                   bg=theme.get("bg_color"), fg=theme.get("fg_color"),
                   selectcolor=theme.get("bg_color")).pack(side="left", padx=5)
    
    def set_deadline():
        if type_var.get() == "none":
            project.deadline_date = ""
            project.deadline_days = 0
            update_project_deadline(project.id, "", 0)
            force_update_callback()
            messagebox.showinfo("Успех", "Дедлайн удалён")
            edit_window.destroy()
        elif type_var.get() == "days":
            days = int(days_spinbox.get())
            if days > 0:
                project.set_deadline_from_days(days)
                update_project_deadline(project.id, project.deadline_date, days)
                force_update_callback()
                messagebox.showinfo("Успех", f"Дедлайн установлен: {format_deadline(project.get_deadline_date_obj())}")
                edit_window.destroy()
        else:
            date_str = date_entry.get()
            deadline_date = parse_deadline_date(date_str)
            if deadline_date:
                project.set_deadline_from_date(deadline_date)
                update_project_deadline(project.id, project.deadline_date, project.deadline_days)
                force_update_callback()
                messagebox.showinfo("Успех", f"Дедлайн установлен: {format_deadline(project.get_deadline_date_obj())}")
                edit_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ")
    
    btn_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    btn_frame.pack(fill="x", pady=(20, 0))
    
    tk.Button(btn_frame, text="✅ Применить", command=set_deadline,
             bg=theme.get("success_color"), fg="white", relief="flat", width=12).pack(side="left", padx=5)
    tk.Button(btn_frame, text="❌ Отмена", command=edit_window.destroy,
             bg=theme.get("error_color"), fg="white", relief="flat", width=12).pack(side="right", padx=5)