from database.academic.majors_repository import MajorsRepository
from database.academic.colleges_repository import CollegesRepository

class MajorsService:
    
    def __init__(self):
        self.majors_repo = MajorsRepository()
        self.colleges_repo = CollegesRepository()

    def create_major(self, name, college_id):
        if not name or len(name.strip()) < 2:
            raise ValueError("Major name must be at least 2 characters")
        
        if not self.colleges_repo.get_college(college_id):
            raise ValueError("College does not exist")
            
        existing = [m for m in self.get_majors_by_college(college_id) 
                  if m['name'].lower() == name.lower()]
        if existing:
            raise ValueError("Major already exists in this college")
            
        return self.majors_repo.create_major(name.strip(), college_id)

    def get_major(self, major_id):
        major = self.majors_repo.get_major(major_id)
        if not major:
            raise ValueError("Major not found")
        return major

    def get_majors_by_college(self, college_id):
        return self.majors_repo.get_majors_by_college(college_id)

    def update_major(self, major_id, name, college_id):
        if not name or len(name.strip()) < 2:
            raise ValueError("Major name must be at least 2 characters")
            
        if not self.colleges_repo.get_college(college_id):
            raise ValueError("College does not exist")
            
        updated = self.majors_repo.update_major(major_id, name.strip(), college_id)
        if not updated:
            raise ValueError("Major not found")
        return updated

    def delete_major(self, major_id):
        deleted = self.majors_repo.delete_major(major_id)
        if not deleted:
            raise ValueError("Major not found")
        return {"message": "Major deleted"}