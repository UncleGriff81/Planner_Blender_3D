"""
Выбор темы оформления
"""
import tkinter as tk
from theme_manager import ThemeManager


def create_theme_selector(parent, theme, theme_manager, refresh_ui_callback):
    """Создаёт панель выбора темы"""
    theme_frame = tk.Frame(parent, bg=theme.get("bg_color"))
    
    theme_label = tk.Label(theme_frame, text="Тема:", font=("Arial", 10), 
                           bg=theme.get("bg_color"), fg=theme.get("fg_color"))
    theme_label.pack(side="left", padx=(0, 5))
    
    available_themes = theme_manager.get_available_themes()
    theme_var = tk.StringVar(value=theme_manager.current_theme_name)
    
    def change_theme(theme_name):
        if theme_manager.set_theme(theme_name):
            refresh_ui_callback()
            theme_var.set(theme_name)
    
    theme_dropdown = tk.OptionMenu(theme_frame, theme_var, *available_themes.keys(), command=change_theme)
    theme_dropdown.config(bg=theme.get("accent_color"), fg="white", relief="flat", 
                          font=("Arial", 9), width=18)
    theme_dropdown.pack(side="left")
    
    def show_themes_info():
        from tkinter import messagebox
        info_text = "Доступно 5 тем:\n"
        for key, name in available_themes.items():
            info_text += f"• {name}\n"
        messagebox.showinfo("Темы", info_text)
    
    info_btn = tk.Button(theme_frame, text="ℹ️", font=("Arial", 10, "bold"),
                         bg=theme.get("accent_color"), fg="white", relief="flat", command=show_themes_info)
    info_btn.pack(side="left", padx=(5, 0))
    
    # Находим метку "Разработчикам"
    developers_label = None
    def find_developers_label(widget):
        for child in widget.winfo_children():
            if isinstance(child, tk.Label) and child.cget("text") == "Разработчикам":
                return child
            result = find_developers_label(child)
            if result:
                return result
        return None
    
    root = parent.winfo_toplevel()
    developers_label = find_developers_label(root)
    
    return theme_frame, theme_dropdown, info_btn, developers_label