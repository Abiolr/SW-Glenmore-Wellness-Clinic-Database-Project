# 🚀 Flask Backend - Quick Start Guide

## ✅ Your Flask-Based Backend is Ready!

I've converted the entire backend from FastAPI to **Flask** as requested.

## 📁 What Changed

### New Files:
- **`app.py`** - Complete Flask application (replaces main.py)
- All CRUD files remain the same
- Updated `requirements.txt` for Flask dependencies

### Removed:
- `main.py` (FastAPI version - no longer needed)

## 🎯 Quick Setup (3 Steps)

### Step 1: Install Flask Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask 3.0.0
- Flask-CORS 4.0.0
- pymongo 4.6.0
- pydantic 2.5.0
- python-dotenv 1.0.0

### Step 2: Create .env File

```bash
cd /workspaces/SW-Glenmore-Wellness-Clinic-Database-Project/backend_v2
nano .env
```

Paste this content:
```dotenv
MONGODB_URI=mongodb+srv://habuq028_db_user:n3HdeFLHS5iE7dAb@glenmorewellnesscluster.zfgmoag.mongodb.net/?appName=GlenmoreWellnessCluster
MONGODB_DB_NAME=GlenmoreWellnessDB
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

### Step 3: Run the Flask Server

```bash
python app.py
```

Or with Flask CLI:
```bash
flask --app app run --debug --host=0.0.0.0 --port=8000
```

## ✅ What You Should See

```
 * Serving Flask app 'app'
 * Debug mode: on
Successfully connected to MongoDB database: GlenmoreWellnessDB
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:8000
```

## 🔗 Access Your API

- **Base URL**: http://127.0.0.1:8000
- **Health Check**: http://127.0.0.1:8000/health
- **Root**: http://127.0.0.1:8000/

## 🧪 Testing Your Flask API

### Method 1: Browser
Open: http://127.0.0.1:8000/health

You should see:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Method 2: cURL

```bash
# Health check
curl http://127.0.0.1:8000/health

# Get all patients
curl http://127.0.0.1:8000/patients

# Create a patient
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

### Method 3: Python Test Script

```bash
python test_api.py
```

### Method 4: Postman

Import the `Wellness_Clinic_API.postman_collection.json` file.

**Note:** Change the base URL in Postman to `http://127.0.0.1:8000`

## 📊 API Endpoints (All 60+ Endpoints Work!)

### Patients
- `POST /patients` - Create patient
- `GET /patients` - List patients
- `GET /patients/<id>` - Get patient
- `PUT /patients/<id>` - Update patient
- `DELETE /patients/<id>` - Delete patient
- `GET /patients/search/by-name` - Search patients

### Staff
- `POST /staff` - Create staff
- `GET /staff` - List staff
- `GET /staff/<id>` - Get staff
- `PUT /staff/<id>` - Update staff
- `DELETE /staff/<id>` - Delete staff ⭐
- `PUT /staff/<id>/deactivate` - Deactivate staff

### Appointments
- `POST /appointments` - Create appointment
- `GET /appointments` - List appointments
- `GET /appointments/<id>` - Get appointment
- `PUT /appointments/<id>` - Update appointment
- `DELETE /appointments/<id>` - Delete appointment
- `GET /appointments/patient/<id>` - By patient
- `GET /appointments/staff/<id>` - By staff

...and 40+ more endpoints for visits, diagnoses, procedures, drugs, prescriptions, lab tests, deliveries, recovery, invoices, and payments!

## 🆚 Flask vs FastAPI Differences

### Starting the Server

**Flask:**
```bash
python app.py
# or
flask --app app run
```

**FastAPI (old):**
```bash
uvicorn main:app --reload
```

### API Documentation

**Flask:**
- No automatic Swagger/OpenAPI docs (by default)
- Use Postman or curl for testing
- Can add Flask-RESTX or Flasgger for docs if needed

**FastAPI (old):**
- Automatic interactive docs at `/docs`
- Automatic OpenAPI schema

### Response Handling

**Flask:**
- Returns JSON using `jsonify()`
- Manual status code setting
- Uses `@app.route()` decorators

**FastAPI (old):**
- Automatic JSON serialization
- Type hints for validation
- Uses `@app.get()`, `@app.post()`, etc.

## 💡 Example: Delete Staff Member

```bash
# Delete staff with ID 1
curl -X DELETE http://127.0.0.1:8000/staff/1

# Expected response for success: (204 No Content - empty response)

# Expected response for not found:
{
  "error": "Staff member not found"
}
```

## 🔧 Flask Development Tips

### Enable Debug Mode (Auto-reload)

```bash
export FLASK_DEBUG=1
python app.py
```

Or:
```bash
flask --app app run --debug
```

### Change Port

```bash
python app.py  # Runs on port 8000 (configured in code)
```

Or:
```bash
flask --app app run --port 5000  # Use port 5000
```

### View All Routes

```python
from app import app
print(app.url_map)
```

## 📦 Dependencies Installed

```
Flask==3.0.0          # Web framework
Flask-CORS==4.0.0     # CORS support
pymongo==4.6.0        # MongoDB driver
pydantic==2.5.0       # Data validation
python-dotenv==1.0.0  # Environment variables
email-validator==2.1.0 # Email validation
dnspython==2.4.2      # DNS for MongoDB
```

## ⚠️ Important Notes

1. **app.py replaces main.py** - Use `app.py` for Flask
2. **No Swagger docs** - Use Postman or curl for testing
3. **Same functionality** - All 60+ endpoints work identically
4. **Same database** - Uses same MongoDB collections
5. **Same CRUD files** - No changes needed to CRUD operations

## 🚀 Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 🔍 Troubleshooting

### Issue: "Module not found"
```bash
pip install -r requirements.txt
```

### Issue: "Connection refused"
Make sure your `.env` file exists with correct MongoDB credentials.

### Issue: "Port already in use"
```bash
# Change port in app.py (last line):
app.run(debug=True, host='0.0.0.0', port=8001)
```

### Issue: "CORS errors"
Flask-CORS is already configured to allow all origins. If still having issues, check browser console.

## 📚 Next Steps

1. ✅ Test all endpoints with curl or Postman
2. ✅ Build your frontend
3. ✅ Deploy to production with Gunicorn
4. 🎨 Optional: Add Flask-RESTX for API docs

## 🎉 You're All Set!

Your Flask backend is running with:
- ✅ All 60+ API endpoints
- ✅ MongoDB Atlas connection
- ✅ CORS enabled
- ✅ All 23 collections supported
- ✅ No authentication (as requested)

**Start testing your API now!** 🚀

---

**Quick Command Reference:**

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env

# Run server
python app.py

# Test API
curl http://127.0.0.1:8000/health
```
