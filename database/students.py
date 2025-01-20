import sqlite3

class Student:
    table_name = 'students'
    #db_name=":memory:"
    def __init__(self, db_name="database/students.db"):
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS students (
            StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentName TEXT NOT NULL,
            Number TEXT NOT NULL UNIQUE,
            College TEXT NOT NULL,
            Level TEXT NOT NULL CHECK(LENGTH(Level) = 1),
            Specialization TEXT NOT NULL,
            Gender INTEGER NOT NULL CHECK(Gender IN (0, 1)),
            ImagePath TEXT NOT NULL,
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
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
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return None
        finally:
            connection.close()

    def create(self, **kwargs):
        try:
            columns = ', '.join(kwargs.keys())
            placeholders = ', '.join(['?'] * len(kwargs))
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            self.execute_query(query, tuple(kwargs.values()))
            print("Student added successfully.")
        except sqlite3.IntegrityError as e:
            print(f"Error: Duplicate entry for 'Number'. Details: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")

    def all(self, **filters):
        try:
            query = f"SELECT * FROM {self.table_name}"
            if filters:
                conditions = ' AND '.join([f"{key} = ?" for key in filters])
                query += f" WHERE {conditions}"
                return self.execute_read_query(query, tuple(filters.values()))
            return self.execute_read_query(query)
        except Exception as e:
            print(f"Error while fetching data: {e}")
            return []

    def first(self, **filters):
        try:
            result = self.all(**filters)
            return result[0] if result else None
        except Exception as e:
            print(f"Error while fetching first record: {e}")
            return None

    def last(self, **filters):
        try:
            result = self.all(**filters)
            return result[-1] if result else None
        except Exception as e:
            print(f"Error while fetching last record: {e}")
            return None

    def update(self, identifier, **kwargs):
        try:
            set_clause = ', '.join([f"{key} = ?" for key in kwargs])
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE StudentID = ?"
            self.execute_query(query, tuple(kwargs.values()) + (identifier,))
            print(f"Student with ID {identifier} updated successfully.")
        except Exception as e:
            print(f"Error while updating: {e}")

    def delete(self, **kwargs):
        try:
            query = f"DELETE FROM {self.table_name} WHERE "
            conditions = ' AND '.join([f"{key} = ?" for key in kwargs])
            query += conditions
            self.execute_query(query, tuple(kwargs.values()))
            print("Student deleted successfully.")
        except Exception as e:
            print(f"Error while deleting: {e}")

    def exists(self, **kwargs):
        try:
            query = f"SELECT COUNT(*) FROM {self.table_name} WHERE "
            conditions = ' AND '.join([f"{key} = ?" for key in kwargs])
            query += conditions
            result = self.execute_read_query(query, tuple(kwargs.values()))
            return result[0][0] > 0
        except Exception as e:
            print(f"Error while checking existence: {e}")
            return False


    def execute_read_query(self, query, params=()):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        connection.close()
        return result
    

    def find_by_number(self, number):
        """البحث عن طالب باستخدام رقم القيد"""
        query = f"SELECT * FROM {self.table_name} WHERE Number = ?"
        result = self.execute_read_query(query, (number,))
        return result[0] if result else None

    def find_by_name(self, name):
        """البحث عن طالب باستخدام الاسم"""
        query = f"SELECT * FROM {self.table_name} WHERE StudentName LIKE ?"
        result = self.execute_read_query(query, (f"%{name}%",))
        return result

    def get_student_info_by_number(self, number):
        """
        Retrieve the enrollment number, college, and image path of a student based on their enrollment number.
        """
        query = f"SELECT Number, College, ImagePath FROM {self.table_name} WHERE Number = ?"
        result = self.execute_read_query(query, (number,))
        return result[0] if result else None

    def fetch_students_info_by_ids(self, ids):
        """
        Retrieve student data based on a list of IDs.
        """
        try:
            # بناء الاستعلام باستخدام IN
            placeholders = ', '.join(['?'] * len(ids))
            query = f"SELECT StudentID,Number,StudentName,Gender,Level,Specialization,College, ImagePath FROM {self.table_name} WHERE Number IN ({placeholders})"
            return self.execute_read_query(query, tuple(ids))
        except Exception as e:
            print(f"Error while fetching students by IDs: {e}")
            return []

    # def fetch_students_info_by_ids(self, ids):
    #     """
    #     Retrieve student data based on a list of IDs.
    #     """
    #     if not ids:  # التحقق إذا كانت القائمة فارغة
    #         print("Error: The list of IDs is empty.")
    #         return []

    #     try:
    #         # بناء الاستعلام باستخدام IN
    #         placeholders = ', '.join(['?'] * len(ids))
    #         query = f"SELECT StudentID, Number, College, ImagePath FROM {self.table_name} WHERE StudentID IN ({placeholders})"
    #         return self.execute_read_query(query, tuple(ids))
    #     except Exception as e:
    #         print(f"Error while fetching students by IDs: {e}")
    #         return []
