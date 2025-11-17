# MongoDB Views for SW Glenmore Wellness Clinic

## 5 Essential Views

This script creates 5 useful views for the wellness clinic database.

## Prerequisites
- MongoDB Atlas cluster running
- Database: GlenmoreWellnessDB
- Collections populated with data

## Views to Create

### 1. patient_full_details
Combines patient information with their appointment count and last visit

### 2. staff_appointments_summary
Shows staff members with their appointment counts and schedules

### 3. active_visits_overview
Displays currently active (not completed) visits with patient and staff details

### 4. invoice_payment_summary
Combines invoices with their payment status and amounts

### 5. appointment_calendar_view
Enhanced appointment view with patient and staff names for calendar display

## MongoDB Shell Commands

```javascript
// Connect to your database first
use GlenmoreWellnessDB

// ============================================
// VIEW 1: patient_full_details
// ============================================
// Purpose: Complete patient information with visit statistics
// Combines: patients + aggregated visit data

db.createView(
  "patient_full_details",
  "patients",
  [
    {
      $lookup: {
        from: "visits",
        localField: "patient_id",
        foreignField: "patient_id",
        as: "visits"
      }
    },
    {
      $lookup: {
        from: "appointments",
        localField: "patient_id",
        foreignField: "patient_id",
        as: "appointments"
      }
    },
    {
      $addFields: {
        total_visits: { $size: "$visits" },
        total_appointments: { $size: "$appointments" },
        last_visit_date: { 
          $max: "$visits.start_time" 
        },
        completed_visits: {
          $size: {
            $filter: {
              input: "$visits",
              as: "visit",
              cond: { $ne: ["$$visit.end_time", null] }
            }
          }
        }
      }
    },
    {
      $project: {
        patient_id: 1,
        first_name: 1,
        last_name: 1,
        full_name: { $concat: ["$first_name", " ", "$last_name"] },
        date_of_birth: 1,
        age: {
          $dateDiff: {
            startDate: { $toDate: "$date_of_birth" },
            endDate: "$$NOW",
            unit: "year"
          }
        },
        phone: 1,
        email: 1,
        gov_card_no: 1,
        insurance_no: 1,
        total_visits: 1,
        completed_visits: 1,
        total_appointments: 1,
        last_visit_date: 1,
        has_active_visits: { $gt: ["$total_visits", "$completed_visits"] }
      }
    }
  ]
);

// ============================================
// VIEW 2: staff_appointments_summary
// ============================================
// Purpose: Staff workload and schedule overview
// Combines: staff + aggregated appointment data

db.createView(
  "staff_appointments_summary",
  "staff",
  [
    {
      $lookup: {
        from: "appointments",
        localField: "staff_id",
        foreignField: "staff_id",
        as: "appointments"
      }
    },
    {
      $lookup: {
        from: "visits",
        localField: "staff_id",
        foreignField: "staff_id",
        as: "visits"
      }
    },
    {
      $addFields: {
        total_appointments: { $size: "$appointments" },
        total_visits: { $size: "$visits" },
        upcoming_appointments: {
          $size: {
            $filter: {
              input: "$appointments",
              as: "apt",
              cond: { $gte: [{ $toDate: "$$apt.scheduled_start" }, "$$NOW"] }
            }
          }
        },
        walkin_appointments: {
          $size: {
            $filter: {
              input: "$appointments",
              as: "apt",
              cond: { $eq: ["$$apt.is_walkin", true] }
            }
          }
        }
      }
    },
    {
      $project: {
        staff_id: 1,
        first_name: 1,
        last_name: 1,
        full_name: { $concat: ["$first_name", " ", "$last_name"] },
        email: 1,
        phone: 1,
        active: 1,
        total_appointments: 1,
        upcoming_appointments: 1,
        total_visits: 1,
        walkin_appointments: 1,
        scheduled_appointments: { $subtract: ["$total_appointments", "$walkin_appointments"] }
      }
    }
  ]
);

// ============================================
// VIEW 3: active_visits_overview
// ============================================
// Purpose: Currently in-progress visits
// Filters: end_time is null (visit not completed)

db.createView(
  "active_visits_overview",
  "visits",
  [
    {
      $match: {
        end_time: null
      }
    },
    {
      $lookup: {
        from: "patients",
        localField: "patient_id",
        foreignField: "patient_id",
        as: "patient"
      }
    },
    {
      $lookup: {
        from: "staff",
        localField: "staff_id",
        foreignField: "staff_id",
        as: "staff"
      }
    },
    {
      $unwind: "$patient"
    },
    {
      $unwind: "$staff"
    },
    {
      $project: {
        visit_id: 1,
        patient_id: 1,
        patient_name: { $concat: ["$patient.first_name", " ", "$patient.last_name"] },
        patient_phone: "$patient.phone",
        staff_id: 1,
        staff_name: { $concat: ["$staff.first_name", " ", "$staff.last_name"] },
        visit_type: 1,
        start_time: 1,
        duration_minutes: {
          $dateDiff: {
            startDate: { $toDate: "$start_time" },
            endDate: "$$NOW",
            unit: "minute"
          }
        },
        notes: 1,
        appointment_id: 1
      }
    },
    {
      $sort: { start_time: -1 }
    }
  ]
);

// ============================================
// VIEW 4: invoice_payment_summary
// ============================================
// Purpose: Invoice overview with payment details
// Combines: invoices + aggregated payment data + patient info

db.createView(
  "invoice_payment_summary",
  "invoices",
  [
    {
      $lookup: {
        from: "patients",
        localField: "patient_id",
        foreignField: "patient_id",
        as: "patient"
      }
    },
    {
      $lookup: {
        from: "payments",
        localField: "invoice_id",
        foreignField: "invoice_id",
        as: "payments"
      }
    },
    {
      $lookup: {
        from: "invoice_lines",
        localField: "invoice_id",
        foreignField: "invoice_id",
        as: "line_items"
      }
    },
    {
      $unwind: {
        path: "$patient",
        preserveNullAndEmptyArrays: true
      }
    },
    {
      $addFields: {
        total_amount: {
          $sum: {
            $map: {
              input: "$line_items",
              as: "line",
              in: { $multiply: ["$$line.qty", "$$line.unit_price"] }
            }
          }
        },
        total_paid: {
          $sum: "$payments.amount"
        },
        payment_count: { $size: "$payments" }
      }
    },
    {
      $addFields: {
        balance: { $subtract: ["$total_amount", "$total_paid"] }
      }
    },
    {
      $project: {
        invoice_id: 1,
        patient_id: 1,
        patient_name: { $concat: ["$patient.first_name", " ", "$patient.last_name"] },
        patient_email: "$patient.email",
        invoice_date: 1,
        status: 1,
        total_amount: 1,
        total_paid: 1,
        balance: 1,
        payment_count: 1,
        line_item_count: { $size: "$line_items" },
        is_fully_paid: { $eq: ["$balance", 0] },
        is_overdue: {
          $and: [
            { $ne: ["$status", "paid"] },
            { $lt: [{ $toDate: "$invoice_date" }, { $subtract: ["$$NOW", 2592000000] }] }
          ]
        }
      }
    },
    {
      $sort: { invoice_date: -1 }
    }
  ]
);

// ============================================
// VIEW 5: appointment_calendar_view
// ============================================
// Purpose: Enhanced appointments for calendar display
// Combines: appointments + patient + staff names

db.createView(
  "appointment_calendar_view",
  "appointments",
  [
    {
      $lookup: {
        from: "patients",
        localField: "patient_id",
        foreignField: "patient_id",
        as: "patient"
      }
    },
    {
      $lookup: {
        from: "staff",
        localField: "staff_id",
        foreignField: "staff_id",
        as: "staff"
      }
    },
    {
      $unwind: "$patient"
    },
    {
      $unwind: "$staff"
    },
    {
      $addFields: {
        duration_minutes: {
          $dateDiff: {
            startDate: { $toDate: "$scheduled_start" },
            endDate: { $toDate: "$scheduled_end" },
            unit: "minute"
          }
        }
      }
    },
    {
      $project: {
        appointment_id: 1,
        patient_id: 1,
        patient_name: { $concat: ["$patient.first_name", " ", "$patient.last_name"] },
        patient_phone: "$patient.phone",
        patient_email: "$patient.email",
        staff_id: 1,
        staff_name: { $concat: ["$staff.first_name", " ", "$staff.last_name"] },
        scheduled_start: 1,
        scheduled_end: 1,
        duration_minutes: 1,
        is_walkin: 1,
        appointment_type: {
          $cond: {
            if: "$is_walkin",
            then: "Walk-in",
            else: "Scheduled"
          }
        },
        created_at: 1,
        calendar_title: {
          $concat: [
            "$patient.first_name",
            " ",
            "$patient.last_name",
            " - ",
            "$staff.first_name",
            " ",
            "$staff.last_name"
          ]
        },
        color: {
          $cond: {
            if: "$is_walkin",
            then: "#ff9f40",
            else: "#4285f4"
          }
        }
      }
    },
    {
      $sort: { scheduled_start: 1 }
    }
  ]
);

// ============================================
// VERIFY VIEWS CREATED
// ============================================

// List all views
db.getCollectionNames().filter(name => db.getCollectionInfos({name: name})[0].type === "view")

// Query each view to test
db.patient_full_details.find().limit(5)
db.staff_appointments_summary.find().limit(5)
db.active_visits_overview.find().limit(5)
db.invoice_payment_summary.find().limit(5)
db.appointment_calendar_view.find().limit(5)
```

