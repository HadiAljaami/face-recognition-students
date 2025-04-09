# database/devices_repository.py
from database.connection import get_db_connection
from typing import Optional, List, Dict

class DevicesRepository:
    
    def add_device(self, device_number: int, device_token: str, room_number: str, center_id: int) -> Dict:
        """إضافة جهاز جديد"""
        try:
            query = """
            INSERT INTO devices (device_number, device_token, room_number, center_id)
            VALUES (%s, %s, %s, %s)
            RETURNING *;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (device_number, device_token, room_number, center_id))
                    return cursor.fetchone()
        except Exception as e:
            print(f"Error adding device: {e}")
            raise

    def update_device(self, device_id: int, device_number: Optional[int] = None, 
                     device_token: Optional[str] = None, room_number: Optional[str] = None,
                     center_id: Optional[int] = None) -> bool:
        """تحديث بيانات الجهاز"""
        try:
            updates = []
            params = []
            
            if device_number is not None:
                updates.append("device_number = %s")
                params.append(device_number)
            if device_token is not None:
                updates.append("device_token = %s")
                params.append(device_token)
            if room_number is not None:
                updates.append("room_number = %s")
                params.append(room_number)
            if center_id is not None:
                updates.append("center_id = %s")
                params.append(center_id)
                
            if not updates:
                return False
                
            params.append(device_id)
            query = f"""
            UPDATE devices
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING *;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error updating device: {e}")
            raise

    def delete_device(self, device_id: int) -> bool:
        """حذف جهاز"""
        try:
            query = """
            DELETE FROM devices
            WHERE id = %s
            RETURNING id;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (device_id,))
                    return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error deleting device: {e}")
            raise

    def get_device_by_number(self, device_number: int) -> Optional[Dict]:
        """البحث عن جهاز بواسطة رقم الجهاز"""
        try:
            query = """
            SELECT * FROM devices
            WHERE device_number = %s;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (device_number,))
                    return cursor.fetchone()
        except Exception as e:
            print(f"Error getting device by number: {e}")
            raise
    def get_device_by_id(self, device_id: int) -> Optional[Dict]:
        """البحث عن جهاز بواسطة رقم الجهاز"""
        try:
            query = """
            SELECT * FROM devices
            WHERE id = %s;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (device_id,))
                    return cursor.fetchone()
        except Exception as e:
            print(f"Error getting device by number: {e}")
            raise

    def get_all_devices(self, center_id: Optional[int] = None, 
                       room_number: Optional[str] = None) -> List[Dict]:
        """جلب جميع الأجهزة مع إمكانية الفلترة حسب المركز والغرفة"""
        try:
            base_query = "SELECT * FROM devices"
            conditions = []
            params = []
            
            if center_id is not None:
                conditions.append("center_id = %s")
                params.append(center_id)
            if room_number is not None:
                conditions.append("room_number = %s")
                params.append(room_number)
                
            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
                
            base_query += " ORDER BY device_number;"
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(base_query, params)
                    return cursor.fetchall()
        except Exception as e:
            print(f"Error getting all devices: {e}")
            raise

    def toggle_device_status(self, device_id: int) -> Optional[Dict]:
        """تبديل حالة الجهاز (تشغيل/إيقاف)"""
        try:
            query = """
            UPDATE devices
            SET status = 1 - status
            WHERE id = %s
            RETURNING *;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (device_id,))
                    return cursor.fetchone()
        except Exception as e:
            print(f"Error toggling device status: {e}")
            raise

    def get_device_by_token(self, device_token: str) -> Optional[Dict]:
        """البحث عن جهاز بواسطة التوكن"""
        try:
            query = """
            SELECT * FROM devices
            WHERE device_token = %s;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (device_token,))
                    return cursor.fetchone()
        except Exception as e:
            print(f"Error getting device by token: {e}")
            raise