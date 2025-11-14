# Project Structure - Wellness Clinic Backend

## Overview
This document provides a comprehensive overview of the project structure, file purposes, and relationships.

## Directory Structure

```
wellness-clinic-backend/
│
├── main.py                                 # Main FastAPI application with all routes
├── database.py                            # MongoDB connection and database utilities
├── models.py                              # Pydantic data models for all entities
│
├── CRUD Operations (Database Layer)
│   ├── crud_patient.py                   # Patient CRUD operations
│   ├── crud_staff.py                     # Staff CRUD operations
│   ├── crud_appointment.py               # Appointment CRUD operations
│   ├── crud_visit.py                     # Visit, VisitDiagnosis, VisitProcedure CRUD
│   ├── crud_invoice.py                   # Invoice, InvoiceLine, Payment CRUD
│   └── crud_other.py                     # Diagnosis, Procedure, Drug, Prescription, etc.
│
├── Configuration Files
│   ├── requirements.txt                  # Python dependencies
│   ├── .env.example                      # Environment variables template
│   └── .env                              # Your environment variables (create this)
│
├── Documentation
│   ├── README.md                         # Comprehensive project documentation
│   ├── QUICKSTART.md                     # Quick start guide
│   └── PROJECT_STRUCTURE.md              # This file
│
├── Testing & Development
│   ├── test_api.py                       # API test script
│   └── Wellness_Clinic_API.postman_collection.json  # Postman collection
│
└── Deployment
    ├── Dockerfile                        # Docker container configuration
    └── docker-compose.yml                # Docker Compose configuration
```

## File Descriptions

### Core Application Files

#### `main.py` (2,400+ lines)
- **Purpose**: Main FastAPI application with all API routes
- **Key Components**:
  - FastAPI app initialization
  - CORS configuration
  - Database connection lifecycle (startup/shutdown)
  - All REST API endpoints for:
    - Patients
    - Staff
    - Appointments
    - Visits
    - Diagnoses
    - Procedures
    - Drugs & Prescriptions
    - Lab Tests
    - Deliveries
    - Recovery Stays
    - Invoices & Payments
- **Dependencies**: All CRUD modules, models, database

#### `database.py` (60 lines)
- **Purpose**: MongoDB database connection and utilities
- **Key Features**:
  - Singleton database connection pattern
  - Connection pooling
  - Auto-increment sequence management
  - Collection access methods
- **Functions**:
  - `connect_db()`: Establish MongoDB connection
  - `close_db()`: Close database connection
  - `get_db()`: Get database instance
  - `get_collection()`: Get specific collection
  - `get_next_sequence()`: Generate auto-increment IDs

#### `models.py` (700+ lines)
- **Purpose**: Pydantic models for data validation
- **Key Features**:
  - Type validation
  - Automatic JSON serialization
  - API documentation generation
- **Model Categories**:
  - Core Entities: Patient, Staff, Role
  - Scheduling: Appointment, WeeklyCoverage, PractitionerDailySchedule
  - Clinical: Visit, Diagnosis, Procedure, Prescription
  - Lab & Delivery: LabTestOrder, Delivery, RecoveryStay
  - Financial: Invoice, InvoiceLine, Payment
  - Relationships: StaffRole, VisitDiagnosis, VisitProcedure

### CRUD Operation Files

Each CRUD file follows a consistent pattern with these operations:
- `create()`: Insert new record
- `get()`: Retrieve single record by ID
- `get_all()`: Retrieve multiple records with pagination
- `update()`: Update existing record
- `delete()`: Remove record
- Additional specialized queries as needed

#### `crud_patient.py` (90 lines)
- Patient management operations
- Search by name functionality

#### `crud_staff.py` (75 lines)
- Staff management operations
- Active/inactive status management
- Deactivation instead of deletion

#### `crud_appointment.py` (180 lines)
- Appointment scheduling operations
- Filter by patient, staff, date
- Date range queries

#### `crud_visit.py` (180 lines)
- Visit tracking operations
- Visit-Diagnosis relationship management
- Visit-Procedure relationship management

#### `crud_invoice.py` (230 lines)
- Invoice management operations
- Invoice line item management
- Payment tracking
- Status management (pending/paid/partial)

#### `crud_other.py` (280 lines)
- Diagnosis management
- Procedure management
- Drug catalog management
- Prescription handling
- Lab test orders
- Delivery records
- Recovery stay tracking
- Recovery observations

### Configuration Files

#### `requirements.txt`
```
fastapi==0.104.1          # Web framework
uvicorn[standard]==0.24.0 # ASGI server
pymongo==4.6.0            # MongoDB driver
pydantic==2.5.0           # Data validation
python-dotenv==1.0.0      # Environment variables
python-multipart==0.0.6   # Form data handling
email-validator==2.1.0    # Email validation
dnspython==2.4.2          # DNS for MongoDB connection
```

#### `.env.example`
Template for environment variables:
- `MONGODB_URL`: MongoDB Atlas connection string
- `MONGODB_DB_NAME`: Database name

### Documentation Files

#### `README.md`
Complete documentation including:
- Project overview
- Installation instructions
- API endpoint documentation
- Configuration guide
- Deployment instructions
- Troubleshooting guide

#### `QUICKSTART.md`
Step-by-step quick start guide for:
- Initial setup
- Configuration
- Running the server
- Testing the API
- Common issues

### Testing Files

