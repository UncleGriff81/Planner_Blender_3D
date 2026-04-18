"""
Planner_Blender_3D - Главный файл запуска
"""
import sys
import os
import tkinter as tk

# Добавляем пути для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импорты из модулей
from core.app_init import auto_install_packages, setup_mutex, suppress_console
from core.startup_manager import is_in_startup
from ui.top_panel import create_top_panel
from ui.filter_panel import create_filter_panel
from ui.buttons_panel import create_buttons_panel
from ui.theme_selector import create_theme_selector
from handlers.project_handlers import refresh_projects_list, update_monitor_dict
from handlers.report_handlers import generate_reports
from handlers.update_handlers import check_for_updates
from monitors.file_monitor_starter import start_file_monitoring
from monitors.process_monitor_starter import start_process_monitoring
from dialogs.create_project_dialog import create_project_dialog
from dialogs.feedback_dialog import show_feedback_form
from theme_manager import ThemeManager
from auto_saver import AutoSaver
from path_utils import load_config
from db_manager import init_db, get_all_projects, update_project_time
from task_plan import Project
from ui_components import set_projects_list, set_update_monitor_callback
from date_utils import show_notification

# Константы
WIDTH = 1100
HEIGHT = 600
TITLE = "Planner_Blender_3D"
CURRENT_VERSION = "1.0.1"
TARGET_EMAIL = "bobikovd81@gmail.com"  # Почта разработчика (неизменна)

# Глобальные переменные
root = None
theme = None
canvas = None
projects_inner_frame = None
projects_objects_list = []
task_frames_list = []
auto_saver = None
sort_var = None
urgent_var = None
developers_label = None
_pystray_available = False
PROJECTS_DICT_MONITOR = {}
tray_icon = None
is_minimized_to_tray = False

# Глобальные ссылки на UI элементы для обновления темы
_top_panel = None
_filter_frame = None
_buttons_frame = None
_theme_container = None
_theme_frame = None
_theme_dropdown = None
_info_btn = None


def refresh_ui():
    """Обновляет UI после смены темы"""
    global root, task_frames_list, developers_label, _top_panel, _filter_frame, _buttons_frame, _theme_container, _theme_frame, _theme_dropdown, _info_btn
    
    if root:
        theme_manager = ThemeManager()
        theme_manager.refresh_ui(
            root, None, task_frames_list,
            _top_panel, _filter_frame, _buttons_frame,
            _theme_container, _theme_frame, _theme_dropdown, _info_btn,
            developers_label,
            refresh_projects_callback=refresh_projects_list_func
        )


