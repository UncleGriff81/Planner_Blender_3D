"""
Инициализация приложения: автоустановка библиотек, подавление консоли, mutex
"""
import sys
import subprocess


def suppress_console():
    """Подавляет консольное окно для Windows EXE"""
    if sys.platform == "win32" and getattr(sys, 'frozen', False):
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            ctypes.windll.kernel32.SetConsoleCtrlHandler(None, 1)
        except:
            pass


def setup_mutex():
    """Предотвращает множественный запуск программы"""
    if sys.platform == "win32" and getattr(sys, 'frozen', False):
        try:
            import win32event
            import win32api
            from win32event import CreateMutex
            from win32api import GetLastError
            from winerror import ERROR_ALREADY_EXISTS
            
            mutex_name = "Planner_Blender_3D_MUTEX"
            mutex = CreateMutex(None, False, mutex_name)
            if GetLastError() == ERROR_ALREADY_EXISTS:
                sys.exit(0)
        except:
            pass


def auto_install_packages():
    """Автоматически устанавливает недостающие библиотеки"""
    if getattr(sys, 'frozen', False):
        return
    
    required_packages = ['pillow', 'pystray', 'requests', 'psutil', 'watchdog']
    missing = []
    
    for package in required_packages:
        try:
            if package == 'pillow':
                import PIL
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[INFO] Устанавливаются отсутствующие библиотеки: {missing}")
        for package in missing:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             capture_output=True, 
                             creationflags=0x08000000 if sys.platform == "win32" else 0)
                print(f"[INFO] Установлена библиотека: {package}")
            except Exception as e:
                print(f"[ERROR] Не удалось установить {package}: {e}")
        
        print("[INFO] Библиотеки установлены. Пожалуйста, перезапустите программу вручную.")
        input("Нажмите Enter для выхода...")
        sys.exit(0)