#### `test_api.py`
Automated test script that:
- Tests all major endpoints
- Creates sample data
- Verifies CRUD operations
- Provides visual feedback

#### `Wellness_Clinic_API.postman_collection.json`
Postman collection with:
- Pre-configured API requests
- Variable support
- Request examples
- Documentation

## Data Flow

### Request Flow
```
Client Request
    ↓
FastAPI Router (main.py)
    ↓
CRUD Operations (crud_*.py)
    ↓
Database Layer (database.py)
    ↓
MongoDB Atlas
    ↓
Response back through the chain
```

### Entity Relationships

```
Patient ←→ Appointment ←→ Staff
    ↓
Visit ←→ Staff
    ↓├─→ VisitDiagnosis ←→ Diagnosis
    ↓├─→ VisitProcedure ←→ Procedure
    ↓├─→ Prescription ←→ Drug
    ↓├─→ LabTestOrder
    ↓└─→ Delivery

Patient ←→ Invoice ←→ InvoiceLine
    ↓
Payment

Patient ←→ RecoveryStay ←→ RecoveryObservation

Staff ←→ StaffRole ←→ Role
    ↓
WeeklyCoverage
    ↓
PractitionerDailySchedule
```

## MongoDB Collections

### Collections with Auto-Increment IDs
All main entities use auto-increment IDs managed by the `counters_primary_key_collection`:
- Patient (patient_id)
- Staff (staff_id)
- Appointment (appointment_id)
- Visit (visit_id)
- Diagnosis (diagnosis_id)
- Procedure (procedure_id)
- Drug (drug_id)
- Prescription (prescription_id)
- LabTestOrder (labtest_id)
- Delivery (delivery_id)
- RecoveryStay (stay_id)
- Invoice (invoice_id)
- Payment (payment_id)

### Junction Tables (No Auto-Increment)
These collections manage many-to-many relationships:
- VisitDiagnosis (visit_id, diagnosis_id)
- VisitProcedure (visit_id, procedure_id)
- StaffRole (staff_id, role_id)

### Dependent Collections
These have composite or parent-dependent keys:
- InvoiceLine (invoice_id, line_no)
- RecoveryObservation (stay_id, text_on)

## API Endpoint Categories

### Patient Management
- CRUD operations for patients
- Search functionality
- Patient history access

### Staff Management
- CRUD operations for staff
- Active/inactive status
- Role assignments

### Scheduling
- Appointment creation and management
- Daily schedules
- Weekly coverage

### Clinical Operations
- Visit recording
- Diagnosis assignment
- Procedure tracking
- Prescription management
- Lab test orders

### Special Care
- Delivery records
- Recovery room management
- Observation logging

### Financial
- Invoice generation
- Line item management
- Payment processing
- Balance tracking

## Best Practices Implemented

### Code Organization
- Separation of concerns (routes, CRUD, models, database)
- Consistent naming conventions
- Type hints throughout
- Comprehensive docstrings

### Database Operations
- Connection pooling
- Auto-increment ID management
- Proper indexing support
- Transaction safety

### API Design
- RESTful principles
- Proper HTTP methods
- Meaningful status codes
- Comprehensive error handling
- Pagination support

### Data Validation
- Pydantic models for all entities
- Type checking
- Email validation
- Required field enforcement

### Documentation
- OpenAPI/Swagger integration
- Inline code documentation
- Comprehensive README
- Example requests

## Extension Points

### Adding New Entities
1. Define Pydantic models in `models.py`
2. Create CRUD operations in new `crud_<entity>.py`
3. Add routes in `main.py`
4. Update documentation

### Adding Authentication
1. Install `python-jose` and `passlib`
2. Create authentication module
3. Add JWT token generation
4. Implement dependency injection for protected routes

### Adding Business Logic
1. Create service layer modules
2. Implement business rules
3. Add validation logic
4. Update CRUD operations

### Adding Reporting
1. Create aggregation queries
2. Add report generation endpoints
3. Implement export functionality
4. Add scheduling if needed

## Development Workflow

### Local Development
1. Set up virtual environment
2. Install dependencies
3. Configure `.env` file
4. Run development server with hot reload
5. Use Swagger UI for testing
6. Run test script for validation

### Testing
1. Unit tests for CRUD operations
2. Integration tests for API endpoints
3. End-to-end tests for workflows
4. Load testing for performance

### Deployment
1. Set up hosting environment (Heroku, AWS, etc.)
2. Configure environment variables
3. Deploy application code
4. Set up monitoring
5. Configure backup strategy

## Security Considerations

### Current State (No Authentication)
- All endpoints are publicly accessible
- No rate limiting
- No input sanitization beyond Pydantic

### Recommended Additions
- JWT authentication
- Role-based access control (RBAC)
- API rate limiting
- Input sanitization
- SQL injection prevention (MongoDB uses BSON)
- HTTPS enforcement
- CORS restriction for production
- Audit logging
- Data encryption at rest

## Performance Optimization

### Current Implementation
- Connection pooling
- Pagination support
- Indexed queries (MongoDB side)

### Potential Improvements
- Caching (Redis)
- Query optimization
- Database indexing
- Load balancing
- CDN for static assets
- Async database operations
- Batch processing

## Maintenance

### Regular Tasks
- Monitor logs
- Review error rates
- Check database performance
- Update dependencies
- Backup database
- Review security patches

### Monitoring
- API response times
- Error rates
- Database connections
- Memory usage
- Disk space

---

**This structure provides a solid foundation for a production-ready medical clinic management system.**
