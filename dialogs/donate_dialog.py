"""
donate_dialog.py - Диалог поддержки проекта через ЮMoney
"""
import tkinter as tk
import webbrowser
from yoomoney import Quickpay


def show_donate_form(root, theme, wallet_number):
    """Показывает окно с вариантами поддержки проекта"""
    
    donate_window = tk.Toplevel(root)
    donate_window.title("Поддержать проект — Planner_Blender_3D")
    donate_window.configure(bg=theme.get("bg_color"))
    donate_window.geometry("500x480")
    donate_window.transient(root)
    donate_window.grab_set()
    donate_window.resizable(False, False)
    
    # Центрируем окно
    donate_window.update_idletasks()
    x = (donate_window.winfo_screenwidth() // 2) - 250
    y = (donate_window.winfo_screenheight() // 2) - 240
    donate_window.geometry(f"500x480+{x}+{y}")
    
    main_frame = tk.Frame(donate_window, bg=theme.get("bg_color"))
    main_frame.pack(fill="both", expand=True, padx=25, pady=20)
    
    # Заголовок с сердечком
    tk.Label(main_frame, text="❤️ Поддержать проект",
            font=("Arial", 16, "bold"),
            bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(pady=(0, 15))
    
    # Описание (разбито на две строки, чтобы не выходило за границы)
    desc_text = "Если вам нравится Planner_Blender_3D и вы хотите помочь его развитию,\nвы можете поддержать проект донатом."
    tk.Label(main_frame, text=desc_text,
            font=("Arial", 10),
            bg=theme.get("bg_color"), fg=theme.get("fg_color"),
            justify="center").pack(pady=(0, 20))
    
    # Разделительная линия
    separator = tk.Frame(main_frame, height=1, bg=theme.get("accent_color"))
    separator.pack(fill="x", pady=(0, 15))
    
    # Фрейм с вариантами сумм
    amounts_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    amounts_frame.pack(pady=10)
    
    def donate(amount):
        """Создаёт ссылку на оплату и открывает браузер"""
        quickpay = Quickpay(
            receiver=wallet_number,
            quickpay_form="shop",
            targets="Поддержка разработки Planner_Blender_3D",
            paymentType="SB",
            sum=amount,
        )
        webbrowser.open(quickpay.base_url)
    
    # Ряд 1: 100, 300, 500
    row1_frame = tk.Frame(amounts_frame, bg=theme.get("bg_color"))
    row1_frame.pack(pady=5)
    
    btn_100 = tk.Button(row1_frame, text="100 ₽", font=("Arial", 11, "bold"),
                        bg=theme.get("success_color"), fg="white",
                        relief="flat", padx=25, pady=8,
                        command=lambda: donate(100))
    btn_100.pack(side="left", padx=8)
    
    btn_300 = tk.Button(row1_frame, text="300 ₽", font=("Arial", 11, "bold"),
                        bg=theme.get("success_color"), fg="white",
                        relief="flat", padx=25, pady=8,
                        command=lambda: donate(300))
    btn_300.pack(side="left", padx=8)
    
    btn_500 = tk.Button(row1_frame, text="500 ₽", font=("Arial", 11, "bold"),
                        bg=theme.get("success_color"), fg="white",
                        relief="flat", padx=25, pady=8,
                        command=lambda: donate(500))
    btn_500.pack(side="left", padx=8)
    
    # Ряд 2: 1000 и произвольная сумма
    row2_frame = tk.Frame(amounts_frame, bg=theme.get("bg_color"))
    row2_frame.pack(pady=5)
    
    btn_1000 = tk.Button(row2_frame, text="1000 ₽", font=("Arial", 11, "bold"),
                         bg=theme.get("success_color"), fg="white",
                         relief="flat", padx=25, pady=8,
                         command=lambda: donate(1000))
    btn_1000.pack(side="left", padx=8)
    
    # Произвольная сумма
    custom_frame = tk.Frame(row2_frame, bg=theme.get("bg_color"))
    custom_frame.pack(side="left", padx=8)
    
    custom_entry = tk.Entry(custom_frame, width=8, font=("Arial", 11),
                            bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                            insertbackground=theme.get("fg_color"))
    custom_entry.pack(side="left", padx=(0, 5))
    
    tk.Label(custom_frame, text="₽", font=("Arial", 11, "bold"),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(side="left")
    
    def donate_custom():
        try:
            amount = int(custom_entry.get())
            if amount >= 10:
                donate(amount)
            else:
                tk.messagebox.showwarning("Минимальная сумма", "Минимальная сумма доната — 10 рублей")
        except ValueError:
            tk.messagebox.showerror("Ошибка", "Введите число")
    
    btn_custom = tk.Button(custom_frame, text="Поддержать", font=("Arial", 10),
                           bg=theme.get("accent_color"), fg="white",
                           relief="flat", command=donate_custom)
    btn_custom.pack(side="left", padx=(5, 0))
    
    # Разделительная линия
    separator2 = tk.Frame(main_frame, height=1, bg=theme.get("accent_color"))
    separator2.pack(fill="x", pady=(20, 15))
    
    # Информация о том, на что пойдут средства
    info_text = "Средства пойдут на:\n• Хостинг и обновления\n• Разработку новых функций\n• Поддержку проекта"
    info_label = tk.Label(main_frame, text=info_text,
                         font=("Arial", 9),
                         bg=theme.get("bg_color"), fg="gray",
                         justify="center")
    info_label.pack(pady=(0, 15))
    
    # Кнопка закрытия
    close_btn = tk.Button(main_frame, text="Закрыть", font=("Arial", 10),
                          bg=theme.get("error_color"), fg="white",
                          relief="flat", padx=20, pady=5,
                          command=donate_window.destroy)
    close_btn.pack()