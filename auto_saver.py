import threading
import time
from db_manager import update_project_time

class AutoSaver:
    """Автоматическое сохранение времени проектов"""
    
    def __init__(self, interval_seconds=30):
        self.interval = interval_seconds
        self.projects = []
        self.running = False
        self.thread = None
        
    def add_project(self, project):
        """Добавляет проект для автосохранения"""
        if project not in self.projects:
            self.projects.append(project)
    
    def remove_project(self, project):
        """Удаляет проект из автосохранения"""
        if project in self.projects:
            self.projects.remove(project)
    
    def start(self):
        """Запускает автосохранение в отдельном потоке"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._save_loop, daemon=True)
            self.thread.start()
            print(f"[AUTOSAVER] Запущен с интервалом {self.interval} сек")
    
    def stop(self):
        """Останавливает автосохранение"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("[AUTOSAVER] Остановлен")
    
    def _save_loop(self):
        """Цикл автосохранения"""
        while self.running:
            time.sleep(self.interval)
            self._save_all()
    
    def _save_all(self):
        """Сохраняет все проекты"""
        for project in self.projects:
            try:
                current_time = project.get_total_seconds() if hasattr(project, 'get_total_seconds') else project.elapsed_time
                update_project_time(project.id, current_time)
                print(f"[AUTOSAVER] Сохранён проект {project.id}: {current_time:.2f} сек")
            except Exception as e:
                print(f"[AUTOSAVER] Ошибка сохранения проекта {project.id}: {e}")
    
    def save_now(self):
        """Немедленное сохранение всех проектов"""
        self._save_all()