from flask import Blueprint, request, jsonify
from services.vectors_service import VectorsService
from services.image_processor import ImageProcessor
from services.students_service import fetch_student_info_by_number
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
    البحث عن متجهات مشابهة باستخدام صورة
    ---
    tags:
      - Vectors
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: صورة الوجه للبحث
      - name: threshold
        in: formData
        type: number
        required: true
        description: العتبة لتحديد التشابه
      - name: limit
        in: formData
        type: integer
        required: true
        description: عدد النواتج المطلوبة
    responses:
      200:
        description: نتائج البحث
      400:
        description: خطأ في الإدخال
      500:
        description: خطأ في السيرفر
    """
    try:
        # استلام البيانات من الطلب
        if "image" not in request.files:
            return jsonify({"error": "Image file is required."}), 400

        image_file = request.files["image"]
        threshold = request.form.get("threshold", type=float)
        limit = request.form.get("limit", type=int)

        if threshold is None or limit is None:
            return jsonify({"error": "Threshold and limit are required."}), 400

        # حفظ الصورة مؤقتًا
        filename = ImageProcessor.secure_filename(image_file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(temp_path)

        # تحويل الصورة إلى متجه
        query_vector = ImageProcessor.convert_image_to_vector(temp_path)

        # البحث عن المتجهات المشابهة
        results = service.find_similar_vectors(query_vector, threshold, limit)

        # حذف الصورة المؤقتة
        os.remove(temp_path)

        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vectors_routes.route("/vectors/search-by-college", methods=["POST"])
def search_vectors_by_college():
    """
    البحث عن متجهات مشابهة باستخدام صورة والكلية
    ---
    tags:
      - Vectors
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: صورة الوجه للبحث
      - name: college
        in: formData
        type: string
        required: true
        description: الكلية للبحث داخلها
      - name: threshold
        in: formData
        type: number
        required: true
        description: العتبة لتحديد التشابه
      - name: limit
        in: formData
        type: integer
        required: true
        description: عدد النواتج المطلوبة
    responses:
      200:
        description: نتائج البحث
      400:
        description: خطأ في الإدخال
      500:
        description: خطأ في السيرفر
    """
    try:
        # استلام البيانات من الطلب
        if "image" not in request.files:
            return jsonify({"error": "Image file is required."}), 400

        image_file = request.files["image"]
        college = request.form.get("college")
        threshold = request.form.get("threshold", type=float)
        limit = request.form.get("limit", type=int)

        if not college or threshold is None or limit is None:
            return jsonify({"error": "College, threshold, and limit are required."}), 400

        # حفظ الصورة مؤقتًا
        filename = ImageProcessor.secure_filename(image_file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(temp_path)

        # تحويل الصورة إلى متجه
        query_vector = ImageProcessor.convert_image_to_vector(temp_path)

        # البحث عن المتجهات المشابهة داخل الكلية
        results = service.search_vectors_by_college(query_vector, college, threshold, limit)

        # حذف الصورة المؤقتة
        os.remove(temp_path)

        return jsonify({"results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#================================================

# @vectors_routes.route("/vectors/add-vector", methods=["POST"])
# def add_vector():
#     """
#     Add a vector to the database using student ID and image.
#     ---
#     tags:
#       - Vectors
#     parameters:
#       - name: student_id
#         in: formData
#         type: string
#         required: true
#         description: The student's ID.
#       - name: image
#         in: formData
#         type: file
#         required: true
#         description: The image file to upload (JPG, JPEG, PNG only).
#     responses:
#       201:
#         description: Vector added successfully.
#       400:
#         description: Bad Request. Validation failed.
#       500:
#         description: Internal Server Error.
#     """
#     try:
#         # التحقق من وجود الملف
#         if "image" not in request.files:
#             return jsonify({"error": "No file uploaded."}), 400

#         file = request.files["image"]
#         student_id = request.form.get("student_id")

#         if not student_id:
#             return jsonify({"error": "Student ID is required."}), 400

#         # حفظ الملف مؤقتًا
#         filename = ImageProcessor.secure_filename(file.filename)
#         filepath = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(filepath)

#         # تحويل الصورة إلى متجه
#         vector = ImageProcessor.convert_image_to_vector(filepath)

#         # إزالة الملف المؤقت
#         os.remove(filepath)

