"""
Колбэки для работы с файлами проекта
"""
import os
import sys
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox
from db_manager import update_project_file_path
from theme_manager import ThemeManager


def show_blender_launch_warning(root, theme):
    """Показывает предупреждение о консоли Blender (поверх всех окон)"""
    warning_window = tk.Toplevel(root)
    warning_window.title("🎨 Запуск Blender")
    warning_window.configure(bg=theme.get("bg_color"))
    warning_window.geometry("550x320")
    warning_window.transient(root)
    warning_window.grab_set()
    warning_window.resizable(False, False)
    warning_window.attributes('-topmost', True)
    
    # Центрируем окно
    warning_window.update_idletasks()
    x = (warning_window.winfo_screenwidth() // 2) - 275
    y = (warning_window.winfo_screenheight() // 2) - 160
    warning_window.geometry(f"550x320+{x}+{y}")
    
    main_frame = tk.Frame(warning_window, bg=theme.get("bg_color"))
    main_frame.pack(fill="both", expand=True, padx=25, pady=20)
    
    tk.Label(main_frame, text="🎨 Запуск Blender", 
             font=("Arial", 14, "bold"),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(pady=(0, 15))
    
    info_text = """При запуске Blender может открыться дополнительное окно (консоль аддонов).

⚠️ НЕ ЗАКРЫВАЙТЕ ЕГО!

Если вы закроете это окно, Blender завершит свою работу.

Просто сверните его или оставьте открытым — оно не мешает работе.

Таймер в программе продолжает работать автоматически."""
    
    tk.Label(main_frame, text=info_text, 
             font=("Arial", 10),
             bg=theme.get("bg_color"), fg=theme.get("fg_color"),
             justify="left").pack(pady=(0, 20))
    
    def on_ok():
        warning_window.destroy()
    
    ok_btn = tk.Button(main_frame, text="OK", font=("Arial", 11, "bold"),
                       bg=theme.get("success_color"), fg="white",
                       relief="flat", padx=30, pady=5,
                       command=on_ok)
    ok_btn.pack()


def create_blend_file(project, force_update_callback):
    """Создаёт .blend файл через Blender"""
    if not project.blender_path:
        messagebox.showerror("Ошибка", "Сначала выберите версию Blender для этого проекта!")
        return False
    
    if not os.path.exists(project.blender_path):
        messagebox.showerror("Ошибка", f"Blender не найден по пути:\n{project.blender_path}")
        return False
    
    initial_dir = os.path.dirname(project.get_full_file_path()) if project.get_full_file_path() else os.path.expanduser("~/Documents")
    
    save_folder = filedialog.askdirectory(
        title=f"Выберите папку для сохранения {project.blend_file}.blend",
        initialdir=initial_dir
    )
    
    if not save_folder:
        return False
    
    save_folder = os.path.normpath(save_folder)
    full_path = os.path.join(save_folder, f"{project.blend_file}.blend")
    full_path = os.path.normpath(full_path)
    
    project.set_full_file_path(full_path)
    update_project_file_path(project.id, full_path)
    
    try:
        blender_path = os.path.normpath(project.blender_path)
        
        script_content = f'''
import bpy
bpy.ops.wm.save_as_mainfile(filepath=r'{full_path}')
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(script_content)
            script_path = f.name
        
        cmd = [blender_path, '--background', '--python', script_path]
        
        # Запускаем без консоли
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                    creationflags=subprocess.CREATE_NO_WINDOW,
                                    startupinfo=startupinfo)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        try:
            os.unlink(script_path)
        except:
            pass
        
        if os.path.exists(full_path) and os.path.getsize(full_path) > 1024:
            messagebox.showinfo("Успех", f"Файл создан:\n{full_path}")
            force_update_callback()
            return True
        else:
            error_msg = result.stderr if result.stderr else "Неизвестная ошибка"
            messagebox.showerror("Ошибка", f"Не удалось создать файл:\n{full_path}\n\n{error_msg[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        messagebox.showerror("Ошибка", "Превышено время ожидания при создании файла")
        return False
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось создать файл:\n{str(e)}")
        return False


def launch_blender(project, monitor, on_file_opened, on_file_closed, create_blend_file_callback):
    """Запускает Blender с файлом проекта"""
    if not project.blender_path:
        messagebox.showerror("Ошибка", "Сначала выберите версию Blender для этого проекта!\n\n"
                           "Нажмите кнопку '🔧 Выбрать Blender'")
        return
    
    if not os.path.exists(project.blender_path):
        messagebox.showerror("Ошибка", f"Blender не найден по пути:\n{project.blender_path}\n\n"
                           "Выберите другую версию")
        return
    
    file_path = project.get_full_file_path()
    
    if not file_path or not os.path.exists(file_path):
        response = messagebox.askyesno(
            "Файл не найден",
            f"Файл '{project.blend_file}.blend' не найден.\n\n"
            f"Хотите создать его сейчас?"
        )
        if response:
            if not create_blend_file_callback():
                return
            file_path = project.get_full_file_path()
        else:
            return
    
    if file_path and os.path.exists(file_path):
        monitor.register_file(file_path, on_file_opened, on_file_closed)
    
    # Показываем предупреждение о консоли (поверх всех окон)
    root = tk._default_root
    if root:
        theme = ThemeManager()
        show_blender_launch_warning(root, theme)
    
    try:
        blender_path = os.path.normpath(project.blender_path)
        file_path = os.path.normpath(file_path)
        
        # Запускаем Blender
        subprocess.Popen([blender_path, file_path], shell=False)
        print(f"[LAUNCH] Запущен Blender с файлом: {file_path}")
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить Blender:\n{str(e)}")