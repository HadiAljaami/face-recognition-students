from typing import List, Dict, Optional
from database.academic.semesters_repository import SemestersRepository

class SemestersService:
    def __init__(self):
        self.repo = SemestersRepository()

    def create_semester(self, semester_name: str) -> Dict:
        """Create new semester with validation"""
        if not semester_name or not isinstance(semester_name, str):
            raise ValueError("Semester name must be a non-empty string")
        if len(semester_name) > 50:
            raise ValueError("Semester name exceeds maximum length (50 chars)")
        
        return self.repo.create_semester(semester_name)

    def get_all_semesters(self) -> List[Dict]:
        """Get all semesters"""
        return self.repo.get_all_semesters()

    def get_semester_by_id(self, semester_id: int) -> Optional[Dict]:
        """Get semester by ID with validation"""
        if not isinstance(semester_id, int) or semester_id <= 0:
            raise ValueError("Invalid semester ID")
        
        result = self.repo.get_semester_by_id(semester_id)
        if not result:
            raise ValueError("Semester not found")
        return result

    def update_semester(self, semester_id: int, semester_name: str) -> Dict:
        """Update semester with validation"""
        if not isinstance(semester_id, int) or semester_id <= 0:
            raise ValueError("Invalid semester ID")
        if not semester_name or not isinstance(semester_name, str):
            raise ValueError("Semester name must be a non-empty string")
        if len(semester_name) > 50:
            raise ValueError("Semester name exceeds maximum length (50 chars)")
        
        return self.repo.update_semester(semester_id, semester_name)

    def delete_semester(self, semester_id: int) -> Dict:
        """Delete semester with validation"""
        if not isinstance(semester_id, int) or semester_id <= 0:
            raise ValueError("Invalid semester ID")
        
        if self.repo.delete_semester(semester_id):
            return {"message": "Semester deleted successfully"}
        raise RuntimeError("Failed to delete semester")