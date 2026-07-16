"""
database.py
------------
SQLite integration for the AI Resume Builder.

Creates (on first run) a `resume_data.db` file with 4 tables:
    - resumes     (one row per "save" — personal info + about_me + skills)
    - education   (many rows per resume, linked by resume_id)
    - experience  (many rows per resume, linked by resume_id)
    - projects    (many rows per resume, linked by resume_id)

Open `resume_data.db` in VS Code with the "SQLite Viewer" extension anytime
to see the saved data in a table/grid view.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resume_data.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables if they don't already exist. Safe to call every app run."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            job_title TEXT,
            email TEXT,
            phone TEXT,
            linkedin TEXT,
            github TEXT,
            address TEXT,
            about_me TEXT,
            skills TEXT,
            template_key TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            degree TEXT,
            institution TEXT,
            year TEXT,
            gpa TEXT,
            FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            role TEXT,
            company TEXT,
            duration TEXT,
            description TEXT,
            FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            title TEXT,
            link TEXT,
            description TEXT,
            FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def save_resume(context: dict, template_key: str = ""):
    """
    Insert one full resume snapshot (personal info + education + experience
    + projects) into the database. Called whenever the user clicks
    'Preview Resume' or 'Generate PDF'.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO resumes
            (name, job_title, email, phone, linkedin, github, address,
             about_me, skills, template_key, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            context.get("name", ""),
            context.get("job_title", ""),
            context.get("email", ""),
            context.get("phone", ""),
            context.get("linkedin", ""),
            context.get("github", ""),
            context.get("address", ""),
            context.get("about_me", ""),
            ", ".join(context.get("skills", [])),
            template_key,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    resume_id = cur.lastrowid

    for edu in context.get("education", []):
        cur.execute(
            "INSERT INTO education (resume_id, degree, institution, year, gpa) VALUES (?, ?, ?, ?, ?)",
            (resume_id, edu.get("degree", ""), edu.get("institution", ""), edu.get("year", ""), edu.get("gpa", "")),
        )

    for exp in context.get("experience", []):
        cur.execute(
            "INSERT INTO experience (resume_id, role, company, duration, description) VALUES (?, ?, ?, ?, ?)",
            (resume_id, exp.get("role", ""), exp.get("company", ""), exp.get("duration", ""), exp.get("description", "")),
        )

    for proj in context.get("projects", []):
        cur.execute(
            "INSERT INTO projects (resume_id, title, link, description) VALUES (?, ?, ?, ?)",
            (resume_id, proj.get("title", ""), proj.get("link", ""), proj.get("description", "")),
        )

    conn.commit()
    conn.close()
    return resume_id
