import sqlite3
from subjects_data import SUBJECTS_DATA

DB_NAME = "database.db"


def create_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # جدول السنين
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS years (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)

    # جدول المواد
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY (year_id) REFERENCES years (id)
    )
    """)

    # جدول المحتوى
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        file_id TEXT,
        link TEXT,
        FOREIGN KEY (subject_id) REFERENCES subjects (id)
    )
    """)

    conn.commit()
    conn.close()


def insert_initial_data():
    conn = create_connection()
    cursor = conn.cursor()

    # إدخال السنين
    years = [
        "First Year",
        "Second Year",
        "Third Year",
        "Fourth Year",
        "Fifth Year"
    ]

    for year in years:
        cursor.execute(
            "INSERT OR IGNORE INTO years (name) VALUES (?)",
            (year,)
        )

    conn.commit()

    # نجيب IDs السنين
    cursor.execute("SELECT id, name FROM years")
    years_data = {
        name: year_id
        for year_id, name in cursor.fetchall()
    }

    # إدخال المواد
    for year_name, subjects in SUBJECTS_DATA.items():

        year_id = years_data[year_name]

        for subject in subjects:

            cursor.execute("""
                INSERT OR IGNORE INTO subjects
                (year_id, name)
                VALUES (?, ?)
            """, (year_id, subject))
    cursor.execute("SELECT COUNT(*) FROM subjects")
    print(cursor.fetchone())
    conn.commit()
    conn.close()

def get_years():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM years")
    years = cursor.fetchall()

    conn.close()
    return years


def get_subjects_by_year(year_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM subjects WHERE year_id = ?", (year_id,))
    subjects = cursor.fetchall()

    conn.close()
    return subjects

def get_subject_id_by_name(subject_name):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM subjects WHERE name = ? LIMIT 1", (subject_name,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    return None


def get_materials_by_subject_and_type(subject_id, material_type):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, title
    FROM materials
    WHERE subject_id = ? AND type = ?
""", (subject_id, material_type))

    materials = cursor.fetchall()
    conn.close()

    return materials

def insert_sample_materials():
    conn = create_connection()
    cursor = conn.cursor()

    sample_data = {
        "Anatomy": {
            "lecture": ["Lecture 1 PDF", "Lecture 2 PDF", "Lecture 3 PDF"],
            "record": ["Record 1 Video", "Record 2 Video"],
            "assignment": ["Assignment 1", "Assignment 2"]
        },
        "Physiology": {
            "lecture": ["Lecture 1 PDF", "Lecture 2 PDF"],
            "record": ["Record 1 Video"],
            "assignment": ["Assignment 1"]
        },
        "Biomechanics": {
            "lecture": ["Lecture 1 PDF", "Lecture 2 PDF"],
            "record": ["Record 1 Video", "Record 2 Video"],
            "assignment": ["Assignment 1", "Assignment 2"]
        }
    }

    for subject_name, materials in sample_data.items():
        subject_id = get_subject_id_by_name(subject_name)

        if subject_id:
            for material_type, titles in materials.items():
                for title in titles:
                    cursor.execute("""
                        INSERT INTO materials (subject_id, type, title)
                        VALUES (?, ?, ?)
                    """, (subject_id, material_type, title))

    conn.commit()
    conn.close()

def get_material_by_id(material_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, subject_id, type, title, file_id, link
        FROM materials
        WHERE id = ?
    """, (material_id,))

    material = cursor.fetchone()
    conn.close()

    return material

def add_material(subject_id, material_type, title, file_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO materials(subject_id, type, title, file_id)
        VALUES (?, ?, ?, ?)
    """, (subject_id, material_type, title, file_id))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    insert_initial_data()
    insert_sample_materials()
    print("Database initialized with years, subjects, and materials successfully.")

def add_material(subject_id, material_type, title, file_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO materials (subject_id, type, title, file_id)
        VALUES (?, ?, ?, ?)
    """, (subject_id, material_type, title, file_id))

    conn.commit()
    conn.close()
