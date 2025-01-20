# from database.students import Student

# def get_all_students():
#     """إرجاع قائمة بجميع الطلاب"""
#     db = Student()
#     return db.all()

# def search_student_by_name(name):
#     """البحث عن طالب بالاسم"""
#     db = Student()
#     return db.all(StudentName=name)
import os
import uuid
from werkzeug.utils import secure_filename
from database.students import Student



# إنشاء كائن قاعدة البيانات
student_db = Student()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB
IMAGE_FOLDER = 'database/student_images'


def is_allowed_file(filename):
    """تحقق من أن الملف يحمل امتدادًا مسموحًا به."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(image_file):
    """حفظ الصورة في المجلد المحدد باسم فريد."""
    filename = secure_filename(image_file.filename)
    extension = os.path.splitext(filename)[1][1:].lower()
    print(extension)
    # التحقق من الامتداد
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid image format. Only PNG, JPG, and JPEG are allowed.")

    # إنشاء اسم فريد للصورة
    unique_filename = f"{uuid.uuid4().hex}.{extension}"
    image_path = os.path.join(IMAGE_FOLDER, unique_filename)

    # حفظ الصورة
    os.makedirs(IMAGE_FOLDER, exist_ok=True)
    image_file.save(image_path)

    return unique_filename  # إرجاع اسم الصورة فقط


def add_student(data, image_file):
    """إضافة طالب إلى قاعدة البيانات مع معالجة الصورة."""
    # التحقق من وجود رقم القيد مسبقًا
    if student_db.exists(Number=data.get("Number")):
        return {"error": "Enrollment number already exists"}, 400

    # التحقق من الصورة وحفظها
    if image_file and is_allowed_file(image_file.filename):
        if image_file.content_length > MAX_IMAGE_SIZE:
            return {"error": "Image size exceeds 2MB"}, 400

        try:
            # حفظ الصورة والحصول على اسمها
            image_filename = save_image(image_file)

            # تحديث البيانات باسم الصورة فقط
            data['ImagePath'] = image_filename
            student_db.create(**data)
            return {"message": "Student added successfully"}, 201
        except ValueError as e:
            return {"error": str(e)}, 400
        except Exception as e:
            return {"error": f"Failed to save image. Details: {e}"}, 500
    else:
        return {"error": "Invalid image format. Only PNG, JPG, and JPEG are allowed."}, 400


def get_image_path(image_name):
    """إنشاء المسار الكامل للصورة ديناميكيًا."""
    return os.path.join(IMAGE_FOLDER, image_name)


def get_all_students():
    """استرجاع جميع الطلاب من قاعدة البيانات"""
    return student_db.all()

def add_student2(data):
    """إضافة طالب جديد إلى قاعدة البيانات"""
    student_db.create(**data)

def update_student(student_id, data):
    """تحديث بيانات طالب معين"""
    student_db.update(student_id, **data)

def delete_student(student_id):
    """حذف طالب معين"""
    student_db.delete(StudentID=student_id)

def search_student_by_number(number):
    """البحث عن طالب برقم القيد"""
    return student_db.find_by_number(number)

def search_students_by_name(name):
    """البحث عن الطلاب بالاسم"""
    return student_db.find_by_name(name)

def fetch_student_info_by_number(number):
    """
    Fetch student info (number, college, image) using the Student database model.
    """
    student_db = Student()
    return student_db.get_student_info_by_number(number)

def fetch_students_by_ids(student_ids):
    """
    Service function to fetch student data by IDs.
    Args:
        student_ids (list): List of student IDs.
    Returns:
        list: List of student data dictionaries.
    """
    try:
        # التحقق من أن القائمة غير فارغة
        if not student_ids or not isinstance(student_ids, list):
            raise ValueError("The input student IDs must be a non-empty list.")

        students_data = student_db.fetch_students_info_by_ids(student_ids)

        # التحقق من أن هناك بيانات مسترجعة
        if not students_data:
            raise ValueError(f"No students found for the given IDs: {student_ids}")

        return students_data

    except Exception as e:
        raise
    


