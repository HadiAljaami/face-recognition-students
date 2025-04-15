# Step 2: Repository for student_vectors table (vectors_repository.py)
# Located in database/vectors_repository.py
from database.connection import get_db_connection

class VectorsRepository:

    def insert_vector(self, student_id, college, vector):
        try:
            query = """
            INSERT INTO student_vectors (student_id, college, vector)
            VALUES (%s, %s, %s) RETURNING id;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (student_id, college, vector))
                    return cursor.fetchone()["id"]
        except Exception as e:
            print("Error inserting vector:", e)
            raise

    def update_vector_by_id(self, vector_id, vector):
        try:
            query = """
            UPDATE student_vectors
            SET  vector = %s
            WHERE id = %s;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (vector, vector_id))
                    return cursor.rowcount
        except Exception as e:
            print("Error updating vector:", e)
            raise

    def update_vector2(self, student_id, college, vector):
        try:
            query = """
            UPDATE student_vectors
            SET college = %s, vector = %s
            WHERE student_id = %s;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (college, vector, student_id))
                    return cursor.rowcount
        except Exception as e:
            print("Error updating vector:", e)
            raise

    def delete_vector(self, student_id):
        try:
            query = """
            DELETE FROM student_vectors
            WHERE student_id = %s;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (student_id,))
                    return cursor.rowcount
        except Exception as e:
            print("Error deleting vector:", e)
            raise

    def get_all_vectors(self):
        try:
            query = "SELECT * FROM student_vectors;"
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except Exception as e:
            print("Error fetching all vectors:", e)
            raise

    def get_vector_by_student_id(self, student_id):
        try:
            query = "SELECT * FROM student_vectors WHERE student_id = %s;"
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (student_id,))
                    return cursor.fetchone()
        except Exception as e:
            print("Error fetching vector by student ID:", e)
            raise

    def search_similar_vectors(self, vector, threshold=0.8, limit=1):
        """
        البحث عن متجهات مشابهة بناءً على التشابه
        """
        try: 
            query = """
            SELECT id,student_id,college,created_at,   (1 - (vector <-> %s::vector)) * 100 AS similarity
            FROM student_vectors
            WHERE (vector <-> %s::vector) <= %s
            ORDER BY similarity DESC
            LIMIT %s;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (vector, vector, threshold, limit))
                    return cursor.fetchall()
        except Exception as e:
            print("Error searching similar vectors:", e)
            raise

    def search_similar_vectors_in_college(self, vector, college, threshold=0.8, limit=1):
        """
        البحث عن متجهات مشابهة ضمن نطاق كلية معينة
        """
        try:#(vector <-> %s::vector) AS distance
            query = """
            SELECT id,student_id,college,created_at,  (1 - (vector <-> %s::vector)) * 100 AS similarity
            FROM student_vectors
            WHERE college = %s AND (vector <-> %s::vector) <= %s
            ORDER BY similarity DESC
            LIMIT %s;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (vector, college, vector, threshold, limit))
                    return cursor.fetchall()
        except Exception as e:
            print("Error searching similar vectors in college:", e)
            raise


    def search_similar_vectors_by_studen_id(self, vector, studen_id, threshold=0.8):
        """
        البحث عن متجهات مشابهة عبر رقم الطالب  
        """
        try:#(vector <-> %s::vector) AS distance
            query = """
            SELECT id,student_id,college,created_at,  (1 - (vector <-> %s::vector)) * 100 AS similarity
            FROM student_vectors
            WHERE studen_id = %s AND (vector <-> %s::vector) <= %s;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (vector, studen_id, vector, threshold, limit))
                    return cursor.fetchall()
        except Exception as e:
            print("Error searching similar vectors studen id:", e)
            raise
















        # def search_similar_vectors(self, vector, threshold=0.8):
        #     try:
        #         query = """
        #         SELECT *, (vector <-> %s) AS distance
        #         FROM student_vectors
        #         WHERE (vector <-> %s) <= %s
        #         ORDER BY distance ASC;
        #         """
        #         with get_db_connection() as conn:
        #             with conn.cursor() as cursor:
        #                 cursor.execute(query, (vector, vector, threshold))
        #                 return cursor.fetchall()
        #     except Exception as e:
        #         print("Error searching similar vectors:", e)
        #         raise

        # def search_similar_vectors_in_college(self, vector, college, threshold=0.8):
        #     try:
        #         query = """
        #         SELECT *, (vector <-> %s) AS distance
        #         FROM student_vectors
        #         WHERE college = %s AND (vector <-> %s) <= %s
        #         ORDER BY distance ASC;
        #         """
        #         with get_db_connection() as conn:
        #             with conn.cursor() as cursor:
        #                 cursor.execute(query, (vector, college, vector, threshold))
        #                 return cursor.fetchall()
        #     except Exception as e:
        #         print("Error searching similar vectors in college:", e)
        #         raise

    def get_all_student_ids(self):
        try:
            query = "SELECT student_id FROM student_vectors;"
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchall()
                    return [row["student_id"] for row in result]
        except Exception as e:
            print("Error fetching student IDs:", e)
            raise
