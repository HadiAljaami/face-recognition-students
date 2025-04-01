import sqlite3
from datetime import datetime, timedelta

# def delete_exam_schedule_table(db_name="database/students.db"):
#     connection = sqlite3.connect(db_name)
#     cursor = connection.cursor()
    
#     try:
#         cursor.execute("DROP TABLE IF EXISTS exam_schedule")
#         connection.commit()
#         print("Table 'exam_schedule' deleted successfully.")
#     except sqlite3.Error as e:
#         print(f"Error deleting table: {e}")
#     finally:
#         connection.close()


def insert_sample_exams(db_name="database/students.db"):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    
    sample_data = [
        ("20231001", "Math", "A101", "Room 1", "Center 1", datetime.now(), 120),
        ("20231002", "Physics", "A102", "Room 1", "Center 1", datetime.now() + timedelta(days=1), 90),
        ("20231003", "Chemistry", "A103", "Room 2", "Center 2", datetime.now() + timedelta(days=2), 120),
        ("20231004", "Biology", "A104", "Room 2", "Center 2", datetime.now() + timedelta(days=3), 90),
        ("20231005", "History", "A105", "Room 3", "Center 3", datetime.now() + timedelta(days=4), 120),
        ("20231006", "Geography", "A106", "Room 3", "Center 3", datetime.now() + timedelta(days=5), 90),
        ("20231007", "Computer Science", "A107", "Room 4", "Center 4", datetime.now() + timedelta(days=6), 120),
        ("20231008", "English", "A108", "Room 4", "Center 4", datetime.now() + timedelta(days=7), 90),
        ("20231009", "Arabic", "A109", "Room 5", "Center 5", datetime.now() + timedelta(days=8), 120),
        ("20231010", "Philosophy", "A110", "Room 5", "Center 5", datetime.now() + timedelta(days=9), 90),
    ]

    try:
        cursor.executemany("""
            INSERT INTO exam_schedule (student_number, subject, seat_number, exam_room, exam_center, exam_datetime, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        
        connection.commit()
        print("10 sample exam records inserted successfully.")
    
    except sqlite3.Error as e:
        print(f"Error inserting sample exams: {e}")
    
    finally:
        connection.close()

# استدعاء الدالة لإضافة الصفوف
#delete_exam_schedule_table()
insert_sample_exams()

