# database/users_repository.py
from .connection import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

class UsersRepository:
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

    def get_all_users(self):
        query = "SELECT id, username, role,created_at FROM users;"
        return self._execute_query(query, fetch_all=True)

    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE id = %s;"
        return self._execute_query(query, (user_id,), fetch_one=True)

    def add_user(self, username, password, role):
        if not username or not password or not role:
            raise ValueError("Username, password, and role are required")

        password_hash = generate_password_hash(password)  # تشفير كلمة المرور
        query = """
        INSERT INTO users (username, password, role) VALUES (%s, %s, %s) RETURNING id,username,role;
        """
        return self._execute_query(query, (username, password_hash, role), fetch_one=True)

    def verify_user(self, username, password):
        query = "SELECT * FROM users WHERE username = %s;"
        user = self._execute_query(query, (username,), fetch_one=True)
        if user and check_password_hash(user['password'], password):  # التحقق من كلمة المرور
            return user
        return None

    def update_user(self, user_id, username=None, password=None, role=None):
        query = "UPDATE users SET "
        params = []
        if username:
            query += "username = %s, "
            params.append(username)
        if password:
            password_hash = generate_password_hash(password)  # تشفير كلمة المرور الجديدة
            query += "password = %s, "
            params.append(password_hash)
        if role:
            query += "role = %s, "
            params.append(role)
        query = query.rstrip(", ") + " WHERE id = %s RETURNING id,username,role;"
        params.append(user_id)
        return self._execute_query(query, params, fetch_one=True)

    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE id = %s RETURNING *;"
        return self._execute_query(query, (user_id,), fetch_one=True)

    def search_users_by_username(self, username):
        query = "SELECT id, username, role,created_at FROM users WHERE username ILIKE %s;"
        return self._execute_query(query, (f"%{username}%",), fetch_all=True)



#=============================================================
# # database/users_repository.py
# from .connection import get_db_connection
# from werkzeug.security import generate_password_hash, check_password_hash

# class UsersRepository:
#     def get_all_users(self):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT * FROM users;")
#                 return cur.fetchall()
#         finally:
#             conn.close()

#     def get_user_by_id(self, user_id):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
#                 return cur.fetchone()
#         finally:
#             conn.close()

#     def add_user(self, username, password, role):
#             conn = get_db_connection()
#             try:
#                 password_hash = generate_password_hash(password)  # تشفير كلمة المرور
#                 with conn.cursor() as cur:
#                     cur.execute(
#                         "INSERT INTO users (username, password, role) VALUES (%s, %s, %s) RETURNING *;",
#                         (username, password_hash, role)  # تخزين كلمة المرور المشفرة في العمود `password`
#                     )
#                     conn.commit()
#                     return cur.fetchone()
#             finally:
#                 conn.close()

#     def verify_user(self, username, password):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
#                 user = cur.fetchone()
#                 if user and check_password_hash(user['password'], password):  # التحقق من كلمة المرور في العمود `password`
#                     return user
#                 return None
#         finally:
#             conn.close()

#     def update_user(self, user_id, username=None, password=None, role=None):
#         conn = get_db_connection()
#         try:
#             query = "UPDATE users SET "
#             params = []
#             if username:
#                 query += "username = %s, "
#                 params.append(username)
#             if password:
#                 password_hash = generate_password_hash(password)  # تشفير كلمة المرور الجديدة
#                 query += "password = %s, "
#                 params.append(password_hash)
#             if role:
#                 query += "role = %s, "
#                 params.append(role)
#             query = query.rstrip(", ") + " WHERE id = %s RETURNING *;"
#             params.append(user_id)
#             with conn.cursor() as cur:
#                 cur.execute(query, params)
#                 conn.commit()
#                 return cur.fetchone()
#         finally:
#             conn.close()
                
#     def delete_user(self, user_id):
#         conn = get_db_connection()
#         try:
#             with conn.cursor() as cur:
#                 cur.execute("DELETE FROM users WHERE id = %s RETURNING *;", (user_id,))
#                 conn.commit()
#                 return cur.fetchone()
#         finally:
#             conn.close()

#     def search_users_by_username(self, username):
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE username ILIKE %s;", (f"%{username}%",))
                return cur.fetchall()
        finally:
            conn.close()