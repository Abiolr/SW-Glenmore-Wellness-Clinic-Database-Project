# weekly_coverage.py

from services.database import get_next_sequence

def handle_get_staff_assignments(db):
    """
    Handles the logic for fetching all staff assignments,
    sorted by date and then on_call_start time.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        collection = db.WeeklyCoverage
        
        # Find all documents and sort them
        # Sort by 'date' (ascending, 1) then 'on_call_start' (ascending, 1)
        assignments_cursor = collection.find().sort([
            ("date", 1),
            ("on_call_start", 1)
        ])
        
        assignments_list = []
        for doc in assignments_cursor:
            doc.pop('_id', None) 
            
            assignments_list.append({
                "assignment_id": doc.get("assignment_id"),
                "date": doc.get("date"),
                "staff_name": doc.get("staff_name"),
                "on_call_start": doc.get("on_call_start"),
                "on_call_end": doc.get("on_call_end"),
                "phone": doc.get("phone")
            })
            
        return {
            "status": "success",
            "assignments": assignments_list
        }, 200
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }, 500

def handle_add_staff_assignment(db, data):
    """
    Handles the logic for adding a new staff assignment.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        if not data:
            return {"status": "error", "message": "No input data provided"}, 400
        
        # --- Validation ---
        required_fields = ['date', 'staff_name', 'on_call_start', 'on_call_end', 'phone']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return {"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"}, 400
            
        # --- ID Generation ---
        try:
            new_id = get_next_sequence("assignment_id")
        except ValueError as e:
            return {"status": "error", "message": f"Could not generate sequence ID: {e}"}, 500
        
        # --- Document Creation ---
        new_assignment = {
            "assignment_id": new_id,
            "date": data['date'],
            "staff_name": data['staff_name'],
            "on_call_start": data['on_call_start'],
            "on_call_end": data['on_call_end'],
            "phone": data['phone']
        }

        # --- Database Insertion ---
        collection = db.WeeklyCoverage
        collection.insert_one(new_assignment)
        
        new_assignment.pop('_id', None) # Remove DB-specific ID for the response
        
        return {
            "status": "success", 
            "message": "Assignment added",
            "assignment": new_assignment
        }, 201
        
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def handle_update_staff_assignment(db, assignment_id, data):
    """
    Handles the logic for updating an existing staff assignment.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        if not data:
            return {"status": "error", "message": "No input data provided"}, 400

        # --- Build Update Document ---
        # Only include fields that were provided in the request
        update_data = {}
        if data.get("date") is not None:
            update_data["date"] = data.get("date")
        if data.get("staff_name") is not None:
            update_data["staff_name"] = data.get("staff_name")
        if data.get("on_call_start") is not None:
            update_data["on_call_start"] = data.get("on_call_start")
        if data.get("on_call_end") is not None:
            update_data["on_call_end"] = data.get("on_call_end")
        if data.get("phone") is not None:
            update_data["phone"] = data.get("phone")
            
        if not update_data:
            return {"status": "error", "message": "No fields to update provided"}, 400

        # --- Database Update ---
        collection = db.WeeklyCoverage
        result = collection.find_one_and_update(
            {"assignment_id": assignment_id},
            {"$set": update_data},
            return_document=True # Returns the new, updated document
        )
        
        # --- Handle Response ---
        if result:
            result.pop('_id', None)
            return {
                "status": "success",
                "message": "Assignment updated",
                "assignment": result
            }, 200
        else:
            return {
                "status": "error",
                "message": f"Assignment with id {assignment_id} not found"
            }, 404
            
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def handle_delete_staff_assignment(db, assignment_id):
    """
    Handles the logic for deleting an existing staff assignment.
    """
    if db is None:
        return {"status": "error", "message": "Database not connected"}, 500
        
    try:
        collection = db.WeeklyCoverage
        
        result = collection.delete_one({"assignment_id": assignment_id})
        
        if result.deleted_count > 0:
            return {
                "status": "success",
                "message": f"Assignment with id {assignment_id} deleted"
            }, 200
        else:
            return {
                "status": "error",
                "message": f"Assignment with id {assignment_id} not found"
            }, 404
            
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500