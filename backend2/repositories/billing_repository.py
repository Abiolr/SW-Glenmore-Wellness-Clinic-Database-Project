from .base_repository import BaseRepository


class BillingRepository(BaseRepository):
    def create_billing(self, data: dict):
        return self.db["billing"].insert_one(data).inserted_id
