"""
Обработчики проектов: сортировка, обновление, нумерация, поиск
"""
import tkinter as tk
from date_utils import get_deadline_color


def renumber_projects(task_frames_list):
    """Перенумеровывает отображаемые ID проектов"""
    for idx, frame in enumerate(task_frames_list, 1):
        for child in frame.winfo_children():
            if isinstance(child, tk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Label):
                        text = subchild.cget("text")
                        if text and text.startswith("#"):
                            subchild.config(text=f"#{idx}.")
                            break
                break


def filter_projects_by_search(projects, search_text):
    """Фильтрует проекты по поисковому запросу (название + описание)"""
    if not search_text or not search_text.strip():
        return projects
    
    search_lower = search_text.lower().strip()
    filtered = []
    for project in projects:
        if (search_lower in project.name.lower() or 
            search_lower in project.description.lower()):
            filtered.append(project)
    return filtered


def sort_projects(projects, sort_key, urgent_only=False, search_text=""):
    """Сортирует и фильтрует проекты"""
    # Сначала фильтруем по поиску
    projects = filter_projects_by_search(projects, search_text)
    
    # Потом фильтруем по срочности
    if urgent_only:
        filtered = []
        for p in projects:
            deadline_color = get_deadline_color(p.get_deadline_date_obj())
            if deadline_color in ("red", "yellow"):
                filtered.append(p)
        projects = filtered
    
    # Сортируем
    if sort_key == "date_desc":
        return sorted(projects, key=lambda p: p.creation_date, reverse=True)
    elif sort_key == "date_asc":
        return sorted(projects, key=lambda p: p.creation_date)
    elif sort_key == "deadline_asc":
        return sorted(projects, key=lambda p: p.deadline_date if p.deadline_date else "9999-12-31")
    elif sort_key == "deadline_desc":
        return sorted(projects, key=lambda p: p.deadline_date if p.deadline_date else "0000-01-01", reverse=True)
    elif sort_key == "name_asc":
        return sorted(projects, key=lambda p: p.name.lower())
    elif sort_key == "name_desc":
        return sorted(projects, key=lambda p: p.name.lower(), reverse=True)
    else:
        return projects


def refresh_projects_list(projects_inner_frame, projects_objects_list, task_frames_list,
                          sort_var, urgent_var, canvas, search_var, create_task_frame_func):
    """Обновляет список проектов в UI с учётом поиска"""
    if projects_inner_frame is None:
        return
    
    # Очищаем старые виджеты
    for widget in projects_inner_frame.winfo_children():
        widget.destroy()
    
    task_frames_list.clear()
    
    sort_key = sort_var.get() if sort_var else "deadline_asc"
    urgent = urgent_var.get() if urgent_var else False
    search_text = search_var.get() if search_var else ""
    
    sorted_projects = sort_projects(projects_objects_list, sort_key, urgent, search_text)
    
    for project in sorted_projects:
        task_frame = create_task_frame_func(projects_inner_frame, project, task_frames_list,
                                            lambda: renumber_projects(task_frames_list))
        task_frame.pack(fill="x", pady=(5, 5), padx=5)
        task_frames_list.append(task_frame)
    
    renumber_projects(task_frames_list)
    if canvas:
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))


def update_monitor_dict(projects_objects_list, PROJECTS_DICT_MONITOR):
    """Обновляет словарь для мониторинга файлов"""
    PROJECTS_DICT_MONITOR.clear()
    
    for proj in projects_objects_list:
        file_name_no_ext = proj.blend_file
        if file_name_no_ext.lower().endswith('.blend'):
            file_name_no_ext = file_name_no_ext[:-6]
        
        PROJECTS_DICT_MONITOR[file_name_no_ext] = proj
        PROJECTS_DICT_MONITOR[proj.id] = proj
        PROJECTS_DICT_MONITOR[proj.name] = proj
    
    import file_monitor
    file_monitor.PROJECTS_DICT = PROJECTS_DICT_MONITOR