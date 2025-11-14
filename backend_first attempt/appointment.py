from database import get_next_sequence
from .services.connection_DB import db
from datetime import datetime

# ===========================
#  APPOINTMENT COLLECTION
# ===========================
# Insert appointment function
def insert_appointment(patient_id, staff_id, scheduled_start, scheduled_end, is_walkin=False):
    """
    Insert a new appointment record.
    """
    appointment_id = get_next_sequence("Appointment_Id")

    new_appointment = {
        "Appointment_Id": appointment_id,
        "Patient_Id": patient_id,
        "Staff_Id": staff_id,
        "Scheduled_Start": scheduled_start,
        "Scheduled_End": scheduled_end,
        "Is_Walkin": is_walkin,
        "Created_At": datetime.now()
    }

    db.Appointment.insert_one(new_appointment)
    print(f"Appointment inserted with ID: {appointment_id}")
    return appointment_id

# Update appointment function
def update_appointment(appointment_id: int, **updates):
    """
    Updates an appointment record in the Appointment collection.
    All fields except Appointment_Id are allowed to be updated.
    """
    if not updates:
        print("No fields provided to update.")
        return False

    # Disallowed fields
    restricted_fields = {"Appointment_Id"}

    # Filter out restricted fields
    valid_updates = {k: v for k, v in updates.items() if k not in restricted_fields}

    if not valid_updates:
        print("No valid fields provided to update (Appointment_Id is immutable).")
        return False

    result = db.Appointment.update_one(
        {"Appointment_Id": appointment_id},
        {"$set": valid_updates}
    )

    if result.matched_count > 0:
        print(f"Appointment {appointment_id} updated successfully: {valid_updates}")
        return True
    else:
        print(f"Appointment {appointment_id} not found.")
        return False

# Delete appointment function
def delete_appointment(appointment_id):
    """
    Delete an appointment by ID.
    """
    result = db.Appointment.delete_one({"Appointment_Id": appointment_id})
    if result.deleted_count:
        print(f"Appointment {appointment_id} deleted.")
        return True
    else:
        print(f"Appointment {appointment_id} not found.")
        return False


# ===========================
#  VISIT COLLECTION
# ===========================
# Insert visit function
def insert_visit(patient_id, staff_id, appointment_id, start_time, end_time, visit_type, notes=None):
    """
    Insert a new visit record.
    """
    visit_id = get_next_sequence("Visit_Id")

    new_visit = {
        "Visit_Id": visit_id,
        "Patient_Id": patient_id,
        "Staff_Id": staff_id,
        "Appointment_Id": appointment_id,
        "Start_Time": start_time,
        "End_Time": end_time,
        "Visit_Type": visit_type,
        "Notes": notes or ""
    }

    db.Visit.insert_one(new_visit)
    print(f"Visit inserted with ID: {visit_id}")
    return visit_id

# Update visit function
def update_visit(visit_id: int, **updates):
    """
    Updates a visit record in the Visit collection.
    All fields except Visit_Id are allowed to be updated.
    """
    if not updates:
        print("No fields provided to update.")
        return False

    # Disallowed fields
    restricted_fields = {"Visit_Id"}

    # Filter out restricted fields
    valid_updates = {k: v for k, v in updates.items() if k not in restricted_fields}

    if not valid_updates:
        print("No valid fields provided to update (Visit_Id is immutable).")
        return False

    result = db.Visit.update_one(
        {"Visit_Id": visit_id},
        {"$set": valid_updates}
    )

    if result.matched_count > 0:
        print(f"Visit {visit_id} updated successfully: {valid_updates}")
        return True
    else:
        print(f"Visit {visit_id} not found.")
        return False

# Delete visit function
def delete_visit(visit_id):
    """
    Delete a visit by ID.
    """
    result = db.Visit.delete_one({"Visit_Id": visit_id})
    if result.deleted_count:
        print(f"Visit {visit_id} deleted.")
        return True
    else:
        print(f"Visit {visit_id} not found.")
        return False