#         # إضافة المتجه إلى قاعدة البيانات
#         vector_id = service.add_vector(student_id, vector)
#         return jsonify({"message": "Vector added successfully.", "id": vector_id}), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @vectors_routes.route("/vectors/update-vector/<int:vector_id>", methods=["PUT"])
# def update_vector(vector_id):
#     """
#     Update a vector in the database using vector ID and image.
#     ---
#     tags:
#       - Vectors
#     parameters:
#       - name: vector_id
#         in: path
#         type: integer
#         required: true
#         description: The ID of the vector to update.
#       - name: image
#         in: formData
#         type: file
#         required: true
#         description: The image file to upload (JPG, JPEG, PNG only).
#     responses:
#       200:
#         description: Vector updated successfully.
#       400:
#         description: Bad Request. Validation failed.
#       500:
#         description: Internal Server Error.
#     """
#     try:
#         # التحقق من وجود الملف
#         if "image" not in request.files:
#             return jsonify({"error": "No file uploaded."}), 400

#         file = request.files["image"]

#         # حفظ الملف مؤقتًا
#         filename = ImageProcessor.secure_filename(file.filename)
#         filepath = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(filepath)

#         # تحويل الصورة إلى متجه
#         vector = ImageProcessor.convert_image_to_vector(filepath)

#         # إزالة الملف المؤقت
#         os.remove(filepath)

#         # تحديث المتجه في قاعدة البيانات
#         success = service.update_vector(vector_id, vector)
#         if success:
#             return jsonify({"message": "Vector updated successfully."}), 200
#         else:
#             return jsonify({"error": "Failed to update vector. Check vector ID."}), 400

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# from flask import Blueprint, request, jsonify 
# from services.vectors_service import VectorsService
# from database.vectors_repository import VectorsRepository

# #======================================================
# #new code
# from werkzeug.utils import secure_filename
# from PIL import Image
# import os
# import face_recognition
# from flasgger import Swagger, swag_from
# #======================================================
# #base codes
# vectors_routes = Blueprint("vectors_routes", __name__)

# repository = VectorsRepository()
# service = VectorsService(repository)

# #======================================================
# #new code

# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# MAX_FILE_SIZE_MB = 5
# UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # مجلد مؤقت داخل المشروع

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @vectors_routes.route("/upload-image", methods=["POST"])
# @swag_from({
#     "tags": ["Image Processing"],
#     "summary": "Upload an image and process it",
#     "description": "Upload an image, check if it contains one face, and store its vector in the database.",
#     "consumes": ["multipart/form-data"],
#     "parameters": [
#         {
#             "name": "image",
#             "in": "formData",
#             "type": "file",
#             "required": True,
#             "description": "The image file to upload (JPG, JPEG, PNG only)."
#         },
#         {
#             "name": "student_id",
#             "in": "formData",
#             "type": "string",
#             "required": True,
#             "description": "The student's ID."
#         },
#         {
#             "name": "college",
#             "in": "formData",
#             "type": "string",
#             "required": True,
#             "description": "The student's college."
#         }
#     ],
#     "responses": {
#         201: {
#             "description": "Image processed and vector stored successfully."
#         },
#         400: {
#             "description": "Bad Request. Validation failed."
#         },
#         500: {
#             "description": "Internal Server Error."
#         }
#     }
# })#@vectors_routes.route("/upload-image", methods=["POST"])

# def upload_image():
#     try:
#         # التحقق من وجود الملف
#         if "image" not in request.files:
#             return jsonify({"error": "No file uploaded."}), 400

#         file = request.files["image"]

#         # التحقق من الامتداد
#         if not allowed_file(file.filename):
#             return jsonify({"error": "Invalid file extension. Allowed: png, jpg, jpeg."}), 400

#         #=============================
#         # إنشاء مجلد للرفع إذا لم يكن موجودًا
#         if not os.path.exists(UPLOAD_FOLDER):
#             os.makedirs(UPLOAD_FOLDER)

#         # حفظ الملف مؤقتًا
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(filepath)


#         # التحقق من حجم الصورة
#         if os.path.getsize(filepath) > MAX_FILE_SIZE_MB * 1024 * 1024:
#             os.remove(filepath)
#             return jsonify({"error": f"File size exceeds {MAX_FILE_SIZE_MB} MB."}), 400

#         # تحميل الصورة والتحقق من وجود وجه
#         image = face_recognition.load_image_file(filepath)
#         face_locations = face_recognition.face_locations(image)

