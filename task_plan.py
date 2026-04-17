import time
import datetime
import os
from db_manager import add_work_session

class Project:
    def __init__(self, id, name, description, blend_file, creation_date,
                 elapsed_time=0.0, blender_path="", deadline_date="", deadline_days=0):
        self.id = id
        self.name = name
        self.description = description
        self.blend_file = blend_file
        self.creation_date = creation_date
        self.elapsed_time = elapsed_time
        self.start_time = None
        self.timer_running = False
        self.paused_time = 0
        self.session_start = None  # Время начала текущего сеанса
        self.update_ui_callback = None
        self.auto_save_callback = None
        self.blender_path = blender_path
        self.full_file_path = ""
        self.deadline_date = deadline_date
        self.deadline_days = deadline_days

    def set_full_file_path(self, file_path):
        self.full_file_path = file_path

    def get_full_file_path(self):
        if self.full_file_path:
            return self.full_file_path
        search_dirs = [
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Documents/blender"),
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Downloads"),
        ]
        for search_dir in search_dirs:
            full_path = os.path.join(search_dir, f"{self.blend_file}.blend")
            if os.path.exists(full_path):
                self.full_file_path = full_path
                return full_path
        return ""

    def get_deadline_date_obj(self):
        if not self.deadline_date:
            return None
        try:
            return datetime.datetime.strptime(self.deadline_date, '%Y-%m-%d %H:%M:%S')
        except:
            return None

    def set_deadline_from_days(self, days):
        if days and days > 0:
            self.deadline_days = days
            deadline = datetime.datetime.now() + datetime.timedelta(days=days)
            self.deadline_date = deadline.strftime('%Y-%m-%d %H:%M:%S')
        else:
            self.deadline_days = 0
            self.deadline_date = ""

    def set_deadline_from_date(self, date_obj):
        if date_obj:
            self.deadline_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
            delta = date_obj - datetime.datetime.now()
            self.deadline_days = max(1, delta.days)
        else:
            self.deadline_date = ""
            self.deadline_days = 0

    def start_timer(self):
        if not self.timer_running:
            self.start_time = time.time() - self.paused_time
            self.timer_running = True
            self.paused_time = 0
            self.session_start = datetime.datetime.now()
            print(f"[TIMER] Таймер запущен для проекта {self.id} ({self.name})")
            self._update_ui()
            self._trigger_auto_save()

    def pause_timer(self):
        if self.timer_running:
            self.elapsed_time += time.time() - self.start_time
            self.timer_running = False
            self.paused_time = self.elapsed_time

            if self.session_start:
                end_time = datetime.datetime.now()
                duration = (end_time - self.session_start).total_seconds()
                if duration > 0:
                    add_work_session(
                        self.id,
                        self.session_start.strftime('%Y-%m-%d %H:%M:%S'),
                        end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        duration
                    )
                    print(f"[TIMER] Записан сеанс работы: {duration:.0f} сек")
                self.session_start = None

            print(f"[TIMER] Таймер приостановлен для проекта {self.id} ({self.name})")
            self._update_ui()
            self._save_to_db()

    def stop_timer(self):
        if self.timer_running:
            self.elapsed_time += time.time() - self.start_time
            self.timer_running = False

            if self.session_start:
                end_time = datetime.datetime.now()
                duration = (end_time - self.session_start).total_seconds()
                if duration > 0:
                    add_work_session(
                        self.id,
                        self.session_start.strftime('%Y-%m-%d %H:%M:%S'),
                        end_time.strftime('%Y-%m-%d %H:%M:%S'),
                        duration
                    )
                    print(f"[TIMER] Записан сеанс работы: {duration:.0f} сек")
                self.session_start = None

        self.start_time = None
        self.paused_time = 0
        print(f"[TIMER] Таймер остановлен для проекта {self.id} ({self.name})")
        self._update_ui()
        self._save_to_db()

    def get_formatted_time(self):
        total_seconds = self.elapsed_time
        if self.timer_running and self.start_time:
            total_seconds += time.time() - self.start_time
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_total_seconds(self):
        total_seconds = self.elapsed_time
        if self.timer_running and self.start_time:
            total_seconds += time.time() - self.start_time
        return total_seconds

    def _update_ui(self):
        if self.update_ui_callback:
            self.update_ui_callback()

    def _save_to_db(self):
        if self.auto_save_callback:
            self.auto_save_callback(self.id, self.elapsed_time)

    def _trigger_auto_save(self):
        if self.auto_save_callback and self.timer_running:
            current_total = self.get_total_seconds()
            self.auto_save_callback(self.id, current_total)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'blend_file': self.blend_file,
            'creation_date': self.creation_date,
            'elapsed_time': self.elapsed_time,
            'blender_path': self.blender_path,
            'full_file_path': self.full_file_path,
            'deadline_date': self.deadline_date,
            'deadline_days': self.deadline_days
        }