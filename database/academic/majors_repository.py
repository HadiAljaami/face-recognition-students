from database.connection import get_db_connection

class MajorsRepository:
    
    def create_major(self, name, college_id):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO Majors (name, college_id) 
                    VALUES (%s, %s) RETURNING *;""",
                    (name, college_id)
                )
                return cursor.fetchone()

    def get_major(self, major_id):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT m.*, c.name as college_name 
                    FROM Majors m JOIN Colleges c ON m.college_id = c.college_id
                    WHERE m.major_id = %s;""", 
                    (major_id,)
                )
                return cursor.fetchone()

    def get_majors_by_college(self, college_id):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT m.*, c.name as college_name 
                    FROM Majors m JOIN Colleges c ON m.college_id = c.college_id
                    WHERE m.college_id = %s ORDER BY m.name;""",
                    (college_id,)
                )
                return cursor.fetchall()

    def update_major(self, major_id, name, college_id):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """UPDATE Majors 
                    SET name = %s, college_id = %s 
                    WHERE major_id = %s RETURNING *;""",
                    (name, college_id, major_id)
                )
                return cursor.fetchone()

    def delete_major(self, major_id):
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM Majors WHERE major_id = %s RETURNING major_id;",
                    (major_id,)
                )
                return cursor.fetchone()