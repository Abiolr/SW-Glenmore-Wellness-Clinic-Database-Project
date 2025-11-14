# appointment.py

from .database import get_next_sequence
from datetime import datetime
from pymongo.collection import ReturnDocument

# ===================================================================
# HELPER FUNCTIONS FOR NAME/ID LOOKUPS
# These work with the Staff and Patient collections that have full_name fields
# ===================================================================

def get_staff_id_by_name(db, full_name):
    """Helper to find a staff_id by their full_name."""
    if db is None:
        raise Exception("Database not connected")
    
    staff = db.Staff.find_one({"full_name": full_name})
    return staff.get("staff_id") if staff else None

def get_patient_id_by_name(db, full_name):
    """Helper to find a patient_id by their full_name."""
    if db is None:
        raise Exception("Database not connected")
    
    patient = db.Patient.find_one({"full_name": full_name})
    return patient.get("patient_id") if patient else None

def get_staff_name_by_id(db, staff_id):
    """Helper to find a Staff's full_name by their staff_id."""
    if db is None:
        raise Exception("Database not connected")
    
    staff = db.Staff.find_one({"staff_id": staff_id})
    return staff.get("full_name") if staff else "Unknown Practitioner"

def get_patient_name_by_id(db, patient_id):
    """Helper to find a Patient's full_name by their patient_id."""
    if db is None:
        raise Exception("Database not connected")
    
    patient = db.Patient.find_one({"patient_id": patient_id})
    return patient.get("full_name") if patient else "Unknown Patient"

def format_appointment_response(db, appointment_doc):
    """
    Converts an Appointment document (with IDs) into the
    JSON response format (with names).
    """
    if not appointment_doc:
        return None
        
    # Pop internal DB ID
    appointment_doc.pop('_id', None)
    
    # Get names from IDs
    practitioner_name = get_staff_name_by_id(db, appointment_doc.get("staff_id"))
    patient_name = get_patient_name_by_id(db, appointment_doc.get("patient_id"))

    return {
        "appointment_id": appointment_doc.get("appointment_id"),
        "practitioner_name": practitioner_name,
        "patient_name": patient_name,
        "date": appointment_doc.get("date"),
        "start_time": appointment_doc.get("start_time"),
        "end_time": appointment_doc.get("end_time"),
        "type": appointment_doc.get("type"),
        "patient_details": appointment_doc.get("patient_details", "")
    }

# ===========================
#  SCHEDULE HANDLER FUNCTIONS
# ===========================

def handle_get_master_schedule(db, date):
    """
    Fetches a sorted list of all appointments for a specific date.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
    
    try:
        # Find all appointments for the given date
        # Sort by start_time, then by practitioner's staff_id
        appointments_cursor = db.Appointment.find({"date": date}).sort([
            ("start_time", 1),
            ("staff_id", 1)
        ])
        
        schedule_list = []
        for appt in appointments_cursor:
            formatted_appt = format_appointment_response(db, appt)
            if formatted_appt:
                schedule_list.append(formatted_appt)
                
        return {"status": "success", "schedule": schedule_list}, 200

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}, 500

def handle_get_practitioner_schedule(db, date, practitioner_name):
    """
    Fetches a sorted list of appointments for a specific practitioner on a specific date.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        # 1. Find the practitioner's ID
        staff_id = get_staff_id_by_name(db, practitioner_name)
        if not staff_id:
            return {"status": "error", "message": f"Practitioner not found: {practitioner_name}"}, 404
            
        # 2. Find appointments for that practitioner on that date
        appointments_cursor = db.Appointment.find({
            "date": date,
            "staff_id": staff_id
        }).sort("start_time", 1)
        
        schedule_list = []
        for appt in appointments_cursor:
            formatted_appt = format_appointment_response(db, appt)
            if formatted_appt:
                schedule_list.append(formatted_appt)
                
        return {"status": "success", "schedule": schedule_list}, 200

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}, 500

