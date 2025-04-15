# database/monitoring/alert_repository.py
from datetime import time
from database.connection import get_db_connection
from psycopg.errors import ForeignKeyViolation, UndefinedTable
from typing import Dict, List, Optional

class AlertRepository:

    def create(self, exam_id: int, student_id: int, device_id: int, 
            alert_type: int, message: str = None) -> Dict:
        """Create new alert"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO alerts 
                        (exam_id, student_id, device_id, alert_type, alert_message) 
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING alert_id, exam_id, student_id, device_id, 
                                 alert_type, alert_message, alert_timestamp, is_read""",
                        (exam_id, student_id, device_id, alert_type, message)
                    )
                    result = cursor.fetchone()
                    conn.commit()
                    return result
        except ForeignKeyViolation as e:
            conn.rollback()
            raise ValueError(f"Invalid foreign key: {str(e)}")
        except UndefinedTable:
            conn.rollback()
            raise Exception("Alerts table does not exist")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Database error: {str(e)}")

    def get_alert_devices(self, center_id=None, room_number=None, exam_date=None, start_time=None, end_time=None):
        query = """
        SELECT 
            d.id AS device_id,
            d.device_number,
            d.room_number,
            ec.center_name,
            d.status,
            COUNT(a.alert_id) AS alert_count,
            SUM(CASE WHEN a.is_read = FALSE THEN 1 ELSE 0 END) AS unread_count,
            MAX(a.alert_timestamp) AS last_alert_time,
            a.student_id, 
            e.exam_id,
            e.exam_date, 
            e.exam_start_time || ' - ' || e.exam_end_time AS exam_period
        FROM alerts a
        JOIN devices d ON a.device_id = d.id
        JOIN exams e ON a.exam_id = e.exam_id
        JOIN exam_centers ec ON d.center_id = ec.id
        WHERE 
        (%(center_id)s::INTEGER IS NULL OR ec.id = %(center_id)s::INTEGER) AND
        (%(room_number)s::TEXT IS NULL OR d.room_number = %(room_number)s::TEXT) AND
        (%(exam_date)s::DATE IS NULL OR e.exam_date = %(exam_date)s::DATE) AND
        (
            (%(start_time)s::TIME IS NULL OR %(end_time)s::TIME IS NULL)
            OR 
            (e.exam_start_time >= %(start_time)s::TIME AND e.exam_end_time <= %(end_time)s::TIME)
        )
        GROUP BY 
            d.id, d.device_number, d.room_number, ec.center_name, 
            d.status, a.student_id,  e.exam_id, e.exam_date, 
            e.exam_start_time, e.exam_end_time
        ORDER BY last_alert_time DESC;

        """
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # تحويل أنواع البيانات بشكل صريح قبل الإرسال
                    params = {
                        'center_id': center_id if center_id is not None else None,
                        'room_number': str(room_number) if room_number is not None else None,
                        'exam_date': exam_date.isoformat() if exam_date else None,
                        'start_time': start_time.isoformat() if start_time else None,
                        'end_time': end_time.isoformat() if end_time else None
                    }
                    
                    cursor.execute(query, params)
                    return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
        
    def get_alert_details(self, device_id: int, student_id: int, exam_id: int):
        """Fetch alerts for a specific device/student/exam combination."""
        query = """
        SELECT 
            at.type_name AS alert_type,
            a.alert_message,
            a.alert_timestamp,
            a.is_read
        FROM alerts a
        JOIN alert_types at ON a.alert_type = at.id
        WHERE 
            a.device_id = %(device_id)s AND
            a.student_id = %(student_id)s AND
            a.exam_id = %(exam_id)s
        ORDER BY a.alert_timestamp DESC;
        """
        params = {
            'device_id': device_id,
            'student_id': student_id,
            'exam_id': exam_id
        }

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
        return results

    def mark_alerts_as_read(self, device_id: int, student_id: int, exam_id: int):
        """Update all unread alerts to be marked as read."""
        query = """
        UPDATE alerts
        SET is_read = true
        WHERE 
            device_id = %(device_id)s AND
            student_id = %(student_id)s AND
            exam_id = %(exam_id)s AND
            is_read = false;
        """
        params = {
            'device_id': device_id,
            'student_id': student_id,
            'exam_id': exam_id
        }

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
#------------------------------------------------------
    def get_student_cheating_reports(self, student_id: int) -> List[Dict]:
            """
            Retrieve detailed cheating reports for a specific student.
            
            Args:
                student_id: The ID of the student to get reports for
                
            Returns:
                List of dictionaries containing cheating report details
                
            Raises:
                ValueError: If student_id is invalid
                Exception: For database errors
            """
            if not isinstance(student_id, int) or student_id <= 0:
                raise ValueError("Invalid student_id. It must be a positive integer.")
    
            query = """
            SELECT 
                a.student_id,
                c.name AS college_name,
                l.level_name,
                m.name AS major_name,
                y.year_name,
                s.semester_name,
                cr.name AS course_name,
                e.exam_date,
                e.exam_start_time,
                e.exam_end_time,
                ec.center_name,
                d.room_number,
                COUNT(a.alert_id) AS total_alerts,
                e.exam_id,
                    JSON_AGG(
                    JSON_BUILD_OBJECT(
                'alert_id', a.alert_id, 
                        'alert_type', at.type_name,
                        'alert_message', a.alert_message,
                        'alert_timestamp', a.alert_timestamp,
                        'is_read', a.is_read
                    )
                ) AS alerts_details
            FROM alerts a
            JOIN exams e ON a.exam_id = e.exam_id
            JOIN courses cr ON e.course_id = cr.course_id
            JOIN majors m ON e.major_id = m.major_id
            JOIN colleges c ON e.college_id = c.college_id
            JOIN levels l ON e.level_id = l.level_id
            JOIN academic_years y ON e.year_id = y.year_id
            JOIN semesters s ON e.semester_id = s.semester_id
            JOIN devices d ON a.device_id = d.id
            JOIN exam_centers ec ON d.center_id = ec.id
            JOIN alert_types at ON a.alert_type = at.id
            WHERE a.student_id =%(student_id)s 
            GROUP BY 
                a.student_id, c.name, l.level_name, m.name, y.year_name,
                s.semester_name, cr.name, e.exam_date, e.exam_start_time,
                e.exam_end_time, ec.center_name, d.room_number, e.exam_id
            ORDER BY a.student_id, e.exam_date DESC;
            """
            
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query, {'student_id': student_id})
                        #cursor.execute(query, (student_id,))
                        return cursor.fetchall()
            except Exception as e:
                raise Exception(f"Failed to get student reports: {str(e)}")

    def get_college_cheating_stats(self, year_id: Optional[int] = None) -> List[Dict]:
        """
        Retrieve cheating statistics grouped by college and academic year.
        
        Args:
            year_id: Optional academic year ID to filter by
            
        Returns:
            List of dictionaries containing college cheating statistics
            
        Raises:
            DatabaseError: If there's an error executing the query
        """
        query = """
        SELECT 
            c.name AS college_name,
            ay.year_name AS academic_year,
            COUNT(a.alert_id) AS total_cheating_cases,
            COUNT(DISTINCT a.student_id) AS cheating_students_count
        FROM alerts a
        JOIN exams e ON a.exam_id = e.exam_id
        JOIN colleges c ON e.college_id = c.college_id
        JOIN academic_years ay ON e.year_id = ay.year_id
        WHERE (%(year_id)s::INTEGER IS NULL OR e.year_id = %(year_id)s::INTEGER)
        GROUP BY c.name, ay.year_name
        ORDER BY c.name, ay.year_name, total_cheating_cases DESC;
        """
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
 
                    cursor.execute(query, {'year_id': year_id if year_id is not None else None}) 
                    return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Database error while fetching college stats: {str(e)}")
  
    def get_major_level_stats(
        self, 
        college_id: Optional[int] = None, 
        year_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get cheating statistics grouped by major, level, and academic year
        
        Args:
            college_id: Optional college ID to filter by
            year_id: Optional academic year ID to filter by
            
        Returns:
            List of dictionaries containing statistics for each major/level/year combination
            
        Raises:
            DatabaseError: If there's an error executing the query
        """
        query = """
        SELECT 
            c.name AS college_name,
            m.name AS major_name,
            l.level_name,
            ay.year_name,
            COUNT(a.alert_id) AS total_alerts,
            COUNT(DISTINCT a.student_id) AS alerted_students_count
        FROM alerts a
        JOIN exams e ON a.exam_id = e.exam_id
        JOIN majors m ON e.major_id = m.major_id
        JOIN colleges c ON e.college_id = c.college_id
        JOIN levels l ON e.level_id = l.level_id
        JOIN academic_years ay ON e.year_id = ay.year_id
        WHERE 
            (%(college_id)s::INTEGER IS NULL OR e.college_id = %(college_id)s::INTEGER)
            AND (%(year_id)s::INTEGER IS NULL OR e.year_id = %(year_id)s::INTEGER)
        GROUP BY 
            c.name,m.name, l.level_name, ay.year_name
        ORDER BY 
            COUNT(a.alert_id) DESC;
        """
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, {
                        'college_id': college_id,
                        'year_id': year_id
                    })
                    
                    return  cursor.fetchall()
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")
  
    def get_course_cheating_stats(
        self,
        college_id: int,
        major_id: Optional[int] = None,
        level_id: Optional[int] = None,
        year_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve cheating statistics by course with filters
        
        Args:
            college_id: Required college ID
            major_id: Optional major ID filter
            level_id: Optional level ID filter
            year_id: Optional academic year ID filter
            
        Returns:
            List of course cheating statistics
        """
        query = """
        SELECT 
            cr.name AS course_name,
            COUNT(*) AS total_cheating_cases,
            COUNT(DISTINCT a.student_id) AS cheating_students_count,
            e.exam_date,
            sem.semester_name,
            ay.year_name AS academic_year,
            m.name AS major_name,
            l.level_name
        FROM alerts a
        JOIN exams e ON a.exam_id = e.exam_id
        JOIN courses cr ON e.course_id = cr.course_id
        JOIN majors m ON e.major_id = m.major_id
        JOIN levels l ON e.level_id = l.level_id
        JOIN academic_years ay ON e.year_id = ay.year_id
        JOIN semesters sem ON e.semester_id = sem.semester_id
        WHERE e.college_id = %(college_id)s::INTEGER
          AND (%(major_id)s::INTEGER IS NULL OR e.major_id = %(major_id)s::INTEGER)
          AND (%(level_id)s::INTEGER IS NULL OR e.level_id = %(level_id)s::INTEGER)
          AND (%(year_id)s::INTEGER IS NULL OR e.year_id = %(year_id)s::INTEGER)
        GROUP BY 
            cr.name, e.exam_date, sem.semester_name, ay.year_name,
            m.name, l.level_name
        ORDER BY total_cheating_cases DESC;
        """
        if college_id is None:
            raise ValueError("College ID is required and cannot be empty")
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, {
                        'college_id': college_id,
                        'major_id': major_id,
                        'level_id': level_id,
                        'year_id': year_id
                    })
                    
                    return  cursor.fetchall()
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def delete(self, alert_ids: List[int]) -> int:
        """Delete multiple alerts"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                   
                    placeholders = ','.join(['%s'] * len(alert_ids))
                    cursor.execute(
                        f"DELETE FROM alerts WHERE alert_id IN ({placeholders})",
                        alert_ids
                    )
                    deleted = cursor.rowcount
                    conn.commit()
                    return deleted
        except Exception as e:
            conn.rollback()

    def delete_multiple_alerts(self, alert_keys: List[Dict]) -> int:
        """
        Delete alerts for multiple (exam_id, student_id, device_id) combinations.
        Returns number of deleted records.
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    total_deleted = 0
                    for key in alert_keys:
                        exam_id = key["exam_id"]
                        student_id = key["student_id"]
                        device_id = key["device_id"]
                        print(exam_id)
                        print(student_id)
                        print(device_id)
                        print('--------')
                        cursor.execute(
                            "DELETE FROM alerts WHERE exam_id = %s AND student_id = %s AND device_id = %s",
                            (exam_id, student_id, device_id)
                        )
                        total_deleted += cursor.rowcount

                    conn.commit()
                    return total_deleted
        except Exception as e:
            raise RuntimeError(f"Failed to delete alerts: {str(e)}")

