from typing import List, Dict, Optional
from database.connection import get_db_connection
from psycopg import sql, errors

class CoursesRepository:
    def create_course(self, name: str, major_id: int, level_id: int, year_id: int, semester_id: int) -> Dict:
        """Create a new course with all required relationships"""
        query = sql.SQL("""
        INSERT INTO Courses (name, major_id, level_id, year_id, semester_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING course_id, name, major_id, level_id, year_id, semester_id;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (name, major_id, level_id, year_id, semester_id))
                    result = cursor.fetchone()
                    conn.commit()
                    return result
        except errors.ForeignKeyViolation as e:
            raise ValueError(f"Invalid reference: {str(e)}")
        except errors.UniqueViolation:
            raise ValueError("Course with these attributes already exists")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_all_courses(self) -> List[Dict]:
        """Get all courses with their relationships"""
        query = sql.SQL("""
        SELECT course_id, name, major_id, level_id, year_id, semester_id
        FROM Courses;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def get_course_by_id(self, course_id: int) -> Optional[Dict]:
        """Get single course by ID"""
        query = sql.SQL("""
        SELECT course_id, name, major_id, level_id, year_id, semester_id
        FROM Courses WHERE course_id = %s;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (course_id,))
                    return cursor.fetchone()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def update_course(self, course_id: int, name: str, major_id: int, level_id: int, year_id: int, semester_id: int) -> Dict:
        """Update course details"""
        query = sql.SQL("""
        UPDATE Courses
        SET name = %s, major_id = %s, level_id = %s, 
            year_id = %s, semester_id = %s
        WHERE course_id = %s
        RETURNING course_id, name, major_id, level_id, year_id, semester_id;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (name, major_id, level_id, year_id, semester_id, course_id))
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError("Course not found")
                    conn.commit()
                    return result
        except errors.ForeignKeyViolation as e:
            raise ValueError(f"Invalid reference: {str(e)}")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def delete_course(self, course_id: int) -> bool:
        """Delete a course"""
        query = sql.SQL("""
        DELETE FROM Courses
        WHERE course_id = %s
        RETURNING course_id;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (course_id,))
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError("Course not found")
                    conn.commit()
                    return True
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")
        
        # Add these new methods to the existing CoursesRepository class
    def search_courses_by_name(self, search_term: str) -> List[Dict]:
        """Search courses by name (partial match)"""
        query = sql.SQL("""
        SELECT course_id, name, major_id, level_id, year_id, semester_id
        FROM Courses 
        WHERE name ILIKE %s
        ORDER BY name;
        """)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (f'%{search_term}%',))
                    return cursor.fetchall()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")


    def filter_courses(self, major_id: int = None, level_id: int = None, 
                    year_id: int = None, semester_id: int = None) -> List[Dict]:
        """Filter courses by one or more criteria"""
        base_query = sql.SQL("""
        SELECT course_id, name, major_id, level_id, year_id, semester_id
        FROM Courses
        """)
        
        conditions = []
        params = []
        
        if major_id:
            conditions.append(sql.SQL("major_id = %s"))
            params.append(major_id)
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
        
        base_query = sql.SQL("{0} ORDER BY name").format(base_query)
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(base_query, params)
                    return cursor.fetchall()
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")