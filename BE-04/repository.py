import os, psycopg, sys
from psycopg.rows import dict_row

def get_db_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("CRITICAL ERROR: DATABASE_URL environment variable is either missing or not loaded.")
    return url

def setup_database():

    # Grab seed
    seed_file_path = "database/seed.sql"

    # If seed does not exist in path, exit
    if not os.path.exists(seed_file_path):
        print("Error: Seed file missing", file=sys.stderr)
        sys.exit(1)

    # Open seed file in read mode
    with open(seed_file_path, "r", encoding="utf-8") as file:
        sql_script = file.read()

    try:
        with psycopg.connect(get_db_url()) as conn:
            conn.execute(sql_script)
            conn.commit()
            print("Postgres database setup and seed verified using seed.sql.")

    except psycopg.Error as e:
        print(f"Database startup execution failed: {e}")

# Fetch all tasks
def get_all_tasks():
    with psycopg.connect(get_db_url(), row_factory=dict_row) as conn:
        return conn.execute(
            """
            SELECT *
            FROM tasks
            ORDER BY id ASC;
            """
        ).fetchall()

# Fetch a specific task
def get_task(task_id: int):
    with psycopg.connect(get_db_url(), row_factory=dict_row) as conn:
        return conn.execute(
            """
            SELECT *
            FROM tasks
            WHERE id = %s
            """, (task_id)
        ).fetchone

def create_task(title: str, done: bool = False):
    with psycopg.connect(get_db_url(), row_factory=dict_row) as conn:
        row = conn.execute(
            """
            INSERT INTO tasks (title, done)
            VALUES (%s, %s) 
            RETURNING id, title, done;
            """, (title, done)
        ).fetchone()
        conn.commit()
        return row

def update_task(task_id: int, title: str, done: bool):
    with psycopg.connect(get_db_url(), row_factory=dict_row) as conn:
        row = conn.execute(
            """
            UPDATE tasks
            SET title = %s, done = %s
            WHERE id = %s 
            RETURNING id, title, done
            """, (title, done, task_id)
        ).fetchone()
        conn.commit()
        return row

def delete_task(task_id: int) -> bool:
    with psycopg.connect(get_db_url()) as conn:
        result = conn.execute(
            """
            DELETE FROM tasks
            WHERE id = %s
            """, (task_id,)
        ) 
        conn.commit()
        return result.rowcount > 0
