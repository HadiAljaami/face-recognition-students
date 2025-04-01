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

def create_tables2():
    # جدول الكليات
    query_create_colleges = """
    CREATE TABLE IF NOT EXISTS Colleges (
        college_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE
    );
    """

    # جدول التخصصات
    query_create_majors = """
    CREATE TABLE IF NOT EXISTS Majors (
        major_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        college_id INT REFERENCES Colleges(college_id) ON DELETE RESTRICT
    );
    """

    # جدول المستويات الدراسية
    query_create_levels = """
    CREATE TABLE IF NOT EXISTS Levels (
        level_id SERIAL PRIMARY KEY,
        level_name VARCHAR(50) NOT NULL UNIQUE
    );
    """

    # جدول السنوات الدراسية
    query_create_academic_years = """
    CREATE TABLE IF NOT EXISTS Academic_Years (
        year_id SERIAL PRIMARY KEY,
        year_name VARCHAR(50) NOT NULL UNIQUE
    );
    """

    # جدول الفصول الدراسية
    query_create_semesters = """
    CREATE TABLE IF NOT EXISTS Semesters (
        semester_id SERIAL PRIMARY KEY,
        semester_name VARCHAR(50) NOT NULL UNIQUE
    );
    """

    # جدول المواد الدراسية
    query_create_courses = """
    CREATE TABLE IF NOT EXISTS Courses (
        course_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        major_id INT REFERENCES Majors(major_id) ON DELETE RESTRICT,
        level_id INT REFERENCES Levels(level_id) ON DELETE RESTRICT,
        year_id INT REFERENCES Academic_Years(year_id) ON DELETE RESTRICT,
        semester_id INT REFERENCES Semesters(semester_id) ON DELETE RESTRICT
    );
    """

    # جدول الاختبارات
    query_create_exams = """
    CREATE TABLE IF NOT EXISTS Exams (
        exam_id SERIAL PRIMARY KEY,
        course_id INT REFERENCES Courses(course_id) ON DELETE RESTRICT,
        major_id INT REFERENCES Majors(major_id) ON DELETE RESTRICT,
        college_id INT REFERENCES Colleges(college_id) ON DELETE RESTRICT,
        level_id INT REFERENCES Levels(level_id) ON DELETE RESTRICT,
        year_id INT REFERENCES Academic_Years(year_id) ON DELETE RESTRICT,
        semester_id INT REFERENCES Semesters(semester_id) ON DELETE RESTRICT,
        exam_date DATE  NULL,
        exam_time TIME  NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        execute_query(DB_URL, query_create_colleges)
        print("Table 'Colleges' created successfully.")

        execute_query(DB_URL, query_create_majors)
        print("Table 'Majors' created successfully.")

        execute_query(DB_URL, query_create_levels)
        print("Table 'Levels' created successfully.")

        execute_query(DB_URL, query_create_academic_years)
        print("Table 'Academic_Years' created successfully.")

        execute_query(DB_URL, query_create_semesters)
        print("Table 'Semesters' created successfully.")

        execute_query(DB_URL, query_create_courses)
        print("Table 'Courses' created successfully.")

        execute_query(DB_URL, query_create_exams)
        print("Table 'Exams' created successfully.")

    except Exception as e:
        print(f"Error creating tables: {e}")
        raise


def create_tables3():
    # Create Devices Table
    query_create_devices = (
        "CREATE TABLE IF NOT EXISTS devices ("
        "id SERIAL PRIMARY KEY, "
        "device_number INTEGER UNIQUE NOT NULL,"
        "device_token TEXT UNIQUE NOT NULL, "
        "status INTEGER DEFAULT 1 CHECK (status IN (0, 1)), "
        "room_number VARCHAR(50)  NOT NULL, "
        "center_id INTEGER REFERENCES exam_centers(id) ON DELETE RESTRICT, "
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ");"
    )
    
    # Create Alert Types Table
    query_create_alert_types = (
        "CREATE TABLE IF NOT EXISTS alert_types ("
        "id SERIAL PRIMARY KEY, "
        "type_name TEXT NOT NULL"
        ");"
    )
    
    # Create Alerts Table
    query_create_alerts = (
        "CREATE TABLE IF NOT EXISTS alerts ("
        "alert_id SERIAL PRIMARY KEY, "
        "exam_id INTEGER NOT NULL REFERENCES Exams(exam_id) ON DELETE RESTRICT, "  
        "student_id INTEGER NOT NULL, "
        "device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE SET NULL, "
        "alert_type INTEGER NOT NULL REFERENCES alert_types(id) ON DELETE RESTRICT, "
        "alert_message TEXT, "
        "alert_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ");"
    )
    
    try:
        execute_query(DB_URL, query_create_devices)
        print("Table 'devices' created successfully.")

        execute_query(DB_URL, query_create_alert_types)
        print("Table 'alert_types' created successfully.")

        execute_query(DB_URL, query_create_alerts)
        print("Table 'alerts' created successfully.")
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise


if __name__ == "__main__":
    #create_database()
    #create_extension()
    create_tables()
    create_tables2()
    create_tables3()
