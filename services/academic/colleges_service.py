# services/academic/colleges_service.py
from database.academic.colleges_repository import CollegesRepository

class CollegesService:
    
    def __init__(self, repo=None):
        self.repo = repo or CollegesRepository()

    def create_college(self, name):
        if not name or len(name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        existing = [c for c in self.get_all_colleges() if c['name'].lower() == name.lower()]
        if existing:
            raise ValueError("College already exists")
        return self.repo.create_college(name.strip())

    def get_college(self, college_id):
        college = self.repo.get_college(college_id)
        if not college:
            raise ValueError("College not found")
        return college

    def get_all_colleges(self):
        return self.repo.get_all_colleges()

    def update_college(self, college_id, name):
        if not name or len(name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        college = self.repo.update_college(college_id, name.strip())
        if not college:
            raise ValueError("College not found")
        return college

    def delete_college(self, college_id):
        if not self.repo.delete_college(college_id):
            raise ValueError("College not found")
        return {"message": "College deleted"}