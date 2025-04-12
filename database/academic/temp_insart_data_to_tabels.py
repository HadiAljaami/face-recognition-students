import psycopg
from psycopg import errors

# abod password
DB_URL = "postgresql://postgres:12345678@localhost:5432/vectors_db"
POSTGRES_URL = "postgresql://postgres:12345678@localhost:5432/postgres"

# # hadi password
# DB_URL = "postgresql://postgres:1234@localhost:5432/vectors_db"
# POSTGRES_URL = "postgresql://postgres:1234@localhost:5432/postgres"



def populate_table(table_name, data, columns):
    """Generic function to populate a table with data"""
    print(f"\n⏳ Populating {table_name} table...")
    placeholders = ", ".join(["%s"] * len(columns))
    cols = ", ".join(columns)
    
    query = f"""
        INSERT INTO {table_name} ({cols})
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING;
    """
    
    success_count = 0
    for item in data:
        try:
            with psycopg.connect(DB_URL, autocommit=True) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, item)
                    success_count += 1
        except Exception as e:
            print(f"⚠ Error inserting {item}: {e}")
    
    print(f"✓ Inserted {success_count}/{len(data)} records into {table_name}")

def populate_database():
    """Main function to populate all tables"""
    try:
        # 1. First add required constraints
        
        # 2. Populate tables
        colleges = [
            ('College of Engineering',),
            ('College of Medicine',),
            ('College of Science',),
            ('College of Arts',),
            ('College of Business Administration',)
        ]
        populate_table("Colleges", colleges, ["name"])
        
        majors = [
            ('Computer Engineering', 1),
            ('Electrical Engineering', 1),
            ('Mechanical Engineering', 1),
            ('Medicine', 2),
            ('Dental Surgery', 2),
            ('Computer Science', 3),
            ('Physics', 3),
            ('Chemistry', 3),
            ('Arabic Language', 4),
            ('History', 4),
            ('Business Administration', 5),
            ('Accounting', 5)
        ]
        populate_table("Majors", majors, ["name", "college_id"])
        
        levels = [
            ('Level 1',),
            ('Level 2',),
            ('Level 3',),
            ('Level 4',),
            ('Level 5',),
            ('Level 6',),
            ('Level 7',)
        ]
        populate_table("Levels", levels, ["level_name"])
        
        academic_years = [
            ('2023-2024',),
            ('2024-2025',),
            ('2025-2026',)
        ]
        populate_table("Academic_Years", academic_years, ["year_name"])
        
        semesters = [
            ('First Semester',),
            ('Second Semester',)
        ]
        populate_table("Semesters", semesters, ["semester_name"])
        
        courses = [
            ('Computer Programming 1', 1, 1, 1, 1),
            ('Engineering Mathematics', 1, 1, 1, 1),
            ('Electrical Circuits', 1, 1, 1, 2),
            ('Data Structures', 1, 2, 1, 1),
            ('Database Systems', 1, 2, 1, 2),
            ('Operating Systems', 1, 3, 2, 1),
            ('Computer Networks', 1, 3, 2, 2),
            ('Artificial Intelligence', 1, 4, 2, 1),
            ('Information Security', 1, 4, 2, 2),
            ('Electrical Circuits 1', 2, 1, 1, 1),
            ('Digital Electronics', 2, 1, 1, 2),
            ('General Anatomy', 4, 1, 1, 1),
            ('Physiology', 4, 1, 1, 2),
            ('Principles of Management', 11, 1, 1, 1),
            ('Financial Accounting', 11, 1, 1, 2)
        ]
        populate_table("Courses", courses, ["name", "major_id", "level_id", "year_id", "semester_id"])
        
        print("\n✅ Database population completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Database population failed: {e}")
        raise