## Using Views in Queries

### Patient Full Details
```javascript
// Get all patients with their visit statistics
db.patient_full_details.find()

// Find patients with active visits
db.patient_full_details.find({ has_active_visits: true })

// Find patients by age range
db.patient_full_details.find({ age: { $gte: 18, $lte: 65 } })
```

### Staff Appointments Summary
```javascript
// Get all active staff with workload
db.staff_appointments_summary.find({ active: true })

// Find staff with upcoming appointments
db.staff_appointments_summary.find({ upcoming_appointments: { $gt: 0 } })

// Sort by workload
db.staff_appointments_summary.find().sort({ total_appointments: -1 })
```

### Active Visits Overview
```javascript
// Get all ongoing visits
db.active_visits_overview.find()

// Find visits by type
db.active_visits_overview.find({ visit_type: "checkup" })

// Find long-running visits (over 60 minutes)
db.active_visits_overview.find({ duration_minutes: { $gt: 60 } })
```

### Invoice Payment Summary
```javascript
// Get unpaid invoices
db.invoice_payment_summary.find({ is_fully_paid: false })

// Find overdue invoices
db.invoice_payment_summary.find({ is_overdue: true })

// Get invoices with balance
db.invoice_payment_summary.find({ balance: { $gt: 0 } })
```

