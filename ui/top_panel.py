"""
Верхняя панель с логотипом, версией и ссылкой "Разработчикам"
"""
import tkinter as tk
import os


def create_top_panel(parent, root, theme, feedback_callback, current_version):
    """Создаёт верхнюю панель"""
    top_panel = tk.Frame(parent, bg=theme.get("bg_color"))
    
    # Левый угол (Создано BDV и версия)
    corner_frame = tk.Frame(top_panel, bg=theme.get("bg_color"))
    corner_frame.pack(side="left", anchor="nw", padx=(10, 0))
    
    bdv_label = tk.Label(corner_frame, text="Создано BDV", font=("Arial", 8), 
                         bg=theme.get("bg_color"), fg="gray")
    bdv_label.pack(side="left")
    
    version_label = tk.Label(corner_frame, text=f"  v{current_version}", font=("Arial", 8), 
                             bg=theme.get("bg_color"), fg="gray")
    version_label.pack(side="left")
    
    # Правый угол (Разработчикам)
    right_corner_frame = tk.Frame(top_panel, bg=theme.get("bg_color"))
    right_corner_frame.pack(side="right", anchor="ne", padx=(0, 10))
    
    developers_label = tk.Label(
        right_corner_frame, 
        text="Разработчикам", 
        font=("Arial", 8, "underline"), 
        bg=theme.get("bg_color"), 
        fg=theme.get("accent_color"),
        cursor="hand2"
    )
    developers_label.pack(side="right")
    developers_label.bind("<Button-1>", lambda e: feedback_callback())
    
    def on_enter(event):
        developers_label.config(fg=theme.get("info_color"))
    
    def on_leave(event):
        developers_label.config(fg=theme.get("accent_color"))
    
    developers_label.bind("<Enter>", on_enter)
    developers_label.bind("<Leave>", on_leave)
    
    # Левая панель с логотипом
    left_frame = tk.Frame(top_panel, bg=theme.get("bg_color"))
    left_frame.pack(side="left", padx=(20, 0), pady=(20, 0))
    
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logo.png")
    logo_loaded = False
    
    if os.path.exists(logo_path):
        try:
            from PIL import Image, ImageTk
            PIL_AVAILABLE = True
        except:
            PIL_AVAILABLE = False
        
        if PIL_AVAILABLE:
            try:
                logo_image = Image.open(logo_path)
                new_height = 120
                new_width = int(logo_image.width * new_height / logo_image.height)
                logo_image = logo_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = tk.Label(left_frame, image=logo_photo, bg=theme.get("bg_color"))
                logo_label.image = logo_photo
                logo_label.pack(side="top")
                logo_loaded = True
            except:
                pass
    
    if not logo_loaded:
        title_label = tk.Label(left_frame, text="Planner_Blender_3D", font=("Arial", 18, "bold"), 
                               bg=theme.get("bg_color"), fg=theme.get("fg_color"))
        title_label.pack(side="top")
    
    return top_panel