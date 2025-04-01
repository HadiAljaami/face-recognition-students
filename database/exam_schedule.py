import sqlite3

class ExamSchedule:
    table_name = 'exam_schedule'
    
    def __init__(self, db_name="database/students.db"):
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_number TEXT NOT NULL ,
            subject TEXT NOT NULL,
            seat_number TEXT NOT NULL ,
            exam_room TEXT NOT NULL,
            exam_center TEXT NOT NULL,
            exam_datetime DATETIME NOT NULL,
            duration INTEGER NOT NULL
        )
        """
        self.execute_query(query)

    def execute_query(self, query, params=()):
        try:
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
        except sqlite3.IntegrityError as e:
            print(f"Integrity Error: {e}")
        except sqlite3.OperationalError as e:
            print(f"Operational Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")
        finally:
            connection.close()

    def execute_read_query(self, query, params=()):
        try:
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except sqlite3.OperationalError as e:
            print(f"Operational Error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return []
        finally:
            connection.close()

    def add_exam(self, student_number, subject, seat_number, exam_room, exam_center, exam_datetime, duration):
        query = f"""
        INSERT INTO {self.table_name} (student_number, subject, seat_number, exam_room, exam_center, exam_datetime, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.execute_query(query, (student_number, subject, seat_number, exam_room, exam_center, exam_datetime, duration))
        print("Exam schedule added successfully.")

    def get_all_exams(self):
        query = f"SELECT * FROM {self.table_name}"
        return self.execute_read_query(query)

    def find_by_student_number(self, student_number):
        query = f"SELECT * FROM {self.table_name} WHERE student_number = ?"
        return self.execute_read_query(query, (student_number,))

    def update_exam(self, student_number, **kwargs):
        set_clause = ', '.join([f"{key} = ?" for key in kwargs])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE student_number = ?"
        self.execute_query(query, tuple(kwargs.values()) + (student_number,))
        print("Exam schedule updated successfully.")

    def delete_exam_by_student_number(self, student_number):
        query = f"DELETE FROM {self.table_name} WHERE student_number = ?"
        self.execute_query(query, (student_number,))
        print("Exam schedule deleted successfully.")
    
    def delete_exam_by_id(self, exam_id):
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        self.execute_query(query, (exam_id,))
        print("Exam record deleted successfully.")

    