/**
 * PATIENT PAGE
 * 
 * Purpose:
 * - Manage all patient-related information and records
 * - Primary interface for patient CRUD operations
 * 
 * Features:
 * - Search patients by name, ID, phone, or medical card number
 * - View patient list with pagination/filtering
 * - Add new patient registration form
 * - Edit existing patient information
 * - Delete patient records (with confirmation)
 * - View patient details including:
 *   - Personal information (name, DOB, contact, address)
 *   - Medical card/insurance information
 *   - Emergency contact details
 *   - Appointment history
 *   - Medical history/diagnoses
 *   - Prescription history
 *   - Billing history
 * 
 * Components:
 * - Patient search bar
 * - Patient data table/grid
 * - Patient registration form modal
 * - Patient edit form modal
 * - Patient detail view panel
 * 
 * Data Requirements:
 * - Patient table (all fields)
 * - Related appointments
 * - Related prescriptions
 * - Related billing records
 * 
 * Database Operations:
 * - INSERT new patients
 * - UPDATE patient information
 * - DELETE patients (with cascade considerations)
 * - SELECT with various filters and joins
 */