"""
Диалог обратной связи (универсальная отправка писем с автоопределением SMTP и сохранением пароля)
"""
import tkinter as tk
from tkinter import messagebox
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from path_utils import load_config, save_config


def get_smtp_settings(email):
    """
    Автоматически определяет SMTP-настройки по домену почты
    Возвращает (smtp_server, port, use_tls, requires_app_password)
    """
    domain = email.split('@')[-1].lower() if '@' in email else ''
    
    # Словарь настроек для разных почтовых сервисов
    smtp_settings = {
        'gmail.com': ('smtp.gmail.com', 587, True, True),
        'yandex.ru': ('smtp.yandex.ru', 587, True, False),
        'yandex.com': ('smtp.yandex.com', 587, True, False),
        'mail.ru': ('smtp.mail.ru', 587, True, False),
        'bk.ru': ('smtp.mail.ru', 587, True, False),
        'list.ru': ('smtp.mail.ru', 587, True, False),
        'inbox.ru': ('smtp.mail.ru', 587, True, False),
        'rambler.ru': ('smtp.rambler.ru', 587, True, False),
        'lenta.ru': ('smtp.rambler.ru', 587, True, False),
        'ro.ru': ('smtp.rambler.ru', 587, True, False),
        'outlook.com': ('smtp-mail.outlook.com', 587, True, False),
        'hotmail.com': ('smtp-mail.outlook.com', 587, True, False),
        'live.com': ('smtp-mail.outlook.com', 587, True, False),
        'yahoo.com': ('smtp.mail.yahoo.com', 587, True, False),
        'yahoo.ru': ('smtp.mail.yahoo.com', 587, True, False),
        'icloud.com': ('smtp.mail.me.com', 587, True, False),
        'me.com': ('smtp.mail.me.com', 587, True, False),
        'mail.com': ('smtp.mail.com', 587, True, False),
    }
    
    # Поиск по точному совпадению
    if domain in smtp_settings:
        return smtp_settings[domain]
    
    # Поиск по частичному совпадению
    for key, settings in smtp_settings.items():
        if key in domain or domain in key:
            return settings
    
    return None


def load_saved_credentials():
    """Загружает сохранённые учётные данные из конфига"""
    config = load_config()
    return {
        'name': config.get('feedback_name', ''),
        'email': config.get('feedback_email', ''),
        'password': config.get('feedback_password', ''),
        'save_password': config.get('feedback_save_password', False)
    }


def save_credentials(name, email, password, save_password):
    """Сохраняет учётные данные в конфиг"""
    config = load_config()
    if save_password:
        config['feedback_name'] = name
        config['feedback_email'] = email
        config['feedback_password'] = password
        config['feedback_save_password'] = True
    else:
        config.pop('feedback_name', None)
        config.pop('feedback_email', None)
        config.pop('feedback_password', None)
        config['feedback_save_password'] = False
    save_config(config)


