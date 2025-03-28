# Step 3: Setup Database and Table (setup_db_vectors.py)
# Located in setup_db_vectors.py
import psycopg

# abod password
# DB_URL = "postgresql://postgres:12345678@localhost:5432/vectors_db"
# POSTGRES_URL = "postgresql://postgres:12345678@localhost:5432/postgres"

# # # hadi password
DB_URL = "postgresql://postgres:1234@localhost:5432/vectors_db"
POSTGRES_URL = "postgresql://postgres:1234@localhost:5432/postgres"

def execute_query(connection_url, query, fetch_one=False):
    try:
        with psycopg.connect(connection_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                if fetch_one:
                    return cur.fetchone()
    except Exception as e:
        print(f"Error executing query: {e}")
        raise

def create_database():
    # التحقق من وجود قاعدة البيانات وإنشاؤها إذا لم تكن موجودة
    query_check_db = "SELECT 1 FROM pg_database WHERE datname = 'vectors_db';"
    query_create_db = "CREATE DATABASE vectors_db;"
    try:
        exists = execute_query(POSTGRES_URL, query_check_db, fetch_one=True)
        if not exists:
            execute_query(POSTGRES_URL, query_create_db)
            print("Database 'vectors_db' created successfully.")
        else:
            print("Database 'vectors_db' already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")
        raise

def create_extension():
    # التحقق من وجود امتداد pgvector وإنشاؤه إذا لم يكن موجودًا
    query_create_extension = "CREATE EXTENSION IF NOT EXISTS vector;"
    try:
        execute_query(DB_URL, query_create_extension)
        print("Extension 'pgvector' created successfully in 'vectors_db'.")
    except Exception as e:
        print(f"Error creating extension: {e}")
        raise


def create_tables():
    # Create student_vectors table if not exist
    query_create_table = (
        "CREATE TABLE IF NOT EXISTS student_vectors ("
        "id SERIAL PRIMARY KEY, "
        "student_id VARCHAR(50) NOT NULL UNIQUE, "
        "college VARCHAR(100) NOT NULL, "
        "vector vector(128) NOT NULL,"
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ");"
    )

    #Create centers Table
    query_create_exam_centers = (
        "CREATE TABLE IF NOT EXISTS exam_centers ("
        "id SERIAL PRIMARY KEY, "
        "center_code VARCHAR(50) NOT NULL UNIQUE, "
        "center_name VARCHAR(100) NOT NULL UNIQUE, "
        "status INTEGER DEFAULT 1 CHECK (status IN (0, 1))"
        ");"
    )
    
    # Create Users Table
    query_create_users = (
        "CREATE TABLE IF NOT EXISTS users ("
        "id SERIAL PRIMARY KEY, "
        "username VARCHAR(50) NOT NULL UNIQUE, "
        "password VARCHAR(255) NOT NULL, "
        "role VARCHAR(10) CHECK (role IN ('Admin', 'User')) NOT NULL, "
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ");"
    )

    try:
        execute_query(DB_URL, query_create_table)
        print("Table 'student_vectors' created successfully.")

        execute_query(DB_URL, query_create_exam_centers)
        print("Table 'exam_centers' created successfully.")
        
        execute_query(DB_URL, query_create_users)
        print("Table 'users' created successfully.")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

if __name__ == "__main__":
    create_database()
    create_extension()
    create_tables()
