from typing import List, Dict, Optional
from database.academic.academic_years_repository import AcademicYearsRepository

class AcademicYearsService:
    def __init__(self):
        self.repo = AcademicYearsRepository()

    def create_year(self, year_name: str) -> Dict:
        """Create new academic year with validation"""
        if not year_name or not isinstance(year_name, str):
            raise ValueError("Year name must be a non-empty string")
        if len(year_name) > 50:
            raise ValueError("Year name exceeds maximum length (50 characters)")
        
        try:
            return self.repo.create_year(year_name)
        except ValueError as e:
            raise ValueError(str(e))
        except RuntimeError as e:
            raise RuntimeError("Service unavailable: " + str(e))
        except Exception as e:
            raise Exception("Internal server error")

    def get_all_years(self) -> List[Dict]:
        """Retrieve all academic years"""
        try:
            return self.repo.get_all_years()
        except RuntimeError as e:
            raise RuntimeError("Service unavailable: " + str(e))
        except Exception as e:
            raise Exception("Internal server error")

    def get_year_by_id(self, year_id: int) -> Optional[Dict]:
        """Get academic year by ID with validation"""
        if not isinstance(year_id, int) or year_id <= 0:
            raise ValueError("Invalid year ID format")
        
        try:
            result = self.repo.get_year_by_id(year_id)
            if not result:
                raise ValueError("Academic year not found")
            return result
        except ValueError as e:
            raise ValueError(str(e))
        except RuntimeError as e:
            raise RuntimeError("Service unavailable: " + str(e))
        except Exception as e:
            raise Exception("Internal server error")

    def update_year(self, year_id: int, year_name: str) -> Dict:
        """Update academic year with validation"""
        if not isinstance(year_id, int) or year_id <= 0:
            raise ValueError("Invalid year ID format")
        if not year_name or not isinstance(year_name, str):
            raise ValueError("Year name must be a non-empty string")
        if len(year_name) > 50:
            raise ValueError("Year name exceeds maximum length (50 characters)")
        
        try:
            return self.repo.update_year(year_id, year_name)
        except ValueError as e:
            raise ValueError(str(e))
        except RuntimeError as e:
            raise RuntimeError("Service unavailable: " + str(e))
        except Exception as e:
            raise Exception("Internal server error")

    def delete_year(self, year_id: int) -> Dict:
        """Delete academic year with validation"""
        if not isinstance(year_id, int) or year_id <= 0:
            raise ValueError("Invalid year ID format")
        
        try:
            success = self.repo.delete_year(year_id)
            if not success:
                raise RuntimeError("Deletion operation failed")
            return {"message": "Academic year deleted successfully"}
        except ValueError as e:
            raise ValueError(str(e))
        except RuntimeError as e:
            raise RuntimeError("Service unavailable: " + str(e))
        except Exception as e:
            raise Exception("Internal server error")