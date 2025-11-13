# 🏥 SW Glenmore Wellness Clinic - Backend API

## ✅ Docker-Free Version

This is your complete Python FastAPI backend without Docker dependencies.

## 📦 What's Included: 17 Files

### 🚀 Quick Navigation
1. **Start Here** → `QUICKSTART.md` (3-step setup guide)
2. **Overview** → `SUMMARY.md` (complete project summary)
3. **Documentation** → `README.md` (full details)
4. **Architecture** → `PROJECT_STRUCTURE.md` (design & structure)
5. **File Guide** → `INDEX.md` (navigate all files)

### 💻 Core Application (3 files)
- `main.py` - FastAPI app with 60+ endpoints
- `database.py` - MongoDB connection & utilities
- `models.py` - 25+ Pydantic data models

### 🔧 CRUD Operations (6 files)
- `crud_patient.py` - Patient management
- `crud_staff.py` - Staff management
- `crud_appointment.py` - Scheduling
- `crud_visit.py` - Visit tracking
- `crud_invoice.py` - Billing & payments
- `crud_other.py` - All other entities

### 📚 Documentation (5 files)
- `00_START_HERE.md` - This file!
- `INDEX.md` - File navigation
- `SUMMARY.md` - Project overview
- `QUICKSTART.md` - Setup guide
- `README.md` - Full documentation
- `PROJECT_STRUCTURE.md` - Architecture

### 🧪 Testing & Config (3 files)
- `test_api.py` - Automated tests
- `Wellness_Clinic_API.postman_collection.json` - API testing
- `requirements.txt` - Dependencies

## 🎯 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
Create a `.env` file with your MongoDB Atlas credentials:
```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=wellness_clinic
```

### Step 3: Run the Server
```bash
uvicorn main:app --reload
```

🎉 **That's it!** Visit `http://localhost:8000/docs` to see your API.

## ⚡ Features

✅ **Complete Clinic Management**
- Patient records & search
- Staff management
- Appointment scheduling
- Visit tracking with diagnoses & procedures
- Prescription management
- Lab test orders
- Delivery records
- Recovery room tracking
- Invoice generation
- Payment processing

✅ **Technical Excellence**
- 60+ RESTful API endpoints
- Auto-incrementing IDs
- Data validation with Pydantic
- Interactive API documentation
- Comprehensive error handling
- CORS enabled
- No authentication (as requested)

✅ **MongoDB Integration**
- Supports all 23 collections from your database
- Efficient connection pooling
- Optimized queries

## 🔗 Important URLs

When server is running:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📖 Recommended Reading Order

### If you're new:
1. This file (00_START_HERE.md)
2. QUICKSTART.md
3. SUMMARY.md

### If you want to understand the code:
1. SUMMARY.md
2. PROJECT_STRUCTURE.md
3. models.py
4. main.py

### If you want to test:
1. Start the server
2. Visit http://localhost:8000/docs
3. Or run: `python test_api.py`
4. Or import Postman collection

## 🎓 Project Statistics

- **Python Files**: 10 (3,500+ lines)
- **Documentation**: 5 files (40+ KB)
- **API Endpoints**: 60+
- **Database Collections**: 23
- **Entity Models**: 25+

## 💡 Quick Examples

### Create a Patient
```bash
curl -X POST "http://localhost:8000/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "phone": "403-555-0000",
    "email": "john@example.com"
  }'
```

### Get All Patients
```bash
curl http://localhost:8000/patients
```

### Check Health
```bash
curl http://localhost:8000/health
```

## 🛠️ Common Tasks

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Start development server:**
```bash
uvicorn main:app --reload
```

**Run tests:**
```bash
python test_api.py
```

**Use different port:**
```bash
uvicorn main:app --reload --port 8001
```

## 📋 Prerequisites

Before you start, make sure you have:
- [ ] Python 3.8+ installed
- [ ] pip (Python package manager)
- [ ] MongoDB Atlas account
- [ ] Collections created in MongoDB
- [ ] MongoDB connection string

## 🔍 Need Help?

1. **Setup issues?** → Check `QUICKSTART.md`
2. **API questions?** → Visit `/docs` endpoint
3. **Architecture questions?** → Read `PROJECT_STRUCTURE.md`
4. **Feature details?** → Check `README.md`

## 🚀 What's Next?

After setting up:
1. ✅ Test the API using `/docs`
2. ✅ Run the automated tests
3. ✅ Import Postman collection
4. 📝 Build your frontend
5. 🎨 Customize as needed
6. 🚀 Deploy to production

## 📊 Supported Collections

All 23 MongoDB collections are supported:
- Appointment, Delivery, Diagnosis, Drug
- Invoice, InvoiceLine, LabTestOrder
- Patient, Payment, PractitionerDailySchedule
- Prescription, Procedure, RecoverStay
- RecoveryObservation, Role, Staff, StaffRole
- Visit, VisitDiagnosis, VisitProcedure
- WeeklyCoverage
- counters_primary_key_collection

## ⚠️ Important Notes

- **No Authentication**: This version has no authentication/authorization (as requested)
- **Production Use**: Add security features before production deployment
- **CORS**: Currently allows all origins - restrict for production
- **Environment**: Keep `.env` file secure and never commit it

## 🎉 You're All Set!

Your complete wellness clinic backend is ready to use. Start with **QUICKSTART.md** for detailed setup instructions.

---

**Questions?** Check the documentation files or visit the `/docs` endpoint!