### Appointment Calendar View
```javascript
// Get all appointments for calendar
db.appointment_calendar_view.find()

// Get walk-in appointments
db.appointment_calendar_view.find({ is_walkin: true })

// Get appointments for specific date range
db.appointment_calendar_view.find({
  scheduled_start: {
    $gte: ISODate("2024-01-01"),
    $lt: ISODate("2024-02-01")
  }
})
```

## Drop Views (if needed)

```javascript
// Drop individual view
db.patient_full_details.drop()
db.staff_appointments_summary.drop()
db.active_visits_overview.drop()
db.invoice_payment_summary.drop()
db.appointment_calendar_view.drop()

// Or drop all at once
[
  "patient_full_details",
  "staff_appointments_summary", 
  "active_visits_overview",
  "invoice_payment_summary",
  "appointment_calendar_view"
].forEach(view => db[view].drop())
```

## Benefits of These Views

1. **Performance**: Pre-computed aggregations
2. **Simplicity**: Complex queries become simple
3. **Consistency**: Same data structure across queries
4. **Reusability**: Use in multiple parts of application
5. **Maintainability**: Update logic in one place

## Integration with Flask API

You can query these views just like regular collections:

```python
# In your Flask API
from database import get_database

db = get_database()

# Query patient_full_details view
@app.route('/api/patients/full-details')
def get_patients_full_details():
    patients = list(db.patient_full_details.find())
    return jsonify(patients)

# Query staff_appointments_summary view
@app.route('/api/staff/summary')
def get_staff_summary():
    staff = list(db.staff_appointments_summary.find({'active': True}))
    return jsonify(staff)

# Query active_visits_overview view
@app.route('/api/visits/active')
def get_active_visits():
    visits = list(db.active_visits_overview.find())
    return jsonify(visits)

# Query invoice_payment_summary view
@app.route('/api/invoices/summary')
def get_invoice_summary():
    invoices = list(db.invoice_payment_summary.find())
    return jsonify(invoices)

# Query appointment_calendar_view view
@app.route('/api/appointments/calendar')
def get_calendar_appointments():
    appointments = list(db.appointment_calendar_view.find())
    return jsonify(appointments)
```
