"""
Запуск мониторинга файлов .blend
"""
import os
import pathlib
import threading
from blender_utils import get_blender_recent_files_path


def start_file_monitoring(root):
    """Запускает мониторинг файлов в отдельном потоке"""
    import file_monitor
    file_monitor.ROOT_WINDOW = root
    
    possible_paths = [
        get_blender_recent_files_path(),
        str(pathlib.Path.home() / "Documents"),
        str(pathlib.Path.home() / "Documents" / "blender"),
        str(pathlib.Path.home() / "Desktop"),
        str(pathlib.Path.home() / "Downloads"),
    ]
    
    path_to_watch = None
    for path in possible_paths:
        if path and os.path.exists(path):
            path_to_watch = path
            break
    
    if not path_to_watch:
        path_to_watch = str(pathlib.Path.home() / "Documents")
    
    monitor_thread = threading.Thread(target=file_monitor.start_monitoring, args=(path_to_watch,), daemon=True)
    monitor_thread.start()
    print(f"[MONITOR] Запущен файловый мониторинг для: {path_to_watch}")