def handle_add_appointment(db, data):
    """
    Adds a new pre-scheduled appointment.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500

    try:
        # 1. Validate required fields
        required_fields = ['practitioner_name', 'patient_name', 'date', 'start_time', 'end_time']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return {"status": "error", "message": f"Missing required fields: {', '.join(missing)}"}, 400
            
        # 2. Get IDs from names
        staff_id = get_staff_id_by_name(db, data['practitioner_name'])
        if not staff_id:
            return {"status": "error", "message": f"Practitioner not found: {data['practitioner_name']}"}, 404
            
        patient_id = get_patient_id_by_name(db, data['patient_name'])
        if not patient_id:
            return {"status": "error", "message": f"Patient not found: {data['patient_name']}"}, 404
            
        # 3. Check for conflicting appointments for the same practitioner
        conflict = db.Appointment.find_one({
            "staff_id": staff_id,
            "date": data['date'],
            "start_time": data['start_time']
        })
        if conflict:
            return {"status": "error", "message": "This time slot is already booked for this practitioner."}, 409

        # 4. Create new appointment document
        new_appointment_id = get_next_sequence("appointment_id")
        
        new_appointment_doc = {
            "appointment_id": new_appointment_id,
            "staff_id": staff_id,
            "patient_id": patient_id,
            "date": data['date'],
            "start_time": data['start_time'],
            "end_time": data['end_time'],
            "type": "scheduled",
            "patient_details": data.get("patient_details", ""),
            "created_at": datetime.now()
        }
        
        # 5. Insert into database
        db.Appointment.insert_one(new_appointment_doc)
        
        # 6. Format and return response
        formatted_response = format_appointment_response(db, new_appointment_doc)
        
        return {
            "status": "success",
            "message": "Appointment added",
            "appointment": formatted_response
        }, 201

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def handle_add_walk_in(db, data):
    """
    Adds a new walk-in patient by finding an available walk-in slot.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500

    try:
        # 1. Validate required fields
        required_fields = ['patient_name', 'date']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return {"status": "error", "message": f"Missing required fields: {', '.join(missing)}"}, 400

        # 2. Get Patient ID
        patient_id = get_patient_id_by_name(db, data['patient_name'])
        if not patient_id:
            return {"status": "error", "message": f"Patient not found: {data['patient_name']}"}, 404

        # 3. Find an available walk-in slot
        # Assumes PractitionerDailySchedule collection uses snake_case
        walk_in_slots = list(db.PractitionerDailySchedule.find({
            "work_date": data['date'],
            "is_walkin": True
        }).sort("slot_start", 1))
        
        if not walk_in_slots:
            return {"status": "error", "message": "No walk-in availability on this date."}, 404

        # Get all taken appointments for the day
        taken_appointments = list(db.Appointment.find(
            {"date": data['date']},
            {"staff_id": 1, "start_time": 1}
        ))
        
        # Convert taken appointments to a set for quick lookup
        taken_slots = set(
            (appt.get('staff_id'), appt.get('start_time'))
            for appt in taken_appointments
        )

        found_slot = None
        for slot in walk_in_slots:
            slot_key = (slot.get('staff_id'), slot.get('slot_start'))
            if slot_key not in taken_slots:
                found_slot = slot
                break
        
        if not found_slot:
            return {"status": "error", "message": "All walk-in slots for today are currently full."}, 409
        
        # 4. Create the appointment
        new_appointment_id = get_next_sequence("appointment_id")
        
        new_appointment_doc = {
            "appointment_id": new_appointment_id,
            "staff_id": found_slot['staff_id'],
            "patient_id": patient_id,
            "date": data['date'],
            "start_time": found_slot['slot_start'],
            "end_time": found_slot['slot_end'],
            "type": "walk-in",
            "patient_details": data.get("patient_details", ""),
            "created_by": data.get("scheduled_by", "System"),
            "created_at": datetime.now()
        }
        
        # 5. Insert into database
        db.Appointment.insert_one(new_appointment_doc)
        
        # 6. Format and return response
        formatted_response = format_appointment_response(db, new_appointment_doc)
        
        return {
            "status": "success",
            "message": "Walk-in appointment added",
            "appointment": formatted_response
        }, 201

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def handle_update_appointment(db, appointment_id, data):
    """
    Updates an existing appointment.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        if not data:
            return {"status": "error", "message": "No update data provided"}, 400

        update_fields = {}
        
        # Handle fields that require ID lookup
        if 'practitioner_name' in data:
            staff_id = get_staff_id_by_name(db, data['practitioner_name'])
            if not staff_id:
                return {"status": "error", "message": f"Practitioner not found: {data['practitioner_name']}"}, 404
            update_fields['staff_id'] = staff_id
            
        if 'patient_name' in data:
            patient_id = get_patient_id_by_name(db, data['patient_name'])
            if not patient_id:
                return {"status": "error", "message": f"Patient not found: {data['patient_name']}"}, 404
            update_fields['patient_id'] = patient_id
            
        # Handle direct fields
        direct_fields = ['date', 'start_time', 'end_time', 'patient_details']
        for field in direct_fields:
            if field in data:
                update_fields[field] = data[field]
                
        if not update_fields:
            return {"status": "error", "message": "No valid fields provided for update"}, 400

        # Perform the update
        updated_doc = db.Appointment.find_one_and_update(
            {"appointment_id": appointment_id},
            {"$set": update_fields},
            return_document=ReturnDocument.AFTER
        )
        
        if not updated_doc:
            return {"status": "error", "message": f"Appointment with id {appointment_id} not found"}, 404

        # Format and return response
        formatted_response = format_appointment_response(db, updated_doc)
        
        return {
            "status": "success",
            "message": "Appointment updated",
            "appointment": formatted_response
        }, 200

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def handle_delete_appointment(db, appointment_id):
    """
    Deletes an appointment by its ID.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        result = db.Appointment.delete_one({"appointment_id": appointment_id})
        
        if result.deleted_count > 0:
            return {
                "status": "success",
                "message": f"Appointment with id {appointment_id} deleted"
            }, 200
        else:
            return {
                "status": "error",
                "message": f"Appointment with id {appointment_id} not found"
            }, 404

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500