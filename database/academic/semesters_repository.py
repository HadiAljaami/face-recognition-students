from typing import List, Dict, Optional
from database.connection import get_db_connection
from psycopg import sql, errors

class SemestersRepository:
    def create_semester(self, semester_name: str) -> Dict:
        """Create a new semester"""
        query = sql.SQL("""
        INSERT INTO Semesters (semester_name)
        VALUES (%s)
        RETURNING semester_id, semester_name;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (semester_name,))
                    result = cursor.fetchone()
                    conn.commit()
                    return result
        except errors.UniqueViolation:
            raise ValueError("Semester already exists")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_all_semesters(self) -> List[Dict]:
        """Get all semesters"""
        query = sql.SQL("""
        SELECT semester_id, semester_name 
        FROM Semesters;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_semester_by_id(self, semester_id: int) -> Optional[Dict]:
        """Get semester by ID"""
        query = sql.SQL("""
        SELECT semester_id, semester_name
        FROM Semesters 
        WHERE semester_id = %s;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (semester_id,))
                    return cursor.fetchone()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def update_semester(self, semester_id: int, semester_name: str) -> Dict:
        """Update semester"""
        query = sql.SQL("""
        UPDATE Semesters 
        SET semester_name = %s
        WHERE semester_id = %s
        RETURNING semester_id, semester_name;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (semester_name, semester_id))
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError("Semester not found")
                    conn.commit()
                    return result
        except errors.UniqueViolation:
            raise ValueError("Semester name already exists")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def delete_semester(self, semester_id: int) -> bool:
        """Delete semester"""
        query = sql.SQL("""
        DELETE FROM Semesters 
        WHERE semester_id = %s
        RETURNING semester_id;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (semester_id,))
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError("Semester not found")
                    conn.commit()
                    return True
        except errors.ForeignKeyViolation:
            raise ValueError("Semester is referenced by other records")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")