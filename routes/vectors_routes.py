from flask import Blueprint, request, jsonify
from services.vectors_service import VectorsService
from services.image_processor import ImageProcessor
from services.students_service import fetch_student_info_by_number,fetch_students_by_ids
from database.vectors_repository import VectorsRepository
from datetime import datetime, timedelta
import os
from database.connection import get_db_connection
from psycopg.rows import dict_row 
from psycopg import sql

vectors_routes = Blueprint("vectors_routes", __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # مجلد مؤقت داخل المشروع

repository = VectorsRepository()
service = VectorsService(repository)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@vectors_routes.route("/vectors/add-vector", methods=["POST"])
def add_vector():
    """
    Add a vector to the database using student ID and image.
    ---
    tags:
      - Vectors
    parameters:
      - name: student_id
        in: formData
        type: string
        required: true
        description: The student's ID.
      - name: image
        in: formData
        type: file
        required: true
        description: The image file to upload (JPG, JPEG, PNG only).
    responses:
      201:
        description: Vector added successfully.
      400:
        description: Bad Request. Validation failed.
      500:
        description: Internal Server Error.
    """
    try:
        # التحقق من وجود الملف
        if "image" not in request.files:
            return jsonify({"error": "No file uploaded."}), 400

        file = request.files["image"]
        student_id = request.form.get("student_id")

        if not student_id:
            return jsonify({"error": "Student ID is required."}), 400

        # التحقق من وجود الطالب في قاعدة بيانات الطلاب
        student_data = fetch_student_info_by_number(student_id)
        if not student_data:
            return jsonify({"error": f"Student with ID {student_id} not found."}), 400

        college = student_data[1]

        # حفظ الملف مؤقتًا
        filename = ImageProcessor.secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # تحويل الصورة إلى متجه
        vector = ImageProcessor.convert_image_to_vector(filepath)

        # إزالة الملف المؤقت
        os.remove(filepath)

        repository = VectorsRepository()
        service = VectorsService(repository)
        # إضافة المتجه إلى قاعدة البيانات
        vector_id = service.add_vector(student_id, college, vector)
        return jsonify({"message": "Vector added successfully.", "id": vector_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vectors_routes.route("/vectors/update-vector/<int:vector_id>", methods=["PUT"])
def update_vector(vector_id):
    """
    Update a vector in the database using vector ID and image.
    ---
    tags:
      - Vectors
    parameters:
      - name: vector_id
        in: path
        type: integer
        required: true
        description: The ID of the vector to update.
      - name: image
        in: formData
        type: file
        required: true
        description: The image file to upload (JPG, JPEG, PNG only).
    responses:
      200:
        description: Vector updated successfully.
      400:
        description: Bad Request. Validation failed.
      500:
        description: Internal Server Error.
    """
    try:
        # التحقق من وجود الملف
        if "image" not in request.files:
            return jsonify({"error": "No file uploaded."}), 400

        file = request.files["image"]

        # حفظ الملف مؤقتًا
        filename = ImageProcessor.secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # تحويل الصورة إلى متجه
        vector = ImageProcessor.convert_image_to_vector(filepath)

        # إزالة الملف المؤقت
        os.remove(filepath)

        #repository = VectorsRepository()
        #service = VectorsService(repository)
        # تحديث المتجه في قاعدة البيانات
        success = service.update_vector_by_id(vector_id, vector)
        if success:
            return jsonify({"message": "Vector updated successfully."}), 200
        else:
            return jsonify({"error": "Failed to update vector. Check vector ID."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vectors_routes.route("/vectors/<student_id>", methods=["GET"])
def get_vector(student_id):
    """الحصول على متجه باستخدام ID
    ---
    tags:
      - Vectors
    parameters:
      - name: student_id
        in: path
        type: string
        required: true
        example: "S12345"
    responses:
      200:
        description: تم جلب المتجه بنجاح
      404:
        description: لم يتم العثور على المتجه
      500:
        description: خطأ في السيرفر
    """
    try:
        vector = service.get_vector_by_id(student_id)
        if vector:
            return jsonify(vector), 200
        return jsonify({"message": "Vector not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vectors_routes.route("/vectors", methods=["GET"])
def get_all_vectors():
    """جلب جميع المتجهات
    ---
    tags:
      - Vectors
    responses:
      200:
        description: تم جلب جميع المتجهات بنجاح
      500:
        description: خطأ في السيرفر
    """
    try:
        vectors = service.get_all_vectors()
       
        return jsonify(vectors), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@vectors_routes.route("/vectors/all-student-ids", methods=["GET"])
def get_all_student_ids():
    """جلب جميع ارقام الطلاب
    ---
    tags:
      - Vectors
    responses:
      200:
        description: تم جلب جميع ارقام الطلاب بنجاح
      500:
        description: خطأ في السيرفر
    """
    try:
        studenIds = service.get_all_student_ids()
      
        return jsonify(studenIds), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vectors_routes.route("/vectors/<student_id>", methods=["DELETE"])
def delete_vector(student_id):
    """حذف متجه باستخدام ID
    ---
    tags:
      - Vectors
    parameters:
      - name: student_id
        in: path
        type: string
        required: true
        example: "S12345"
    responses:
      200:
        description: تم حذف المتجه بنجاح
      404:
        description: لم يتم العثور على المتجه
      500:
        description: خطأ في السيرفر
    """
    try:
        result = service.delete_vector(student_id)
        if result:
            return jsonify({"message": "Vector deleted successfully."}), 200
        return jsonify({"message": "Vector not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vectors_routes.route("/vectors/search", methods=["POST"])
def search_vectors():
    """
    Search for similar vectors using an image.
    ---
    tags:
      - Vectors
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: The face image to search for.
      - name: threshold
        in: formData
        type: number
        required: true
        description: The threshold for similarity.
      - name: limit
        in: formData
        type: integer
        required: true
        description: The number of desired results.
    responses:
      200:
        description: Search results.
      400:
        description: Input error.
      500:
        description: Server error.
    """
    try:
        # Check if the image file is in the request
        if "image" not in request.files:
            return jsonify({"error": "Image file is required."}), 400

        image_file = request.files["image"]
        threshold = request.form.get("threshold", type=float)
        limit = request.form.get("limit", type=int)

        if threshold is None or limit is None:
            return jsonify({"error": "Threshold and limit are required."}), 400

        # Save the image temporarily
        filename = ImageProcessor.secure_filename(image_file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(temp_path)

        # Convert the image to a vector
        query_vector = ImageProcessor.convert_image_to_vector(temp_path)

        # Search for similar vectors
        results = service.find_similar_vectors(query_vector, threshold, limit)

        # Delete the temporary image
        os.remove(temp_path)

        # Extract student_id from the results
        student_ids = [result["student_id"] for result in results]

        # Fetch student data using the fetch_students_info_by_ids function
        students_data = fetch_students_by_ids(student_ids)

        # Convert students_data to a list of dictionaries
        students_dicts = []
        for student in students_data:
            students_dicts.append({
                #"StudentID": student[0],  # ID
                "Number": student[1],  # Registration number
                "StudentName": student[2],  # Student name
                "Gender": student[3],  # Gender
                "Level": student[4],  # Level
                "Specialization": student[5],  # Specialization
                "College": student[6],  # College
                "ImagePath": student[7]  # Image path
            })

        # الحصول على الوقت الحالي من السيرفر
        current_datetime = datetime.now()

        # Update student data by adding new fields
        for result in results:
            student_id = result["student_id"]
            # Find the student data in students_dicts
            student_info = next((student for student in students_dicts if str(student["Number"]) == student_id), None)
            if student_info:
                exam_distribution_data = get_exam_distribution_by_student(student_id)
                if exam_distribution_data:
                    exam_id = exam_distribution_data.get("exam_id")
                    exam_data = get_exam_data(exam_id)
                    if exam_data:
                        # استخراج تاريخ الاختبار ووقت بداية الاختبار
                        exam_date_str = exam_data.get("exam_date")
                        exam_start_time_str = exam_data.get("exam_start_time")
                        
                        # دمج التاريخ والوقت لتكوين كائن datetime
                        exam_datetime_str = f"{exam_date_str} {exam_start_time_str}"
                        exam_datetime = datetime.strptime(exam_datetime_str, "%Y-%m-%d %H:%M:%S")
                        
                        # تحديد النافذة الزمنية:
                        # صالح إذا كان الوقت الحالي بين (exam_start_time - 30 دقيقة) وبين (exam_start_time + 60 دقيقة)
                        valid_start = exam_datetime - timedelta(minutes=30)
                        valid_end = exam_datetime + timedelta(minutes=60)

                        # فحص صلاحية الوقت: كما يجب التأكد من أن تاريخ الاختبار يطابق تاريخ اليوم
                        is_date_match = (exam_datetime.date() == current_datetime.date())
                        is_time_valid = valid_start <= current_datetime <= valid_end
                        # إضافة بيانات الاختبار إلى الطالب
                        student_info["exam_distribution"] = exam_distribution_data
                        student_info["exam_data"] = exam_data
                        student_info["isExamTimeValid"] = is_date_match and is_time_valid
                        student_info["time_window"] = {
                            "valid_start": valid_start.strftime("%Y-%m-%d %H:%M:%S"),
                            "valid_end": valid_end.strftime("%Y-%m-%d %H:%M:%S"),
                            "current_time": current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    else:
                        student_info["exam_error"] = "No exam data found."
                else:
                    student_info["exam_distribution_error"] = "No exam distribution data found."

                # Add new fields to the student data
                student_info["created_at"] = result["created_at"]
                student_info["similarity"] = result["similarity"]

        return jsonify({"results": students_dicts}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vectors_routes.route("/vectors/search-by-college", methods=["POST"])
def search_vectors_by_college():
    """
    Search for similar vectors using an image and college.
    ---
    tags:
      - Vectors
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: The face image to search for.
      - name: college
        in: formData
        type: string
        required: true
        description: The college to restrict the search within.
      - name: threshold
        in: formData
        type: number
        required: true
        description: The threshold for similarity.
      - name: limit
        in: formData
        type: integer
        required: true
        description: The number of desired results.
    responses:
      200:
        description: Search results.
      400:
        description: Input error.
      500:
        description: Server error.
    """
    try:
        # Check if the image file is in the request
        if "image" not in request.files:
            return jsonify({"error": "Image file is required."}), 400

        image_file = request.files["image"]
        college = request.form.get("college")
        threshold = request.form.get("threshold", type=float)
        limit = request.form.get("limit", type=int)

        if not college or threshold is None or limit is None:
            return jsonify({"error": "College, threshold, and limit are required."}), 400

        # Save the image temporarily
        filename = ImageProcessor.secure_filename(image_file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(temp_path)

        # Convert the image to a vector
        query_vector = ImageProcessor.convert_image_to_vector(temp_path)

        # Search for similar vectors within the specified college
        results = service.search_vectors_by_college(query_vector, college, threshold, limit)

        # Delete the temporary image
        os.remove(temp_path)

        # Extract student IDs from the results
        student_ids = [result["student_id"] for result in results]

        # Fetch student data using the fetch_students_info_by_ids function
        students_data = fetch_students_by_ids(student_ids)

        # Convert students_data to a list of dictionaries
        students_dicts = []
        for student in students_data:
            students_dicts.append({
                #"StudentID": student[0],  # ID
                "Number": student[1],  # Registration number
                "StudentName": student[2],  # Student name
                "Gender": student[3],  # Gender
                "Level": student[4],  # Level
                "Specialization": student[5],  # Specialization
                "College": student[6],  # College
                "ImagePath": student[7]  # Image path
            })

        # Update student data by adding new fields
        for result in results:
            student_id = result["student_id"]
            # Find the student data in students_dicts
            student_info = next((student for student in students_dicts if str(student["Number"]) == student_id), None)
            if student_info:
                # Add new fields to the student data
                student_info["created_at"] = result["created_at"]
                student_info["similarity"] = result["similarity"]

        return jsonify({"results": students_dicts}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# دالة لجلب بيانات توزيع الاختبار (مثال)
def get_exam_distribution_by_student(student_id: str) -> dict:
    query = sql.SQL("""
        SELECT id, student_id, student_name, exam_id, device_id, assigned_at
        FROM exam_distribution
        WHERE student_id = %s
        LIMIT 1
    """)
    try:
        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, (student_id,))
                row = cursor.fetchone()
                if row:
                    return row  # row يكون من نوع dict بالفعل
    except Exception as ex:
        print(f"Error fetching exam distribution: {ex}")
    return {}

# دالة لجلب بيانات الاختبار من جدول الاختبارات باستخدام exam_id
def get_exam_data(exam_id: int) -> dict:
    query = """
        SELECT exam_date, exam_start_time, exam_end_time, college_id, course_id,
               level_id, major_id, semester_id, year_id
        FROM Exams
        WHERE exam_id = %s
        LIMIT 1
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (exam_id,))
                # بما أن نتيجة الاستعلام بالفعل عبارة عن dict (كما يظهر في print(row))
                row = cursor.fetchone()
                if row:
                    # استخدام المفاتيح مباشرةً بدلاً من الفهارس
                    exam_date = row.get("exam_date")
                    exam_start_time = row.get("exam_start_time")
                    exam_end_time = row.get("exam_end_time")
                    
                    exam_date_str = exam_date.strftime("%Y-%m-%d") if hasattr(exam_date, "strftime") else exam_date
                    exam_start_time_str = exam_start_time.strftime("%H:%M:%S") if hasattr(exam_start_time, "strftime") else exam_start_time
                    exam_end_time_str = exam_end_time.strftime("%H:%M:%S") if hasattr(exam_end_time, "strftime") else exam_end_time

                    return {
                        "exam_date": exam_date_str,
                        "exam_start_time": exam_start_time_str,
                        "exam_end_time": exam_end_time_str,
                        "college_id": row.get("college_id"),
                        "course_id": row.get("course_id"),
                        "level_id": row.get("level_id"),
                        "major_id": row.get("major_id"),
                        "semester_id": row.get("semester_id"),
                        "year_id": row.get("year_id")
                    }
    except Exception as ex:
        print(f"Error fetching exam data: {ex}")
    return {}