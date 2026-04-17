import time
import os
import re
import platform
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PROJECTS_DICT = {}
ROOT_WINDOW = None

class BlendFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.blend'):
            self.process_file(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.blend'):
            self.process_file(event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory and event.dest_path.lower().endswith('.blend'):
            self.process_file(event.dest_path)
    
    def process_file(self, file_path):
        src_path = file_path.lower()
        
        if not src_path.endswith('.blend'):
            return
        
        file_name_with_ext = os.path.basename(src_path)
        file_name_without_ext = os.path.splitext(file_name_with_ext)[0]
        
        print(f"\n[MONITOR] Обнаружен файл .blend: {file_name_without_ext}")
        print(f"[MONITOR] Полный путь: {src_path}")
        
        found_project = None
        
        if file_name_without_ext in PROJECTS_DICT:
            found_project = PROJECTS_DICT[file_name_without_ext]
            print(f"[MONITOR] Найдено точное совпадение по имени")
        
        if not found_project:
            for key, project in PROJECTS_DICT.items():
                if isinstance(key, str) and key.lower() and key.lower() in file_name_without_ext.lower():
                    found_project = project
                    print(f"[MONITOR] Найдено частичное совпадение: {key} в {file_name_without_ext}")
                    break
        
        if not found_project:
            for key, project in PROJECTS_DICT.items():
                if isinstance(key, int):
                    if str(key) in file_name_without_ext:
                        found_project = project
                        print(f"[MONITOR] Найдено совпадение по ID: {key}")
                        break
        
        if found_project:
            print(f"[MONITOR] Найден проект: {found_project.name} (ID: {found_project.id})")
            print(f"[MONITOR] Таймер запущен: {found_project.timer_running}")
            
            if not found_project.timer_running:
                print(f"[MONITOR] Запуск таймера для проекта {found_project.id}")
                found_project.start_timer()
                
                if ROOT_WINDOW:
                    ROOT_WINDOW.event_generate("<<ProjectTimerStarted>>", when="tail")
                    ROOT_WINDOW.after(100, lambda: ROOT_WINDOW.event_generate("<<UpdateAllTimers>>", when="tail"))
            else:
                print(f"[MONITOR] Таймер уже запущен для проекта {found_project.id}")
        else:
            print(f"[MONITOR] Файл не найден в базе проектов")
            print(f"[MONITOR] Доступные проекты: {list(PROJECTS_DICT.keys())}")

def start_monitoring(path_to_watch):
    """Запускает мониторинг файлов в указанной папке"""
    if not os.path.exists(path_to_watch):
        print(f"[ERROR] Папка для мониторинга не существует: {path_to_watch}")
        return None
    
    event_handler = BlendFileHandler()
    observer = Observer()
    
    observer.schedule(event_handler, path=path_to_watch, recursive=True)
    
    observer.start()
    print(f"[MONITOR] Мониторинг запущен для папки: {path_to_watch}")
    print(f"[MONITOR] Отслеживание рекурсивно: ДА")
    
    return observer