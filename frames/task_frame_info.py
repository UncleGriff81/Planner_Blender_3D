"""
Информационная панель фрейма проекта (файл, версия Blender)
"""
import tkinter as tk
import os


def create_info_frame(parent, frame_bg, theme, project):
    """Создаёт информационную панель"""
    info_frame = tk.Frame(parent, bg=frame_bg)
    
    file_icon = tk.Label(info_frame, text="📁", font=("Arial", 10),
                         bg=frame_bg, fg="gray")
    file_icon.pack(side="left", padx=(0, 5))
    
    file_path_display = project.get_full_file_path() or f"{project.blend_file}.blend (не создан)"
    if len(file_path_display) > 70:
        file_path_display = "..." + file_path_display[-67:]
    
    file_label = tk.Label(info_frame, text=file_path_display, font=("Arial", 9),
                          bg=frame_bg, fg="lightgray")
    file_label.pack(side="left", padx=(0, 20))
    
    blender_icon = tk.Label(info_frame, text="🔧", font=("Arial", 10),
                            bg=frame_bg, fg="gray")
    blender_icon.pack(side="left", padx=(0, 5))
    
    if project.blender_path:
        path_parts = project.blender_path.split(os.sep)
        blender_display = "Blender: "
        for part in path_parts:
            if 'Blender' in part and len(part) > 7:
                blender_display += part
                break
        else:
            blender_display += os.path.basename(os.path.dirname(project.blender_path))
        blender_label = tk.Label(info_frame, text=blender_display, font=("Arial", 9),
                                 bg=frame_bg, fg=theme.get("success_color"))
    else:
        blender_label = tk.Label(info_frame, text="Blender: не выбран", font=("Arial", 9),
                                 bg=frame_bg, fg="orange")
    blender_label.pack(side="left")
    
    return info_frame, blender_label