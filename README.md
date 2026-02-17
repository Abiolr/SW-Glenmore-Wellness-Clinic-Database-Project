# SW Glenmore Wellness Clinic Database

A comprehensive full-stack platform designed for medical clinics to streamline patient visits, clinical logging, financial billing, and staff scheduling.

---

## Table of Contents

- [Overview](#overview)
- [The Solution](#the-solution)
- [Key Features](#key-features)
  - [Financial Management](#financial-management)
  - [Clinical Operations](#clinical-operations)
  - [Scheduling & Staffing](#scheduling--staffing)
- [Tech Stack](#tech-stack)
  - [Frontend](#frontend)
  - [Backend](#backend)
- [Architecture](#architecture)
- [Advanced Backend Patterns](#advanced-backend-patterns)
- [Database Design](#database-design)
  - [Core Collections](#core-collections)
- [API Documentation](#api-documentation)
  - [Clinical Endpoints](#clinical-endpoints)
  - [Financial Endpoints](#financial-endpoints)
- [Setup & Installation](#setup--installation)

---

## Overview

The Medical Practice Management System is a dual-interface application designed to modernize the administrative and clinical workflows of a healthcare facility. It integrates a React-based frontend dashboard with a robust Flask and MongoDB backend to handle complex data relationships between patients, staff, invoices, and clinical records.

The system replaces disjointed legacy processes with a unified platform that handles everything from the moment a patient checks in (**Active Visits**) to the final financial reconciliation (**Monthly Statements**).

---

## The Solution

Medical practices often struggle with disconnected systems for billing and clinical care. This project solves that by creating a centralized data hub that:

- **Unifies Clinical and Financial Data:** Links clinical procedures directly to invoices, ensuring accurate billing.
- **Automates Reporting:** Replaces manual spreadsheet calculations with real-time MongoDB aggregation pipelines for monthly activity and financial outstanding balances.
- **Ensures Data Integrity:** Uses a strict Service-Repository pattern in the backend with Pydantic validation to prevent data corruption.
- **Supports Legacy Workflows:** Implements custom integer-based sequencing and ISO date enforcement to maintain compatibility with existing physical filing systems.

---

## Key Features

### Financial Management

- **Monthly Statements:** Comprehensive breakdown of Paid vs. Unpaid accounts with visual aging indicators (0–30, 31–60, 61+ days).
- **CSV Export:** One-click export functionality for financial audits.
- **Insurance Forms:** Generation of print-ready Physician Statements and Insurance Receipts.
- **Automated Status Logic:** Backend triggers automatically update invoice statuses (`Pending → Partial → Paid`) as payments are recorded.

### Clinical Operations

- **Active Visit Dashboard:** Real-time view of currently admitted patients and their assigned staff.
- **Departmental Logs:** Specialized interfaces for Delivery Room, Laboratory, and Recovery Room data entry.
- **Prescription Management:** Integrated search and filtering with distinct views for Patient Bottle Labels and Billing Receipts.

### Scheduling & Staffing

- **Master Schedule:** Daily view of all staff shifts and roles.
- **Practitioner Daily:** Personalized schedule view for individual doctors or nurses.
- **Weekly Coverage:** Management of on-call rotations and staff assignments.

---

## Tech Stack

### Frontend

- **React 18** — Component-based UI library  
- **TypeScript** — Strongly typed development for reliability  
- **Vite** — High-performance build tool  
- **React Router v6** — Dynamic client-side routing  
- **Custom CSS** — Bespoke styling for print layouts and dashboards  

### Backend

- **Python Flask** — Lightweight, extensible REST API framework  
- **MongoDB (PyMongo)** — Document-oriented database for flexible schema management  
- **Pydantic** — Data validation and settings management  
- **Flask-CORS** — Cross-origin resource sharing management  

---

## Architecture

The application follows a strict separation of concerns using a Service-Repository pattern in the backend.

```
┌─────────────────┐
│ React Frontend  │
│ (Pages & Views) │
└────────┬────────┘
         │ HTTP / JSON
┌────────▼────────┐
│ Flask API       │◄─────┐
│ (Controllers)   │      │
└────────┬────────┘      │
         │                │
         │ PyMongo        │ Service / CRUD Layer
         │ Aggregations   │ (Business Logic)
┌────────▼──────────────────────────▼──────────┐
│ MongoDB Database                              │
│ (Collections: Patient, Visit, Invoice, etc.)  │
└──────────────────────────────────────────────┘
```

---

## Advanced Backend Patterns

- **Materialized Views:** The system initializes read-optimized MongoDB views on startup (e.g., `patient_full_details`) to ensure dashboard performance.
- **Stored Aggregations:** Complex reports, such as the Monthly Activity Report, are calculated database-side to minimize application memory overhead.
- **Custom Sequencing:** Implements a custom counter collection to generate sequential, human-readable IDs (e.g., `Patient #1001`) instead of random hashes.

---

## Database Design

The system utilizes MongoDB but enforces a structured schema via Pydantic models.

### Core Collections

### Patient

| Field          | Type   | Description                        |
|---------------|--------|------------------------------------|
| patient_id    | Int    | Unique sequential identifier       |
| first_name    | String | Patient first name                 |
| date_of_birth | String | ISO 8601 date string               |
| gov_card_no   | String | Government health ID               |

---

### Visit

| Field       | Type   | Description                                   |
|------------|--------|-----------------------------------------------|
| visit_id   | Int    | Unique sequential identifier                  |
| patient_id | Int    | Foreign key to Patient                        |
| start_time | String | ISO 8601 timestamp                            |
| visit_type | String | Enum (`checkup`, `illness`, `prenatal`) |

---

### Invoice

| Field        | Type  | Description                                   |
|-------------|-------|-----------------------------------------------|
| invoice_id  | Int   | Unique sequential identifier                  |
| patient_id  | Int   | Foreign key to Patient                        |
| total_amount| Float | Total billed amount                           |
| status      | String| Enum (`pending`, `paid`, `partial`) |

---

### Prescription

| Field            | Type   | Description                                     |
|------------------|--------|-------------------------------------------------|
| prescription_id  | Int    | Unique sequential identifier                    |
| visit_id         | Int    | Foreign key to Visit                            |
| drug_id          | Int    | Foreign key to Drug                             |
| dosage           | String | Instructions (e.g., `"10mg daily"`)         |

---

## API Documentation

### Clinical Endpoints

#### `GET /api/visits/active`

Retrieves a summary of all patients currently checked into the clinic.

**Response:**

```json
[
  {
    "visit_id": 1024,
    "patient_name": "John Doe",
    "start_time": "2023-10-27T09:30:00",
    "department": "Recovery"
  }
]
```

#### `GET /api/prescriptions/:id/details`

Fetches enriched prescription data, automatically joining Patient, Drug, and Prescribing Staff details.

---

### Financial Endpoints

#### `GET /api/statements/monthly`

Generates the financial statement for a specific month/year.

**Parameters:**

- month (int)  
- year (int)  

**Response:**

```json
{
  "month": "10/2023",
  "summary": {
    "paid": {
      "total_invoiced": 5000.00,
      "patients": []
    },
    "unpaid": {
      "total_invoiced": 1200.00,
      "patients": []
    }
  }
}
```

#### `GET /api/invoices/:id/summary`

Uses an aggregation pipeline to return an invoice, its line items, and payment history in a single request.

---

## Setup & Installation

### Prerequisites

- Node.js (v16+)  
- Python (v3.9+)  
- MongoDB Instance (Local or Atlas)  

---

### 1. Database Configuration

Ensure MongoDB is running. The application will automatically initialize necessary Views and Counters upon the first successful connection.

---

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
```

The server will start on: http://localhost:8000

---

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start the development server
npm run dev
```

The application will be accessible at: http://localhost:5173
