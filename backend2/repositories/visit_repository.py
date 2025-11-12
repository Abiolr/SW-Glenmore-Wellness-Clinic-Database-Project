from .base_repository import BaseRepository


class VisitRepository(BaseRepository):
    def create_visit(self, data: dict):
        return self.db["visits"].insert_one(data).inserted_id
