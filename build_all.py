"""
build_all.py - Полная автоматизация сборки
Запуск: python build_all.py
"""

import os
import subprocess
import shutil

# ========== НАСТРОЙКИ (проверь пути!) ==========
INNO_SETUP_PATH = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
# ===============================================

PROJECT_NAME = "Planner_Blender_3D"
VERSION = "1.0.1"

def print_header(text):
    """Красивый вывод заголовка"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def run_command(cmd, description):
    """Выполняет команду и проверяет успешность"""
    print(f"\n▶ {description}...")
    try:
        result = subprocess.run(cmd, check=True, shell=True)
        print(f"✅ {description} - выполнено")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {description}")
        print(f"   Команда: {cmd}")
        print(f"   Код ошибки: {e.returncode}")
        return False

def main():
    print_header(f"СБОРКА {PROJECT_NAME} v{VERSION}")
    
    # ===== ШАГ 1: Очистка старых файлов =====
    print_header("1. ОЧИСТКА")
    folders_to_remove = ["build", "dist", "Output"]
    for folder in folders_to_remove:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Удалена папка: {folder}")
    
    # Удаляем временные .c и .pyd файлы (оставляем исходники)
    for file in os.listdir("."):
        if file.endswith(".c") or (file.endswith(".pyd") and file != "setup.pyd"):
            os.remove(file)
            print(f"   Удалён файл: {file}")
    
    # ===== ШАГ 2: Компиляция в .pyd (защита) =====
    print_header("2. ЗАЩИТА КОДА (Cython)")
    if not run_command("python setup.py build_ext --inplace", "Компиляция модулей"):
        print("⚠️ Продолжаем без защиты...")
    
    # Удаляем временные .c файлы
    for file in os.listdir("."):
        if file.endswith(".c"):
            os.remove(file)
            print(f"   Удалён временный файл: {file}")
    
    # ===== ШАГ 3: Сборка EXE (PyInstaller) =====
    print_header("3. СБОРКА EXE (PyInstaller)")
    pyinstaller_cmd = (
        f'pyinstaller --onefile --windowed --icon=icon.ico --name={PROJECT_NAME} '
        f'--add-data "themes.json;." '
        f'--add-data "icon.ico;." '
        f'--add-data "icon.png;." '
        f'--add-data "logo.png;." '
        f'main.py'
    )
    
    if not run_command(pyinstaller_cmd, "Сборка EXE"):
        print("❌ Критическая ошибка! Сборка прервана.")
        return
    
    # ===== ШАГ 4: Создание установщика (Inno Setup) =====
    print_header("4. СОЗДАНИЕ УСТАНОВЩИКА (Inno Setup)")
    
    if not os.path.exists(INNO_SETUP_PATH):
        print(f"⚠️ Inno Setup не найден по пути: {INNO_SETUP_PATH}")
        print("   Установщик не будет создан.")
        print("   Скачай Inno Setup: https://jrsoftware.org/isdl.php")
    elif not os.path.exists("installer_script.iss"):
        print("⚠️ Файл installer_script.iss не найден!")
    else:
        run_command(f'"{INNO_SETUP_PATH}" installer_script.iss', "Компиляция установщика")
    
    # ===== ШАГ 5: Финальный отчёт =====
    print_header("5. РЕЗУЛЬТАТ")
    
    exe_path = f"dist/{PROJECT_NAME}.exe"
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✅ EXE файл: {exe_path} ({size_mb:.1f} МБ)")
    else:
        print(f"❌ EXE файл не найден: {exe_path}")
    
    setup_path = "Output/Planner_Blender_3D_Setup.exe"
    if os.path.exists(setup_path):
        size_mb = os.path.getsize(setup_path) / (1024 * 1024)
        print(f"✅ Установщик: {setup_path} ({size_mb:.1f} МБ)")
    
    print("\n🎉 ГОТОВО! Загружай установщик на GitHub в раздел Releases.")
    print("=" * 60)

if __name__ == "__main__":
    main()