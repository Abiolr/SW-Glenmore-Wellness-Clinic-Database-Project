from .base_repository import BaseRepository


class AppointmentRepository(BaseRepository):
    def find_by_patient(self, patient_id: int):
        return list(self.db["appointments"].find({"patient_id": patient_id}))
