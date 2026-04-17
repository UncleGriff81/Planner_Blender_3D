"""
Запуск мониторинга процессов Blender
"""
from blender_process_monitor import get_process_monitor


def start_process_monitoring():
    """Запускает мониторинг процессов Blender"""
    process_monitor = get_process_monitor()
    process_monitor.start_monitoring()
    print("[MONITOR] Запущен мониторинг процессов Blender")