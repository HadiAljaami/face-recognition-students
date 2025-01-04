import os
import logging

def setup_logging():
    """
    Set up logging configuration for student errors only.
    """
    # إنشاء مجلد logs إذا لم يكن موجودًا
    log_directory = os.path.join("logs")
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # مسار ملف log
    log_file_path = os.path.join(log_directory, "students_to_vectors.log")

    # إنشاء logger مخصص
    logger = logging.getLogger('student_errors')
    logger.setLevel(logging.ERROR)  # تسجيل الأخطاء فقط

    # إعداد formatter لتنسيق السجلات
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # إعداد handler لملف log
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(formatter)

    # إضافة handler إلى ال logger
    logger.addHandler(file_handler)

    # منع ظهور السجلات في شاشة الكنسل
    logger.propagate = False

    return logger