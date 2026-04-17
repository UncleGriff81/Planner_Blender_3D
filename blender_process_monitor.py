"""
Мониторинг процессов Blender для отслеживания открытых файлов
"""
import os
import subprocess
import time
import threading
import platform
import re

class BlenderProcessMonitor:
    """Мониторит процессы Blender и определяет, какой файл открыт"""
    
    def __init__(self):
        self.system = platform.system()
        self.monitoring = False
        self.monitor_thread = None
        self.callbacks = {}
        self.debug = False  # Отключаем отладку для EXE
        
    def log(self, message):
        if self.debug:
            print(f"[PROCESS_MONITOR] {message}")
    
    def start_monitoring(self):
        if self.monitoring:
            return
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        if self.debug:
            self.log("Мониторинг процессов Blender запущен")
    
    def stop_monitoring(self):
        self.monitoring = False
    
    def register_file(self, file_path, callback_on_open, callback_on_close):
        file_path = os.path.normpath(file_path)
        self.callbacks[file_path] = {
            'on_open': callback_on_open,
            'on_close': callback_on_close,
            'is_open': False,
            'name': os.path.basename(file_path)
        }
        if self.debug:
            self.log(f"Зарегистрирован файл: {file_path}")
    
    def unregister_file(self, file_path):
        file_path = os.path.normpath(file_path)
        if file_path in self.callbacks:
            if self.callbacks[file_path]['is_open'] and self.callbacks[file_path]['on_close']:
                self.callbacks[file_path]['on_close'](file_path)
            del self.callbacks[file_path]
            if self.debug:
                self.log(f"Удалён из отслеживания: {file_path}")
    
    def _monitor_loop(self):
        while self.monitoring:
            try:
                self._check_processes()
            except Exception as e:
                if self.debug:
                    self.log(f"Ошибка в цикле мониторинга: {e}")
            time.sleep(2)
    
    def _check_processes(self):
        current_open_files = self._get_open_blender_files()
        
        for file_path, data in self.callbacks.items():
            was_open = data['is_open']
            normalized_path = os.path.normpath(file_path)
            
            is_open = normalized_path in current_open_files
            
            if not is_open:
                file_name = data['name']
                for open_file in current_open_files:
                    if os.path.basename(open_file) == file_name:
                        is_open = True
                        break
            
            if is_open and not was_open:
                data['is_open'] = True
                if data['on_open']:
                    try:
                        data['on_open'](file_path)
                    except Exception as e:
                        if self.debug:
                            self.log(f"Ошибка в callback открытия: {e}")
            
            elif not is_open and was_open:
                data['is_open'] = False
                if data['on_close']:
                    try:
                        data['on_close'](file_path)
                    except Exception as e:
                        if self.debug:
                            self.log(f"Ошибка в callback закрытия: {e}")
    
    def _run_command(self, cmd, encoding='cp866', errors='ignore'):
        """Безопасный запуск команды с обработкой кодировки и без окон"""
        try:
            # Добавляем CREATE_NO_WINDOW для Windows
            if self.system == "Windows":
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=5,
                    encoding=encoding,
                    errors=errors,
                    creationflags=0x08000000  # CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=5,
                    encoding=encoding,
                    errors=errors
                )
            return result
        except subprocess.TimeoutExpired:
            if self.debug:
                self.log(f"Таймаут команды: {cmd}")
            return None
        except Exception as e:
            if self.debug:
                self.log(f"Ошибка команды {cmd}: {e}")
            return None
    
    def _get_open_blender_files(self):
        open_files = set()
        
        if self.system == "Windows":
            open_files = self._get_open_files_windows()
        elif self.system == "Linux":
            open_files = self._get_open_files_linux()
        elif self.system == "Darwin":
            open_files = self._get_open_files_macos()
        
        return open_files
    
    def _get_open_files_windows(self):
        open_files = set()
        
        # Способ 1: Через psutil (наиболее надёжный и тихий)
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                    if 'blender' in proc_name:
                        cmdline = proc.info['cmdline']
                        if cmdline:
                            for arg in cmdline:
                                if arg and arg.endswith('.blend') and os.path.exists(arg):
                                    open_files.add(os.path.normpath(arg))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass
        except Exception:
            pass
        
        return open_files
    
    def _get_open_files_linux(self):
        open_files = set()
        try:
            result = self._run_command(['pgrep', '-a', 'blender'])
            if result and result.stdout:
                for line in result.stdout.split('\n'):
                    if '.blend' in line:
                        matches = re.findall(r'([^\s]+\.blend)', line)
                        for match in matches:
                            if os.path.exists(match):
                                open_files.add(os.path.normpath(match))
        except:
            pass
        return open_files
    
    def _get_open_files_macos(self):
        open_files = set()
        try:
            result = self._run_command(['pgrep', '-a', 'Blender'])
            if result and result.stdout:
                for line in result.stdout.split('\n'):
                    if '.blend' in line:
                        matches = re.findall(r'([^\s]+\.blend)', line)
                        for match in matches:
                            if os.path.exists(match):
                                open_files.add(os.path.normpath(match))
        except:
            pass
        return open_files
    
    def is_file_open(self, file_path):
        file_path = os.path.normpath(file_path)
        return file_path in self._get_open_blender_files()

_process_monitor = None

def get_process_monitor():
    global _process_monitor
    if _process_monitor is None:
        _process_monitor = BlenderProcessMonitor()
        _process_monitor.start_monitoring()
    return _process_monitor