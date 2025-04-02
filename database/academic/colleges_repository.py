# database/academic/colleges_repository.py
from database.connection import get_db_connection

class CollegesRepository:
    
    def create_college(self, name):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Colleges (name) VALUES (%s) RETURNING *;",
                    (name,)
                )
                return cursor.fetchone()

    def get_college(self, college_id):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Colleges WHERE college_id = %s;", 
                    (college_id,)
                )
                return cursor.fetchone()

    def get_all_colleges(self):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Colleges ORDER BY name;")
                return cursor.fetchall()

    def update_college(self, college_id, name):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE Colleges SET name = %s WHERE college_id = %s RETURNING *;",
                    (name, college_id)
                )
                return cursor.fetchone()

    def delete_college(self, college_id):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM Colleges WHERE college_id = %s RETURNING college_id;",
                    (college_id,)
                )
                return cursor.fetchone()