from database.academic.levels_repository import LevelsRepository

class LevelsService:
    
    def __init__(self, repo=None):
        self.repo = repo or LevelsRepository()

    def create_level(self, level_name):
        if not level_name or len(level_name.strip()) < 2:
            raise ValueError("Level name must be at least 2 characters")
        
        try:
            return self.repo.create_level(level_name.strip())
        except ValueError as e:
            raise ValueError(str(e))
        except RuntimeError as e:
            raise RuntimeError("Service temporarily unavailable")

    def get_level(self, level_id):
        try:
            level = self.repo.get_level(level_id)
            if not level:
                raise ValueError("Level not found")
            return level
        except RuntimeError as e:
            raise RuntimeError("Service temporarily unavailable")

    def get_all_levels(self):
        try:
            return self.repo.get_all_levels()
        except RuntimeError as e:
            raise RuntimeError("Service temporarily unavailable")

    def update_level(self, level_id, new_name):
        if not new_name or len(new_name.strip()) < 2:
            raise ValueError("Level name must be at least 2 characters")
            
        try:
            return self.repo.update_level(level_id, new_name.strip())
        except ValueError as e:
            raise ValueError(str(e))
        except RuntimeError as e:
            raise RuntimeError("Service temporarily unavailable")

    def delete_level(self, level_id):
        try:
            return self.repo.delete_level(level_id)
        except ValueError as e:
            raise ValueError(str(e))
        except RuntimeError as e:
            raise RuntimeError("Service temporarily unavailable")