import sqlite3


def create_database():

    connection = sqlite3.connect("projects.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            description TEXT NOT NULL,
            start_date TEXT,
            deadline TEXT,
            members TEXT,
            technologies TEXT,
            objectives TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            description TEXT,
            assigned_to TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            uploaded_by TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            overview TEXT,
            requirements TEXT,
            technical_details TEXT,
            notes TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    connection.commit()

    connection.close()