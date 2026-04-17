import os
import datetime
from path_utils import get_reports_folder
from db_manager import get_daily_stats

def generate_full_report(projects_list):
    reports_folder = get_reports_folder()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"full_report_{timestamp}.txt"
    filepath = os.path.join(reports_folder, filename)

    total_time = 0
    active_projects = 0
    overdue_projects = 0

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("         ПЛАНЕР BLENDER 3D — ОБЩИЙ ОТЧЁТ\n")
        f.write(f"         Дата генерации: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        for project in projects_list:
            total_seconds = project.get_total_seconds()
            total_time += total_seconds
            if project.timer_running:
                active_projects += 1
            deadline = project.get_deadline_date_obj()
            if deadline and deadline < datetime.datetime.now():
                overdue_projects += 1

        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)

        f.write("ОБЩАЯ СТАТИСТИКА\n")
        f.write("-" * 70 + "\n")
        f.write(f"  Всего проектов:          {len(projects_list)}\n")
        f.write(f"  Активных таймеров:        {active_projects}\n")
        f.write(f"  Общее время:             {hours} ч {minutes} мин ({total_time:.0f} сек)\n")
        f.write(f"  Просроченных проектов:    {overdue_projects}\n\n")

        f.write("ДЕТАЛИ ПО ПРОЕКТАМ\n")
        f.write("-" * 70 + "\n\n")

        for idx, project in enumerate(projects_list, 1):
            deadline = project.get_deadline_date_obj()
            deadline_str = deadline.strftime('%d.%m.%Y') if deadline else "Не указан"
            f.write(f"ПРОЕКТ #{idx}\n")
            f.write(f"  ID в БД:          {project.id}\n")
            f.write(f"  Название:         {project.name}\n")
            f.write(f"  Описание:         {project.description[:100]}{'...' if len(project.description) > 100 else ''}\n")
            f.write(f"  Время:            {project.get_formatted_time()}\n")
            f.write(f"  Дедлайн:          {deadline_str}\n")
            f.write(f"  Статус:           {'Активен' if project.timer_running else 'Остановлен'}\n")
            f.write(f"  Файл:             {project.blend_file}.blend\n")
            f.write("\n" + "-" * 50 + "\n\n")

    print(f"[REPORT] Создан общий отчёт: {filepath}")
    return filepath

def generate_project_report(project, display_number=None):
    reports_folder = get_reports_folder()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    safe_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    filename = f"project_{project.id}_{safe_name}_{timestamp}.txt"
    filepath = os.path.join(reports_folder, filename)

    total_seconds = project.get_total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    deadline = project.get_deadline_date_obj()
    deadline_str = deadline.strftime('%d.%m.%Y %H:%M') if deadline else "Не указан"
    from date_utils import get_time_left_string
    time_left = get_time_left_string(deadline) if deadline else "Не указан"

    display_num = display_number if display_number else project.id
    daily_stats = get_daily_stats(project.id)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write(f"         ОТЧЁТ ПО ПРОЕКТУ #{display_num}\n")
        f.write(f"         {project.name}\n")
        f.write(f"         Дата: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        f.write("ОСНОВНАЯ ИНФОРМАЦИЯ\n")
        f.write("-" * 70 + "\n")
        f.write(f"  Номер в списке:       {display_num}\n")
        f.write(f"  ID в БД:              {project.id}\n")
        f.write(f"  Название:             {project.name}\n")
        f.write(f"  Описание:             {project.description}\n")
        f.write(f"  Дата создания:        {project.creation_date}\n\n")

        f.write("ВРЕМЯ\n")
        f.write("-" * 70 + "\n")
        f.write(f"  Затрачено времени:    {project.get_formatted_time()}\n")
        f.write(f"  Всего секунд:         {total_seconds:.0f} сек\n")
        f.write(f"  В часах/минутах:      {hours} ч {minutes} мин {seconds} сек\n")
        f.write(f"  Статус таймера:       {'Активен' if project.timer_running else 'Остановлен'}\n\n")

        f.write("ДЕДЛАЙН\n")
        f.write("-" * 70 + "\n")
        f.write(f"  Дедлайн:              {deadline_str}\n")
        f.write(f"  Осталось:             {time_left}\n\n")

        f.write("ФАЙЛЫ\n")
        f.write("-" * 70 + "\n")
        f.write(f"  Имя файла:            {project.blend_file}.blend\n")
        f.write(f"  Путь к файлу:         {project.get_full_file_path() or 'Не создан'}\n\n")

        f.write("BLENDER\n")
        f.write("-" * 70 + "\n")
        f.write(f"  Версия Blender:       {os.path.basename(os.path.dirname(project.blender_path)) if project.blender_path else 'Не выбран'}\n")
        f.write(f"  Путь:                 {project.blender_path or 'Не выбран'}\n\n")

        f.write("ДНЕВНАЯ СТАТИСТИКА\n")
        f.write("-" * 70 + "\n")
        if daily_stats:
            f.write("  Дата         Время (чч:мм)   Сеансов\n")
            f.write("  " + "-" * 50 + "\n")
            for stat in daily_stats:
                day = stat['day']
                duration_seconds = stat['total_duration']
                dur_hours = int(duration_seconds // 3600)
                dur_minutes = int((duration_seconds % 3600) // 60)
                sessions = stat['sessions_count']
                f.write(f"  {day}   {dur_hours:02d}:{dur_minutes:02d}          {sessions}\n")
        else:
            f.write("  Нет записей о сеансах работы\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("              КОНЕЦ ОТЧЁТА\n")
        f.write("=" * 70 + "\n")

    print(f"[REPORT] Создан отчёт по проекту {project.id}: {filepath}")
    return filepath

def generate_all_reports(projects_list):
    reports = []
    reports.append(generate_full_report(projects_list))
    for idx, project in enumerate(projects_list, 1):
        reports.append(generate_project_report(project, display_number=idx))
    return reports