from typing import List, Dict, Optional
from database.connection import get_db_connection
from psycopg import sql, errors
from datetime import datetime, date, time

class ExamDistributionRepository:

    def assign_exam_to_student(self, student_id: str, student_name: str, exam_id: int, device_id: int = None) -> Dict:
        """Assign an exam to a student with optional device assignment (insert or update)"""
        query = sql.SQL("""
        WITH upserted_distribution AS (
            INSERT INTO exam_distribution (student_id, student_name, exam_id, device_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (student_id)
            DO UPDATE SET 
                student_name = EXCLUDED.student_name,
                exam_id = EXCLUDED.exam_id,
                device_id = EXCLUDED.device_id,
                assigned_at = CURRENT_TIMESTAMP
            RETURNING id, student_id, student_name, exam_id, device_id, assigned_at, xmax

        )
        SELECT 
            d.id,
            d.student_id,
            d.student_name,
            d.exam_id,
            e.exam_date,
            e.exam_start_time,
            e.exam_end_time,
            c.name AS course_name,
            m.name AS major_name,
            col.name AS college_name,
            l.level_name,
            ay.year_name,
            s.semester_name,
            d.device_id,
            dev.center_id,
            cen.center_name,
            d.assigned_at,
            d.xmax
        FROM upserted_distribution d
        JOIN Exams e ON d.exam_id = e.exam_id
        JOIN Courses c ON e.course_id = c.course_id
        JOIN Majors m ON e.major_id = m.major_id
        JOIN Colleges col ON e.college_id = col.college_id
        JOIN Levels l ON e.level_id = l.level_id
        JOIN Academic_Years ay ON e.year_id = ay.year_id
        JOIN Semesters s ON e.semester_id = s.semester_id
        LEFT JOIN devices dev ON d.device_id = dev.id
        LEFT JOIN exam_centers cen ON dev.center_id = cen.id
        """)
       
        try:

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (student_id, student_name, exam_id, device_id))
                    result = cursor.fetchone()
                    conn.commit()
                    
                    if not result:
                        return None
                       
                    action = "insert" if result["xmax"] == 0 else "update"
                    

                    result.pop("xmax")  # Remove internal field
                    result["action"] = action

                    # Convert datetime values to string
                    for key, value in result.items():
                        if isinstance(value, (date, time, datetime)):
                            result[key] = value.isoformat()

                    return result

        except errors.ForeignKeyViolation as e:
            error_msg = str(e)
            if 'exam_distribution_device_id_fkey' in error_msg:
                raise ValueError("Device not found.")
            elif 'exam_distribution_exam_id_fkey' in error_msg:
                raise ValueError("Exam not found.")
            else:
                raise ValueError("Invalid reference.")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    # def assign_exam_to_student(self, student_id: str, student_name: str, exam_id: int, device_id: int = None) -> Dict:
    #     """Assign an exam to a student with optional device assignment"""
    #     query = sql.SQL("""
    #     WITH upserted_distribution AS (
    #         INSERT INTO exam_distribution (student_id, student_name, exam_id, device_id)
    #         VALUES (%s, %s, %s, %s)
    #         ON CONFLICT (student_id)
    #         DO UPDATE SET 
    #             student_name = EXCLUDED.student_name,
    #             device_id = EXCLUDED.device_id,
    #             assigned_at = CURRENT_TIMESTAMP
    #         RETURNING id, student_id, student_name, exam_id, device_id, assigned_at
    #     )
    #     SELECT 
    #         d.id,
    #         d.student_id,
    #         d.student_name,
    #         d.exam_id,
    #         e.exam_date,
    #         e.exam_start_time,
    #         e.exam_end_time,
    #         c.name AS course_name,
    #         m.name AS major_name,
    #         col.name AS college_name,
    #         l.level_name,
    #         ay.year_name,
    #         s.semester_name,
    #         d.device_id,
    #         dev.center_id,
    #         cen.center_name,
    #         d.assigned_at
    #     FROM inserted_distribution d
    #     JOIN Exams e ON d.exam_id = e.exam_id
    #     JOIN Courses c ON e.course_id = c.course_id
    #     JOIN Majors m ON e.major_id = m.major_id
    #     JOIN Colleges col ON e.college_id = col.college_id
    #     JOIN Levels l ON e.level_id = l.level_id
    #     JOIN Academic_Years ay ON e.year_id = ay.year_id
    #     JOIN Semesters s ON e.semester_id = s.semester_id
    #     LEFT JOIN devices dev ON d.device_id = dev.id
    #     LEFT JOIN exam_centers cen ON dev.center_id = cen.id
    #     """)
        
    #     try:
    #         with get_db_connection() as conn:
    #             with conn.cursor() as cursor:
    #                 cursor.execute(query, (student_id, student_name, exam_id, device_id))
    #                 result = cursor.fetchone()
    #                 conn.commit()
                    
    #                 if not result:
    #                     return None
                    
    #                 # تحويل أنواع التاريخ والوقت إلى strings
    #                 for key, value in result.items():
    #                     if isinstance(value, (date, time, datetime)):
    #                         result[key] = value.isoformat()

    #                 return result
    #     except errors.UniqueViolation:
    #         raise ValueError("This student already has an assigned exam.")
    #     except errors.ForeignKeyViolation as e:
    #         raise ValueError(f"Invalid reference: {str(e)}")
    #     except errors.Error as e:
    #         raise RuntimeError(f"Database error: {str(e)}")

    def update_exam_distribution(self, distribution_id: int, student_name: str = None, 
                               exam_id: int = None, device_id: int = None) -> Optional[Dict]:
        """Update exam distribution record including student name"""
        updates = []
        params = []
        
        if student_name is not None:
            updates.append(sql.SQL("student_name = %s"))
            params.append(student_name)
        if exam_id is not None:
            updates.append(sql.SQL("exam_id = %s"))
            params.append(exam_id)
        if device_id is not None:
            updates.append(sql.SQL("device_id = %s"))
            params.append(device_id)
            
        if not updates:
            raise ValueError("No fields provided for update")
            
        params.append(distribution_id)
        
        update_query = sql.SQL("""
        WITH updated_distribution AS (
            UPDATE exam_distribution
            SET {updates}
            WHERE id = %s
            RETURNING id, student_id, student_name, exam_id, device_id, assigned_at
        )
        SELECT 
            d.id,
            d.student_id,
            d.student_name,
            d.exam_id,
            e.exam_date,
            e.exam_start_time,
            e.exam_end_time,
            c.name AS course_name,
            m.name AS major_name,
            col.name AS college_name,
            l.level_name,
            ay.year_name,
            s.semester_name,
            d.device_id,
            dev.center_id,
            cen.center_name,
            d.assigned_at
        FROM updated_distribution d
        JOIN Exams e ON d.exam_id = e.exam_id
        JOIN Courses c ON e.course_id = c.course_id
        JOIN Majors m ON e.major_id = m.major_id
        JOIN Colleges col ON e.college_id = col.college_id
        JOIN Levels l ON e.level_id = l.level_id
        JOIN Academic_Years ay ON e.year_id = ay.year_id
        JOIN Semesters s ON e.semester_id = s.semester_id
        LEFT JOIN devices dev ON d.device_id = dev.id
        LEFT JOIN exam_centers cen ON dev.center_id = cen.id
        """).format(updates=sql.SQL(", ").join(updates))
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(update_query, params)
                    result = cursor.fetchone()
                    conn.commit()
                    return result
        except errors.UniqueViolation:
            raise ValueError("This exam is already assigned to the student")
        except errors.ForeignKeyViolation as e:
            raise ValueError(f"Invalid reference: {str(e)}")
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def delete_multiple_distributions(self, distribution_ids: List[int]) -> int:
        """Delete multiple exam distribution records"""
        if not distribution_ids:
            return 0
            
        query = sql.SQL("""
        DELETE FROM exam_distribution
        WHERE id = ANY(%s)
        RETURNING id;
        """)
        
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (distribution_ids,))
                    deleted_count = len(cursor.fetchall())
                    conn.commit()
                    return deleted_count
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")
    
    def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        """
        البحث عن بيانات الطالب باستخدام رقم القيد
        
        Args:
            student_id: رقم القيد الجامعي للطالب
            
        Returns:
            قاموس يحتوي على بيانات الطالب أو None إذا لم يتم العثور عليه
        """
        query = sql.SQL("""
        SELECT
            ed.student_id,
            ed.student_name,
            d.device_number,
            d.room_number,
            ec.center_name,
            e.exam_id,
            e.exam_date,
            e.exam_start_time,
            e.exam_end_time,
            c.name AS course_name,
            col.name AS college_name,
            m.name AS major_name,
            l.level_name,
            s.semester_name,
            ay.year_name AS academic_year
        FROM exam_distribution ed
        JOIN devices d ON ed.device_id = d.id
        JOIN exam_centers ec ON d.center_id = ec.id
        JOIN Exams e ON ed.exam_id = e.exam_id
        JOIN Courses c ON e.course_id = c.course_id
        JOIN Colleges col ON e.college_id = col.college_id
        JOIN Majors m ON e.major_id = m.major_id
        JOIN Levels l ON e.level_id = l.level_id
        JOIN Semesters s ON e.semester_id = s.semester_id
        JOIN Academic_Years ay ON e.year_id = ay.year_id
        WHERE ed.student_id = %s
        LIMIT 1;
        """)
        

