class BaseRepository:
    def __init__(self, db):
        self.db = db

    def find_one(self, collection: str, query: dict):
        return self.db[collection].find_one(query)
class BaseRepository:
    def __init__(self, db):
        self._db = db
