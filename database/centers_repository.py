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

# class CentersRepository:
#     def get_all_centers(self):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT * FROM exam_centers;")
#                 return cur.fetchall()
#         finally:
#             conn.close()

#     def get_center_by_id(self, center_id):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT * FROM exam_centers WHERE id = %s;", (center_id,))
#                 return cur.fetchone()
#         finally:
#             conn.close()

#     def add_center(self, center_code, center_name, status=1):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cur:
#                 cur.execute(
#                     "INSERT INTO exam_centers (center_code, center_name, status) VALUES (%s, %s, %s) RETURNING *;",
#                     (center_code, center_name, status)
#                 )
#                 conn.commit()
#                 return cur.fetchone()
#         finally:
#             conn.close()

#     def update_center(self, center_id, center_code=None, center_name=None, status=None):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cur:
#                 query = "UPDATE exam_centers SET "
#                 params = []
#                 if center_code:
#                     query += "center_code = %s, "
#                     params.append(center_code)
#                 if center_name:
#                     query += "center_name = %s, "
#                     params.append(center_name)
#                 if status is not None:
#                     query += "status = %s, "
#                     params.append(status)
#                 query = query.rstrip(", ") + " WHERE id = %s RETURNING *;"
#                 params.append(center_id)
#                 cur.execute(query, params)
#                 conn.commit()
#                 return cur.fetchone()
#         finally:
#             conn.close()

#     def delete_center(self, center_id):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cur:
#                 cur.execute("DELETE FROM exam_centers WHERE id = %s RETURNING *;", (center_id,))
#                 conn.commit()
#                 return cur.fetchone()
#         finally:
#             conn.close()

#     def search_centers_by_name(self, name):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT * FROM exam_centers WHERE center_name ILIKE %s;", (f"%{name}%",))
#                 return cur.fetchall()
#         finally:
#             conn.close()

#     def search_centers_by_code(self, code):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT * FROM exam_centers WHERE center_code ILIKE %s;", (f"%{code}%",))
#                 return cur.fetchall()
#         finally:
#             conn.close()