#  with get_db_connection() as conn:
#                 with conn.cursor() as cursor:
#                     cursor.execute(query, (distribution_ids,))
#                     deleted_count = len(cursor.fetchall())
#                     conn.commit()
#                     return deleted_count

        try: 
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (student_id,))
                    result = cursor.fetchone()
                    
                    if not result:
                        return None
                    
                    # تحويل أنواع التاريخ والوقت إلى strings
                    if isinstance(result.get('exam_date'), date):
                        result['exam_date'] = result['exam_date'].isoformat()
                    if isinstance(result.get('exam_start_time'), time):
                        result['exam_start_time'] = str(result['exam_start_time'])
                    if isinstance(result.get('exam_end_time'), time):
                        result['exam_end_time'] = str(result['exam_end_time'])
                    
                    return result
            
        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# جلب ولكن عرض رقم الغرفة مع كل طالب 

    # def get_exam_distribution_report(self, exam_id: int) -> Dict:
    #         """
    #         Get exam distribution report with header and students list
    #         Returns: {
    #             'header': Dict with exam details,
    #             'students': List of student dictionaries
    #         }
    #         """
    #         # استعلام بيانات الهيدر
    #         header_query = """
    #         SELECT 
    #             c.name AS course_name,
    #             e.exam_date,
    #             e.exam_start_time,
    #             e.exam_end_time,
    #             col.name AS college_name,
    #             m.name AS major_name,
    #             l.level_name,
    #             s.semester_name,
    #             ay.year_name AS academic_year,
    #             ec.center_name
    #         FROM Exams e
    #         JOIN Courses c ON e.course_id = c.course_id
    #         JOIN Colleges col ON e.college_id = col.college_id
    #         JOIN Majors m ON e.major_id = m.major_id
    #         JOIN Levels l ON e.level_id = l.level_id
    #         JOIN Semesters s ON e.semester_id = s.semester_id
    #         JOIN Academic_Years ay ON e.year_id = ay.year_id
    #         JOIN exam_distribution ed ON e.exam_id = ed.exam_id
    #         JOIN devices d ON ed.device_id = d.id
    #         JOIN exam_centers ec ON d.center_id = ec.id
    #         WHERE e.exam_id = %s
    #         LIMIT 1;
    #         """

    #         # استعلام قائمة الطلاب
    #         students_query = """
    #         SELECT 
    #             d.device_number,
    #             ed.student_id,
    #             ed.student_name,
    #             d.room_number
    #         FROM exam_distribution ed
    #         JOIN devices d ON ed.device_id = d.id
    #         WHERE ed.exam_id = %s
    #         ORDER BY  d.room_number,d.device_number ;
    #         """

    #         try:
    #             with get_db_connection() as conn:
    #                 with conn.cursor() as cursor:
    #                     # جلب بيانات الهيدر
    #                     cursor.execute(header_query, (exam_id,))
    #                     header_data = cursor.fetchone()
                        
    #                     if not header_data:
    #                         raise ValueError("Exam not found or no students assigned")

    #                     # جلب بيانات الطلاب
    #                     cursor.execute(students_query, (exam_id,))
    #                     students_data = cursor.fetchall()

    #                     # تحويل أنواع البيانات
    #                     formatted_header = self._format_header(header_data)
    #                     formatted_students =students_data #self._format_students(students_data)

    #                     return {
    #                         'header': formatted_header,
    #                         'students': formatted_students
    #                     }

    #         except errors.Error as e:
    #             raise RuntimeError(f"Database error: {str(e)}")

    # def _format_header(self, header_data: Dict) -> Dict:
    #     """Convert header data types to JSON-serializable formats"""
    #     return {
    #         'course_name': header_data['course_name'],
    #         'exam_date': header_data['exam_date'].isoformat() if header_data['exam_date'] else None,
    #         'exam_start_time': str(header_data['exam_start_time']) if header_data['exam_start_time'] else None,
    #         'exam_end_time': str(header_data['exam_end_time']) if header_data['exam_end_time'] else None,
    #         'college_name': header_data['college_name'],
    #         'major_name': header_data['major_name'],
    #         'level_name': header_data['level_name'],
    #         'semester_name': header_data['semester_name'],
    #         'academic_year': header_data['academic_year'],
    #         'center_name': header_data['center_name']
    #     }

    # def _format_students(self, students_data: List[Dict]) -> List[Dict]:
    #     """Convert students data types to JSON-serializable formats"""
    #     return [{
    #         'device_number': student['device_number'],
    #         'student_id': student['student_id'],
    #         'student_name': student['student_name'],
    #         'room_number': student['room_number']
    #     } for student in students_data]

