from typing import List, Dict, Optional, Tuple, Union
from database.connection import get_db_connection
from psycopg import sql, errors
from datetime import datetime, date, time

class ExamsRepository:
    # def create_exam(self, course_id: int, major_id: int, college_id: int, 
    #                level_id: int, year_id: int, semester_id: int,
    #                exam_date: date = None,
    #                exam_start_time: time = None, 
    #                exam_end_time: time = None) -> Dict:
    #     """Create a new exam with all time fields"""
    #     query = sql.SQL("""
    #     INSERT INTO Exams (
    #         course_id, major_id, college_id, level_id, 
    #         year_id, semester_id, exam_date, exam_start_time, exam_end_time
    #     )
    #     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    #     RETURNING exam_id, course_id, major_id, college_id, level_id, 
    #              year_id, semester_id, exam_date, exam_start_time, 
    #              exam_end_time, created_at;
    #     """)
    #     try:
    #         with get_db_connection() as conn:
    #             with conn.cursor() as cursor:
    #                 cursor.execute(query, (
    #                     course_id, major_id, college_id, level_id,
    #                     year_id, semester_id, exam_date, 
    #                     exam_start_time, exam_end_time
    #                 ))
    #                 result = cursor.fetchone()
    #                 conn.commit()
    #                 return result
    #     except errors.ForeignKeyViolation as e:
    #         raise ValueError(f"Invalid reference: {str(e)}")
    #     except errors.Error as e:
    #         raise RuntimeError(f"Database error: {str(e)}")

    def create_exam(self, course_id: int, major_id: int, college_id: int, 
                level_id: int, year_id: int, semester_id: int,
                exam_date: date = None,
                exam_start_time: time = None, 
                exam_end_time: time = None) -> Dict:
        """Create a new exam with all time fields and return full details with names"""
        query = sql.SQL("""
        WITH inserted_exam AS (
            INSERT INTO Exams (
                course_id, major_id, college_id, level_id, 
                year_id, semester_id, exam_date, exam_start_time, exam_end_time
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING exam_id, course_id, major_id, college_id, level_id, 
                    year_id, semester_id, exam_date, exam_start_time, 
                    exam_end_time, created_at
        )
               SELECT 
            e.exam_id,
            e.course_id,
            c.name AS course_name,
            e.major_id,
            m.name AS major_name,
            e.college_id,
            col.name AS college_name,
            e.level_id,
            l.level_name,
            e.year_id,
            ay.year_name,
            e.semester_id,
            s.semester_name,
            e.exam_date,
            e.exam_start_time,
            e.exam_end_time,
            e.created_at
        FROM Exams e
        JOIN Courses c ON e.course_id = c.course_id
        JOIN Majors m ON e.major_id = m.major_id
        JOIN Colleges col ON e.college_id = col.college_id
        JOIN Levels l ON e.level_id = l.level_id
        JOIN Academic_Years ay ON e.year_id = ay.year_id
        JOIN Semesters s ON e.semester_id = s.semester_id
        """)
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (
                        course_id, major_id, college_id, level_id,
                        year_id, semester_id, exam_date, 
                        exam_start_time, exam_end_time
                    ))
                    result = cursor.fetchone()
                    conn.commit()
                    return result
                    
        except errors.ForeignKeyViolation as e:
            raise ValueError(f"Invalid reference: {str(e)}")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_exam_by_id(self, exam_id: int) -> Optional[Dict]:
        """Get exam by ID with all time fields"""
        query = sql.SQL("""
        SELECT exam_id, course_id, major_id, college_id, level_id,
               year_id, semester_id, exam_date, exam_start_time, 
               exam_end_time, created_at
        FROM Exams WHERE exam_id = %s;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (exam_id,))
                    return cursor.fetchone()
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

    def update_exam(self, exam_id: int, 
                    course_id: int = None, 
                    major_id: int = None, 
                    college_id: int = None,
                    level_id: int = None, 
                    year_id: int = None, 
                    semester_id: int = None,
                    exam_date: date = None,
                    exam_start_time: time = None, 
                    exam_end_time: time = None) -> Optional[Dict]:
        """
        Update existing exam with partial updates for all fields
        Then return full exam data joined with related tables
        """
        # Build dynamic update query
        updates = []
        params = []

        if course_id is not None:
            updates.append(sql.SQL("course_id = %s"))
            params.append(course_id)
        if major_id is not None:
            updates.append(sql.SQL("major_id = %s"))
            params.append(major_id)
        if college_id is not None:
            updates.append(sql.SQL("college_id = %s"))
            params.append(college_id)
        if level_id is not None:
            updates.append(sql.SQL("level_id = %s"))
            params.append(level_id)
        if year_id is not None:
            updates.append(sql.SQL("year_id = %s"))
            params.append(year_id)
        if semester_id is not None:
            updates.append(sql.SQL("semester_id = %s"))
            params.append(semester_id)
        if exam_date is not None:
            updates.append(sql.SQL("exam_date = %s"))
            params.append(exam_date)
        if exam_start_time is not None:
            updates.append(sql.SQL("exam_start_time = %s"))
            params.append(exam_start_time)
        if exam_end_time is not None:
            updates.append(sql.SQL("exam_end_time = %s"))
            params.append(exam_end_time)

        if not updates:
            raise ValueError("No fields provided for update")

        params.append(exam_id)

        update_query = sql.SQL("""
            UPDATE Exams
            SET {updates}
            WHERE exam_id = %s
            RETURNING exam_id;
        """).format(updates=sql.SQL(", ").join(updates))

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Execute the update
                    cursor.execute(update_query, params)
                    updated = cursor.fetchone()
                    conn.commit()

                    if not updated:
                        return None  # Exam not found

                    # Fetch detailed info after update
                    cursor.execute("""
                        SELECT 
                                    e.exam_id,
                                    e.course_id,
                                    c.name AS course_name,
                                    e.major_id,
                                    m.name AS major_name,
                                    e.college_id,
                                    col.name AS college_name,
                                    e.level_id,
                                    l.level_name,
                                    e.year_id,
                                    ay.year_name,
                                    e.semester_id,
                                    s.semester_name,
                                    e.exam_date,
                                    e.exam_start_time,
                                    e.exam_end_time,
                                    e.created_at
                                FROM Exams e
                                JOIN Courses c ON e.course_id = c.course_id
                                JOIN Majors m ON e.major_id = m.major_id
                                JOIN Colleges col ON e.college_id = col.college_id
                                JOIN Levels l ON e.level_id = l.level_id
                                JOIN Academic_Years ay ON e.year_id = ay.year_id
                                JOIN Semesters s ON e.semester_id = s.semester_id
                        WHERE e.exam_id = %s;
                    """, [exam_id])

                    result = cursor.fetchone()
                    return result if result else None 


        except errors.ForeignKeyViolation as e:
            raise ValueError(f"Invalid reference ID: {str(e)}")
        except errors.Error as e:
            raise RuntimeError(f"Database operation failed: {str(e)}")

    def filter_exams(self, 
                    major_id: int = None, 
                    college_id: int = None,
                    level_id: int = None, 
                    year_id: int = None,
                    semester_id: int = None,
                    exam_date: date = None,
                    start_time: time = None,
                    end_time: time = None) -> List[Dict]:
        """
        Filter exams with names and IDs from related tables and time range filtering
        
        Args:
            major_id: Filter by major ID
            college_id: Filter by college ID
            level_id: Filter by level ID
            year_id: Filter by academic year ID
            semester_id: Filter by semester ID
            exam_date: Filter by specific date
            start_time: Filter exams starting after this time
            end_time: Filter exams ending before this time
        
        Returns:
            List of exam dictionaries with both IDs and related names
        """
        base_query = sql.SQL("""
        SELECT 
            e.exam_id,
            e.course_id,
            c.name AS course_name,
            e.major_id,
            m.name AS major_name,
            e.college_id,
            col.name AS college_name,
            e.level_id,
            l.level_name,
            e.year_id,
            ay.year_name,
            e.semester_id,
            s.semester_name,
            e.exam_date,
            e.exam_start_time,
            e.exam_end_time,
            e.created_at
        FROM Exams e
        JOIN Courses c ON e.course_id = c.course_id
        JOIN Majors m ON e.major_id = m.major_id
        JOIN Colleges col ON e.college_id = col.college_id
        JOIN Levels l ON e.level_id = l.level_id
        JOIN Academic_Years ay ON e.year_id = ay.year_id
        JOIN Semesters s ON e.semester_id = s.semester_id
        """)
        
        conditions = []
        params = []
        
        # ID filters
        if major_id:
            conditions.append(sql.SQL("e.major_id = %s"))
            params.append(major_id)
        if college_id:
            conditions.append(sql.SQL("e.college_id = %s"))
            params.append(college_id)
        if level_id:
            conditions.append(sql.SQL("e.level_id = %s"))
            params.append(level_id)
        if year_id:
            conditions.append(sql.SQL("e.year_id = %s"))
            params.append(year_id)
        if semester_id:
            conditions.append(sql.SQL("e.semester_id = %s"))
            params.append(semester_id)
        
        # Date filter
        if exam_date:
            conditions.append(sql.SQL("e.exam_date = %s"))
            params.append(exam_date)
        
        # Time range filters
        if start_time and end_time:
            conditions.append(sql.SQL("""
                (e.exam_start_time >= %s AND e.exam_end_time <= %s)
            """))
            params.extend([start_time, end_time])
        elif start_time:
            conditions.append(sql.SQL("e.exam_start_time >= %s"))
            params.append(start_time)
        elif end_time:
            conditions.append(sql.SQL("e.exam_end_time <= %s"))
            params.append(end_time)
        
        # Build final query
        if conditions:
            base_query = sql.SQL("{0} WHERE {1}").format(
                base_query,
                sql.SQL(" AND ").join(conditions)
            )
        
        base_query = sql.SQL("""
        {0} ORDER BY e.exam_date DESC, e.exam_start_time
        """).format(base_query)
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(base_query, params)
                    return cursor.fetchall()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_exam_dates(self) -> List[date]:
        """Retrieve all distinct exam dates from database""" 
        query = sql.SQL("""
        SELECT DISTINCT exam_date
        FROM Exams
        WHERE exam_date IS NOT NULL
        ORDER BY exam_date DESC;
        """)
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    return results 
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}") from e
        
    def get_exam_time_slots(self, target_date: date = None) -> List[Dict[str, time]]:
        date_to_use = target_date if target_date else date.today()
        
        query = """
        SELECT DISTINCT
            exam_start_time as start_time,
            exam_end_time as end_time
        FROM Exams
        WHERE exam_date = %s
        ORDER BY exam_start_time
        """
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (date_to_use,))
                    return cursor.fetchall() 
        except errors.Error as e:
            raise RuntimeError(f"Database operation failed: {str(e)}")