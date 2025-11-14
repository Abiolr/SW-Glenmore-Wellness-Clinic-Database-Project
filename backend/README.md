# SW Glenmore Wellness Clinic - Backend API

A comprehensive Python FastAPI backend for managing clinic operations including patients, appointments, visits, billing, and more.

## Features

- **Patient Management**: Create, read, update, and delete patient records
- **Staff Management**: Manage medical professionals and administrative staff
- **Appointment Scheduling**: Schedule and manage patient appointments
- **Visit Tracking**: Record patient visits with diagnoses and procedures
- **Prescription Management**: Handle drug prescriptions and dispensing
- **Lab Test Orders**: Track laboratory test orders and results
- **Delivery Records**: Manage delivery/birthing records
- **Recovery Stay**: Track recovery room usage and observations
- **Billing & Invoicing**: Generate invoices and track payments
- **RESTful API**: Clean, well-documented REST endpoints
- **MongoDB Integration**: Scalable NoSQL database storage
- **Auto-incrementing IDs**: Managed primary key sequences

## Technology Stack

- **Python 3.8+**
- **FastAPI**: Modern, fast web framework
- **MongoDB**: NoSQL database (MongoDB Atlas)
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## Project Structure

```
wellness-clinic-backend/
├── main.py                    # FastAPI application with all routes
├── database.py                # MongoDB connection and utilities
├── models.py                  # Pydantic models for all entities
├── crud_patient.py           # CRUD operations for patients
├── crud_staff.py             # CRUD operations for staff
├── crud_appointment.py       # CRUD operations for appointments
├── crud_visit.py             # CRUD operations for visits
├── crud_invoice.py           # CRUD operations for invoices and payments
├── crud_other.py             # CRUD operations for other entities
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account (or local MongoDB instance)
- pip (Python package manager)

## Installation

### 1. Clone or Download the Project

Download all the project files to your local machine.

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit the `.env` file with your MongoDB Atlas credentials:

```env
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=wellness_clinic
```

**To get your MongoDB Atlas URL:**
1. Log in to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Navigate to your cluster
3. Click "Connect"
4. Choose "Connect your application"
5. Copy the connection string
6. Replace `<password>` with your database user's password

### 5. Initialize Collections

The collections you've already created in MongoDB Atlas:
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
- RecoverStay
- RecoveryObservation
- Role
- Staff
- StaffRole
- Visit
- VisitDiagnosis
- VisitProcedure
- WeeklyCoverage
- counters_primary_key_collection

## Running the Application

### Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API Base URL: `http://localhost:8000`
- Interactive API Docs: `http://localhost:8000/docs`
- Alternative API Docs: `http://localhost:8000/redoc`

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

### Main API Endpoints

#### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

#### Patients
- `POST /patients` - Create a new patient
- `GET /patients` - Get all patients (with pagination)
- `GET /patients/{patient_id}` - Get a specific patient
- `PUT /patients/{patient_id}` - Update a patient
- `DELETE /patients/{patient_id}` - Delete a patient
- `GET /patients/search/by-name` - Search patients by name

#### Staff
- `POST /staff` - Create a new staff member
- `GET /staff` - Get all staff members
- `GET /staff/{staff_id}` - Get a specific staff member
- `PUT /staff/{staff_id}` - Update a staff member
- `DELETE /staff/{staff_id}` - Delete a staff member
- `PUT /staff/{staff_id}/deactivate` - Deactivate a staff member

#### Appointments
- `POST /appointments` - Create a new appointment
- `GET /appointments` - Get all appointments
- `GET /appointments/{appointment_id}` - Get a specific appointment
- `PUT /appointments/{appointment_id}` - Update an appointment
- `DELETE /appointments/{appointment_id}` - Delete an appointment
- `GET /appointments/patient/{patient_id}` - Get appointments by patient
- `GET /appointments/staff/{staff_id}` - Get appointments by staff

#### Visits
- `POST /visits` - Create a new visit
- `GET /visits` - Get all visits
- `GET /visits/{visit_id}` - Get a specific visit
- `PUT /visits/{visit_id}` - Update a visit
- `DELETE /visits/{visit_id}` - Delete a visit
- `GET /visits/patient/{patient_id}` - Get visits by patient

#### Diagnoses
- `POST /diagnoses` - Create a new diagnosis
- `GET /diagnoses` - Get all diagnoses
- `GET /diagnoses/{diagnosis_id}` - Get a specific diagnosis
- `GET /diagnoses/search/{code}` - Search diagnoses by code
- `POST /visits/{visit_id}/diagnoses` - Add diagnosis to visit
- `GET /visits/{visit_id}/diagnoses` - Get visit diagnoses

#### Procedures
- `POST /procedures` - Create a new procedure
- `GET /procedures` - Get all procedures
- `GET /procedures/{procedure_id}` - Get a specific procedure
- `POST /visits/{visit_id}/procedures` - Add procedure to visit
- `GET /visits/{visit_id}/procedures` - Get visit procedures

#### Drugs & Prescriptions
- `POST /drugs` - Create a new drug
- `GET /drugs` - Get all drugs
- `GET /drugs/{drug_id}` - Get a specific drug
- `GET /drugs/search/{name}` - Search drugs by name
- `POST /prescriptions` - Create a new prescription
- `GET /prescriptions/{prescription_id}` - Get a specific prescription
- `GET /prescriptions/visit/{visit_id}` - Get prescriptions by visit

