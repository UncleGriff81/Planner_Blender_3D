"""
setup.py - Компиляция ключевых модулей в .pyd для защиты кода
"""
from distutils.core import setup
from Cython.Build import cythonize
import os

# Список файлов, которые нужно защитить (вся логика программы)
files_to_protect = [
    "task_plan.py",              # Класс Project, таймер
    "db_manager.py",             # Работа с базой данных
    "date_utils.py",             # Дедлайны, даты
    "blender_utils.py",          # Утилиты Blender
    "blender_finder.py",         # Поиск Blender
    "blender_process_monitor.py", # Мониторинг процессов
    "file_monitor.py",           # Мониторинг файлов
    "path_utils.py",             # Утилиты путей
    "report_generator.py",       # Генерация отчётов
    "theme_manager.py",          # Управление темами
    "ui_components.py",          # UI компоненты
]

print(f"🔒 Защищаемые модули: {len(files_to_protect)} шт.")

setup(
    name="Planner_Blender_3D_Core",
    ext_modules=cythonize(files_to_protect, language_level=3, compiler_directives={'boundscheck': False}),
)