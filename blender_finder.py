"""
Модуль для поиска установленных версий Blender
Поддерживает Windows, Linux, macOS
"""
import os
import platform
import subprocess
import json
import re
from pathlib import Path

class BlenderFinder:
    """Поиск и управление установленными версиями Blender"""
    
    def __init__(self):
        self.system = platform.system()
        self.versions = []
        self.scan_for_blender()
    
    def scan_for_blender(self):
        """Сканирует систему на наличие установленных версий Blender"""
        self.versions = []
        
        if self.system == "Windows":
            self._scan_windows()
        elif self.system == "Linux":
            self._scan_linux()
        elif self.system == "Darwin":  # macOS
            self._scan_macos()
        
        # Добавляем ручные пути из конфига
        self._load_custom_paths()
        
        # Удаляем дубликаты
        self.versions = self._remove_duplicates(self.versions)
        
        # Сортируем по версии (новые сверху)
        self.versions.sort(key=lambda x: x.get('version_sort', 0), reverse=True)
        
        return self.versions
    
    def _scan_windows(self):
        """Сканирует Windows на наличие Blender"""
        # Стандартные пути установки
        base_paths = [
            r"C:\Program Files\Blender Foundation",
            r"C:\Program Files (x86)\Blender Foundation",
            r"C:\Program Files\Blender",
            r"C:\Program Files (x86)\Blender",
            os.path.expanduser(r"~\AppData\Roaming\Blender Foundation"),
            os.path.expanduser(r"~\AppData\Local\Programs\Blender"),
        ]
        
        # Поиск через реестр
        self._scan_windows_registry()
        
        # Поиск в стандартных папках
        for base_path in base_paths:
            if os.path.exists(base_path):
                for item in os.listdir(base_path):
                    full_path = os.path.join(base_path, item)
                    blender_exe = os.path.join(full_path, "blender.exe")
                    if os.path.exists(blender_exe):
                        self._add_version(blender_exe)
                    
                    # Поиск во вложенных папках
                    if os.path.isdir(full_path):
                        for subitem in os.listdir(full_path):
                            sub_path = os.path.join(full_path, subitem)
                            blender_exe = os.path.join(sub_path, "blender.exe")
                            if os.path.exists(blender_exe):
                                self._add_version(blender_exe)
    
    def _scan_windows_registry(self):
        """Поиск Blender в реестре Windows"""
        try:
            import winreg
            
            # Ключи реестра для поиска
            registry_keys = [
                (winreg.HKEY_CURRENT_USER, r"Software\Blender Foundation\Blender"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Blender Foundation\Blender"),
                (winreg.HKEY_CURRENT_USER, r"Software\Classes\Applications\blender.exe\shell\open\command"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Classes\Applications\blender.exe\shell\open\command"),
            ]
            
            for hkey, key_path in registry_keys:
                try:
                    key = winreg.OpenKey(hkey, key_path)
                    
                    # Пробуем получить последнюю версию
                    try:
                        last_version, _ = winreg.QueryValueEx(key, "lastversion")
                        version_key_path = rf"{key_path}\{last_version}"
                        try:
                            version_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, version_key_path)
                            try:
                                install_path, _ = winreg.QueryValueEx(version_key, "InstallPath")
                                blender_exe = os.path.join(install_path, "blender.exe")
                                if os.path.exists(blender_exe):
                                    self._add_version(blender_exe)
                            except:
                                pass
                        except:
                            pass
                    except:
                        pass
                    
                    # Пробуем получить путь напрямую
                    try:
                        default_value, _ = winreg.QueryValueEx(key, "")
                        if "blender.exe" in default_value.lower():
                            # Извлекаем путь из командной строки
                            match = re.search(r'"([^"]+blender\.exe)"', default_value)
                            if match:
                                blender_exe = match.group(1)
                                if os.path.exists(blender_exe):
                                    self._add_version(blender_exe)
                    except:
                        pass
                    
                    winreg.CloseKey(key)
                except:
                    pass
        except:
            pass
    
    def _scan_linux(self):
        """Сканирует Linux на наличие Blender"""
        # Поиск через which
        try:
            result = subprocess.run(['which', 'blender'], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                if path and os.path.exists(path):
                    self._add_version(path)
        except:
            pass
        
        # Поиск в стандартных папках
        search_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            os.path.expanduser("~/bin/blender"),
            "/snap/bin/blender",
            "/opt/blender",
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                self._add_version(path)
        
        # Поиск всех версий в /usr/bin (blender-*)
        try:
            usr_bin = "/usr/bin"
            if os.path.exists(usr_bin):
                for item in os.listdir(usr_bin):
                    if item.startswith("blender"):
                        full_path = os.path.join(usr_bin, item)
                        if os.access(full_path, os.X_OK):
                            self._add_version(full_path)
        except:
            pass
        
        # Flatpak версии
        flatpak_paths = [
            "/var/lib/flatpak/app/org.blender.Blender/current/active/files/bin/blender",
            os.path.expanduser("~/.local/share/flatpak/app/org.blender.Blender/current/active/files/bin/blender"),
        ]
        for path in flatpak_paths:
            if os.path.exists(path):
                self._add_version(path)
    
    def _scan_macos(self):
        """Сканирует macOS на наличие Blender"""
        # Стандартный путь
        app_path = "/Applications/Blender.app/Contents/MacOS/Blender"
        if os.path.exists(app_path):
            self._add_version(app_path)
        
        # Пользовательский путь
        user_app = os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender")
        if os.path.exists(user_app):
            self._add_version(user_app)
        
        # Поиск через which
        try:
            result = subprocess.run(['which', 'blender'], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                if path and os.path.exists(path):
                    self._add_version(path)
        except:
            pass
        
        # Поиск всех версий в /Applications (Blender*.app)
        try:
            applications = "/Applications"
            if os.path.exists(applications):
                for item in os.listdir(applications):
                    if item.startswith("Blender") and item.endswith(".app"):
                        app_path = os.path.join(applications, item, "Contents/MacOS/Blender")
                        if os.path.exists(app_path):
                            self._add_version(app_path)
        except:
            pass
    
    def _add_version(self, executable_path):
        """Добавляет версию Blender в список"""
        if not executable_path or not os.path.exists(executable_path):
            return
        
        version = self._get_version_from_executable(executable_path)
        version_str = version.get('version_str', 'Unknown')
        version_sort = version.get('version_sort', 0)
        
        # Проверяем, нет ли уже такой версии
        for v in self.versions:
            if v['path'] == executable_path:
                return
        
        self.versions.append({
            'path': executable_path,
            'version_str': version_str,
            'version_sort': version_sort,
            'is_default': self._is_default_blender(executable_path)
        })
    
    def _get_version_from_executable(self, executable_path):
        """Получает версию Blender из исполняемого файла"""
        try:
            # Пробуем получить версию через --version
            result = subprocess.run([executable_path, '--version'], 
                                   capture_output=True, text=True, timeout=5)
            output = result.stdout + result.stderr
            
            # Ищем версию в выводе
            match = re.search(r'Blender\s+(\d+)\.(\d+)\.(\d+)', output)
            if match:
                major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
                version_str = f"{major}.{minor}.{patch}"
                version_sort = major * 10000 + minor * 100 + patch
                return {'version_str': version_str, 'version_sort': version_sort}
            
            # Пробуем другой паттерн
            match = re.search(r'(\d+)\.(\d+)\.(\d+)', output)
            if match:
                major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
                version_str = f"{major}.{minor}.{patch}"
                version_sort = major * 10000 + minor * 100 + patch
                return {'version_str': version_str, 'version_sort': version_sort}
        except:
            pass
        
        # Пробуем получить из пути
        path_parts = executable_path.split(os.sep)
        for part in path_parts:
            match = re.search(r'(\d+)\.(\d+)', part)
            if match:
                major, minor = int(match.group(1)), int(match.group(2))
                version_str = f"{major}.{minor}"
                version_sort = major * 10000 + minor * 100
                return {'version_str': version_str, 'version_sort': version_sort}
        
        return {'version_str': 'Unknown', 'version_sort': 0}
    
    def _is_default_blender(self, executable_path):
        """Проверяет, является ли Blender версией по умолчанию"""
        if self.system == "Windows":
            try:
                result = subprocess.run(['where', 'blender'], capture_output=True, text=True)
                if result.returncode == 0:
                    default_path = result.stdout.strip().split('\n')[0]
                    return default_path.lower() == executable_path.lower()
            except:
                pass
        elif self.system == "Linux" or self.system == "Darwin":
            try:
                result = subprocess.run(['which', 'blender'], capture_output=True, text=True)
                if result.returncode == 0:
                    default_path = result.stdout.strip()
                    return default_path == executable_path
            except:
                pass
        return False
    
    def _load_custom_paths(self):
        """Загружает пользовательские пути из config.json"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                custom_paths = config.get('blender_custom_paths', [])
                for path in custom_paths:
                    if path and os.path.exists(path):
                        self._add_version(path)
        except:
            pass
    
    def _remove_duplicates(self, versions):
        """Удаляет дубликаты версий"""
        seen_paths = set()
        unique_versions = []
        for v in versions:
            if v['path'] not in seen_paths:
                seen_paths.add(v['path'])
                unique_versions.append(v)
        return unique_versions
    
    def get_default_version(self):
        """Возвращает версию Blender по умолчанию"""
        for v in self.versions:
            if v['is_default']:
                return v
        return self.versions[0] if self.versions else None
    
    def get_version_by_path(self, path):
        """Возвращает версию по пути"""
        for v in self.versions:
            if v['path'] == path:
                return v
        return None
    
    def save_selected_version(self, version_path):
        """Сохраняет выбранную версию в конфиг"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
        
        config['selected_blender_path'] = version_path
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print(f"[BLENDER] Сохранена выбранная версия: {version_path}")
    
    def get_selected_version(self):
        """Возвращает сохранённую версию из конфига"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                selected_path = config.get('selected_blender_path', '')
                if selected_path and os.path.exists(selected_path):
                    return self.get_version_by_path(selected_path)
        except:
            pass
        return self.get_default_version()