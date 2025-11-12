from .base_repository import BaseRepository


class PrescriptionRepository(BaseRepository):
    def create(self, data: dict):
        return self.db["prescriptions"].insert_one(data).inserted_id
