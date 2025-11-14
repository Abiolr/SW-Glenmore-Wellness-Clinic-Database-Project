# 🚀 SW Glenmore Wellness Clinic - Flask Backend

## ✅ Complete Backend Package

This is your **complete Flask backend** for the SW Glenmore Wellness Clinic project.

## 📦 What's Included: 23 Files

### Core Application (10 files)
- `app.py` - Flask application with 60+ API endpoints
- `database.py` - MongoDB connection and utilities
- `models.py` - Pydantic data validation models
- `crud_patient.py` - Patient CRUD operations
- `crud_staff.py` - Staff CRUD operations
- `crud_appointment.py` - Appointment CRUD operations
- `crud_visit.py` - Visit CRUD operations
- `crud_invoice.py` - Invoice and Payment CRUD operations
- `crud_other.py` - Other entities CRUD operations
- `test_api.py` - Automated API test script

### Configuration (3 files)
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore rules

### Documentation (10 files)
- `START_HERE_FLASK.md` - This file (main entry point)
- `FLASK_QUICKSTART.md` - Quick start guide
- `FLASK_MIGRATION.md` - Migration from FastAPI notes
- `QUICK_FIX.md` - MongoDB connection fix
- `YOUR_ENV_FILE.md` - Your specific configuration
- `TROUBLESHOOTING.md` - Connection troubleshooting
- `README.md` - Complete documentation
- `SUMMARY.md` - Project summary
- `INDEX.md` - File navigation guide
- `PROJECT_STRUCTURE.md` - Architecture details

### Testing (1 file)
- `Wellness_Clinic_API.postman_collection.json` - Postman collection

## 🎯 Quick Setup (4 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Create .env File
Create a file named `.env` in this directory:

```dotenv
MONGODB_URI=mongodb+srv://habuq028_db_user:n3HdeFLHS5iE7dAb@glenmorewellnesscluster.zfgmoag.mongodb.net/?appName=GlenmoreWellnessCluster
MONGODB_DB_NAME=GlenmoreWellnessDB
```

### Step 3: Run the Server
```bash
python app.py
```

### Step 4: Test It
Open: http://127.0.0.1:8000/health

You should see:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## ✅ Success!

If you see the above, your backend is running! 

## 📊 What You Can Do Now

### View All Patients
```bash
curl http://127.0.0.1:8000/patients
```

### Create a Patient
```bash
curl -X POST http://127.0.0.1:8000/patients \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "phone": "403-555-0000",
    "email": "john@example.com"
  }'
```

### Delete a Staff Member
```bash
curl -X DELETE http://127.0.0.1:8000/staff/1
```

### Get All Staff
```bash
curl http://127.0.0.1:8000/staff
```

## 📚 Available Endpoints (60+)

### Patients
- `POST /patients` - Create
- `GET /patients` - List all
- `GET /patients/<id>` - Get one
- `PUT /patients/<id>` - Update
- `DELETE /patients/<id>` - Delete
- `GET /patients/search/by-name` - Search

### Staff
- `POST /staff` - Create
- `GET /staff` - List all
- `GET /staff/<id>` - Get one
- `PUT /staff/<id>` - Update
- `DELETE /staff/<id>` - Delete ⭐
- `PUT /staff/<id>/deactivate` - Deactivate

### Appointments
- `POST /appointments` - Create
- `GET /appointments` - List all
- `GET /appointments/<id>` - Get one
- `PUT /appointments/<id>` - Update
- `DELETE /appointments/<id>` - Delete
- `GET /appointments/patient/<id>` - By patient
- `GET /appointments/staff/<id>` - By staff

### Visits
- `POST /visits` - Create
- `GET /visits` - List all
- `GET /visits/<id>` - Get one
- `PUT /visits/<id>` - Update
- `DELETE /visits/<id>` - Delete
- `GET /visits/patient/<id>` - By patient

### Visit Relationships
- `POST /visits/<id>/diagnoses` - Add diagnosis
- `GET /visits/<id>/diagnoses` - Get diagnoses
- `DELETE /visits/<id>/diagnoses/<diagnosis_id>` - Remove diagnosis
- `POST /visits/<id>/procedures` - Add procedure
- `GET /visits/<id>/procedures` - Get procedures
- `DELETE /visits/<id>/procedures/<procedure_id>` - Remove procedure

### Diagnoses
- `POST /diagnoses` - Create
- `GET /diagnoses` - List all
- `GET /diagnoses/<id>` - Get one
- `GET /diagnoses/search/<code>` - Search by code