#-----------------------------------------------------

    # def get_by_id(self, alert_id: int) -> Optional[Dict]:
    #     """Get alert details with related data"""
    #     try:
    #         with get_db_connection() as conn:
    #             with conn.cursor() as cursor:
    #                 cursor.execute(
    #                     """SELECT a.*, at.type_name, d.device_number, d.room_number
    #                     FROM alerts a
    #                     JOIN alert_types at ON a.alert_type = at.id
    #                     LEFT JOIN devices d ON a.device_id = d.id
    #                     WHERE a.alert_id = %s""",
    #                     (alert_id,)
    #                 )
    #                 return cursor.fetchone()
    #     except Exception as e:
    #         raise Exception(f"Database error: {str(e)}")

    # def get_all(self, filters: Dict = None) -> List[Dict]:
    #     """Get alerts with optional filters"""
    #     try:
    #         with get_db_connection() as conn:
    #             with conn.cursor() as cursor:
    #                 base_query = """SELECT a.*, at.type_name, d.device_number
    #                               FROM alerts a
    #                               JOIN alert_types at ON a.alert_type = at.id
    #                               LEFT JOIN devices d ON a.device_id = d.id"""
    #                 where_clauses = []
    #                 params = []
                    
    #                 if filters:
    #                     for key, value in filters.items():
    #                         where_clauses.append(f"a.{key} = %s")
    #                         params.append(value)
                        
    #                     if where_clauses:
    #                         base_query += " WHERE " + " AND ".join(where_clauses)
                    
    #                 base_query += " ORDER BY a.alert_timestamp DESC"
    #                 cursor.execute(base_query, params)
    #                 return cursor.fetchall()
    #     except Exception as e:
    #         raise Exception(f"Database error: {str(e)}")

    # def mark_as_read(self, alert_ids: List[int]) -> int:
    #     """Mark alerts as read"""
    #     try:
    #         with get_db_connection() as conn:
    #             with conn.cursor() as cursor:
    #                 placeholders = ','.join(['%s'] * len(alert_ids))
    #                 cursor.execute(
    #                     f"""UPDATE alerts 
    #                     SET is_read = TRUE 
    #                     WHERE alert_id IN ({placeholders})""",
    #                     alert_ids
    #                 )
    #                 updated = cursor.rowcount
    #                 conn.commit()
    #                 return updated
    #     except Exception as e:
    #         conn.rollback()
    #         raise Exception(f"Database error: {str(e)}")
