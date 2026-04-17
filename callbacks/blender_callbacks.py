"""
Колбэки для выбора версии Blender
"""
import tkinter as tk
from tkinter import messagebox
import os
from blender_utils import get_all_blender_versions
from db_manager import update_project_blender_path


def choose_blender_for_project(project, update_blender_info_callback, force_update_callback):
    """Открывает диалог выбора версии Blender для проекта"""
    versions = get_all_blender_versions()
    
    if not versions:
        messagebox.showerror("Ошибка", "Blender не найден в системе!\n\n"
                           "Установите Blender или добавьте путь вручную.")
        return
    
    # Создаём окно выбора
    selector_window = tk.Toplevel()
    selector_window.title(f"Выбор Blender для проекта: {project.name}")
    selector_window.configure(bg=project.update_ui_callback.__self__.theme.get("bg_color") if hasattr(project.update_ui_callback, '__self__') else "#282828")
    selector_window.geometry("750x500")
    selector_window.transient()
    selector_window.grab_set()
    
    tk.Label(selector_window, text=f"Выберите версию Blender для проекта:\n{project.name}", 
             font=("Arial", 12, "bold"),
             bg="#282828", fg="white").pack(pady=(15, 10))
    
    list_frame = tk.Frame(selector_window, bg="#282828")
    list_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")
    
    version_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                  font=("Courier New", 10),
                                  bg="#3c3c3c", fg="white",
                                  selectbackground="#ff8c00",
                                  height=10)
    version_listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=version_listbox.yview)
    
    current_selected = project.blender_path
    
    for i, v in enumerate(versions):
        version_str = v['version_str']
        path = v['path']
        is_default = v['is_default']
        
        display_text = f"{version_str:<12} - {path}"
        if is_default:
            display_text += " (по умолчанию)"
        
        version_listbox.insert(i, display_text)
        
        if current_selected and current_selected == path:
            version_listbox.selection_set(i)
    
    def select_version():
        selection = version_listbox.curselection()
        if selection:
            index = selection[0]
            selected_version = versions[index]
            project.blender_path = selected_version['path']
            update_project_blender_path(project.id, selected_version['path'])
            
            update_blender_info_callback()
            force_update_callback()
            
            messagebox.showinfo("Версия выбрана", 
                               f"Для проекта '{project.name}' выбрана версия:\n"
                               f"{selected_version['version_str']}\n"
                               f"{selected_version['path']}",
                               parent=selector_window)
            selector_window.destroy()
    
    btn_select = tk.Button(selector_window, text="✅ Выбрать эту версию",
                           bg="#7cb518", fg="white",
                           relief="flat", command=select_version, font=("Arial", 11))
    btn_select.pack(pady=(0, 20))


def update_blender_info(project, blender_label, theme):
    """Обновляет отображение информации о Blender"""
    if project.blender_path:
        path_parts = project.blender_path.split(os.sep)
        blender_display = "Blender: "
        for part in path_parts:
            if 'Blender' in part and len(part) > 7:
                blender_display += part
                break
        else:
            blender_display += os.path.basename(os.path.dirname(project.blender_path))
        blender_label.config(text=blender_display, fg=theme.get("success_color"))
    else:
        blender_label.config(text="Blender: не выбран", fg="orange")