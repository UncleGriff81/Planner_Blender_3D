"""
theme_manager.py - Управление темами оформления
"""
import json
import os
import tkinter as tk  # <-- ДОБАВЛЯЕМ ЭТУ СТРОКУ!


class ThemeManager:
    """Менеджер тем оформления интерфейса"""
    
    def __init__(self):
        self.current_theme_name = "blender_orange"
        self.themes = self._load_themes()
        self._load_saved_theme()
    
    def _load_themes(self):
        """Загружает темы из themes.json"""
        themes_path = os.path.join(os.path.dirname(__file__), "themes.json")
        default_themes = {
            "blender_orange": {
                "name": "Blender Оранжевая",
                "bg_color": "#282828",
                "fg_color": "#f0f0f0",
                "accent_color": "#ff8c00",
                "success_color": "#7cb518",
                "error_color": "#e63946",
                "warning_color": "#ffb347",
                "info_color": "#ff8c00",
                "frame_bg": "#3c3c3c",
                "timer_running_color": "#7cb518",
                "timer_stopped_color": "#b0b0b0",
            },
            "dark_modern": {
                "name": "Тёмная Современная",
                "bg_color": "#0a0a0a",
                "fg_color": "#e0e0e0",
                "accent_color": "#00adb5",
                "success_color": "#00ff9d",
                "error_color": "#ff2e2e",
                "warning_color": "#ffb347",
                "info_color": "#00adb5",
                "frame_bg": "#1a1a1a",
                "timer_running_color": "#00ff9d",
                "timer_stopped_color": "#888888",
            },
            "light_clean": {
                "name": "Светлая Чистая",
                "bg_color": "#f5f5f5",
                "fg_color": "#2d2d2d",
                "accent_color": "#4a90e2",
                "success_color": "#2ecc71",
                "error_color": "#e74c3c",
                "warning_color": "#f39c12",
                "info_color": "#4a90e2",
                "frame_bg": "#ffffff",
                "timer_running_color": "#27ae60",
                "timer_stopped_color": "#7f8d8d",
            },
            "purple_night": {
                "name": "Фиолетовая Ночь",
                "bg_color": "#1a0b2e",
                "fg_color": "#e0b0ff",
                "accent_color": "#9b59b6",
                "success_color": "#2ecc71",
                "error_color": "#e74c3c",
                "warning_color": "#f1c40f",
                "info_color": "#9b59b6",
                "frame_bg": "#2c1a4a",
                "timer_running_color": "#2ecc71",
                "timer_stopped_color": "#b07ce0",
            },
            "catppuccin_mocha": {
                "name": "Catppuccin Mocha",
                "bg_color": "#1e1e2e",
                "fg_color": "#cdd6f4",
                "accent_color": "#89b4fa",
                "success_color": "#a6e3a1",
                "error_color": "#f38ba8",
                "warning_color": "#f9e2af",
                "info_color": "#89b4fa",
                "frame_bg": "#313244",
                "timer_running_color": "#a6e3a1",
                "timer_stopped_color": "#cdd6f4",
            }
        }
        
        if os.path.exists(themes_path):
            try:
                with open(themes_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "themes" in data:
                        for key, theme_data in data["themes"].items():
                            if "colors" in theme_data:
                                default_themes[key] = theme_data["colors"]
                                default_themes[key]["name"] = theme_data.get("name", key)
                    else:
                        default_themes.update(data)
            except:
                pass
        
        return default_themes
    
    def _load_saved_theme(self):
        """Загружает сохранённую тему из конфига"""
        try:
            from path_utils import load_config
            config = load_config()
            saved_theme = config.get("current_theme", "blender_orange")
            if saved_theme in self.themes:
                self.current_theme_name = saved_theme
        except:
            pass
    
    def save_theme(self):
        """Сохраняет текущую тему в конфиг"""
        try:
            from path_utils import load_config, save_config
            config = load_config()
            config["current_theme"] = self.current_theme_name
            save_config(config)
        except:
            pass
    
    def get_theme(self):
        """Возвращает словарь с настройками текущей темы"""
        return self.themes.get(self.current_theme_name, self.themes["blender_orange"])
    
    def get(self, key):
        """Возвращает конкретное значение темы"""
        theme = self.get_theme()
        return theme.get(key, "")
    
    def get_available_themes(self):
        """Возвращает словарь доступных тем {ключ: название}"""
        return {key: value.get("name", key) for key, value in self.themes.items()}
    
    def set_theme(self, theme_name):
        """Устанавливает тему по имени"""
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            self.save_theme()
            return True
        return False
    
    def refresh_ui(self, root, main_container, task_frames_list, top_panel, filter_frame,
                   buttons_frame, theme_container, theme_frame, theme_dropdown, info_btn,
                   developers_label, refresh_projects_callback=None):
        """Обновляет цвета всех виджетов при смене темы"""
        bg_color = self.get("bg_color")
        fg_color = self.get("fg_color")
        accent_color = self.get("accent_color")
        frame_bg = self.get("frame_bg")
        
        if root:
            root.configure(bg=bg_color)
        
        # Обновляем панели
        for widget in [main_container, top_panel, filter_frame, buttons_frame, theme_container, theme_frame]:
            if widget:
                widget.configure(bg=bg_color)
                self._recursive_refresh(widget, bg_color, fg_color, accent_color, frame_bg)
        
        # Обновляем dropdown и кнопки
        if theme_dropdown:
            theme_dropdown.config(bg=accent_color, fg="white")
        if info_btn:
            info_btn.config(bg=accent_color, fg="white")
        if developers_label:
            developers_label.config(fg=accent_color)
        
        # Обновляем фреймы проектов
        for frame in task_frames_list:
            if frame:
                self._refresh_project_frame(frame, frame_bg, fg_color, accent_color)
        
        if refresh_projects_callback:
            refresh_projects_callback()
    
    def _recursive_refresh(self, widget, bg_color, fg_color, accent_color, frame_bg):
        """Рекурсивно обновляет цвета виджета и его детей"""
        try:
            if isinstance(widget, tk.Label):
                current_bg = widget.cget("bg")
                if current_bg not in ("red", "#8B0000", "#B8860B", "orange"):
                    widget.configure(bg=bg_color)
                current_fg = widget.cget("fg")
                if current_fg != "gray":
                    widget.configure(fg=fg_color)
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=bg_color)
            elif isinstance(widget, tk.Text):
                widget.configure(bg=frame_bg, fg=fg_color)
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=frame_bg, fg=fg_color)
            elif isinstance(widget, tk.Listbox):
                widget.configure(bg=frame_bg, fg=fg_color)
        except:
            pass
        
        for child in widget.winfo_children():
            self._recursive_refresh(child, bg_color, fg_color, accent_color, frame_bg)
    
    def _refresh_project_frame(self, frame, frame_bg, fg_color, accent_color):
        """Обновляет цвета фрейма проекта"""
        try:
            deadline_color = None
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, tk.Label):
                            text = subchild.cget("text")
                            if text and text.startswith("#"):
                                deadline_color = subchild.cget("fg")
                                break
                if deadline_color:
                    break
            
            if deadline_color == "red":
                frame.configure(bg="#8B0000")
            elif deadline_color == "yellow":
                frame.configure(bg="#B8860B")
            else:
                frame.configure(bg=frame_bg)
            
            self._recursive_refresh(frame, frame.cget("bg"), fg_color, accent_color, frame_bg)
        except:
            pass