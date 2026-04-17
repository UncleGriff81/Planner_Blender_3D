"""
Обработчики отчётов
"""
import tkinter as tk
import subprocess
import sys
import os
import datetime
from path_utils import get_reports_folder


def generate_reports(root, theme, projects_objects_list, show_notification):
    """Генерирует общий отчёт и показывает окно с информацией"""
    from tkinter import messagebox
    from report_generator import generate_full_report
    
    if not projects_objects_list:
        messagebox.showwarning("Нет проектов", "Нет проектов для создания отчётов.")
        return
    
    try:
        show_notification("⏳ Генерация общего отчёта...", "info", 2000)
        
        report_path = generate_full_report(projects_objects_list)
        
        report_window = tk.Toplevel(root)
        report_window.title("Общий отчёт — Planner_Blender_3D")
        report_window.configure(bg=theme.get("bg_color"))
        report_window.geometry("750x650")
        report_window.transient(root)
        report_window.grab_set()
        
        report_window.update_idletasks()
        x = (report_window.winfo_screenwidth() // 2) - 375
        y = (report_window.winfo_screenheight() // 2) - 325
        report_window.geometry(f"750x650+{x}+{y}")
        
        main_frame = tk.Frame(report_window, bg=theme.get("bg_color"))
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="📊 ОБЩИЙ ОТЧЁТ ПО ВСЕМ ПРОЕКТАМ", 
                font=("Arial", 14, "bold"),
                bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(pady=(0, 10))
        
        tk.Label(main_frame, text=f"Дата генерации: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", 
                font=("Arial", 10),
                bg=theme.get("bg_color"), fg=theme.get("accent_color")).pack(pady=(0, 20))
        
        text_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
        text_frame.pack(fill="both", expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        info_text_widget = tk.Text(text_frame, wrap="word", 
                                   font=("Courier New", 10),
                                   bg=theme.get("frame_bg"), 
                                   fg=theme.get("fg_color"),
                                   yscrollcommand=scrollbar.set,
                                   relief="flat")
        info_text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=info_text_widget.yview)
        
        total_time = 0
        active_projects = 0
        overdue_projects = 0
        
        for project in projects_objects_list:
            total_seconds = project.get_total_seconds()
            total_time += total_seconds
            if project.timer_running:
                active_projects += 1
            deadline = project.get_deadline_date_obj()
            if deadline and deadline < datetime.datetime.now():
                overdue_projects += 1
        
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        
        info_text = f"""
ОБЩАЯ СТАТИСТИКА
{"-" * 68}

  Всего проектов:          {len(projects_objects_list)}
  Активных таймеров:        {active_projects}
  Общее время:             {hours} ч {minutes} мин ({total_time:.0f} сек)
  Просроченных проектов:    {overdue_projects}


ДЕТАЛИ ПО ПРОЕКТАМ
{"-" * 68}

"""
        for idx, project in enumerate(projects_objects_list, 1):
            deadline = project.get_deadline_date_obj()
            deadline_str = deadline.strftime('%d.%m.%Y') if deadline else "Не указан"
            proj_hours = int(project.get_total_seconds() // 3600)
            proj_minutes = int((project.get_total_seconds() % 3600) // 60)
            
            info_text += f"""
ПРОЕКТ #{idx} — {project.name}
{"-" * 40}
  ID в БД:          {project.id}
  Время:            {project.get_formatted_time()} ({proj_hours} ч {proj_minutes} мин)
  Дедлайн:          {deadline_str}
  Статус:           {'Активен' if project.timer_running else 'Остановлен'}
  Файл:             {project.blend_file}.blend

"""
        
        info_text += f"""
ИНФОРМАЦИЯ ОБ ОТЧЁТЕ
{"-" * 68}

  Полный отчёт сохранён в файл:
  {report_path}

{"=" * 68}
"""
        
        info_text_widget.insert("1.0", info_text)
        info_text_widget.config(state="disabled")
        
        btn_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
        btn_frame.pack(fill="x", pady=(20, 0))
        
        def open_txt_file():
            try:
                if os.path.exists(report_path):
                    if sys.platform == "win32":
                        os.startfile(report_path)
                    elif sys.platform == "darwin":
                        subprocess.run(["open", report_path])
                    else:
                        subprocess.run(["xdg-open", report_path])
                else:
                    messagebox.showerror("Ошибка", f"Файл отчёта не найден:\n{report_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
        
        def open_reports_folder():
            try:
                if sys.platform == "win32":
                    os.startfile(get_reports_folder())
                elif sys.platform == "darwin":
                    subprocess.run(["open", get_reports_folder()])
                else:
                    subprocess.run(["xdg-open", get_reports_folder()])
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть папку:\n{str(e)}")
        
        open_btn = tk.Button(btn_frame, text="📄 Открыть файл .txt", 
                            font=("Arial", 10),
                            bg=theme.get("info_color"), fg="white",
                            relief="flat", command=open_txt_file, padx=15, pady=5)
        open_btn.pack(side="left", padx=5)
        
        folder_btn = tk.Button(btn_frame, text="📁 Открыть папку с отчётами", 
                              font=("Arial", 10),
                              bg=theme.get("accent_color"), fg="white",
                              relief="flat", command=open_reports_folder, padx=15, pady=5)
        folder_btn.pack(side="left", padx=5)
        
        close_btn = tk.Button(btn_frame, text="❌ Закрыть", 
                             font=("Arial", 10),
                             bg=theme.get("error_color"), fg="white",
                             relief="flat", command=report_window.destroy, padx=15, pady=5)
        close_btn.pack(side="right", padx=5)
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось создать отчёт:\n{str(e)}")