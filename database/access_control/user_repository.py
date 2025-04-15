from werkzeug.security import generate_password_hash, check_password_hash
from database.connection import get_db_connection

def add_user_with_role(username, password, role_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # تشفير كلمة السر
                hashed_password = generate_password_hash(password)

                # إدراج المستخدم وإرجاع كافة بياناته
                cur.execute(
                    """
                    INSERT INTO users (username, password)
                    VALUES (%s, %s)
                    RETURNING id, username, is_active, created_at;
                    """,
                    (username, hashed_password)
                )
                user = cur.fetchone()

                # ربط المستخدم مع الدور
                cur.execute(
                    """
                    INSERT INTO user_roles (user_id, role_id)
                    VALUES (%s, %s)
                    RETURNING id, created_at;
                    """,
                    (user['id'], role_id)
                )
                user_role = cur.fetchone()

                # جلب بيانات الدور المربوط
                cur.execute("SELECT * FROM roles WHERE id = %s", (role_id,))
                role = cur.fetchone()

                conn.commit()
                
                # إرجاع كافة البيانات المطلوبة للعرض مباشرة
                return {
                    "status": "success",
                    "user": {
                        **user,
                        "role": role,
                        "role_assigned_at": user_role['created_at']
                    }
                }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def login_user(username, password):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT u.*, r.id as role_id, r.role_name
                    FROM users u
                    JOIN user_roles ur ON u.id = ur.user_id
                    JOIN roles r ON ur.role_id = r.id
                    WHERE u.username = %s;
                    """,
                    (username,)
                )
                user = cur.fetchone()

                if user and check_password_hash(user["password"], password):
                    return {"status": "success", "user": user}
                return {"status": "error", "message": "Invalid username or password"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_all_users():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        u.id, u.username, u.is_active, u.created_at,
                        r.id as role_id, r.role_name,
                        rp.permissions
                    FROM users u
                    JOIN user_roles ur ON u.id = ur.user_id
                    JOIN roles r ON ur.role_id = r.id
                    LEFT JOIN (
                        SELECT 
                            role_id,
                            array_agg(p.permission_name) as permissions
                        FROM role_permissions rp
                        JOIN permissions p ON rp.permission_id = p.id
                        GROUP BY role_id
                    ) rp ON r.id = rp.role_id
                    ORDER BY u.id;
                    """
                )
                return {"status": "success", "users": cur.fetchall()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def update_user(user_id, username=None, password=None, is_active=None, role_id=None):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                updates = []
                params = []
                
                if username:
                    updates.append("username = %s")
                    params.append(username)
                
                if password:
                    hashed_password = generate_password_hash(password)
                    updates.append("password = %s")
                    params.append(hashed_password)
                
                if is_active is not None:
                    updates.append("is_active = %s")
                    params.append(is_active)
                
                if updates:
                    params.append(user_id)
                    cur.execute(
                        f"UPDATE users SET {', '.join(updates)} WHERE id = %s RETURNING *",
                        params
                    )
                    user = cur.fetchone()

                if role_id:
                    cur.execute(
                        """
                        UPDATE user_roles 
                        SET role_id = %s 
                        WHERE user_id = %s
                        RETURNING *;
                        """,
                        (role_id, user_id)
                    )
                    user_role = cur.fetchone()

                    # جلب بيانات الدور الجديد
                    cur.execute("SELECT * FROM roles WHERE id = %s", (role_id,))
                    role = cur.fetchone()

                conn.commit()
                
                # إرجاع البيانات المحدثة
                result = {"status": "success"}
                if 'user' in locals():
                    result['user'] = user
                if 'role' in locals():
                    result['role'] = role
                    result['role_assigned_at'] = user_role['created_at']
                
                return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_user_by_id(user_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 
                        u.*, 
                        r.id as role_id, 
                        r.role_name,
                        array_agg(p.permission_name) as permissions
                    FROM users u
                    JOIN user_roles ur ON u.id = ur.user_id
                    JOIN roles r ON ur.role_id = r.id
                    LEFT JOIN role_permissions rp ON r.id = rp.role_id
                    LEFT JOIN permissions p ON rp.permission_id = p.id
                    WHERE u.id = %s
                    GROUP BY u.id, r.id;
                    """,
                    (user_id,)
                )
                user = cur.fetchone()
                return {
                    "status": "success" if user else "error",
                    "user": user if user else None,
                    "message": "User not found" if not user else None
                }
    except Exception as e:
        return {"status": "error", "message": str(e)}