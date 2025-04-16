import os
import logging
from services.image_processor import ImageProcessor
from services.students_service import fetch_students_by_ids
from services.vectors_service import VectorsService
from database.vectors_repository import VectorsRepository
from services.logging_config import setup_logging

# إعداد logger
logger = setup_logging()

class StudentsToVectorsService:
    IMAGE_DIRECTORY = os.path.join("database", "student_images")

    @staticmethod
    def get_image_path(image_name):
        """Get the full path of the image based on its name."""
        return os.path.join(StudentsToVectorsService.IMAGE_DIRECTORY, image_name)

    @staticmethod
    def log_error(error_message, student_id=None, batch_ids=None):
        """Log errors with optional student or batch details."""
        if student_id:
            logger.error(f"Error processing student ID {student_id}: {error_message}")
        elif batch_ids:
            logger.error(f"Error processing batch {batch_ids}: {error_message}")
        else:
            logger.error(f"Error: {error_message}")

    @staticmethod
    def save_vector(student_id, college, vector):
        """Save the student vector to the database using VectorsService."""
        try:
            repository = VectorsRepository()
            service = VectorsService(repository)
            vector_id = service.add_vector(student_id, college, vector)
            return vector_id
        except Exception as e:
            raise

    @staticmethod
    def process_students_to_vectors(student_ids, batch_size=200):
        """Process students in batches to convert their images to vectors and save them."""
        success_count = 0
        failure_count = 0
        failure_details = []
        for i in range(0, len(student_ids), batch_size):
            batch_ids = student_ids[i:i + batch_size]
            try:
                students_data = fetch_students_by_ids(batch_ids)


                for student in students_data:
                    try:
                        student_id, college, image_name = student[1], student[2], student[7]
                        image_path = StudentsToVectorsService.get_image_path(image_name)
                        # Convert image to vector
                        vector = ImageProcessor.convert_image_to_vector(image_path)
                        # Save vector to the database
                        StudentsToVectorsService.save_vector(student_id, college, vector)
                        success_count += 1
                    except Exception as e:
                        failure_count += 1
                        failure_details.append({"student_id": student_id, "error": str(e)})
                        # تسجيل الخطأ في ملف log
                        StudentsToVectorsService.log_error(str(e), student_id=student_id)
            except Exception as e:
                failure_count += len(batch_ids)
                failure_details.append({"batch_ids": batch_ids, "error": str(e)})
                # تسجيل الخطأ في ملف log
                StudentsToVectorsService.log_error(str(e), batch_ids=batch_ids)

        # إنشاء رسالة واحدة بناءً على النتائج
        if success_count > 0 and failure_count == 0:
            message = f"All students processed successfully. Total: {success_count}."
        elif failure_count > 0 and success_count == 0:
            message = f"All students failed to process. Total: {failure_count}."
        else:
            message = f"Some students processed successfully. Success: {success_count}, Failures: {failure_count}."

        # إرجاع النتيجة في شكل واحد
        return {
            "message": message,
            "success_count": success_count,
            "failure_count": failure_count,
            "failure_details": failure_details if failure_count > 0 else None
        }