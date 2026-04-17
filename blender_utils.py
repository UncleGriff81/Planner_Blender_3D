import os
import pathlib
import subprocess
import platform
import json
from blender_finder import BlenderFinder

# Глобальный экземпляр для кэширования
_blender_finder = None

def get_blender_finder():
    """Возвращает экземпляр BlenderFinder (с кэшированием)"""
    global _blender_finder
    if _blender_finder is None:
        _blender_finder = BlenderFinder()
    return _blender_finder

def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def get_blender_recent_files_path():
    system = platform.system()
    config = load_config()
    
    if config.get("blender_files_path"):
        return config["blender_files_path"]
    
    if system == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Blender Foundation\Blender"
            )
            last_version, _ = winreg.QueryValueEx(key, "lastversion")
            
            docs_path = pathlib.Path.home() / "Documents" / "blender"
            if docs_path.exists():
                return str(docs_path)
            
            return str(pathlib.Path.home() / "Documents")
            
        except:
            return str(pathlib.Path.home() / "Documents")
    
    elif system == "Linux":
        paths = [
            os.path.expanduser("~/Documents/blender"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/blender"),
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return os.path.expanduser("~/Documents")
    
    elif system == "Darwin":
        paths = [
            os.path.expanduser("~/Documents/Blender"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Library/Application Support/Blender"),
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return os.path.expanduser("~/Documents")
    
    return None

def find_blender_executable():
    """Находит Blender с учётом выбранной версии"""
    finder = get_blender_finder()
    
    # Сначала проверяем сохранённую версию
    selected = finder.get_selected_version()
    if selected:
        return selected['path']
    
    # Затем версию по умолчанию
    default = finder.get_default_version()
    if default:
        return default['path']
    
    # Если ничего не найдено
    print("[ERROR] Blender не найден в системе")
    return None

def get_all_blender_versions():
    """Возвращает все найденные версии Blender"""
    finder = get_blender_finder()
    return finder.versions

def get_blender_version_info():
    """Возвращает информацию о текущей версии Blender"""
    blender_path = find_blender_executable()
    if not blender_path:
        return None
    
    finder = get_blender_finder()
    return finder.get_version_by_path(blender_path)

def open_blender_with_file(file_path):
    blender_exe = find_blender_executable()
    
    if not blender_exe:
        print("[ERROR] Blender не найден в системе")
        return False
    
    if not os.path.exists(file_path):
        print(f"[ERROR] Файл не существует: {file_path}")
        return False
    
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        else:
            subprocess.Popen([blender_exe, file_path])
        print(f"[SUCCESS] Blender запущен с файлом: {file_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Не удалось запустить Blender: {e}")
        return False