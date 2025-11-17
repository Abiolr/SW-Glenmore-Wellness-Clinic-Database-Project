# 🔧 MongoDB Stored Procedures (Functions) Guide

## ✅ 5 Stored Procedures for Wellness Clinic

MongoDB supports stored JavaScript functions (similar to stored procedures in SQL databases).

---

## 📦 What's Included

### Script Files
1. **[stored_procedures.py](computer:///mnt/user-data/outputs/stored_procedures.py)** - Python script to create stored functions

### The 5 Stored Functions

| # | Function Name | Purpose | Parameters |
|---|---------------|---------|------------|
| 1 | `calculatePatientAge` | Calculate age from DOB | dateOfBirth (string) |
| 2 | `getPatientVisitCount` | Get visit count for patient | patientId (int) |
| 3 | `calculateInvoiceTotal` | Calculate invoice total | invoiceId (int) |
| 4 | `getStaffAppointmentCount` | Get appointment count for staff | staffId (int) |
| 5 | `isAppointmentAvailable` | Check if time slot available | staffId, startTime, endTime |

---

## 🚀 QUICK START

### Option 1: Run Python Script

```bash
cd backend_v2
cp /mnt/user-data/outputs/stored_procedures.py .
python stored_procedures.py
```

**Expected Output:**
```
============================================================
MongoDB Stored Functions Creator
SW Glenmore Wellness Clinic Database
============================================================

Creating stored functions...
INFO:root:Created function: calculatePatientAge
INFO:root:Created function: getPatientVisitCount
INFO:root:Created function: calculateInvoiceTotal
INFO:root:Created function: getStaffAppointmentCount
INFO:root:Created function: isAppointmentAvailable
INFO:root:Created 5/5 functions successfully

============================================================
Creation Results:
============================================================
calculatePatientAge: ✓ SUCCESS
getPatientVisitCount: ✓ SUCCESS
calculateInvoiceTotal: ✓ SUCCESS
getStaffAppointmentCount: ✓ SUCCESS
isAppointmentAvailable: ✓ SUCCESS

============================================================
Testing Functions:
============================================================
INFO:root:calculatePatientAge('1990-05-15') = 34 years
INFO:root:getPatientVisitCount(1) = 5 visits
INFO:root:calculateInvoiceTotal(1) = $250.50
INFO:root:getStaffAppointmentCount(1) = 12 appointments
INFO:root:isAppointmentAvailable(1, ...) = true

============================================================
✅ ALL STORED FUNCTIONS CREATED!
============================================================

Available functions:
  - calculatePatientAge
  - getPatientVisitCount
  - calculateInvoiceTotal
  - getStaffAppointmentCount
  - isAppointmentAvailable
```

### Option 2: MongoDB Shell

```javascript
// Connect to MongoDB
use GlenmoreWellnessDB

// Create calculatePatientAge function
db.system.js.save({
    _id: "calculatePatientAge",
    value: function(dateOfBirth) {
        if (!dateOfBirth) return null;
        var dob = new Date(dateOfBirth);
        var today = new Date();
        var age = today.getFullYear() - dob.getFullYear();
        var monthDiff = today.getMonth() - dob.getMonth();
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
            age--;
        }
        return age;
    }
})

// Test it
db.eval('calculatePatientAge("1990-05-15")')
```

---

## 📚 Function Details

### 1. calculatePatientAge

**Purpose:** Calculate patient's age from date of birth

**Parameters:**
- `dateOfBirth` (string) - Date in format "YYYY-MM-DD"

**Returns:** Integer (age in years)

**Usage:**
```javascript
// MongoDB Shell
db.eval('calculatePatientAge("1990-05-15")')
// Returns: 34

// In aggregation pipeline
db.patients.aggregate([
  {
    $addFields: {
      age: {
        $function: {
          body: calculatePatientAge,
          args: ["$date_of_birth"],
          lang: "js"
        }
      }
    }
  }
])
```

**Python Usage:**
```python
age = db.command('eval', 'calculatePatientAge("1990-05-15")')
print(f"Age: {age['retval']} years")
```

---

### 2. getPatientVisitCount

**Purpose:** Get total visit count for a patient

**Parameters:**
- `patientId` (int) - Patient ID

**Returns:** Integer (number of visits)

**Usage:**
```javascript
// MongoDB Shell
db.eval('getPatientVisitCount(1)')
// Returns: 5

// Get visit counts for all patients
db.patients.aggregate([
  {
    $addFields: {
      visit_count: {
        $function: {
          body: getPatientVisitCount,
          args: ["$patient_id"],
          lang: "js"
        }
      }
    }
  }
])
```

**Python Usage:**
```python
count = db.command('eval', 'getPatientVisitCount(1)')
print(f"Total visits: {count['retval']}")
```

---

### 3. calculateInvoiceTotal

**Purpose:** Calculate total amount for an invoice from line items

**Parameters:**
- `invoiceId` (int) - Invoice ID

**Returns:** Number (total amount)

**Usage:**
```javascript
// MongoDB Shell
db.eval('calculateInvoiceTotal(1)')
// Returns: 250.50

// Calculate totals for all invoices
db.invoices.aggregate([
  {
    $addFields: {
      calculated_total: {
        $function: {
          body: calculateInvoiceTotal,
          args: ["$invoice_id"],
          lang: "js"
        }
      }
    }
  }
])
```

**Python Usage:**
```python
total = db.command('eval', 'calculateInvoiceTotal(1)')
print(f"Invoice total: ${total['retval']}")
```

---

### 4. getStaffAppointmentCount

**Purpose:** Get total appointment count for a staff member

**Parameters:**
- `staffId` (int) - Staff ID

**Returns:** Integer (number of appointments)

**Usage:**
```javascript
// MongoDB Shell
db.eval('getStaffAppointmentCount(1)')
// Returns: 12

// Get appointment counts for all staff
db.staff.aggregate([
  {
    $addFields: {
      appointment_count: {
        $function: {
          body: getStaffAppointmentCount,
          args: ["$staff_id"],
          lang: "js"
        }
      }
    }
  }
])
```

**Python Usage:**
```python
count = db.command('eval', 'getStaffAppointmentCount(1)')
print(f"Total appointments: {count['retval']}")
```

---

### 5. isAppointmentAvailable

**Purpose:** Check if a time slot is available for scheduling

**Parameters:**
- `staffId` (int) - Staff ID
- `startTime` (string) - Start time in ISO format
- `endTime` (string) - End time in ISO format

**Returns:** Boolean (true if available, false if conflict)

**Usage:**
```javascript
// MongoDB Shell
db.eval('isAppointmentAvailable(1, "2024-12-25T10:00:00", "2024-12-25T11:00:00")')
// Returns: true or false

// Check availability before creating appointment
var available = db.eval('isAppointmentAvailable(1, "2024-12-25T10:00:00", "2024-12-25T11:00:00")')
if (available) {
    db.appointments.insertOne({
        staff_id: 1,
        scheduled_start: "2024-12-25T10:00:00",
        scheduled_end: "2024-12-25T11:00:00",
        // ... other fields
    })
} else {
    print("Time slot not available!")
}
```

**Python Usage:**
```python
available = db.command('eval', 'isAppointmentAvailable(1, "2024-12-25T10:00:00", "2024-12-25T11:00:00")')
if available['retval']:
    print("Time slot is available!")
else:
    print("Time slot is not available - conflict detected")
```

---

## 🔗 Flask Integration

Add these endpoints to your Flask app:

```python
from flask import Flask, jsonify, request
from database import Database
from stored_procedures import initialize_stored_functions

app = Flask(__name__)
db = Database.connect_db()

# Initialize stored functions on startup
logger.info("Initializing stored functions...")
functions_manager = initialize_stored_functions()
logger.info("Stored functions initialized")


# Endpoint: Calculate patient age
@app.route('/api/functions/patient-age/<date_of_birth>', methods=['GET'])
def calculate_patient_age(date_of_birth):
    """Calculate age from date of birth"""
    try:
        result = db.command('eval', f'calculatePatientAge("{date_of_birth}")')
        return jsonify({'age': result['retval']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint: Get patient visit count
@app.route('/api/functions/patient-visits/<int:patient_id>', methods=['GET'])
def get_patient_visit_count(patient_id):
    """Get visit count for a patient"""
    try:
        result = db.command('eval', f'getPatientVisitCount({patient_id})')
        return jsonify({'visit_count': result['retval']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint: Calculate invoice total
@app.route('/api/functions/invoice-total/<int:invoice_id>', methods=['GET'])
def calculate_invoice_total(invoice_id):
    """Calculate total for an invoice"""
    try:
        result = db.command('eval', f'calculateInvoiceTotal({invoice_id})')
        return jsonify({'total': result['retval']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint: Get staff appointment count
@app.route('/api/functions/staff-appointments/<int:staff_id>', methods=['GET'])
def get_staff_appointment_count(staff_id):
    """Get appointment count for a staff member"""
    try:
        result = db.command('eval', f'getStaffAppointmentCount({staff_id})')
        return jsonify({'appointment_count': result['retval']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint: Check appointment availability
@app.route('/api/functions/check-availability', methods=['POST'])
def check_appointment_availability():
    """Check if time slot is available"""
    try:
        data = request.json
        staff_id = data.get('staff_id')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        result = db.command('eval', f'isAppointmentAvailable({staff_id}, "{start_time}", "{end_time}")')
        return jsonify({'available': result['retval']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint: List all stored functions
@app.route('/api/functions/list', methods=['GET'])
def list_stored_functions():
    """List all stored functions"""
    try:
        functions = list(db.system.js.find())
        function_names = [f['_id'] for f in functions]
        return jsonify({'functions': function_names}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint: Recreate all functions
@app.route('/api/functions/recreate', methods=['POST'])
def recreate_stored_functions():
    """Force recreation of all stored functions"""
    try:
        from stored_procedures import recreate_all_functions
        results = recreate_all_functions()
        return jsonify({'message': 'Functions recreated', 'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## 🧪 Testing Endpoints

```bash
# Calculate patient age
curl http://localhost:8000/api/functions/patient-age/1990-05-15

# Get patient visit count
curl http://localhost:8000/api/functions/patient-visits/1

# Calculate invoice total
curl http://localhost:8000/api/functions/invoice-total/1

# Get staff appointment count
curl http://localhost:8000/api/functions/staff-appointments/1

# Check appointment availability
curl -X POST http://localhost:8000/api/functions/check-availability \
  -H "Content-Type: application/json" \
  -d '{
    "staff_id": 1,
    "start_time": "2024-12-25T10:00:00",
    "end_time": "2024-12-25T11:00:00"
  }'

