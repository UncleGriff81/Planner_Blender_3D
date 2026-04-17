"""
UI Components - экспорт функций для создания фреймов проектов
"""
import tkinter as tk
import os
from frames.task_frame_header import create_header_frame
from frames.task_frame_timer import create_timer_frame
from frames.task_frame_info import create_info_frame
from frames.task_frame_buttons import create_action_buttons
from callbacks.timer_callbacks import start_timer_updates, start_deadline_updates, force_update
from callbacks.file_callbacks import create_blend_file, launch_blender
from callbacks.blender_callbacks import choose_blender_for_project, update_blender_info
from callbacks.deadline_callbacks import edit_deadline
from callbacks.report_callbacks import show_project_report
from notifications.timer_notification import show_timer_notification
from theme_manager import ThemeManager
from blender_process_monitor import get_process_monitor
from date_utils import get_deadline_color
from tkinter import messagebox

# Глобальные переменные
_projects_objects_list = None
_update_monitor_callback = None


def set_projects_list(projects_list):
    """Устанавливает глобальный список проектов"""
    global _projects_objects_list
    _projects_objects_list = projects_list


def set_update_monitor_callback(callback):
    """Устанавливает callback для обновления монитора"""
    global _update_monitor_callback
    _update_monitor_callback = callback


def delete_task_frame(project, proj_frame, file_path, monitor, task_frames_list, renumber_callback):
    """Удаляет фрейм проекта"""
    from db_manager import delete_project_from_db
    
    if messagebox.askyesno("Удалить", f"Удалить проект '{project.name}'?"):
        if file_path and os.path.exists(file_path):
            try:
                monitor.unregister_file(file_path)
            except:
                pass
        
        delete_project_from_db(project.id)
        proj_frame.destroy()
        
        if task_frames_list is not None and proj_frame in task_frames_list:
            try:
                task_frames_list.remove(proj_frame)
            except:
                pass
        
        global _projects_objects_list
        if _projects_objects_list is not None:
            for i, p in enumerate(_projects_objects_list):
                if p.id == project.id:
                    _projects_objects_list.pop(i)
                    break
        
        if _update_monitor_callback:
            _update_monitor_callback()
        
        if renumber_callback:
            renumber_callback()


def create_task_frame(parent_frame, project, task_frames_list=None, renumber_callback=None):
    """
    Создаёт фрейм проекта со всем интерфейсом
    """
    theme = ThemeManager()
    
    # Определяем цвет фона на основе дедлайна
    deadline_color = get_deadline_color(project.get_deadline_date_obj())
    if deadline_color == "red":
        frame_bg = "#8B0000"
    elif deadline_color == "yellow":
        frame_bg = "#B8860B"
    else:
        frame_bg = theme.get("frame_bg")
    
    # Основной фрейм
    proj_frame = tk.Frame(parent_frame, bg=frame_bg, bd=2, relief="groove", padx=15, pady=10)
    
    # Шапка
    header_frame, deadline_label, id_label = create_header_frame(proj_frame, frame_bg, theme, project, deadline_color)
    header_frame.pack(fill="x", pady=(0, 8))
    
    # Панель таймера (возвращает frame, label и label_var)
    timer_frame, timer_label, timer_label_var = create_timer_frame(proj_frame, frame_bg, theme, project)
    timer_frame.pack(fill="x", pady=(5, 5))
    
    # Информационная панель
    info_frame, blender_label = create_info_frame(proj_frame, frame_bg, theme, project)
    info_frame.pack(fill="x", pady=(8, 0))
    
    # Монитор процессов
    monitor = get_process_monitor()
    file_path = project.get_full_file_path()
    
    # Колбэки для файлового монитора
    def on_file_opened(file_path):
        print(f"[UI] Файл открыт, запускаем таймер для проекта {project.id}")
        project.start_timer()
        show_timer_notification("▶ Таймер запущен", theme.get("success_color"))
        force_update(project, proj_frame, header_frame, timer_frame, deadline_label, blender_label, theme)
    
    def on_file_closed(file_path):
        print(f"[UI] Файл закрыт, останавливаем таймер для проекта {project.id}")
        project.pause_timer()
        show_timer_notification("⏸ Таймер остановлен", theme.get("warning_color"))
        force_update(project, proj_frame, header_frame, timer_frame, deadline_label, blender_label, theme)
    
    # Регистрируем файл в мониторе, если он существует
    if file_path and os.path.exists(file_path):
        monitor.register_file(file_path, on_file_opened, on_file_closed)
    
    # Функция принудительного обновления UI
    def force_update_callback():
        force_update(project, proj_frame, header_frame, timer_frame, deadline_label, blender_label, theme)
    
    # Колбэк для создания файла
    def create_blend_file_callback():
        return create_blend_file(project, force_update_callback)
    
    # Колбэк для запуска Blender
    def launch_blender_callback():
        return launch_blender(project, monitor, on_file_opened, on_file_closed, create_blend_file_callback)
    
    # Колбэк для редактирования дедлайна
    def edit_deadline_callback():
        return edit_deadline(project, force_update_callback)
    
    # Колбэк для выбора версии Blender
    def choose_blender_callback():
        return choose_blender_for_project(project, 
                                          lambda: update_blender_info(project, blender_label, theme), 
                                          force_update_callback)
    
    # Колбэк для показа отчёта
    def show_report_callback():
        return show_project_report(project, task_frames_list, proj_frame, theme)
    
    # Колбэк для удаления проекта
    def delete_callback():
        delete_task_frame(project, proj_frame, file_path, monitor, task_frames_list, renumber_callback)
    
    # Создание кнопок управления
    create_action_buttons(
        timer_frame, theme,
        start_callback=project.start_timer,
        pause_callback=project.pause_timer,
        stop_callback=project.stop_timer,
        deadline_callback=edit_deadline_callback,
        report_callback=show_report_callback,
        blender_callback=choose_blender_callback,
        create_file_callback=create_blend_file_callback,
        launch_callback=launch_blender_callback,
        delete_callback=delete_callback
    )
    
    # Запуск циклов обновления таймера и дедлайна
    start_timer_updates(project, timer_label_var, timer_label, theme, parent_frame)
    start_deadline_updates(project, deadline_label, parent_frame)
    
    # Сохраняем callback для внешнего принудительного обновления
    project.update_ui_callback = force_update_callback
    
    return proj_frame