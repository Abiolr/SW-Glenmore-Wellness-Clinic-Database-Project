from .base_repository import BaseRepository


class StaffRepository(BaseRepository):
    def list_all(self):
        return list(self.db["staff"].find())