# List all functions
curl http://localhost:8000/api/functions/list

# Recreate functions
curl -X POST http://localhost:8000/api/functions/recreate
```

---

## 🎯 Use Cases

### 1. Patient Dashboard
```python
# Get patient with age and visit count
patient = db.patients.find_one({'patient_id': 1})
age = db.command('eval', f'calculatePatientAge("{patient["date_of_birth"]}")')
visits = db.command('eval', f'getPatientVisitCount(1)')

dashboard = {
    'patient': patient,
    'age': age['retval'],
    'total_visits': visits['retval']
}
```

### 2. Staff Workload
```python
# Get all staff with appointment counts
staff_list = db.staff.find()
for staff in staff_list:
    count = db.command('eval', f'getStaffAppointmentCount({staff["staff_id"]})')
    print(f"{staff['first_name']} {staff['last_name']}: {count['retval']} appointments")
```

### 3. Invoice Validation
```python
# Verify invoice total matches line items
invoice = db.invoices.find_one({'invoice_id': 1})
calculated = db.command('eval', 'calculateInvoiceTotal(1)')

if invoice.get('total') != calculated['retval']:
    print(f"Warning: Invoice total mismatch!")
```

### 4. Appointment Scheduling
```python
# Check before creating appointment
available = db.command('eval', 'isAppointmentAvailable(1, "2024-12-25T10:00:00", "2024-12-25T11:00:00")')

