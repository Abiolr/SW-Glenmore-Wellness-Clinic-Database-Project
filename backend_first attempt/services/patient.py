# patient.py

from services.database import get_next_sequence

def handle_get_all_patients(db):
    """
    Handles the logic for fetching all patients.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        collection = db.Patient
        
        patients_cursor = collection.find().sort("patient_id", 1)
        
        patients_list = []
        for doc in patients_cursor:
            doc.pop('_id', None)
            
            patients_list.append({
                "patient_id": doc.get("patient_id"),
                "first_name": doc.get("first_name"),
                "last_name": doc.get("last_name"),
                "full_name": doc.get("full_name"),
                "date_of_birth": doc.get("date_of_birth"),
                "phone": doc.get("phone"),
                "email": doc.get("email"),
                "address": doc.get("address"),
                "emergency_contact": doc.get("emergency_contact"),
                "emergency_phone": doc.get("emergency_phone")
            })
            
        return {
            "status": "success",
            "patients": patients_list
        }, 200
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }, 500

def handle_get_patient_by_id(db, patient_id):
    """
    Handles the logic for fetching a single patient by ID.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        collection = db.Patient
        
        patient = collection.find_one({"patient_id": patient_id})
        
        if patient:
            patient.pop('_id', None)
            return {
                "status": "success",
                "patient": patient
            }, 200
        else:
            return {
                "status": "error",
                "message": f"Patient with ID {patient_id} not found"
            }, 404
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }, 500

def handle_add_patient(db, data):
    """
    Handles the logic for adding a new patient.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        if not data:
            return {"status": "error", "message": "No input data provided"}, 400
        
        # --- Validation ---
        required_fields = ['first_name', 'last_name', 'date_of_birth']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return {"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"}, 400
            
        # --- ID Generation ---
        try:
            new_id = get_next_sequence("patient_id")
        except ValueError as e:
            return {"status": "error", "message": f"Could not generate sequence ID: {e}"}, 500
        
        # --- Create full_name ---
        full_name = f"{data['first_name']} {data['last_name']}"
        
        # --- Document Creation ---
        new_patient = {
            "patient_id": new_id,
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "full_name": full_name,
            "date_of_birth": data['date_of_birth'],
            "phone": data.get('phone'),
            "email": data.get('email'),
            "address": data.get('address'),
            "emergency_contact": data.get('emergency_contact'),
            "emergency_phone": data.get('emergency_phone')
        }

        # --- Database Insertion ---
        collection = db.Patient
        collection.insert_one(new_patient)
        
        new_patient.pop('_id', None)
        
        return {
            "status": "success", 
            "message": "Patient added",
            "patient": new_patient
        }, 201
        
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def handle_update_patient(db, patient_id, data):
    """
    Handles the logic for updating an existing patient.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        if not data:
            return {"status": "error", "message": "No input data provided"}, 400

        # --- Build Update Document ---
        update_data = {}
        allowed_fields = ['first_name', 'last_name', 'date_of_birth', 'phone', 
                          'email', 'address', 'emergency_contact', 'emergency_phone']
        
        for field in allowed_fields:
            if data.get(field) is not None:
                update_data[field] = data.get(field)
        
        # --- Update full_name if first_name or last_name changed ---
        if 'first_name' in update_data or 'last_name' in update_data:
            # Get current patient to build full name
            current_patient = db.Patient.find_one({"patient_id": patient_id})
            if not current_patient:
                return {
                    "status": "error",
                    "message": f"Patient with ID {patient_id} not found"
                }, 404
            
            first_name = update_data.get('first_name', current_patient.get('first_name'))
            last_name = update_data.get('last_name', current_patient.get('last_name'))
            update_data['full_name'] = f"{first_name} {last_name}"
            
        if not update_data:
            return {"status": "error", "message": "No fields to update provided"}, 400

        # --- Database Update ---
        collection = db.Patient
        result = collection.find_one_and_update(
            {"patient_id": patient_id},
            {"$set": update_data},
            return_document=True
        )
        
        # --- Handle Response ---
        if result:
            result.pop('_id', None)
            return {
                "status": "success",
                "message": "Patient updated",
                "patient": result
            }, 200
        else:
            return {
                "status": "error",
                "message": f"Patient with ID {patient_id} not found"
            }, 404
            
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def handle_delete_patient(db, patient_id):
    """
    Handles the logic for deleting an existing patient.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        collection = db.Patient
        
        result = collection.delete_one({"patient_id": patient_id})
        
        if result.deleted_count > 0:
            return {
                "status": "success",
                "message": f"Patient with ID {patient_id} deleted"
            }, 200
        else:
            return {
                "status": "error",
                "message": f"Patient with ID {patient_id} not found"
            }, 404
            
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500