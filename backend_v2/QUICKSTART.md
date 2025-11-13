# Quick Start Guide - Wellness Clinic Backend

## Prerequisites Checklist
- [ ] Python 3.8+ installed
- [ ] MongoDB Atlas account created
- [ ] Collections created in MongoDB Atlas

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the root directory:

```env
MONGODB_URL=mongodb+srv://your-username:your-password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=wellness_clinic
```

**Get your MongoDB Atlas connection string:**
1. Login to MongoDB Atlas
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. Replace `<password>` with your actual password

### 3. Verify Your Collections

Make sure these collections exist in your MongoDB Atlas database:
- Appointment
- Delivery
- Diagnosis
- Drug
- Invoice
- InvoiceLine
- LabTestOrder
- Patient
- Payment
- PractitionerDailySchedule
- Prescription
- Procedure
- RecoverStay (or RecovertStay)
- RecoveryObservation
- Role
- Staff
- StaffRole
- Visit
- VisitDiagnosis
- VisitProcedure
- WeeklyCoverage
- counters_primary_key_collection

### 4. Start the Server

```bash
uvicorn main:app --reload
```

The server will start at: `http://localhost:8000`

### 5. Test the API

**Option 1: Open your browser**
- Visit `http://localhost:8000/docs` for interactive API documentation

**Option 2: Run the test script**
```bash
python test_api.py
```

**Option 3: Use curl**
```bash
# Health check
curl http://localhost:8000/health

# Create a patient
curl -X POST "http://localhost:8000/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "Patient",
    "date_of_birth": "1990-01-01",
    "phone": "403-555-0000",
    "email": "test@example.com"
  }'
```

### 6. Import Postman Collection

1. Open Postman
2. Click "Import"
3. Select `Wellness_Clinic_API.postman_collection.json`
4. All API endpoints are ready to test!

## Common Issues & Solutions

### Issue: "Failed to connect to MongoDB"
**Solution:** 
- Check your MongoDB Atlas connection string
- Verify your IP is whitelisted in MongoDB Atlas Network Access
- Ensure your password doesn't contain special characters that need URL encoding

### Issue: "Port 8000 is already in use"
**Solution:** Use a different port
```bash
uvicorn main:app --reload --port 8001
```

### Issue: "Module not found"
**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Collection not found"
**Solution:** Create the missing collection in MongoDB Atlas or use the API to create data

## Next Steps

1. **Create some test data** using the `/docs` interface
2. **Try different API endpoints** in Postman or the browser
3. **Build your frontend** to consume this API
4. **Add more features** as needed for your project

## API Documentation

Once running, access comprehensive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Support

If you encounter issues:
1. Check the terminal for error messages
2. Verify your `.env` file is properly configured
3. Ensure MongoDB Atlas is accessible
4. Check the README.md for more detailed information

## Production Deployment

When ready for production:
1. Set `MONGODB_URL` and `MONGODB_DB_NAME` as environment variables
2. Update CORS settings in `main.py`
3. Use a production ASGI server like Gunicorn with Uvicorn workers
4. Enable HTTPS
5. Add authentication and authorization

---

**Ready to start building! 🚀**
