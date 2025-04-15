# repository.py
import psycopg
from psycopg import sql, errors
from datetime import date, time
from typing import List, Tuple
from database.connection import get_db_connection

class ExamsExcelRepository:

    def validate_exams_data(self, exams_data: List[Tuple]) -> List[Tuple[int, str]]:
        invalid_records = []
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Create temporary table matching exams structure
                    cursor.execute("""
                        CREATE TEMP TABLE IF NOT EXISTS temp_exams_validation (
                            course_id INTEGER,
                            major_id INTEGER,
                            college_id INTEGER,
                            level_id INTEGER,
                            year_id INTEGER,
                            semester_id INTEGER,
                            exam_date DATE,
                            exam_start_time TIME,
                            exam_end_time TIME
                        ) ON COMMIT DROP
                    """)
                    
                    for idx, record in enumerate(exams_data):
                        try:
                            cursor.execute(
                                """
                                INSERT INTO temp_exams_validation 
                                (course_id, major_id, college_id, level_id,
                                year_id, semester_id, exam_date, exam_start_time, exam_end_time)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                                record
                            )
                        except errors.Error as e:
                            invalid_records.append((idx, str(e)))
                    
                    conn.rollback()
                    
        except errors.Error as e:
            raise RuntimeError(f"Validation failed: {str(e)}")
        
        return invalid_records    

    def bulk_create_exams(self, exams_data: List[Tuple]) -> None:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if exams_data:
                        print("First record for insertion:", exams_data[0])
                        print("Data types:", [type(x) for x in exams_data[0]])
                    
                    query = """
                        INSERT INTO exams (
                            course_id, major_id, college_id, level_id,
                            year_id, semester_id, exam_date, exam_start_time, exam_end_time
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    print("SQL query:", query)
                    
                    cursor.executemany(query, exams_data)
                    conn.commit()
                    
        except errors.Error as e:
            conn.rollback()
            print("Database error details:", str(e))
            raise RuntimeError(f"Bulk insert failed: {str(e)}")