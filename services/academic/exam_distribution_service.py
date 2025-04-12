from typing import List, Dict, Optional
from database.academic.exam_distribution_repository import ExamDistributionRepository


class ExamDistributionService:
    def __init__(self):
        self.repository = ExamDistributionRepository()

    def assign_exam_to_student(self, student_id: str, student_name: str, exam_id: int, device_id: int = None):
        
        return self.repository.assign_exam_to_student(
            student_id=student_id,
            student_name=student_name,
            exam_id=exam_id,
            device_id=device_id
        )

    def update_exam_distribution(self, distribution_id: int, student_name: str = None, 
                               exam_id: int = None, device_id: int = None):
        return self.repository.update_exam_distribution(
            distribution_id=distribution_id,
            student_name=student_name,
            exam_id=exam_id,
            device_id=device_id
        )

    def delete_multiple_distributions(self, distribution_ids: List[int]):
        return self.repository.delete_multiple_distributions(distribution_ids)

    def get_exam_distribution_report(self, exam_id: int) -> Dict:
            """
            Get exam distribution report with validation
            Args:
                exam_id: Exam ID to get distribution for
            Returns:
                Dictionary with 'header' and 'students' keys
            Raises:
                ValueError: If exam_id is invalid or exam not found
                RuntimeError: For database errors
            """
            try:
                # التحقق من صحة exam_id
                if not exam_id or not isinstance(exam_id, int):
                    raise ValueError("Invalid exam ID. Must be a positive integer")
                
                if exam_id <= 0:
                    raise ValueError("Exam ID must be a positive number")

                return self.repository.get_exam_distribution_report(exam_id)
                
            except ValueError as e:
                raise  # نعيد نفس الخطأ للطبقة الأعلى
            except Exception as e:
                raise RuntimeError(f"Service error: {str(e)}")



    def get_student_info(self, student_id: str) -> Dict:
        """
        Get student information by ID
        
        Args:
            student_id: University registration number
            
        Returns:
            Dictionary containing student information
            
        Raises:
            ValueError: For invalid input or student not found
        """
        if not student_id or not isinstance(student_id, str):
            raise ValueError("Valid student ID must be provided")
            
        student_data = self.repository.get_student_by_id(student_id)
        
        if not student_data:
            raise ValueError("Student not found in the system")
            
        return student_data



    # def get_exam_distribution_report(self, exam_id: int) -> List[Dict]:
    #     """
    #     Get exam distribution grouped by rooms
    #     Args:
    #         exam_id: ID of the exam
    #     Returns:
    #         List of room groups with headers and students
    #     Raises:
    #         ValueError: If exam_id is invalid or no distribution found
    #         RuntimeError: For database errors
    #     """
    #     if not isinstance(exam_id, int) or exam_id <= 0:
    #         raise ValueError("Exam ID must be a positive integer")
        
    #     return self.repository.get_exam_distribution_report(exam_id)


    def get_distribution_by_id(self, distribution_id: int):
        return self.repository.get_distribution_by_id(distribution_id)


    def filter_distributions(self, student_id: str = None, exam_id: int = None, 
                           device_id: int = None, center_id: int = None,
                           date_from: str = None, date_to: str = None):
        return self.repository.filter_distributions(
            student_id=student_id,
            exam_id=exam_id,
            device_id=device_id,
            center_id=center_id,
            date_from=date_from,
            date_to=date_to
        )