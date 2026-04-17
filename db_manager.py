import sqlite3
import os
from path_utils import get_db_folder

def get_db_path():
    db_folder = get_db_folder()
    return os.path.join(db_folder, "projects.db")

DB_FILE = get_db_path()

def init_db():
    """Инициализирует базу данных и создаёт все необходимые таблицы"""
    db_folder = os.path.dirname(DB_FILE)
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        print(f"[DB] Создана папка: {db_folder}")

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Таблица проектов
    c.execute("""CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                blend_file TEXT NOT NULL,
                creation_date TEXT NOT NULL,
                elapsed_time REAL DEFAULT 0,
                blender_path TEXT DEFAULT '',
                full_file_path TEXT DEFAULT '',
                deadline_date TEXT DEFAULT '',
                deadline_days INTEGER DEFAULT 0)
                """)

    # Таблица для сеансов работы
    c.execute("""CREATE TABLE IF NOT EXISTS work_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration REAL DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE)
                """)

    # Миграция для старых таблиц (добавляем колонки, если их нет)
    columns_to_check = ['deadline_date', 'deadline_days', 'blender_path', 'full_file_path']
    for col in columns_to_check:
        try:
            c.execute(f"ALTER TABLE projects ADD COLUMN {col} TEXT DEFAULT ''")
            print(f"[DB] Добавлена колонка {col}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()
    print(f"[DB] База данных инициализирована: {DB_FILE}")

def add_work_session(project_id, start_time, end_time, duration):
    """Добавляет сеанс работы над проектом"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO work_sessions (project_id, start_time, end_time, duration)
                VALUES (?, ?, ?, ?)""", (project_id, start_time, end_time, duration))
    conn.commit()
    conn.close()
    print(f"[DB] Добавлен сеанс работы для проекта {project_id}: {duration:.0f} сек")

def get_work_sessions(project_id):
    """Возвращает все сеансы работы по проекту"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM work_sessions WHERE project_id = ? ORDER BY start_time DESC", (project_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_work_sessions(project_id):
    """Удаляет все сеансы работы проекта (при удалении проекта)"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM work_sessions WHERE project_id = ?", (project_id,))
    conn.commit()
    conn.close()

def get_daily_stats(project_id):
    """Возвращает статистику по дням для проекта: дата, суммарная длительность, кол-во сеансов"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT DATE(start_time) as day, 
               SUM(duration) as total_duration,
               COUNT(*) as sessions_count
        FROM work_sessions 
        WHERE project_id = ? 
        GROUP BY DATE(start_time)
        ORDER BY day DESC
    """, (project_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_project(project_data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO projects (name, description, blend_file, creation_date, elapsed_time, 
                blender_path, full_file_path, deadline_date, deadline_days)
                VALUES (:name, :description, :blend_file, :creation_date, :elapsed_time, 
                :blender_path, :full_file_path, :deadline_date, :deadline_days)""",
              project_data)
    project_id = c.lastrowid
    conn.commit()
    conn.close()
    print(f"[DB] Проект сохранен с ID: {project_id}")
    return project_id

def get_all_projects():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("PRAGMA table_info(projects)")
    columns = [col[1] for col in c.fetchall()]

    select_cols = ['id', 'name', 'description', 'blend_file', 'creation_date', 'elapsed_time']
    if 'blender_path' in columns:
        select_cols.append('blender_path')
    if 'full_file_path' in columns:
        select_cols.append('full_file_path')
    if 'deadline_date' in columns:
        select_cols.append('deadline_date')
    if 'deadline_days' in columns:
        select_cols.append('deadline_days')

    query = f"SELECT {', '.join(select_cols)} FROM projects ORDER BY id"
    c.execute(query)
    rows = c.fetchall()
    conn.close()

    result = []
    for row in rows:
        proj_dict = dict(row)
        for key in ['blender_path', 'full_file_path', 'deadline_date']:
            if key not in proj_dict:
                proj_dict[key] = ''
        if 'deadline_days' not in proj_dict:
            proj_dict['deadline_days'] = 0
        result.append(proj_dict)
    return result

def delete_project_from_db(project_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM work_sessions WHERE project_id=?", (project_id,))
    c.execute("DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    conn.close()
    print(f"[DB] Проект {project_id} удален из БД вместе с сеансами")

def update_project_time(project_id, elapsed_time):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE projects SET elapsed_time = ? WHERE id = ?", (elapsed_time, project_id))
    conn.commit()
    conn.close()

def update_project_blender_path(project_id, blender_path):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE projects SET blender_path = ? WHERE id = ?", (blender_path, project_id))
    conn.commit()
    conn.close()

def update_project_file_path(project_id, full_file_path):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE projects SET full_file_path = ? WHERE id = ?", (full_file_path, project_id))
    conn.commit()
    conn.close()

def update_project_deadline(project_id, deadline_date, deadline_days):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE projects SET deadline_date = ?, deadline_days = ? WHERE id = ?",
              (deadline_date, deadline_days, project_id))
    conn.commit()
    conn.close()