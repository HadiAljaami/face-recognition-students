from typing import List, Dict, Optional
from datetime import date, time
from database.academic.exams_repository import ExamsRepository
import time as time_module

class ExamsService:
    def __init__(self):
        self.repo = ExamsRepository()

    def create_exam(self, course_id: int, major_id: int, college_id: int,
                   level_id: int, year_id: int, semester_id: int,
                   exam_date: date = None, exam_time: time = None) -> Dict:
        """Validate and create exam"""
        # Validate IDs
        for field, value in [
            ('course_id', course_id),
            ('major_id', major_id),
            ('college_id', college_id),
            ('level_id', level_id),
            ('year_id', year_id),
            ('semester_id', semester_id)
        ]:
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"Invalid {field} format")
        
        # Validate date/time if provided
        if exam_date and not isinstance(exam_date, date):
            raise ValueError("Invalid exam date format")
        if exam_time and not isinstance(exam_time, time):
            raise ValueError("Invalid exam time format")
        
        return self.repo.create_exam(
            course_id, major_id, college_id, level_id,
            year_id, semester_id, exam_date, exam_time
        )

    def get_all_exams(self) -> List[Dict]:
        """Get all exams"""
        return self.repo.get_all_exams()

    def get_exam_by_id(self, exam_id: int) -> Optional[Dict]:
        """Get exam by ID with validation"""
        if not isinstance(exam_id, int) or exam_id <= 0:
            raise ValueError("Invalid exam ID")
        
        result = self.repo.get_exam_by_id(exam_id)
        if not result:
            raise ValueError("Exam not found")
        return result

    def filter_exams(self, major_id: int = None, college_id: int = None,
                    level_id: int = None, year_id: int = None,
                    semester_id: int = None) -> List[Dict]:
        """Filter exams with validation"""
        filters = {
            'major_id': major_id,
            'college_id': college_id,
            'level_id': level_id,
            'year_id': year_id,
            'semester_id': semester_id
        }
        
        # التعديل هنا: تحقق من أن القيمة إما None أو integer موجب
        for field, value in filters.items():
            if value is not None:
                if not isinstance(value, int) or value <= 0:
                    raise ValueError(f"Invalid {field} format. Must be positive integer or null")
        
        return self.repo.filter_exams(major_id, college_id, level_id, year_id, semester_id)
        # Add these methods to the existing ExamsService class

    def delete_exams(self, exam_ids: List[int]) -> Dict:
        """Delete multiple exams with validation"""
        if not exam_ids:
            raise ValueError("No exam IDs provided")
        
        if not all(isinstance(id, int) and id > 0 for id in exam_ids):
            raise ValueError("All exam IDs must be positive integers")
        
        deleted_count = self.repo.delete_exams(exam_ids)
        if deleted_count == 0:
            raise ValueError("No exams found with the provided IDs")
        
        return {
            "message": f"Successfully deleted {deleted_count} exam(s)",
            "deleted_count": deleted_count
        }
    
    def update_exam(self, exam_id: int, course_id: int, major_id: int, college_id: int,
                   level_id: int, year_id: int, semester_id: int,
                   exam_date: date = None, exam_time: time = None) -> Dict:
        """Validate and update exam with connection retry"""
        max_retries = 3
        retry_delay = 1  # ثانية بين المحاولات
        
        for attempt in range(max_retries):
            try:
                # التحقق من الصحة
                self._validate_exam_data(
                    exam_id, course_id, major_id, college_id,
                    level_id, year_id, semester_id,
                    exam_date, exam_time
                )
                
                result = self.repo.update_exam(
                    exam_id, course_id, major_id, college_id,
                    level_id, year_id, semester_id,
                    exam_date, exam_time
                )
                
                if not result:
                    raise ValueError("Exam not found")
                
                return result
                
            except RuntimeError as e:
                if "connection" in str(e).lower() and attempt < max_retries - 1:
                    time_module.sleep(retry_delay)
                    continue
                raise RuntimeError(f"Failed after {max_retries} attempts: {str(e)}")
            except ValueError as e:
                raise ValueError(str(e))
            except Exception as e:
                raise RuntimeError(f"Unexpected error: {str(e)}")

    def _validate_exam_data(self, exam_id: int, *args):
        """تحقق من صحة جميع المدخلات"""
        ids = {
            'exam_id': exam_id,
            'course_id': args[0],
            'major_id': args[1],
            'college_id': args[2],
            'level_id': args[3],
            'year_id': args[4],
            'semester_id': args[5]
        }
        
        for field, value in ids.items():
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{field} must be positive integer")

        if args[6] and not isinstance(args[6], date):
            raise ValueError("exam_date must be date object")
            
        if args[7] and not isinstance(args[7], time):
            raise ValueError("exam_time must be time object")