### Procedures
- `POST /procedures` - Create
- `GET /procedures` - List all
- `GET /procedures/<id>` - Get one

### Drugs
- `POST /drugs` - Create
- `GET /drugs` - List all
- `GET /drugs/<id>` - Get one
- `GET /drugs/search/<name>` - Search by name

### Prescriptions
- `POST /prescriptions` - Create
- `GET /prescriptions/<id>` - Get one
- `GET /prescriptions/visit/<id>` - By visit

### Lab Tests
- `POST /lab-tests` - Create
- `GET /lab-tests/<id>` - Get one
- `GET /lab-tests/visit/<id>` - By visit

### Deliveries
- `POST /deliveries` - Create
- `GET /deliveries/visit/<id>` - By visit

### Recovery Stays
- `POST /recovery-stays` - Create
- `GET /recovery-stays/<id>` - Get one
- `POST /recovery-observations` - Create observation
- `GET /recovery-observations/stay/<id>` - By stay

### Invoices
- `POST /invoices` - Create
- `GET /invoices` - List all
- `GET /invoices/<id>` - Get one
- `PUT /invoices/<id>` - Update
- `PUT /invoices/<id>/status` - Update status
- `DELETE /invoices/<id>` - Delete
- `GET /invoices/patient/<id>` - By patient
- `POST /invoices/<id>/lines` - Add line item
- `GET /invoices/<id>/lines` - Get line items
- `DELETE /invoices/<id>/lines/<line_no>` - Delete line item

### Payments
- `POST /payments` - Create
- `GET /payments` - List all
- `GET /payments/<id>` - Get one
- `DELETE /payments/<id>` - Delete
- `GET /payments/patient/<id>` - By patient
- `GET /payments/invoice/<id>` - By invoice

## 🧪 Testing Options

### 1. Automated Test Script
```bash
python test_api.py
```

### 2. Postman Collection
Import `Wellness_Clinic_API.postman_collection.json` into Postman

### 3. cURL Commands
Use the examples above

### 4. Browser
Visit: http://127.0.0.1:8000/health

## 📖 Documentation Files

- **FLASK_QUICKSTART.md** - Detailed setup guide
- **QUICK_FIX.md** - MongoDB connection solution
- **TROUBLESHOOTING.md** - Common issues and fixes
- **README.md** - Complete API documentation
- **YOUR_ENV_FILE.md** - Your specific MongoDB config

## 🏗️ Project Structure

```
wellness-clinic-backend/
├── app.py                    # Main Flask application
├── database.py               # MongoDB connection
├── models.py                 # Data models
├── crud_*.py                 # CRUD operations (6 files)
├── requirements.txt          # Dependencies
├── .env                      # Your config (create this)
├── .env.example              # Config template
├── test_api.py              # Test script
└── Documentation/            # All .md files
```

## 🔧 Technology Stack

- **Flask 3.0.0** - Web framework
- **Flask-CORS 4.0.0** - CORS support
- **PyMongo 4.6.0** - MongoDB driver
- **Pydantic 2.5.0** - Data validation
- **Python 3.8+** - Programming language

## 🌟 Key Features

✅ 60+ RESTful API endpoints
✅ Complete CRUD operations
✅ MongoDB Atlas integration
✅ Auto-incrementing IDs
✅ Data validation with Pydantic
✅ CORS enabled
✅ Error handling
✅ No authentication (as requested)
✅ All 23 MongoDB collections supported

## 🚀 Production Deployment

For production, use Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## ⚠️ Important Notes

1. **Create .env file** - Required for MongoDB connection
2. **Install dependencies** - Run `pip install -r requirements.txt`
3. **Python 3.8+** - Required version
4. **MongoDB Atlas** - IP must be whitelisted
5. **Port 8000** - Default port (configurable in app.py)

## 🆘 Need Help?

1. **Setup issues?** → See FLASK_QUICKSTART.md
2. **Connection errors?** → See QUICK_FIX.md
3. **General troubleshooting?** → See TROUBLESHOOTING.md
4. **API details?** → See README.md

## 📝 Quick Command Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env

# Run server
python app.py

# Test health
curl http://127.0.0.1:8000/health

# Run tests
python test_api.py
```

## 🎉 You're Ready!

Your complete Flask backend is ready to use. Start with creating the `.env` file, then run `python app.py`.

**Happy coding!** 🚀
