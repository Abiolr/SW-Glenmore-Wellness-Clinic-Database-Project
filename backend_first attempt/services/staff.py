# staff.py

from services.database import get_next_sequence

def handle_get_all_staff(db):
    """
    Handles the logic for fetching all staff members.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        collection = db.Staff
        
        staff_cursor = collection.find().sort("staff_id", 1)
        
        staff_list = []
        for doc in staff_cursor:
            doc.pop('_id', None)
            
            staff_list.append({
                "staff_id": doc.get("staff_id"),
                "first_name": doc.get("first_name"),
                "last_name": doc.get("last_name"),
                "full_name": doc.get("full_name"),
                "role": doc.get("role"),
                "phone": doc.get("phone"),
                "email": doc.get("email"),
                "specialization": doc.get("specialization")
            })
            
        return {
            "status": "success",
            "staff": staff_list
        }, 200
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }, 500

def handle_get_staff_by_id(db, staff_id):
    """
    Handles the logic for fetching a single staff member by ID.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        collection = db.Staff
        
        staff = collection.find_one({"staff_id": staff_id})
        
        if staff:
            staff.pop('_id', None)
            return {
                "status": "success",
                "staff": staff
            }, 200
        else:
            return {
                "status": "error",
                "message": f"Staff member with ID {staff_id} not found"
            }, 404
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }, 500

def handle_add_staff(db, data):
    """
    Handles the logic for adding a new staff member.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        if not data:
            return {"status": "error", "message": "No input data provided"}, 400
        
        # --- Validation ---
        required_fields = ['first_name', 'last_name', 'role']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return {"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"}, 400
            
        # --- ID Generation ---
        try:
            new_id = get_next_sequence("staff_id")
        except ValueError as e:
            return {"status": "error", "message": f"Could not generate sequence ID: {e}"}, 500
        
        # --- Create full_name ---
        full_name = f"{data['first_name']} {data['last_name']}"
        
        # --- Document Creation ---
        new_staff = {
            "staff_id": new_id,
            "first_name": data['first_name'],
            "last_name": data['last_name'],
            "full_name": full_name,
            "role": data['role'],
            "phone": data.get('phone'),
            "email": data.get('email'),
            "specialization": data.get('specialization')
        }

        # --- Database Insertion ---
        collection = db.Staff
        collection.insert_one(new_staff)
        
        new_staff.pop('_id', None)
        
        return {
            "status": "success", 
            "message": "Staff member added",
            "staff": new_staff
        }, 201
        
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def handle_update_staff(db, staff_id, data):
    """
    Handles the logic for updating an existing staff member.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        if not data:
            return {"status": "error", "message": "No input data provided"}, 400

        # --- Build Update Document ---
        update_data = {}
        allowed_fields = ['first_name', 'last_name', 'role', 'phone', 'email', 'specialization']
        
        for field in allowed_fields:
            if data.get(field) is not None:
                update_data[field] = data.get(field)
        
        # --- Update full_name if first_name or last_name changed ---
        if 'first_name' in update_data or 'last_name' in update_data:
            # Get current staff to build full name
            current_staff = db.Staff.find_one({"staff_id": staff_id})
            if not current_staff:
                return {
                    "status": "error",
                    "message": f"Staff member with ID {staff_id} not found"
                }, 404
            
            first_name = update_data.get('first_name', current_staff.get('first_name'))
            last_name = update_data.get('last_name', current_staff.get('last_name'))
            update_data['full_name'] = f"{first_name} {last_name}"
            
        if not update_data:
            return {"status": "error", "message": "No fields to update provided"}, 400

        # --- Database Update ---
        collection = db.Staff
        result = collection.find_one_and_update(
            {"staff_id": staff_id},
            {"$set": update_data},
            return_document=True
        )
        
        # --- Handle Response ---
        if result:
            result.pop('_id', None)
            return {
                "status": "success",
                "message": "Staff member updated",
                "staff": result
            }, 200
        else:
            return {
                "status": "error",
                "message": f"Staff member with ID {staff_id} not found"
            }, 404
            
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def handle_delete_staff(db, staff_id):
    """
    Handles the logic for deleting an existing staff member.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        collection = db.Staff
        
        result = collection.delete_one({"staff_id": staff_id})
        
        if result.deleted_count > 0:
            return {
                "status": "success",
                "message": f"Staff member with ID {staff_id} deleted"
            }, 200
        else:
            return {
                "status": "error",
                "message": f"Staff member with ID {staff_id} not found"
            }, 404
            
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500