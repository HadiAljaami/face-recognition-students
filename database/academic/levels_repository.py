from database.connection import get_db_connection
from psycopg import errors as pg_errors

class LevelsRepository:
    
    def create_level(self, level_name):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO Levels (level_name) VALUES (%s) RETURNING *;",
                        (level_name,)
                    )
                    result = cursor.fetchone()
                    if not result:
                        raise RuntimeError("Create operation failed")
                    return result
        except pg_errors.UniqueViolation:
            raise ValueError("Level name already exists")
        except pg_errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_level(self, level_id):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT * FROM Levels WHERE level_id = %s;",
                        (level_id,)
                    )
                    return cursor.fetchone()
        except pg_errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_all_levels(self):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM Levels ORDER BY level_name;")
                    return cursor.fetchall()
        except pg_errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def update_level(self, level_id, new_name):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE Levels SET level_name = %s WHERE level_id = %s RETURNING *;",
                        (new_name, level_id)
                    )
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError("Level not found")
                    return result
        except pg_errors.UniqueViolation:
            raise ValueError("Level name already exists")
        except pg_errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def delete_level(self, level_id):
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM Levels WHERE level_id = %s RETURNING level_id;",
                        (level_id,)
                    )
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError("Level not found")
                    return result['level_id']
        except pg_errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")