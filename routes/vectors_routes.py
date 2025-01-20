from flask import Blueprint, request, jsonify
from services.vectors_service import VectorsService
from services.image_processor import ImageProcessor
from services.students_service import fetch_student_info_by_number,fetch_students_by_ids
from database.vectors_repository import VectorsRepository
import os

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


# @vectors_routes.route("/vectors/search-by-college", methods=["POST"])
# def search_vectors_by_college():
#     """
#     البحث عن متجهات مشابهة باستخدام صورة والكلية
#     ---
#     tags:
#       - Vectors
#     parameters:
#       - name: image
#         in: formData
#         type: file
#         required: true
#         description: صورة الوجه للبحث
#       - name: college
#         in: formData
#         type: string
#         required: true
#         description: الكلية للبحث داخلها
#       - name: threshold
#         in: formData
#         type: number
#         required: true
#         description: العتبة لتحديد التشابه
#       - name: limit
#         in: formData
#         type: integer
#         required: true
#         description: عدد النواتج المطلوبة
#     responses:
#       200:
#         description: نتائج البحث
#       400:
#         description: خطأ في الإدخال
#       500:
#         description: خطأ في السيرفر
#     """
#     try:
#         # استلام البيانات من الطلب
#         if "image" not in request.files:
#             return jsonify({"error": "Image file is required."}), 400

#         image_file = request.files["image"]
#         college = request.form.get("college")
#         threshold = request.form.get("threshold", type=float)
#         limit = request.form.get("limit", type=int)

#         if not college or threshold is None or limit is None:
#             return jsonify({"error": "College, threshold, and limit are required."}), 400

#         # حفظ الصورة مؤقتًا
#         filename = ImageProcessor.secure_filename(image_file.filename)
#         temp_path = os.path.join(UPLOAD_FOLDER, filename)
#         image_file.save(temp_path)

#         # تحويل الصورة إلى متجه
#         query_vector = ImageProcessor.convert_image_to_vector(temp_path)

#         # البحث عن المتجهات المشابهة داخل الكلية
#         results = service.search_vectors_by_college(query_vector, college, threshold, limit)

#         # حذف الصورة المؤقتة
#         os.remove(temp_path)

#         return jsonify({"results": results}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @vectors_routes.route("/vectors/search", methods=["POST"])
# def search_vectors():
#     """
#     البحث عن متجهات مشابهة باستخدام صورة
#     ---
#     tags:
#       - Vectors
#     parameters:
#       - name: image
#         in: formData
#         type: file
#         required: true
#         description: صورة الوجه للبحث
#       - name: threshold
#         in: formData
#         type: number
#         required: true
#         description: العتبة لتحديد التشابه
#       - name: limit
#         in: formData
#         type: integer
#         required: true
#         description: عدد النواتج المطلوبة
#     responses:
#       200:
#         description: نتائج البحث
#       400:
#         description: خطأ في الإدخال
#       500:
#         description: خطأ في السيرفر
#     """
#     try:
#         # استلام البيانات من الطلب
#         if "image" not in request.files:
#             return jsonify({"error": "Image file is required."}), 400

#         image_file = request.files["image"]
#         threshold = request.form.get("threshold", type=float)
#         limit = request.form.get("limit", type=int)

#         if threshold is None or limit is None:
#             return jsonify({"error": "Threshold and limit are required."}), 400

#         # حفظ الصورة مؤقتًا
#         filename = ImageProcessor.secure_filename(image_file.filename)
#         temp_path = os.path.join(UPLOAD_FOLDER, filename)
#         image_file.save(temp_path)

#         # تحويل الصورة إلى متجه
#         query_vector = ImageProcessor.convert_image_to_vector(temp_path)
        
#         # print("hello")
#         # البحث عن المتجهات المشابهة
#         results = service.find_similar_vectors(query_vector, threshold, limit)

#         # حذف الصورة المؤقتة
#         # print("hello")
#         os.remove(temp_path)

#         return jsonify({"results": results}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
