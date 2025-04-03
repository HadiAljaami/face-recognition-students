from typing import List, Dict, Optional
from database.connection import get_db_connection
from psycopg import sql, errors
from datetime import date, time

class ExamsRepository:
    def create_exam(self, course_id: int, major_id: int, college_id: int, 
                   level_id: int, year_id: int, semester_id: int,
                   exam_date: date = None, exam_time: time = None) -> Dict:
        """Create a new exam"""
        query = sql.SQL("""
        INSERT INTO Exams (
            course_id, major_id, college_id, level_id, 
            year_id, semester_id, exam_date, exam_time
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING exam_id, course_id, major_id, college_id, level_id, 
                 year_id, semester_id, exam_date, exam_time, created_at;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (
                        course_id, major_id, college_id, level_id,
                        year_id, semester_id, exam_date, exam_time
                    ))
                    result = cursor.fetchone()
                    conn.commit()
                    return result
        except errors.ForeignKeyViolation as e:
            raise ValueError(f"Invalid reference: {str(e)}")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_all_exams(self) -> List[Dict]:
        """Get all exams"""
        query = sql.SQL("""
        SELECT exam_id, course_id, major_id, college_id, level_id,
               year_id, semester_id, exam_date, exam_time, created_at
        FROM Exams;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_exam_by_id(self, exam_id: int) -> Optional[Dict]:
        """Get exam by ID"""
        query = sql.SQL("""
        SELECT exam_id, course_id, major_id, college_id, level_id,
               year_id, semester_id, exam_date, exam_time, created_at
        FROM Exams WHERE exam_id = %s;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (exam_id,))
                    return cursor.fetchone()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def filter_exams(self, major_id: int = None, college_id: int = None,
                   level_id: int = None, year_id: int = None,
                   semester_id: int = None) -> List[Dict]:
        """Filter exams by multiple criteria"""
        base_query = sql.SQL("""
        SELECT exam_id, course_id, major_id, college_id, level_id,
               year_id, semester_id, exam_date, exam_time, created_at
        FROM Exams
        """)
        
        conditions = []
        params = []
        
        if major_id:
            conditions.append(sql.SQL("major_id = %s"))
            params.append(major_id)
        if college_id:
            conditions.append(sql.SQL("college_id = %s"))
            params.append(college_id)
        if level_id:
            conditions.append(sql.SQL("level_id = %s"))
            params.append(level_id)
        if year_id:
            conditions.append(sql.SQL("year_id = %s"))
            params.append(year_id)
        if semester_id:
            conditions.append(sql.SQL("semester_id = %s"))
            params.append(semester_id)
        
        if conditions:
            base_query = sql.SQL("{0} WHERE {1}").format(
                base_query,
                sql.SQL(" AND ").join(conditions)
            )
        
        base_query = sql.SQL("{0} ORDER BY exam_date DESC, exam_time").format(base_query)
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(base_query, params)
                    return cursor.fetchall()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")
        
    def delete_exams(self, exam_ids: List[int]) -> int:
        """Delete multiple exams by IDs"""
        if not exam_ids:
            return 0
            
        query = sql.SQL("""
        DELETE FROM Exams
        WHERE exam_id = ANY(%s)
        RETURNING exam_id;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (exam_ids,))
                    deleted_count = len(cursor.fetchall())
                    conn.commit()
                    return deleted_count
        except errors.ForeignKeyViolation:
            raise ValueError("Cannot delete - exams are referenced by other records")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")
        
    def update_exam(self, exam_id: int, course_id: int, major_id: int, college_id: int,
                   level_id: int, year_id: int, semester_id: int,
                   exam_date: date = None, exam_time: time = None) -> Optional[Dict]:
        """Update existing exam with robust connection handling"""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # استعلام SQL مع معاملة صريحة
            query = sql.SQL("""
            UPDATE Exams
            SET 
                course_id = %s,
                major_id = %s,
                college_id = %s,
                level_id = %s,
                year_id = %s,
                semester_id = %s,
                exam_date = %s,
                exam_time = %s
            WHERE exam_id = %s
            RETURNING exam_id, course_id, major_id, college_id, level_id,
                     year_id, semester_id, exam_date, exam_time, created_at;
            """)

            cursor.execute(query, (
                course_id, major_id, college_id, level_id,
                year_id, semester_id, exam_date, exam_time,
                exam_id
            ))

            result = cursor.fetchone()
            conn.commit()  # تأكيد المعاملة
            
            return dict(result) if result else None

        except errors.ForeignKeyViolation as e:
            if conn:
                conn.rollback()
            raise ValueError(f"Invalid reference ID: {str(e)}")
        except errors.Error as e:
            if conn:
                conn.rollback()
            raise RuntimeError(f"Database operation failed: {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()