"""
Управление автозагрузкой Windows
"""
import sys
import os


def add_to_startup():
    """Добавляет программу в автозагрузку"""
    if sys.platform != "win32":
        return False
    
    from tkinter import messagebox
    
    if not messagebox.askyesno("Автозагрузка", "Разрешить программе запускаться при старте Windows?"):
        return False
    
    try:
        import winreg
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__).replace('.py', '.exe')
            if not os.path.exists(exe_path):
                exe_path = sys.executable
        
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Planner_Blender_3D", 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)
        messagebox.showinfo("Успех", "Программа добавлена в автозагрузку!")
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось добавить в автозагрузку: {str(e)}")
        return False


def remove_from_startup():
    """Удаляет программу из автозагрузки"""
    if sys.platform != "win32":
        return False
    
    from tkinter import messagebox
    
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "Planner_Blender_3D")
        winreg.CloseKey(key)
        messagebox.showinfo("Успех", "Программа удалена из автозагрузки!")
        return True
    except:
        return False


def is_in_startup():
    """Проверяет, добавлена ли программа в автозагрузку"""
    if sys.platform != "win32":
        return False
    
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, "Planner_Blender_3D")
        winreg.CloseKey(key)
        return True
    except:
        return False


def on_closing(auto_saver, projects_objects_list, root):
    """Обработчик закрытия программы"""
    print("[INFO] Закрытие программы...")
    if auto_saver:
        auto_saver.stop()
    for project in projects_objects_list:
        if project.timer_running:
            project.stop_timer()
    root.destroy()