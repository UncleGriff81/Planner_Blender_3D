"""
Всплывающие уведомления для таймера
"""
import tkinter as tk


def show_timer_notification(message, color):
    """Показывает временное всплывающее уведомление"""
    try:
        # Находим корневое окно
        root = tk._default_root
        if root is None:
            return
        
        notification = tk.Toplevel(root)
        notification.title("Таймер")
        notification.configure(bg=color)
        notification.overrideredirect(True)
        notification.attributes('-topmost', True)
        
        notification.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() // 2) - 150
        y = root.winfo_y() + (root.winfo_height() // 2) - 30
        notification.geometry(f"300x60+{x}+{y}")
        
        tk.Label(notification, text=message, 
                font=("Arial", 12, "bold"),
                bg=color, fg="white").pack(expand=True)
        
        notification.after(2000, notification.destroy)
    except:
        pass