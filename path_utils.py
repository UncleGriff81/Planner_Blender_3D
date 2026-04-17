"""
Утилиты для корректной работы с путями в собранном EXE
"""
import os
import sys
import json
import tkinter as tk
from tkinter import filedialog, messagebox

_DATA_FOLDER_PATH = None
_FIRST_RUN_CHECK = None

def get_first_run_flag_path():
    """Возвращает путь к файлу-флагу первого запуска"""
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, ".first_run_done")

def is_first_run():
    """Проверяет, первый ли это запуск программы"""
    global _FIRST_RUN_CHECK
    if _FIRST_RUN_CHECK is not None:
        return _FIRST_RUN_CHECK
    
    flag_file = get_first_run_flag_path()
    _FIRST_RUN_CHECK = not os.path.exists(flag_file)
    return _FIRST_RUN_CHECK

def mark_first_run_done():
    """Отмечает, что первый запуск завершён"""
    flag_file = get_first_run_flag_path()
    try:
        with open(flag_file, 'w') as f:
            f.write("done")
        print(f"[DATA] Первый запуск завершён, создан флаг: {flag_file}")
    except:
        pass

def ask_for_data_folder():
    """Запрашивает у пользователя папку для хранения данных"""
    temp_root = tk.Tk()
    temp_root.withdraw()
    
    messagebox.showinfo(
        "Добро пожаловать!",
        "Перед началом работы выберите папку,\n"
        "где будут храниться все данные программы:\n"
        "• База данных проектов\n"
        "• Отчёты\n"
        "• Настройки\n\n"
        "Рекомендуется выбрать папку в 'Документах'."
    )
    
    folder = filedialog.askdirectory(
        title="Выберите папку для хранения данных Planner_Blender_3D",
        initialdir=os.path.expanduser("~/Documents"),
        parent=temp_root
    )
    
    temp_root.destroy()
    
    if not folder:
        folder = os.path.expanduser("~/Documents/PlannerBlenderData")
        messagebox.showinfo(
            "Папка по умолчанию",
            f"Будет использована папка:\n{folder}"
        )
    
    os.makedirs(folder, exist_ok=True)
    
    config_path = os.path.join(folder, "config.json")
    config = {
        "data_folder": folder,
        "auto_save_interval": 30,
        "current_theme": "blender_orange",
        "tray_configured": True,
        "first_run_complete": True
    }
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    mark_first_run_done()
    
    return folder

def get_data_folder():
    """Возвращает путь к папке-хранилищу"""
    global _DATA_FOLDER_PATH
    
    if _DATA_FOLDER_PATH:
        return _DATA_FOLDER_PATH
    
    if is_first_run():
        _DATA_FOLDER_PATH = ask_for_data_folder()
        return _DATA_FOLDER_PATH
    
    possible_paths = [
        os.path.expanduser("~/Documents/PlannerBlenderData"),
        os.path.expanduser("~/PlannerBlenderData"),
        os.path.expanduser("~/Desktop/PlannerBlenderData"),
    ]
    
    for path in possible_paths:
        config_path = os.path.join(path, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'data_folder' in config:
                        _DATA_FOLDER_PATH = config['data_folder']
                        return _DATA_FOLDER_PATH
            except:
                pass
    
    _DATA_FOLDER_PATH = os.path.expanduser("~/Documents/PlannerBlenderData")
    os.makedirs(_DATA_FOLDER_PATH, exist_ok=True)
    
    return _DATA_FOLDER_PATH

def get_db_folder():
    """Возвращает путь к папке с БД"""
    data_folder = get_data_folder()
    db_folder = os.path.join(data_folder, "database")
    os.makedirs(db_folder, exist_ok=True)
    return db_folder

def get_reports_folder():
    """Возвращает путь к папке с отчётами"""
    data_folder = get_data_folder()
    reports_folder = os.path.join(data_folder, "reports")
    os.makedirs(reports_folder, exist_ok=True)
    return reports_folder

def get_config_path():
    """Возвращает путь к config.json"""
    return os.path.join(get_data_folder(), "config.json")

def load_config():
    """Загружает конфиг из папки-хранилища"""
    config_path = get_config_path()
    default_config = {
        "auto_save_interval": 30,
        "current_theme": "blender_orange",
        "tray_configured": True,
        "monitor_paths": [
            "~/Documents",
            "~/Documents/blender",
            "~/Desktop",
            "~/Downloads"
        ]
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except:
            return default_config
    else:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        return default_config

def save_config(config):
    """Сохраняет конфиг в папку-хранилище"""
    config_path = get_config_path()
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)