#----------------------------------------------------------------------
#عرض الغرفة في الهدري 
# جلب بدون ترقيم الطلاب 
    # def get_exam_distribution_report(self, exam_id: int) -> Dict:
    #     """
    #     Get exam distribution report where كل مجموعة تتكون من هيدر مدمج مع 
    #     بيانات المركز والغرفة، ثم مصفوفة الطلاب المرتبطين بهذه الغرفة.
        
    #     مثال على النتيجة:
    #     {
    #     "groups": [
    #         {
    #         "header": {
    #             "room_number": "102",
    #             "center_name": "كلية الحاسوب",
    #             "academic_year": "2024-2025",
    #             "college_name": "االحاسوب وتكنلوجيا المعلومات",
    #             "course_name": "Introduction to Computer Science",
    #             "exam_date": "2033-12-15",
    #             "exam_end_time": "11:00:00",
    #             "exam_start_time": "09:00:00",
    #             "level_name": "First Year",
    #             "major_name": "علوم حاسوب",
    #             "semester_name": "الترم الثاني"
    #         },
    #         "students": [
    #             {
    #             "device_number": 124,
    #             "student_id": "113",
    #             "student_name": "شريف الحكيم"
    #             },
    #             {
    #             "device_number": 124,
    #             "student_id": "112",
    #             "student_name": "أحمد محمد"
    #             }
    #         ]
    #         }
    #     ]
    #     }
    #     """
    #     # استعلام لجلب بيانات الاختبار المشتركة (الهيدر بدون المركز والغرفة)
    #     header_query = """
    #     SELECT 
    #         c.name AS course_name,
    #         e.exam_date,
    #         e.exam_start_time,
    #         e.exam_end_time,
    #         col.name AS college_name,
    #         m.name AS major_name,
    #         l.level_name,
    #         s.semester_name,
    #         ay.year_name AS academic_year
    #     FROM Exams e
    #     JOIN Courses c ON e.course_id = c.course_id
    #     JOIN Colleges col ON e.college_id = col.college_id
    #     JOIN Majors m ON e.major_id = m.major_id
    #     JOIN Levels l ON e.level_id = l.level_id
    #     JOIN Semesters s ON e.semester_id = s.semester_id
    #     JOIN Academic_Years ay ON e.year_id = ay.year_id
    #     JOIN exam_distribution ed ON e.exam_id = ed.exam_id
    #     WHERE e.exam_id = %s
    #     LIMIT 1;
    #     """

    #     # استعلام لجلب بيانات الطلاب مع معلومات الغرفة والمركز
    #     students_query = """
    #     SELECT 
    #         d.device_number,
    #         ed.student_id,
    #         ed.student_name,
    #         d.room_number,
    #         ec.center_name
    #     FROM exam_distribution ed
    #     JOIN devices d ON ed.device_id = d.id
    #     JOIN exam_centers ec ON d.center_id = ec.id
    #     WHERE ed.exam_id = %s
    #     ORDER BY ec.center_name, d.room_number, d.device_number;
    #     """

    #     try:
    #         with get_db_connection() as conn:
    #             with conn.cursor() as cursor:
    #                 # جلب بيانات الهيدر الأساسي
    #                 cursor.execute(header_query, (exam_id,))
    #                 header_data = cursor.fetchone()
    #                 if not header_data:
    #                     raise ValueError("Exam not found or no students assigned")
    #                 base_header = self._format_header(header_data)

    #                 # جلب بيانات الطلاب مع معلومات الغرفة والمركز
    #                 cursor.execute(students_query, (exam_id,))
    #                 students_data = cursor.fetchall()

    #                 # تجميع الطلاب حسب (center_name, room_number)
    #                 groups = {}
    #                 for student in students_data:
    #                     # المفتاح هو (center_name, room_number)
    #                     key = (student['center_name'], student['room_number'])
    #                     if key not in groups:
    #                         groups[key] = {
    #                             'students': [],
    #                             # سنستخدم هنا نفس بيانات الهيدر الأساسي ونضيف معلومات المجموعة
    #                             'center_name': student['center_name'],
    #                             'room_number': student['room_number']
    #                         }
    #                     groups[key]['students'].append({
    #                         'device_number': student['device_number'],
    #                         'student_id': student['student_id'],
    #                         'student_name': student['student_name']
    #                     })

    #                 # بناء النتيجة النهائية بحيث يتم دمج الهيدر مع بيانات الغرفة والمركز
    #                 groups_list = []
    #                 for key, group in groups.items():
    #                     # إنشاء نسخة من الهيدر الأساسي ودمج معلومات المجموعة
    #                     group_header = base_header.copy()
    #                     group_header['center_name'] = group['center_name']
    #                     group_header['room_number'] = group['room_number']
    #                     groups_list.append({
    #                         'header': group_header,
    #                         'students': group['students']
    #                     })

    #                 return {'groups': groups_list}

    #     except errors.Error as e:
    #         raise RuntimeError(f"Database error: {str(e)}")

