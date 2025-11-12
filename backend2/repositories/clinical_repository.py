from .base_repository import BaseRepository


class ClinicalRepository(BaseRepository):
    def add_note(self, data: dict):
        return self.db["clinical_notes"].insert_one(data).inserted_id
