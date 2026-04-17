"""
Колбэки для таймера проекта
"""
import os
from date_utils import get_deadline_color, get_time_left_string


def start_timer_updates(project, timer_label_var, timer_label, theme, parent_frame):
    """Запускает цикл обновления таймера (бесконечный)"""
    def update():
        try:
            if project:
                timer_label_var.set(project.get_formatted_time())
                if project.timer_running:
                    timer_label.config(fg=theme.get("timer_running_color"))
                else:
                    timer_label.config(fg=theme.get("timer_stopped_color"))
            parent_frame.after(1000, update)
        except:
            parent_frame.after(1000, update)
    
    update()


def start_deadline_updates(project, deadline_label, parent_frame):
    """Запускает цикл обновления дедлайна (бесконечный)"""
    def update():
        try:
            if project:
                deadline_label.config(text=get_time_left_string(project.get_deadline_date_obj()))
            parent_frame.after(1000, update)
        except:
            parent_frame.after(1000, update)
    
    update()


def force_update(project, proj_frame, header_frame, timer_frame, deadline_label, blender_label, theme):
    """Принудительно обновляет UI проекта (цвета, статус, информацию)"""
    try:
        deadline_color = get_deadline_color(project.get_deadline_date_obj())
        if deadline_color == "red":
            new_bg = "#8B0000"
        elif deadline_color == "yellow":
            new_bg = "#B8860B"
        else:
            new_bg = theme.get("frame_bg")
        
        proj_frame.configure(bg=new_bg)
        header_frame.configure(bg=new_bg)
        timer_frame.configure(bg=new_bg)
        deadline_label.configure(fg="#FFD700" if deadline_color else "gray")
        
        # Обновление информации о Blender
        if project.blender_path:
            path_parts = project.blender_path.split(os.sep)
            blender_display = "Blender: "
            for part in path_parts:
                if 'Blender' in part and len(part) > 7:
                    blender_display += part
                    break
            else:
                blender_display += os.path.basename(os.path.dirname(project.blender_path))
            blender_label.config(text=blender_display, fg=theme.get("success_color"))
        else:
            blender_label.config(text="Blender: не выбран", fg="orange")
    except:
        pass