def execute_query(connection_url, query, params=None, fetch_one=False):
    """Generic query execution function"""
    try:
        with psycopg.connect(connection_url, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                if fetch_one:
                    return cur.fetchone()
                return True
    except Exception as e:
        print(f"Error executing query: {e}")
        raise

def add_courses():
    """Adds the specified courses to the database"""
    courses = [
        {"name": "Computer Programming 1", "major": "Computer Engineering", "level": "Level 1", "year": "2023-2024", "semester": "First Semester"},
        {"name": "Engineering Mathematics", "major": "Computer Engineering", "level": "Level 1", "year": "2023-2024", "semester": "First Semester"},
        {"name": "Electrical Circuits", "major": "Computer Engineering", "level": "Level 1", "year": "2023-2024", "semester": "Second Semester"},
        {"name": "Data Structures", "major": "Computer Engineering", "level": "Level 2", "year": "2023-2024", "semester": "First Semester"},
        {"name": "Database Systems", "major": "Computer Engineering", "level": "Level 2", "year": "2023-2024", "semester": "Second Semester"},
        {"name": "Operating Systems", "major": "Computer Engineering", "level": "Level 3", "year": "2024-2025", "semester": "First Semester"},
        {"name": "Computer Networks", "major": "Computer Engineering", "level": "Level 3", "year": "2024-2025", "semester": "Second Semester"},
        {"name": "Artificial Intelligence", "major": "Computer Engineering", "level": "Level 4", "year": "2024-2025", "semester": "First Semester"},
        {"name": "Information Security", "major": "Computer Engineering", "level": "Level 4", "year": "2024-2025", "semester": "Second Semester"},
        {"name": "Electrical Circuits 1", "major": "Electrical Engineering", "level": "Level 1", "year": "2023-2024", "semester": "First Semester"},
        {"name": "Digital Electronics", "major": "Electrical Engineering", "level": "Level 1", "year": "2023-2024", "semester": "Second Semester"},
        {"name": "General Anatomy", "major": "Medicine", "level": "Level 1", "year": "2023-2024", "semester": "First Semester"},
        {"name": "Physiology", "major": "Medicine", "level": "Level 1", "year": "2023-2024", "semester": "Second Semester"},
        {"name": "Principles of Management", "major": "Business Administration", "level": "Level 1", "year": "2023-2024", "semester": "First Semester"},
        {"name": "Financial Accounting", "major": "Business Administration", "level": "Level 1", "year": "2023-2024", "semester": "Second Semester"}
    ]

    print("⏳ Adding courses to the database...")
    
    success_count = 0
    for course in courses:
        try:
            # Check if the course already exists
            check_query = """
                SELECT 1 FROM Courses
                WHERE name = %s AND major_id = (SELECT major_id FROM Majors WHERE name = %s)
                AND level_id = (SELECT level_id FROM Levels WHERE level_name = %s)
                AND year_id = (SELECT year_id FROM Academic_Years WHERE year_name = %s)
                AND semester_id = (SELECT semester_id FROM Semesters WHERE semester_name = %s)
            """
            exists = execute_query(DB_URL, check_query, (
                course["name"],
                course["major"],
                course["level"],
                course["year"],
                course["semester"]
            ), fetch_one=True)
            
            if exists:
                print(f"⚠ Course already exists: {course['name']}")
                continue
            
            # Insert the new course
            insert_query = """
                INSERT INTO Courses (name, major_id, level_id, year_id, semester_id)
                VALUES (
                    %s,
                    (SELECT major_id FROM Majors WHERE name = %s),
                    (SELECT level_id FROM Levels WHERE level_name = %s),
                    (SELECT year_id FROM Academic_Years WHERE year_name = %s),
                    (SELECT semester_id FROM Semesters WHERE semester_name = %s)
                )
            """
            execute_query(DB_URL, insert_query, (
                course["name"],
                course["major"],
                course["level"],
                course["year"],
                course["semester"]
            ))
            success_count += 1
            print(f"✓ Added course: {course['name']}")
            
        except Exception as e:
            print(f"❌ Failed to add course {course['name']}: {e}")
    
    print(f"\n✅ Successfully added {success_count}/{len(courses)} courses")
    print(f"⚠ Skipped {len(courses) - success_count} duplicate courses")


if __name__ == "__main__":
    # print("\n" + "="*50)
    # print("Database Population Script")
    # print("="*50)
    # populate_database()

    print("\n" + "="*50)
    print("Course Population Script")
    print("="*50)
    add_courses()














# from psycopg import errors
# import sys
# from pathlib import Path

# # Add project root to Python path
# project_root = Path(__file__).parent.parent.parent
# sys.path.append(str(project_root))

# from database.connection import get_db_connection

# def insert_colleges():
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         colleges = [
#             'College of Engineering',
#             'College of Medicine',
#             'College of Science',
#             'College of Arts',
#             'College of Business Administration'
#         ]
        
#         for college in colleges:
#             try:
#                 cursor.execute("INSERT INTO Colleges (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;", (college,))
#                 print(f"[SUCCESS] Added college: {college}")
#             except Exception as e:
#                 print(f"[ERROR] Failed to add college {college}: {e}")
#                 conn.rollback()
        
#         conn.commit()
        
#     except Exception as e:
#         print(f"[ERROR] College insertion failed: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()

# def insert_majors():
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         majors = [
#             ('Computer Engineering', 'College of Engineering'),
#             ('Electrical Engineering', 'College of Engineering'),
#             ('Mechanical Engineering', 'College of Engineering'),
#             ('Medicine', 'College of Medicine'),
#             ('Dental Surgery', 'College of Medicine'),
#             ('Computer Science', 'College of Science'),
#             ('Physics', 'College of Science'),
#             ('Chemistry', 'College of Science'),
#             ('Arabic Language', 'College of Arts'),
#             ('History', 'College of Arts'),
#             ('Business Administration', 'College of Business Administration'),
#             ('Accounting', 'College of Business Administration')
#         ]
        
#         for major_name, college_name in majors:
#             try:
#                 cursor.execute("""
#                     INSERT INTO Majors (name, college_id)
#                     SELECT %s, college_id FROM Colleges WHERE name = %s
#                     ON CONFLICT (name, college_id) DO NOTHING;
#                     """, (major_name, college_name))
#                 print(f"[SUCCESS] Added major: {major_name}")
#             except Exception as e:
#                 print(f"[ERROR] Failed to add major {major_name}: {e}")
#                 conn.rollback()
        
#         conn.commit()
        
#     except Exception as e:
#         print(f"[ERROR] Major insertion failed: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()

# def insert_levels():
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         levels = ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5', 'Level 6', 'Level 7']
        
#         for level in levels:
#             try:
#                 cursor.execute("INSERT INTO Levels (level_name) VALUES (%s) ON CONFLICT (level_name) DO NOTHING;", (level,))
#                 print(f"[SUCCESS] Added level: {level}")
#             except Exception as e:
#                 print(f"[ERROR] Failed to add level {level}: {e}")
#                 conn.rollback()
        
#         conn.commit()
        
#     except Exception as e:
#         print(f"[ERROR] Level insertion failed: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()

# def insert_academic_years():
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         years = ['2023-2024', '2024-2025', '2025-2026']
        
#         for year in years:
#             try:
#                 cursor.execute("INSERT INTO Academic_Years (year_name) VALUES (%s) ON CONFLICT (year_name) DO NOTHING;", (year,))
#                 print(f"[SUCCESS] Added academic year: {year}")
#             except Exception as e:
#                 print(f"[ERROR] Failed to add year {year}: {e}")
#                 conn.rollback()
        
#         conn.commit()
        
#     except Exception as e:
#         print(f"[ERROR] Academic year insertion failed: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()

# def insert_semesters():
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         semesters = ['First Semester', 'Second Semester']
        
#         for semester in semesters:
#             try:
#                 cursor.execute("INSERT INTO Semesters (semester_name) VALUES (%s) ON CONFLICT (semester_name) DO NOTHING;", (semester,))
#                 print(f"[SUCCESS] Added semester: {semester}")
#             except Exception as e:
#                 print(f"[ERROR] Failed to add semester {semester}: {e}")
#                 conn.rollback()
        
#         conn.commit()
        
#     except Exception as e:
#         print(f"[ERROR] Semester insertion failed: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()

# def insert_courses():
#     conn = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         courses = [
#             ('Computer Programming 1', 'Computer Engineering', 'Level 1', '2023-2024', 'First Semester'),
#             ('Engineering Mathematics', 'Computer Engineering', 'Level 1', '2023-2024', 'First Semester'),
#             ('Electrical Circuits', 'Computer Engineering', 'Level 1', '2023-2024', 'Second Semester'),
#             ('Data Structures', 'Computer Engineering', 'Level 2', '2023-2024', 'First Semester'),
#             ('Database Systems', 'Computer Engineering', 'Level 2', '2023-2024', 'Second Semester'),
#             ('Operating Systems', 'Computer Engineering', 'Level 3', '2024-2025', 'First Semester'),
#             ('Computer Networks', 'Computer Engineering', 'Level 3', '2024-2025', 'Second Semester'),
#             ('Artificial Intelligence', 'Computer Engineering', 'Level 4', '2024-2025', 'First Semester'),
#             ('Information Security', 'Computer Engineering', 'Level 4', '2024-2025', 'Second Semester'),
#             ('Electrical Circuits 1', 'Electrical Engineering', 'Level 1', '2023-2024', 'First Semester'),
#             ('Digital Electronics', 'Electrical Engineering', 'Level 1', '2023-2024', 'Second Semester'),
#             ('General Anatomy', 'Medicine', 'Level 1', '2023-2024', 'First Semester'),
#             ('Physiology', 'Medicine', 'Level 1', '2023-2024', 'Second Semester'),
#             ('Principles of Management', 'Business Administration', 'Level 1', '2023-2024', 'First Semester'),
#             ('Financial Accounting', 'Business Administration', 'Level 1', '2023-2024', 'Second Semester')
#         ]
        
#         for course_name, major_name, level_name, year_name, semester_name in courses:
#             try:
#                 cursor.execute("""
#                     INSERT INTO Courses (name, major_id, level_id, year_id, semester_id)
#                     SELECT %s, m.major_id, l.level_id, y.year_id, s.semester_id
#                     FROM Majors m, Levels l, Academic_Years y, Semesters s
#                     WHERE m.name = %s AND l.level_name = %s AND y.year_name = %s AND s.semester_name = %s
#                     ON CONFLICT (name, major_id, level_id, year_id, semester_id) DO NOTHING;
#                     """, (course_name, major_name, level_name, year_name, semester_name))
#                 print(f"[SUCCESS] Added course: {course_name}")
#             except Exception as e:
#                 print(f"[ERROR] Failed to add course {course_name}: {e}")
#                 conn.rollback()
        
#         conn.commit()
        
#     except Exception as e:
#         print(f"[ERROR] Course insertion failed: {e}")
#         if conn:
#             conn.rollback()
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()

# if __name__ == "__main__":
#     # Run each insertion separately
#     insert_colleges()
#     insert_majors()
#     insert_levels()
#     insert_academic_years()
#     insert_semesters()
#     insert_courses()
#     print("[COMPLETE] All insertions attempted")