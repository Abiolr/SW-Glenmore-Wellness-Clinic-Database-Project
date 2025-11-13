from .services.connection_DB import db
from datetime import datetime
from database import get_next_sequence

# Add patient function
def add_patient(first_name: str, last_name: str, date_of_birth: str, phone: str,
                email: str, gov_card_no: str, insurance_no: str):
    """
    Inserts a new patient document into the Patient collection.
    Automatically assigns a unique Patient_Id using the counters collection.
    """

    # Ensure database connection exists
    if not db:
        raise ConnectionError("Database connection not found.")

    # Convert date string (YYYY-MM-DD) to datetime object
    try:
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date of Birth must be in YYYY-MM-DD format")

    # Check for duplicate government or insurance card numbers
    existing = db.Patient.find_one({
        "$or": [
            {"Gov_Card_no": gov_card_no},
            {"Insurance_no": insurance_no}
        ]
    })

    if existing:
        print("A patient with the same government or insurance card already exists.")
        return None

    #Explicitly get next Patient_Id using your sequence counter
    patient_id = get_next_sequence("Patient_id")

    # Create the document
    new_patient = {
        "Patient_Id": patient_id,
        "First_Name": first_name,
        "Last_Name": last_name,
        "Date_Of_Birth": dob,
        "Phone": phone,
        "Email": email,
        "Gov_Card_no": gov_card_no,
        "Insurance_no": insurance_no
    }

    # Insert into the Patient collection
    db.Patient.insert_one(new_patient)

    print(f"New patient added: {first_name} {last_name} (Patient_Id: {patient_id})")

# Update patient function
def update_patient(
    patient_id: int,
    first_name=None,
    last_name=None,
    date_of_birth=None,
    phone=None,
    email=None,
    gov_card_no=None,
    insurance_no=None
):
    """
    Updates a patient's information in the Patient collection.
    All fields are optional — only those provided will be updated.
    The Patient_Id cannot be changed.
    """

    # Check if patient exists
    patient = db.Patient.find_one({"Patient_Id": patient_id})
    if not patient:
        print(f"No patient found with Patient_Id: {patient_id}")
        return False

    # Build the update dictionary dynamically
    update_fields = {}
    if first_name is not None:
        update_fields["First_Name"] = first_name
    if last_name is not None:
        update_fields["Last_Name"] = last_name
    if date_of_birth is not None:
        update_fields["Date_Of_Birth"] = date_of_birth
    if phone is not None:
        update_fields["Phone"] = phone
    if email is not None:
        update_fields["Email"] = email
    if gov_card_no is not None:
        update_fields["Gov_Card_no"] = gov_card_no
    if insurance_no is not None:
        update_fields["Insurance_no"] = insurance_no

    # If there are updates, apply them
    if update_fields:
        db.Patient.update_one(
            {"Patient_Id": patient_id},
            {"$set": update_fields}
        )
        print(f"Updated Patient_Id {patient_id} fields: {update_fields}")
    else:
        print("No fields were provided for update.")

    print("Patient update complete.")
    return True

# Delete patient function
def delete_patient(patient_id: int):
    """
    Deletes a patient from the Patient collection by Patient_Id.
    """

    result = db.Patient.delete_one({"Patient_Id": patient_id})

    if result.deleted_count == 0:
        print(f"No patient found with Patient_Id {patient_id}.")
        return False

    print(f"Patient {patient_id} deleted successfully.")
    return True