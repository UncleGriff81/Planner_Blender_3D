"""
deadline_warning.py - Диалог предупреждения о дедлайнах при закрытии
"""
import tkinter as tk
from tkinter import messagebox
from date_utils import format_deadline


def show_deadline_warning(root, theme, projects_objects_list, on_confirm_close):
    """
    Показывает окно предупреждения о проектах с дедлайнами
    Возвращает True, если пользователь подтвердил закрытие
    """
    projects_with_deadline = [p for p in projects_objects_list if p.get_deadline_date_obj()]
    
    if not projects_with_deadline:
        on_confirm_close()
        return True
    
    # Формируем список проектов
    project_list = "\n".join([f"📅 {p.name} — {format_deadline(p.get_deadline_date_obj())}" 
                               for p in projects_with_deadline[:5]])
    if len(projects_with_deadline) > 5:
        project_list += f"\n... и ещё {len(projects_with_deadline) - 5}"
    
    result = messagebox.askyesno(
        "⚠️ Срочные проекты",
        f"У вас есть проекты с приближающимся сроком сдачи:\n\n{project_list}\n\n"
        f"Убедитесь, что вы успеете завершить работу вовремя.\n\n"
        f"Закрыть программу?",
        icon='warning'
    )
    
    if result:
        on_confirm_close()
        return True
    else:
        return False