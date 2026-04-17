import json
import os
import sys
import tkinter as tk
from path_utils import get_data_folder, load_config, save_config

class ThemeManager:
    """Управление темами оформления с возможностью выбора"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_all_themes()
            cls._instance._load_current_theme()
        return cls._instance
    
    def _get_themes_path(self):
        """Возвращает путь к themes.json (сначала ищет рядом с EXE, потом в папке-хранилище)"""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        local_themes = os.path.join(base_dir, "themes.json")
        if os.path.exists(local_themes):
            return local_themes
        
        data_folder = get_data_folder()
        data_themes = os.path.join(data_folder, "themes.json")
        if os.path.exists(data_themes):
            return data_themes
        
        if os.path.exists(local_themes):
            import shutil
            shutil.copy2(local_themes, data_themes)
            print(f"[THEMES] Скопирован themes.json в: {data_themes}")
            return data_themes
        
        return None
    
    def _load_all_themes(self):
        """Загружает все доступные темы из themes.json"""
        themes_path = self._get_themes_path()
        
        # Базовые темы на случай, если файл не найден
        default_themes = {
            "blender_orange": {
                "name": "Blender Оранжевая",
                "description": "В стиле Blender 3D — тёмно-серая с оранжевыми акцентами",
                "colors": {
                    "bg_color": "#282828",
                    "fg_color": "#f0f0f0",
                    "accent_color": "#ff8c00",
                    "success_color": "#7cb518",
                    "warning_color": "#ffb347",
                    "error_color": "#e63946",
                    "info_color": "#ff8c00",
                    "frame_bg": "#3c3c3c",
                    "button_hover": "#4a4a4a",
                    "timer_running_color": "#7cb518",
                    "timer_stopped_color": "#b0b0b0"
                }
            },
            "catppuccin_mocha": {
                "name": "Catppuccin Mocha",
                "description": "Тёмная, спокойная тема с пастельными акцентами",
                "colors": {
                    "bg_color": "#1e1e2e",
                    "fg_color": "#cdd6f4",
                    "accent_color": "#89b4fa",
                    "success_color": "#a6e3a1",
                    "warning_color": "#f9e2af",
                    "error_color": "#f38ba8",
                    "info_color": "#89b4fa",
                    "frame_bg": "#313244",
                    "button_hover": "#45475a",
                    "timer_running_color": "#a6e3a1",
                    "timer_stopped_color": "#cdd6f4"
                }
            },
            "dark_modern": {
                "name": "Тёмная Современная",
                "description": "Современная тёмная тема с неоновыми акцентами",
                "colors": {
                    "bg_color": "#0a0a0a",
                    "fg_color": "#e0e0e0",
                    "accent_color": "#00adb5",
                    "success_color": "#00ff9d",
                    "warning_color": "#ffb347",
                    "error_color": "#ff2e2e",
                    "info_color": "#00adb5",
                    "frame_bg": "#1a1a1a",
                    "button_hover": "#2a2a2a",
                    "timer_running_color": "#00ff9d",
                    "timer_stopped_color": "#888888"
                }
            },
            "light_clean": {
                "name": "Светлая Чистая",
                "description": "Светлая минималистичная тема для дневной работы",
                "colors": {
                    "bg_color": "#f5f5f5",
                    "fg_color": "#2d2d2d",
                    "accent_color": "#4a90e2",
                    "success_color": "#2ecc71",
                    "warning_color": "#f39c12",
                    "error_color": "#e74c3c",
                    "info_color": "#4a90e2",
                    "frame_bg": "#ffffff",
                    "button_hover": "#e0e0e0",
                    "timer_running_color": "#27ae60",
                    "timer_stopped_color": "#7f8d8d"
                }
            },
            "purple_night": {
                "name": "Фиолетовая Ночь",
                "description": "Фиолетовая ночная тема для творческой атмосферы",
                "colors": {
                    "bg_color": "#1a0b2e",
                    "fg_color": "#e0b0ff",
                    "accent_color": "#9b59b6",
                    "success_color": "#2ecc71",
                    "warning_color": "#f1c40f",
                    "error_color": "#e74c3c",
                    "info_color": "#9b59b6",
                    "frame_bg": "#2c1a4a",
                    "button_hover": "#3a2a5a",
                    "timer_running_color": "#2ecc71",
                    "timer_stopped_color": "#b07ce0"
                }
            }
        }
        
        if themes_path and os.path.exists(themes_path):
            try:
                with open(themes_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.all_themes = data.get('themes', default_themes)
                    self.default_theme = data.get('default_theme', 'blender_orange')
                print(f"[THEMES] Загружены темы из: {themes_path}")
            except Exception as e:
                print(f"[THEMES] Ошибка загрузки тем: {e}")
                self.all_themes = default_themes
                self.default_theme = 'blender_orange'
        else:
            print(f"[THEMES] Файл themes.json не найден, использую встроенные темы")
            self.all_themes = default_themes
            self.default_theme = 'blender_orange'
    
    def _load_current_theme(self):
        """Загружает выбранную тему из config.json"""
        config = load_config()
        self.current_theme_name = config.get('current_theme', 'blender_orange')
        self._apply_theme(self.current_theme_name)
    
    def _apply_theme(self, theme_name):
        """Применяет тему по имени"""
        if theme_name in self.all_themes:
            self.theme = self.all_themes[theme_name]['colors'].copy()
            self.current_theme_name = theme_name
        else:
            first_theme = list(self.all_themes.keys())[0]
            self.theme = self.all_themes[first_theme]['colors'].copy()
            self.current_theme_name = first_theme
    
    def get_available_themes(self):
        """Возвращает список доступных тем"""
        return {name: data['name'] for name, data in self.all_themes.items()}
    
    def set_theme(self, theme_name):
        """Устанавливает новую тему и сохраняет в config"""
        if theme_name in self.all_themes:
            self._apply_theme(theme_name)
            config = load_config()
            config['current_theme'] = self.current_theme_name
            save_config(config)
            return True
        return False
    
    def get(self, key, default=None):
        return self.theme.get(key, default)
    
    def refresh_ui(self, root, main_container, task_frames_list, top_panel, filter_frame, 
                   buttons_frame, theme_container, theme_frame, theme_dropdown, info_btn, developers_label,
                   refresh_projects_callback=None):
        """Обновляет цвета всех виджетов при смене темы"""
        bg_color = self.get("bg_color")
        fg_color = self.get("fg_color")
        accent_color = self.get("accent_color")
        frame_bg = self.get("frame_bg")
        
        # Обновляем корневое окно
        root.configure(bg=bg_color)
        
        # Обновляем main_container
        if main_container:
            main_container.configure(bg=bg_color)
        
        # Обновляем top_panel
        if top_panel:
            top_panel.configure(bg=bg_color)
            self._recursive_refresh(top_panel, bg_color, fg_color, accent_color, frame_bg)
        
        # Обновляем filter_frame
        if filter_frame:
            filter_frame.configure(bg=bg_color)
            self._recursive_refresh(filter_frame, bg_color, fg_color, accent_color, frame_bg)
        
        # Обновляем buttons_frame
        if buttons_frame:
            buttons_frame.configure(bg=bg_color)
            self._recursive_refresh(buttons_frame, bg_color, fg_color, accent_color, frame_bg)
        
        # Обновляем theme_container
        if theme_container:
            theme_container.configure(bg=bg_color)
            self._recursive_refresh(theme_container, bg_color, fg_color, accent_color, frame_bg)
        
        # Обновляем theme_frame
        if theme_frame:
            theme_frame.configure(bg=bg_color)
            self._recursive_refresh(theme_frame, bg_color, fg_color, accent_color, frame_bg)
        
        # Обновляем theme_dropdown
        if theme_dropdown:
            theme_dropdown.config(bg=accent_color, fg="white")
        
        # Обновляем info_btn
        if info_btn:
            info_btn.config(bg=accent_color, fg="white")
        
        # Обновляем developers_label
        if developers_label:
            developers_label.config(fg=accent_color)
        
        # Обновляем фреймы проектов
        for frame in task_frames_list:
            if frame:
                self._refresh_project_frame(frame, frame_bg, fg_color, accent_color)
        
        # Принудительно обновляем список проектов, если есть callback
        if refresh_projects_callback:
            refresh_projects_callback()
    
    def _refresh_project_frame(self, frame, frame_bg, fg_color, accent_color):
        """Обновляет цвета отдельного фрейма проекта и всех его внутренностей"""
        try:
            frame.configure(bg=frame_bg)
            
            for child in frame.winfo_children():
                # Определяем тип виджета и обновляем его
                if isinstance(child, tk.Frame):
                    child.configure(bg=frame_bg)
                    # Рекурсивно обновляем внутренности фрейма
                    for subchild in child.winfo_children():
                        self._refresh_widget(subchild, frame_bg, fg_color, accent_color)
                else:
                    self._refresh_widget(child, frame_bg, fg_color, accent_color)
        except:
            pass
    
    def _refresh_widget(self, widget, frame_bg, fg_color, accent_color):
        """Обновляет цвета отдельного виджета"""
        try:
            if isinstance(widget, tk.Label):
                text = widget.cget("text")
                # Не меняем цвет специальных элементов
                if text not in ["", "📁", "▶", "⏸", "⏹", "🎨", "💾", "🗑", "🔧"]:
                    if widget.cget("fg") not in ["gray", "lightgray", "orange", "white", "#FFD700"]:
                        widget.configure(fg=fg_color)
                widget.configure(bg=frame_bg)
                
            elif isinstance(widget, tk.Button):
                text = widget.cget("text")
                if "Начать" in text or "▶" in text:
                    widget.configure(bg=self.get("success_color"))
                elif "Пауза" in text or "⏸" in text:
                    widget.configure(bg=self.get("warning_color"))
                elif "Стоп" in text or "Удалить" in text or "⏹" in text or "🗑" in text:
                    widget.configure(bg=self.get("error_color"))
                elif "Открыть" in text or "🎨" in text:
                    widget.configure(bg=self.get("info_color"))
                elif "Сохранить" in text or "💾" in text:
                    widget.configure(bg=self.get("accent_color"))
                else:
                    widget.configure(bg=accent_color)
                widget.configure(fg="white", relief="flat")
                
        except:
            pass
    
    def _recursive_refresh(self, widget, bg_color, fg_color, accent_color, frame_bg):
        """Рекурсивно обновляет цвета виджета и всех его детей"""
        try:
            if isinstance(widget, tk.Frame):
                widget.configure(bg=frame_bg)
            elif isinstance(widget, tk.Label):
                current_fg = widget.cget("fg")
                current_text = widget.cget("text")
                if current_fg not in ["gray", "lightgray", "orange", "white"]:
                    if current_text not in ["", "📁", "▶", "⏸", "⏹", "🎨", "💾", "🗑", "🔧"]:
                        widget.configure(fg=fg_color)
                widget.configure(bg=frame_bg)
            elif isinstance(widget, tk.Button):
                text = widget.cget("text")
                if "Начать" in text or "▶" in text:
                    widget.configure(bg=self.get("success_color"))
                elif "Пауза" in text or "⏸" in text:
                    widget.configure(bg=self.get("warning_color"))
                elif "Стоп" in text or "Удалить" in text or "⏹" in text or "🗑" in text:
                    widget.configure(bg=self.get("error_color"))
                elif "Открыть" in text or "🎨" in text:
                    widget.configure(bg=self.get("info_color"))
                elif "Сохранить" in text or "💾" in text:
                    widget.configure(bg=self.get("accent_color"))
                else:
                    widget.configure(bg=accent_color)
                widget.configure(fg="white", relief="flat")
            elif isinstance(widget, tk.OptionMenu):
                widget.config(bg=accent_color, fg="white")
            elif isinstance(widget, tk.Checkbutton):
                widget.configure(bg=bg_color, fg=fg_color, selectcolor=bg_color)
            
            for child in widget.winfo_children():
                self._recursive_refresh(child, bg_color, fg_color, accent_color, frame_bg)
        except:
            pass