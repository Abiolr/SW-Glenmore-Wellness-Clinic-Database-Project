from .base_repository import BaseRepository


class PatientRepository(BaseRepository):
    def create(self, data: dict):
        return self.db["patients"].insert_one(data).inserted_id