#### Lab Tests
- `POST /lab-tests` - Create a new lab test order
- `GET /lab-tests/{labtest_id}` - Get a specific lab test
- `GET /lab-tests/visit/{visit_id}` - Get lab tests by visit

#### Deliveries
- `POST /deliveries` - Create a new delivery record
- `GET /deliveries/visit/{visit_id}` - Get delivery by visit

#### Recovery Stay
- `POST /recovery-stays` - Create a new recovery stay
- `GET /recovery-stays/{stay_id}` - Get a specific recovery stay
- `POST /recovery-observations` - Create a new observation
- `GET /recovery-observations/stay/{stay_id}` - Get observations by stay

#### Invoices & Payments
- `POST /invoices` - Create a new invoice
- `GET /invoices` - Get all invoices
- `GET /invoices/{invoice_id}` - Get a specific invoice
- `PUT /invoices/{invoice_id}` - Update an invoice
- `PUT /invoices/{invoice_id}/status` - Update invoice status
- `DELETE /invoices/{invoice_id}` - Delete an invoice
- `GET /invoices/patient/{patient_id}` - Get invoices by patient
- `POST /invoices/{invoice_id}/lines` - Add invoice line
- `GET /invoices/{invoice_id}/lines` - Get invoice lines
- `POST /payments` - Create a new payment
- `GET /payments` - Get all payments
- `GET /payments/{payment_id}` - Get a specific payment
- `GET /payments/patient/{patient_id}` - Get payments by patient
- `GET /payments/invoice/{invoice_id}` - Get payments by invoice

## Example API Calls

### Create a Patient

```bash
curl -X POST "http://localhost:8000/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1985-05-15",
    "phone": "403-555-0123",
    "email": "john.doe@example.com",
    "gov_card_no": "123456789",
    "insurance_no": "INS-123456"
  }'
```

### Create an Appointment

```bash
curl -X POST "http://localhost:8000/appointments" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "staff_id": 1,
    "scheduled_start": "2025-11-15T10:00:00",
    "scheduled_end": "2025-11-15T10:10:00",
    "is_walkin": false
  }'
```

### Get All Patients

```bash
curl -X GET "http://localhost:8000/patients?skip=0&limit=10"
```

## Database Schema

### Collections Overview

#### Patient
- patient_id (auto-increment)
- first_name, last_name
- date_of_birth
- phone, email
- gov_card_no, insurance_no

#### Staff
- staff_id (auto-increment)
- first_name, last_name
- email, phone
- active (boolean)

#### Appointment
- appointment_id (auto-increment)
- patient_id, staff_id
- scheduled_start, scheduled_end
- created_at
- is_walkin

#### Visit
- visit_id (auto-increment)
- patient_id, staff_id
- appointment_id (optional)
- visit_type
- start_time, end_time
- notes

#### Invoice
- invoice_id (auto-increment)
- patient_id
- invoice_date
- status (pending/paid/partial)

#### Payment
- payment_id (auto-increment)
- patient_id, invoice_id
- payment_date
- method (cash/insurance/government)
- amount

## CORS Configuration

The API is configured to accept requests from any origin (`*`). For production, update the CORS settings in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Error Handling

The API returns standard HTTP status codes:
- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses include a detail message:
```json
{
  "detail": "Error message here"
}
```

## Testing

You can test the API using:
1. **Swagger UI**: Visit `http://localhost:8000/docs`
2. **Postman**: Import the endpoints
3. **cURL**: Command-line requests
4. **Python requests library**: Automated testing

## Deployment

### Deploy to Cloud Platform

This application can be deployed to various cloud platforms:

- **Heroku**: Use Procfile with gunicorn
- **AWS (Elastic Beanstalk, Lambda)**: Package with dependencies
- **Google Cloud Platform**: Use App Engine or Cloud Run
- **Azure**: Use App Service
- **DigitalOcean**: Use App Platform or Droplets

Make sure to:
1. Set environment variables on your deployment platform
2. Update CORS settings for production
3. Use a production-ready ASGI server (gunicorn with uvicorn workers)
4. Enable HTTPS

Example Procfile for Heroku:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Security Considerations

**Important**: This backend has no authentication or authorization as requested. For production use, consider adding:
- JWT authentication
- Role-based access control
- Input validation
- Rate limiting
- HTTPS enforcement
- API key management

## Troubleshooting

### Connection Issues

If you get database connection errors:
1. Check your MongoDB Atlas credentials
2. Verify your IP is whitelisted in MongoDB Atlas
3. Ensure the database name matches your configuration

### Port Already in Use

If port 8000 is already in use:
```bash
uvicorn main:app --reload --port 8001
```

### Module Not Found Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes as part of the SW Glenmore Wellness Clinic coursework.

## Support

For questions or issues:
- Check the interactive API documentation at `/docs`
- Review the error messages in the response
- Check the server logs for detailed error information

## Future Enhancements

Potential features for future versions:
- Authentication and authorization
- Real-time notifications
- Email/SMS reminders for appointments
- Report generation
- Analytics dashboard
- Audit logging
- File upload for medical documents
- Integration with external lab systems
- Telemedicine features

---

**Note**: This is a development version without authentication. Do not use in production without implementing proper security measures.
