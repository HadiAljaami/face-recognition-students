from database.connection import get_db_connection
from psycopg.errors import UniqueViolation, ForeignKeyViolation, UndefinedTable
from typing import Dict, List, Optional

class AlertTypeRepository:
    
    def create(self, type_name: str) -> Dict:
        """Create new alert type"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO alert_types (type_name) VALUES (%s) RETURNING id, type_name",
                        (type_name,)
                    )
                    result = cursor.fetchone()
                    conn.commit()
                    return result
        except UniqueViolation:
            raise ValueError("Alert type already exists")
        except UndefinedTable:
            raise Exception("Database table does not exist")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Database error: {str(e)}")

    def get_by_id(self, type_id: int) -> Optional[Dict]:
        """Get alert type by ID"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, type_name FROM alert_types WHERE id = %s",
                        (type_id,)
                    )
                    return cursor.fetchone()
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def get_all(self) -> List[Dict]:
        """Get all alert types"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, type_name FROM alert_types ORDER BY id")
                    return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Database error: {str(e)}")

    def update(self, type_id: int, new_name: str) -> Dict:
        """Update alert type"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """UPDATE alert_types 
                        SET type_name = %s 
                        WHERE id = %s 
                        RETURNING id, type_name""",
                        (new_name, type_id)
                    )
                    result = cursor.fetchone()
                    conn.commit()
                    if not result:
                        raise ValueError("Alert type not found")
                    return result
        except UniqueViolation:
            raise ValueError("Alert type name already exists")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Database error: {str(e)}")

    def delete(self, type_id: int) -> bool:
        """Delete alert type"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM alert_types WHERE id = %s",
                        (type_id,)
                    )
                    deleted = cursor.rowcount > 0
                    conn.commit()
                    return deleted
        except ForeignKeyViolation:
            raise ValueError("Cannot delete - type is in use by alerts")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Database error: {str(e)}")