if available['retval']:
    db.appointments.insert_one({
        'staff_id': 1,
        'scheduled_start': "2024-12-25T10:00:00",
        'scheduled_end': "2024-12-25T11:00:00",
        # ...
    })
else:
    print("Cannot schedule - time slot conflict!")
```

---

## ⚠️ Important Notes

### MongoDB Server Version
- Stored functions require MongoDB 4.4+
- The `eval` command must be enabled (it is by default)
- For MongoDB Atlas, ensure your tier supports server-side JavaScript

### Security Considerations
- Stored functions run on the server with full database access
- Only create functions from trusted sources
- Test thoroughly before using in production
- Consider using aggregation pipeline stages instead for simpler operations

### Performance
- Stored functions run on MongoDB server
- Good for complex calculations
- May be slower than native aggregation operators
- Use sparingly for critical paths

### Alternatives
Instead of stored functions, consider:
- Aggregation pipeline (preferred for most cases)
- Views with pre-computed fields
- Application-level logic

---

## 🔄 Updating Functions

### Option 1: Re-run Script
```bash
python stored_procedures.py
```

### Option 2: Via API
```bash
curl -X POST http://localhost:8000/api/functions/recreate
```

### Option 3: Manually in MongoDB Shell
```javascript
// Drop old function
db.system.js.remove({_id: "calculatePatientAge"})

// Create new version
db.system.js.save({
    _id: "calculatePatientAge",
    value: function(dateOfBirth) {
        // Updated code here
    }
})
```

---

## ✅ Checklist

- [ ] Copy `stored_procedures.py` to backend directory
- [ ] Run script to create functions
- [ ] Verify functions exist in `system.js` collection
- [ ] Test each function with sample data
- [ ] Add Flask endpoints (optional)
- [ ] Update frontend to use new endpoints
- [ ] Document function usage for your team

---

## 🎉 You're Done!

You now have 5 stored procedures/functions in MongoDB:
- ✅ calculatePatientAge
- ✅ getPatientVisitCount
- ✅ calculateInvoiceTotal
- ✅ getStaffAppointmentCount
- ✅ isAppointmentAvailable

**Use them to simplify complex database operations!** 🚀
