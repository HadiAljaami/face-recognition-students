# servers/vectors_service.py
from database.vectors_repository import VectorsRepository

class VectorsService:
    def __init__(self, repository):
        self.repository = repository

    def add_vector(self, student_id, college, vector):
        return self.repository.insert_vector(student_id, college, vector)

    def update_vector_by_id(self, vector_id, vector):
        return self.repository.update_vector_by_id(vector_id,vector)

    def delete_vector(self, student_id):
        return self.repository.delete_vector(student_id)

    def get_all_vectors(self):
        return self.repository.get_all_vectors()
    
    def get_all_student_ids(self):
        return self.repository.get_all_student_ids()

    def get_vector_by_id(self, student_id):
        return self.repository.get_vector_by_student_id(student_id)

    def find_similar_vectors(self, vector, threshold=0.8,limit=1):
        # print("length:",len(vector))
        # print(type (vector) )
        return self.repository.search_similar_vectors(vector, threshold,limit)

    def search_vectors_by_college(self, vector, college, threshold=0.8,limit=1):
        return self.repository.search_similar_vectors_in_college(vector, college,  threshold, limit)