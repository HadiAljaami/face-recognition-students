from typing import List, Dict, Optional
from datetime import date, time  # Changed: removed datetime import
import time as time_module
from database.academic.exams_repository import ExamsRepository

class ExamsService:
    def __init__(self):
        self.repo = ExamsRepository()

    def create_exam(self, course_id: int, major_id: int, college_id: int,
                   level_id: int, year_id: int, semester_id: int,
                   exam_date: date = None,
                   exam_start_time: time = None,  # Changed to time
                   exam_end_time: time = None) -> Dict:  # Changed to time
        """
        Create a new exam with validation
        
        Args:
            course_id: ID of the course
            major_id: ID of the major
            college_id: ID of the college
            level_id: ID of the level
            year_id: ID of the academic year
            semester_id: ID of the semester
            exam_date: Date of the exam
            exam_start_time: Start time of the exam (now time object)
            exam_end_time: End time of the exam (now time object)
            
        Returns:
            Created exam details
            
        Raises:
            ValueError: If any validation fails
            RuntimeError: If database operation fails
        """
        # Validate IDs (unchanged)
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
        
        # Validate date/time (updated for time objects)
        if exam_date and not isinstance(exam_date, date):
            raise ValueError("Invalid exam date format")
        if exam_start_time and not isinstance(exam_start_time, time):  # Changed
            raise ValueError("Invalid exam start time format (expected time)")
        if exam_end_time and not isinstance(exam_end_time, time):  # Changed
            raise ValueError("Invalid exam end time format (expected time)")
        
        # Validate time window (still works with time objects)
        if exam_start_time and exam_end_time and exam_start_time >= exam_end_time:
            raise ValueError("Exam start time must be before end time")
        
        try:
            return self.repo.create_exam(
                course_id, major_id, college_id, level_id,
                year_id, semester_id, exam_date,
                exam_start_time, exam_end_time
            )
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise RuntimeError(f"Failed to create exam: {str(e)}")

    def update_exam(self, exam_id: int, 
                   course_id: int = None, 
                   major_id: int = None, 
                   college_id: int = None,
                   level_id: int = None, 
                   year_id: int = None, 
                   semester_id: int = None,
                   exam_date: date = None,
                   exam_start_time: time = None,  # Changed to time
                   exam_end_time: time = None) -> Dict:  # Changed to time
        """
        Update exam with validation and retry logic
        
        Args:
            exam_id: ID of exam to update
            Other parameters: Fields to update (None means don't update)
            
        Returns:
            Updated exam details
            
        Raises:
            ValueError: If validation fails or exam not found
            RuntimeError: If database operation fails after retries
        """
        max_retries = 3
        retry_delay = 1  # seconds between retries
        
        for attempt in range(max_retries):
            try:
                # Validate inputs
                self._validate_exam_data(
                    exam_id, course_id, major_id, college_id,
                    level_id, year_id, semester_id,
                    exam_date, exam_start_time, exam_end_time
                )
                
                result = self.repo.update_exam(
                    exam_id, course_id, major_id, college_id,
                    level_id, year_id, semester_id,
                    exam_date, exam_start_time, exam_end_time
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

    def _validate_exam_data(self, exam_id: int,
                            course_id: Optional[int],
                            major_id: Optional[int],
                            college_id: Optional[int],
                            level_id: Optional[int],
                            year_id: Optional[int],
                            semester_id: Optional[int],
                            exam_date: Optional[date],
                            exam_start_time: Optional[time],
                            exam_end_time: Optional[time]):
        """Validate all input data for exam operations"""

        # Validate exam_id
        if not isinstance(exam_id, int) or exam_id <= 0:
            raise ValueError("exam_id must be positive integer")

        # Validate optional IDs
        optional_ids = {
            'course_id': course_id,
            'major_id': major_id,
            'college_id': college_id,
            'level_id': level_id,
            'year_id': year_id,
            'semester_id': semester_id
        }
        for field, value in optional_ids.items():
            if value is not None and (not isinstance(value, int) or value <= 0):
                raise ValueError(f"{field} must be a positive integer or None")

        # Validate date
        if exam_date is not None and not isinstance(exam_date, date):
            raise ValueError("exam_date must be a date object")

        # Validate time fields
        if exam_start_time is not None and not isinstance(exam_start_time, time):
            raise ValueError("exam_start_time must be a time object")
        if exam_end_time is not None and not isinstance(exam_end_time, time):
            raise ValueError("exam_end_time must be a time object")

        if exam_start_time and exam_end_time and exam_start_time >= exam_end_time:
            raise ValueError("Exam start time must be before end time")

    # def _validate_exam_data(self, exam_id: int, *args):
    #     """Validate all input data for exam operations"""
    #     # Validate exam_id
    #     if not isinstance(exam_id, int) or exam_id <= 0:
    #         raise ValueError("exam_id must be positive integer")

    #     # Validate IDs (can be None or positive integers)
    #     id_fields = ['course_id', 'major_id', 'college_id', 
    #                 'level_id', 'year_id', 'semester_id']
    #     for i, field in enumerate(id_fields):
    #         if args[i] is not None and (not isinstance(args[i], int) or args[i] <= 0):
    #             raise ValueError(f"{field} must be positive integer or null")

    #     # Validate date/times (updated for time objects)
    #     if args[6] is not None and not isinstance(args[6], date):
    #         raise ValueError("exam_date must be date object or null")
            
    #     if args[7] is not None and not isinstance(args[7], time):  # Changed
    #         raise ValueError("exam_start_time must be time object or null")
            
    #     if args[8] is not None and not isinstance(args[8], time):  # Changed
    #         raise ValueError("exam_end_time must be time object or null")

    #     # Validate time window (still works with time objects)
    #     if args[7] and args[8] and args[7] >= args[8]:
    #         raise ValueError("Exam start time must be before end time")

    def filter_exams(self, 
                   major_id: int = None, 
                   college_id: int = None,
                   level_id: int = None, 
                   year_id: int = None,
                   semester_id: int = None,
                   exam_date: date = None,
                   start_time: time = None,  # Changed to time
                   end_time: time = None) -> List[Dict]:  # Changed to time
        """
        Filter exams with comprehensive filtering options
        
        Args:
            major_id: Filter by major ID
            college_id: Filter by college ID
            level_id: Filter by level ID
            year_id: Filter by academic year ID
            semester_id: Filter by semester ID
            exam_date: Filter by specific date
            start_time: Filter exams starting after this time
            end_time: Filter exams ending before this time
            
        Returns:
            List of filtered exams with related information
            
        Raises:
            ValueError: If any filter parameter is invalid
            RuntimeError: If database operation fails
        """
        # Validate all filter parameters (updated for time objects)
        filters = {
            'major_id': major_id,
            'college_id': college_id,
            'level_id': level_id,
            'year_id': year_id,
            'semester_id': semester_id,
            'exam_date': exam_date,
            'start_time': start_time,
            'end_time': end_time
        }
        
        for field, value in filters.items():
            if value is not None:
                if field in ['major_id', 'college_id', 'level_id', 'year_id', 'semester_id']:
                    if not isinstance(value, int) or value <= 0:
                        raise ValueError(f"Invalid {field} format. Must be positive integer or null")
                elif field == 'exam_date' and not isinstance(value, date):
                    raise ValueError("exam_date must be date object or null")
                elif field in ['start_time', 'end_time'] and not isinstance(value, time):  # Changed
                    raise ValueError(f"{field} must be time object or null")
        
        # Validate time window (still works with time objects)
        if start_time and end_time and start_time >= end_time:
            raise ValueError("Start time must be before end time")
        
        try:
            return self.repo.filter_exams(
                major_id, college_id, level_id,
                year_id, semester_id, exam_date,
                start_time, end_time
            )
        except Exception as e:
            raise RuntimeError(f"Failed to filter exams: {str(e)}")

    def get_exam_time_slots(self, target_date: Optional[date] = None) -> List[Dict[str, time]]:  # Changed return type
        """
        Retrieve exam time slots for a specific date
        
        Args:
            target_date: Optional date to filter (default: today)
            
        Returns:
            List of time slots as dictionaries with 'start_time' and 'end_time'
            Example: [{
                'start_time': time(9,0),  # Changed to time
                'end_time': time(11,0)    # Changed to time
            }]
            
        Raises:
            ValueError: If date is invalid
            RuntimeError: For database errors
        """
        try:
            # Validate date
            if target_date and not isinstance(target_date, date):
                raise ValueError("target_date must be a date object or None")
                
            return self.repo.get_exam_time_slots(target_date)
            
        except ValueError as e:
            raise ValueError(f"Validation error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Service error: {str(e)}")
        
    def get_exam_dates(self) -> List[date]:
        """
        Retrieve all distinct exam dates from database
        
        Returns:
            List of unique exam dates sorted in descending order
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
          
            return self.repo.get_exam_dates()
        except Exception as e:
            raise RuntimeError(f"Failed to get exam dates: {str(e)}")

    def get_exam_by_id(self, exam_id: int) -> Dict:
        """
        Get exam by ID with validation
        
        Args:
            exam_id: ID of the exam to retrieve
            
        Returns:
            Exam details with time objects (not datetime)
            Example: {
                'exam_id': 1,
                'course_id': 1,
                'exam_date': date(2023,12,15),
                'exam_start_time': time(9,0),  # time object
                'exam_end_time': time(11,0),   # time object
                ...
            }
            
        Raises:
            ValueError: If exam_id is invalid or exam not found
            RuntimeError: If database operation fails
        """
        # Validate exam_id
        if not isinstance(exam_id, int) or exam_id <= 0:
            raise ValueError("Invalid exam ID - must be positive integer")
        
        try:
            # Repository now returns time objects automatically
            result = self.repo.get_exam_by_id(exam_id)
            if not result:
                raise ValueError(f"Exam with ID {exam_id} not found")
            return result
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise RuntimeError(f"Failed to get exam: {str(e)}")