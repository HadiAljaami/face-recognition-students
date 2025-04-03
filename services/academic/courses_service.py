from typing import List, Dict, Optional
from database.academic.courses_repository import CoursesRepository

class CoursesService:
    def __init__(self):
        self.repo = CoursesRepository()

    def create_course(self, name: str, major_id: int, level_id: int, year_id: int, semester_id: int) -> Dict:
        """Validate and create a new course"""
        if not name or not isinstance(name, str):
            raise ValueError("Course name must be a non-empty string")
        if len(name) > 255:
            raise ValueError("Course name exceeds maximum length (255 chars)")
        if not all(isinstance(id, int) and id > 0 for id in [major_id, level_id, year_id, semester_id]):
            raise ValueError("All reference IDs must be positive integers")

        return self.repo.create_course(name, major_id, level_id, year_id, semester_id)

    def get_all_courses(self) -> List[Dict]:
        """Retrieve all courses"""
        return self.repo.get_all_courses()

    def get_course_by_id(self, course_id: int) -> Optional[Dict]:
        """Get course by ID with validation"""
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValueError("Invalid course ID")

        result = self.repo.get_course_by_id(course_id)
        if not result:
            raise ValueError("Course not found")
        return result

    def update_course(self, course_id: int, name: str, major_id: int, level_id: int, year_id: int, semester_id: int) -> Dict:
        """Validate and update course"""
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValueError("Invalid course ID")
        if not name or not isinstance(name, str):
            raise ValueError("Course name must be a non-empty string")
        if len(name) > 255:
            raise ValueError("Course name exceeds maximum length (255 chars)")
        if not all(isinstance(id, int) and id > 0 for id in [major_id, level_id, year_id, semester_id]):
            raise ValueError("All reference IDs must be positive integers")

        return self.repo.update_course(course_id, name, major_id, level_id, year_id, semester_id)

    def delete_course(self, course_id: int) -> Dict:
        """Delete course with validation"""
        if not isinstance(course_id, int) or course_id <= 0:
            raise ValueError("Invalid course ID")

        if self.repo.delete_course(course_id):
            return {"message": "Course deleted successfully"}
        raise RuntimeError("Failed to delete course")
    
    
        # Add these new methods to the existing CoursesService class
    
    def search_courses(self, search_term: str) -> List[Dict]:
        """Search courses by name with validation"""
        if not search_term or not isinstance(search_term, str):
            raise ValueError("Search term must be a non-empty string")
        if len(search_term) > 100:
            raise ValueError("Search term too long")
        
        return self.repo.search_courses_by_name(search_term)

    def filter_courses(self, major_id: int = None, level_id: int = None,
                    year_id: int = None, semester_id: int = None) -> List[Dict]:
        """Filter courses with validation"""
        filters = {
            'major_id': major_id,
            'level_id': level_id,
            'year_id': year_id,
            'semester_id': semester_id
        }
        
        # Validate all provided IDs
        for field, value in filters.items():
            if value is not None and (not isinstance(value, int) or value <= 0):
                raise ValueError(f"Invalid {field} format")
        
        return self.repo.filter_courses(major_id, level_id, year_id, semester_id)