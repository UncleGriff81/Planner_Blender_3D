"""
Панель таймера фрейма проекта
"""
import tkinter as tk


def create_timer_frame(parent, frame_bg, theme, project):
    """Создаёт панель с таймером и возвращает все необходимые элементы"""
    timer_frame = tk.Frame(parent, bg=frame_bg)
    
    timer_label_var = tk.StringVar(value=project.get_formatted_time())
    
    timer_label = tk.Label(timer_frame, textvariable=timer_label_var,
                          font=("Courier New", 16, "bold"),
                          bg=frame_bg,
                          fg=theme.get("timer_running_color") if project.timer_running else theme.get("timer_stopped_color"))
    timer_label.pack(side="left", padx=15)
    
    return timer_frame, timer_label, timer_label_var