# Initialize counters for primary keys in the database 2025-11-05
'''db = client[db_name]
ids = [
    "Staff_id", "Sched_id", "Patient_id", "Invoice_id",
    "Appointment_id", "Coverage_id", "Role_id", "Diagnosis_id",
    "Procedure_id", "Drug_id", "Visit_id", "Payment_id",
    "Delivery_id", "Stay_id", "Labtest_id"
]

for id_name in ids:
    db.counters_primary_key_collection.update_one(
        {"_id": id_name},
        {"$setOnInsert": {"sequence_value": 0}},
        upsert=True
    )

print("✅ Counters initialized.") '''


# Populate Roles collection with predefined roles
'''
def populate_roles():
    roles_data = [
        "Physician",
        "Practitioner",
        "Nurse",
        "Midwife",
        "Pharmacist",
        "Medical Technician",
        "Office Administrator",
        "Receptionist",
        "Bookkeeper"
    ]

    for role_name in roles_data:
        role_id = get_next_sequence("Role_id")

        db.Role.insert_one({
            "Role_Id": role_id,
            "Role_Name": role_name
        })

        print(f"✅ Inserted Role: {role_name} with Role_Id: {role_id}")

    print("\nAll roles successfully inserted into Roles collection!") '''


'''
drug_data = [
    {"Generic_Name": "Lisinopril", "Brand_Name": "Prinivil", "Strength_Form": "10mg Tablet", "Price": 12.99},
    {"Generic_Name": "Metformin", "Brand_Name": "Glucophage", "Strength_Form": "500mg Tablet", "Price": 8.50},
    {"Generic_Name": "Amlodipine", "Brand_Name": "Norvasc", "Strength_Form": "5mg Tablet", "Price": 15.75},
    {"Generic_Name": "Simvastatin", "Brand_Name": "Zocor", "Strength_Form": "20mg Tablet", "Price": 18.99},
    {"Generic_Name": "Omeprazole", "Brand_Name": "Prilosec", "Strength_Form": "20mg Capsule", "Price": 22.50},
    {"Generic_Name": "Levothyroxine", "Brand_Name": "Synthroid", "Strength_Form": "50mcg Tablet", "Price": 14.25},
    {"Generic_Name": "Azithromycin", "Brand_Name": "Zithromax", "Strength_Form": "250mg Tablet", "Price": 35.00},
    {"Generic_Name": "Amoxicillin", "Brand_Name": "Amoxil", "Strength_Form": "500mg Capsule", "Price": 10.99},
    {"Generic_Name": "Atorvastatin", "Brand_Name": "Lipitor", "Strength_Form": "40mg Tablet", "Price": 28.50},
    {"Generic_Name": "Metoprolol", "Brand_Name": "Lopressor", "Strength_Form": "50mg Tablet", "Price": 16.75},
    {"Generic_Name": "Losartan", "Brand_Name": "Cozaar", "Strength_Form": "50mg Tablet", "Price": 19.99},
    {"Generic_Name": "Albuterol", "Brand_Name": "Ventolin", "Strength_Form": "90mcg Inhaler", "Price": 45.00},
    {"Generic_Name": "Gabapentin", "Brand_Name": "Neurontin", "Strength_Form": "300mg Capsule", "Price": 24.99},
    {"Generic_Name": "Sertraline", "Brand_Name": "Zoloft", "Strength_Form": "50mg Tablet", "Price": 32.50},
    {"Generic_Name": "Clopidogrel", "Brand_Name": "Plavix", "Strength_Form": "75mg Tablet", "Price": 65.00},
    {"Generic_Name": "Warfarin", "Brand_Name": "Coumadin", "Strength_Form": "5mg Tablet", "Price": 20.25},
    {"Generic_Name": "Furosemide", "Brand_Name": "Lasix", "Strength_Form": "40mg Tablet", "Price": 11.50},
    {"Generic_Name": "Pantoprazole", "Brand_Name": "Protonix", "Strength_Form": "40mg Tablet", "Price": 26.75},
    {"Generic_Name": "Escitalopram", "Brand_Name": "Lexapro", "Strength_Form": "10mg Tablet", "Price": 38.99},
    {"Generic_Name": "Hydrochlorothiazide", "Brand_Name": "Microzide", "Strength_Form": "25mg Tablet", "Price": 9.99},
    {"Generic_Name": "Prednisone", "Brand_Name": "Deltasone", "Strength_Form": "10mg Tablet", "Price": 13.50},
    {"Generic_Name": "Tramadol", "Brand_Name": "Ultram", "Strength_Form": "50mg Tablet", "Price": 29.99},
    {"Generic_Name": "Insulin Glargine", "Brand_Name": "Lantus", "Strength_Form": "100units/mL Injection", "Price": 125.00},
    {"Generic_Name": "Montelukast", "Brand_Name": "Singulair", "Strength_Form": "10mg Tablet", "Price": 42.50},
    {"Generic_Name": "Rosuvastatin", "Brand_Name": "Crestor", "Strength_Form": "20mg Tablet", "Price": 55.00},
    {"Generic_Name": "Carvedilol", "Brand_Name": "Coreg", "Strength_Form": "25mg Tablet", "Price": 21.75},
    {"Generic_Name": "Tamsulosin", "Brand_Name": "Flomax", "Strength_Form": "0.4mg Capsule", "Price": 33.25},
    {"Generic_Name": "Meloxicam", "Brand_Name": "Mobic", "Strength_Form": "15mg Tablet", "Price": 17.99},
    {"Generic_Name": "Duloxetine", "Brand_Name": "Cymbalta", "Strength_Form": "60mg Capsule", "Price": 48.50},
    {"Generic_Name": "Fluoxetine", "Brand_Name": "Prozac", "Strength_Form": "20mg Capsule", "Price": 27.99}
]


# --- Insert Function ---
def populate_drugs():
    for d in drug_data:
        drug_id = get_next_sequence("Drug_Id")
        d["Drug_Id"] = drug_id

        db.Drug.insert_one(d)
        print(f"✅ Inserted Drug: {d['Brand_Name']} (ID: {drug_id})")

    print("\nAll drug records successfully inserted into the Drug collection!")

'''