#         if len(face_locations) != 1:
#             os.remove(filepath)
#             return jsonify({"error": "Image must contain exactly one face."}), 400

#         # استخراج المتجه
#         face_encodings = face_recognition.face_encodings(image)
#         if not face_encodings:
#             os.remove(filepath)
#             return jsonify({"error": "Unable to extract face vector."}), 400

#         vector = face_encodings[0].tolist()

#         # إزالة الملف المؤقت
#         #os.remove(filepath)

#         # البيانات الإضافية
#         data = request.form
#         student_id = data.get("student_id")
#         college = data.get("college")

#         if not student_id or not college:
#             return jsonify({"error": "Student ID and college are required."}), 400

#         # تخزين المتجه في قاعدة البيانات
#         vector_id = service.add_vector(student_id, college, vector)
#         return jsonify({"message": "Image processed and vector stored successfully.", "id": vector_id}), 201

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @vectors_routes.route("/vectors/update-image", methods=["PUT"])
# def update_vector_image():
#     """
#     تحديث متجه بناءً على صورة
#     ---
#     tags:
#       - vectors
#     parameters:
#       - name: image
#         in: formData
#         type: file
#         required: true
#         description: صورة الوجه لتحديث المتجه
#       - name: student_id
#         in: formData
#         type: string
#         required: true
#         description: معرف الطالب
#       - name: college
#         in: formData
#         type: string
#         required: true
#         description: الكلية التي ينتمي إليها الطالب
#     responses:
#       200:
#         description: تم تحديث المتجه بنجاح
#       400:
#         description: خطأ في الإدخال
#       500:
#         description: خطأ في السيرفر
#     """
#     try:
#         # التحقق من وجود الملف
#         if "image" not in request.files:
#             return jsonify({"error": "No file uploaded."}), 400

        
#         student_id = request.form.get("student_id")
#         college = request.form.get("college")

#         if not student_id or not college:
#             return jsonify({"error": "student_id and college are required."}), 400

#         file = request.files["image"]

#         # التحقق من الامتداد
#         if not allowed_file(file.filename):
#             return jsonify({"error": "Invalid file extension. Allowed: png, jpg, jpeg."}), 400

#         #=============================
#         # إنشاء مجلد للرفع إذا لم يكن موجودًا
#         if not os.path.exists(UPLOAD_FOLDER):
#             os.makedirs(UPLOAD_FOLDER)

#         # حفظ الملف مؤقتًا
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(filepath)


#         # التحقق من حجم الصورة
#         if os.path.getsize(filepath) > MAX_FILE_SIZE_MB * 1024 * 1024:
#             os.remove(filepath)
#             return jsonify({"error": f"File size exceeds {MAX_FILE_SIZE_MB} MB."}), 400

#         # تحميل الصورة والتحقق من وجود وجه
#         image = face_recognition.load_image_file(filepath)
#         face_locations = face_recognition.face_locations(image)

#         if len(face_locations) != 1:
#             os.remove(filepath)
#             return jsonify({"error": "Image must contain exactly one face."}), 400

#         # استخراج المتجه
#         face_encodings = face_recognition.face_encodings(image)
#         if not face_encodings:
#             os.remove(filepath)
#             return jsonify({"error": "Unable to extract face vector."}), 400

#         vector = face_encodings[0].tolist()

#         # إزالة الملف المؤقت
#         os.remove(filepath)

#       # تحديث البيانات
#         success = service.update_vector(student_id, college, vector)
#         if success:
#             return jsonify({"message": "Vector updated successfully."}), 200
#         else:
#             return jsonify({"error": "Failed to update vector. Check student_id and college."}), 400

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#======================================================
# @vectors_routes.route("/vectors", methods=["POST"])
# def add_vector():
#     """إضافة متجه جديد
#     ---
#     tags:
#       - vectors

#     parameters:
#       - name: body
#         in: body
#         required: true
#         schema:
#           type: object
#           properties:
#             student_id:
#               type: string
#               example: "S12345"
#             college:
#               type: string
#               example: "Engineering"
#             vector:
#               type: array
#               items:
#                 type: number
#               example: [0.1, 0.2, 0.3, ..., 0.128]
#     responses:
#       201:
#         description: تم إضافة المتجه بنجاح
#       400:
#         description: خطأ في الإدخال
#       500:
#         description: خطأ في السيرفر
#     """
#     data = request.get_json()
#     student_id = data.get("student_id")
#     college = data.get("college")
#     vector = data.get("vector")

