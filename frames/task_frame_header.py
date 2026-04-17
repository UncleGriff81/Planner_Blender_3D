"""
Шапка фрейма проекта (ID, имя, кнопка Подробнее, дедлайн, дата)
"""
import tkinter as tk
from date_utils import format_deadline, get_time_left_string
from tkinter import messagebox


def create_header_frame(parent, frame_bg, theme, project, deadline_color):
    """Создаёт шапку фрейма проекта"""
    header_frame = tk.Frame(parent, bg=frame_bg)
    
    id_label = tk.Label(header_frame, text=f"#{project.id}", font=("Arial", 12, "bold"),
                        bg=frame_bg, fg=theme.get("accent_color"))
    id_label.pack(side="left", padx=(0, 10))
    
    name_label = tk.Label(header_frame, text=f"📌 {project.name}", font=("Arial", 12),
                          bg=frame_bg, fg=theme.get("fg_color"))
    name_label.pack(side="left")
    
    def show_details():
        blender_ver = "Выбран" if project.blender_path else "Не выбран"
        if project.blender_path:
            for part in project.blender_path.split("/"):
                if 'Blender' in part and len(part) > 7:
                    blender_ver = part
                    break
        
        deadline_info = f"Дедлайн: {format_deadline(project.get_deadline_date_obj())}\n"
        deadline_info += f"Осталось: {get_time_left_string(project.get_deadline_date_obj())}"
        
        messagebox.showinfo("Подробности", 
                            f"ID: {project.id}\nНазвание: {project.name}\nОписание: {project.description}\n"
                            f"Файл: {project.blend_file}.blend\n"
                            f"Путь к файлу: {project.get_full_file_path() or 'Не создан'}\n"
                            f"Blender: {blender_ver}\n"
                            f"Дата создания: {project.creation_date}\n"
                            f"Затраченное время: {project.get_formatted_time()}\n"
                            f"{deadline_info}")
    
    details_btn = tk.Button(header_frame, text="📄 Подробнее", font=("Arial", 9),
                            bg=theme.get("accent_color"), fg="white",
                            relief="flat", command=show_details)
    details_btn.pack(side="left", padx=10)
    
    deadline_label = tk.Label(header_frame, 
                              text=get_time_left_string(project.get_deadline_date_obj()),
                              font=("Arial", 9, "bold"),
                              bg=frame_bg, 
                              fg="#FFD700" if deadline_color else "gray")
    deadline_label.pack(side="right", padx=10)
    
    date_label = tk.Label(header_frame, text=f"📅 {project.creation_date[:10]}", font=("Arial", 9),
                          bg=frame_bg, fg="gray")
    date_label.pack(side="right", padx=10)
    
    return header_frame, deadline_label, id_label