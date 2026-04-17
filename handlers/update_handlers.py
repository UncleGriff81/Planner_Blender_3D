"""
Обработчики обновлений
"""
import webbrowser
import requests
from tkinter import messagebox


def check_for_updates(current_version, silent=False):
    """Проверяет наличие обновлений на GitHub"""
    try:
        import requests
        REQUESTS_AVAILABLE = True
    except ImportError:
        REQUESTS_AVAILABLE = False
    
    if not REQUESTS_AVAILABLE:
        if not silent:
            messagebox.showinfo("Проверка обновлений", "Функция будет доступна в следующей версии.")
        return False
    
    try:
        response = requests.get("https://raw.githubusercontent.com/UncleGriff81/Planner_Blender_3D_Updates/main/version.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("version", "")
            download_url = data.get("download_url", "")
            release_notes = data.get("release_notes", "")
            
            if latest_version and latest_version > current_version:
                msg = f"Доступна новая версия {latest_version}!\n\n"
                msg += f"Текущая версия: {current_version}\n"
                if release_notes:
                    msg += f"\nЧто нового:\n{release_notes}\n\n"
                msg += "Перейти на страницу загрузки?"
                
                if messagebox.askyesno("Обновление", msg):
                    webbrowser.open(download_url)
                return True
            elif not silent:
                messagebox.showinfo("Обновления", f"У вас последняя версия ({current_version})")
        else:
            if not silent:
                messagebox.showinfo("Проверка обновлений", "Сервер временно недоступен.")
    except:
        if not silent:
            messagebox.showinfo("Проверка обновлений", "Сервер временно недоступен.")
    
    return False