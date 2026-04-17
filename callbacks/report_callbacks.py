"""
Колбэки для отображения отчётов по проектам
"""
import tkinter as tk
import subprocess
import sys
import os
from tkinter import messagebox
from report_generator import generate_project_report
from db_manager import get_daily_stats
from date_utils import format_deadline, get_time_left_string
from path_utils import get_reports_folder


def show_project_report(project, task_frames_list, proj_frame, theme):
    """Показывает окно с отчётом по проекту и кнопкой открытия файла"""
    try:
        # Находим текущий номер проекта в списке
        display_number = None
        if task_frames_list is not None:
            for idx, frame in enumerate(task_frames_list, 1):
                if frame == proj_frame:
                    display_number = idx
                    break
        
        if display_number is None:
            display_number = project.id
        
        report_path = generate_project_report(project, display_number)
        daily_stats = get_daily_stats(project.id)
        
        report_window = tk.Toplevel()
        report_window.title(f"Отчёт по проекту #{display_number} — {project.name}")
        report_window.configure(bg=theme.get("bg_color"))
        report_window.geometry("700x650")
        report_window.transient()
        report_window.grab_set()
        
        report_window.update_idletasks()
        x = (report_window.winfo_screenwidth() // 2) - 350
        y = (report_window.winfo_screenheight() // 2) - 325
        report_window.geometry(f"700x650+{x}+{y}")
        
        main_frame = tk.Frame(report_window, bg=theme.get("bg_color"))
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text=f"📊 Отчёт по проекту #{display_number}", 
                font=("Arial", 14, "bold"),
                bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(pady=(0, 10))
        
        tk.Label(main_frame, text=f"{project.name}", 
                font=("Arial", 12),
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
        
        total_seconds = project.get_total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        deadline = project.get_deadline_date_obj()
        deadline_str = format_deadline(deadline) if deadline else "Не указан"
        time_left_str = get_time_left_string(deadline) if deadline else "Не указан"
        
        blender_display = os.path.basename(os.path.dirname(project.blender_path)) if project.blender_path else "Не выбран"
        
        info_text = f"""
ОСНОВНАЯ ИНФОРМАЦИЯ
{"-" * 68}

  Номер в списке:     {display_number}
  ID в БД:            {project.id}
  Название:           {project.name}
  Дата создания:      {project.creation_date}


ВРЕМЯ
{"-" * 68}

  Затрачено времени:  {project.get_formatted_time()}
  Всего секунд:       {total_seconds:.0f} сек
  В часах/минутах:    {hours} ч {minutes} мин {seconds} сек
  Статус таймера:     {'Активен' if project.timer_running else 'Остановлен'}


ДЕДЛАЙН
{"-" * 68}

  Дедлайн:            {deadline_str}
  Осталось:           {time_left_str}


ФАЙЛЫ
{"-" * 68}

  Имя файла:          {project.blend_file}.blend
  Полный путь:        {project.get_full_file_path() or 'Не создан'}


BLENDER
{"-" * 68}

  Версия Blender:     {blender_display}
  Путь:               {project.blender_path or 'Не выбран'}


ДНЕВНАЯ СТАТИСТИКА
{"-" * 68}

"""
        if daily_stats:
            info_text += "  Дата         Время (чч:мм)   Сеансов\n"
            info_text += "  " + "-" * 50 + "\n"
            for stat in daily_stats:
                day = stat['day']
                duration_seconds = stat['total_duration']
                dur_hours = int(duration_seconds // 3600)
                dur_minutes = int((duration_seconds % 3600) // 60)
                sessions = stat['sessions_count']
                info_text += f"  {day}   {dur_hours:02d}:{dur_minutes:02d}          {sessions}\n"
        else:
            info_text += "  Нет записей о сеансах работы\n"
        
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