#     if not student_id or not college or not vector:
#         return jsonify({"error": "All fields (student_id, college, vector) are required."}), 400

#     try:
#         vector_id = service.add_vector(student_id, college, vector)
#         return jsonify({"message": "Vector added successfully.", "id": vector_id}), 201
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
#         filename = secure_filename(image_file.filename)
#         temp_path = os.path.join("tmp", filename)
#         image_file.save(temp_path)

#         # تحميل الصورة والتحقق من وجود وجه واحد
#         image = face_recognition.load_image_file(temp_path)
#         face_encodings = face_recognition.face_encodings(image)

#         if len(face_encodings) != 1:
#             os.remove(temp_path)
#             return jsonify({"error": "The image must contain exactly one face."}), 400

#         # استخراج المتجه
#         query_vector = face_encodings[0].tolist()

#         # البحث عن المتجهات المشابهة
#         results = service.find_similar_vectors(query_vector, threshold, limit)

#         # حذف الصورة المؤقتة
#         #os.remove(temp_path)

#         return jsonify({"results": results}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



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
#         filename = secure_filename(image_file.filename)
#         temp_path = os.path.join("tmp", filename)
#         image_file.save(temp_path)

#         # تحميل الصورة والتحقق من وجود وجه واحد
#         image = face_recognition.load_image_file(temp_path)
#         face_encodings = face_recognition.face_encodings(image)

#         if len(face_encodings) != 1:
#             os.remove(temp_path)
#             return jsonify({"error": "The image must contain exactly one face."}), 400

#         # استخراج المتجه
#         query_vector = face_encodings[0].tolist()

#         # البحث عن المتجهات المشابهة داخل الكلية
#         results = service.search_vectors_by_college(query_vector, college, threshold, limit)

#         # حذف الصورة المؤقتة
#         #os.remove(temp_path)

#         return jsonify({"results": results}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500





# @vectors_routes.route("/vectors/search", methods=["POST"])
# def search_vectors():
#     """البحث عن المتجهات المشابهة
#     ---
#     tags:
#       - vectors
#     parameters:
#       - name: body
#         in: body
#         required: true
#         schema:
#           type: object
#           properties:
#             vector:
#               type: array
#               items:
#                 type: number
#               example: [0.1, 0.2, 0.3, ..., 0.128]
#             threshold:
#               type: number
#               example: 0.8
#             limit:
#               type: integer
#               example: 10
#     responses:
#       200:
#         description: نتائج البحث عن المتجهات
#       400:
#         description: خطأ في الإدخال
#       500:
#         description: خطأ في السيرفر
#     """
#     data = request.get_json()
#     vector = data.get("vector")
#     threshold = data.get("threshold", 0.8)
#     limit = data.get("limit", 1)

#     if not vector:
#         return jsonify({"error": "Vector is required for searching."}), 400

#     if not isinstance(vector, list) or len(vector) != 128:
#         return jsonify({"error": "Vector must be a list with 128 dimensions."}), 400

#     try:
#         results = service.find_similar_vectors(vector, threshold, limit)
#         return jsonify(results), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @vectors_routes.route("/vectors/search/college", methods=["POST"])
# def search_vectors_in_college():
#     """البحث عن المتجهات المشابهة ضمن كلية معينة
#     ---
#     tags:
#       - vectors
#     parameters:
#       - name: body
#         in: body
#         required: true
#         schema:
#           type: object
#           properties:
#             vector:
#               type: array
#               items:
#                 type: number
#               example: [0.1, 0.2, 0.3, ..., 0.128]
#             college:
#               type: string
#               example: "Engineering"
#             threshold:
#               type: number
#               example: 0.8
#             limit:
#               type: integer
#               example: 10
#     responses:
#       200:
#         description: نتائج البحث ضمن الكلية
#       400:
#         description: خطأ في الإدخال
#       500:
#         description: خطأ في السيرفر
#     """
#     data = request.get_json()
#     vector = data.get("vector")
#     college = data.get("college")
#     threshold = data.get("threshold", 0.8)
#     limit = data.get("limit", 1)

#     if not vector or not college:
#         return jsonify({"error": "Vector and college are required for searching."}), 400

#     try:
#         results = service.find_similar_vectors_by_college(vector, college, threshold, limit)
#         return jsonify(results), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
