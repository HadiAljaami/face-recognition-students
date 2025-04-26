# database/centers_repository.py
from .connection import get_db_connection

class CentersRepository:
    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """
        دالة مساعدة لتنفيذ الاستعلامات
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    if fetch_one:
                        return cur.fetchone()
                    if fetch_all:
                        return cur.fetchall()
                    return cur.rowcount
        except Exception as e:
            # رفع الاستثناء للطبقة الأعلى
            raise Exception(f"Database error: {str(e)}")

    def get_all_centers(self):
        query = "SELECT * FROM exam_centers;"
        return self._execute_query(query, fetch_all=True)

    def get_center_by_id(self, center_id):
        query = "SELECT * FROM exam_centers WHERE id = %s;"
        return self._execute_query(query, (center_id,), fetch_one=True)

    def add_center(self, center_name, status=1):
        query = """
        INSERT INTO exam_centers (center_name, status) VALUES (%s, %s) RETURNING *;
        """
        return self._execute_query(query, (center_name, status), fetch_one=True)

    def update_center(self, center_id, center_name=None, status=None):
        query = "UPDATE exam_centers SET "
        params = []
        if center_name:
            query += "center_name = %s, "
            params.append(center_name)
        if status is not None:
            query += "status = %s, "
            params.append(status)
        query = query.rstrip(", ") + " WHERE id = %s RETURNING *;"
        params.append(center_id)
        return self._execute_query(query, params, fetch_one=True)

    def delete_center(self, center_id):
        query = "DELETE FROM exam_centers WHERE id = %s RETURNING *;"
        return self._execute_query(query, (center_id,), fetch_one=True)

    def search_centers_by_name(self, name):
        query = "SELECT * FROM exam_centers WHERE center_name ILIKE %s;"
        return self._execute_query(query, (f"%{name}%",), fetch_all=True)

