# Step 3: Setup Database and Table (setup_db_vectors.py)
# Located in setup_db_vectors.py
import psycopg
from psycopg import errors

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
        exam_start_time TIME  NULL, 
        exam_end_time TIME  NULL,   
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
        "is_read BOOLEAN DEFAULT FALSE"
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

def create_exam_distribution_table():
    query_create_exam_distribution = (
        """
        CREATE TABLE IF NOT EXISTS exam_distribution (
            id SERIAL PRIMARY KEY,
            student_id VARCHAR(50) NOT NULL,
            student_name VARCHAR(100) NOT NULL,
            exam_id INTEGER REFERENCES Exams(exam_id) ON DELETE SET NULL,
            device_id INTEGER REFERENCES devices(id) ON DELETE SET NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (student_id, exam_id)
        );
        """
    )

    try:
        execute_query(DB_URL, query_create_exam_distribution)
        print("Table 'exam_distribution' created successfully.")
    except Exception as e:
        print(f"Error creating 'exam_distribution' table: {e}")



def modify_exams_table():
    print("Starting exams table modification...")
    
    # Check if table exists
    if not execute_query(DB_URL, 
        "SELECT 1 FROM information_schema.tables WHERE table_name = 'exams'",
        fetch_one=True):
        print("Error: 'exams' table doesn't exist!")
        return False

    # Check if old column exists
    old_column_exists = execute_query(DB_URL,
        "SELECT 1 FROM information_schema.columns WHERE table_name='exams' AND column_name='exam_time'",
        fetch_one=True)

    if not old_column_exists:
        print("Old column 'exam_time' doesn't exist - no modification needed")
        return True

    # Add new columns if they don't exist
    new_columns = [
        ('exam_start_time', 'TIME NULL'),
        ('exam_end_time', 'TIME NULL')
    ]

    for column_name, column_type in new_columns:
        if not execute_query(DB_URL,
            f"SELECT 1 FROM information_schema.columns WHERE table_name='exams' AND column_name='{column_name}'",
            fetch_one=True):
            
            execute_query(DB_URL, f"ALTER TABLE exams ADD COLUMN {column_name} {column_type}")
            print(f"Successfully added new column '{column_name}'")

    # Migrate data from old column to new columns
    # Assuming exam_time was the start time and exams last 2 hours by default
    execute_query(DB_URL, """
        UPDATE exams 
        SET 
            exam_start_time = exam_time,
            exam_end_time = (exam_time + INTERVAL '2 hours')::TIME
        WHERE exam_time IS NOT NULL
    """)
    print("Successfully migrated data from old to new columns")

    # Add validation constraints
    execute_query(DB_URL, """
        ALTER TABLE exams 
        ADD CONSTRAINT chk_exam_times 
        CHECK (exam_start_time < exam_end_time)
    """)
    print("Added time validation constraints")

    # Remove old column (comment this out if you want to wait)
    execute_query(DB_URL, "ALTER TABLE exams DROP COLUMN exam_time")
    print("Successfully dropped old 'exam_time' column")


    print("All modifications completed successfully!")
    return True


def modify_alerts_table():
    print("Starting alerts table modification...")
    
    # Check if table exists
    if not execute_query(DB_URL, 
        "SELECT 1 FROM information_schema.tables WHERE table_name = 'alerts'",
        fetch_one=True):
        print("Error: 'alerts' table doesn't exist!")
        return False

    # Check if column already exists
    column_exists = execute_query(DB_URL,
        "SELECT 1 FROM information_schema.columns WHERE table_name='alerts' AND column_name='is_read'",
        fetch_one=True)

    if column_exists:
        print("Column 'is_read' already exists - no modification needed")
        return True

    # Add new column with default value
    try:
        execute_query(DB_URL, """
            ALTER TABLE alerts 
            ADD COLUMN is_read BOOLEAN NOT NULL DEFAULT FALSE
        """)
        print("Successfully added new column 'is_read'")
        
        # Add index for better performance on read status queries
        execute_query(DB_URL, """
            CREATE INDEX idx_alerts_read_status 
            ON alerts(is_read)
        """)
        print("Added index for read status column")
        
        # Optional: Add comment to column
        execute_query(DB_URL, """
            COMMENT ON COLUMN alerts.is_read 
            IS 'Indicates whether alert has been reviewed by supervisor'
        """)
        print("Added column comment")
        
        print("All modifications completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error modifying alerts table: {str(e)}")
        return False


def modify_exam_centers_table():
    print("Starting exam_centers table modification...")
    
    # Check if table exists
    if not execute_query(DB_URL, 
        "SELECT 1 FROM information_schema.tables WHERE table_name = 'exam_centers'",
        fetch_one=True):
        print("Error: 'exam_centers' table doesn't exist!")
        return False

    # Check if column exists
    column_exists = execute_query(DB_URL,
        "SELECT 1 FROM information_schema.columns WHERE table_name='exam_centers' AND column_name='center_code'",
        fetch_one=True)

    if not column_exists:
        print("Column 'center_code' doesn't exist - no modification needed")
        return True

    # Remove the column
    try:
        execute_query(DB_URL, """
            ALTER TABLE exam_centers 
            DROP COLUMN center_code
        """)
        print("Successfully removed column 'center_code'")
        
        print("All modifications completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error modifying exam_centers table: {str(e)}")
        return False


def add_required_constraints():
    """Adds all necessary UNIQUE constraints to enable ON CONFLICT functionality"""
    constraints = [
        {
            'name': 'unique_major_name_per_college',
            'table': 'Majors',
            'columns': ['name', 'college_id'],
            'message': "No duplicate major names per college"
        },
        {
            'name': 'unique_course_details',
            'table': 'Courses',
            'columns': ['name', 'major_id', 'level_id', 'year_id', 'semester_id'],
            'message': "No duplicate courses with same details"
        }
    ]

    print("⏳ Adding required UNIQUE constraints...")
    
    for constraint in constraints:
        columns = ", ".join(constraint['columns'])
        query = f"""
            ALTER TABLE {constraint['table']} 
            ADD CONSTRAINT {constraint['name']} 
            UNIQUE ({columns});
        """
        try:
            execute_query(DB_URL, query)
            print(f"✓ Added constraint '{constraint['name']}': {constraint['message']}")
        except errors.DuplicateObject:
            print(f"⚠ Constraint '{constraint['name']}' already exists")
        except Exception as e:
            print(f"❌ Failed to add constraint '{constraint['name']}': {e}")
            raise

    print("✅ Constraints setup completed")




if __name__ == "__main__":
    #create_database()
    #create_extension()
    #create_tables()
    #create_tables2()
    #create_tables3()
    #modify_exams_table()
    #modify_alerts_table()
    #modify_exam_centers_table()

    #==========================
    # print("\n" + "="*50)
    # print("Database UNIQUE Constraints Setup")
    # print("="*50 + "\n")
    # add_required_constraints()
    create_exam_distribution_table()