def show_feedback_form(root, theme, target_email, current_version):
    """Показывает форму обратной связи внутри приложения"""
    
    # Загружаем сохранённые данные
    saved = load_saved_credentials()
    
    feedback_window = tk.Toplevel(root)
    feedback_window.title("Обратная связь — Planner_Blender_3D")
    feedback_window.configure(bg=theme.get("bg_color"))
    feedback_window.transient(root)
    feedback_window.grab_set()
    feedback_window.geometry("620x720")
    feedback_window.resizable(False, False)
    
    feedback_window.update_idletasks()
    x = (feedback_window.winfo_screenwidth() // 2) - 310
    y = (feedback_window.winfo_screenheight() // 2) - 360
    feedback_window.geometry(f"620x720+{x}+{y}")
    
    main_frame = tk.Frame(feedback_window, bg=theme.get("bg_color"))
    main_frame.pack(fill="both", expand=True, padx=25, pady=20)
    
    tk.Label(main_frame, 
             text="🎨 Planner_Blender_3D — ваш инструмент для творчества", 
             font=("Arial", 12, "bold"),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(pady=(0, 10))
    
    tk.Label(main_frame, 
             text="Этот проект создаётся с любовью к 3D и планированию.\nНо без вашей помощи он не станет идеальным!",
             font=("Arial", 10),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(pady=(0, 15))
    
    separator = tk.Frame(main_frame, height=1, bg=theme.get("accent_color"))
    separator.pack(fill="x", pady=(0, 15))
    
    # Поле: Ваше имя
    name_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    name_frame.pack(fill="x", pady=(0, 12))
    
    tk.Label(name_frame, text="👤 Ваше имя:", font=("Arial", 10),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(anchor="w")
    
    name_entry = tk.Entry(name_frame, font=("Arial", 11),
                          bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                          insertbackground=theme.get("fg_color"))
    name_entry.pack(fill="x", pady=(5, 0))
    if saved['name']:
        name_entry.insert(0, saved['name'])
    
    # Поле: Ваша почта
    email_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    email_frame.pack(fill="x", pady=(0, 12))
    
    tk.Label(email_frame, text="📧 Ваша почта:", font=("Arial", 10),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(anchor="w")
    
    email_entry = tk.Entry(email_frame, font=("Arial", 11),
                           bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                           insertbackground=theme.get("fg_color"))
    email_entry.pack(fill="x", pady=(5, 0))
    if saved['email']:
        email_entry.insert(0, saved['email'])
    
    # Поле: Пароль
    password_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    password_frame.pack(fill="x", pady=(0, 12))
    
    tk.Label(password_frame, text="🔑 Пароль (или пароль приложения):", font=("Arial", 10),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(anchor="w")
    
    password_entry = tk.Entry(password_frame, font=("Arial", 11),
                              bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                              insertbackground=theme.get("fg_color"), show="•")
    password_entry.pack(fill="x", pady=(5, 0))
    if saved['password'] and saved['save_password']:
        password_entry.insert(0, saved['password'])
    
    # Чекбокс "Сохранить пароль"
    save_var = tk.BooleanVar(value=saved['save_password'])
    save_check = tk.Checkbutton(password_frame, text="Сохранить пароль (при следующем обращении не нужно будет вводить заново)",
                                variable=save_var,
                                bg=theme.get("bg_color"), fg=theme.get("fg_color"),
                                selectcolor=theme.get("bg_color"))
    save_check.pack(anchor="w", pady=(5, 0))
    
    # Информационная метка
    info_label = tk.Label(password_frame, 
                         text="ℹ️ Введите пароль от почтового ящика",
                         font=("Arial", 8),
                         bg=theme.get("bg_color"), fg="gray")
    info_label.pack(anchor="w", pady=(2, 0))
    
    # Функция обновления подсказки при вводе почты
    def update_info(*args):
        email = email_entry.get().strip()
        if '@' in email:
            domain = email.split('@')[-1].lower()
            if 'gmail' in domain:
                info_label.config(text="ℹ️ Для Gmail требуется пароль приложения (получите в настройках аккаунта)")
            elif 'yandex' in domain:
                info_label.config(text="ℹ️ Для Яндекс.Почты можно использовать обычный пароль")
            elif 'mail' in domain and 'ru' in domain:
                info_label.config(text="ℹ️ Для Mail.ru можно использовать обычный пароль")
            else:
                info_label.config(text="ℹ️ Введите пароль от почтового ящика")
    
    email_entry.bind('<KeyRelease>', update_info)
    
    # Поле: Тип обращения
    subject_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    subject_frame.pack(fill="x", pady=(0, 12))
    
    tk.Label(subject_frame, text="📋 Тип обращения:", font=("Arial", 10),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(anchor="w")
    
    subject_var = tk.StringVar(value="💡 Идея по улучшению")
    subjects = [
        "💡 Идея по улучшению",
        "🐛 Сообщение об ошибке",
        "🎨 Дизайн-предложение",
        "⚡ Оптимизация",
        "📝 Другое"
    ]
    
    subject_dropdown = tk.OptionMenu(subject_frame, subject_var, *subjects)
    subject_dropdown.config(bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                            relief="flat", width=40)
    subject_dropdown.pack(fill="x", pady=(5, 0))
    
    # Поле: Сообщение
    message_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    message_frame.pack(fill="both", expand=True, pady=(0, 12))
    
    tk.Label(message_frame, text="💬 Ваше сообщение:", font=("Arial", 10),
             bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(anchor="w")
    
    message_text = tk.Text(message_frame, height=8, font=("Arial", 10),
                           bg=theme.get("frame_bg"), fg=theme.get("fg_color"),
                           insertbackground=theme.get("fg_color"), wrap="word")
    message_text.pack(fill="both", expand=True, pady=(5, 0))
    
    status_label = tk.Label(main_frame, text="", font=("Arial", 9),
                            bg=theme.get("bg_color"), fg=theme.get("success_color"))
    status_label.pack(pady=(5, 5))
    
    btn_frame = tk.Frame(main_frame, bg=theme.get("bg_color"))
    btn_frame.pack(fill="x", pady=(15, 0))
    
    def send_feedback():
        name = name_entry.get().strip()
        user_email = email_entry.get().strip()
        user_password = password_entry.get().strip()
        subject_type = subject_var.get()
        message = message_text.get("1.0", "end-1c").strip()
        save_password = save_var.get()
        
        # Валидация
        if not name:
            status_label.config(text="⚠️ Пожалуйста, укажите ваше имя", fg="orange")
            return
        
        if not user_email:
            status_label.config(text="⚠️ Пожалуйста, укажите вашу почту", fg="orange")
            return
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, user_email):
            status_label.config(text="⚠️ Неверный формат почты", fg="orange")
            return
        
        if not user_password:
            status_label.config(text="⚠️ Пожалуйста, укажите пароль", fg="orange")
            return
        
        if not message:
            status_label.config(text="⚠️ Пожалуйста, напишите сообщение", fg="orange")
            return
        
        # Сохраняем учётные данные
        save_credentials(name, user_email, user_password, save_password)
        
        # Определяем SMTP-настройки
        smtp_settings = get_smtp_settings(user_email)
        
        if smtp_settings is None:
            response = messagebox.askyesno(
                "Неизвестный почтовый сервис",
                f"Не удалось автоматически определить настройки для {user_email}\n\n"
                "Хотите ввести SMTP-настройки вручную?\n"
                "Если нет, отправка будет отменена."
            )
            if not response:
                return
            
            manual_dialog = tk.Toplevel(feedback_window)
            manual_dialog.title("Ручная настройка SMTP")
            manual_dialog.configure(bg=theme.get("bg_color"))
            manual_dialog.geometry("450x350")
            manual_dialog.transient(feedback_window)
            manual_dialog.grab_set()
            
            tk.Label(manual_dialog, text="Введите SMTP-настройки для вашего почтового сервиса:",
                    font=("Arial", 10), bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(pady=15)
            
            tk.Label(manual_dialog, text="SMTP сервер:", bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(anchor="w", padx=20)
            smtp_server_entry = tk.Entry(manual_dialog, width=40)
            smtp_server_entry.pack(padx=20, pady=5)
            
            tk.Label(manual_dialog, text="Порт (обычно 587):", bg=theme.get("bg_color"), fg=theme.get("fg_color")).pack(anchor="w", padx=20)
            port_entry = tk.Entry(manual_dialog, width=40)
            port_entry.insert(0, "587")
            port_entry.pack(padx=20, pady=5)
            
            result = {'confirmed': False, 'server': '', 'port': 587}
            
            def confirm():
                result['confirmed'] = True
                result['server'] = smtp_server_entry.get().strip()
                try:
                    result['port'] = int(port_entry.get().strip())
                except:
                    result['port'] = 587
                manual_dialog.destroy()
            
            tk.Button(manual_dialog, text="Подтвердить", command=confirm,
                     bg=theme.get("success_color"), fg="white").pack(pady=15)
            
            feedback_window.wait_window(manual_dialog)
            
            if not result['confirmed'] or not result['server']:
                status_label.config(text="⚠️ Отправка отменена: не указаны SMTP-настройки", fg="orange")
                return
            
            smtp_server = result['server']
            smtp_port = result['port']
            use_tls = True
        else:
            smtp_server, smtp_port, use_tls, requires_app_password = smtp_settings
            if requires_app_password:
                info_label.config(text="ℹ️ Для Gmail требуется пароль приложения, а не обычный пароль")
        
        # Блокируем кнопки на время отправки
        send_btn.config(state="disabled", text="⏳ ОТПРАВКА...")
        cancel_btn.config(state="disabled")
        status_label.config(text="⏳ Отправка письма...", fg="orange")
        feedback_window.update()
        
        try:
            msg = MIMEMultipart()
            msg["From"] = user_email
            msg["To"] = target_email
            msg["Subject"] = f"[Planner_Blender_3D] {subject_type} от {name}"
            
            body = f"""
🌟 НОВОЕ ОБРАЩЕНИЕ 🌟

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 Отправитель: {name}
📧 Почта: {user_email}
📋 Тип: {subject_type}
📅 Дата: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
💻 Версия: {current_version}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 СООБЩЕНИЕ:

{message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ответ можно отправить на почту: {user_email}

Спасибо за обратную связь! ✨
"""
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if use_tls:
                    server.starttls()
                server.login(user_email, user_password)
                server.sendmail(user_email, target_email, msg.as_string())
            
            status_label.config(text="✅ Письмо успешно отправлено! Спасибо!", fg=theme.get("success_color"))
            send_btn.config(state="normal", text="✉️ ОТПРАВИТЬ")
            cancel_btn.config(state="normal")
            
            # Очищаем только сообщение, имя и почту оставляем если сохранены
            message_text.delete("1.0", tk.END)
            if not save_password:
                name_entry.delete(0, tk.END)
                email_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
            
            feedback_window.after(2000, feedback_window.destroy)
            
        except smtplib.SMTPAuthenticationError:
            status_label.config(text="❌ Ошибка: Неверная почта или пароль", fg="red")
            send_btn.config(state="normal", text="✉️ ОТПРАВИТЬ")
            cancel_btn.config(state="normal")
        except smtplib.SMTPException as e:
            status_label.config(text=f"❌ SMTP ошибка: {str(e)[:40]}...", fg="red")
            send_btn.config(state="normal", text="✉️ ОТПРАВИТЬ")
            cancel_btn.config(state="normal")
        except Exception as e:
            error_msg = str(e)
            status_label.config(text=f"❌ Ошибка: {error_msg[:40]}...", fg="red")
            send_btn.config(state="normal", text="✉️ ОТПРАВИТЬ")
            cancel_btn.config(state="normal")
            print(f"[EMAIL ERROR] {e}")
    
    def cancel():
        feedback_window.destroy()
    
    send_btn = tk.Button(
        btn_frame, 
        text="✉️ ОТПРАВИТЬ", 
        font=("Arial", 11, "bold"),
        bg=theme.get("success_color"), 
        fg="white",
        relief="raised",
        bd=2,
        padx=20,
        pady=5,
        cursor="hand2",
        command=send_feedback
    )
    send_btn.pack(side="left", padx=5, expand=True, fill="x")
    
    cancel_btn = tk.Button(
        btn_frame, 
        text="❌ ОТМЕНА", 
        font=("Arial", 11, "bold"),
        bg=theme.get("error_color"), 
        fg="white",
        relief="raised",
        bd=2,
        padx=20,
        pady=5,
        cursor="hand2",
        command=cancel
    )
    cancel_btn.pack(side="right", padx=5, expand=True, fill="x")
    
    name_entry.focus()
    feedback_window.bind('<Return>', lambda e: send_feedback())
    feedback_window.bind('<Escape>', lambda e: cancel())