# جلب مع ترقيم الطلاب 
    def get_exam_distribution_report(self, exam_id: int) -> Dict:
        """
        Get exam distribution report حيث يتضمن كل مجموعة:
        - هيدر يحتوي على تفاصيل الاختبار بالإضافة إلى معلومات (center_name, room_number)
        - قائمة الطلاب مع ترقيم يبدأ من 1 لكل مجموعة
        مثال على النتيجة:
        {
        "groups": [
            {
            "header": { ... تفاصيل الاختبار مع room_number و center_name ... },
            "students": [
                {
                "device_number": 124,
                "student_id": "113",
                "student_name": "شريف الحكيم",
                "number": 1
                },
                {
                "device_number": 124,
                "student_id": "112",
                "student_name": "أحمد محمد",
                "number": 2
                }
            ]
            },
            {
            "header": { ... تفاصيل الاختبار مع room_number و center_name ... },
            "students": [
                {
                "device_number": 123,
                "student_id": "114",
                "student_name": "هادي",
                "number": 1
                }
            ]
            }
        ]
        }
        """
        # استعلام لجلب بيانات الاختبار المشتركة (الهيدر الأساسي)
        header_query = """
        SELECT 
            c.name AS course_name,
            e.exam_date,
            e.exam_start_time,
            e.exam_end_time,
            col.name AS college_name,
            m.name AS major_name,
            l.level_name,
            s.semester_name,
            ay.year_name AS academic_year
        FROM Exams e
        JOIN Courses c ON e.course_id = c.course_id
        JOIN Colleges col ON e.college_id = col.college_id
        JOIN Majors m ON e.major_id = m.major_id
        JOIN Levels l ON e.level_id = l.level_id
        JOIN Semesters s ON e.semester_id = s.semester_id
        JOIN Academic_Years ay ON e.year_id = ay.year_id
        JOIN exam_distribution ed ON e.exam_id = ed.exam_id
        WHERE e.exam_id = %s
        LIMIT 1;
        """

        # استعلام لجلب بيانات الطلاب مع معلومات الغرفة والمركز
        students_query = """
        SELECT 
            d.device_number,
            ed.student_id,
            ed.student_name,
            d.room_number,
            ec.center_name
        FROM exam_distribution ed
        JOIN devices d ON ed.device_id = d.id
        JOIN exam_centers ec ON d.center_id = ec.id
        WHERE ed.exam_id = %s
        ORDER BY ec.center_name, d.room_number, d.device_number;
        """

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # جلب بيانات الهيدر الأساسي
                    cursor.execute(header_query, (exam_id,))
                    header_data = cursor.fetchone()
                    if not header_data:
                        raise ValueError("Exam not found or no students assigned")
                    base_header = self._format_header(header_data)

                    # جلب بيانات الطلاب
                    cursor.execute(students_query, (exam_id,))
                    students_data = cursor.fetchall()

                    # تجميع الطلاب حسب (center_name, room_number)
                    groups = {}
                    for student in students_data:
                        # المفتاح هو (center_name, room_number)
                        key = (student['center_name'], student['room_number'])
                        if key not in groups:
                            groups[key] = {
                                'students': [],
                                'center_name': student['center_name'],
                                'room_number': student['room_number']
                            }
                        groups[key]['students'].append({
                            'device_number': student['device_number'],
                            'student_id': student['student_id'],
                            'student_name': student['student_name']
                        })

                    # بناء النتيجة النهائية بحيث يتم دمج الهيدر مع بيانات المجموعة وترقيم الطلاب
                    groups_list = []
                    for group in groups.values():
                        # إنشاء نسخة من الهيدر الأساسي وإضافة معلومات المجموعة
                        group_header = base_header.copy()
                        group_header['center_name'] = group['center_name']
                        group_header['room_number'] = group['room_number']
                        
                        # ترقيم الطلاب داخل المجموعة بحيث يبدأ الترقيم من 1
                        for idx, student in enumerate(group['students'], start=1):
                            student['number'] = idx

                        groups_list.append({
                            'header': group_header,
                            'students': group['students']
                        })

                    return {'groups': groups_list}

        except errors.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")

    def _format_header(self, header_data: Dict) -> Dict:
        """Convert header data types to JSON-serializable formats"""
        return {
            'course_name': header_data['course_name'],
            'exam_date': header_data['exam_date'].isoformat() if header_data['exam_date'] else None,
            'exam_start_time': str(header_data['exam_start_time']) if header_data['exam_start_time'] else None,
            'exam_end_time': str(header_data['exam_end_time']) if header_data['exam_end_time'] else None,
            'college_name': header_data['college_name'],
            'major_name': header_data['major_name'],
            'level_name': header_data['level_name'],
            'semester_name': header_data['semester_name'],
            'academic_year': header_data['academic_year']
        }

