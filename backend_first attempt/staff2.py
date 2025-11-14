from .services.connection_DB import db
from database import get_next_sequence

# Add staff function
def add_new_staff(first_name: str, last_name: str, email: str, role_id: int, active: bool = True):
    """
    Adds a new staff member and links them to a role.
    Inserts into both 'Staff' and 'StaffRole' collections.
    """
    # Generate the next Staff ID
    staff_id = get_next_sequence("Staff_id")

    # Prepare staff document
    staff_doc = {
        "Staff_Id": staff_id,
        "First_Name": first_name,
        "Last_Name": last_name,
        "Email": email,
        "Active": active
    }

    # Insert into Staff collection
    db.Staff.insert_one(staff_doc)

    # Prepare StaffRole document (linking Staff ↔ Role)
    staff_role_doc = {
        "Staff_Id": staff_id,
        "Role_Id": role_id
    }

    # Insert into StaffRole collection
    db.StaffRole.insert_one(staff_role_doc)

    print(f"Added new staff: {first_name} {last_name} (Staff_Id: {staff_id}) assigned to Role_Id: {role_id}")
    return staff_id

# Update staff function
def update_staff(staff_id: int, first_name=None, last_name=None, email=None, role_id=None, active=None):
    """
    Updates a staff member's information in the Staff and StaffRole collections.
    Fields are optional — only those provided will be updated.
    """
    # Check if staff exists
    staff = db.Staff.find_one({"Staff_Id": staff_id})
    if not staff:
        print(f"No staff member found with Staff_Id: {staff_id}")
        return False

    # Build update object for Staff collection
    update_fields = {}
    if first_name is not None:
        update_fields["First_Name"] = first_name
    if last_name is not None:
        update_fields["Last_Name"] = last_name
    if email is not None:
        update_fields["Email"] = email
    if active is not None:
        update_fields["Active"] = active

    # Perform the staff update if needed
    if update_fields:
        db.Staff.update_one(
            {"Staff_Id": staff_id},
            {"$set": update_fields}
        )
        print(f"Updated Staff_Id {staff_id} details: {update_fields}")

    # Update the role in StaffRole if provided
    if role_id is not None:
        db.StaffRole.update_one(
            {"Staff_Id": staff_id},
            {"$set": {"Role_Id": role_id}},
            upsert=True  # ensure record exists
        )
        print(f"Updated Role_Id for Staff_Id {staff_id} to {role_id}")

    print("Staff update complete.")
    return True

# Delete staff function
def delete_staff(staff_id: int):
    """
    Deletes a staff member and their role mapping from the database.
    Ensures both Staff and StaffRole collections stay in sync.
    """
    # Check if staff exists before deleting
    staff = db.Staff.find_one({"Staff_Id": staff_id})
    if not staff:
        print(f"No staff member found with Staff_Id: {staff_id}")
        return False

    # Delete from Staff collection
    staff_result = db.Staff.delete_one({"Staff_Id": staff_id})

    # Delete from StaffRole collection
    role_result = db.StaffRole.delete_one({"Staff_Id": staff_id})

    if staff_result.deleted_count > 0:
        print(f"Deleted staff record for Staff_Id: {staff_id}")
    if role_result.deleted_count > 0:
        print(f"Deleted StaffRole mapping for Staff_Id: {staff_id}")

    print("Staff deletion completed successfully.")
    return True