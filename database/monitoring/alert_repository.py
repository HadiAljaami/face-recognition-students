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
            d.status, a.student_id, e.exam_id, e.exam_date, 
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

    # def delete(self, alert_ids: List[int]) -> int:
        # """Delete multiple alerts"""
        # try:
        #     with get_db_connection() as conn:
        #         with conn.cursor() as cursor:
        #             placeholders = ','.join(['%s'] * len(alert_ids))
        #             cursor.execute(
        #                 f"DELETE FROM alerts WHERE alert_id IN ({placeholders})",
        #                 alert_ids
        #             )
        #             deleted = cursor.rowcount
        #             conn.commit()
        #             return deleted
        # except Exception as e:
        #     conn.rollback()
        #     raise Exception(f"Database error: {str(e)}")