from flask import Flask, render_template, request, redirect
from database import create_database
import sqlite3
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

create_database()


@app.route("/")
def home():

    connection = sqlite3.connect("projects.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Dashboard statistics

    cursor.execute("SELECT COUNT(*) FROM projects")
    total_projects = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks")
    dashboard_total_tasks = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE status = 'Completed'
    """)
    dashboard_completed_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM files")
    total_files = cursor.fetchone()[0]

    # Get all projects

    cursor.execute("""
        SELECT * FROM projects
        ORDER BY id DESC
    """)

    projects = cursor.fetchall()

    project_data = []

    # Calculate progress for every project

    for project in projects:

        cursor.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
        """, (project["id"],))

        total_project_tasks = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE project_id = ?
            AND status = 'Completed'
        """, (project["id"],))

        completed_project_tasks = cursor.fetchone()[0]

        if total_project_tasks > 0:

            progress = int(
                (completed_project_tasks / total_project_tasks) * 100
            )

        else:

            progress = 0

        project_data.append({
            "project": project,
            "progress": progress,
            "total_tasks": total_project_tasks,
            "completed_tasks": completed_project_tasks
        })

    connection.close()

    return render_template(
        "index.html",
        projects=project_data,
        total_projects=total_projects,
        total_tasks=dashboard_total_tasks,
        completed_tasks=dashboard_completed_tasks,
        total_files=total_files
    )


@app.route("/create-project", methods=["GET", "POST"])
def create_project():

    if request.method == "POST":

        project_name = request.form["projectName"]
        description = request.form["description"]
        start_date = request.form["startDate"]
        deadline = request.form["deadline"]
        members = request.form["members"]
        technologies = request.form["technologies"]
        objectives = request.form["objectives"]

        connection = sqlite3.connect("projects.db")

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO projects
            (
                project_name,
                description,
                start_date,
                deadline,
                members,
                technologies,
                objectives
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_name,
            description,
            start_date,
            deadline,
            members,
            technologies,
            objectives
        ))

        connection.commit()

        connection.close()

        return "Project created successfully!"

    return render_template("create_project.html")
@app.route("/projects")
def projects():

    connection = sqlite3.connect("projects.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM projects
        ORDER BY id DESC
    """)

    projects = cursor.fetchall()

    connection.close()

    return render_template(
        "projects.html",
        projects=projects
    )

@app.route("/project/<int:project_id>")
def project_details(project_id):

    connection = sqlite3.connect("projects.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    )

    project = cursor.fetchone()

    connection.close()

    if project is None:
        return "Project not found"

    return render_template(
        "project_details.html",
        project=project
    )


@app.route("/tasks")
def tasks():

    connection = sqlite3.connect("projects.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT tasks.*, projects.project_name
        FROM tasks
        JOIN projects ON tasks.project_id = projects.id
        ORDER BY tasks.id DESC
    """)

    tasks = cursor.fetchall()

    connection.close()

    return render_template(
        "tasks.html",
        tasks=tasks
    )


@app.route("/files")
def files():

    connection = sqlite3.connect("projects.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT files.*, projects.project_name
        FROM files
        JOIN projects ON files.project_id = projects.id
        ORDER BY files.id DESC
    """)

    files = cursor.fetchall()

    connection.close()

    return render_template(
        "files.html",
        files=files
    )


@app.route("/upload-file", methods=["GET", "POST"])
def upload_file():

    connection = sqlite3.connect("projects.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    if request.method == "POST":

        project_id = request.form["project_id"]
        uploaded_by = request.form["uploaded_by"]

        file = request.files["file"]

        if file and file.filename:

            os.makedirs("uploads", exist_ok=True)

            file_name = secure_filename(file.filename)

            file_path = os.path.join(
                "uploads",
                file_name
            )

            file.save(file_path)

            cursor.execute("""
                INSERT INTO files
                (
                    project_id,
                    file_name,
                    file_path,
                    uploaded_by
                )
                VALUES (?, ?, ?, ?)
            """, (
                project_id,
                file_name,
                file_path,
                uploaded_by
            ))

            connection.commit()

            connection.close()

            return "File uploaded successfully!"

    cursor.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    )

    projects = cursor.fetchall()

    connection.close()

    return render_template(
        "upload_file.html",
        projects=projects
    )


@app.route("/documentation", methods=["GET", "POST"])
def documentation():

    connection = sqlite3.connect("projects.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    if request.method == "POST":

        project_id = request.form["project_id"]
        overview = request.form["overview"]
        requirements = request.form["requirements"]
        technical_details = request.form["technical_details"]
        notes = request.form["notes"]

        cursor.execute("""
            INSERT INTO documentation
            (
                project_id,
                overview,
                requirements,
                technical_details,
                notes
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            project_id,
            overview,
            requirements,
            technical_details,
            notes
        ))

        connection.commit()

        connection.close()

        return "Documentation saved successfully!"

    cursor.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    )

    projects = cursor.fetchall()

    connection.close()

    return render_template(
        "documentation.html",
        projects=projects
    )
@app.route("/view-documentation")
def view_documentation():

    connection = sqlite3.connect("projects.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT documentation.*, projects.project_name
        FROM documentation
        JOIN projects
        ON documentation.project_id = projects.id
        ORDER BY documentation.id DESC
    """)

    documentation = cursor.fetchall()

    connection.close()

    return render_template(
        "view_documentation.html",
        documentation=documentation
    )

@app.route("/create-task", methods=["GET", "POST"])
def create_task():

    connection = sqlite3.connect("projects.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    if request.method == "POST":

        project_id = request.form["project_id"]
        task_name = request.form["task_name"]
        description = request.form["description"]
        assigned_to = request.form["assigned_to"]
        status = request.form["status"]

        cursor.execute("""
            INSERT INTO tasks
            (
                project_id,
                task_name,
                description,
                assigned_to,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            project_id,
            task_name,
            description,
            assigned_to,
            status
        ))

        connection.commit()

        connection.close()

        return "Task created successfully!"

    cursor.execute(
        "SELECT * FROM projects ORDER BY id DESC"
    )

    projects = cursor.fetchall()

    connection.close()

    return render_template(
        "create_task.html",
        projects=projects
    )


@app.route("/update-task-status/<int:task_id>", methods=["POST"])
def update_task_status(task_id):

    status = request.form["status"]

    connection = sqlite3.connect("projects.db")

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET status = ?
        WHERE id = ?
    """, (
        status,
        task_id
    ))

    connection.commit()

    connection.close()

    return redirect("/tasks")


if __name__ == "__main__":
    app.run(debug=True)