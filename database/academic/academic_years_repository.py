from typing import List, Dict, Optional
from database.connection import get_db_connection
from psycopg import sql, errors

class AcademicYearsRepository:
    def create_year(self, year_name: str) -> Dict:
        query = sql.SQL("""
        INSERT INTO Academic_Years (year_name)
        VALUES (%s)
        RETURNING year_id, year_name;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (year_name,))
                    result = cursor.fetchone()
                    conn.commit()
                    return result
        except errors.UniqueViolation:
            raise ValueError("Year already exists")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_all_years(self) -> List[Dict]:
        query = sql.SQL("""
        SELECT year_id, year_name 
        FROM Academic_Years;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_year_by_id(self, year_id: int) -> Optional[Dict]:
        query = sql.SQL("""
        SELECT year_id, year_name
        FROM Academic_Years 
        WHERE year_id = %s;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (year_id,))
                    return cursor.fetchone()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def update_year(self, year_id: int, year_name: str) -> Dict:
        query = sql.SQL("""
        UPDATE Academic_Years 
        SET year_name = %s
        WHERE year_id = %s
        RETURNING year_id, year_name;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (year_name, year_id))
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError("Year not found")
                    conn.commit()
                    return result
        except errors.UniqueViolation:
            raise ValueError("Year name already exists")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def delete_year(self, year_id: int) -> bool:
        query = sql.SQL("""
        DELETE FROM Academic_Years 
        WHERE year_id = %s
        RETURNING year_id;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (year_id,))
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError("Year not found")
                    conn.commit()
                    return True
        except errors.ForeignKeyViolation:
            raise ValueError("Year is referenced by other records")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")