def setup_main_window():
    """Создаёт и настраивает главное окно"""
    global root, theme, canvas, projects_inner_frame, sort_var, urgent_var, developers_label, _pystray_available
    global _top_panel, _filter_frame, _buttons_frame, _theme_container, _theme_frame, _theme_dropdown, _info_btn
    
    # Проверяем доступность pystray
    try:
        import pystray
        _pystray_available = True
    except ImportError:
        _pystray_available = False
    
    # Инициализация темы
    theme_manager = ThemeManager()
    theme = theme_manager
    
    # Создание окна
    root = tk.Tk()
    root.title(TITLE)
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(True, True)
    root.configure(bg=theme.get("bg_color"))
    
    # Установка иконки
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Planner_Blender_3D")
        except:
            pass
    
    # Основной контейнер
    main_container = tk.Frame(root, bg=theme.get("bg_color"))
    main_container.pack(fill="both", expand=True)
    
    # Верхняя панель
    _top_panel = create_top_panel(main_container, root, theme, 
                                 lambda: show_feedback_form(root, theme, TARGET_EMAIL, CURRENT_VERSION), 
                                 CURRENT_VERSION)
    _top_panel.grid(row=0, column=0, columnspan=2, pady=(5, 5), sticky="ew")
    
    # Разделитель
    separator = tk.Frame(main_container, height=2, bg=theme.get("accent_color"))
    separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
    
    # Панель фильтрации
    _filter_frame, sort_var, urgent_var = create_filter_panel(main_container, theme, 
                                                lambda: refresh_projects_list_func())
    
    # Панель кнопок
    _buttons_frame = create_buttons_panel(
        main_container, theme, 
        create_project=lambda: create_project_dialog(root, theme, projects_objects_list, auto_saver, auto_save_callback, 
                                                      lambda: refresh_projects_list_func(), 
                                                      lambda: update_monitor_dict(projects_objects_list, PROJECTS_DICT_MONITOR), 
                                                      show_notification),
        generate_reports=lambda: generate_reports(root, theme, projects_objects_list, show_notification),
        show_statistics=lambda: show_statistics(),
        check_updates=lambda: check_for_updates(CURRENT_VERSION, silent=False),
        toggle_startup=lambda: toggle_startup(),
        minimize_to_tray=lambda: minimize_to_tray(),
        is_pystray_available=_pystray_available
    )
    
    # Контейнер для выбора темы
    _theme_container = tk.Frame(main_container, bg=theme.get("bg_color"))
    _theme_container.grid(row=3, column=1, sticky="e", padx=10, pady=(0, 15))
    
    _theme_frame, _theme_dropdown, _info_btn, developers_label = create_theme_selector(_theme_container, theme, theme_manager, refresh_ui)
    _theme_frame.pack(side="right")
    
    # Контейнер с проектами
    projects_outer_frame = tk.Frame(main_container, bg=theme.get("bg_color"), bd=2, relief="groove")
    projects_outer_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 5))
    
    main_container.grid_rowconfigure(4, weight=1)
    main_container.grid_columnconfigure(0, weight=1)
    main_container.grid_columnconfigure(1, weight=0)
    
    projects_container = tk.Frame(projects_outer_frame, bg=theme.get("bg_color"))
    projects_container.pack(fill="both", expand=True, padx=2, pady=2)
    
    canvas = tk.Canvas(projects_container, bg=theme.get("bg_color"), highlightthickness=0)
    scrollbar = tk.Scrollbar(projects_container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    projects_inner_frame = tk.Frame(canvas, bg=theme.get("bg_color"))
    canvas.create_window((0, 0), window=projects_inner_frame, anchor="nw", width=canvas.winfo_reqwidth())
    
    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def on_canvas_configure(event):
        canvas.itemconfig(1, width=event.width)
    
    projects_inner_frame.bind("<Configure>", configure_scroll_region)
    canvas.bind("<Configure>", on_canvas_configure)
    
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    canvas.bind("<MouseWheel>", on_mousewheel)
    
    return root, canvas, projects_inner_frame


def refresh_projects_list_func():
    """Обёртка для refresh_projects_list"""
    global projects_inner_frame, projects_objects_list, task_frames_list, sort_var, urgent_var, canvas
    
    from ui_components import create_task_frame
    
    refresh_projects_list(
        projects_inner_frame, projects_objects_list, task_frames_list,
        sort_var, urgent_var, canvas,
        lambda parent, proj, frames, callback: create_task_frame(parent, proj, frames, callback)
    )


def auto_save_callback(project_id, elapsed_time):
    """Колбэк для автосохранения"""
    update_project_time(project_id, elapsed_time)


def show_statistics():
    """Показывает статистику"""
    from tkinter import messagebox
    
    total_time = 0
    active_projects = 0
    
    for project in projects_objects_list:
        total_time += project.get_total_seconds()
        if project.timer_running:
            active_projects += 1
    
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    
    stats_text = f"📊 Статистика:\n\n"
    stats_text += f"📁 Всего проектов: {len(projects_objects_list)}\n"
    stats_text += f"▶ Активных таймеров: {active_projects}\n"
    stats_text += f"⏱ Общее время: {hours} ч {minutes} мин\n"
    
    messagebox.showinfo("Статистика", stats_text)


def toggle_startup():
    """Переключает автозагрузку"""
    from core.startup_manager import add_to_startup, remove_from_startup, is_in_startup
    
    if is_in_startup():
        remove_from_startup()
    else:
        add_to_startup()


def minimize_to_tray():
    """Сворачивает в трей"""
    global tray_icon, is_minimized_to_tray, root
    
    if not _pystray_available:
        root.iconify()
        return
    
    if is_minimized_to_tray:
        return
    
    is_minimized_to_tray = True
    root.withdraw()
    
    try:
        from PIL import Image
        import pystray as _pystray
        
        tray_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        if os.path.exists(tray_icon_path):
            image = Image.open(tray_icon_path)
            image = image.resize((64, 64))
        else:
            image = Image.new('RGB', (64, 64), color='#ff8c00')
        
        def show_window():
            global is_minimized_to_tray, tray_icon
            root.deiconify()
            root.lift()
            root.focus_force()
            is_minimized_to_tray = False
            if tray_icon:
                tray_icon.stop()
        
        def quit_app():
            global tray_icon, is_minimized_to_tray
            if tray_icon:
                tray_icon.stop()
            on_closing()
        
        menu = _pystray.Menu(
            _pystray.MenuItem("Показать окно", show_window),
            _pystray.MenuItem("Выход", quit_app)
        )
        
        tray_icon = _pystray.Icon("Planner_Blender_3D", image, TITLE, menu)
        tray_icon.run_detached()
    except Exception as e:
        print(f"[TRAY] Ошибка: {e}")
        root.iconify()


def on_closing():
    """Закрытие программы с проверкой активных таймеров"""
    from tkinter import messagebox
    
    # Проверяем, есть ли активные таймеры
    active_projects = [p for p in projects_objects_list if p.timer_running]
    
    if active_projects:
        # Формируем список проектов с активными таймерами
        project_names = "\n".join([f"  • {p.name}" for p in active_projects])
        
        # Показываем предупреждение
        result = messagebox.askyesno(
            "⚠️ Активные таймеры",
            f"Обнаружены проекты с активными таймерами:\n\n{project_names}\n\n"
            f"⚠️ ВНИМАНИЕ: Blender всё ещё открыт с этими файлами!\n\n"
            f"Если вы закроете программу сейчас, текущее время работы НЕ БУДЕТ СОХРАНЕНО,\n"
            f"так как сессия работы ещё не завершена.\n\n"
            f"Рекомендуется сначала закрыть файлы в Blender или остановить таймеры.\n\n"
            f"Всё равно закрыть программу?",
            icon='warning'
        )
        
        if not result:
            return  # Отмена закрытия
    
    # Закрываем программу
    print("[INFO] Закрытие программы...")
    if auto_saver:
        auto_saver.stop()
    root.destroy()


def load_projects():
    """Загружает проекты из БД"""
    global projects_objects_list, auto_saver, PROJECTS_DICT_MONITOR
    
    PROJECTS_DICT_MONITOR = {}
    init_db()
    projects_list_from_db = get_all_projects()
    
    auto_saver = AutoSaver(load_config().get("auto_save_interval", 30))
    
    for proj_dict in projects_list_from_db:
        loaded_project_obj = Project(
            id=proj_dict['id'],
            name=proj_dict['name'],
            description=proj_dict['description'],
            blend_file=proj_dict['blend_file'],
            creation_date=proj_dict['creation_date'],
            elapsed_time=float(proj_dict['elapsed_time']),
            blender_path=proj_dict.get('blender_path', ''),
            deadline_date=proj_dict.get('deadline_date', ''),
            deadline_days=proj_dict.get('deadline_days', 0)
        )
        loaded_project_obj.auto_save_callback = auto_save_callback
        
        if proj_dict.get('full_file_path'):
            loaded_project_obj.set_full_file_path(proj_dict['full_file_path'])
        
        projects_objects_list.append(loaded_project_obj)
        auto_saver.add_project(loaded_project_obj)
    
    set_projects_list(projects_objects_list)
    set_update_monitor_callback(lambda: update_monitor_dict(projects_objects_list, PROJECTS_DICT_MONITOR))
    
    refresh_projects_list_func()


def main():
    """Главная функция запуска"""
    global root, projects_objects_list, auto_saver
    
    # Подавление консоли для EXE
    suppress_console()
    
    # Проверка единственного экземпляра
    setup_mutex()
    
    # Автоустановка библиотек
    auto_install_packages()
    
    # Настройка главного окна
    root, canvas, projects_inner_frame = setup_main_window()
    
    # Загрузка проектов
    load_projects()
    
    # Запуск автосохранения
    if auto_saver:
        auto_saver.start()
    
    # Запуск мониторингов
    start_file_monitoring(root)
    start_process_monitoring()
    
    # Настройка закрытия
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Проверка обновлений при запуске
    root.after(3000, lambda: check_for_updates(CURRENT_VERSION, silent=True))
    
    print("[INFO] Запуск главного окна программы...")
    root.mainloop()
    print("[INFO] Программа завершена")


if __name__ == "__main__":
    main()